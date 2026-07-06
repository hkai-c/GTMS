"""角色管理路由 (Role Router)

Sprint 3 — Task 3.6
严格依据 SRS §4.1、CODE_WIKI、Sprint 2 Frozen API、Sprint 3 Schema。

提供角色与权限查询接口（只读）：
    - GET /api/roles                      — 角色列表
    - GET /api/roles/{role_id}            — 角色详情
    - GET /api/roles/{role_id}/permissions — 角色权限

本 Sprint 仅实现只读查询，不实现创建/修改/删除角色。
数据来源：Sprint 1 ORM（Role / Permission 模型）+ ROLE_PERMISSION_MAP。
不新增 RoleService。
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.core.dependencies import get_current_active_user, get_db
from server.core.exceptions import NotFoundException
from server.models.permission import Permission
from server.models.role import Role
from server.models.user import User
from server.schemas.role_schema import (
    PermissionResponse,
    RoleListResponse,
    RoleResponse,
)

# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/roles",
    tags=["Roles"],
)


# ============================================================
# GET /api/roles — 角色列表
# ============================================================


@router.get(
    "",
    response_model=RoleListResponse,
    status_code=status.HTTP_200_OK,
    summary="角色列表",
    description="查询所有角色及其关联权限。",
)
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RoleListResponse:
    """角色列表接口。

    查询所有未删除的角色，包含关联的权限列表。

    Args:
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        RoleListResponse: 角色列表与总数。
    """
    roles = (
        db.query(Role)
        .filter(Role.is_deleted == False)
        .order_by(Role.id)
        .all()
    )
    return RoleListResponse(
        items=roles,
        total=len(roles),
    )


# ============================================================
# GET /api/roles/{role_id} — 角色详情
# ============================================================


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    summary="角色详情",
    description="根据角色 ID 查询角色详情。",
)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RoleResponse:
    """角色详情接口。

    查询指定角色及其关联权限。

    Args:
        role_id: 角色 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        RoleResponse: 角色详情（含权限列表）。

    Raises:
        NotFoundException: 角色不存在或已删除（由全局异常处理器处理）。
    """
    role = (
        db.query(Role)
        .filter(Role.id == role_id, Role.is_deleted == False)
        .first()
    )
    if role is None:
        raise NotFoundException(
            "角色不存在",
            detail={"role_id": role_id},
        )
    return role


# ============================================================
# GET /api/roles/{role_id}/permissions — 角色权限列表
# ============================================================


@router.get(
    "/{role_id}/permissions",
    response_model=list[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="角色权限列表",
    description="查询指定角色的所有权限。",
)
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[PermissionResponse]:
    """角色权限列表接口。

    查询指定角色的所有关联权限。

    Args:
        role_id: 角色 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        list[PermissionResponse]: 权限列表。

    Raises:
        NotFoundException: 角色不存在或已删除（由全局异常处理器处理）。
    """
    role = (
        db.query(Role)
        .filter(Role.id == role_id, Role.is_deleted == False)
        .first()
    )
    if role is None:
        raise NotFoundException(
            "角色不存在",
            detail={"role_id": role_id},
        )
    return role.permissions


__all__ = [
    "router",
]