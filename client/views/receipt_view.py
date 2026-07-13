"""GTMS 桌面端收件登记页面 (ReceiptView)

Sprint 6 — Task 6.8
严格依据 UI_PROTOTYPE §9、SRS §4.4、CODE_WIKI §15.5/§15.6/§15.7/§15.8。

提供收件登记管理界面：
    - 收件记录列表（QTableWidget）
    - 搜索（SearchBar Widget）
    - 新增/编辑/删除收件记录
    - 分页（第一页/上一页/下一页/最后一页）
    - StatusBar
    - 图片上传（FileUploader Widget）
    - 图片预览（ImageViewer Widget）

所有业务逻辑委托 Desktop ReceiptService，禁止直接 HTTP。
"""

import logging
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client.services.receipt_service import ReceiptService
from client.widgets.file_uploader import FileUploader
from client.widgets.image_viewer import ImageViewer
from client.widgets.search_bar import SearchBar

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义
# ============================================================

WINDOW_TITLE: str = "收件登记管理"

TABLE_HEADERS: list[str] = [
    "ID",
    "任务ID",
    "收件时间",
    "收件人ID",
    "图片路径",
    "创建时间",
]

COLUMN_INDEX: dict[str, int] = {
    "id": 0,
    "task_id": 1,
    "received_at": 2,
    "receiver_id": 3,
    "image_paths": 4,
    "created_at": 5,
}

DEFAULT_PAGE_SIZE: int = 20

BUTTON_TEXT: dict[str, str] = {
    "add": "新增",
    "edit": "编辑",
    "delete": "删除",
    "refresh": "刷新",
    "first_page": "第一页",
    "prev_page": "上一页",
    "next_page": "下一页",
    "last_page": "最后一页",
    "search": "搜索",
    "upload": "上传",
    "clear": "清除",
    "browse": "浏览",
}

OBJECT_NAMES: dict[str, str] = {
    "toolbar": "toolbar",
    "search_bar": "search_bar",
    "receipt_table": "receipt_table",
    "pagination_widget": "pagination_widget",
    "status_bar": "status_bar",
    "add_btn": "add_btn",
    "edit_btn": "edit_btn",
    "delete_btn": "delete_btn",
    "refresh_btn": "refresh_btn",
    "first_page_btn": "first_page_btn",
    "prev_page_btn": "prev_page_btn",
    "next_page_btn": "next_page_btn",
    "last_page_btn": "last_page_btn",
    "page_label": "page_label",
    "total_label": "total_label",
    "title_label": "title_label",
    "file_uploader": "file_uploader",
    "image_viewer": "image_viewer",
    "upload_section_label": "upload_section_label",
    "preview_section_label": "preview_section_label",
}

LOGGER_NAME: str = "gtms.client"


