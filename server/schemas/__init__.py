"""
server.schemas 包

Sprint 3 — Task 3.1 / Sprint 4 — Task 4.1 / Sprint 5 — Task 5.1
GTMS Pydantic Schema 层，用于 API 请求/响应序列化。

包含:
    - user_schema:          用户相关 Schema（LoginRequest, UserCreate, UserResponse 等）
    - role_schema:           角色相关 Schema（RoleResponse, PermissionResponse 等）
    - customer_schema:       客户相关 Schema（CustomerCreate, CustomerResponse 等）
    - trial_task_schema:     试磨任务相关 Schema（TrialTaskCreate, TrialTaskResponse 等）
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
from server.schemas.customer_schema import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
)
from server.schemas.trial_task_schema import (
    TrialTaskBase,
    TrialTaskCreate,
    TrialTaskUpdate,
    TrialTaskResponse,
    TrialTaskListResponse,
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
    # Customer
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerListResponse",
    # TrialTask
    "TrialTaskBase",
    "TrialTaskCreate",
    "TrialTaskUpdate",
    "TrialTaskResponse",
    "TrialTaskListResponse",
]