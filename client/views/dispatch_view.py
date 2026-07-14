"""GTMS 桌面端工件派发管理页面 (DispatchView)

Sprint 9 — Task 9.5
严格依据 UI_PROTOTYPE §12、SRS §4.7、CODE_WIKI §15.5/§15.7/§15.10/§15.11/§15.12。

提供工件派发记录管理界面：
    - 派发记录列表（QTableWidget）
    - 搜索（SearchBar Widget）
    - 新增去向 / 编辑 / 删除 / 刷新
    - 分页（第一页/上一页/下一页/最后一页）
    - StatusBar

所有业务逻辑委托 Desktop DispatchService，禁止直接 HTTP。
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

from client.services.dispatch_service import DispatchService
from client.widgets.search_bar import SearchBar

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义
# ============================================================

WINDOW_TITLE: str = "派发管理"

TABLE_HEADERS: list[str] = [
    "ID",
    "任务编号",
    "去向方向",
    "去向日期",
    "操作人ID",
    "创建时间",
    "更新时间",
]

COLUMN_INDEX: dict[str, int] = {
    "id": 0,
    "task_id": 1,
    "direction": 2,
    "dispatch_date": 3,
    "operator_id": 4,
    "created_at": 5,
    "updated_at": 6,
}

DEFAULT_PAGE_SIZE: int = 20

BUTTON_TEXT: dict[str, str] = {
    "add": "新增去向",
    "edit": "编辑",
    "delete": "删除",
    "refresh": "刷新",
    "first_page": "第一页",
    "prev_page": "上一页",
    "next_page": "下一页",
    "last_page": "最后一页",
    "search": "搜索",
}

OBJECT_NAMES: dict[str, str] = {
    "title_label": "title_label",
    "toolbar": "toolbar",
    "search_bar": "search_bar",
    "dispatch_table": "dispatch_table",
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
}

STATUS_TEXT: dict[str, str] = {
    "ready": "就绪",
    "refresh_completed": "刷新完成",
}

MESSAGE_TEXT: dict[str, str] = {
    "delete_confirm": "确定要删除该派发记录吗？",
    "delete_title": "确认删除",
    "refresh_failed": "刷新派发记录失败",
    "delete_failed": "删除派发记录失败",
    "add_placeholder": "新增去向功能将在后续版本实现。",
    "edit_placeholder": "编辑功能将在后续版本实现。",
}

LOGGER_NAME: str = "gtms.client"


class DispatchView(QWidget):
    """GTMS 桌面端工件派发管理页面。

    提供派发记录查询、新增去向、编辑、删除界面，支持分页和搜索。

    Signals:
        dispatch_changed: 派发记录变更（新增/编辑/删除后发射）。

    Attributes:
        _dispatch_service: DispatchService 实例。
        _dispatches: 当前派发记录列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。
        _search_task_id: 当前搜索任务编号。

    Usage:
        view = DispatchView(dispatch_service)
        view.dispatch_changed.connect(on_dispatch_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    dispatch_changed: Signal = Signal()
    """派发记录变更信号（新增/编辑/删除后发射）。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        dispatch_service: DispatchService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化工件派发管理页面。

        Args:
            dispatch_service: DispatchService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._dispatch_service: DispatchService = dispatch_service
        self._dispatches: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total: int = 0
        self._search_task_id: int | None = None

        self._setup_ui()
        self._update_button_permissions()

        logger.debug("DispatchView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建工件派发管理页面 UI。

        标准布局: 标题 → Toolbar → Table → Pagination → StatusBar。
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

        # 新增去向
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
            placeholder="请输入任务编号...",
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
        """创建派发记录列表表格。

        Returns:
            QTableWidget: 派发记录列表表格。
        """
        table = QTableWidget()
        table.setObjectName(OBJECT_NAMES["dispatch_table"])
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

        return table

    # ============================================================
    # 分页
    # ============================================================

    def _create_pagination(self) -> QHBoxLayout:
        """创建分页控件。

        Returns:
            QHBoxLayout: 分页控件布局。
        """
        pagination = QHBoxLayout()
        pagination.setObjectName(OBJECT_NAMES["pagination_widget"])
        pagination.setSpacing(6)

        pagination.addStretch()

        self._first_page_btn = QPushButton(BUTTON_TEXT["first_page"])
        self._first_page_btn.setObjectName(OBJECT_NAMES["first_page_btn"])
        self._first_page_btn.setFixedHeight(28)
        self._first_page_btn.clicked.connect(self._on_first_page)
        pagination.addWidget(self._first_page_btn)

        self._prev_page_btn = QPushButton(BUTTON_TEXT["prev_page"])
        self._prev_page_btn.setObjectName(OBJECT_NAMES["prev_page_btn"])
        self._prev_page_btn.setFixedHeight(28)
        self._prev_page_btn.clicked.connect(self._on_prev_page)
        pagination.addWidget(self._prev_page_btn)

        self._page_label = QLabel("1 / 1")
        self._page_label.setObjectName(OBJECT_NAMES["page_label"])
        self._page_label.setStyleSheet("padding: 0 8px;")
        pagination.addWidget(self._page_label)

        self._next_page_btn = QPushButton(BUTTON_TEXT["next_page"])
        self._next_page_btn.setObjectName(OBJECT_NAMES["next_page_btn"])
        self._next_page_btn.setFixedHeight(28)
        self._next_page_btn.clicked.connect(self._on_next_page)
        pagination.addWidget(self._next_page_btn)

        self._last_page_btn = QPushButton(BUTTON_TEXT["last_page"])
        self._last_page_btn.setObjectName(OBJECT_NAMES["last_page_btn"])
        self._last_page_btn.setFixedHeight(28)
        self._last_page_btn.clicked.connect(self._on_last_page)
        pagination.addWidget(self._last_page_btn)

        pagination.addStretch()

        self._total_label = QLabel("共 0 条")
        self._total_label.setObjectName(OBJECT_NAMES["total_label"])
        pagination.addWidget(self._total_label)

        return pagination

    # ============================================================
    # 状态栏
    # ============================================================

    def _create_status_bar(self) -> QLabel:
        """创建状态栏。

        Returns:
            QLabel: 状态栏控件。
        """
        status_bar = QLabel(STATUS_TEXT["ready"])
        status_bar.setObjectName(OBJECT_NAMES["status_bar"])
        status_bar.setStyleSheet(
            "color: #888888; font-size: 12px; padding: 4px 0;"
        )
        return status_bar

    # ============================================================
    # 公开 API：刷新
    # ============================================================

    def refresh(self) -> None:
        """刷新派发记录列表。

        唯一刷新入口，所有操作（新增/编辑/删除/搜索/分页）成功后统一调用。
        内部流程:
            list_dispatches → populate_table →
            update_pagination → update_status.

        Raises:
            Exception: 刷新失败时弹出 QMessageBox 错误提示。
        """
        try:
            self._status_bar.setText("刷新中...")

            data = self._dispatch_service.list_dispatches(
                task_id=self._search_task_id,
                page=self._current_page,
                page_size=self._page_size,
            )

            self._dispatches = data.get("items", [])
            self._total = data.get("total", 0)

            self._populate_table()
            self._update_pagination_ui()
            self._update_status_bar()

            self._status_bar.setText(STATUS_TEXT["refresh_completed"])
            logger.info(
                "派发记录刷新完成: page=%d, total=%d, items=%d",
                self._current_page,
                self._total,
                len(self._dispatches),
            )

        except Exception as e:
            self._status_bar.setText("刷新失败")
            logger.error(
                "派发记录刷新失败: %s", e, exc_info=True
            )
            QMessageBox.critical(
                self,
                "错误",
                f"{MESSAGE_TEXT['refresh_failed']}: {e}",
            )

    # ============================================================
    # 填充表格
    # ============================================================

    def _populate_table(self) -> None:
        """将派发记录列表填充到表格中。"""
        self._table.setRowCount(len(self._dispatches))

        for row, dispatch in enumerate(self._dispatches):
            # ID
            self._table.setItem(
                row,
                COLUMN_INDEX["id"],
                QTableWidgetItem(str(dispatch.get("id", ""))),
            )
            # 任务编号
            self._table.setItem(
                row,
                COLUMN_INDEX["task_id"],
                QTableWidgetItem(str(dispatch.get("task_id", ""))),
            )
            # 去向方向
            self._table.setItem(
                row,
                COLUMN_INDEX["direction"],
                QTableWidgetItem(str(dispatch.get("direction", ""))),
            )
            # 去向日期
            self._table.setItem(
                row,
                COLUMN_INDEX["dispatch_date"],
                QTableWidgetItem(str(dispatch.get("dispatch_date", ""))),
            )
            # 操作人ID
            self._table.setItem(
                row,
                COLUMN_INDEX["operator_id"],
                QTableWidgetItem(str(dispatch.get("operator_id", ""))),
            )
            # 创建时间
            self._table.setItem(
                row,
                COLUMN_INDEX["created_at"],
                QTableWidgetItem(str(dispatch.get("created_at", ""))),
            )
            # 更新时间
            self._table.setItem(
                row,
                COLUMN_INDEX["updated_at"],
                QTableWidgetItem(str(dispatch.get("updated_at", ""))),
            )

    # ============================================================
    # 更新分页 UI
    # ============================================================

    def _update_pagination_ui(self) -> None:
        """更新分页控件显示（按钮状态 + 页码 + 总条数）。"""
        total_pages = max(
            1, (self._total + self._page_size - 1) // self._page_size
        )

        self._page_label.setText(
            f"{self._current_page} / {total_pages}"
        )
        self._total_label.setText(f"共 {self._total} 条")

        self._first_page_btn.setEnabled(self._current_page > 1)
        self._prev_page_btn.setEnabled(self._current_page > 1)
        self._next_page_btn.setEnabled(
            self._current_page < total_pages
        )
        self._last_page_btn.setEnabled(
            self._current_page < total_pages
        )

    # ============================================================
    # 更新状态栏
    # ============================================================

    def _update_status_bar(self) -> None:
        """更新状态栏显示。"""
        total_pages = max(
            1, (self._total + self._page_size - 1) // self._page_size
        )
        self._status_bar.setText(
            f"第 {self._current_page}/{total_pages} 页，"
            f"共 {self._total} 条记录"
        )

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
        """按任务编号进行搜索。

        仅当 keyword 可解析为 int 时执行搜索，否则重置搜索。

        Args:
            keyword: 搜索关键词。
        """
        try:
            task_id = int(keyword.strip())
            self._search_task_id = task_id
        except ValueError:
            self._search_task_id = None

        self._current_page = 1
        self.refresh()

    # ============================================================
    # CRUD：新增去向
    # ============================================================

    def _on_add(self) -> None:
        """新增派发去向（占位实现）。

        后续版本将弹出 DispatchDialog 对话框。
        """
        logger.debug("DispatchView._on_add: 占位实现")
        QMessageBox.information(
            self,
            "提示",
            MESSAGE_TEXT["add_placeholder"],
        )

    # ============================================================
    # CRUD：编辑
    # ============================================================

    def _on_edit(self) -> None:
        """编辑派发记录（占位实现）。

        后续版本将弹出 DispatchEditDialog 对话框。
        """
        logger.debug("DispatchView._on_edit: 占位实现")
        QMessageBox.information(
            self,
            "提示",
            MESSAGE_TEXT["edit_placeholder"],
        )

    # ============================================================
    # CRUD：删除
    # ============================================================

    def _on_delete(self) -> None:
        """删除派发记录。

        流程：
            ① 确认删除
            ② 调用 DispatchService.delete_dispatch()
            ③ refresh()
            ④ emit dispatch_changed
        """
        current_row = self._table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选择一条记录。")
            return

        dispatch_id = self._dispatches[current_row].get("id")
        if dispatch_id is None:
            return

        # 确认删除
        reply = QMessageBox.question(
            self,
            MESSAGE_TEXT["delete_title"],
            MESSAGE_TEXT["delete_confirm"],
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._dispatch_service.delete_dispatch(dispatch_id)
            logger.info(
                "派发记录删除成功: dispatch_id=%d", dispatch_id
            )
            self.refresh()
            self.dispatch_changed.emit()

        except Exception as e:
            logger.error(
                "派发记录删除失败: dispatch_id=%d, error=%s",
                dispatch_id, e, exc_info=True,
            )
            QMessageBox.critical(
                self,
                "错误",
                f"{MESSAGE_TEXT['delete_failed']}: {e}",
            )

    # ============================================================
    # 权限管理
    # ============================================================

    def _update_button_permissions(self) -> None:
        """更新按钮权限状态。

        根据当前用户权限启用/禁用各操作按钮。
        后续版本将根据 RBAC 权限动态控制。
        """
        self._add_btn.setEnabled(True)
        self._edit_btn.setEnabled(True)
        self._delete_btn.setEnabled(True)
        self._refresh_btn.setEnabled(True)


__all__ = [
    "DispatchView",
]
