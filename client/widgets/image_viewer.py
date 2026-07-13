"""GTMS 通用图片查看组件 (ImageViewer)

Sprint 6 — Task 6.7
严格依据 CODE_WIKI §15.6、§15.8、Sprint 2~6 Frozen API。

可复用的图片查看组件，使用 QLabel 显示 QPixmap，支持自动缩放（保持比例）。
包含占位文本，图片加载/清空/失败 Signal 通知。
不实现 HTTP 加载、不调用 ApiClient、不执行任何业务逻辑。

Usage:
    viewer = ImageViewer(parent=self)
    viewer.image_loaded.connect(on_image_loaded)
    viewer.image_load_failed.connect(on_image_load_failed)
    viewer.load_image("/path/to/image.jpg")
    viewer.clear()
    viewer.set_placeholder("请选择图片")
"""

import logging
import os
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量
# ============================================================

DEFAULT_PLACEHOLDER: str = "暂无图片"
"""默认占位文本。"""

SUPPORTED_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png")
"""支持的图片扩展名。"""

OBJECT_NAME_IMAGE_LABEL: str = "image_label"
"""图片显示 QLabel ObjectName。"""

OBJECT_NAME_PLACEHOLDER_LABEL: str = "placeholder_label"
"""占位文本 QLabel ObjectName。"""

LOGGER_NAME: str = "gtms.client"
"""Logger 名称。"""

DEFAULT_ALIGNMENT = Qt.AlignCenter
"""默认对齐方式。"""

DEFAULT_MIN_WIDTH: int = 200
"""默认最小宽度（像素）。"""

DEFAULT_MIN_HEIGHT: int = 150
"""默认最小高度（像素）。"""


class ImageViewer(QWidget):
    """GTMS 通用图片查看组件。

    使用 QLabel 显示 QPixmap，支持 jpg/jpeg/png 格式。
    自动缩放保持比例，包含占位文本和加载状态 Signal。

    Attributes:
        image_loaded: 图片加载成功信号，参数为图片路径。
        image_cleared: 图片清除信号，无参数。
        image_load_failed: 图片加载失败信号，参数为错误原因。

    Usage:
        viewer = ImageViewer(parent=self)
        viewer.image_loaded.connect(self._on_image_loaded)
        viewer.load_image("/path/to/image.jpg")
        viewer.clear()
    """

    # ============================================================
    # 信号定义
    # ============================================================

    image_loaded: Signal = Signal(str)
    """图片加载成功信号，参数为图片路径。"""

    image_cleared: Signal = Signal()
    """图片清除信号，无参数。"""

    image_load_failed: Signal = Signal(str)
    """图片加载失败信号，参数为错误原因。"""

    # ============================================================
    # 公开 API
    # ============================================================

    def __init__(
        self,
        placeholder: str = DEFAULT_PLACEHOLDER,
        parent: Optional[QWidget] = None,
    ) -> None:
        """初始化图片查看组件。

        Args:
            placeholder: 占位文本（可选）。
            parent: 父级 Widget（可选）。
        """
        super().__init__(parent)

        # ---- 内部状态 ----
        self._current_image: Optional[str] = None
        self._original_pixmap: Optional[QPixmap] = None

        # ---- 布局 ----
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # ---- 图片显示 QLabel ----
        self._image_label: QLabel = QLabel()
        self._image_label.setObjectName(OBJECT_NAME_IMAGE_LABEL)
        self._image_label.setAlignment(DEFAULT_ALIGNMENT)
        self._image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._image_label.setToolTip("图片显示区域")
        self._image_label.hide()

        # ---- 占位文本 QLabel ----
        self._placeholder_label: QLabel = QLabel(placeholder)
        self._placeholder_label.setObjectName(OBJECT_NAME_PLACEHOLDER_LABEL)
        self._placeholder_label.setAlignment(DEFAULT_ALIGNMENT)
        self._placeholder_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._placeholder_label.setToolTip("暂无图片加载")
        self._placeholder_label.setStyleSheet("color: #999999;")
        self._placeholder_label.show()

        # ---- 组装布局 ----
        self._layout.addWidget(self._image_label)
        self._layout.addWidget(self._placeholder_label)

        # ---- 最小尺寸 ----
        self.setMinimumSize(DEFAULT_MIN_WIDTH, DEFAULT_MIN_HEIGHT)

        logger.debug("ImageViewer 初始化: placeholder=%r", placeholder)

    def load_image(self, path: str) -> None:
        """加载并显示图片。

        支持 jpg/jpeg/png 格式。加载成功后自动缩放适配窗口，
        显示图片并隐藏占位文本，发射 image_loaded 信号。
        加载失败则显示占位文本，发射 image_load_failed 信号。

        Args:
            path: 图片文件路径。
        """
        # 校验扩展名
        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            error_msg = f"不支持的文件格式: {ext}，仅支持 jpg/jpeg/png"
            logger.warning("图片加载失败: %s", error_msg)
            self._show_placeholder()
            self.image_load_failed.emit(error_msg)
            return

        # 加载 QPixmap
        pixmap = QPixmap(path)
        if pixmap.isNull():
            error_msg = f"无法加载图片: {path}"
            logger.warning("图片加载失败: %s", error_msg)
            self._show_placeholder()
            self.image_load_failed.emit(error_msg)
            return

        self._current_image = path
        self._original_pixmap = pixmap
        self._update_display()
        self._image_label.show()
        self._placeholder_label.hide()
        logger.info(
            "图片加载成功: %r (size=%dx%d)",
            path, pixmap.width(), pixmap.height(),
        )
        self.image_loaded.emit(path)

    def clear(self) -> None:
        """清空图片显示。

        恢复默认状态，显示占位文本，发射 image_cleared 信号。
        """
        self._current_image = None
        self._original_pixmap = None
        self._image_label.clear()
        self._show_placeholder()
        logger.debug("ImageViewer 已清除")
        self.image_cleared.emit()

    def current_image(self) -> Optional[str]:
        """获取当前加载的图片路径。

        Returns:
            Optional[str]: 当前图片路径，未加载时返回 None。
        """
        return self._current_image

    def has_image(self) -> bool:
        """检查是否有图片已加载。

        Returns:
            bool: 已加载图片返回 True。
        """
        return self._current_image is not None

    def set_placeholder(self, text: str) -> None:
        """设置占位文本。

        Args:
            text: 占位文本。
        """
        self._placeholder_label.setText(text)
        logger.debug("ImageViewer placeholder 已更新: %r", text)

    # ============================================================
    # Qt 事件重写
    # ============================================================

    def resizeEvent(self, event) -> None:
        """窗口大小变化时触发自动缩放（内部使用）。

        Args:
            event: QResizeEvent 事件对象。
        """
        super().resizeEvent(event)
        if self._original_pixmap is not None:
            self._update_display()

    # ============================================================
    # 私有方法
    # ============================================================

    def _update_display(self) -> None:
        """根据当前窗口大小缩放并显示图片（内部使用）。

        保持图片原始比例，使用平滑缩放。
        """
        if self._original_pixmap is None:
            return

        available_size = self.size()
        if available_size.width() <= 0 or available_size.height() <= 0:
            return

        scaled_pixmap = self._original_pixmap.scaled(
            available_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled_pixmap)

    def _show_placeholder(self) -> None:
        """显示占位文本，隐藏图片（内部使用）。"""
        self._image_label.hide()
        self._image_label.clear()
        self._placeholder_label.show()


__all__ = [
    "ImageViewer",
]
