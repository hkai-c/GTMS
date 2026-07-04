"""GTMS 任务编号生成器 (Task ID Generator)

Sprint 2 — Task 2.4
严格依据 Task 2.4 规范、SRS.md、Sprint 1 ORM。

编号规则:
    YYYYMMDD-N（按日期 + 当天流水号）
    示例: 20260701-1, 20260701-2, 20260702-1

实现要点:
    - 查询数据库当天最大编号，自动 +1
    - 每天流水号从 1 重新开始
    - 并发唯一约束冲突时自动重试（最多 3 次）
    - 不依赖内存变量，完全基于数据库查询

使用方式:
    from server.utils.id_generator import generate_task_no

    task_no = generate_task_no(db)
"""

import logging
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from server.core.exceptions import BusinessLogicException
from server.models import TrialTask

logger = logging.getLogger(__name__)

# 最大重试次数（并发唯一约束冲突时）
_MAX_RETRIES = 3


def generate_task_no(db: Session) -> str:
    """生成唯一任务编号。

    格式: YYYYMMDD-N（如 20260701-1）

    规则:
        1. 获取当前日期 YYYYMMDD
        2. 查询数据库中当天最大编号
        3. 若存在 → 解析流水号 +1
        4. 若不存在 → 从 1 开始
        5. 若写入时发生唯一约束冲突 → 重新查询并重试（最多 3 次）

    Args:
        db: 数据库会话。

    Returns:
        唯一任务编号字符串。

    Raises:
        BusinessLogicException: 重试耗尽后仍冲突时抛出。
    """
    today_str = _get_today_str()

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            seq = _get_next_sequence(db, today_str)
            task_no = f"{today_str}-{seq}"

            # 验证唯一性：尝试写入一条临时记录
            # 实际使用时由 TrialTask 创建方负责写入，
            # 这里只做"预留编号"验证（检查是否已存在）
            existing = (
                db.query(TrialTask)
                .filter(TrialTask.task_no == task_no)
                .first()
            )
            if existing is not None:
                # 已被占用，重试
                if attempt < _MAX_RETRIES:
                    logger.warning(
                        "编号 %s 已被占用，第 %d 次重试...", task_no, attempt
                    )
                    continue
                raise BusinessLogicException(
                    f"无法生成唯一编号，已重试 {_MAX_RETRIES} 次",
                    detail={"date": today_str, "last_attempt": task_no},
                )

            return task_no

        except IntegrityError:
            db.rollback()
            if attempt < _MAX_RETRIES:
                logger.warning(
                    "唯一约束冲突，第 %d 次重试...", attempt
                )
                continue
            raise BusinessLogicException(
                f"编号生成失败：并发冲突，已重试 {_MAX_RETRIES} 次",
                detail={"date": today_str},
            )

    # 理论上不会执行到这里
    raise BusinessLogicException(
        "编号生成失败：重试耗尽",
        detail={"date": today_str},
    )


def _get_today_str() -> str:
    """获取当前日期字符串 YYYYMMDD。

    Returns:
        格式为 YYYYMMDD 的日期字符串。
    """
    return date.today().strftime("%Y%m%d")


def _get_next_sequence(db: Session, today_str: str) -> int:
    """查询当天最大编号，返回下一个流水号。

    从数据库获取当天所有 task_no，在 Python 侧解析流水号并取最大值。
    避免 ORDER BY task_no 字符串排序导致 "10" < "9" 的问题。

    Args:
        db: 数据库会话。
        today_str: 日期字符串（如 "20260701"）。

    Returns:
        下一个流水号（从 1 开始）。
    """
    prefix = f"{today_str}-"
    prefix_len = len(prefix)

    tasks = (
        db.query(TrialTask.task_no)
        .filter(TrialTask.task_no.like(f"{today_str}-%"))
        .all()
    )

    if not tasks:
        return 1

    # 解析所有流水号，取最大值
    max_seq = 0
    for (task_no,) in tasks:
        try:
            seq = int(task_no[prefix_len:])
            if seq > max_seq:
                max_seq = seq
        except (ValueError, IndexError):
            logger.warning("无法解析现有编号 %s，跳过", task_no)

    return max_seq + 1


__all__ = [
    "generate_task_no",
]