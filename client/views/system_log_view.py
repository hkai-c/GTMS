"""GTMS 桌面端操作日志页面 (SystemLogView)

Sprint 11 — Task 11.6
严格依据 UI_PROTOTYPE §15、SRS §4.10、
    Sprint 11 Task 11.5 Desktop LogService Public API、
    §15.15 Audit Logging Principle。

提供操作日志查看界面：
    - 多条件筛选（SearchBar + 操作人 + 操作类型 + 模块 + 时间范围）
    - 日志表格（QTableWidget，8 列）
    - 分页（第一页/上一页/下一页/最后一页）
    - 导出数据准备
    - StatusBar

所有业务逻辑委托 Desktop LogService，禁止直接 HTTP/ORM/统计。
日志只读，禁止新增、编辑、删除。
"""

import logging
from datetime import datetime
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateTimeEdit,
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

from client.services.log_service import LogService
from client.widgets.search_bar import SearchBar

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义
# ============================================================

WINDOW_TITLE: str = "操作日志"

COLUMN_HEADERS: list[str] = [
    "ID",
    "操作人",
    "操作类型",
    "操作模块",
    "操作对象",
    "对象ID",
    "描述",
    "操作时间",
]

COLUMN_INDEX: dict[str, int] = {
    "id": 0,
    "operator": 1,
    "operation": 2,
    "module": 3,
    "target_type": 4,
    "target_id": 5,
    "description": 6,
    "created_at": 7,
}

DEFAULT_PAGE_SIZE: int = 20

BUTTON_TEXT: dict[str, str] = {
    "refresh": "刷新",
    "export": "导出",
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
    "operator_filter": "operator_filter",
    "operation_filter": "operation_filter",
    "module_filter": "module_filter",
    "start_time_filter": "start_time_filter",
    "end_time_filter": "end_time_filter",
    "toolbar": "toolbar",
    "refresh_btn": "refresh_btn",
    "export_btn": "export_btn",
    "log_table": "log_table",
    "pagination_widget": "pagination_widget",
    "first_page_btn": "first_page_btn",
    "prev_page_btn": "prev_page_btn",
    "next_page_btn": "next_page_btn",
    "last_page_btn": "last_page_btn",
    "page_label": "page_label",
    "total_label": "total_label",
    "status_bar": "status_bar",
}

OPERATION_TYPES: list[str] = [
    "全部",
    "create",
    "update",
    "delete",
    "status_change",
]

STATUS_TEXT: dict[str, str] = {
    "ready": "就绪",
    "refresh_completed": "刷新完成",
    "export_completed": "导出数据准备完成",
}

MESSAGE_TEXT: dict[str, str] = {
    "refresh_failed": "刷新操作日志失败",
    "export_failed": "导出数据失败",
    "export_success": "导出数据成功",
}

LABEL_TEXT: dict[str, str] = {
    "filter_operator": "操作人",
    "filter_operation": "操作类型",
    "filter_module": "模块",
    "filter_start_time": "开始时间",
    "filter_end_time": "结束时间",
}


