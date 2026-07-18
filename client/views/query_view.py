"""GTMS 桌面端查询统计页面 (QueryView)

Sprint 10 — Task 10.5
严格依据 UI_PROTOTYPE §13、SRS §4.8、CODE_WIKI §15.11/§15.12/§15.13。

提供查询统计管理界面：
    - 多条件组合查询（SearchBar Widget）
    - 统计面板（本月/年度数量、成功率）
    - 排行面板（客户 Top N、机型 Top N）
    - 数据表格（QTableWidget）
    - 导出 Excel 按钮
    - 分页（第一页/上一页/下一页/最后一页）
    - StatusBar

所有业务逻辑委托 Desktop QueryService，禁止直接 HTTP/ORM/统计。
"""

import logging
from datetime import datetime
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client.services.query_service import QueryService
from client.widgets.search_bar import SearchBar

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义
# ============================================================

WINDOW_TITLE: str = "查询统计"

TABLE_HEADERS: list[str] = [
    "任务编号",
    "客户",
    "责任人",
    "机型",
    "流程状态",
    "结果状态",
    "创建时间",
    "更新时间",
]

COLUMN_INDEX: dict[str, int] = {
    "task_no": 0,
    "customer_name": 1,
    "operator_name": 2,
    "machine_model": 3,
    "process_status": 4,
    "result_status": 5,
    "created_at": 6,
    "updated_at": 7,
}

DEFAULT_PAGE_SIZE: int = 20

BUTTON_TEXT: dict[str, str] = {
    "refresh": "刷新",
    "export": "导出 Excel",
    "search": "搜索",
    "first_page": "第一页",
    "prev_page": "上一页",
    "next_page": "下一页",
    "last_page": "最后一页",
}

OBJECT_NAMES: dict[str, str] = {
    "title_label": "title_label",
    "search_bar": "search_bar",
    "filter_area": "filter_area",
    "customer_filter": "customer_filter",
    "status_filter": "status_filter",
    "date_filter": "date_filter",
    "operator_filter": "operator_filter",
    "machine_filter": "machine_filter",
    "statistics_panel": "statistics_panel",
    "monthly_count_label": "monthly_count_label",
    "annual_count_label": "annual_count_label",
    "success_rate_label": "success_rate_label",
    "ranking_panel": "ranking_panel",
    "customer_ranking_label": "customer_ranking_label",
    "machine_ranking_label": "machine_ranking_label",
    "toolbar": "toolbar",
    "refresh_btn": "refresh_btn",
    "export_btn": "export_btn",
    "query_table": "query_table",
    "pagination_widget": "pagination_widget",
    "first_page_btn": "first_page_btn",
    "prev_page_btn": "prev_page_btn",
    "next_page_btn": "next_page_btn",
    "last_page_btn": "last_page_btn",
    "page_label": "page_label",
    "total_label": "total_label",
    "status_bar": "status_bar",
}

STATUS_TEXT: dict[str, str] = {
    "ready": "就绪",
    "refresh_completed": "刷新完成",
    "export_completed": "导出数据准备完成",
}

MESSAGE_TEXT: dict[str, str] = {
    "refresh_failed": "刷新查询数据失败",
    "export_failed": "导出数据失败",
    "export_success": "导出数据成功",
}

LABEL_TEXT: dict[str, str] = {
    "statistics_title": "统计摘要",
    "monthly_count": "本月数量",
    "annual_count": "年度数量",
    "success_rate": "成功率",
    "ranking_title": "排行",
    "customer_ranking": "客户排行",
    "machine_ranking": "机型排行",
    "filter_customer": "客户",
    "filter_status": "状态",
    "filter_date": "日期",
    "filter_operator": "责任人",
    "filter_machine": "机型",
}

LOGGER_NAME: str = "gtms.client"


