"""GTMS 桌面端试磨管理页面 (GrindingView)

Sprint 7 — Task 7.5
严格依据 UI_PROTOTYPE §10、SRS §4.5、CODE_WIKI §15.5/§15.7/§15.10/§15.11/§15.12。

提供试磨记录管理界面：
    - 试磨记录列表（QTableWidget）
    - 搜索（SearchBar Widget）
    - 开始试磨 / 编辑 / 完成试磨 / 删除
    - 分页（第一页/上一页/下一页/最后一页）
    - StatusBar

所有业务逻辑委托 Desktop GrindingService，禁止直接 HTTP。
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

from client.services.grinding_service import GrindingService
from client.widgets.search_bar import SearchBar

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义
# ============================================================

WINDOW_TITLE: str = "试磨管理"

TABLE_HEADERS: list[str] = [
    "ID",
    "任务编号",
    "责任人ID",
    "试磨机型",
    "砂轮型号",
    "开始时间",
    "完成时间",
    "失败原因",
    "创建时间",
]

COLUMN_INDEX: dict[str, int] = {
    "id": 0,
    "task_id": 1,
    "operator_id": 2,
    "machine_type": 3,
    "wheel_type": 4,
    "start_time": 5,
    "end_time": 6,
    "fail_reason": 7,
    "created_at": 8,
}

DEFAULT_PAGE_SIZE: int = 20

BUTTON_TEXT: dict[str, str] = {
    "add": "开始试磨",
    "edit": "编辑",
    "finish": "完成试磨",
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
    "grinding_table": "grinding_table",
    "pagination_widget": "pagination_widget",
    "status_bar": "status_bar",
    "add_btn": "add_btn",
    "edit_btn": "edit_btn",
    "finish_btn": "finish_btn",
    "delete_btn": "delete_btn",
    "refresh_btn": "refresh_btn",
    "first_page_btn": "first_page_btn",
    "prev_page_btn": "prev_page_btn",
    "next_page_btn": "next_page_btn",
    "last_page_btn": "last_page_btn",
    "page_label": "page_label",
    "total_label": "total_label",
}

LOGGER_NAME: str = "gtms.client"


class GrindingView(QWidget):
    """GTMS 桌面端试磨管理页面。

    提供试磨记录查询、开始试磨、编辑、完成试磨、删除界面，支持分页和搜索。

    Signals:
        grinding_changed: 试磨记录变更（开始/编辑/完成/删除后发射）。

    Attributes:
        _grinding_service: GrindingService 实例。
        _grindings: 当前试磨记录列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。
        _search_task_id: 当前搜索任务编号。

    Usage:
        view = GrindingView(grinding_service)
        view.grinding_changed.connect(on_grinding_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    grinding_changed: Signal = Signal()
    """试磨记录变更信号（开始/编辑/完成/删除后发射）。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        grinding_service: GrindingService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化试磨管理页面。

        Args:
            grinding_service: GrindingService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._grinding_service: GrindingService = grinding_service
        self._grindings: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total: int = 0
        self._search_task_id: int | None = None

        self._setup_ui()
        self._update_button_permissions()

        logger.debug("GrindingView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建试磨管理页面 UI。

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

        # 开始试磨
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

        # 完成试磨
        self._finish_btn = QPushButton(BUTTON_TEXT["finish"])
        self._finish_btn.setObjectName(OBJECT_NAMES["finish_btn"])
        self._finish_btn.setFixedHeight(30)
        self._finish_btn.clicked.connect(self._on_finish)
        toolbar.addWidget(self._finish_btn)

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
        """创建试磨记录列表表格。

        Returns:
            QTableWidget: 试磨记录列表表格。
        """
        table = QTableWidget()
        table.setObjectName(OBJECT_NAMES["grinding_table"])
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
    # 数据和分页 — 刷新流程
    # ============================================================

    def refresh(self) -> None:
        """刷新试磨记录列表。

        调用 GrindingService.list_grindings() 加载数据到表格。
        重新从当前页请求服务器，不使用本地缓存。
        """
        try:
            data = self._grinding_service.list_grindings(
                task_id=self._search_task_id,
                page=self._current_page,
                page_size=self._page_size,
            )
            self._grindings = data.get("items", [])
            self._total = data.get("total", 0)
            self._populate_table(self._grindings)
            self._update_pagination_ui()
            self._update_status_bar("刷新完成")
            logger.info(
                "试磨记录列表刷新: page=%d, total=%d, task_id=%s",
                self._current_page, self._total, self._search_task_id,
            )
        except Exception as e:
            logger.error("刷新试磨记录列表失败: %s", e)
            QMessageBox.critical(
                self, "加载失败", f"加载试磨记录列表失败: {e}"
            )

    def _populate_table(self, grindings: list[dict[str, Any]]) -> None:
        """填充表格数据。

        Args:
            grindings: 试磨记录列表。
        """
        self._table.setRowCount(len(grindings))
        for row, grinding in enumerate(grindings):
            # ID
            self._table.setItem(
                row, COLUMN_INDEX["id"],
                QTableWidgetItem(str(grinding.get("id", ""))),
            )
            # 任务编号
            self._table.setItem(
                row, COLUMN_INDEX["task_id"],
                QTableWidgetItem(str(grinding.get("task_id", ""))),
            )
            # 责任人ID
            self._table.setItem(
                row, COLUMN_INDEX["operator_id"],
                QTableWidgetItem(str(grinding.get("operator_id", ""))),
            )
            # 试磨机型
            self._table.setItem(
                row, COLUMN_INDEX["machine_type"],
                QTableWidgetItem(
                    str(grinding.get("machine_type") or "")
                ),
            )
            # 砂轮型号
            self._table.setItem(
                row, COLUMN_INDEX["wheel_type"],
                QTableWidgetItem(
                    str(grinding.get("wheel_type") or "")
                ),
            )
            # 开始时间
            start_time = grinding.get("start_time", "")
            self._table.setItem(
                row, COLUMN_INDEX["start_time"],
                QTableWidgetItem(str(start_time)),
            )
            # 完成时间
            end_time = grinding.get("end_time", "")
            self._table.setItem(
                row, COLUMN_INDEX["end_time"],
                QTableWidgetItem(str(end_time)),
            )
            # 失败原因
            self._table.setItem(
                row, COLUMN_INDEX["fail_reason"],
                QTableWidgetItem(
                    str(grinding.get("fail_reason") or "")
                ),
            )
            # 创建时间
            created_at = grinding.get("created_at", "")
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
        """按任务编号搜索。

        SearchBar 发射 search_requested Signal，重置到第一页。

        Args:
            keyword: 搜索关键词（任务编号）。
        """
        try:
            self._search_task_id = int(keyword) if keyword.strip() else None
        except ValueError:
            self._search_task_id = None
        self._current_page = 1
        self.refresh()

    # ============================================================
    # 开始试磨
    # ============================================================

    def _on_add(self) -> None:
        """开始试磨。

        GrindingDialog 未实现，暂显示提示。
        完成后的流程：
        GrindingDialog → create_grinding() → refresh() → emit grinding_changed。
        """
        QMessageBox.information(
            self, "功能提示", "开始试磨功能将在后续实现。"
        )

    # ============================================================
    # 编辑试磨记录
    # ============================================================

    def _on_edit(self) -> None:
        """编辑试磨记录。

        GrindingDialog 未实现，暂显示提示。
        完成后的流程：
        选中行 → GrindingDialog → update_grinding() → refresh()
        → emit grinding_changed。
        """
        QMessageBox.information(
            self, "功能提示", "编辑试磨记录功能将在后续实现。"
        )

    # ============================================================
    # 完成试磨
    # ============================================================

    def _on_finish(self) -> None:
        """完成试磨。

        GrindingFinishDialog 未实现，暂显示提示。
        完成后的流程：
        选中行 → GrindingFinishDialog → finish_grinding() → refresh()
        → emit grinding_changed。
        """
        QMessageBox.information(
            self, "功能提示", "完成试磨功能将在后续实现。"
        )

    # ============================================================
    # 删除试磨记录
    # ============================================================

    def _on_delete(self) -> None:
        """删除试磨记录。

        确认 → delete_grinding() → refresh() → emit grinding_changed。
        """
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(
                self, "提示", "请先选择要删除的试磨记录"
            )
            return

        grinding = self._grindings[row]
        grinding_id = grinding.get("id")

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除试磨记录 #{grinding_id} 吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._grinding_service.delete_grinding(grinding_id)
            self.refresh()
            self.grinding_changed.emit()
            logger.info(
                "试磨记录删除完成: grinding_id=%d", grinding_id,
            )
        except Exception as e:
            logger.error("删除试磨记录失败: %s", e)
            QMessageBox.critical(
                self, "删除失败", f"删除试磨记录失败: {e}"
            )

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
        self._finish_btn.setEnabled(True)
        self._delete_btn.setEnabled(True)
        self._refresh_btn.setEnabled(True)


__all__ = [
    "GrindingView",
]
