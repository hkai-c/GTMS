"""GTMS 后台调度器 (Scheduler)

Sprint 12 — Task 12.4 / Sprint 13 — Task 13.2
依据 SRS §4.9、§15.19 Scheduler Principle。

GTMS 后台定时任务调度器，管理 APScheduler 生命周期。
提供：
    - start_scheduler: 启动调度器
    - stop_scheduler: 停止调度器
    - get_scheduler: 获取调度器实例
    - JobIds: 统一 Job ID 常量
    - SchedulerConfig: 统一调度器配置

调度器仅负责定时触发，所有业务逻辑委托给对应 Service / Manager。
"""

import logging

from .constants import JobIds, SchedulerConfig
from .jobs import generate_backup_job
from .scheduler import (
    get_scheduler,
    start_scheduler,
    stop_scheduler,
)

logger = logging.getLogger(__name__)

__all__ = [
    "generate_backup_job",
    "get_scheduler",
    "JobIds",
    "SchedulerConfig",
    "start_scheduler",
    "stop_scheduler",
]
