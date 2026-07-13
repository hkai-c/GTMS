"""GTMS 桌面端检测管理页面 (InspectionView)

Sprint 8 — Task 8.5
严格依据 UI_PROTOTYPE §11、SRS §4.6、CODE_WIKI §15.5/§15.7/§15.10/§15.11/§15.12。

提供检测记录管理界面：
    - 检测记录列表（QTableWidget）
    - 搜索（SearchBar Widget）
    - 新增检测 / 编辑 / 完成检测 / 删除
    - 分页（第一页/上一页/下一页/最后一页）
    - StatusBar

所有业务逻辑委托 Desktop InspectionService，禁止直接 HTTP。
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

from client.services.inspection_service import InspectionService
from client.widgets.search_bar import SearchBar

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义
# ============================================================

WINDOW_TITLE: str = "检测管理"

TABLE_HEADERS: list[str] = [
    "ID",
    "任务编号",
    "检测人ID",
    "检测报告路径",
    "精度检测结果",
    "粗糙度检测结果",
    "检测结论",
    "创建时间",
    "更新时间",
]

COLUMN_INDEX: dict[str, int] = {
    "id": 0,
    "task_id": 1,
    "inspector_id": 2,
    "report_path": 3,
    "accuracy": 4,
    "roughness": 5,
    "result": 6,
    "created_at": 7,
    "updated_at": 8,
}

DEFAULT_PAGE_SIZE: int = 20

BUTTON_TEXT: dict[str, str] = {
    "add": "新增检测",
    "edit": "编辑",
    "finish": "完成检测",
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
    "inspection_table": "inspection_table",
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


class InspectionView(QWidget):
    """GTMS 桌面端检测管理页面。

    提供检测记录查询、新增、编辑、完成检测、删除界面，支持分页和搜索。

    Signals:
        inspection_changed: 检测记录变更（新增/编辑/完成/删除后发射）。

    Attributes:
        _inspection_service: InspectionService 实例。
        _inspections: 当前检测记录列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。
        _search_task_id: 当前搜索任务编号。

    Usage:
        view = InspectionView(inspection_service)
        view.inspection_changed.connect(on_inspection_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    inspection_changed: Signal = Signal()
    """检测记录变更信号（新增/编辑/完成/删除后发射）。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        inspection_service: InspectionService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化检测管理页面。

        Args:
            inspection_service: InspectionService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._inspection_service: InspectionService = inspection_service
        self._inspections: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total: int = 0
        self._search_task_id: int | None = None

        self._setup_ui()
        self._update_button_permissions()

        logger.debug("InspectionView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建检测管理页面 UI。

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

        # 新增检测
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

        # 完成检测
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
        """创建检测记录列表表格。

        Returns:
            QTableWidget: 检测记录列表表格。
        """
        table = QTableWidget()
        table.setObjectName(OBJECT_NAMES["inspection_table"])
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
        """刷新检测记录列表。

        调用 InspectionService.list_inspections() 加载数据到表格。
        重新从当前页请求服务器，不使用本地缓存。
        """
        try:
            data = self._inspection_service.list_inspections(
                task_id=self._search_task_id,
                page=self._current_page,
                page_size=self._page_size,
            )
            self._inspections = data.get("items", [])
            self._total = data.get("total", 0)
            self._populate_table(self._inspections)
            self._update_pagination_ui()
            self._update_status_bar("刷新完成")
            logger.info(
                "检测记录列表刷新: page=%d, total=%d, task_id=%s",
                self._current_page, self._total, self._search_task_id,
            )
        except Exception as e:
            logger.error("刷新检测记录列表失败: %s", e)
            QMessageBox.critical(
                self, "加载失败", f"加载检测记录列表失败: {e}"
            )

    def _populate_table(self, inspections: list[dict[str, Any]]) -> None:
        """填充表格数据。

        Args:
            inspections: 检测记录列表。
        """
        self._table.setRowCount(len(inspections))
        for row, inspection in enumerate(inspections):
            # ID
            self._table.setItem(
                row, COLUMN_INDEX["id"],
                QTableWidgetItem(str(inspection.get("id", ""))),
            )
            # 任务编号
            self._table.setItem(
                row, COLUMN_INDEX["task_id"],
                QTableWidgetItem(str(inspection.get("task_id", ""))),
            )
            # 检测人ID
            self._table.setItem(
                row, COLUMN_INDEX["inspector_id"],
                QTableWidgetItem(
                    str(inspection.get("inspector_id") or "")
                ),
            )
            # 检测报告路径
            self._table.setItem(
                row, COLUMN_INDEX["report_path"],
                QTableWidgetItem(
                    str(inspection.get("report_path") or "")
                ),
            )
            # 精度检测结果
            self._table.setItem(
                row, COLUMN_INDEX["accuracy"],
                QTableWidgetItem(
                    str(inspection.get("accuracy") or "")
                ),
            )
            # 粗糙度检测结果
            self._table.setItem(
                row, COLUMN_INDEX["roughness"],
                QTableWidgetItem(
                    str(inspection.get("roughness") or "")
                ),
            )
            # 检测结论
            self._table.setItem(
                row, COLUMN_INDEX["result"],
                QTableWidgetItem(
                    str(inspection.get("result") or "")
                ),
            )
            # 创建时间
            created_at = inspection.get("created_at", "")
            self._table.setItem(
                row, COLUMN_INDEX["created_at"],
                QTableWidgetItem(str(created_at)),
            )
            # 更新时间
            updated_at = inspection.get("updated_at", "")
            self._table.setItem(
                row, COLUMN_INDEX["updated_at"],
                QTableWidgetItem(str(updated_at)),
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
    # 新增检测
    # ============================================================

    def _on_add(self) -> None:
        """新增检测记录。

        InspectionDialog 未实现，暂显示提示。
        完成后的流程：
        InspectionDialog → create_inspection() → refresh()
        → emit inspection_changed。
        """
        QMessageBox.information(
            self, "功能提示", "新增检测功能将在后续实现。"
        )

    # ============================================================
    # 编辑检测记录
    # ============================================================

    def _on_edit(self) -> None:
        """编辑检测记录。

        InspectionDialog 未实现，暂显示提示。
        完成后的流程：
        选中行 → InspectionDialog → update_inspection() → refresh()
        → emit inspection_changed。
        """
        QMessageBox.information(
            self, "功能提示", "编辑检测记录功能将在后续实现。"
        )

    # ============================================================
    # 完成检测
    # ============================================================

    def _on_finish(self) -> None:
        """完成检测。

        InspectionFinishDialog 未实现，暂显示提示。
        完成后的流程：
        选中行 → InspectionFinishDialog → finish_inspection() → refresh()
        → emit inspection_changed。
        """
        QMessageBox.information(
            self, "功能提示", "完成检测功能将在后续实现。"
        )

    # ============================================================
    # 删除检测记录
    # ============================================================

    def _on_delete(self) -> None:
        """删除检测记录。

        确认 → delete_inspection() → refresh() → emit inspection_changed。
        """
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(
                self, "提示", "请先选择要删除的检测记录"
            )
            return

        inspection = self._inspections[row]
        inspection_id = inspection.get("id")

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除检测记录 #{inspection_id} 吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._inspection_service.delete_inspection(inspection_id)
            self.refresh()
            self.inspection_changed.emit()
            logger.info(
                "检测记录删除完成: inspection_id=%d", inspection_id,
            )
        except Exception as e:
            logger.error("删除检测记录失败: %s", e)
            QMessageBox.critical(
                self, "删除失败", f"删除检测记录失败: {e}"
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
    "InspectionView",
]
