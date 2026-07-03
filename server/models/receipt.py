"""Receipt ORM 模型 — 收件记录表

Sprint 1 — Task 1.6
参考：DB_DESIGN.md §4.5, CODE_WIKI.md §5.2.4
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Text, DateTime, ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.trial_task import TrialTask


class Receipt(BaseModel):
    """收件记录模型 — 记录技术员收到客户工件的登记信息

    字段清单（10 列 = 4 业务 + 6 BaseModel）：
        业务字段:
            task_id      - 关联试磨任务（FK → trial_tasks.id, UNIQUE, CASCADE）
            received_at  - 收件日期时间
            receiver_id  - 收件人（FK → users.id, RESTRICT）
            image_paths  - 工件图片路径（JSON 数组文本, 可选）

        BaseModel 继承字段:
            id, created_at, updated_at, created_by, updated_by, is_deleted

        关联关系:
            task     - 关联的试磨任务（一对一, back_populates="receipt"）
            receiver - 收件人用户（多对一）
    """

    __tablename__ = "receipts"

    # ============================================================
    # 业务字段
    # ============================================================

    task_id: Mapped[int] = mapped_column(
        ForeignKey("trial_tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="关联试磨任务 ID",
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="收件日期时间",
    )

    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="收件人 ID",
    )

    image_paths: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="工件图片路径（JSON 数组）",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    task: Mapped["TrialTask"] = relationship(
        "TrialTask",
        back_populates="receipt",
        uselist=False,
        lazy="selectin",
    )

    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        lazy="selectin",
    )

    # ============================================================
    # 特殊方法
    # ============================================================

    def __repr__(self) -> str:
        receipt_id = self.id if self.id is not None else "?"
        return (
            f"<Receipt(id={receipt_id}, task_id={self.task_id}, "
            f"receiver_id={self.receiver_id})>"
        )