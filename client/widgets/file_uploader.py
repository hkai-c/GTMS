"""GTMS 通用文件上传组件 (FileUploader)

Sprint 6 — Task 6.6
严格依据 CODE_WIKI §15.6、§15.8、Sprint 2~6 Frozen API。

可复用的文件上传组件，包含文件路径展示 + 浏览/上传/清除按钮。
支持文件类型过滤、文件大小校验、动态配置。
发射 file_selected / upload_requested / cleared Signal，不执行实际上传。

Usage:
    uploader = FileUploader(parent=self)
    uploader.file_selected.connect(on_file_selected)
    uploader.upload_requested.connect(on_upload_requested)
    uploader.set_filter("Images (*.jpg *.png)")
    path = uploader.selected_file()
    uploader.clear()
"""

import logging
import os
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量
# ============================================================

DEFAULT_FILTER: str = "All Files (*.*)"
"""默认文件过滤器。"""

DEFAULT_MAX_FILE_SIZE: int = 10 * 1024 * 1024
"""默认最大文件大小（10 MB）。"""

DEFAULT_PLACEHOLDER: str = "请选择文件..."
"""默认路径输入框占位符。"""

BUTTON_TEXT_BROWSE: str = "浏览"
"""浏览按钮文字。"""

BUTTON_TEXT_UPLOAD: str = "上传"
"""上传按钮文字。"""

BUTTON_TEXT_CLEAR: str = "清除"
"""清除按钮文字。"""

OBJECT_NAME_PATH_EDIT: str = "file_path_edit"
"""文件路径输入框 ObjectName。"""

OBJECT_NAME_BROWSE_BUTTON: str = "browse_button"
"""浏览按钮 ObjectName。"""

OBJECT_NAME_UPLOAD_BUTTON: str = "upload_button"
"""上传按钮 ObjectName。"""

OBJECT_NAME_CLEAR_BUTTON: str = "clear_button"
"""清除按钮 ObjectName。"""

LOGGER_NAME: str = "gtms.client"
"""Logger 名称。"""

MESSAGE_TITLE_ERROR: str = "文件校验失败"
"""校验失败弹窗标题。"""

MESSAGE_TEXT_SIZE_TOO_LARGE: str = "文件大小超过限制（最大 {size_mb:.1f} MB）"
"""文件大小超限提示文本模板。"""

MESSAGE_TEXT_EXTENSION_INVALID: str = "文件格式不支持，允许的格式: {extensions}"
"""文件扩展名无效提示文本模板。"""

SIZE_MB_DIVISOR: int = 1024 * 1024
"""字节转 MB 的除数。"""


