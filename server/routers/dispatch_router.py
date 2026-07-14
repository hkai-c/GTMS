"""工件派发路由 (Dispatch Router)

Sprint 9 — Task 9.3
依据 SRS §4.7、Dispatch Schema (Task 9.1)、Dispatch Service (Task 9.2)、
    Sprint 1~9 Frozen API。

提供工件派发 HTTP 接口：
    - GET    /api/dispatch              — 派发记录列表（分页+筛选）
    - GET    /api/dispatch/{dispatch_id} — 派发记录详情
    - POST   /api/dispatch              — 创建派发记录
    - PUT    /api/dispatch/{dispatch_id} — 修改派发记录
    - DELETE /api/dispatch/{dispatch_id} — 删除派发记录（软删除）

Router 不实现任何业务逻辑，所有能力委托给 DispatchService。
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
from server.enums import DestinationType
from server.models.user import User
from server.schemas.dispatch_schema import (
    DispatchCreate,
    DispatchUpdate,
    DispatchResponse,
    DispatchListResponse,
)
from server.services.dispatch_service import DispatchService


# ============================================================
# Router 定义
# ============================================================


router = APIRouter(
    prefix="/api/dispatch",
    tags=["Dispatch"],
)

# ============================================================
# 服务实例
# ============================================================

_dispatch_service = DispatchService()

# ============================================================
# GET /api/dispatch — 派发记录列表
# ============================================================


@router.get(
    "",
    response_model=DispatchListResponse,
    status_code=status.HTTP_200_OK,
    summary="派发记录列表",
    description="分页查询派发记录列表，支持按 direction、task_id 筛选。",
)
def list_dispatches(
    direction: Optional[DestinationType] = Query(
        default=None,
        description="去向方向筛选",
    ),
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
    _: None = Depends(require_permission("dispatch:view")),
) -> DispatchListResponse:
    """派发记录列表接口。

    调用 DispatchService.list_dispatches() 查询派发记录列表。

    Args:
        direction: 去向方向筛选（可选）。
        task_id: 关联试磨任务 ID（可选）。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（dispatch:view）。

    Returns:
        DispatchListResponse: 分页派发记录列表。
    """
    return _dispatch_service.list_dispatches(
        db,
        direction=direction,
        task_id=task_id,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET /api/dispatch/{dispatch_id} — 派发记录详情
# ============================================================


@router.get(
    "/{dispatch_id}",
    response_model=DispatchResponse,
    status_code=status.HTTP_200_OK,
    summary="派发记录详情",
    description="根据派发记录 ID 查询派发记录详情。",
)
def get_dispatch(
    dispatch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("dispatch:view")),
) -> DispatchResponse:
    """派发记录详情接口。

    调用 DispatchService.get_dispatch() 查询派发记录。

    Args:
        dispatch_id: 派发记录 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（dispatch:view）。

    Returns:
        DispatchResponse: 派发记录详情。

    Raises:
        NotFoundException: 派发记录不存在（由全局异常处理器处理）。
    """
    return _dispatch_service.get_dispatch(db, dispatch_id)


# ============================================================
# POST /api/dispatch — 创建派发记录
# ============================================================


@router.post(
    "",
    response_model=DispatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建派发记录",
    description=(
        "创建派发记录。校验 TrialTask 存在且检测合格、"
        "InspectionRecord 存在、process_status 为 GRINDING，"
        "创建成功后推进 process_status → DISPATCHED。"
    ),
)
def create_dispatch(
    data: DispatchCreate = Body(..., description="派发创建数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("dispatch:create")),
) -> DispatchResponse:
    """创建派发记录接口。

    调用 DispatchService.create_dispatch() 完成创建流程：
        ① 校验 TrialTask 存在
        ② 校验 InspectionRecord 存在
        ③ 校验 Dispatch 不重复
        ④ 校验 result_status == PASSED
        ⑤ 校验 process_status == GRINDING
        ⑥ 创建 DispatchRecord
        ⑦ 推进 process_status → DISPATCHED
        ⑧ 写入 SystemLog

    Args:
        data: 派发创建数据（DispatchCreate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（dispatch:create）。

    Returns:
        DispatchResponse: 新创建的派发记录。

    Raises:
        NotFoundException: 试磨任务或检测记录不存在（由全局异常处理器处理）。
        BusinessLogicException: 状态不符合条件（由全局异常处理器处理）。
    """
    return _dispatch_service.create_dispatch(
        db,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# PUT /api/dispatch/{dispatch_id} — 修改派发记录
# ============================================================


@router.put(
    "/{dispatch_id}",
    response_model=DispatchResponse,
    status_code=status.HTTP_200_OK,
    summary="修改派发记录",
    description="修改派发记录。仅更新传入的非 None 字段。",
)
def update_dispatch(
    dispatch_id: int,
    data: DispatchUpdate = Body(..., description="派发记录更新数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("dispatch:edit")),
) -> DispatchResponse:
    """修改派发记录接口。

    调用 DispatchService.update_dispatch() 完成更新流程：
        ① 查询派发记录
        ② 仅更新传入字段（exclude_unset）
        ③ 写入 SystemLog

    Args:
        dispatch_id: 目标派发记录 ID。
        data: 更新数据（DispatchUpdate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（dispatch:edit）。

    Returns:
        DispatchResponse: 更新后的派发记录。

    Raises:
        NotFoundException: 派发记录不存在（由全局异常处理器处理）。
    """
    return _dispatch_service.update_dispatch(
        db,
        dispatch_id=dispatch_id,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# DELETE /api/dispatch/{dispatch_id} — 删除派发记录
# ============================================================


@router.delete(
    "/{dispatch_id}",
    status_code=status.HTTP_200_OK,
    summary="删除派发记录",
    description="软删除派发记录（设置 is_deleted=True）。",
)
def delete_dispatch(
    dispatch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("dispatch:delete")),
) -> dict:
    """删除派发记录接口。

    调用 DispatchService.delete_dispatch() 完成软删除。

    Args:
        dispatch_id: 目标派发记录 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（dispatch:delete）。

    Returns:
        dict: {"message": "派发记录已删除"}。

    Raises:
        NotFoundException: 派发记录不存在（由全局异常处理器处理）。
    """
    _dispatch_service.delete_dispatch(
        db,
        dispatch_id=dispatch_id,
        operator_id=current_user.id,
    )
    return {"message": "派发记录已删除"}


__all__ = [
    "router",
]
