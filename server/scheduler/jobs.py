"""GTMS 定时任务 (Jobs)

Sprint 12 — Task 12.4 / Sprint 13 — Task 13.2
依据 §15.19 Scheduler Principle、§15.21 Backup Principle。

定义所有后台定时任务函数。
每个 Job 仅负责：
    - 创建数据库会话（如需要）
    - 调用对应 Service / Manager
    - 关闭数据库会话（如需要）
    - 输出运行日志

Job 禁止包含任何业务逻辑。
"""

import logging
import time

from server.database.session import SessionLocal
from server.services.notification_service import NotificationService
from server.utils.backup import BackupManager

logger = logging.getLogger("gtms.server")


def generate_notifications_job() -> None:
    """定时生成消息提醒。

    每小时执行一次，调用 NotificationService.generate_notifications()。
    内部创建独立数据库会话，不依赖 HTTP 请求上下文。

    日志输出：
        - 开始执行
        - 执行耗时
        - 新增消息数量
        - 异常信息
    """
    logger.info("定时任务: 开始生成消息提醒")
    start_time = time.time()

    db = SessionLocal()
    try:
        service = NotificationService()
        count = service.generate_notifications(db)
        elapsed = time.time() - start_time
        logger.info(
            "定时任务: 消息提醒生成完成，新增 %d 条，耗时 %.2fs",
            count, elapsed,
        )
    except Exception:
        elapsed = time.time() - start_time
        logger.exception(
            "定时任务: 消息提醒生成失败，耗时 %.2fs",
            elapsed,
        )
    finally:
        db.close()


def generate_backup_job() -> None:
    """定时执行数据库备份。

    每天执行一次，调用 BackupManager.create_backup()。
    BackupManager 属于 Infrastructure Layer，不依赖数据库会话。

    日志输出：
        - 开始执行
        - 备份文件路径
        - 执行耗时
        - 异常信息
    """
    logger.info("定时任务: 开始执行数据库备份")
    start_time = time.time()

    try:
        manager = BackupManager()
        backup_path = manager.create_backup()
        elapsed = time.time() - start_time
        logger.info(
            "定时任务: 数据库备份完成，备份文件: %s，耗时 %.2fs",
            backup_path, elapsed,
        )
    except Exception:
        elapsed = time.time() - start_time
        logger.exception(
            "定时任务: 数据库备份失败，耗时 %.2fs",
            elapsed,
        )


__all__ = [
    "generate_backup_job",
    "generate_notifications_job",
]