class QueryView(QWidget):
    """GTMS 桌面端查询统计页面。

    提供多条件查询、统计摘要、排行展示、数据导出界面。

    Signals:
        query_changed: 查询条件变更信号。

    Attributes:
        _query_service: QueryService 实例。
        _tasks: 当前任务列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。
        _statistics: 统计摘要数据缓存。
        _customer_ranking: 客户排行数据缓存。
        _machine_ranking: 机型排行数据缓存。

    Usage:
        view = QueryView(query_service)
        view.query_changed.connect(on_query_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    query_changed: Signal = Signal()
    """查询条件变更信号。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        query_service: QueryService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化查询统计页面。

        Args:
            query_service: QueryService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._query_service: QueryService = query_service
        self._tasks: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total: int = 0
        self._statistics: dict[str, Any] = {}
        self._customer_ranking: list[dict[str, Any]] = []
        self._machine_ranking: list[dict[str, Any]] = []

        self._setup_ui()

        logger.debug("QueryView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建查询统计页面 UI。

        标准布局: 标题 → SearchBar → Statistics Panel →
        Ranking Panel → Toolbar → Table → Pagination → StatusBar。
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

        # --- 搜索区域 ---
        search_area = self._create_search_area()
        layout.addLayout(search_area)

        # --- 统计面板 ---
        stats_panel = self._create_statistics_panel()
        layout.addLayout(stats_panel)

        # --- 排行面板 ---
        ranking_panel = self._create_ranking_panel()
        layout.addLayout(ranking_panel)

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
    # 搜索区域
    # ============================================================

    def _create_search_area(self) -> QHBoxLayout:
        """创建搜索区域（组合查询筛选 + SearchBar）。

        Returns:
            QHBoxLayout: 搜索区域布局。
        """
        filter_area = QHBoxLayout()
        filter_area.setObjectName(OBJECT_NAMES["filter_area"])
        filter_area.setSpacing(6)

        # 客户筛选
        customer_label = QLabel(LABEL_TEXT["filter_customer"])
        customer_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(customer_label)

        self._customer_filter = QLineEdit()
        self._customer_filter.setPlaceholderText("客户ID/名称")
        self._customer_filter.setObjectName(OBJECT_NAMES["customer_filter"])
        self._customer_filter.setFixedWidth(100)
        filter_area.addWidget(self._customer_filter)

        # 状态筛选
        status_label = QLabel(LABEL_TEXT["filter_status"])
        status_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(status_label)

        self._status_filter = QComboBox()
        self._status_filter.setObjectName(OBJECT_NAMES["status_filter"])
        self._status_filter.addItems(
            ["全部", "grinding", "dispatched", "closed"]
        )
        self._status_filter.setFixedWidth(100)
        filter_area.addWidget(self._status_filter)

        # 日期筛选
        date_label = QLabel(LABEL_TEXT["filter_date"])
        date_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(date_label)

        self._date_from_filter = QDateEdit()
        self._date_from_filter.setObjectName(OBJECT_NAMES["date_filter"])
        self._date_from_filter.setCalendarPopup(True)
        self._date_from_filter.setSpecialValueText("起始日期")
        self._date_from_filter.setFixedWidth(110)
        filter_area.addWidget(self._date_from_filter)

        # 责任人筛选
        operator_label = QLabel(LABEL_TEXT["filter_operator"])
        operator_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(operator_label)

        self._operator_filter = QLineEdit()
        self._operator_filter.setPlaceholderText("责任人ID")
        self._operator_filter.setObjectName(OBJECT_NAMES["operator_filter"])
        self._operator_filter.setFixedWidth(80)
        filter_area.addWidget(self._operator_filter)

        # 机型筛选
        machine_label = QLabel(LABEL_TEXT["filter_machine"])
        machine_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(machine_label)

        self._machine_filter = QLineEdit()
        self._machine_filter.setPlaceholderText("机型")
        self._machine_filter.setObjectName(OBJECT_NAMES["machine_filter"])
        self._machine_filter.setFixedWidth(80)
        filter_area.addWidget(self._machine_filter)

        # 弹性空间
        filter_area.addStretch()

        # 搜索栏（关键字搜索）
        self._search_bar = SearchBar(
            placeholder="请输入任务编号...",
            button_text=BUTTON_TEXT["search"],
            parent=self,
        )
        self._search_bar.setObjectName(OBJECT_NAMES["search_bar"])
        self._search_bar.search_requested.connect(self._on_search)
        filter_area.addWidget(self._search_bar)

        return filter_area

    # ============================================================
    # 统计面板
    # ============================================================

    def _create_statistics_panel(self) -> QHBoxLayout:
        """创建统计摘要面板。

        Returns:
            QHBoxLayout: 统计面板布局。
        """
        panel = QHBoxLayout()
        panel.setObjectName(OBJECT_NAMES["statistics_panel"])
        panel.setSpacing(16)

        title = QLabel(LABEL_TEXT["statistics_title"])
        title.setStyleSheet("font-size: 13px; font-weight: bold;")
        panel.addWidget(title)

        self._monthly_count_label = QLabel("--")
        self._monthly_count_label.setObjectName(
            OBJECT_NAMES["monthly_count_label"]
        )
        self._monthly_count_label.setStyleSheet("font-size: 12px;")
        panel.addWidget(QLabel(LABEL_TEXT["monthly_count"] + ":"))
        panel.addWidget(self._monthly_count_label)

        self._annual_count_label = QLabel("--")
        self._annual_count_label.setObjectName(
            OBJECT_NAMES["annual_count_label"]
        )
        self._annual_count_label.setStyleSheet("font-size: 12px;")
        panel.addWidget(QLabel(LABEL_TEXT["annual_count"] + ":"))
        panel.addWidget(self._annual_count_label)

        self._success_rate_label = QLabel("--")
        self._success_rate_label.setObjectName(
            OBJECT_NAMES["success_rate_label"]
        )
        self._success_rate_label.setStyleSheet("font-size: 12px;")
        panel.addWidget(QLabel(LABEL_TEXT["success_rate"] + ":"))
        panel.addWidget(self._success_rate_label)

        panel.addStretch()
        return panel

    # ============================================================
    # 排行面板
    # ============================================================

    def _create_ranking_panel(self) -> QHBoxLayout:
        """创建排行面板。

        Returns:
            QHBoxLayout: 排行面板布局。
        """
        panel = QHBoxLayout()
        panel.setObjectName(OBJECT_NAMES["ranking_panel"])
        panel.setSpacing(16)

        title = QLabel(LABEL_TEXT["ranking_title"])
        title.setStyleSheet("font-size: 13px; font-weight: bold;")
        panel.addWidget(title)

        self._customer_ranking_label = QLabel("--")
        self._customer_ranking_label.setObjectName(
            OBJECT_NAMES["customer_ranking_label"]
        )
        self._customer_ranking_label.setStyleSheet("font-size: 12px;")
        panel.addWidget(QLabel(LABEL_TEXT["customer_ranking"] + ":"))
        panel.addWidget(self._customer_ranking_label)

        self._machine_ranking_label = QLabel("--")
        self._machine_ranking_label.setObjectName(
            OBJECT_NAMES["machine_ranking_label"]
        )
        self._machine_ranking_label.setStyleSheet("font-size: 12px;")
        panel.addWidget(QLabel(LABEL_TEXT["machine_ranking"] + ":"))
        panel.addWidget(self._machine_ranking_label)

        panel.addStretch()
        return panel

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

        self._refresh_btn = QPushButton(BUTTON_TEXT["refresh"])
        self._refresh_btn.setObjectName(OBJECT_NAMES["refresh_btn"])
        self._refresh_btn.setFixedHeight(30)
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)

        self._export_btn = QPushButton(BUTTON_TEXT["export"])
        self._export_btn.setObjectName(OBJECT_NAMES["export_btn"])
        self._export_btn.setFixedHeight(30)
        self._export_btn.clicked.connect(self._on_export)
        toolbar.addWidget(self._export_btn)

        toolbar.addStretch()
        return toolbar

    # ============================================================
    # 表格
    # ============================================================

    def _create_table(self) -> QTableWidget:
        """创建查询结果表格。

        Returns:
            QTableWidget: 查询结果表格。
        """
        table = QTableWidget()
        table.setObjectName(OBJECT_NAMES["query_table"])
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
        """刷新查询统计数据。

        唯一刷新入口。
        流程: list_tasks -> populate_table -> update_statistics ->
            update_rankings -> update_pagination -> update_status_bar。

        Raises:
            Exception: 刷新失败时弹出 QMessageBox 错误提示。
        """
        try:
            self._status_bar.setText("刷新中...")

            keyword = self._search_bar.text()
            customer_id = self._get_filter_int(self._customer_filter.text())
            process_status = self._get_filter_str(self._status_filter)
            date_from = self._get_filter_date()
            operator_id = self._get_filter_int(self._operator_filter.text())
            machine_model = self._get_filter_str(self._machine_filter)

            data = self._query_service.list_tasks(
                customer_id=customer_id,
                process_status=process_status,
                operator_id=operator_id,
                machine_model=machine_model,
                keyword=keyword if keyword else None,
                date_from=date_from,
                page=self._current_page,
                page_size=self._page_size,
            )

            self._tasks = data.get("items", [])
            self._total = data.get("total", 0)

            self._populate_table()
            self._update_statistics()
            self._update_rankings()
            self._update_pagination()
            self._update_status_bar()

            self._status_bar.setText(STATUS_TEXT["refresh_completed"])
            logger.info(
                "查询统计刷新完成: page=%d, total=%d, items=%d",
                self._current_page,
                self._total,
                len(self._tasks),
            )

        except Exception as e:
            self._status_bar.setText("刷新失败")
            logger.error(
                "查询统计刷新失败: %s", e, exc_info=True
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
        """将任务列表填充到表格中。"""
        self._table.setRowCount(len(self._tasks))

        for row, task in enumerate(self._tasks):
            self._table.setItem(
                row,
                COLUMN_INDEX["task_no"],
                QTableWidgetItem(str(task.get("task_no", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["customer_name"],
                QTableWidgetItem(str(task.get("customer_name", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["operator_name"],
                QTableWidgetItem(str(task.get("operator_name", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["machine_model"],
                QTableWidgetItem(str(task.get("machine_model", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["process_status"],
                QTableWidgetItem(str(task.get("process_status", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["result_status"],
                QTableWidgetItem(str(task.get("result_status", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["created_at"],
                QTableWidgetItem(str(task.get("created_at", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["updated_at"],
                QTableWidgetItem(str(task.get("updated_at", ""))),
            )

    # ============================================================
    # 更新统计面板
    # ============================================================

    def _update_statistics(self) -> None:
        """更新统计摘要数据。

        从 QueryService.get_statistics() 获取统计摘要，
        委托 Server 完成所有统计计算。
        """
        try:
            self._statistics = self._query_service.get_statistics()
            summary = self._statistics.get("summary", {})

            monthly = summary.get("monthly_count", 0)
            annual = summary.get("annual_count", 0)
            success_rate = summary.get("success_rate", 0)

            self._monthly_count_label.setText(str(monthly))
            self._annual_count_label.setText(str(annual))
            self._success_rate_label.setText(
                f"{success_rate:.1f}%" if success_rate else "--"
            )
        except Exception:
            self._monthly_count_label.setText("--")
            self._annual_count_label.setText("--")
            self._success_rate_label.setText("--")

    # ============================================================
    # 更新排行面板
    # ============================================================

    def _update_rankings(self) -> None:
        """更新排行数据。

        从 QueryService 获取排行数据，
        委托 Server 完成所有排行计算。
        """
        try:
            self._customer_ranking = self._query_service.get_customer_ranking()
            if self._customer_ranking:
                top = self._customer_ranking[:5]
                parts = [
                    f"{r.get('customer_name', '')}({r.get('count', 0)})"
                    for r in top
                ]
                self._customer_ranking_label.setText(", ".join(parts))
            else:
                self._customer_ranking_label.setText("--")

            self._machine_ranking = self._query_service.get_machine_ranking()
            if self._machine_ranking:
                top = self._machine_ranking[:5]
                parts = [
                    f"{r.get('machine_model', '')}({r.get('count', 0)})"
                    for r in top
                ]
                self._machine_ranking_label.setText(", ".join(parts))
            else:
                self._machine_ranking_label.setText("--")
        except Exception:
            self._customer_ranking_label.setText("--")
            self._machine_ranking_label.setText("--")

    # ============================================================
    # 更新分页 UI
    # ============================================================

    def _update_pagination(self) -> None:
        """更新分页控件显示。"""
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
        """搜索触发回调。

        Args:
            keyword: 搜索关键词（任务编号）。
        """
        self._current_page = 1
        self.refresh()
        self.query_changed.emit()

    # ============================================================
    # 导出 Excel
    # ============================================================

    def _on_export(self) -> None:
        """导出 Excel 按钮回调。

        调用 QueryService.export_excel() 获取导出数据，
        禁止 View 生成 Excel 文件。
        """
        try:
            keyword = self._search_bar.text()
            customer_id = self._get_filter_int(self._customer_filter.text())
            process_status = self._get_filter_str(self._status_filter)
            operator_id = self._get_filter_int(self._operator_filter.text())
            machine_model = self._get_filter_str(self._machine_filter)

            data = self._query_service.export_excel(
                customer_id=customer_id,
                process_status=process_status,
                operator_id=operator_id,
                machine_model=machine_model,
                keyword=keyword if keyword else None,
            )

            self._status_bar.setText(
                STATUS_TEXT["export_completed"]
            )
            logger.info(
                "导出数据准备完成: total=%d", len(data)
            )
            QMessageBox.information(
                self,
                "提示",
                f"{MESSAGE_TEXT['export_success']}，共 {len(data)} 条记录。",
            )

        except Exception as e:
            logger.error(
                "导出数据失败: %s", e, exc_info=True
            )
            QMessageBox.critical(
                self,
                "错误",
                f"{MESSAGE_TEXT['export_failed']}: {e}",
            )

    # ============================================================
    # 筛选参数辅助方法
    # ============================================================

    @staticmethod
    def _get_filter_int(text: str) -> int | None:
        """将文本转换为整数筛选参数。

        Args:
            text: 输入文本。

        Returns:
            int | None: 有效整数或 None。
        """
        if not text or not text.strip():
            return None
        try:
            return int(text.strip())
        except ValueError:
            return None

    @staticmethod
    def _get_filter_str(widget: QComboBox) -> str | None:
        """从下拉框获取筛选参数。

        Args:
            widget: QComboBox 控件。

        Returns:
            str | None: 有效选项或 None。
        """
        value = widget.currentText()
        if value == "全部" or not value:
            return None
        return value

    def _get_filter_date(self) -> datetime | None:
        """从日期选择器获取筛选参数。

        Returns:
            datetime | None: 有效日期或 None。
        """
        date = self._date_from_filter.date()
        if date == self._date_from_filter.minimumDate():
            return None
        return datetime(
            date.year(), date.month(), date.day()
        )


__all__ = [
    "QueryView",
]
