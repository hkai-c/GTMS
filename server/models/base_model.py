"""
ORM 抽象基类 BaseModel

所有业务模型必须继承此类以自动获得公共字段。
继承链: BaseModel → Base (server.database.base.Base)

公共字段（严格对照 DB_DESIGN.md）：
    - id:            主键，自增整数
    - created_at:    创建时间 (UTC)
    - updated_at:    更新时间 (UTC)
    - created_by:    创建人 ID
    - updated_by:    更新人 ID
    - is_deleted:    软删除标记

使用方式:
    from server.models import BaseModel

    class User(BaseModel):
        __tablename__ = "users"
        username: Mapped[str] = mapped_column(...)
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from server.database.base import Base


class BaseModel(Base):
    """ORM 抽象基类

    所有业务模型继承此类，自动获得：
    - 主键 id
    - 时间戳 created_at / updated_at
    - 审计字段 created_by / updated_by
    - 软删除标记 is_deleted

    注意：此类为抽象类，不会在数据库中创建对应的表。
    """

    __abstract__ = True

    # ============================================================
    # 主键
    # ============================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键 ID",
    )

    # ============================================================
    # 时间戳
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="创建时间 (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="更新时间 (UTC)",
    )

    # ============================================================
    # 审计字段
    # ============================================================

    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        comment="创建人 ID",
    )

    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        comment="更新人 ID",
    )

    # ============================================================
    # 软删除
    # ============================================================

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="软删除标记 (True=已删除)",
    )