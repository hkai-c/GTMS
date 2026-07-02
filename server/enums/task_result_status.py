"""
试磨结果状态枚举 (TrialTaskResultStatus)

对应 DB_DESIGN.md trial_tasks.result_status。

表示试磨的最终结果。

流转规则（不可逆）：
    PENDING → PASSED
    PENDING → FAILED
    禁止 PASSED ↔ FAILED 互转。

UI 颜色：
    PENDING — 灰色
    PASSED  — 绿色
    FAILED  — 红色
"""

from enum import Enum


class TrialTaskResultStatus(str, Enum):
    """试磨结果状态"""

    PENDING = "pending"
    """待试磨 — 尚未完成试磨"""

    PASSED = "passed"
    """试磨成功 — 已上传检测报告且合格"""

    FAILED = "failed"
    """试磨失败 — 无法满足加工要求"""

    # ============================================================
    # UI 颜色映射
    # ============================================================

    @property
    def color(self) -> str:
        """返回该状态对应的 UI 颜色（十六进制）"""
        _color_map = {
            TrialTaskResultStatus.PENDING: "#9E9E9E",
            TrialTaskResultStatus.PASSED: "#4CAF50",
            TrialTaskResultStatus.FAILED: "#F44336",
        }
        return _color_map[self]

    # ============================================================
    # 流转规则
    # ============================================================

    @property
    def next_statuses(self) -> list["TrialTaskResultStatus"]:
        """返回当前状态允许流转到的下一个状态列表"""
        _flow_map = {
            TrialTaskResultStatus.PENDING: [
                TrialTaskResultStatus.PASSED,
                TrialTaskResultStatus.FAILED,
            ],
            TrialTaskResultStatus.PASSED: [],   # 终态，不可逆
            TrialTaskResultStatus.FAILED: [],   # 终态，不可逆
        }
        return _flow_map[self]

    @property
    def is_terminal(self) -> bool:
        """是否为终态（不可继续流转）"""
        return self in (TrialTaskResultStatus.PASSED, TrialTaskResultStatus.FAILED)

    @classmethod
    def initial(cls) -> "TrialTaskResultStatus":
        """返回初始状态"""
        return cls.PENDING