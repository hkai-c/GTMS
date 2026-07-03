"""消息提醒类型枚举 (NotifyType)

对应 DB_DESIGN.md notifications.type ENUM('receipt_delay','grinding_delay','report_missing')。

表示系统自动生成的消息提醒类型。
"""

from enum import Enum


class NotifyType(str, Enum):
    """消息提醒类型"""

    RECEIPT_DELAY = "receipt_delay"
    """收件超时提醒 — 客户寄出后超过预期时间未收件"""

    GRINDING_DELAY = "grinding_delay"
    """试磨超时提醒 — 收件后超过预期时间未完成试磨"""

    REPORT_MISSING = "report_missing"
    """报告缺失提醒 — 试磨完成但未上传检测报告"""

    # ============================================================
    # UI 显示名映射
    # ============================================================

    @property
    def display_name(self) -> str:
        """返回中文显示名"""
        _name_map = {
            NotifyType.RECEIPT_DELAY: "收件超时",
            NotifyType.GRINDING_DELAY: "试磨超时",
            NotifyType.REPORT_MISSING: "报告缺失",
        }
        return _name_map[self]