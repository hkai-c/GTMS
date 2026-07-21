"""GTMS 调度器常量 (Scheduler Constants)

Sprint 13 — Task 13.2 补充开发
依据 §15.19 Scheduler Principle。

统一管理所有调度器相关常量和配置。
仅包含常量定义，不得包含任何业务逻辑。

以后新增任何 Scheduler Job：
    1. 在 JobIds 中新增 Job ID
    2. 在 SchedulerConfig 中新增 Cron 配置
    3. 在 jobs.py 中新增 Job 函数
    4. 在 scheduler.py 中注册 Job
"""

# ============================================================
# 统一 Job ID 常量
# ============================================================


class JobIds:
    """调度器 Job ID 统一管理。

    所有 Job ID 集中定义于此，禁止在代码中硬编码 Job ID 字符串。

    使用方式:
        from server.scheduler.constants import JobIds

        scheduler.add_job(func, id=JobIds.BACKUP, ...)
    """

    BACKUP: str = "generate_backup"
    """数据库备份 Job ID。"""

    NOTIFICATION: str = "generate_notifications"
    """消息提醒生成 Job ID。"""

    # 预留
    REPORT: str = "generate_report"
    """报表生成 Job ID（预留）。"""

    AUTO_CLEANUP: str = "auto_cleanup"
    """自动清理 Job ID（预留）。"""

    MAIL: str = "send_mail"
    """邮件发送 Job ID（预留）。"""

    HEALTH_CHECK: str = "health_check"
    """健康检查 Job ID（预留）。"""


# ============================================================
# 统一调度器配置
# ============================================================


class SchedulerConfig:
    """调度器统一配置。

    所有调度器配置集中定义于此，禁止在代码中硬编码 Cron 参数。

    使用方式:
        from server.scheduler.constants import SchedulerConfig

        scheduler = BackgroundScheduler(timezone=SchedulerConfig.TIMEZONE)
        scheduler.add_job(func, trigger=CronTrigger(**SchedulerConfig.BACKUP_CRON))
    """

    TIMEZONE: str = "Asia/Shanghai"
    """调度器统一时区。"""

    BACKUP_CRON: dict = {
        "hour": 2,
        "minute": 0,
    }
    """数据库备份 Cron 配置：每天凌晨 2:00。"""

    NOTIFICATION_CRON: dict = {
        "minute": 0,
    }
    """消息提醒生成 Cron 配置：每小时整点。"""

    # 预留
    REPORT_CRON: dict = {
        "hour": 8,
        "minute": 0,
    }
    """报表生成 Cron 配置（预留）：每天 8:00。"""

    MAIL_CRON: dict = {
        "minute": 30,
    }
    """邮件发送 Cron 配置（预留）：每半小时。"""

    AUTO_CLEANUP_CRON: dict = {
        "hour": 3,
        "minute": 0,
    }
    """自动清理 Cron 配置（预留）：每天凌晨 3:00。"""


__all__ = [
    "JobIds",
    "SchedulerConfig",
]
