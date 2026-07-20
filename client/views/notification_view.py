"""GTMS 桌面端消息提醒页面 (NotificationView)

Sprint 12 — Task 12.6
严格依据 SRS §4.9、§15.17 Notification Principle、
    §15.20 Desktop HTTP Mapping Principle。

提供消息提醒查看界面：
    - 筛选（SearchBar + 是否已读 + 消息类型）
    - 消息表格（QTableWidget，8 列）
    - 未读数量角标（Badge）
    - 全部已读按钮
    - 刷新按钮
    - 分页
    - StatusBar

所有业务逻辑委托 Desktop NotificationService。
只读，仅支持查看、标记已读、全部已读、刷新。
禁止新增、编辑、删除、生成 Notification。
"""

import logging
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
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

from client.services.notification_service import NotificationService
from client.widgets.search_bar import SearchBar

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义
# ============================================================

WINDOW_TITLE: str = "消息提醒"

COLUMN_HEADERS: list[str] = [
    "ID",
    "用户ID",
    "消息类型",
    "标题",
    "内容",
    "关联对象",
    "已读",
    "创建时间",
]

COLUMN_INDEX: dict[str, int] = {
    "id": 0,
    "user_id": 1,
    "notification_type": 2,
    "title": 3,
    "content": 4,
    "target_type": 5,
    "is_read": 6,
    "created_at": 7,
}

DEFAULT_PAGE_SIZE: int = 20

BUTTON_TEXT: dict[str, str] = {
    "refresh": "刷新",
    "mark_all_read": "全部已读",
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
    "is_read_filter": "is_read_filter",
    "type_filter": "type_filter",
    "toolbar": "toolbar",
    "refresh_btn": "refresh_btn",
    "mark_all_read_btn": "mark_all_read_btn",
    "unread_badge": "unread_badge",
    "notification_table": "notification_table",
    "pagination_widget": "pagination_widget",
    "first_page_btn": "first_page_btn",
    "prev_page_btn": "prev_page_btn",
    "next_page_btn": "next_page_btn",
    "last_page_btn": "last_page_btn",
    "page_label": "page_label",
    "total_label": "total_label",
    "status_bar": "status_bar",
}

IS_READ_OPTIONS: list[str] = [
    "全部",
    "未读",
    "已读",
]

NOTIFICATION_TYPE_OPTIONS: list[str] = [
    "全部",
    "收件超时",
    "试磨超时",
    "报告缺失",
]

STATUS_TEXT: dict[str, str] = {
    "ready": "就绪",
    "refreshing": "刷新中...",
    "refresh_completed": "刷新完成",
    "mark_all_read_completed": "全部已读完成",
    "refresh_failed": "刷新失败",
}

MESSAGE_TEXT: dict[str, str] = {
    "refresh_failed": "刷新消息提醒失败",
    "mark_all_read_failed": "全部已读失败",
    "mark_all_read_success": "全部已标记为已读",
}

LABEL_TEXT: dict[str, str] = {
    "filter_is_read": "是否已读",
    "filter_type": "消息类型",
}


