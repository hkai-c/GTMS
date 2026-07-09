"""GTMS 桌面端试磨任务编辑对话框 (TaskEditDialog)

Sprint 5 — Task 5.8
严格依据 SRS §4.3、UI_PROTOTYPE §7、CODE_WIKI.md §15.5 / §15.6 / §15.7。

提供试磨任务新增/编辑对话框：
    - 客户输入
    - 加工要求输入
    - 销售输入
    - 快递单号输入
    - 备注输入

Pure UI 组件，不调用任何业务服务。
所有业务逻辑由 TrialTaskView → Desktop TaskService → Server TaskService 负责。
"""

import logging
from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义 (§15.7.25 / §15.7.26)
# ============================================================

WINDOW_TITLE_CREATE: str = "新增试磨任务"
WINDOW_TITLE_EDIT: str = "编辑试磨任务"

FORM_LABELS: dict[str, str] = {
    "customer": "客户:",
    "requirement": "加工要求:",
    "sales": "销售:",
    "tracking_no": "快递单号:",
    "remark": "备注:",
}

OBJECT_NAMES: dict[str, str] = {
    "customer_edit": "customer_edit",
    "requirement_edit": "requirement_edit",
    "sales_edit": "sales_edit",
    "tracking_no_edit": "tracking_no_edit",
    "remark_edit": "remark_edit",
    "button_box": "dialog_button_box",
}

DEFAULT_WIDTH: int = 420
DEFAULT_HEIGHT: int = 320

LOGGER_NAME: str = "gtms.client"


class TaskEditDialog(QDialog):
    """试磨任务新增/编辑对话框。

    Pure UI 组件，仅负责表单展示和数据采集。
    不调用 Desktop TaskService、ApiClient、Server、ORM、Database。

    Attributes:
        _mode: 模式（"create" 或 "edit"）。
        _result: 操作结果数据（用户输入）。

    Usage:
        # 新增
        dialog = TaskEditDialog(mode="create")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_result()

        # 编辑
        dialog = TaskEditDialog(mode="edit")
        dialog.fill_data(task_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_result()
    """

    def __init__(
        self,
        mode: str = "create",
        parent: QWidget | None = None,
    ) -> None:
        """初始化试磨任务编辑对话框。

        Args:
            mode: 模式（"create" 或 "edit"）。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._mode: str = mode
        self._result: dict[str, Any] | None = None

        self._setup_window()
        self._setup_ui()

        logger.debug("TaskEditDialog 初始化: mode=%s", mode)

    # ============================================================
    # 窗口设置
    # ============================================================

    def _setup_window(self) -> None:
        """设置对话框基本属性。"""
        if self._mode == "create":
            self.setWindowTitle(WINDOW_TITLE_CREATE)
        else:
            self.setWindowTitle(WINDOW_TITLE_EDIT)
        self.setFixedSize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.setModal(True)

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建对话框 UI。

        布局: QFormLayout + QDialogButtonBox。
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # 表单
        form = QFormLayout()
        form.setSpacing(8)

        # 客户
        self._customer_edit = QLineEdit()
        self._customer_edit.setObjectName(OBJECT_NAMES["customer_edit"])
        self._customer_edit.setPlaceholderText("请输入客户名称（必填）")
        form.addRow(FORM_LABELS["customer"], self._customer_edit)

        # 加工要求
        self._requirement_edit = QLineEdit()
        self._requirement_edit.setObjectName(OBJECT_NAMES["requirement_edit"])
        self._requirement_edit.setPlaceholderText("请输入加工要求（必填）")
        form.addRow(FORM_LABELS["requirement"], self._requirement_edit)

        # 销售
        self._sales_edit = QLineEdit()
        self._sales_edit.setObjectName(OBJECT_NAMES["sales_edit"])
        self._sales_edit.setPlaceholderText("请输入销售姓名（必填）")
        form.addRow(FORM_LABELS["sales"], self._sales_edit)

        # 快递单号
        self._tracking_no_edit = QLineEdit()
        self._tracking_no_edit.setObjectName(OBJECT_NAMES["tracking_no_edit"])
        self._tracking_no_edit.setPlaceholderText("请输入快递单号（可选）")
        form.addRow(FORM_LABELS["tracking_no"], self._tracking_no_edit)

        # 备注
        self._remark_edit = QLineEdit()
        self._remark_edit.setObjectName(OBJECT_NAMES["remark_edit"])
        self._remark_edit.setPlaceholderText("请输入备注（可选）")
        form.addRow(FORM_LABELS["remark"], self._remark_edit)

        layout.addLayout(form)

        # 按钮
        ok_btn = QDialogButtonBox.StandardButton.Ok
        cancel_btn = QDialogButtonBox.StandardButton.Cancel
        self._button_box = QDialogButtonBox(ok_btn | cancel_btn)
        self._button_box.setObjectName(OBJECT_NAMES["button_box"])
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ============================================================
    # 数据采集与提交
    # ============================================================

    def _on_accept(self) -> None:
        """处理确认按钮。

        收集表单数据 → 存储到 _result → 接受对话框。
        不调用任何业务服务，仅采集用户输入。
        """
        self._result = {
            "customer": self._customer_edit.text().strip(),
            "requirement": self._requirement_edit.text().strip(),
            "sales": self._sales_edit.text().strip(),
            "tracking_no": self._tracking_no_edit.text().strip() or None,
            "remark": self._remark_edit.text().strip() or None,
        }
        self.accept()
        logger.debug("TaskEditDialog 确认提交: %s", self._mode)

    # ============================================================
    # 公开 API
    # ============================================================

    def get_result(self) -> dict[str, Any] | None:
        """获取操作结果。

        Returns:
            dict | None: 用户输入的数据，None 表示取消。
        """
        return self._result

    def fill_data(self, data: dict[str, Any]) -> None:
        """预填表单数据（编辑模式）。

        Args:
            data: 任务数据 dict。
        """
        self._customer_edit.setText(data.get("customer", ""))
        self._requirement_edit.setText(data.get("requirement", ""))
        self._sales_edit.setText(data.get("sales", ""))
        self._tracking_no_edit.setText(data.get("tracking_no", ""))
        self._remark_edit.setText(data.get("remark", ""))


__all__ = [
    "TaskEditDialog",
]
