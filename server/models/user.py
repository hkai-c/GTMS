"""
用户模型 (User)

对应 DB_DESIGN.md §4.1。
支持 RBAC：用户通过 user_roles 关联表与角色多对多关联。

字段（严格对照 DB_DESIGN.md）：
    - id:            主键
    - username:      登录用户名（唯一）
    - password_hash: bcrypt 密码哈希
    - real_name:     真实姓名
    - phone:         联系电话
    - is_active:     启用状态

关联表（SQLAlchemy Table 对象）：
    - user_roles:      用户 ↔ 角色 多对多
    - role_permissions: 角色 ↔ 权限 多对多

使用方式:
    from server.models import User
    user = User(username="admin", real_name="系统管理员")
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    Table,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database.base import Base
from server.models.base_model import BaseModel

if TYPE_CHECKING:
    from server.models.role import Role

# ============================================================
# 关联表定义（SQLAlchemy Table 对象，非 ORM 模型）
# ============================================================

# 用户-角色关联表
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="用户 ID",
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        comment="角色 ID",
    ),
    # 索引
    Index("ix_user_roles_role_id", "role_id"),
)

# 角色-权限关联表
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        comment="角色 ID",
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
        comment="权限 ID",
    ),
    # 索引
    Index("ix_role_permissions_permission_id", "permission_id"),
)


class User(BaseModel):
    """用户模型"""

    __tablename__ = "users"

    # ============================================================
    # 业务字段
    # ============================================================

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="登录用户名",
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt 密码哈希",
    )

    real_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="真实姓名",
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default=None,
        comment="联系电话",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="启用状态",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    # 用户 ↔ 角色（多对多，通过 user_roles 表）
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"