"""Dispatch ORM 模型 — 工件去向表

Sprint 1 — Task 1.9
参考：DB_DESIGN.md §4.8, CODE_WIKI.md §5.2.4
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, DateTime, ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.trial_task import TrialTask


class Dispatch(BaseModel):
    """工件去向模型 — 记录试磨完成后工件的去向信息

    字段清单（10 列 = 4 业务 + 6 BaseModel）：
        业务字段:
            task_id       - 关联试磨任务（FK → trial_tasks.id, UNIQUE, CASCADE）
            direction     - 去向描述（VARCHAR(200), NOT NULL）
            dispatch_date - 去向日期（DATETIME, NOT NULL）
            operator_id   - 操作人（FK → users.id, RESTRICT）

        BaseModel 继承字段:
            id, created_at, updated_at, created_by, updated_by, is_deleted

        关联关系:
            task     - 关联的试磨任务（一对一, back_populates="dispatch"）
            operator - 操作人用户（多对一）
    """

    __tablename__ = "dispatches"

    # ============================================================
    # 业务字段
    # ============================================================

    task_id: Mapped[int] = mapped_column(
        ForeignKey("trial_tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="关联试磨任务 ID",
    )

    direction: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="去向描述",
    )

    dispatch_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="去向日期",
    )

    operator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="操作人 ID",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    task: Mapped["TrialTask"] = relationship(
        "TrialTask",
        back_populates="dispatch",
        uselist=False,
        lazy="selectin",
    )

    operator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[operator_id],
        lazy="selectin",
    )

    # ============================================================
    # 特殊方法
    # ============================================================

    def __repr__(self) -> str:
        dispatch_id = self.id if self.id is not None else "?"
        return (
            f"<Dispatch(id={dispatch_id}, task_id={self.task_id}, "
            f"direction='{self.direction}')>"
        )