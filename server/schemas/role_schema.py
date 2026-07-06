"""角色 Schema (Role Schema)

Sprint 3 — Task 3.1
严格依据 Sprint 1 Role/Permission ORM 模型、CODE_WIKI.md。

角色来源：ROLE_PERMISSION_MAP（security.py）。
Schema 仅作为 API Response，不用于创建/更新角色。
使用 Pydantic v2 ConfigDict(from_attributes=True)。

Schema 列表:
    - RoleResponse:       角色响应
    - RoleListResponse:   角色列表响应
    - PermissionResponse: 权限响应
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# 权限响应
# ============================================================


class PermissionResponse(BaseModel):
    """权限响应 Schema。

    基于 Sprint 1 Permission ORM 模型。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        code: 权限编码（如 "task:write"）。
        name: 权限名称。
        description: 权限描述。
        module: 所属模块。
    """

    model_config = ConfigDict(from_attributes=True)

    code: str = Field(..., description="权限编码（如 task:write）")
    name: str = Field(..., description="权限名称")
    description: Optional[str] = Field(default=None, description="权限描述")
    module: str = Field(..., description="所属模块")


# ============================================================
# 角色响应
# ============================================================


class RoleResponse(BaseModel):
    """角色响应 Schema。

    基于 Sprint 1 Role ORM 模型。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        id: 角色 ID。
        name: 角色标识（如 "administrator"）。
        display_name: 角色显示名。
        description: 角色描述。
        is_system: 是否系统内置角色。
        created_at: 创建时间。
        permissions: 关联权限列表。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="角色 ID")
    name: str = Field(..., description="角色标识")
    display_name: str = Field(..., description="角色显示名")
    description: Optional[str] = Field(default=None, description="角色描述")
    is_system: bool = Field(default=False, description="是否系统内置角色")
    created_at: datetime = Field(..., description="创建时间")
    permissions: list[PermissionResponse] = Field(
        default_factory=list,
        description="关联权限列表",
    )


# ============================================================
# 角色列表响应
# ============================================================


class RoleListResponse(BaseModel):
    """角色列表响应 Schema。

    Attributes:
        items: 角色列表。
        total: 总数。
    """

    items: list[RoleResponse] = Field(
        default_factory=list,
        description="角色列表",
    )
    total: int = Field(..., description="总数")


__all__ = [
    "RoleResponse",
    "RoleListResponse",
    "PermissionResponse",
]