"""GTMS 桌面端用户管理页面 (UserManageView)

Sprint 3 — Task 3.12
严格依据 Development Roadmap、Sprint 3 Server API。

提供用户管理界面：
    - 用户列表（QTableWidget）
    - 搜索（用户名）
    - 新增/编辑/删除用户
    - 启用/禁用用户
    - 权限控制按钮

所有业务逻辑委托 UserService，禁止直接 HTTP。
"""

import logging
from typing import Any

from PySide6.QtCore import Qt, Signal
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

from client.services.user_service import UserService
from client.views.user_edit_dialog import UserEditDialog

logger = logging.getLogger("gtms.client")


# ============================================================
# 权限常量
# ============================================================

# 可进入用户管理页面的角色
CAN_ACCESS_USER_MANAGE = ["administrator", "manager"]

# 可新增/编辑用户的角色
CAN_MODIFY_USER = ["administrator", "manager"]

# 可删除用户的角色
CAN_DELETE_USER = ["administrator"]


class UserManageView(QWidget):
    """GTMS 桌面端用户管理页面。

    提供用户 CRUD 操作界面，根据角色控制按钮权限。

    Signals:
        user_changed: 用户信息变更（新增/编辑/删除/启用/禁用后发射）。

    Attributes:
        _user_service: UserService 实例。
        _current_user: 当前登录用户信息。
        _role_name: 当前用户角色。
        _users: 当前用户列表缓存。

    Usage:
        view = UserManageView(user_service, current_user, role_name)
        view.user_changed.connect(on_user_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    user_changed = Signal()

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        user_service: UserService,
        current_user: dict[str, Any],
        role_name: str,
        parent: QWidget | None = None,
    ) -> None:
        """初始化用户管理页面。

        Args:
            user_service: UserService 实例。
            current_user: 当前登录用户信息 dict。
            role_name: 当前用户角色名称（小写）。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._user_service: UserService = user_service
        self._current_user: dict[str, Any] = current_user
        self._role_name: str = role_name
        self._users: list[dict[str, Any]] = []

        self._setup_ui()
        self._update_button_permissions()

        logger.debug("UserManageView 初始化: role=%s", role_name)

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建用户管理页面 UI。

        布局: 标题 → 工具栏 → 表格 → 状态栏。
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # --- 标题 ---
        title = QLabel("用户管理")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
        layout.addWidget(title)

        # --- 工具栏 ---
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)

        # --- 表格 ---
        self._table = self._create_table()
        layout.addWidget(self._table, 1)

        # --- 状态栏 ---
        self._status_label = QLabel("共 0 条记录")
        self._status_label.setStyleSheet("font-size: 11px; color: #888888;")
        layout.addWidget(self._status_label)

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

        # 新增用户
        self._add_btn = QPushButton("新增用户")
        self._add_btn.setObjectName("add_btn")
        self._add_btn.setFixedHeight(30)
        self._add_btn.clicked.connect(self._on_add_user)
        toolbar.addWidget(self._add_btn)

        # 编辑用户
        self._edit_btn = QPushButton("编辑用户")
        self._edit_btn.setObjectName("edit_btn")
        self._edit_btn.setFixedHeight(30)
        self._edit_btn.clicked.connect(self._on_edit_user)
        toolbar.addWidget(self._edit_btn)

        # 删除用户
        self._delete_btn = QPushButton("删除用户")
        self._delete_btn.setObjectName("delete_btn")
        self._delete_btn.setFixedHeight(30)
        self._delete_btn.clicked.connect(self._on_delete_user)
        toolbar.addWidget(self._delete_btn)

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
        self._search_edit.setPlaceholderText("搜索用户名...")
        self._search_edit.setFixedWidth(180)
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
        """创建用户列表表格。

        Returns:
            QTableWidget: 用户列表表格。
        """
        table = QTableWidget()
        table.setObjectName("user_table")

        # 列定义
        columns = ["用户名", "姓名", "手机号", "角色", "状态", "创建时间"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        # 表格属性
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
    # 权限控制
    # ============================================================

    def _update_button_permissions(self) -> None:
        """更新按钮权限。

        根据当前用户角色启用/禁用按钮。
        """
        can_modify = self._role_name in CAN_MODIFY_USER
        can_delete = self._role_name in CAN_DELETE_USER

        self._add_btn.setEnabled(can_modify)
        self._edit_btn.setEnabled(can_modify)
        self._delete_btn.setEnabled(can_delete)

        logger.debug("按钮权限更新: modify=%s, delete=%s", can_modify, can_delete)

    # ============================================================
    # 数据刷新
    # ============================================================

    def refresh(self) -> None:
        """刷新用户列表。

        调用 UserService.list_users() 加载数据到表格。
        """
        try:
            data = self._user_service.list_users()
            self._users = data.get("items", [])
            self._populate_table(self._users)
            self._status_label.setText(f"共 {len(self._users)} 条记录")
            logger.info("用户列表刷新: total=%d", len(self._users))
        except Exception as e:
            logger.error("刷新用户列表失败: %s", e)
            QMessageBox.critical(self, "加载失败", f"加载用户列表失败: {e}")

    def _populate_table(self, users: list[dict[str, Any]]) -> None:
        """填充表格数据。

        Args:
            users: 用户列表。
        """
        self._table.setRowCount(len(users))
        for row, user in enumerate(users):
            # 用户名
            self._table.setItem(row, 0, QTableWidgetItem(user.get("username", "")))

            # 姓名
            self._table.setItem(row, 1, QTableWidgetItem(user.get("real_name", "")))

            # 手机号
            self._table.setItem(row, 2, QTableWidgetItem(user.get("phone", "")))

            # 角色
            roles = user.get("roles", [])
            role_names = ", ".join(r.get("name", "") for r in roles)
            self._table.setItem(row, 3, QTableWidgetItem(role_names))

            # 状态
            is_active = user.get("is_active", True)
            status_item = QTableWidgetItem("启用" if is_active else "禁用")
            if is_active:
                status_item.setForeground(Qt.GlobalColor.green)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self._table.setItem(row, 4, status_item)

            # 创建时间
            created_at = user.get("created_at", "")
            self._table.setItem(row, 5, QTableWidgetItem(str(created_at)))

    # ============================================================
    # 搜索
    # ============================================================

    def _on_search(self) -> None:
        """搜索用户。

        按用户名模糊搜索，调用 UserService.list_users()。
        """
        username = self._search_edit.text().strip()
        try:
            if username:
                data = self._user_service.list_users(username=username)
            else:
                data = self._user_service.list_users()
            self._users = data.get("items", [])
            self._populate_table(self._users)
            self._status_label.setText(f"共 {len(self._users)} 条记录")
            logger.info("用户搜索: keyword=%s, total=%d", username, len(self._users))
        except Exception as e:
            logger.error("搜索用户失败: %s", e)
            QMessageBox.critical(self, "搜索失败", f"搜索用户失败: {e}")

    # ============================================================
    # 新增用户
    # ============================================================

    def _on_add_user(self) -> None:
        """新增用户。

        打开 UserEditDialog → 调用 UserService.create_user() → 刷新列表。
        """
        dialog = UserEditDialog(self._user_service, mode="create", parent=self)
        if dialog.exec() == UserEditDialog.DialogCode.Accepted:
            self.refresh()
            self.user_changed.emit()
            logger.info("用户新增完成")

    # ============================================================
    # 编辑用户
    # ============================================================

    def _on_edit_user(self) -> None:
        """编辑用户。

        获取选中行 → 打开 UserEditDialog → 调用 UserService.update_user() → 刷新列表。
        """
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要编辑的用户")
            return

        user = self._users[row]
        user_id = user.get("id")

        dialog = UserEditDialog(
            self._user_service,
            mode="edit",
            user_id=user_id,
            user_data=user,
            parent=self,
        )
        if dialog.exec() == UserEditDialog.DialogCode.Accepted:
            self.refresh()
            self.user_changed.emit()
            logger.info("用户编辑完成: user_id=%d", user_id)

    # ============================================================
    # 删除用户
    # ============================================================

    def _on_delete_user(self) -> None:
        """删除用户。

        获取选中行 → 确认 → 调用 UserService.delete_user() → 刷新列表。
        """
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要删除的用户")
            return

        user = self._users[row]
        user_id = user.get("id")
        username = user.get("username", "")

        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除用户 \"{username}\" 吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._user_service.delete_user(user_id)
            self.refresh()
            self.user_changed.emit()
            logger.info("用户删除完成: user_id=%d", user_id)
        except Exception as e:
            logger.error("删除用户失败: %s", e)
            QMessageBox.critical(self, "删除失败", str(e))

    # ============================================================
    # 启用 / 禁用
    # ============================================================

    def _on_toggle_active(self) -> None:
        """切换用户启用/禁用状态。

        获取选中行 → 调用 UserService.update_user(is_active=...) → 刷新列表。
        """
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择用户")
            return

        user = self._users[row]
        user_id = user.get("id")
        current_active = user.get("is_active", True)
        new_active = not current_active

        action = "启用" if new_active else "禁用"
        try:
            self._user_service.update_user(
                user_id=user_id,
                is_active=new_active,
            )
            self.refresh()
            self.user_changed.emit()
            logger.info("用户%s完成: user_id=%d", action, user_id)
        except Exception as e:
            logger.error("用户%s失败: %s", action, e)
            QMessageBox.critical(self, f"{action}失败", str(e))


__all__ = [
    "UserManageView",
    "CAN_ACCESS_USER_MANAGE",
    "CAN_MODIFY_USER",
    "CAN_DELETE_USER",
]