class ReceiptView(QWidget):
    """GTMS 桌面端收件登记管理页面。

    提供收件记录查询、新增、编辑、删除界面，支持分页和搜索。
    集成 FileUploader 和 ImageViewer 实现图片上传和预览。

    Signals:
        receipt_changed: 收件记录变更（新增/编辑/删除后发射）。

    Attributes:
        _receipt_service: ReceiptService 实例。
        _receipts: 当前收件记录列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。
        _search_keyword: 当前搜索关键词。

    Usage:
        view = ReceiptView(receipt_service)
        view.receipt_changed.connect(on_receipt_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    receipt_changed: Signal = Signal()
    """收件记录变更信号（新增/编辑/删除后发射）。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        receipt_service: ReceiptService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化收件登记管理页面。

        Args:
            receipt_service: ReceiptService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._receipt_service: ReceiptService = receipt_service
        self._receipts: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total: int = 0
        self._search_keyword: str = ""

        self._setup_ui()
        self._update_button_permissions()

        logger.debug("ReceiptView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建收件登记管理页面 UI。

        标准布局: 标题 → Toolbar → Table → Pagination → StatusBar
        → FileUploader → ImageViewer。
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # --- 标题 ---
        self._title_label = QLabel(WINDOW_TITLE)
        self._title_label.setObjectName(OBJECT_NAMES["title_label"])
        self._title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #333333;"
        )
        layout.addWidget(self._title_label)

        # --- 工具栏 ---
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)

        # --- 表格 ---
        self._table = self._create_table()
        layout.addWidget(self._table, 1)

        # --- 分页栏 ---
        pagination = self._create_pagination()
        layout.addLayout(pagination)

        # --- 状态栏 ---
        self._status_bar = self._create_status_bar()
        layout.addWidget(self._status_bar)

        # --- 上传区域 ---
        upload_section = self._create_upload_section()
        layout.addLayout(upload_section)

        # --- 图片预览区域 ---
        preview_section = self._create_preview_section()
        layout.addLayout(preview_section)

    # ============================================================
    # 工具栏
    # ============================================================

    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏。

        Returns:
            QHBoxLayout: 工具栏布局。
        """
        toolbar = QHBoxLayout()
        toolbar.setObjectName(OBJECT_NAMES["toolbar"])
        toolbar.setSpacing(6)

        # 新增
        self._add_btn = QPushButton(BUTTON_TEXT["add"])
        self._add_btn.setObjectName(OBJECT_NAMES["add_btn"])
        self._add_btn.setFixedHeight(30)
        self._add_btn.clicked.connect(self._on_add)
        toolbar.addWidget(self._add_btn)

        # 编辑
        self._edit_btn = QPushButton(BUTTON_TEXT["edit"])
        self._edit_btn.setObjectName(OBJECT_NAMES["edit_btn"])
        self._edit_btn.setFixedHeight(30)
        self._edit_btn.clicked.connect(self._on_edit)
        toolbar.addWidget(self._edit_btn)

        # 删除
        self._delete_btn = QPushButton(BUTTON_TEXT["delete"])
        self._delete_btn.setObjectName(OBJECT_NAMES["delete_btn"])
        self._delete_btn.setFixedHeight(30)
        self._delete_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self._delete_btn)

        # 刷新
        self._refresh_btn = QPushButton(BUTTON_TEXT["refresh"])
        self._refresh_btn.setObjectName(OBJECT_NAMES["refresh_btn"])
        self._refresh_btn.setFixedHeight(30)
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)

        # 弹性空间
        toolbar.addStretch()

        # 搜索栏
        self._search_bar = SearchBar(
            placeholder="请输入收件记录关键字...",
            button_text=BUTTON_TEXT["search"],
            parent=self,
        )
        self._search_bar.setObjectName(OBJECT_NAMES["search_bar"])
        self._search_bar.search_requested.connect(self._on_search)
        toolbar.addWidget(self._search_bar)

        return toolbar

    # ============================================================
    # 表格
    # ============================================================

    def _create_table(self) -> QTableWidget:
        """创建收件记录列表表格。

        Returns:
            QTableWidget: 收件记录列表表格。
        """
        table = QTableWidget()
        table.setObjectName(OBJECT_NAMES["receipt_table"])
        table.setColumnCount(len(TABLE_HEADERS))
        table.setHorizontalHeaderLabels(TABLE_HEADERS)

        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        table.setAlternatingRowColors(True)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStyleSheet(
            "QHeaderView::section {"
            "  background-color: #fafafa;"
            "  border: none;"
            "  border-bottom: 1px solid #e8e8e8;"
            "  padding: 6px;"
            "  font-weight: bold;"
            "}"
        )

        table.setStyleSheet(
            "QTableWidget {"
            "  border: 1px solid #e8e8e8;"
            "  gridline-color: #f0f0f0;"
            "  background-color: #ffffff;"
            "  alternate-background-color: #fafafa;"
            "}"
            "QTableWidget::item {"
            "  padding: 4px 8px;"
            "}"
        )

        return table

    # ============================================================
    # 分页栏
    # ============================================================

    def _create_pagination(self) -> QHBoxLayout:
        """创建分页栏。

        Returns:
            QHBoxLayout: 分页栏布局。
        """
        pagination = QHBoxLayout()
        pagination.setSpacing(6)

        # 第一页
        self._first_page_btn = QPushButton(BUTTON_TEXT["first_page"])
        self._first_page_btn.setObjectName(OBJECT_NAMES["first_page_btn"])
        self._first_page_btn.setFixedHeight(28)
        self._first_page_btn.clicked.connect(self._on_first_page)
        pagination.addWidget(self._first_page_btn)

        # 上一页
        self._prev_page_btn = QPushButton(BUTTON_TEXT["prev_page"])
        self._prev_page_btn.setObjectName(OBJECT_NAMES["prev_page_btn"])
        self._prev_page_btn.setFixedHeight(28)
        self._prev_page_btn.clicked.connect(self._on_prev_page)
        pagination.addWidget(self._prev_page_btn)

        # 当前页
        self._page_label = QLabel("第 1 页")
        self._page_label.setObjectName(OBJECT_NAMES["page_label"])
        self._page_label.setStyleSheet("font-size: 12px; color: #333333;")
        pagination.addWidget(self._page_label)

        # 下一页
        self._next_page_btn = QPushButton(BUTTON_TEXT["next_page"])
        self._next_page_btn.setObjectName(OBJECT_NAMES["next_page_btn"])
        self._next_page_btn.setFixedHeight(28)
        self._next_page_btn.clicked.connect(self._on_next_page)
        pagination.addWidget(self._next_page_btn)

        # 最后一页
        self._last_page_btn = QPushButton(BUTTON_TEXT["last_page"])
        self._last_page_btn.setObjectName(OBJECT_NAMES["last_page_btn"])
        self._last_page_btn.setFixedHeight(28)
        self._last_page_btn.clicked.connect(self._on_last_page)
        pagination.addWidget(self._last_page_btn)

        pagination.addStretch()

        # 共 XX 条记录
        self._total_label = QLabel("共 0 条记录")
        self._total_label.setObjectName(OBJECT_NAMES["total_label"])
        self._total_label.setStyleSheet(
            "font-size: 11px; color: #888888;"
        )
        pagination.addWidget(self._total_label)

        return pagination

    # ============================================================
    # 状态栏
    # ============================================================

    def _create_status_bar(self) -> QLabel:
        """创建状态栏。

        Returns:
            QLabel: 状态栏标签。
        """
        status_bar = QLabel("就绪")
        status_bar.setObjectName(OBJECT_NAMES["status_bar"])
        status_bar.setStyleSheet(
            "font-size: 11px; color: #888888;"
            "padding: 4px 0px;"
        )
        return status_bar

    # ============================================================
    # 上传区域
    # ============================================================

    def _create_upload_section(self) -> QHBoxLayout:
        """创建上传区域。

        Returns:
            QHBoxLayout: 上传区域布局。
        """
        upload_section = QHBoxLayout()
        upload_section.setSpacing(8)

        # 上传标签
        label = QLabel("图片上传：")
        label.setObjectName(OBJECT_NAMES["upload_section_label"])
        label.setStyleSheet("font-size: 12px; font-weight: bold;")
        upload_section.addWidget(label)

        # FileUploader
        self._file_uploader = FileUploader(
            browse_text=BUTTON_TEXT["browse"],
            upload_text=BUTTON_TEXT["upload"],
            clear_text=BUTTON_TEXT["clear"],
            parent=self,
        )
        self._file_uploader.setObjectName(OBJECT_NAMES["file_uploader"])
        self._file_uploader.set_filter("Images (*.jpg *.jpeg *.png)")
        self._file_uploader.upload_requested.connect(self._on_upload)
        self._file_uploader.file_selected.connect(self._on_file_selected)
        upload_section.addWidget(self._file_uploader, 1)

        return upload_section

    # ============================================================
    # 图片预览区域
    # ============================================================

    def _create_preview_section(self) -> QVBoxLayout:
        """创建图片预览区域。

        Returns:
            QVBoxLayout: 图片预览区域布局。
        """
        preview_section = QVBoxLayout()
        preview_section.setSpacing(4)

        # 预览标签
        label = QLabel("图片预览：")
        label.setObjectName(OBJECT_NAMES["preview_section_label"])
        label.setStyleSheet("font-size: 12px; font-weight: bold;")
        preview_section.addWidget(label)

        # ImageViewer
        self._image_viewer = ImageViewer(parent=self)
        self._image_viewer.setObjectName(OBJECT_NAMES["image_viewer"])
        self._image_viewer.setFixedHeight(200)
        preview_section.addWidget(self._image_viewer)

        return preview_section

    # ============================================================
    # 数据和分页 — 刷新流程
    # ============================================================

    def refresh(self) -> None:
        """刷新收件记录列表。

        调用 ReceiptService.list_receipts() 加载数据到表格。
        重新从当前页请求服务器，不使用本地缓存。
        """
        try:
            keyword = self._search_keyword or None
            data = self._receipt_service.list_receipts(
                keyword=keyword,
                page=self._current_page,
                page_size=self._page_size,
            )
            self._receipts = data.get("items", [])
            self._total = data.get("total", 0)
            self._populate_table(self._receipts)
            self._update_pagination_ui()
            self._update_status_bar("刷新完成")
            logger.info(
                "收件记录列表刷新: page=%d, total=%d, keyword=%r",
                self._current_page,
                self._total,
                self._search_keyword,
            )
        except Exception as e:
            logger.error("刷新收件记录列表失败: %s", e)
            QMessageBox.critical(self, "加载失败", f"加载收件记录列表失败: {e}")

    def _populate_table(self, receipts: list[dict[str, Any]]) -> None:
        """填充表格数据。

        Args:
            receipts: 收件记录列表。
        """
        self._table.setRowCount(len(receipts))
        for row, receipt in enumerate(receipts):
            # ID
            self._table.setItem(
                row, COLUMN_INDEX["id"],
                QTableWidgetItem(str(receipt.get("id", ""))),
            )
            # 任务ID
            self._table.setItem(
                row, COLUMN_INDEX["task_id"],
                QTableWidgetItem(str(receipt.get("task_id", ""))),
            )
            # 收件时间
            received_at = receipt.get("received_at", "")
            self._table.setItem(
                row, COLUMN_INDEX["received_at"],
                QTableWidgetItem(str(received_at)),
            )
            # 收件人ID
            self._table.setItem(
                row, COLUMN_INDEX["receiver_id"],
                QTableWidgetItem(str(receipt.get("receiver_id", ""))),
            )
            # 图片路径
            self._table.setItem(
                row, COLUMN_INDEX["image_paths"],
                QTableWidgetItem(str(receipt.get("image_paths", ""))),
            )
            # 创建时间
            created_at = receipt.get("created_at", "")
            self._table.setItem(
                row, COLUMN_INDEX["created_at"],
                QTableWidgetItem(str(created_at)),
            )

    def _update_pagination_ui(self) -> None:
        """更新分页栏 UI 状态。"""
        total_pages = max(
            1, (self._total + self._page_size - 1) // self._page_size
        )

        self._page_label.setText(
            f"第 {self._current_page} / {total_pages} 页"
        )
        self._total_label.setText(f"共 {self._total} 条记录")

        self._first_page_btn.setEnabled(self._current_page > 1)
        self._prev_page_btn.setEnabled(self._current_page > 1)
        self._next_page_btn.setEnabled(self._current_page < total_pages)
        self._last_page_btn.setEnabled(self._current_page < total_pages)

    def _update_status_bar(self, message: str) -> None:
        """更新状态栏消息。

        Args:
            message: 状态消息。
        """
        self._status_bar.setText(message)

    # ============================================================
    # 分页操作
    # ============================================================

    def _on_first_page(self) -> None:
        """跳转到第一页。"""
        self._current_page = 1
        self.refresh()

    def _on_prev_page(self) -> None:
        """跳转到上一页。"""
        if self._current_page > 1:
            self._current_page -= 1
            self.refresh()

    def _on_next_page(self) -> None:
        """跳转到下一页。"""
        total_pages = max(
            1, (self._total + self._page_size - 1) // self._page_size
        )
        if self._current_page < total_pages:
            self._current_page += 1
            self.refresh()

    def _on_last_page(self) -> None:
        """跳转到最后一页。"""
        total_pages = max(
            1, (self._total + self._page_size - 1) // self._page_size
        )
        self._current_page = total_pages
        self.refresh()

    # ============================================================
    # 搜索
    # ============================================================

    def _on_search(self, keyword: str) -> None:
        """按关键字搜索。

        SearchBar 发射 search_requested Signal，重置到第一页。

        Args:
            keyword: 搜索关键词。
        """
        self._search_keyword = keyword
        self._current_page = 1
        self.refresh()

    # ============================================================
    # 新增收件记录
    # ============================================================

    def _on_add(self) -> None:
        """新增收件记录。

        ReceiptDialog 未实现，暂显示提示。
        完成后的流程：
        ReceiptDialog → create_receipt() → refresh() → emit receipt_changed。
        """
        QMessageBox.information(
            self, "功能提示", "新增收件记录功能将在后续实现。"
        )

    # ============================================================
    # 编辑收件记录
    # ============================================================

    def _on_edit(self) -> None:
        """编辑收件记录。

        ReceiptDialog 未实现，暂显示提示。
        完成后的流程：
        选中行 → ReceiptDialog → update_receipt() → refresh()
        → emit receipt_changed。
        """
        QMessageBox.information(
            self, "功能提示", "编辑收件记录功能将在后续实现。"
        )

    # ============================================================
    # 删除收件记录
    # ============================================================

    def _on_delete(self) -> None:
        """删除收件记录。

        确认 → delete_receipt() → refresh() → emit receipt_changed。
        """
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要删除的收件记录")
            return

        receipt = self._receipts[row]
        receipt_id = receipt.get("id")

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除收件记录 #{receipt_id} 吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._receipt_service.delete_receipt(receipt_id)
            self.refresh()
            self.receipt_changed.emit()
            logger.info("收件记录删除完成: receipt_id=%d", receipt_id)
        except Exception as e:
            logger.error("删除收件记录失败: %s", e)
            QMessageBox.critical(self, "删除失败", f"删除收件记录失败: {e}")

    # ============================================================
    # 上传图片
    # ============================================================

    def _on_upload(self, file_path: str) -> None:
        """上传图片到服务器。

        FileUploader 发射 upload_requested Signal。
        调用 ReceiptService.upload_receipt_image() 上传图片。

        Args:
            file_path: 待上传的文件路径。
        """
        row = self._table.currentRow()
        task_no = ""
        if row >= 0:
            receipt = self._receipts[row]
            task_no = str(receipt.get("task_id", ""))

        if not task_no:
            QMessageBox.warning(
                self, "提示", "请先选择一条收件记录以获取任务编号。"
            )
            return

        try:
            result = self._receipt_service.upload_receipt_image(
                task_no=task_no,
                file_path=file_path,
            )
            self._update_status_bar(f"上传成功: {result.get('filename', '')}")
            self.refresh()
            logger.info(
                "图片上传成功: task_no=%s, file=%s", task_no, file_path,
            )
        except Exception as e:
            logger.error("图片上传失败: %s", e)
            QMessageBox.critical(self, "上传失败", f"图片上传失败: {e}")

    def _on_file_selected(self, file_path: str) -> None:
        """文件选择后预览图片。

        FileUploader 发射 file_selected Signal。
        调用 ImageViewer.load_image() 预览图片。

        Args:
            file_path: 选中的文件路径。
        """
        self._image_viewer.load_image(file_path)
        self._update_status_bar(f"已选择: {file_path}")

    # ============================================================
    # 权限管理
    # ============================================================

    def _update_button_permissions(self) -> None:
        """更新按钮权限状态。

        统一管理按钮启用/禁用状态。
        当前为默认实现，后续可接入权限系统。
        """
        self._add_btn.setEnabled(True)
        self._edit_btn.setEnabled(True)
        self._delete_btn.setEnabled(True)
        self._refresh_btn.setEnabled(True)


__all__ = [
    "ReceiptView",
]
