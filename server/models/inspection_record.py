"""InspectionRecord ORM 模型 — 检测记录表

Sprint 1 — Task 1.8
参考：DB_DESIGN.md §4.7, CODE_WIKI.md §5.2.6, SRS.md §4.6
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Text, Enum as SAEnum, ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel
from server.enums import InspectionResult

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.trial_task import TrialTask


class InspectionRecord(BaseModel):
    """检测记录模型 — 记录试磨后的尺寸检测、精度检测及报告信息

    字段清单（12 列 = 6 业务 + 6 BaseModel）：
        业务字段:
            task_id      - 关联试磨任务（FK → trial_tasks.id, UNIQUE, CASCADE）
            report_path  - 检测报告文件路径（PDF/Word/Excel, 可选）
            accuracy     - 精度检测结果（可选）
            roughness    - 表面粗糙度检测结果（可选）
            result       - 检测结论（InspectionResult: pass/fail, 可选）
            inspector_id - 检测人（FK → users.id, SET NULL, 可选）

        BaseModel 继承字段:
            id, created_at, updated_at, created_by, updated_by, is_deleted

        关联关系:
            task      - 关联的试磨任务（一对一, back_populates="inspection"）
            inspector - 检测人用户（多对一, 可选）
    """

    __tablename__ = "inspection_records"

    # ============================================================
    # 业务字段
    # ============================================================

    task_id: Mapped[int] = mapped_column(
        ForeignKey("trial_tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="关联试磨任务 ID",
    )

    report_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        default=None,
        comment="检测报告文件路径",
    )

    accuracy: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        comment="精度检测结果",
    )

    roughness: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        comment="表面粗糙度检测结果",
    )

    result: Mapped[Optional[InspectionResult]] = mapped_column(
        SAEnum(InspectionResult),
        nullable=True,
        default=None,
        comment="检测结论（pass / fail）",
    )

    inspector_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        comment="检测人 ID",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    task: Mapped["TrialTask"] = relationship(
        "TrialTask",
        back_populates="inspection",
        uselist=False,
        lazy="selectin",
    )

    inspector: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[inspector_id],
        lazy="selectin",
    )

    # ============================================================
    # 特殊方法
    # ============================================================

    def __repr__(self) -> str:
        rec_id = self.id if self.id is not None else "?"
        return (
            f"<InspectionRecord(id={rec_id}, task_id={self.task_id}, "
            f"result={self.result})>"
        )