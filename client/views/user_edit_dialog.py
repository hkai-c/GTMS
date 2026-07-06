"""GTMS 桌面端用户编辑对话框 (UserEditDialog)

Sprint 3 — Task 3.12
严格依据 Development Roadmap、Sprint 3 Server API。

提供用户新增/编辑对话框：
    - 用户名输入
    - 姓名输入
    - 手机号输入
    - 密码输入（新增必填，编辑可为空）
    - 角色选择（QComboBox）
    - 启用状态（QCheckBox）

所有业务逻辑委托 UserService，禁止直接 HTTP。
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from client.services.user_service import UserService

logger = logging.getLogger("gtms.client")


class UserEditDialog(QDialog):
    """用户新增/编辑对话框。

    用于新增用户或编辑已有用户信息。
    编辑模式下密码字段为空表示不修改密码。

    Attributes:
        _user_service: UserService 实例。
        _mode: 模式（"create" 或 "edit"）。
        _user_id: 编辑模式下的用户 ID。
        _roles: 角色列表缓存。
        _result: 操作结果数据。

    Usage:
        # 新增
        dialog = UserEditDialog(user_service, mode="create")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_result()

        # 编辑
        dialog = UserEditDialog(user_service, mode="edit", user_id=1)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_result()
    """

    def __init__(
        self,
        user_service: UserService,
        mode: str = "create",
        user_id: int | None = None,
        user_data: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """初始化用户编辑对话框。

        Args:
            user_service: UserService 实例。
            mode: 模式（"create" 或 "edit"）。
            user_id: 编辑模式下的用户 ID（可选）。
            user_data: 编辑模式下的用户数据（可选，用于预填表单）。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._user_service: UserService = user_service
        self._mode: str = mode
        self._user_id: int | None = user_id
        self._roles: list[dict[str, Any]] = []
        self._result: dict[str, Any] | None = None

        # 窗口属性
        self._setup_window()

        # 构建 UI
        self._setup_ui()

        # 预填数据（编辑模式）
        if user_data:
            self._fill_form(user_data)

        # 加载角色列表
        self._load_roles()

        logger.debug("UserEditDialog 初始化: mode=%s, user_id=%s", mode, user_id)

    # ============================================================
    # 窗口设置
    # ============================================================

    def _setup_window(self) -> None:
        """设置对话框基本属性。"""
        if self._mode == "create":
            self.setWindowTitle("新增用户")
        else:
            self.setWindowTitle("编辑用户")
        self.setFixedSize(380, 320)
        self.setModal(True)

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建对话框 UI。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # 表单
        form = QFormLayout()
        form.setSpacing(8)

        # 用户名
        self._username_edit = QLineEdit()
        self._username_edit.setObjectName("username_edit")
        self._username_edit.setPlaceholderText("请输入用户名")
        if self._mode == "edit":
            self._username_edit.setEnabled(False)  # 编辑模式不可修改用户名
        form.addRow("用户名:", self._username_edit)

        # 姓名
        self._real_name_edit = QLineEdit()
        self._real_name_edit.setObjectName("real_name_edit")
        self._real_name_edit.setPlaceholderText("请输入真实姓名")
        form.addRow("姓名:", self._real_name_edit)

        # 手机号
        self._phone_edit = QLineEdit()
        self._phone_edit.setObjectName("phone_edit")
        self._phone_edit.setPlaceholderText("请输入手机号（可选）")
        form.addRow("手机号:", self._phone_edit)

        # 密码
        self._password_edit = QLineEdit()
        self._password_edit.setObjectName("password_edit")
        self._password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        if self._mode == "create":
            self._password_edit.setPlaceholderText("请输入密码（至少6位）")
        else:
            self._password_edit.setPlaceholderText("留空则不修改密码")
        form.addRow("密码:", self._password_edit)

        # 角色
        self._role_combo = QComboBox()
        self._role_combo.setObjectName("role_combo")
        form.addRow("角色:", self._role_combo)

        # 启用状态
        self._active_checkbox = QCheckBox("启用")
        self._active_checkbox.setObjectName("active_checkbox")
        self._active_checkbox.setChecked(True)
        form.addRow("状态:", self._active_checkbox)

        layout.addLayout(form)

        # 按钮
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.setObjectName("button_box")
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ============================================================
    # 数据加载
    # ============================================================

    def _fill_form(self, user_data: dict[str, Any]) -> None:
        """预填表单数据（编辑模式）。

        Args:
            user_data: 用户数据 dict。
        """
        self._username_edit.setText(user_data.get("username", ""))
        self._real_name_edit.setText(user_data.get("real_name", ""))
        self._phone_edit.setText(user_data.get("phone", ""))
        self._active_checkbox.setChecked(user_data.get("is_active", True))

        # 预选角色
        roles = user_data.get("roles", [])
        if roles:
            self._preselected_role_id = roles[0].get("id")

    def _load_roles(self) -> None:
        """加载角色列表到下拉框。"""
        try:
            data = self._user_service.get_roles()
            self._roles = data.get("items", [])
            self._role_combo.clear()
            for role in self._roles:
                self._role_combo.addItem(role.get("name", ""), role.get("id"))
            # 编辑模式预选角色
            if self._mode == "edit" and hasattr(self, "_preselected_role_id"):
                for i in range(self._role_combo.count()):
                    if self._role_combo.itemData(i) == self._preselected_role_id:
                        self._role_combo.setCurrentIndex(i)
                        break
        except Exception as e:
            logger.error("加载角色列表失败: %s", e)
            QMessageBox.warning(self, "错误", f"加载角色列表失败: {e}")

    # ============================================================
    # 提交
    # ============================================================

    def _on_accept(self) -> None:
        """处理确认按钮。

        校验表单 → 调用 UserService → 存储结果 → 接受对话框。
        """
        username = self._username_edit.text().strip()
        real_name = self._real_name_edit.text().strip()
        phone = self._phone_edit.text().strip() or None
        password = self._password_edit.text()
        is_active = self._active_checkbox.isChecked()
        role_id = self._role_combo.currentData()

        # 基本校验
        if not username:
            QMessageBox.warning(self, "校验失败", "请输入用户名")
            return
        if not real_name:
            QMessageBox.warning(self, "校验失败", "请输入真实姓名")
            return
        if self._mode == "create" and not password:
            QMessageBox.warning(self, "校验失败", "请输入密码")
            return
        if self._mode == "create" and len(password) < 6:
            QMessageBox.warning(self, "校验失败", "密码至少6位")
            return

        role_ids = [role_id] if role_id is not None else None

        try:
            if self._mode == "create":
                self._result = self._user_service.create_user(
                    username=username,
                    password=password,
                    real_name=real_name,
                    phone=phone,
                    role_ids=role_ids,
                )
            else:
                self._result = self._user_service.update_user(
                    user_id=self._user_id,
                    real_name=real_name,
                    phone=phone,
                    is_active=is_active,
                    password=password if password else None,
                    role_ids=role_ids,
                )
            self.accept()
        except Exception as e:
            logger.error("用户操作失败: %s", e)
            QMessageBox.critical(self, "操作失败", str(e))

    # ============================================================
    # 公开 API
    # ============================================================

    def get_result(self) -> dict[str, Any] | None:
        """获取操作结果。

        Returns:
            dict | None: 操作结果数据，None 表示取消。
        """
        return self._result


__all__ = [
    "UserEditDialog",
]