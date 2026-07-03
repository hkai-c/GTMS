"""Attachment ORM 模型 — 附件表

Sprint 1 — Task 1.10
参考：DB_DESIGN.md §4.9, CODE_WIKI.md §5.2.4
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Integer, Enum as SAEnum, ForeignKey, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel
from server.enums.file_type import FileType

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.trial_task import TrialTask


class Attachment(BaseModel):
    """附件模型 — 记录试磨任务关联的附件文件信息

    字段清单（12 列 = 6 业务 + 6 BaseModel）：
        业务字段:
            task_id     - 关联试磨任务（FK → trial_tasks.id, CASCADE）
            file_type   - 附件类型（FileType: image/document/cad/video）
            file_name   - 原始文件名（VARCHAR(255), NOT NULL）
            file_path   - 存储路径（VARCHAR(500), NOT NULL）
            file_size   - 文件大小（INT, 可选, 单位 bytes）
            uploaded_by - 上传人（FK → users.id, RESTRICT）

        BaseModel 继承字段:
            id, created_at, updated_at, created_by, updated_by, is_deleted

        关联关系:
            task     - 关联的试磨任务（多对一, back_populates="attachments"）
            uploader - 上传人用户（多对一）
    """

    __tablename__ = "attachments"

    # ============================================================
    # 表级约束
    # ============================================================

    __table_args__ = (
        Index("ix_attachments_task_id", "task_id"),
        Index("ix_attachments_file_type", "file_type"),
    )

    # ============================================================
    # 业务字段
    # ============================================================

    task_id: Mapped[int] = mapped_column(
        ForeignKey("trial_tasks.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联试磨任务 ID",
    )

    file_type: Mapped[FileType] = mapped_column(
        SAEnum(FileType),
        nullable=False,
        comment="附件类型（image/document/cad/video）",
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="原始文件名",
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="存储路径",
    )

    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        comment="文件大小（bytes）",
    )

    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="上传人 ID",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    task: Mapped["TrialTask"] = relationship(
        "TrialTask",
        back_populates="attachments",
        lazy="selectin",
    )

    uploader: Mapped["User"] = relationship(
        "User",
        foreign_keys=[uploaded_by],
        lazy="selectin",
    )

    # ============================================================
    # 特殊方法
    # ============================================================

    def __repr__(self) -> str:
        attachment_id = self.id if self.id is not None else "?"
        return (
            f"<Attachment(id={attachment_id}, task_id={self.task_id}, "
            f"file_type={self.file_type}, file_name='{self.file_name}')>"
        )