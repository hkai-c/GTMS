"""GTMS 桌面端客户管理页面 (CustomerView)

Sprint 4 — Task 4.5
严格依据 Development Roadmap、UI_PROTOTYPE §5。

提供客户管理界面：
    - 客户列表（QTableWidget）
    - 搜索（公司名称）
    - 新增/编辑客户
    - 分页（第一页/上一页/下一页/最后一页）

所有业务逻辑委托 Desktop CustomerService，禁止直接 HTTP。
不提供删除功能（Customer 永久保留）。
"""

import logging
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
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

from client.services.customer_service import CustomerService
from client.views.customer_edit_dialog import CustomerEditDialog

logger = logging.getLogger("gtms.client")


class CustomerView(QWidget):
    """GTMS 桌面端客户管理页面。

    提供客户查询、新增、编辑界面，支持分页和搜索。
    不提供删除功能。

    Signals:
        customer_changed: 客户信息变更（新增/编辑后发射）。

    Attributes:
        _customer_service: CustomerService 实例。
        _customers: 当前客户列表缓存。
        _current_page: 当前页码。
        _page_size: 每页条数。
        _total: 总记录数。
        _search_keyword: 当前搜索关键词。

    Usage:
        view = CustomerView(customer_service)
        view.customer_changed.connect(on_customer_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    customer_changed = Signal()

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        customer_service: CustomerService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化客户管理页面。

        Args:
            customer_service: CustomerService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._customer_service: CustomerService = customer_service
        self._customers: list[dict[str, Any]] = []
        self._current_page: int = 1
        self._page_size: int = 20
        self._total: int = 0
        self._search_keyword: str = ""

        self._setup_ui()

        logger.debug("CustomerView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建客户管理页面 UI。

        布局: 标题 → 工具栏 → 表格 → 分页栏。
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # --- 标题 ---
        title = QLabel("客户管理")
        title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #333333;"
        )
        layout.addWidget(title)

        # --- 工具栏 ---
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)

        # --- 表格 ---
        self._table = self._create_table()
        layout.addWidget(self._table, 1)

        # --- 分页栏 ---
        pagination = self._create_pagination()
        layout.addLayout(pagination)

    # ============================================================
    # 工具栏
    # ============================================================

    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏。

        Returns:
            QHBoxLayout: 工具栏布局。
        """
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        # 新增客户
        self._add_btn = QPushButton("新增客户")
        self._add_btn.setObjectName("add_btn")
        self._add_btn.setFixedHeight(30)
        self._add_btn.clicked.connect(self._on_add_customer)
        toolbar.addWidget(self._add_btn)

        # 编辑客户
        self._edit_btn = QPushButton("编辑客户")
        self._edit_btn.setObjectName("edit_btn")
        self._edit_btn.setFixedHeight(30)
        self._edit_btn.clicked.connect(self._on_edit_customer)
        toolbar.addWidget(self._edit_btn)

        # 刷新
        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.setObjectName("refresh_btn")
        self._refresh_btn.setFixedHeight(30)
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)

        # 弹性空间
        toolbar.addStretch()

        # 搜索框
        self._search_edit = QLineEdit()
        self._search_edit.setObjectName("search_edit")
        self._search_edit.setPlaceholderText("搜索公司名称...")
        self._search_edit.setFixedWidth(200)
        self._search_edit.setFixedHeight(30)
        self._search_edit.returnPressed.connect(self._on_search)
        toolbar.addWidget(self._search_edit)

        # 搜索按钮
        self._search_btn = QPushButton("搜索")
        self._search_btn.setObjectName("search_btn")
        self._search_btn.setFixedHeight(30)
        self._search_btn.clicked.connect(self._on_search)
        toolbar.addWidget(self._search_btn)

        return toolbar

    # ============================================================
    # 表格
    # ============================================================

    def _create_table(self) -> QTableWidget:
        """创建客户列表表格。

        Returns:
            QTableWidget: 客户列表表格。
        """
        table = QTableWidget()
        table.setObjectName("customer_table")

        # 列定义
        columns = ["公司名称", "联系人", "电话", "邮箱", "地址", "创建时间"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

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
        self._first_btn = QPushButton("第一页")
        self._first_btn.setObjectName("first_btn")
        self._first_btn.setFixedHeight(28)
        self._first_btn.clicked.connect(self._on_first_page)
        pagination.addWidget(self._first_btn)

        # 上一页
        self._prev_btn = QPushButton("上一页")
        self._prev_btn.setObjectName("prev_btn")
        self._prev_btn.setFixedHeight(28)
        self._prev_btn.clicked.connect(self._on_prev_page)
        pagination.addWidget(self._prev_btn)

        # 当前页
        self._page_label = QLabel("第 1 页")
        self._page_label.setObjectName("page_label")
        self._page_label.setStyleSheet("font-size: 12px; color: #333333;")
        pagination.addWidget(self._page_label)

        # 下一页
        self._next_btn = QPushButton("下一页")
        self._next_btn.setObjectName("next_btn")
        self._next_btn.setFixedHeight(28)
        self._next_btn.clicked.connect(self._on_next_page)
        pagination.addWidget(self._next_btn)

        # 最后一页
        self._last_btn = QPushButton("最后一页")
        self._last_btn.setObjectName("last_btn")
        self._last_btn.setFixedHeight(28)
        self._last_btn.clicked.connect(self._on_last_page)
        pagination.addWidget(self._last_btn)

        pagination.addStretch()

        # 共 XX 条记录
        self._total_label = QLabel("共 0 条记录")
        self._total_label.setObjectName("total_label")
        self._total_label.setStyleSheet(
            "font-size: 11px; color: #888888;"
        )
        pagination.addWidget(self._total_label)

        return pagination

    # ============================================================
    # 数据和分页
    # ============================================================

    def refresh(self) -> None:
        """刷新客户列表。

        调用 CustomerService.list_customers() 加载数据到表格。
        重新从当前页请求服务器，不使用本地缓存。
        """
        try:
            data = self._customer_service.list_customers(
                company_name=self._search_keyword or None,
                page=self._current_page,
                page_size=self._page_size,
            )
            self._customers = data.get("items", [])
            self._total = data.get("total", 0)
            self._populate_table(self._customers)
            self._update_pagination_ui()
            logger.info(
                "客户列表刷新: page=%d, total=%d",
                self._current_page,
                self._total,
            )
        except Exception as e:
            logger.error("刷新客户列表失败: %s", e)
            QMessageBox.critical(self, "加载失败", f"加载客户列表失败: {e}")

    def _populate_table(self, customers: list[dict[str, Any]]) -> None:
        """填充表格数据。

        Args:
            customers: 客户列表。
        """
        self._table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            # 公司名称
            self._table.setItem(
                row, 0,
                QTableWidgetItem(customer.get("company_name", "")),
            )
            # 联系人
            self._table.setItem(
                row, 1,
                QTableWidgetItem(customer.get("contact_person", "")),
            )
            # 电话
            self._table.setItem(
                row, 2,
                QTableWidgetItem(customer.get("phone", "")),
            )
            # 邮箱
            self._table.setItem(
                row, 3,
                QTableWidgetItem(customer.get("email", "")),
            )
            # 地址
            self._table.setItem(
                row, 4,
                QTableWidgetItem(customer.get("address", "")),
            )
            # 创建时间
            created_at = customer.get("created_at", "")
            self._table.setItem(
                row, 5,
                QTableWidgetItem(str(created_at)),
            )

    def _update_pagination_ui(self) -> None:
        """更新分页栏 UI 状态。"""
        total_pages = max(1, (self._total + self._page_size - 1) // self._page_size)

        self._page_label.setText(
            f"第 {self._current_page} / {total_pages} 页"
        )
        self._total_label.setText(f"共 {self._total} 条记录")

        # 按钮状态
        self._first_btn.setEnabled(self._current_page > 1)
        self._prev_btn.setEnabled(self._current_page > 1)
        self._next_btn.setEnabled(self._current_page < total_pages)
        self._last_btn.setEnabled(self._current_page < total_pages)

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

    def _on_search(self) -> None:
        """搜索客户。

        按公司名称模糊搜索，重置到第一页。
        """
        self._search_keyword = self._search_edit.text().strip()
        self._current_page = 1
        self.refresh()

    # ============================================================
    # 新增客户
    # ============================================================

    def _on_add_customer(self) -> None:
        """新增客户。

        打开 CustomerEditDialog → 调用 CustomerService.create_customer() → 刷新。
        """
        dialog = CustomerEditDialog(
            self._customer_service,
            mode="create",
            parent=self,
        )
        if dialog.exec() == CustomerEditDialog.DialogCode.Accepted:
            self.refresh()
            self.customer_changed.emit()
            logger.info("客户新增完成")

    # ============================================================
    # 编辑客户
    # ============================================================

    def _on_edit_customer(self) -> None:
        """编辑客户。

        获取选中行 → 打开 CustomerEditDialog → 调用 CustomerService.update_customer() → 刷新。
        """
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要编辑的客户")
            return

        customer = self._customers[row]
        customer_id = customer.get("id")

        dialog = CustomerEditDialog(
            self._customer_service,
            mode="edit",
            customer_id=customer_id,
            customer_data=customer,
            parent=self,
        )
        if dialog.exec() == CustomerEditDialog.DialogCode.Accepted:
            self.refresh()
            self.customer_changed.emit()
            logger.info("客户编辑完成: customer_id=%d", customer_id)


__all__ = [
    "CustomerView",
]