class FileUploader(QWidget):
    """GTMS 通用文件上传组件。

    包含 QLineEdit（文件路径展示）+ 浏览/上传/清除 QPushButton，使用 QHBoxLayout 布局。
    纯 UI 组件，不实现 HTTP 上传、不调用 ApiClient、不执行任何业务逻辑。

    Attributes:
        file_selected: 文件选择信号，参数为选中文件路径。
        upload_requested: 上传请求信号，参数为当前文件路径。
        cleared: 清除信号，无参数。

    Usage:
        uploader = FileUploader(parent=self)
        uploader.file_selected.connect(self._on_file_selected)
        uploader.upload_requested.connect(self._on_upload_requested)
        uploader.set_filter("Images (*.jpg *.png)")
        uploader.set_max_file_size(5 * 1024 * 1024)
    """

    # ============================================================
    # 信号定义
    # ============================================================

    file_selected: Signal = Signal(str)
    """文件选择信号，参数为选中文件的完整路径。"""

    upload_requested: Signal = Signal(str)
    """上传请求信号，参数为当前文件路径。"""

    cleared: Signal = Signal()
    """清除信号，无参数。"""

    # ============================================================
    # 公开 API
    # ============================================================

    def __init__(
        self,
        placeholder: str = DEFAULT_PLACEHOLDER,
        browse_text: str = BUTTON_TEXT_BROWSE,
        upload_text: str = BUTTON_TEXT_UPLOAD,
        clear_text: str = BUTTON_TEXT_CLEAR,
        parent: Optional[QWidget] = None,
    ) -> None:
        """初始化文件上传组件。

        Args:
            placeholder: 文件路径输入框占位符（可选）。
            browse_text: 浏览按钮文字（可选）。
            upload_text: 上传按钮文字（可选）。
            clear_text: 清除按钮文字（可选）。
            parent: 父级 Widget（可选）。
        """
        super().__init__(parent)

        # ---- 内部状态 ----
        self._filter: str = DEFAULT_FILTER
        self._max_file_size: int = DEFAULT_MAX_FILE_SIZE
        self._default_dir: str = ""

        # ---- 布局 ----
        self._layout: QHBoxLayout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # ---- 文件路径输入框 ----
        self._path_edit: QLineEdit = QLineEdit()
        self._path_edit.setObjectName(OBJECT_NAME_PATH_EDIT)
        self._path_edit.setPlaceholderText(placeholder)
        self._path_edit.setReadOnly(True)
        self._path_edit.setToolTip("选中文件的完整路径")

        # ---- 浏览按钮 ----
        self._browse_button: QPushButton = QPushButton(browse_text)
        self._browse_button.setObjectName(OBJECT_NAME_BROWSE_BUTTON)
        self._browse_button.setToolTip("选择文件")
        self._browse_button.clicked.connect(self._on_browse)

        # ---- 上传按钮 ----
        self._upload_button: QPushButton = QPushButton(upload_text)
        self._upload_button.setObjectName(OBJECT_NAME_UPLOAD_BUTTON)
        self._upload_button.setToolTip("上传文件到服务器")
        self._upload_button.clicked.connect(self._on_upload)

        # ---- 清除按钮 ----
        self._clear_button: QPushButton = QPushButton(clear_text)
        self._clear_button.setObjectName(OBJECT_NAME_CLEAR_BUTTON)
        self._clear_button.setToolTip("清除已选文件")
        self._clear_button.clicked.connect(self._on_clear)

        # ---- 组装布局 ----
        self._layout.addWidget(self._path_edit)
        self._layout.addWidget(self._browse_button)
        self._layout.addWidget(self._upload_button)
        self._layout.addWidget(self._clear_button)

        logger.debug(
            "FileUploader 初始化: placeholder=%r, browse=%r, upload=%r, clear=%r",
            placeholder, browse_text, upload_text, clear_text,
        )

    def selected_file(self) -> Optional[str]:
        """获取当前选中的文件路径。

        Returns:
            Optional[str]: 当前文件路径，未选择时返回 None。
        """
        text = self._path_edit.text().strip()
        return text if text else None

    def clear(self) -> None:
        """清空文件路径和输入框。

        不影响 Placeholder、Filter、最大文件大小设置。
        发射 cleared 信号。
        """
        self._path_edit.clear()
        logger.debug("FileUploader 已清除")
        self.cleared.emit()

    def set_filter(self, filter_text: str) -> None:
        """设置文件类型过滤器。

        Args:
            filter_text: 文件过滤器字符串（如 "Images (*.jpg *.png)"）。

        Raises:
            ValueError: filter_text 为空字符串。
        """
        if not filter_text:
            raise ValueError("filter_text 不能为空")
        self._filter = filter_text
        logger.debug("FileUploader filter 已更新: %r", filter_text)

    def set_max_file_size(self, size: int) -> None:
        """设置最大文件大小限制。

        Args:
            size: 最大文件大小（字节），必须 > 0。

        Raises:
            ValueError: size 不是正整数。
        """
        if size <= 0:
            raise ValueError(f"max_file_size 必须为正整数，当前值: {size}")
        self._max_file_size = size
        logger.debug("FileUploader max_file_size 已更新: %d", size)

    def set_placeholder(self, text: str) -> None:
        """设置路径输入框占位符文本。

        Args:
            text: 占位符文本。
        """
        self._path_edit.setPlaceholderText(text)
        logger.debug("FileUploader placeholder 已更新: %r", text)

    def set_default_dir(self, directory: str) -> None:
        """设置默认打开目录。

        Args:
            directory: 默认目录路径。
        """
        self._default_dir = directory
        logger.debug("FileUploader default_dir 已更新: %r", directory)

    def set_button_texts(
        self,
        browse: Optional[str] = None,
        upload: Optional[str] = None,
        clear: Optional[str] = None,
    ) -> None:
        """动态设置按钮文字。

        Args:
            browse: 浏览按钮文字（可选，None 不更新）。
            upload: 上传按钮文字（可选，None 不更新）。
            clear: 清除按钮文字（可选，None 不更新）。
        """
        if browse is not None:
            self._browse_button.setText(browse)
        if upload is not None:
            self._upload_button.setText(upload)
        if clear is not None:
            self._clear_button.setText(clear)
        logger.debug("FileUploader 按钮文字已更新")

    # ============================================================
    # 私有方法
    # ============================================================

    def _on_browse(self) -> None:
        """浏览按钮回调（内部使用）。

        打开 QFileDialog，选择文件后校验扩展名和大小，
        校验通过后更新路径并发射 file_selected 信号。
        """
        start_dir = self._default_dir if self._default_dir else ""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            start_dir,
            self._filter,
        )
        if not file_path:
            return

        # 校验文件扩展名
        if not self._validate_extension(file_path):
            return

        # 校验文件大小
        if not self._validate_file_size(file_path):
            return

        self._path_edit.setText(file_path)
        logger.debug("文件已选择: %r", file_path)
        self.file_selected.emit(file_path)

    def _on_upload(self) -> None:
        """上传按钮回调（内部使用）。

        校验当前路径不为空，发射 upload_requested 信号。
        不执行实际上传逻辑。
        """
        file_path = self.selected_file()
        if not file_path:
            QMessageBox.warning(
                self,
                "提示",
                "请先选择文件",
            )
            return
        logger.info("上传请求: %r", file_path)
        self.upload_requested.emit(file_path)

    def _on_clear(self) -> None:
        """清除按钮回调（内部使用）。

        调用 clear() 清空内容并发射 cleared 信号。
        """
        self.clear()

    def _validate_extension(self, file_path: str) -> bool:
        """校验文件扩展名是否匹配当前过滤器。

        Args:
            file_path: 文件路径。

        Returns:
            bool: 校验通过返回 True，否则弹出提示并返回 False。
        """
        # 如果过滤器是 All Files (*.*)，跳过校验
        if self._filter == DEFAULT_FILTER:
            return True

        # 提取允许的扩展名列表
        import re
        match = re.findall(r"\*\.(\w+)", self._filter)
        if not match:
            return True

        allowed_extensions = set(match)
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        if ext not in allowed_extensions:
            extensions_str = ", ".join(sorted(allowed_extensions))
            QMessageBox.warning(
                self,
                MESSAGE_TITLE_ERROR,
                MESSAGE_TEXT_EXTENSION_INVALID.format(
                    extensions=extensions_str,
                ),
            )
            return False
        return True

    def _validate_file_size(self, file_path: str) -> bool:
        """校验文件大小是否超过限制。

        Args:
            file_path: 文件路径。

        Returns:
            bool: 校验通过返回 True，否则弹出提示并返回 False。
        """
        try:
            file_size = os.path.getsize(file_path)
        except OSError:
            QMessageBox.warning(
                self,
                MESSAGE_TITLE_ERROR,
                "无法读取文件信息",
            )
            return False

        if file_size > self._max_file_size:
            size_mb = self._max_file_size / SIZE_MB_DIVISOR
            QMessageBox.warning(
                self,
                MESSAGE_TITLE_ERROR,
                MESSAGE_TEXT_SIZE_TOO_LARGE.format(size_mb=size_mb),
            )
            return False
        return True


__all__ = [
    "FileUploader",
]
