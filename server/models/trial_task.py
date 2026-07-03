"""
试磨任务模型 (TrialTask)

对应 DB_DESIGN.md §4.4。

字段（严格对照 DB_DESIGN.md）：
    - id:               主键
    - task_no:          任务编号 (TM202600001)
    - customer_id:      客户 ID（FK → customers.id）
    - requirement:      加工要求
    - tracking_no:      快递单号
    - sales_id:         销售 ID（FK → users.id）
    - process_status:   流程状态（TrialTaskProcessStatus）
    - result_status:    结果状态（TrialTaskResultStatus）
    - destination:      工件去向（DestinationType）
    - destination_date: 工件去向日期
    - failure_reason:   失败原因

使用方式:
    from server.models import TrialTask
    task = TrialTask(
        task_no="TM202600001",
        customer_id=1,
        requirement="加工要求描述",
        sales_id=1,
    )
"""

from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    Date,
    Enum as SAEnum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel
from server.enums import (
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
    DestinationType,
)

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.customer import Customer
    from server.models.receipt import Receipt
    from server.models.grinding_record import GrindingRecord
    from server.models.inspection_record import InspectionRecord
    from server.models.dispatch import Dispatch
    from server.models.attachment import Attachment
    from server.models.notification import Notification


class TrialTask(BaseModel):
    """试磨任务模型 — GTMS 核心业务表

    字段清单（16 列 = 10 业务 + 6 BaseModel）：
        业务字段:
            task_no          - 任务编号 (TM202600001)，唯一约束
            customer_id      - 客户 ID（FK → customers.id, RESTRICT）
            requirement      - 加工要求
            tracking_no      - 快递单号（可选）
            sales_id         - 销售 ID（FK → users.id, RESTRICT）
            process_status   - 流程状态（TrialTaskProcessStatus, 默认 CREATED）
            result_status    - 结果状态（TrialTaskResultStatus, 默认 PENDING）
            destination      - 工件去向（DestinationType, 可选）
            destination_date - 工件去向日期（可选）
            failure_reason   - 失败原因（result_status=failed 时填写, 可选）

        BaseModel 继承字段:
            id, created_at, updated_at, created_by, updated_by, is_deleted

        关联关系:
            customer  - 所属客户（多对一, back_populates="tasks"）
            sales     - 销售/创建人（多对一）
            receipt   - 收件记录（一对一, back_populates="task"）
            grinding  - 试磨记录（一对一, back_populates="task"）
            inspection- 检测记录（一对一, back_populates="task"）
            dispatch  - 工件去向（一对一, back_populates="task"）
            attachments- 附件（一对多, back_populates="task"）
            notifications- 消息提醒（一对多, back_populates="task"）
    """

    __tablename__ = "trial_tasks"

    # ============================================================
    # 表级约束
    # ============================================================

    __table_args__ = (
        Index("ix_trial_tasks_customer_id", "customer_id"),
        Index("ix_trial_tasks_sales_id", "sales_id"),
        Index("ix_trial_tasks_process_status", "process_status"),
        Index("ix_trial_tasks_result_status", "result_status"),
        Index("ix_trial_tasks_created_at", "created_at"),
        Index("ix_trial_tasks_is_deleted", "is_deleted"),
    )

    # ============================================================
    # 业务字段
    # ============================================================

    task_no: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        comment="任务编号 (TM202600001)",
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        comment="客户 ID",
    )

    requirement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="加工要求",
    )

    tracking_no: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        comment="快递单号",
    )

    sales_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="销售 ID",
    )

    process_status: Mapped[TrialTaskProcessStatus] = mapped_column(
        SAEnum(TrialTaskProcessStatus),
        nullable=False,
        default=TrialTaskProcessStatus.CREATED,
        comment="流程状态（created/received/grinding/dispatched/closed）",
    )

    result_status: Mapped[TrialTaskResultStatus] = mapped_column(
        SAEnum(TrialTaskResultStatus),
        nullable=False,
        default=TrialTaskResultStatus.PENDING,
        comment="结果状态（pending/passed/failed）",
    )

    destination: Mapped[Optional[DestinationType]] = mapped_column(
        SAEnum(DestinationType),
        nullable=True,
        default=None,
        comment="工件去向（returned_customer/retained_company/scrapped/returned_sales/other）",
    )

    destination_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        default=None,
        comment="工件去向日期",
    )

    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="失败原因（result_status=failed 时填写）",
    )

    # ============================================================
    # 关联关系（已实现模型）
    # ============================================================

    # 客户（多对一）
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="tasks",
        lazy="selectin",
    )

    # 销售/创建人（多对一）
    sales: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sales_id],
        lazy="selectin",
    )

    # 收件记录（一对一）
    receipt: Mapped[Optional["Receipt"]] = relationship(
        "Receipt",
        back_populates="task",
        uselist=False,
        lazy="selectin",
    )

    # 试磨记录（一对一）
    grinding: Mapped[Optional["GrindingRecord"]] = relationship(
        "GrindingRecord",
        back_populates="task",
        uselist=False,
        lazy="selectin",
    )

    # 检测记录（一对一）
    inspection: Mapped[Optional["InspectionRecord"]] = relationship(
        "InspectionRecord",
        back_populates="task",
        uselist=False,
        lazy="selectin",
    )

    # 工件去向（一对一）
    dispatch: Mapped[Optional["Dispatch"]] = relationship(
        "Dispatch",
        back_populates="task",
        uselist=False,
        lazy="selectin",
    )

    # 附件（一对多）
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        back_populates="task",
        lazy="selectin",
    )

    # 消息提醒（一对多）
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="task",
        lazy="selectin",
    )

    # ============================================================
    # TODO: 待后续 Task 补充的关联关系（当前无）
    # ============================================================
    #
    # 规则：双向 relationship（back_populates）仅在关联模型已实现时建立。
    # 未实现模型不得创建占位 relationship，应在对应模型开发时同步补充。

    def __repr__(self) -> str:
        task_id = self.id if self.id is not None else "?"
        return f"<TrialTask(id={task_id}, task_no='{self.task_no}', process_status={self.process_status})>"