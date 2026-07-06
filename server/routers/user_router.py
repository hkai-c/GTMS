"""用户管理路由 (User Router)

Sprint 3 — Task 3.5
严格依据 SRS §4.1、CODE_WIKI、Sprint 2 Frozen API、Sprint 3 Schema/UserService。

提供用户管理 HTTP 接口：
    - GET    /api/users              — 用户列表（分页+筛选）
    - GET    /api/users/{user_id}    — 用户详情
    - POST   /api/users              — 创建用户
    - PUT    /api/users/{user_id}    — 更新用户
    - DELETE /api/users/{user_id}    — 删除用户
    - POST   /api/users/{user_id}/roles — 分配角色

Router 不实现任何业务逻辑，所有能力委托给 UserService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from server.core.dependencies import get_current_active_user, get_db
from server.models.user import User
from server.schemas.user_schema import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from server.services.user_service import UserService

# ============================================================
# 本地 Schema（仅用于 Router 层，不修改 server/schemas/）
# ============================================================


class UserCreateRequest(UserCreate):
    """创建用户请求体（扩展 UserCreate，增加 role_ids）。

    继承 UserCreate 的全部字段，额外增加 role_ids 可选字段。
    定义在 Router 层，不修改 server/schemas/。
    """

    role_ids: Optional[list[int]] = Field(
        default=None,
        description="角色 ID 列表（可选，不传则不分配角色）",
    )


class UserUpdateRequest(UserUpdate):
    """更新用户请求体（扩展 UserUpdate，增加 role_ids）。

    继承 UserUpdate 的全部字段，额外增加 role_ids 可选字段。
    """

    role_ids: Optional[list[int]] = Field(
        default=None,
        description="新角色 ID 列表（可选，传入时覆盖原有关联）",
    )


class RoleAssignRequest(BaseModel):
    """角色分配请求体。

    用于 POST /api/users/{user_id}/roles 接口。

    Attributes:
        role_ids: 角色 ID 列表。
    """

    role_ids: list[int] = Field(
        ...,
        min_length=1,
        description="角色 ID 列表（至少一个）",
    )


# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)

# ============================================================
# 服务实例
# ============================================================

_user_service = UserService()


# ============================================================
# GET /api/users — 用户列表
# ============================================================


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="用户列表",
    description="分页查询用户列表，支持 username/real_name/is_active/role 筛选。",
)
def list_users(
    page: int = Query(default=1, ge=1, description="页码（从 1 开始）"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    username: Optional[str] = Query(default=None, description="用户名（模糊查询）"),
    real_name: Optional[str] = Query(default=None, description="真实姓名（模糊查询）"),
    is_active: Optional[bool] = Query(default=None, description="启用状态筛选"),
    role: Optional[str] = Query(default=None, description="角色名筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserListResponse:
    """用户列表接口。

    调用 UserService.list_users() 查询用户列表。

    Args:
        page: 页码。
        page_size: 每页条数。
        username: 用户名模糊查询（可选）。
        real_name: 真实姓名模糊查询（可选）。
        is_active: 启用状态筛选（可选）。
        role: 角色名筛选（可选）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        UserListResponse: 分页用户列表。
    """
    items, total = _user_service.list_users(
        db,
        page=page,
        page_size=page_size,
        username=username,
        real_name=real_name,
        is_active=is_active,
        role=role,
    )
    return UserListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET /api/users/{user_id} — 用户详情
# ============================================================


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="用户详情",
    description="根据用户 ID 查询用户详情。",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """用户详情接口。

    调用 UserService.get_user() 查询用户。

    Args:
        user_id: 用户 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        UserResponse: 用户详情。

    Raises:
        NotFoundException: 用户不存在（由全局异常处理器处理）。
    """
    return _user_service.get_user(db, user_id=user_id)


# ============================================================
# POST /api/users — 创建用户
# ============================================================


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户（仅管理员可操作）。",
)
def create_user(
    request: UserCreateRequest = Body(..., description="用户创建数据（含可选角色）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """创建用户接口。

    调用 UserService.create_user() 完成创建流程：
        ① 检查权限（仅 Administrator）
        ② 检查 username 唯一性
        ③ 校验角色
        ④ 哈希密码
        ⑤ 创建 User
        ⑥ 分配角色
        ⑦ 写入 SystemLog

    Args:
        request: 用户创建请求体（UserCreateRequest）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        UserResponse: 创建的用户信息（不含 password_hash）。

    Raises:
        PermissionDeniedException: 非管理员（由全局异常处理器处理）。
        DuplicateException: username 重复（由全局异常处理器处理）。
        BusinessLogicException: 角色不存在（由全局异常处理器处理）。
    """
    return _user_service.create_user(
        db,
        user_data=request,
        current_user=current_user,
        role_ids=request.role_ids,
    )


# ============================================================
# PUT /api/users/{user_id} — 更新用户
# ============================================================


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="更新用户",
    description="更新用户信息（仅管理员可操作）。禁止修改 username 和 password。",
)
def update_user(
    user_id: int,
    request: UserUpdateRequest = Body(..., description="用户更新数据（含可选角色）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """更新用户接口。

    调用 UserService.update_user() 完成更新流程。

    允许修改: real_name, phone, is_active, roles。
    禁止修改: username, password_hash, created_at, created_by。

    Args:
        user_id: 目标用户 ID。
        user_data: 更新数据（UserUpdate Schema）。
        role_ids: 新角色 ID 列表（可选）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        UserResponse: 更新后的用户信息。

    Raises:
        PermissionDeniedException: 非管理员（由全局异常处理器处理）。
        NotFoundException: 用户不存在（由全局异常处理器处理）。
        BusinessLogicException: 角色不存在（由全局异常处理器处理）。
    """
    return _user_service.update_user(
        db,
        user_id=user_id,
        user_data=request,
        current_user=current_user,
        role_ids=request.role_ids,
    )


# ============================================================
# DELETE /api/users/{user_id} — 删除用户
# ============================================================


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="删除用户",
    description="软删除用户（仅管理员可操作，管理员不能删除自己）。",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """删除用户接口。

    调用 UserService.delete_user() 完成软删除。

    Args:
        user_id: 目标用户 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        dict: {"message": "User deleted successfully."}

    Raises:
        PermissionDeniedException: 非管理员（由全局异常处理器处理）。
        BusinessLogicException: 管理员不能删除自己（由全局异常处理器处理）。
        NotFoundException: 用户不存在（由全局异常处理器处理）。
    """
    _user_service.delete_user(db, user_id=user_id, current_user=current_user)
    return {"message": "User deleted successfully."}


# ============================================================
# POST /api/users/{user_id}/roles — 分配角色
# ============================================================


@router.post(
    "/{user_id}/roles",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="分配角色",
    description="重新分配用户角色（覆盖原有关联，仅管理员可操作）。",
)
def assign_roles(
    user_id: int,
    request: RoleAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """分配角色接口。

    调用 UserService.assign_roles() 覆盖用户角色。

    Args:
        user_id: 目标用户 ID。
        request: 角色分配请求体（role_ids）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        UserResponse: 更新后的用户信息。

    Raises:
        PermissionDeniedException: 非管理员（由全局异常处理器处理）。
        NotFoundException: 用户不存在（由全局异常处理器处理）。
        BusinessLogicException: 角色不存在（由全局异常处理器处理）。
    """
    return _user_service.assign_roles(
        db,
        user_id=user_id,
        role_ids=request.role_ids,
        current_user=current_user,
    )


__all__ = [
    "router",
]