class NotificationView(QWidget):
    """GTMS 桌面端消息提醒页面。

    提供消息查看、筛选、分页浏览、标记已读、全部已读界面。
    页面只读，仅支持：查看消息、标记已读、全部已读、刷新。

    Signals:
        notification_changed: 消息状态变化信号。

    Attributes:
        _notification_service: NotificationService 实例。
        _notifications: 当前消息列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。

    Usage:
        view = NotificationView(notification_service)
        view.notification_changed.connect(on_notification_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    notification_changed: Signal = Signal()
    """消息状态变化信号。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        notification_service: NotificationService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化消息提醒页面。

        Args:
            notification_service: NotificationService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._notification_service: NotificationService = (
            notification_service
        )
        self._notifications: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total: int = 0

        self._setup_ui()

        logger.debug("NotificationView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建消息提醒页面 UI。

        标准布局: 标题 → SearchBar → 筛选区域 → Toolbar + Badge →
        Table → Pagination → StatusBar。
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

        # 是否已读筛选
        is_read_label = QLabel(LABEL_TEXT["filter_is_read"])
        is_read_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(is_read_label)

        self._is_read_filter = QComboBox()
        self._is_read_filter.setObjectName(
            OBJECT_NAMES["is_read_filter"]
        )
        self._is_read_filter.addItems(IS_READ_OPTIONS)
        self._is_read_filter.setFixedWidth(100)
        filter_area.addWidget(self._is_read_filter)

        # 消息类型筛选
        type_label = QLabel(LABEL_TEXT["filter_type"])
        type_label.setStyleSheet("font-size: 12px;")
        filter_area.addWidget(type_label)

        self._type_filter = QComboBox()
        self._type_filter.setObjectName(
            OBJECT_NAMES["type_filter"]
        )
        self._type_filter.addItems(NOTIFICATION_TYPE_OPTIONS)
        self._type_filter.setFixedWidth(120)
        filter_area.addWidget(self._type_filter)

        filter_area.addStretch()
        return filter_area

    # ============================================================
    # 工具栏
    # ============================================================

    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏（含未读角标）。

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

        self._mark_all_read_btn = QPushButton(
            BUTTON_TEXT["mark_all_read"]
        )
        self._mark_all_read_btn.setObjectName(
            OBJECT_NAMES["mark_all_read_btn"]
        )
        self._mark_all_read_btn.setFixedHeight(30)
        self._mark_all_read_btn.clicked.connect(self._on_mark_all_read)
        toolbar.addWidget(self._mark_all_read_btn)

        toolbar.addStretch()

        # 未读数量角标
        self._unread_badge = QLabel("未读: 0")
        self._unread_badge.setObjectName(
            OBJECT_NAMES["unread_badge"]
        )
        self._unread_badge.setStyleSheet(
            "color: #ff4d4f; font-size: 13px; font-weight: bold;"
        )
        toolbar.addWidget(self._unread_badge)

        return toolbar

    # ============================================================
    # 表格
    # ============================================================

    def _create_table(self) -> QTableWidget:
        """创建消息表格。

        Returns:
            QTableWidget: 消息表格。
        """
        table = QTableWidget()
        table.setObjectName(OBJECT_NAMES["notification_table"])
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
        """刷新消息提醒数据。

        唯一刷新入口。
        流程: list_notifications → _populate_table →
            _update_unread_badge → _update_status_bar。

        Raises:
            Exception: 刷新失败时弹出 QMessageBox 错误提示。
        """
        try:
            self._status_bar.setText(STATUS_TEXT["refreshing"])

            is_read = self._get_is_read_filter()
            notification_type = self._get_notification_type_filter()
            keyword = self._search_bar.text()
            logger.debug(
                "刷新消息: keyword=%s", keyword
            )

            data = self._notification_service.list_notifications(
                is_read=is_read,
                notification_type=notification_type,
                page=self._current_page,
                page_size=self._page_size,
            )

            self._notifications = data.get("items", [])
            self._total = data.get("total", 0)

            self._populate_table()
            self._update_unread_badge()
            self._update_status_bar()

            self._status_bar.setText(
                STATUS_TEXT["refresh_completed"]
            )
            logger.info(
                "消息提醒刷新完成: page=%d, total=%d, items=%d",
                self._current_page,
                self._total,
                len(self._notifications),
            )

        except Exception as e:
            self._status_bar.setText(STATUS_TEXT["refresh_failed"])
            logger.error(
                "消息提醒刷新失败: %s", e, exc_info=True
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
        """将消息列表填充到表格中。"""
        self._table.setRowCount(len(self._notifications))

        for row, notification in enumerate(self._notifications):
            self._table.setItem(
                row,
                COLUMN_INDEX["id"],
                QTableWidgetItem(
                    str(notification.get("id", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["user_id"],
                QTableWidgetItem(
                    str(notification.get("user_id", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["notification_type"],
                QTableWidgetItem(
                    str(notification.get("notification_type", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["title"],
                QTableWidgetItem(
                    str(notification.get("title", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["content"],
                QTableWidgetItem(
                    str(notification.get("content", ""))
                ),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["target_type"],
                QTableWidgetItem(
                    str(notification.get("target_type", ""))
                ),
            )
            is_read_text = (
                "已读" if notification.get("is_read") else "未读"
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["is_read"],
                QTableWidgetItem(is_read_text),
            )
            self._table.setItem(
                row,
                COLUMN_INDEX["created_at"],
                QTableWidgetItem(
                    str(notification.get("created_at", ""))
                ),
            )

    # ============================================================
    # 更新未读角标
    # ============================================================

    def _update_unread_badge(self) -> None:
        """更新未读数量角标。

        调用 NotificationService.list_notifications
        查询未读总数。
        """
        try:
            data = self._notification_service.list_notifications(
                is_read=False,
                page=1,
                page_size=1,
            )
            unread_total = data.get("total", 0)
            self._unread_badge.setText(f"未读: {unread_total}")
        except Exception:
            self._unread_badge.setText("未读: ?")

    # ============================================================
    # 更新状态栏
    # ============================================================

    def _update_status_bar(self) -> None:
        """更新状态栏显示。"""
        total_pages = max(
            1,
            (self._total + self._page_size - 1) // self._page_size,
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
            1,
            (self._total + self._page_size - 1) // self._page_size,
        )
        if self._current_page < total_pages:
            self._current_page += 1
            self.refresh()

    def _on_last_page(self) -> None:
        """跳转到最后一页。"""
        total_pages = max(
            1,
            (self._total + self._page_size - 1) // self._page_size,
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
        logger.debug("搜索关键词: %s", keyword)
        self._current_page = 1
        self.refresh()
        self.notification_changed.emit()

    # ============================================================
    # 全部已读
    # ============================================================

    def _on_mark_all_read(self) -> None:
        """全部已读按钮回调。

        调用 NotificationService.mark_all_as_read() 批量标记。
        成功后刷新页面并发射 notification_changed 信号。
        """
        try:
            count = self._notification_service.mark_all_as_read()
            self._status_bar.setText(
                STATUS_TEXT["mark_all_read_completed"]
            )
            logger.info("全部已读完成: count=%d", count)
            QMessageBox.information(
                self,
                "提示",
                f"{MESSAGE_TEXT['mark_all_read_success']}，"
                f"共 {count} 条。",
            )
            self.notification_changed.emit()
            self.refresh()
        except Exception as e:
            logger.error(
                "全部已读失败: %s", e, exc_info=True
            )
            QMessageBox.critical(
                self,
                "错误",
                f"{MESSAGE_TEXT['mark_all_read_failed']}: {e}",
            )

    # ============================================================
    # 筛选参数辅助方法
    # ============================================================

    def _get_is_read_filter(self) -> bool | None:
        """从已读筛选下拉框获取筛选参数。

        Returns:
            bool | None: True=已读, False=未读, None=全部。
        """
        value = self._is_read_filter.currentText()
        if value == "已读":
            return True
        if value == "未读":
            return False
        return None

    def _get_notification_type_filter(self) -> str | None:
        """从消息类型下拉框获取筛选参数。

        Returns:
            str | None: 有效消息类型或 None（全部）。
        """
        value = self._type_filter.currentText()
        if value == "全部" or not value:
            return None
        return value


__all__ = [
    "NotificationView",
]
