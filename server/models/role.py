"""
角色模型 (Role)

对应 DB_DESIGN.md §4.2a。
一个角色对应一组权限（角色 → 权限 多对多）。
一个用户可拥有多个角色（用户 → 角色 多对多）。

字段（严格对照 DB_DESIGN.md）：
    - id:           主键
    - name:         角色标识（唯一，如 admin/sales/technician/leader）
    - display_name: 角色显示名
    - description:  角色描述
    - is_system:    是否系统内置角色（不可删除）

使用方式:
    from server.models import Role
    role = Role(name="admin", display_name="管理员")
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.permission import Permission


class Role(BaseModel):
    """角色模型"""

    __tablename__ = "roles"

    # ============================================================
    # 业务字段
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="角色标识（唯一）",
    )

    display_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="角色显示名",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="角色描述",
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否系统内置角色（不可删除）",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    # 角色 ↔ 用户（多对多，通过 user_roles 表）
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",
    )

    # 角色 ↔ 权限（多对多，通过 role_permissions 表）
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"