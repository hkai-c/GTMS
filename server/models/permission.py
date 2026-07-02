"""
权限模型 (Permission)

对应 DB_DESIGN.md §4.2b。
权限由代码定义，管理员只能查看和分配，不能增删改。

字段（严格对照 DB_DESIGN.md）：
    - id:          主键
    - code:        权限编码（唯一，如 task:create）
    - name:        权限名称
    - description: 权限描述
    - module:      所属模块

使用方式:
    from server.models import Permission
    perm = Permission(code="task:create", name="创建任务", module="task")
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel

if TYPE_CHECKING:
    from server.models.role import Role


class Permission(BaseModel):
    """权限模型"""

    __tablename__ = "permissions"

    # ============================================================
    # 业务字段
    # ============================================================

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="权限编码（唯一，如 task:create）",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="权限名称",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="权限描述",
    )

    module: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="所属模块",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    # 权限 ↔ 角色（多对多，通过 role_permissions 表）
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code='{self.code}')>"