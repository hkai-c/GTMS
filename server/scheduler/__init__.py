"""GTMS 后台调度器 (Scheduler)

Sprint 12 — Task 12.4
依据 SRS §4.9、§15.19 Scheduler Principle。

GTMS 后台定时任务调度器，管理 APScheduler 生命周期。
提供：
    - start_scheduler: 启动调度器
    - stop_scheduler: 停止调度器
    - get_scheduler: 获取调度器实例

调度器仅负责定时触发，所有业务逻辑委托给对应 Service。
"""

import logging

from .scheduler import (
    get_scheduler,
    start_scheduler,
    stop_scheduler,
)

logger = logging.getLogger(__name__)

__all__ = [
    "get_scheduler",
    "start_scheduler",
    "stop_scheduler",
]
