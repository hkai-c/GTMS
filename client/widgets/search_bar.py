"""GTMS 全局统一搜索组件 (SearchBar)

Sprint 5 — Task 5.6
严格依据 UI_PROTOTYPE §6.2。

可复用的搜索栏组件，包含输入框 + 搜索按钮。
支持点击搜索按钮、按 Enter、按 Return 触发搜索。
发射 search_requested Signal，不执行搜索逻辑。

Usage:
    search_bar = SearchBar(placeholder="请输入关键字...", button_text="搜索")
    search_bar.search_requested.connect(on_search)
    current_text = search_bar.text()
    search_bar.clear()
"""

import logging
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)

logger = logging.getLogger("gtms.client")


class SearchBar(QWidget):
    """GTMS 全局统一搜索组件。

    包含 QLineEdit 输入框 + QPushButton 搜索按钮，使用 QHBoxLayout 布局。
    支持点击按钮、按 Enter、按 Return 三种方式触发搜索。
    发射 search_requested Signal，不执行实际搜索逻辑。

    Attributes:
        search_requested: 搜索请求信号，参数为当前输入的关键字。

    Usage:
        search_bar = SearchBar(parent=self)
        search_bar.search_requested.connect(self._on_search)
    """

    # ============================================================
    # 信号定义
    # ============================================================

    search_requested: Signal = Signal(str)
    """搜索请求信号，参数为当前输入的关键字。"""

    # ============================================================
    # 公开 API
    # ============================================================

    def __init__(
        self,
        placeholder: str = "请输入关键字...",
        button_text: str = "搜索",
        parent: Optional[QWidget] = None,
    ) -> None:
        """初始化搜索栏。

        Args:
            placeholder: 输入框占位符（可选，默认: "请输入关键字..."）。
            button_text: 搜索按钮文字（可选，默认: "搜索"）。
            parent: 父级 Widget（可选）。
        """
        super().__init__(parent)

        self._layout: QHBoxLayout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        self._search_input: QLineEdit = QLineEdit()
        self._search_input.setPlaceholderText(placeholder)
        self._search_input.returnPressed.connect(self._on_search_triggered)

        self._search_button: QPushButton = QPushButton(button_text)
        self._search_button.clicked.connect(self._on_search_triggered)

        self._layout.addWidget(self._search_input)
        self._layout.addWidget(self._search_button)

        self._placeholder: str = placeholder

        logger.debug(
            "SearchBar 初始化: placeholder=%r, button_text=%r",
            placeholder,
            button_text,
        )

    def text(self) -> str:
        """获取当前输入框内容。

        Returns:
            str: 当前输入的关键字（可能为空字符串）。
        """
        return self._search_input.text().strip()

    def set_text(self, text: str) -> None:
        """设置输入框内容。

        Args:
            text: 要设置的文本。
        """
        self._search_input.setText(text)

    def clear(self) -> None:
        """清空输入框内容。

        不影响 Placeholder 设置。
        """
        self._search_input.clear()

    def set_placeholder(self, text: str) -> None:
        """设置占位符文本。

        Args:
            text: 占位符文本。
        """
        self._placeholder = text
        self._search_input.setPlaceholderText(text)

    def placeholder(self) -> str:
        """获取当前占位符文本。

        Returns:
            str: 当前占位符文本。
        """
        return self._placeholder

    # ============================================================
    # 私有方法
    # ============================================================

    def _on_search_triggered(self) -> None:
        """搜索触发回调（内部使用）。

        由 QLineEdit.returnPressed 和 QPushButton.clicked 共同触发。
        发射 search_requested Signal，参数为当前输入内容。
        """
        keyword = self.text()
        logger.debug("搜索触发: keyword=%r", keyword)
        self.search_requested.emit(keyword)


__all__ = [
    "SearchBar",
]
