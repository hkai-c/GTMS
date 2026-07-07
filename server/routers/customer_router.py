"""客户管理路由 (Customer Router)

Sprint 4 — Task 4.3
严格依据 SRS §4.2、CODE_WIKI、Sprint 2 Frozen API、Sprint 4 Task 4.1/4.2。

提供客户管理 HTTP 接口：
    - GET    /api/customers                — 客户列表（分页+搜索）
    - GET    /api/customers/{customer_id}  — 客户详情
    - POST   /api/customers                — 创建客户
    - PUT    /api/customers/{customer_id}  — 修改客户

注意：Customer 永久保留，不提供 DELETE 接口。

Router 不实现任何业务逻辑，所有能力委托给 CustomerService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from server.core.dependencies import (
    get_current_active_user,
    get_db,
    require_permission,
)
from server.models.user import User
from server.schemas.customer_schema import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from server.services.customer_service import CustomerService

# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/customers",
    tags=["Customer"],
)

# ============================================================
# 服务实例
# ============================================================

_customer_service = CustomerService()


# ============================================================
# GET /api/customers — 客户列表
# ============================================================


@router.get(
    "",
    response_model=CustomerListResponse,
    status_code=status.HTTP_200_OK,
    summary="客户列表",
    description="分页查询客户列表，支持按公司名称模糊搜索。",
)
def list_customers(
    company_name: Optional[str] = Query(
        default=None,
        description="公司名称（模糊搜索）",
    ),
    page: int = Query(default=1, ge=1, description="页码（从 1 开始）"),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="每页条数",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("customer:view")),
) -> CustomerListResponse:
    """客户列表接口。

    调用 CustomerService.list_customers() 查询客户列表。

    Args:
        company_name: 公司名称模糊搜索（可选）。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（customer:view）。

    Returns:
        CustomerListResponse: 分页客户列表。
    """
    return _customer_service.list_customers(
        db,
        company_name=company_name,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET /api/customers/{customer_id} — 客户详情
# ============================================================


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="客户详情",
    description="根据客户 ID 查询客户详情。",
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("customer:view")),
) -> CustomerResponse:
    """客户详情接口。

    调用 CustomerService.get_customer() 查询客户。

    Args:
        customer_id: 客户 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（customer:view）。

    Returns:
        CustomerResponse: 客户详情。

    Raises:
        NotFoundException: 客户不存在（由全局异常处理器处理）。
    """
    return _customer_service.get_customer(db, customer_id)


# ============================================================
# POST /api/customers — 创建客户
# ============================================================


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建客户",
    description="创建新客户。company_name 全库唯一，自动去除首尾空格。",
)
def create_customer(
    data: CustomerCreate = Body(..., description="客户创建数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("customer:create")),
) -> CustomerResponse:
    """创建客户接口。

    调用 CustomerService.create_customer() 完成创建流程：
        ① 自动 strip company_name
        ② 检查 company_name 唯一性
        ③ 创建 Customer ORM
        ④ 写入 SystemLog

    Args:
        data: 客户创建数据（CustomerCreate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（customer:create）。

    Returns:
        CustomerResponse: 新创建的客户。

    Raises:
        BusinessLogicException: company_name 已存在（由全局异常处理器处理）。
    """
    return _customer_service.create_customer(
        db,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# PUT /api/customers/{customer_id} — 修改客户
# ============================================================


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="修改客户",
    description="修改客户信息。仅更新传入的非 None 字段。",
)
def update_customer(
    customer_id: int,
    data: CustomerUpdate = Body(..., description="客户更新数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("customer:edit")),
) -> CustomerResponse:
    """修改客户接口。

    调用 CustomerService.update_customer() 完成更新流程：
        ① 查询客户
        ② 仅更新传入字段（exclude_unset）
        ③ 修改 company_name 时自动 strip 并检查唯一性
        ④ 写入 SystemLog

    Args:
        customer_id: 目标客户 ID。
        data: 更新数据（CustomerUpdate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（customer:edit）。

    Returns:
        CustomerResponse: 更新后的客户。

    Raises:
        NotFoundException: 客户不存在（由全局异常处理器处理）。
        BusinessLogicException: company_name 与其它客户重复（由全局异常处理器处理）。
    """
    return _customer_service.update_customer(
        db,
        customer_id=customer_id,
        data=data,
        operator_id=current_user.id,
    )


__all__ = [
    "router",
]