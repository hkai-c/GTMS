"""GTMS 桌面端试磨任务管理页面 (TrialTaskView)

Sprint 5 — Task 5.7
严格依据 SRS §4.3、UI_PROTOTYPE §6、CODE_WIKI.md §15.5 / §15.6 / §15.7。

提供试磨任务管理界面：
    - 任务列表（QTableWidget）
    - 搜索（SearchBar Widget）
    - 状态标签（StatusBadge Widget）
    - 新增/编辑/删除任务
    - 分页（第一页 / 上一页 / 下一页 / 最后一页）
    - StatusBar

所有业务逻辑委托 Desktop TaskService，禁止直接 HTTP。
Task 5.8 (TaskEditDialog) 未完成前，新增/编辑入口保留为接口。
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

from client.services.task_service import TaskService
from client.widgets.search_bar import SearchBar
from client.widgets.status_badge import StatusBadge

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义 (§15.7.25 / §15.7.26 / §15.7.28)
# ============================================================

WINDOW_TITLE: str = "试磨任务管理"

TABLE_HEADERS: list[str] = [
    "任务编号",
    "客户名称",
    "加工要求",
    "销售",
    "流程状态",
    "结果状态",
    "快递单号",
    "创建时间",
]

COLUMN_INDEX: dict[str, int] = {
    "task_no": 0,
    "customer_name": 1,
    "requirement": 2,
    "sales_name": 3,
    "process_status": 4,
    "result_status": 5,
    "tracking_no": 6,
    "created_at": 7,
}

DEFAULT_PAGE_SIZE: int = 20

BUTTON_TEXT: dict[str, str] = {
    "add": "新增任务",
    "edit": "编辑任务",
    "delete": "删除任务",
    "refresh": "刷新",
    "first_page": "第一页",
    "prev_page": "上一页",
    "next_page": "下一页",
    "last_page": "最后一页",
    "search": "搜索",
}

OBJECT_NAMES: dict[str, str] = {
    "toolbar": "toolbar",
    "search_bar": "search_bar",
    "task_table": "task_table",
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
}

LOGGER_NAME: str = "gtms.client"


class TrialTaskView(QWidget):
    """GTMS 桌面端试磨任务管理页面。

    提供试磨任务查询、新增、编辑、删除界面，支持分页和搜索。
    使用 StatusBadge 显示流程状态和结果状态。

    Signals:
        task_changed: 任务信息变更（新增/编辑/删除后发射）。

    Attributes:
        _task_service: TaskService 实例。
        _tasks: 当前任务列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。
        _search_keyword: 当前搜索关键词。

    Usage:
        view = TrialTaskView(task_service)
        view.task_changed.connect(on_task_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    task_changed: Signal = Signal()
    """任务信息变更信号（新增/编辑/删除后发射）。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        task_service: TaskService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化试磨任务管理页面。

        Args:
            task_service: TaskService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._task_service: TaskService = task_service
        self._tasks: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total: int = 0
        self._search_keyword: str = ""

        self._setup_ui()
        self._update_button_permissions()

        logger.debug("TrialTaskView 初始化")

    # ============================================================
    # UI 构建 (§15.7.4 — 标准布局)
    # ============================================================

    def _setup_ui(self) -> None:
        """构建试磨任务管理页面 UI。

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
    # 工具栏 (§15.7.5)
    # ============================================================

    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏。

        Returns:
            QHBoxLayout: 工具栏布局。
        """
        toolbar = QHBoxLayout()
        toolbar.setObjectName(OBJECT_NAMES["toolbar"])
        toolbar.setSpacing(6)

        # 新增任务
        self._add_btn = QPushButton(BUTTON_TEXT["add"])
        self._add_btn.setObjectName(OBJECT_NAMES["add_btn"])
        self._add_btn.setFixedHeight(30)
        self._add_btn.clicked.connect(self._on_add)
        toolbar.addWidget(self._add_btn)

        # 编辑任务
        self._edit_btn = QPushButton(BUTTON_TEXT["edit"])
        self._edit_btn.setObjectName(OBJECT_NAMES["edit_btn"])
        self._edit_btn.setFixedHeight(30)
        self._edit_btn.clicked.connect(self._on_edit)
        toolbar.addWidget(self._edit_btn)

        # 删除任务
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

        # 搜索栏 (§15.7.6 — 统一 SearchBar Widget)
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
    # 表格 (§15.7.7)
    # ============================================================

    def _create_table(self) -> QTableWidget:
        """创建任务列表表格。

        Returns:
            QTableWidget: 任务列表表格。
        """
        table = QTableWidget()
        table.setObjectName(OBJECT_NAMES["task_table"])

        # 列定义 (§15.7.24 — 统一 TABLE_HEADERS)
        table.setColumnCount(len(TABLE_HEADERS))
        table.setHorizontalHeaderLabels(TABLE_HEADERS)

        # 表格属性
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

        # 表头
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
    # 分页栏 (§15.7.8)
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
    # 状态栏 (§15.7.9)
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
    # 数据和分页 (§15.7.10 — 刷新流程)
    # ============================================================

    def refresh(self) -> None:
        """刷新任务列表。

        调用 TaskService.list_tasks() 加载数据到表格。
        重新从当前页请求服务器，不使用本地缓存。
        """
        try:
            keyword = self._search_keyword or None
            data = self._task_service.list_tasks(
                task_no=keyword,
                page=self._current_page,
                page_size=self._page_size,
            )
            self._tasks = data.get("items", [])
            self._total = data.get("total", 0)
            self._populate_table(self._tasks)
            self._update_pagination_ui()
            self._update_status_bar("刷新完成")
            logger.info(
                "任务列表刷新: page=%d, total=%d, keyword=%r",
                self._current_page,
                self._total,
                self._search_keyword,
            )
        except Exception as e:
            logger.error("刷新任务列表失败: %s", e)
            QMessageBox.critical(self, "加载失败", f"加载任务列表失败: {e}")

    def _populate_table(self, tasks: list[dict[str, Any]]) -> None:
        """填充表格数据。

        Args:
            tasks: 任务列表。
        """
        self._table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            # 任务编号
            self._table.setItem(
                row, COLUMN_INDEX["task_no"],
                QTableWidgetItem(task.get("task_no", "")),
            )
            # 客户名称
            self._table.setItem(
                row, COLUMN_INDEX["customer_name"],
                QTableWidgetItem(task.get("customer_name", "")),
            )
            # 加工要求
            self._table.setItem(
                row, COLUMN_INDEX["requirement"],
                QTableWidgetItem(task.get("requirement", "")),
            )
            # 销售
            self._table.setItem(
                row, COLUMN_INDEX["sales_name"],
                QTableWidgetItem(task.get("sales_name", "")),
            )
            # 流程状态 (StatusBadge)
            process_status = task.get("process_status", "")
            process_badge = StatusBadge(process_status, parent=self)
            self._table.setCellWidget(
                row, COLUMN_INDEX["process_status"], process_badge
            )
            # 结果状态 (StatusBadge)
            result_status = task.get("result_status", "")
            result_badge = StatusBadge(result_status, parent=self)
            self._table.setCellWidget(
                row, COLUMN_INDEX["result_status"], result_badge
            )
            # 快递单号
            self._table.setItem(
                row, COLUMN_INDEX["tracking_no"],
                QTableWidgetItem(task.get("tracking_no", "")),
            )
            # 创建时间
            created_at = task.get("created_at", "")
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

        # 按钮状态
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
    # 搜索 (§15.7.6)
    # ============================================================

    def _on_search(self, keyword: str) -> None:
        """按任务编号搜索。

        SearchBar 发射 search_requested Signal，重置到第一页。

        Args:
            keyword: 搜索关键词。
        """
        self._search_keyword = keyword
        self._current_page = 1
        self.refresh()

    # ============================================================
    # 新增任务 (§15.7.11 — Task 5.8 未完成前保留接口)
    # ============================================================

    def _on_add(self) -> None:
        """新增任务。

        Task 5.8 (TaskEditDialog) 未完成，暂显示提示。
        完成后：打开 TaskEditDialog → create_task() → refresh() → emit task_changed。
        """
        QMessageBox.information(
            self, "功能提示", "新增任务功能将在 Task 5.8 中实现。"
        )

    # ============================================================
    # 编辑任务 (§15.7.11 — Task 5.8 未完成前保留接口)
    # ============================================================

    def _on_edit(self) -> None:
        """编辑任务。

        Task 5.8 (TaskEditDialog) 未完成，暂显示提示。
        完成后：
        选中行 → TaskEditDialog → update_task() → refresh() → emit task_changed。
        """
        QMessageBox.information(
            self, "功能提示", "编辑任务功能将在 Task 5.8 中实现。"
        )

    # ============================================================
    # 删除任务 (§15.7.11)
    # ============================================================

    def _on_delete(self) -> None:
        """删除任务。

        确认 → delete_task() → refresh() → emit task_changed。
        """
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要删除的任务")
            return

        task = self._tasks[row]
        task_id = task.get("id")
        task_no = task.get("task_no", "")

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除任务「{task_no}」吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._task_service.delete_task(task_id)
            self.refresh()
            self.task_changed.emit()
            logger.info("任务删除完成: task_id=%d, task_no=%s", task_id, task_no)
        except Exception as e:
            logger.error("删除任务失败: %s", e)
            QMessageBox.critical(self, "删除失败", f"删除任务失败: {e}")

    # ============================================================
    # 权限管理 (§15.7.13)
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
    "TrialTaskView",
]
