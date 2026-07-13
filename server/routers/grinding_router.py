"""试磨记录路由 (Grinding Router)

Sprint 7 — Task 7.3
依据 SRS §4.5、Grinding Schema (Task 7.1)、Grinding Service (Task 7.2)、Sprint 2~7 Frozen API。

提供试磨记录 HTTP 接口：
    - GET    /api/grinding                     — 试磨记录列表（分页+筛选）
    - GET    /api/grinding/{grinding_id}       — 试磨记录详情
    - POST   /api/grinding                     — 创建试磨记录（开始试磨：RECEIVED→GRINDING）
    - POST   /api/grinding/{grinding_id}/finish — 完成试磨（GRINDING→DISPATCHED）
    - PUT    /api/grinding/{grinding_id}       — 修改试磨记录
    - DELETE /api/grinding/{grinding_id}       — 删除试磨记录（软删除）

Router 不实现任何业务逻辑，所有能力委托给 GrindingService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
Router 不使用 ORM、JWT、bcrypt、事务、SystemLog、HTTPException。
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from server.core.dependencies import (
    get_current_active_user,
    get_db,
    require_permission,
)
from server.enums.task_result_status import TrialTaskResultStatus
from server.models.user import User
from server.schemas.grinding_schema import (
    GrindingCreate,
    GrindingUpdate,
    GrindingResponse,
    GrindingListResponse,
)
from server.services.grinding_service import GrindingService


# ============================================================
# 完成试磨请求 Schema（Router 内部使用）
# ============================================================


class GrindingFinishRequest(BaseModel):
    """完成试磨请求体。

    仅用于 Router 层参数绑定，不纳入 Schema 模块 Frozen API。

    Attributes:
        result_status: 试磨结果（passed 或 failed）。
        failure_reason: 失败原因（result_status=failed 时必填）。
        end_time: 完成时间（可选，默认当前时间）。
    """

    result_status: TrialTaskResultStatus = Field(
        ...,
        description="试磨结果（passed 或 failed）",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="失败原因（result_status=failed 时必填）",
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="完成时间（可选，默认当前时间）",
    )


# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/grinding",
    tags=["Grinding"],
)

# ============================================================
# 服务实例
# ============================================================

_grinding_service = GrindingService()


# ============================================================
# GET /api/grinding — 试磨记录列表
# ============================================================


@router.get(
    "",
    response_model=GrindingListResponse,
    status_code=status.HTTP_200_OK,
    summary="试磨记录列表",
    description="分页查询试磨记录列表，支持按 task_id、operator_id 筛选。",
)
def list_grindings(
    task_id: Optional[int] = Query(
        default=None,
        description="关联试磨任务 ID",
    ),
    operator_id: Optional[int] = Query(
        default=None,
        description="试磨责任人 ID",
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
    _: None = Depends(require_permission("grinding:view")),
) -> GrindingListResponse:
    """试磨记录列表接口。

    调用 GrindingService.list_grindings() 查询试磨记录列表。

    Args:
        task_id: 关联试磨任务 ID（可选）。
        operator_id: 试磨责任人 ID（可选）。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（grinding:view）。

    Returns:
        GrindingListResponse: 分页试磨记录列表。
    """
    return _grinding_service.list_grindings(
        db,
        task_id=task_id,
        operator_id=operator_id,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET /api/grinding/{grinding_id} — 试磨记录详情
# ============================================================


@router.get(
    "/{grinding_id}",
    response_model=GrindingResponse,
    status_code=status.HTTP_200_OK,
    summary="试磨记录详情",
    description="根据试磨记录 ID 查询试磨记录详情。",
)
def get_grinding(
    grinding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("grinding:view")),
) -> GrindingResponse:
    """试磨记录详情接口。

    调用 GrindingService.get_grinding() 查询试磨记录。

    Args:
        grinding_id: 试磨记录 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（grinding:view）。

    Returns:
        GrindingResponse: 试磨记录详情。

    Raises:
        NotFoundException: 试磨记录不存在（由全局异常处理器处理）。
    """
    return _grinding_service.get_grinding(db, grinding_id)


# ============================================================
# POST /api/grinding — 创建试磨记录（开始试磨）
# ============================================================


@router.post(
    "",
    response_model=GrindingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="开始试磨",
    description=(
        "创建试磨记录。校验 TrialTask 存在且状态为 RECEIVED，"
        "推进 process_status 至 GRINDING。"
    ),
)
def create_grinding(
    data: GrindingCreate = Body(..., description="试磨创建数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("grinding:create")),
) -> GrindingResponse:
    """开始试磨接口。

    调用 GrindingService.create_grinding() 完成创建流程：
        ① 校验 TrialTask 存在且状态为 RECEIVED
        ② 校验 task_id 未重复试磨
        ③ 创建 GrindingRecord ORM
        ④ 推进 TrialTask.process_status → GRINDING
        ⑤ 写入 SystemLog

    Args:
        data: 试磨创建数据（GrindingCreate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（grinding:create）。

    Returns:
        GrindingResponse: 新创建的试磨记录。

    Raises:
        NotFoundException: 试磨任务不存在（由全局异常处理器处理）。
        BusinessLogicException: 状态非法或已试磨（由全局异常处理器处理）。
    """
    return _grinding_service.create_grinding(
        db,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# POST /api/grinding/{grinding_id}/finish — 完成试磨
# ============================================================


@router.post(
    "/{grinding_id}/finish",
    response_model=GrindingResponse,
    status_code=status.HTTP_200_OK,
    summary="完成试磨",
    description=(
        "完成试磨。设置 result_status（passed/failed），"
        "推进 process_status 至 DISPATCHED。"
    ),
)
def finish_grinding(
    grinding_id: int,
    data: GrindingFinishRequest = Body(
        ..., description="完成试磨请求数据"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("grinding:edit")),
) -> GrindingResponse:
    """完成试磨接口。

    调用 GrindingService.finish_grinding() 完成试磨流程：
        ① 校验 GrindingRecord 存在
        ② 校验 TrialTask 当前 process_status 为 GRINDING
        ③ 校验 result_status 合法性（PASSED/FAILED）
        ④ 校验 result_status=failed 时 failure_reason 必填
        ⑤ 更新 GrindingRecord（end_time, fail_reason）
        ⑥ 设置 TrialTask.result_status
        ⑦ 推进 TrialTask.process_status → DISPATCHED
        ⑧ 写入 SystemLog

    Args:
        grinding_id: 试磨记录 ID。
        data: 完成试磨请求数据（GrindingFinishRequest）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（grinding:edit）。

    Returns:
        GrindingResponse: 更新后的试磨记录。

    Raises:
        NotFoundException: 试磨记录或任务不存在（由全局异常处理器处理）。
        BusinessLogicException: 状态非法或 failure_reason 缺失（由全局异常处理器处理）。
    """
    return _grinding_service.finish_grinding(
        db,
        grinding_id=grinding_id,
        result_status=data.result_status,
        failure_reason=data.failure_reason,
        end_time=data.end_time,
        operator_id=current_user.id,
    )


# ============================================================
# PUT /api/grinding/{grinding_id} — 修改试磨记录
# ============================================================


@router.put(
    "/{grinding_id}",
    response_model=GrindingResponse,
    status_code=status.HTTP_200_OK,
    summary="修改试磨记录",
    description="修改试磨记录。仅更新传入的非 None 字段。",
)
def update_grinding(
    grinding_id: int,
    data: GrindingUpdate = Body(..., description="试磨记录更新数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("grinding:edit")),
) -> GrindingResponse:
    """修改试磨记录接口。

    调用 GrindingService.update_grinding() 完成更新流程：
        ① 查询试磨记录
        ② 仅更新传入字段（exclude_unset）
        ③ 写入 SystemLog

    Args:
        grinding_id: 目标试磨记录 ID。
        data: 更新数据（GrindingUpdate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（grinding:edit）。

    Returns:
        GrindingResponse: 更新后的试磨记录。

    Raises:
        NotFoundException: 试磨记录不存在（由全局异常处理器处理）。
    """
    return _grinding_service.update_grinding(
        db,
        grinding_id=grinding_id,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# DELETE /api/grinding/{grinding_id} — 删除试磨记录
# ============================================================


@router.delete(
    "/{grinding_id}",
    status_code=status.HTTP_200_OK,
    summary="删除试磨记录",
    description="软删除试磨记录（设置 is_deleted=True）。",
)
def delete_grinding(
    grinding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("grinding:delete")),
) -> dict:
    """删除试磨记录接口。

    调用 GrindingService.delete_grinding() 完成软删除。

    Args:
        grinding_id: 目标试磨记录 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（grinding:delete）。

    Returns:
        dict: {"message": "试磨记录已删除"}。

    Raises:
        NotFoundException: 试磨记录不存在（由全局异常处理器处理）。
    """
    _grinding_service.delete_grinding(
        db,
        grinding_id=grinding_id,
        operator_id=current_user.id,
    )
    return {"message": "试磨记录已删除"}


__all__ = [
    "router",
]
