"""收件记录路由 (Receipt Router)

Sprint 6 — Task 6.3
依据 SRS §4.4、Receipt Schema (Task 6.1)、Receipt Service (Task 6.2)、Sprint 2~6 Frozen API。

提供收件记录 HTTP 接口：
    - GET    /api/receipts                  — 收件记录列表（分页+筛选）
    - GET    /api/receipts/{receipt_id}      — 收件记录详情
    - POST   /api/receipts                  — 创建收件记录（状态推进 CREATED→RECEIVED）
    - PUT    /api/receipts/{receipt_id}      — 修改收件记录
    - DELETE /api/receipts/{receipt_id}      — 删除收件记录（软删除）

Router 不实现任何业务逻辑，所有能力委托给 ReceiptService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
Router 不使用 ORM、JWT、bcrypt、事务、SystemLog、HTTPException。
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
from server.schemas.receipt_schema import (
    ReceiptCreate,
    ReceiptUpdate,
    ReceiptResponse,
    ReceiptListResponse,
)
from server.services.receipt_service import ReceiptService

# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/receipts",
    tags=["Receipt"],
)

# ============================================================
# 服务实例
# ============================================================

_receipt_service = ReceiptService()


# ============================================================
# GET /api/receipts — 收件记录列表
# ============================================================


@router.get(
    "",
    response_model=ReceiptListResponse,
    status_code=status.HTTP_200_OK,
    summary="收件记录列表",
    description="分页查询收件记录列表，支持按 task_id 筛选。",
)
def list_receipts(
    task_id: Optional[int] = Query(
        default=None,
        description="关联试磨任务 ID",
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
    _: None = Depends(require_permission("receipt:view")),
) -> ReceiptListResponse:
    """收件记录列表接口。

    调用 ReceiptService.list_receipts() 查询收件记录列表。

    Args:
        task_id: 关联试磨任务 ID（可选）。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（receipt:view）。

    Returns:
        ReceiptListResponse: 分页收件记录列表。
    """
    return _receipt_service.list_receipts(
        db,
        task_id=task_id,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET /api/receipts/{receipt_id} — 收件记录详情
# ============================================================


@router.get(
    "/{receipt_id}",
    response_model=ReceiptResponse,
    status_code=status.HTTP_200_OK,
    summary="收件记录详情",
    description="根据收件记录 ID 查询收件记录详情。",
)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("receipt:view")),
) -> ReceiptResponse:
    """收件记录详情接口。

    调用 ReceiptService.get_receipt() 查询收件记录。

    Args:
        receipt_id: 收件记录 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（receipt:view）。

    Returns:
        ReceiptResponse: 收件记录详情。

    Raises:
        NotFoundException: 收件记录不存在（由全局异常处理器处理）。
    """
    return _receipt_service.get_receipt(db, receipt_id)


# ============================================================
# POST /api/receipts — 创建收件记录
# ============================================================


@router.post(
    "",
    response_model=ReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建收件记录",
    description="创建收件记录。校验 TrialTask 存在且状态为 CREATED，推进 process_status 至 RECEIVED。",
)
def create_receipt(
    data: ReceiptCreate = Body(..., description="收件记录创建数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("receipt:create")),
) -> ReceiptResponse:
    """创建收件记录接口。

    调用 ReceiptService.create_receipt() 完成创建流程：
        ① 校验 TrialTask 存在且状态为 CREATED
        ② 校验 receiver_id 存在
        ③ 校验 task_id 未重复收件
        ④ 创建 Receipt ORM
        ⑤ 推进 TrialTask.process_status → RECEIVED
        ⑥ 写入 SystemLog

    Args:
        data: 收件记录创建数据（ReceiptCreate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（receipt:create）。

    Returns:
        ReceiptResponse: 新创建的收件记录。

    Raises:
        NotFoundException: 试磨任务或收件人不存在（由全局异常处理器处理）。
        BusinessLogicException: 任务状态非 CREATED 或已收件（由全局异常处理器处理）。
    """
    return _receipt_service.create_receipt(
        db,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# PUT /api/receipts/{receipt_id} — 修改收件记录
# ============================================================


@router.put(
    "/{receipt_id}",
    response_model=ReceiptResponse,
    status_code=status.HTTP_200_OK,
    summary="修改收件记录",
    description="修改收件记录。仅更新传入的非 None 字段。",
)
def update_receipt(
    receipt_id: int,
    data: ReceiptUpdate = Body(..., description="收件记录更新数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("receipt:edit")),
) -> ReceiptResponse:
    """修改收件记录接口。

    调用 ReceiptService.update_receipt() 完成更新流程：
        ① 查询收件记录
        ② 仅更新传入字段（exclude_unset）
        ③ 写入 SystemLog

    Args:
        receipt_id: 目标收件记录 ID。
        data: 更新数据（ReceiptUpdate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（receipt:edit）。

    Returns:
        ReceiptResponse: 更新后的收件记录。

    Raises:
        NotFoundException: 收件记录不存在（由全局异常处理器处理）。
    """
    return _receipt_service.update_receipt(
        db,
        receipt_id=receipt_id,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# DELETE /api/receipts/{receipt_id} — 删除收件记录
# ============================================================


@router.delete(
    "/{receipt_id}",
    status_code=status.HTTP_200_OK,
    summary="删除收件记录",
    description="软删除收件记录（设置 is_deleted=True）。",
)
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("receipt:delete")),
) -> dict:
    """删除收件记录接口。

    调用 ReceiptService.delete_receipt() 完成软删除。

    Args:
        receipt_id: 目标收件记录 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（receipt:delete）。

    Returns:
        dict: {"message": "收件记录已删除"}。

    Raises:
        NotFoundException: 收件记录不存在（由全局异常处理器处理）。
    """
    _receipt_service.delete_receipt(
        db,
        receipt_id=receipt_id,
        operator_id=current_user.id,
    )
    return {"message": "收件记录已删除"}


__all__ = [
    "router",
]
