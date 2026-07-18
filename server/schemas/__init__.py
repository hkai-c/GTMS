"""
server.schemas 包

Sprint 3 — Task 3.1 / Sprint 4 — Task 4.1 / Sprint 5 — Task 5.1 / Sprint 6 — Task 6.1 / Sprint 7 — Task 7.1 / Sprint 8 — Task 8.1 / Sprint 9 — Task 9.1 / Sprint 10 — Task 10.1 / Sprint 11 — Task 11.1
GTMS Pydantic Schema 层，用于 API 请求/响应序列化。

包含:
    - user_schema:          用户相关 Schema（LoginRequest, UserCreate, UserResponse 等）
    - role_schema:           角色相关 Schema（RoleResponse, PermissionResponse 等）
    - customer_schema:       客户相关 Schema（CustomerCreate, CustomerResponse 等）
    - trial_task_schema:     试磨任务相关 Schema（TrialTaskCreate, TrialTaskResponse 等）
    - receipt_schema:        收件记录相关 Schema（ReceiptCreate, ReceiptResponse 等）
    - grinding_schema:       试磨记录相关 Schema（GrindingCreate, GrindingResponse 等）
    - inspection_schema:     检测记录相关 Schema（InspectionCreate, InspectionResponse 等）
    - dispatch_schema:       工件派发相关 Schema（DispatchCreate, DispatchResponse 等）
    - query_schema:          查询统计相关 Schema（QueryFilter, StatisticsResponse 等）
    - log_schema:            操作日志相关 Schema（LogBase, LogResponse 等）
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
from server.schemas.receipt_schema import (
    ReceiptBase,
    ReceiptCreate,
    ReceiptUpdate,
    ReceiptResponse,
    ReceiptListResponse,
)
from server.schemas.trial_task_schema import (
    TrialTaskBase,
    TrialTaskCreate,
    TrialTaskUpdate,
    TrialTaskResponse,
    TrialTaskListResponse,
)
from server.schemas.inspection_schema import (
    InspectionBase,
    InspectionCreate,
    InspectionUpdate,
    InspectionResponse,
    InspectionListResponse,
    InspectionQuery,
    InspectionFinishRequest,
    InspectionReport,
)
from server.schemas.dispatch_schema import (
    DispatchBase,
    DispatchCreate,
    DispatchUpdate,
    DispatchResponse,
    DispatchListResponse,
    DispatchQuery,
)
from server.schemas.query_schema import (
    QueryFilter,
    StatisticsSummary,
    RankingItem,
    StatisticsResponse,
    ExportRequest,
    QueryResponse,
)
from server.schemas.log_schema import (
    LogBase,
    LogResponse,
    LogListResponse,
    LogQuery,
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
    # Receipt
    "ReceiptBase",
    "ReceiptCreate",
    "ReceiptUpdate",
    "ReceiptResponse",
    "ReceiptListResponse",
    # TrialTask
    "TrialTaskBase",
    "TrialTaskCreate",
    "TrialTaskUpdate",
    "TrialTaskResponse",
    "TrialTaskListResponse",
    # Inspection
    "InspectionBase",
    "InspectionCreate",
    "InspectionUpdate",
    "InspectionResponse",
    "InspectionListResponse",
    "InspectionQuery",
    "InspectionFinishRequest",
    "InspectionReport",
    # Dispatch
    "DispatchBase",
    "DispatchCreate",
    "DispatchUpdate",
    "DispatchResponse",
    "DispatchListResponse",
    "DispatchQuery",
    # Query
    "QueryFilter",
    "StatisticsSummary",
    "RankingItem",
    "StatisticsResponse",
    "ExportRequest",
    "QueryResponse",
    # Log
    "LogBase",
    "LogResponse",
    "LogListResponse",
    "LogQuery",
]