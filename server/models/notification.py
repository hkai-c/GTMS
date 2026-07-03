"""Notification ORM 模型 — 消息提醒表

Sprint 1 — Task 1.12
参考：DB_DESIGN.md §4.11, CODE_WIKI.md §5.2.4
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Text, Boolean, Enum as SAEnum, ForeignKey, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel
from server.enums.notify_type import NotifyType

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.trial_task import TrialTask


class Notification(BaseModel):
    """消息提醒模型 — 记录系统自动生成的消息提醒

    字段清单（11 列 = 5 业务 + 6 BaseModel）：
        业务字段:
            task_id        - 关联试磨任务（FK → trial_tasks.id, CASCADE）
            type           - 提醒类型（NotifyType: receipt_delay/grinding_delay/report_missing）
            message        - 提醒内容（TEXT, NOT NULL）
            is_read        - 是否已读（TINYINT(1), NOT NULL, 默认 False）
            target_user_id - 目标用户（FK → users.id, CASCADE）

        BaseModel 继承字段:
            id, created_at, updated_at, created_by, updated_by, is_deleted

        关联关系:
            task        - 关联的试磨任务（多对一, back_populates="notifications"）
            target_user - 目标用户（多对一, back_populates="notifications"）
    """

    __tablename__ = "notifications"

    # ============================================================
    # 表级约束
    # ============================================================

    __table_args__ = (
        Index("ix_notifications_target_user", "target_user_id"),
        Index("ix_notifications_is_read", "is_read"),
        Index("ix_notifications_type", "type"),
    )

    # ============================================================
    # 业务字段
    # ============================================================

    task_id: Mapped[int] = mapped_column(
        ForeignKey("trial_tasks.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联试磨任务 ID",
    )

    type: Mapped[NotifyType] = mapped_column(
        SAEnum(NotifyType),
        nullable=False,
        comment="提醒类型（receipt_delay/grinding_delay/report_missing）",
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="提醒内容",
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否已读",
    )

    target_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="目标用户 ID",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    task: Mapped["TrialTask"] = relationship(
        "TrialTask",
        back_populates="notifications",
        lazy="selectin",
    )

    target_user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        lazy="selectin",
    )

    # ============================================================
    # 特殊方法
    # ============================================================

    def __repr__(self) -> str:
        notification_id = self.id if self.id is not None else "?"
        return (
            f"<Notification(id={notification_id}, task_id={self.task_id}, "
            f"type={self.type}, is_read={self.is_read})>"
        )