"""GTMS 状态标签组件 (StatusBadge)

Sprint 5 — Task 5.5
严格依据 UI_PROTOTYPE §19。

可复用的 QLabel 子类，用于显示试磨任务流程状态和结果状态。
支持 6 个 Process Status + 3 个 Result Status。
使用 Qt StyleSheet 渲染，不依赖 paintEvent 或 QPainter。

Usage:
    badge = StatusBadge("created")
    badge.set_status("grinding")
    print(badge.status)  # "grinding"
"""

import logging
from typing import ClassVar, Optional

from PySide6.QtWidgets import QLabel, QWidget

logger = logging.getLogger("gtms.client")


class StatusBadge(QLabel):
    """状态标签组件。

    以圆角标签形式显示试磨任务的流程状态或结果状态。
    纯展示组件，不实现任何业务逻辑、状态流转、权限校验。

    Attributes:
        STATUS_TEXT: 状态值 → 中文显示文本映射。
        STATUS_STYLE: 状态值 → Qt StyleSheet 映射。

    Usage:
        badge = StatusBadge("created", parent=self)
        badge.set_status("grinding")
    """

    # ============================================================
    # 状态映射（集中管理）
    # ============================================================

    STATUS_TEXT: ClassVar[dict[str, str]] = {
        # ---- 流程状态 (Process Status) ----
        "created": "已创建",
        "received": "已收件",
        "grinding": "试磨中",
        "completed": "已完成",
        "dispatched": "已寄回",
        "closed": "已关闭",
        # ---- 结果状态 (Result Status) ----
        "pending": "待试磨",
        "passed": "试磨成功",
        "failed": "试磨失败",
    }

    STATUS_STYLE: ClassVar[dict[str, str]] = {
        # ---- 流程状态 ----
        "created": (
            "QLabel {"
            "  background-color: #9E9E9E;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
        "received": (
            "QLabel {"
            "  background-color: #2196F3;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
        "grinding": (
            "QLabel {"
            "  background-color: #FF9800;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
        "completed": (
            "QLabel {"
            "  background-color: #00BCD4;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
        "dispatched": (
            "QLabel {"
            "  background-color: #9C27B0;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
        "closed": (
            "QLabel {"
            "  background-color: #424242;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
        # ---- 结果状态 ----
        "pending": (
            "QLabel {"
            "  background-color: #9E9E9E;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
        "passed": (
            "QLabel {"
            "  background-color: #4CAF50;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
        "failed": (
            "QLabel {"
            "  background-color: #F44336;"
            "  color: #FFFFFF;"
            "  border-radius: 10px;"
            "  padding: 2px 10px;"
            "  font-weight: bold;"
            "  font-size: 12px;"
            "}"
        ),
    }

    # ============================================================
    # 公开 API
    # ============================================================

    def __init__(
        self,
        status: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        """初始化状态标签。

        Args:
            status: 状态值（如 "created"、"passed" 等）。
            parent: 父级 Widget（可选）。

        Raises:
            ValueError: 传入未知的状态值。
        """
        super().__init__(parent)
        self._status: Optional[str] = None
        self.set_status(status)
        logger.debug("StatusBadge 初始化: status=%s", status)

    def set_status(self, status: str) -> None:
        """设置状态并刷新标签显示。

        同步更新文字、样式、Property。

        Args:
            status: 状态值（如 "created"、"passed" 等）。

        Raises:
            ValueError: 传入未知的状态值。
        """
        if status not in self.STATUS_TEXT:
            raise ValueError(
                f"未知状态: {status!r}，"
                f"支持的状态: {list(self.STATUS_TEXT.keys())}"
            )

        self._status = status
        self.setText(self.STATUS_TEXT[status])
        self.setStyleSheet(self.STATUS_STYLE[status])
        self.setProperty("status", status)
        logger.debug("StatusBadge 状态更新: %s", status)

    @property
    def status(self) -> Optional[str]:
        """获取当前状态值。

        Returns:
            Optional[str]: 当前状态值，未设置时为 None。
        """
        return self._status


__all__ = [
    "StatusBadge",
]
