"""SystemLog ORM 模型 — 系统日志表

Sprint 1 — Task 1.11
参考：DB_DESIGN.md §4.10, CODE_WIKI.md §5.2.4
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Integer, JSON, Enum as SAEnum, ForeignKey, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel
from server.enums.action_type import ActionType

if TYPE_CHECKING:
    from server.models.user import User


class SystemLog(BaseModel):
    """系统日志模型 — 记录用户操作行为审计日志

    字段清单（12 列 = 6 业务 + 6 BaseModel）：
        业务字段:
            user_id     - 操作人（FK → users.id, RESTRICT）
            action      - 操作类型（ActionType: create/update/delete/status_change）
            target_type - 操作对象类型（VARCHAR(50), NOT NULL）
            target_id   - 操作对象 ID（INT, 可选）
            changes     - 变更内容（JSON, 可选）
            ip_address  - IP 地址（VARCHAR(50), 可选）

        BaseModel 继承字段:
            id, created_at, updated_at, created_by, updated_by, is_deleted

        关联关系:
            user - 操作人用户（多对一, back_populates="system_logs"）
    """

    __tablename__ = "system_logs"

    # ============================================================
    # 表级约束
    # ============================================================

    __table_args__ = (
        Index("ix_logs_user_id", "user_id"),
        Index("ix_logs_action", "action"),
        Index("ix_logs_created_at", "created_at"),
    )

    # ============================================================
    # 业务字段
    # ============================================================

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="操作人 ID",
    )

    action: Mapped[ActionType] = mapped_column(
        SAEnum(ActionType),
        nullable=False,
        comment="操作类型（create/update/delete/status_change）",
    )

    target_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="操作对象类型",
    )

    target_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        comment="操作对象 ID",
    )

    changes: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=None,
        comment="变更内容（JSON）",
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=None,
        comment="IP 地址",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="system_logs",
        lazy="selectin",
    )

    # ============================================================
    # 特殊方法
    # ============================================================

    def __repr__(self) -> str:
        log_id = self.id if self.id is not None else "?"
        return (
            f"<SystemLog(id={log_id}, user_id={self.user_id}, "
            f"action={self.action}, target_type='{self.target_type}')>"
        )