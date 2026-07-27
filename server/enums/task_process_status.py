"""
试磨任务流程状态枚举 (TrialTaskProcessStatus)

对应 DB_DESIGN.md trial_tasks.process_status。

表示任务当前所处流程阶段。

流转规则（严格单向）：
    CREATED → RECEIVED → GRINDING → DISPATCHED → CLOSED
                         ↓
                       CLOSED（试磨失败时跳过 DISPATCHED）
    禁止跳级、禁止逆向、CLOSED 为终态。

UI 颜色：
    CREATED    — 灰色
    RECEIVED   — 蓝色
    GRINDING   — 橙色
    DISPATCHED — 紫色
    CLOSED     — 深灰色
"""

from enum import Enum


class TrialTaskProcessStatus(str, Enum):
    """试磨任务流程状态"""

    CREATED = "created"
    """已创建 — 销售创建试磨任务"""

    RECEIVED = "received"
    """已收件 — 公司收到客户工件"""

    GRINDING = "grinding"
    """试磨中 — 技术人员开始试磨"""

    DISPATCHED = "dispatched"
    """已寄回 — 工件已寄回客户"""

    CLOSED = "closed"
    """已关闭 — 任务结束归档（终态）"""

    # ============================================================
    # UI 颜色映射
    # ============================================================

    @property
    def color(self) -> str:
        """返回该状态对应的 UI 颜色（十六进制）"""
        _color_map = {
            TrialTaskProcessStatus.CREATED: "#9E9E9E",
            TrialTaskProcessStatus.RECEIVED: "#2196F3",
            TrialTaskProcessStatus.GRINDING: "#FF9800",
            TrialTaskProcessStatus.DISPATCHED: "#9C27B0",
            TrialTaskProcessStatus.CLOSED: "#424242",
        }
        return _color_map[self]

    # ============================================================
    # 流转规则
    # ============================================================

    @property
    def next_statuses(self) -> list["TrialTaskProcessStatus"]:
        """返回当前状态允许流转到的下一个状态列表"""
        _flow_map = {
            TrialTaskProcessStatus.CREATED: [TrialTaskProcessStatus.RECEIVED],
            TrialTaskProcessStatus.RECEIVED: [TrialTaskProcessStatus.GRINDING],
            TrialTaskProcessStatus.GRINDING: [
                TrialTaskProcessStatus.DISPATCHED,
                TrialTaskProcessStatus.CLOSED,
            ],
            TrialTaskProcessStatus.DISPATCHED: [TrialTaskProcessStatus.CLOSED],
            TrialTaskProcessStatus.CLOSED: [],  # 终态
        }
        return _flow_map[self]

    @property
    def is_terminal(self) -> bool:
        """是否为终态（不可继续流转）"""
        return self == TrialTaskProcessStatus.CLOSED

    @classmethod
    def initial(cls) -> "TrialTaskProcessStatus":
        """返回初始状态"""
        return cls.CREATED