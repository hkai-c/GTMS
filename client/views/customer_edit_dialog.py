"""GTMS 桌面端客户编辑对话框 (CustomerEditDialog)

Sprint 4 — Task 4.5
严格依据 Development Roadmap、UI_PROTOTYPE §5。

提供客户新增/编辑对话框：
    - 公司名称输入
    - 联系人输入
    - 电话输入
    - 邮箱输入
    - 地址输入
    - 备注输入

所有业务逻辑委托 Desktop CustomerService，禁止直接 HTTP。
不实现任何数据校验（全部由 Server CustomerService 负责）。
"""

import logging
from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from client.services.customer_service import CustomerService

logger = logging.getLogger("gtms.client")


class CustomerEditDialog(QDialog):
    """客户新增/编辑对话框。

    用于新增客户或编辑已有客户信息。
    编辑模式下公司名称可修改（与用户编辑不同，用户名不可修改）。

    Attributes:
        _customer_service: CustomerService 实例。
        _mode: 模式（"create" 或 "edit"）。
        _customer_id: 编辑模式下的客户 ID。
        _result: 操作结果数据。

    Usage:
        # 新增
        dialog = CustomerEditDialog(customer_service, mode="create")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_result()

        # 编辑
        dialog = CustomerEditDialog(customer_service, mode="edit",
                                     customer_id=1, customer_data=data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_result()
    """

    def __init__(
        self,
        customer_service: CustomerService,
        mode: str = "create",
        customer_id: int | None = None,
        customer_data: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """初始化客户编辑对话框。

        Args:
            customer_service: CustomerService 实例。
            mode: 模式（"create" 或 "edit"）。
            customer_id: 编辑模式下的客户 ID（可选）。
            customer_data: 编辑模式下的客户数据（可选，用于预填表单）。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._customer_service: CustomerService = customer_service
        self._mode: str = mode
        self._customer_id: int | None = customer_id
        self._result: dict[str, Any] | None = None

        # 窗口属性
        self._setup_window()

        # 构建 UI
        self._setup_ui()

        # 预填数据（编辑模式）
        if customer_data:
            self._fill_form(customer_data)

        logger.debug(
            "CustomerEditDialog 初始化: mode=%s, customer_id=%s",
            mode,
            customer_id,
        )

    # ============================================================
    # 窗口设置
    # ============================================================

    def _setup_window(self) -> None:
        """设置对话框基本属性。"""
        if self._mode == "create":
            self.setWindowTitle("新增客户")
        else:
            self.setWindowTitle("编辑客户")
        self.setFixedSize(400, 340)
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

        # 公司名称
        self._company_name_edit = QLineEdit()
        self._company_name_edit.setObjectName("company_name_edit")
        self._company_name_edit.setPlaceholderText("请输入公司名称（必填）")
        form.addRow("公司名称:", self._company_name_edit)

        # 联系人
        self._contact_person_edit = QLineEdit()
        self._contact_person_edit.setObjectName("contact_person_edit")
        self._contact_person_edit.setPlaceholderText("请输入联系人（可选）")
        form.addRow("联系人:", self._contact_person_edit)

        # 电话
        self._phone_edit = QLineEdit()
        self._phone_edit.setObjectName("phone_edit")
        self._phone_edit.setPlaceholderText("请输入电话（可选）")
        form.addRow("电话:", self._phone_edit)

        # 邮箱
        self._email_edit = QLineEdit()
        self._email_edit.setObjectName("email_edit")
        self._email_edit.setPlaceholderText("请输入邮箱（可选）")
        form.addRow("邮箱:", self._email_edit)

        # 地址
        self._address_edit = QLineEdit()
        self._address_edit.setObjectName("address_edit")
        self._address_edit.setPlaceholderText("请输入地址（可选）")
        form.addRow("地址:", self._address_edit)

        # 备注
        self._remark_edit = QLineEdit()
        self._remark_edit.setObjectName("remark_edit")
        self._remark_edit.setPlaceholderText("请输入备注（可选）")
        form.addRow("备注:", self._remark_edit)

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

    def _fill_form(self, customer_data: dict[str, Any]) -> None:
        """预填表单数据（编辑模式）。

        Args:
            customer_data: 客户数据 dict。
        """
        self._company_name_edit.setText(
            customer_data.get("company_name", "")
        )
        self._contact_person_edit.setText(
            customer_data.get("contact_person", "")
        )
        self._phone_edit.setText(customer_data.get("phone", ""))
        self._email_edit.setText(customer_data.get("email", ""))
        self._address_edit.setText(customer_data.get("address", ""))
        self._remark_edit.setText(customer_data.get("remark", ""))

    # ============================================================
    # 提交
    # ============================================================

    def _on_accept(self) -> None:
        """处理确认按钮。

        收集表单数据 → 调用 CustomerService → 存储结果 → 接受对话框。
        客户端不校验数据合法性，全部由 Server CustomerService 负责。
        """
        company_name = self._company_name_edit.text().strip()
        contact_person = self._contact_person_edit.text().strip() or None
        phone = self._phone_edit.text().strip() or None
        email = self._email_edit.text().strip() or None
        address = self._address_edit.text().strip() or None
        remark = self._remark_edit.text().strip() or None

        try:
            if self._mode == "create":
                self._result = self._customer_service.create_customer(
                    company_name=company_name,
                    contact_person=contact_person,
                    phone=phone,
                    email=email,
                    address=address,
                    remark=remark,
                )
            else:
                self._result = self._customer_service.update_customer(
                    customer_id=self._customer_id,
                    company_name=company_name,
                    contact_person=contact_person,
                    phone=phone,
                    email=email,
                    address=address,
                    remark=remark,
                )
            self.accept()
        except Exception as e:
            logger.error("客户操作失败: %s", e)
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
    "CustomerEditDialog",
]