class SystemLogView(QWidget):
    """GTMS 桌面端操作日志页面。

    提供日志查看、多条件筛选、分页浏览、导出数据准备界面。
    日志只读，禁止新增、编辑、删除。

    Signals:
        log_changed: 日志数据变更信号。

    Attributes:
        _log_service: LogService 实例。
        _logs: 当前日志列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。

    Usage:
        view = SystemLogView(log_service)
        view.log_changed.connect(on_log_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    log_changed: Signal = Signal()
    """日志数据变更信号。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        log_service: LogService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化操作日志页面。

        Args:
            log_service: LogService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._log_service: LogService = log_service
        self._logs: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total: int = 0

        self._setup_ui()

        logger.debug("SystemLogView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建操作日志页面 UI。

        标准布局: 标题 → SearchBar → 筛选区域 → Toolbar → Table →
        Pagination → StatusBar。
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

        # --- 搜索栏 ---
        self._search_bar = SearchBar(
            placeholder="请输入关键字搜索...",
            button_text=BUTTON_TEXT["search"],
            parent=self,
        )
        self._search_bar.setObjectName(OBJECT_NAMES["search_bar"])
        self._search_bar.search_requested.connect(self._on_search)
        layout.addWidget(self._search_bar)

        # --- 筛选区域 ---
        filter_area = self._create_filter_area()
        layout.addLayout(filter_area)

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
    # 筛选区域
    # ============================================================

    def _create_filter_area(self) -> QHBoxLayout:
        """创建筛选区域。

        Returns:
            QHBoxLayout: 筛选区域布局。
        """
        filter_area = QHBoxLayout()
        filter_area.setObjectName(OBJECT_NAMES["filter_area"])
        filter_area.setSpacing(6)

        # 操作人筛选
        operator_label = QLabel(LABEL_TEXT["filter_operator"])
        operator_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(operator_label)

        self._operator_filter = QLineEdit()
        self._operator_filter.setPlaceholderText("操作人ID")
        self._operator_filter.setObjectName(
            OBJECT_NAMES["operator_filter"]
        )
        self._operator_filter.setFixedWidth(80)
        filter_area.addWidget(self._operator_filter)

        # 操作类型筛选
        operation_label = QLabel(LABEL_TEXT["filter_operation"])
        operation_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(operation_label)

        self._operation_filter = QComboBox()
        self._operation_filter.setObjectName(
            OBJECT_NAMES["operation_filter"]
        )
        self._operation_filter.addItems(OPERATION_TYPES)
        self._operation_filter.setFixedWidth(100)
        filter_area.addWidget(self._operation_filter)

        # 模块筛选
        module_label = QLabel(LABEL_TEXT["filter_module"])
        module_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(module_label)

        self._module_filter = QLineEdit()
        self._module_filter.setPlaceholderText("模块名称")
        self._module_filter.setObjectName(
            OBJECT_NAMES["module_filter"]
        )
        self._module_filter.setFixedWidth(100)
        filter_area.addWidget(self._module_filter)

        # 开始时间
        start_label = QLabel(LABEL_TEXT["filter_start_time"])
        start_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(start_label)

        self._start_time_filter = QDateTimeEdit()
        self._start_time_filter.setObjectName(
            OBJECT_NAMES["start_time_filter"]
        )
        self._start_time_filter.setCalendarPopup(True)
        self._start_time_filter.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._start_time_filter.setSpecialValueText("不限")
        self._start_time_filter.setFixedWidth(150)
        filter_area.addWidget(self._start_time_filter)

        # 结束时间
        end_label = QLabel(LABEL_TEXT["filter_end_time"])
        end_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(end_label)

        self._end_time_filter = QDateTimeEdit()
        self._end_time_filter.setObjectName(
            OBJECT_NAMES["end_time_filter"]
        )
        self._end_time_filter.setCalendarPopup(True)
        self._end_time_filter.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._end_time_filter.setSpecialValueText("不限")
        self._end_time_filter.setFixedWidth(150)
        filter_area.addWidget(self._end_time_filter)

        filter_area.addStretch()
        return filter_area

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
        """创建日志表格。

        Returns:
            QTableWidget: 日志表格。
        """
        table = QTableWidget()
        table.setObjectName(OBJECT_NAMES["log_table"])
        table.setColumnCount(len(COLUMN_HEADERS))
        table.setHorizontalHeaderLabels(COLUMN_HEADERS)

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
        self._first_page_btn.setObjectName(
            OBJECT_NAMES["first_page_btn"]
        )
        self._first_page_btn.setFixedHeight(28)
        self._first_page_btn.clicked.connect(self._on_first_page)
        pagination.addWidget(self._first_page_btn)

        self._prev_page_btn = QPushButton(BUTTON_TEXT["prev_page"])
        self._prev_page_btn.setObjectName(
            OBJECT_NAMES["prev_page_btn"]
        )
        self._prev_page_btn.setFixedHeight(28)
        self._prev_page_btn.clicked.connect(self._on_prev_page)
        pagination.addWidget(self._prev_page_btn)

        self._page_label = QLabel("1 / 1")
        self._page_label.setObjectName(OBJECT_NAMES["page_label"])
        self._page_label.setStyleSheet("padding: 0 8px;")
        pagination.addWidget(self._page_label)

        self._next_page_btn = QPushButton(BUTTON_TEXT["next_page"])
        self._next_page_btn.setObjectName(
            OBJECT_NAMES["next_page_btn"]
        )
        self._next_page_btn.setFixedHeight(28)
        self._next_page_btn.clicked.connect(self._on_next_page)
        pagination.addWidget(self._next_page_btn)

        self._last_page_btn = QPushButton(BUTTON_TEXT["last_page"])
        self._last_page_btn.setObjectName(
            OBJECT_NAMES["last_page_btn"]
        )
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
        """刷新操作日志数据。

        唯一刷新入口。
        流程: list_logs -> populate_table -> update_pagination ->
            update_status_bar。

        Raises:
            Exception: 刷新失败时弹出 QMessageBox 错误提示。
        """
        try:
            self._status_bar.setText("刷新中...")

            keyword = self._search_bar.text()
            operator_id = self._get_filter_int(
                self._operator_filter.text()
            )
            operation = self._get_operation_filter()
            module = self._get_filter_str(self._module_filter.text())
            start_time = self._get_filter_datetime(
                self._start_time_filter
            )
            end_time = self._get_filter_datetime(
                self._end_time_filter
            )

            data = self._log_service.list_logs(
                operator_id=operator_id,
                operation=operation,
                module=module,
                keyword=keyword if keyword else None,
                start_time=start_time,
                end_time=end_time,
                page=self._current_page,
                page_size=self._page_size,
            )

            self._logs = data.get("items", [])
            self._total = data.get("total", 0)

            self._populate_table()
            self._update_pagination()
            self._update_status_bar()

            self._status_bar.setText(STATUS_TEXT["refresh_completed"])
            logger.info(
                "操作日志刷新完成: page=%d, total=%d, items=%d",
                self._current_page,
                self._total,
                len(self._logs),
            )

        except Exception as e:
            self._status_bar.setText("刷新失败")
            logger.error(
                "操作日志刷新失败: %s", e, exc_info=True
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
        """将日志列表填充到表格中。"""
        self._table.setRowCount(len(self._logs))

        for row, log in enumerate(self._logs):
            self._table.setItem(
                row,
                COLUMN_INDEX["id"],
                QTableWidgetItem(str(log.get("id", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["operator"],
                QTableWidgetItem(
                    str(log.get("operator_id", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["operation"],
                QTableWidgetItem(str(log.get("operation", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["module"],
                QTableWidgetItem(str(log.get("module", ""))),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["target_type"],
                QTableWidgetItem(
                    str(log.get("target_type", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["target_id"],
                QTableWidgetItem(
                    str(log.get("target_id", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["description"],
                QTableWidgetItem(
                    str(log.get("description", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["created_at"],
                QTableWidgetItem(
                    str(log.get("created_at", ""))
                ),
            )

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
            keyword: 搜索关键词。
        """
        self._current_page = 1
        self.refresh()
        self.log_changed.emit()

    # ============================================================
    # 导出
    # ============================================================

    def _on_export(self) -> None:
        """导出数据按钮回调。

        调用 LogService.export_logs() 获取导出数据，
        禁止 View 生成 Excel 文件。
        """
        try:
            keyword = self._search_bar.text()
            operator_id = self._get_filter_int(
                self._operator_filter.text()
            )
            operation = self._get_operation_filter()
            module = self._get_filter_str(self._module_filter.text())
            start_time = self._get_filter_datetime(
                self._start_time_filter
            )
            end_time = self._get_filter_datetime(
                self._end_time_filter
            )

            data = self._log_service.export_logs(
                operator_id=operator_id,
                operation=operation,
                module=module,
                keyword=keyword if keyword else None,
                start_time=start_time,
                end_time=end_time,
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
    def _get_filter_str(text: str) -> str | None:
        """将文本转换为字符串筛选参数。

        Args:
            text: 输入文本。

        Returns:
            str | None: 有效字符串或 None。
        """
        if not text or not text.strip():
            return None
        return text.strip()

    def _get_operation_filter(self) -> str | None:
        """从操作类型下拉框获取筛选参数。

        Returns:
            str | None: 有效操作类型或 None。
        """
        value = self._operation_filter.currentText()
        if value == "全部" or not value:
            return None
        return value

    @staticmethod
    def _get_filter_datetime(
        widget: QDateTimeEdit,
    ) -> datetime | None:
        """从日期时间选择器获取筛选参数。

        Args:
            widget: QDateTimeEdit 控件。

        Returns:
            datetime | None: 有效日期时间或 None。
        """
        is_default = (
            widget.specialValueText()
            and widget.text() == widget.specialValueText()
        )
        if is_default:
            return None
        date = widget.dateTime()
        return datetime(
            date.date().year(),
            date.date().month(),
            date.date().day(),
            date.time().hour(),
            date.time().minute(),
        )


__all__ = [
    "SystemLogView",
]
