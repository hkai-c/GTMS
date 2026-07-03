"""系统操作类型枚举 (ActionType)

对应 DB_DESIGN.md system_logs.action ENUM('create','update','delete','status_change')。

表示用户对系统资源执行的操作类型。
"""

from enum import Enum


class ActionType(str, Enum):
    """系统操作类型"""

    CREATE = "create"
    """创建 — 新增记录"""

    UPDATE = "update"
    """更新 — 修改记录"""

    DELETE = "delete"
    """删除 — 软删除记录"""

    STATUS_CHANGE = "status_change"
    """状态变更 — 流程状态或结果状态变更"""

    # ============================================================
    # UI 显示名映射
    # ============================================================

    @property
    def display_name(self) -> str:
        """返回中文显示名"""
        _name_map = {
            ActionType.CREATE: "创建",
            ActionType.UPDATE: "更新",
            ActionType.DELETE: "删除",
            ActionType.STATUS_CHANGE: "状态变更",
        }
        return _name_map[self]