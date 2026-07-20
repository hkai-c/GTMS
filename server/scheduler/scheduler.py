"""GTMS 调度器管理器 (Scheduler Manager)

Sprint 12 — Task 12.4
依据 §15.19 Scheduler Principle。

管理 APScheduler 生命周期，提供：
    - 调度器创建/启动/停止
    - Job 注册
    - 运行日志

调度器不包含任何业务逻辑，仅负责定时触发 Job。
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .jobs import generate_notifications_job

logger = logging.getLogger(__name__)

# ============================================================
# 全局调度器实例（单例）
# ============================================================

_scheduler: BackgroundScheduler | None = None


def _create_scheduler() -> BackgroundScheduler:
    """创建并配置 BackgroundScheduler 实例。

    内部方法，不对外暴露。

    Returns:
        BackgroundScheduler: 已配置的调度器实例。
    """
    scheduler = BackgroundScheduler(
        timezone="Asia/Shanghai",
    )

    # 注册唯一 Job：每小时执行一次消息提醒生成
    scheduler.add_job(
        generate_notifications_job,
        trigger=CronTrigger(
            minute=0,
        ),
        id="generate_notifications",
        name="消息提醒生成",
        replace_existing=True,
        max_instances=1,
    )

    logger.info("调度器已创建，注册 Job: generate_notifications")
    return scheduler


def get_scheduler() -> BackgroundScheduler:
    """获取或创建全局调度器实例。

    懒加载单例模式，确保全局只有一个调度器。

    Returns:
        BackgroundScheduler: 调度器实例。
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = _create_scheduler()
    return _scheduler


def start_scheduler() -> None:
    """启动调度器。

    获取调度器实例并启动。
    重复调用安全（已启动则跳过）。
    """
    scheduler = get_scheduler()
    if scheduler.running:
        logger.info("调度器已在运行中，跳过启动")
        return
    scheduler.start()
    logger.info("调度器已启动")


def stop_scheduler() -> None:
    """停止调度器。

    停止调度器并等待所有 Job 完成。
    重复调用安全（已停止则跳过）。
    """
    global _scheduler
    if _scheduler is None:
        logger.info("调度器未创建，跳过停止")
        return
    if not _scheduler.running:
        logger.info("调度器未运行，跳过停止")
        return
    _scheduler.shutdown(wait=True)
    _scheduler = None
    logger.info("调度器已停止")


__all__ = [
    "get_scheduler",
    "start_scheduler",
    "stop_scheduler",
]
