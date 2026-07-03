"""GrindingRecord ORM 模型 — 试磨记录表

Sprint 1 — Task 1.7
参考：DB_DESIGN.md §4.6, CODE_WIKI.md §5.2.5, SRS.md §4.5
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Text, DateTime, ForeignKey, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.trial_task import TrialTask


class GrindingRecord(BaseModel):
    """试磨记录模型 — 记录每次试磨过程的详细信息

    字段清单（15 列 = 9 业务 + 6 BaseModel）：
        业务字段:
            task_id      - 关联试磨任务（FK → trial_tasks.id, UNIQUE, CASCADE）
            operator_id  - 试磨责任人（FK → users.id, RESTRICT）
            machine_type - 试磨机型（如"MGK-300"）
            wheel_type   - 砂轮型号
            params       - 加工参数（文本描述）
            start_time   - 工件领出时间
            end_time     - 完成时间
            image_paths  - 试磨图片路径（JSON 数组文本, 可选）
            fail_reason  - 失败原因（result_status=failed 时填写）

        BaseModel 继承字段:
            id, created_at, updated_at, created_by, updated_by, is_deleted

        关联关系:
            task     - 关联的试磨任务（一对一, back_populates="grinding"）
            operator - 试磨责任人用户（多对一）
    """

    __tablename__ = "grinding_records"

    __table_args__ = (
        Index("ix_grinding_operator_id", "operator_id"),
        Index("ix_grinding_machine_type", "machine_type"),
        Index("ix_grinding_start_time", "start_time"),
    )

    # ============================================================
    # 业务字段
    # ============================================================

    task_id: Mapped[int] = mapped_column(
        ForeignKey("trial_tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="关联试磨任务 ID",
    )

    operator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="试磨责任人 ID",
    )

    machine_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        comment="试磨机型",
    )

    wheel_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        comment="砂轮型号",
    )

    params: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="加工参数",
    )

    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
        comment="工件领出时间",
    )

    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
        comment="完成时间",
    )

    image_paths: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="试磨图片路径（JSON 数组）",
    )

    fail_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="失败原因（result_status=failed 时填写）",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    task: Mapped["TrialTask"] = relationship(
        "TrialTask",
        back_populates="grinding",
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
        rec_id = self.id if self.id is not None else "?"
        return (
            f"<GrindingRecord(id={rec_id}, task_id={self.task_id}, "
            f"operator_id={self.operator_id})>"
        )