"""GTMS 桌面端试磨任务详情页 (TaskDetailView)

Sprint 5 — Task 5.9
严格依据 SRS §4.3、UI_PROTOTYPE §8、CODE_WIKI.md §15.5 / §15.6 / §15.7。

提供试磨任务详情展示：
    - 基础信息（任务编号、创建时间、更新时间）
    - 任务信息（客户、加工要求、销售、快递单号）
    - 状态信息（流程状态 StatusBadge、结果状态 StatusBadge）
    - 收件信息（流程状态 >= received 时显示）
    - 试磨信息（流程状态 >= grinding 时显示）
    - 检测信息（流程状态 >= completed 时显示）
    - 去向信息（流程状态 >= dispatched 时显示）

根据 process_status 动态控制各 GroupBox 显示/隐藏。
所有业务规则由 Server TaskService 负责，本页仅负责展示。
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from client.services.task_service import TaskService
from client.widgets.status_badge import StatusBadge

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义 (§15.7.25 / §15.7.26)
# ============================================================

WINDOW_TITLE: str = "试磨任务详情"

GROUP_TITLE: dict[str, str] = {
    "basic": "基础信息",
    "task": "任务信息",
    "status": "状态信息",
    "receiving": "收件信息",
    "grinding": "试磨信息",
    "inspection": "检测信息",
    "destination": "去向信息",
}

FIELD_LABEL: dict[str, str] = {
    "task_no": "任务编号:",
    "created_at": "创建时间:",
    "updated_at": "更新时间:",
    "customer": "客户:",
    "requirement": "加工要求:",
    "sales": "销售:",
    "tracking_no": "快递单号:",
    "process_status": "流程状态:",
    "result_status": "结果状态:",
    "failure_reason": "失败原因:",
    "destination": "工件去向:",
    "destination_date": "去向日期:",
}

OBJECT_NAMES: dict[str, str] = {
    "title_label": "title_label",
    "basic_group": "basic_group",
    "task_group": "task_group",
    "status_group": "status_group",
    "receiving_group": "receiving_group",
    "grinding_group": "grinding_group",
    "inspection_group": "inspection_group",
    "destination_group": "destination_group",
    "close_btn": "close_btn",
}

DEFAULT_WIDTH: int = 520
DEFAULT_HEIGHT: int = 600

LOGGER_NAME: str = "gtms.client"


class TaskDetailView(QWidget):
    """GTMS 桌面端试磨任务详情页。

    展示试磨任务全部信息，根据 process_status 动态显示各业务区块。
    使用 StatusBadge 显示流程状态和结果状态。

    Attributes:
        _task_service: TaskService 实例。
        _task_id: 当前任务 ID。
        _task_data: 当前任务数据。

    Usage:
        view = TaskDetailView(task_service)
        view.load_task(123)
        view.show()
    """

    def __init__(
        self,
        task_service: TaskService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化试磨任务详情页。

        Args:
            task_service: TaskService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._task_service: TaskService = task_service
        self._task_id: int | None = None
        self._task_data: dict[str, Any] | None = None

        self._setup_ui()
        logger.debug("TaskDetailView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建详情页 UI。

        滚动区域 + GroupBox 布局。
        """
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # 标题
        self._title_label = QLabel(WINDOW_TITLE)
        self._title_label.setObjectName(OBJECT_NAMES["title_label"])
        self._title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )
        main_layout.addWidget(self._title_label)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        # ---- 基础信息 GroupBox ----
        self._basic_group = self._create_basic_group()
        content_layout.addWidget(self._basic_group)

        # ---- 任务信息 GroupBox ----
        self._task_group = self._create_task_group()
        content_layout.addWidget(self._task_group)

        # ---- 状态信息 GroupBox ----
        self._status_group = self._create_status_group()
        content_layout.addWidget(self._status_group)

        # ---- 收件信息 GroupBox ----
        self._receiving_group = self._create_receiving_group()
        content_layout.addWidget(self._receiving_group)

        # ---- 试磨信息 GroupBox ----
        self._grinding_group = self._create_grinding_group()
        content_layout.addWidget(self._grinding_group)

        # ---- 检测信息 GroupBox ----
        self._inspection_group = self._create_inspection_group()
        content_layout.addWidget(self._inspection_group)

        # ---- 去向信息 GroupBox ----
        self._destination_group = self._create_destination_group()
        content_layout.addWidget(self._destination_group)

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        # 底部关闭按钮
        self._close_btn = QPushButton("关闭")
        self._close_btn.setObjectName(OBJECT_NAMES["close_btn"])
        self._close_btn.clicked.connect(self.close)
        main_layout.addWidget(self._close_btn)

    # ============================================================
    # GroupBox 创建
    # ============================================================

    def _create_group_box(self, key: str) -> QGroupBox:
        """创建通用 GroupBox。

        Args:
            key: GroupBox 标识键。

        Returns:
            QGroupBox: 创建的 GroupBox。
        """
        group = QGroupBox(GROUP_TITLE[key])
        group.setObjectName(OBJECT_NAMES[f"{key}_group"])
        layout = QFormLayout(group)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 16, 12, 8)
        return group

    def _add_form_row(
        self,
        group: QGroupBox,
        label_key: str,
    ) -> QLabel:
        """向 GroupBox 添加表单行。

        Args:
            group: 目标 GroupBox。
            label_key: 标签键。

        Returns:
            QLabel: 创建的值标签。
        """
        label = QLabel("-")
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        label.setStyleSheet("color: #333333;")
        group.layout().addRow(FIELD_LABEL[label_key], label)
        return label

    # ---- 基础信息 ----
    def _create_basic_group(self) -> QGroupBox:
        """创建基础信息 GroupBox。"""
        group = self._create_group_box("basic")
        self._task_no_label = self._add_form_row(group, "task_no")
        self._created_at_label = self._add_form_row(group, "created_at")
        self._updated_at_label = self._add_form_row(group, "updated_at")
        return group

    # ---- 任务信息 ----
    def _create_task_group(self) -> QGroupBox:
        """创建任务信息 GroupBox。"""
        group = self._create_group_box("task")
        self._customer_label = self._add_form_row(group, "customer")
        self._requirement_label = self._add_form_row(group, "requirement")
        self._sales_label = self._add_form_row(group, "sales")
        self._tracking_no_label = self._add_form_row(group, "tracking_no")
        return group

    # ---- 状态信息 ----
    def _create_status_group(self) -> QGroupBox:
        """创建状态信息 GroupBox。"""
        group = self._create_group_box("status")
        layout = group.layout()

        # 流程状态 — StatusBadge
        self._process_badge = StatusBadge("created", parent=self)
        layout.addRow(FIELD_LABEL["process_status"], self._process_badge)

        # 结果状态 — StatusBadge
        self._result_badge = StatusBadge("pending", parent=self)
        layout.addRow(FIELD_LABEL["result_status"], self._result_badge)

        # 失败原因
        self._failure_reason_label = QLabel("-")
        self._failure_reason_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addRow(
            FIELD_LABEL["failure_reason"], self._failure_reason_label
        )

        return group

    # ---- 收件信息 ----
    def _create_receiving_group(self) -> QGroupBox:
        """创建收件信息 GroupBox。"""
        group = self._create_group_box("receiving")
        self._receiving_label = QLabel("收件信息详情将在后续 Sprint 实现")
        self._receiving_label.setStyleSheet("color: #888888;")
        group.layout().addRow(self._receiving_label)
        return group

    # ---- 试磨信息 ----
    def _create_grinding_group(self) -> QGroupBox:
        """创建试磨信息 GroupBox。"""
        group = self._create_group_box("grinding")
        self._grinding_label = QLabel("试磨信息详情将在后续 Sprint 实现")
        self._grinding_label.setStyleSheet("color: #888888;")
        group.layout().addRow(self._grinding_label)
        return group

    # ---- 检测信息 ----
    def _create_inspection_group(self) -> QGroupBox:
        """创建检测信息 GroupBox。"""
        group = self._create_group_box("inspection")
        self._inspection_label = QLabel("检测信息详情将在后续 Sprint 实现")
        self._inspection_label.setStyleSheet("color: #888888;")
        group.layout().addRow(self._inspection_label)
        return group

    # ---- 去向信息 ----
    def _create_destination_group(self) -> QGroupBox:
        """创建去向信息 GroupBox。"""
        group = self._create_group_box("destination")
        self._destination_label = self._add_form_row(group, "destination")
        self._destination_date_label = self._add_form_row(
            group, "destination_date"
        )
        return group

    # ============================================================
    # 公开 API
    # ============================================================

    def load_task(self, task_id: int) -> None:
        """加载并显示任务详情。

        Args:
            task_id: 任务 ID。
        """
        self._task_id = task_id
        self.refresh()

    def refresh(self) -> None:
        """刷新任务详情。

        调用 TaskService.get_task() 加载数据并更新 UI。
        """
        if self._task_id is None:
            return

        try:
            self._task_data = self._task_service.get_task(self._task_id)
            self._update_ui()
            logger.info("任务详情刷新: task_id=%d", self._task_id)
        except Exception as e:
            logger.error("加载任务详情失败: %s", e)
            QMessageBox.critical(self, "加载失败", f"加载任务详情失败: {e}")

    # ============================================================
    # UI 更新
    # ============================================================

    def _update_ui(self) -> None:
        """根据任务数据更新全部 UI 控件。"""
        if self._task_data is None:
            return

        data = self._task_data

        # 基础信息
        self._task_no_label.setText(str(data.get("task_no", "-")))
        created_at = data.get("created_at", "")
        self._created_at_label.setText(str(created_at))
        updated_at = data.get("updated_at", "")
        self._updated_at_label.setText(str(updated_at))

        # 任务信息
        self._customer_label.setText(
            str(data.get("customer_name", data.get("customer_id", "-")))
        )
        self._requirement_label.setText(
            str(data.get("requirement", "-"))
        )
        self._sales_label.setText(
            str(data.get("sales_name", data.get("sales_id", "-")))
        )
        tracking_no = data.get("tracking_no")
        self._tracking_no_label.setText(
            str(tracking_no) if tracking_no else "-"
        )

        # 状态信息
        process_status = str(data.get("process_status", ""))
        result_status = str(data.get("result_status", ""))
        self._process_badge.set_status(process_status)
        self._result_badge.set_status(result_status)

        # 失败原因 — 仅在 result_status=failed 时显示
        failure_reason = data.get("failure_reason")
        if result_status == "failed" and failure_reason:
            self._failure_reason_label.setText(str(failure_reason))
            self._failure_reason_label.setVisible(True)
        else:
            self._failure_reason_label.setText("-")
            self._failure_reason_label.setVisible(False)

        # 去向信息
        destination = data.get("destination")
        self._destination_label.setText(
            str(destination) if destination else "-"
        )
        destination_date = data.get("destination_date")
        self._destination_date_label.setText(
            str(destination_date) if destination_date else "-"
        )

        # 动态 GroupBox 显示/隐藏
        self._update_group_visibility(process_status)

    def _update_group_visibility(self, process_status: str) -> None:
        """根据流程状态更新 GroupBox 显示/隐藏。

        GroupBox 显示规则（累积式）：
            - created:      基础信息 + 任务信息 + 状态信息
            - received:     + 收件信息
            - grinding:     + 试磨信息
            - completed:    + 检测信息
            - dispatched:   + 去向信息
            - closed:       全部显示

        Args:
            process_status: 流程状态值。
        """
        status_priority = {
            "created": 0,
            "received": 1,
            "grinding": 2,
            "completed": 3,
            "dispatched": 4,
            "closed": 5,
        }
        level = status_priority.get(process_status, 0)

        self._receiving_group.setVisible(level >= 1)
        self._grinding_group.setVisible(level >= 2)
        self._inspection_group.setVisible(level >= 3)
        self._destination_group.setVisible(level >= 4)

        logger.debug(
            "GroupBox 可见性更新: status=%s, level=%d",
            process_status,
            level
        )


__all__ = [
    "TaskDetailView",
]
