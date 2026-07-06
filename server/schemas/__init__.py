"""
server.schemas 包

Sprint 3 — Task 3.1
GTMS Pydantic Schema 层，用于 API 请求/响应序列化。

包含:
    - user_schema:  用户相关 Schema（LoginRequest, UserCreate, UserResponse 等）
    - role_schema:   角色相关 Schema（RoleResponse, PermissionResponse 等）
"""

from server.schemas.user_schema import (
    LoginRequest,
    LoginResponse,
    UserBase,
    UserCreate,
    UserUpdate,
    UserPasswordChange,
    UserResponse,
    UserListResponse,
)
from server.schemas.role_schema import (
    RoleResponse,
    RoleListResponse,
    PermissionResponse,
)

__all__ = [
    # User
    "LoginRequest",
    "LoginResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPasswordChange",
    "UserResponse",
    "UserListResponse",
    # Role
    "RoleResponse",
    "RoleListResponse",
    "PermissionResponse",
]