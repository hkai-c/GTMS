"""检测结果枚举 (InspectionResult)

对应 DB_DESIGN.md inspection_records.result。

表示试磨完成后检测的最终结论。

枚举值：
    PASS — 检测合格
    FAIL — 检测不合格
"""

from enum import Enum


class InspectionResult(str, Enum):
    """检测结果"""

    PASS = "pass"
    """检测合格 — 试磨件满足精度和粗糙度要求"""

    FAIL = "fail"
    """检测不合格 — 试磨件不满足要求"""

    # ============================================================
    # UI 颜色映射
    # ============================================================

    @property
    def color(self) -> str:
        """返回该结果对应的 UI 颜色（十六进制）"""
        _color_map = {
            InspectionResult.PASS: "#4CAF50",
            InspectionResult.FAIL: "#F44336",
        }
        return _color_map[self]

    # ============================================================
    # 辅助方法
    # ============================================================

    @property
    def is_pass(self) -> bool:
        """是否为合格"""
        return self == InspectionResult.PASS

    @property
    def is_fail(self) -> bool:
        """是否为不合格"""
        return self == InspectionResult.FAIL