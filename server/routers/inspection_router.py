"""检测记录路由 (Inspection Router)

Sprint 8 — Task 8.3
依据 SRS §4.6、Inspection Schema (Task 8.1)、Inspection Service (Task 8.2)、
    Sprint 1~7 Frozen API。

提供检测记录 HTTP 接口：
    - GET    /api/inspection                     — 检测记录列表（分页+筛选）
    - GET    /api/inspection/{inspection_id}  — 检测记录详情
    - POST   /api/inspection                     — 创建检测记录（上传检测报告后）
    - POST   /api/inspection/{inspection_id}/finish — 完成检测（GRINDING→DISPATCHED）
    - PUT    /api/inspection/{inspection_id}  — 修改检测记录
    - DELETE /api/inspection/{inspection_id}  — 删除检测记录（软删除）

Router 不实现任何业务逻辑，所有能力委托给 InspectionService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
Router 不使用 ORM、JWT、bcrypt、事务、SystemLog、HTTPException。
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from server.core.dependencies import (
    get_current_active_user,
    get_db,
    require_permission,
)
from server.enums.inspection_result import InspectionResult
from server.models.user import User
from server.schemas.inspection_schema import (
    InspectionCreate,
    InspectionUpdate,
    InspectionResponse,
    InspectionListResponse,
)
from server.services.inspection_service import InspectionService


# ============================================================
# 完成检测请求 Schema（Router 内部使用）
# ============================================================


class InspectionFinishRequest(BaseModel):
    """完成检测请求体。

    仅用于 Router 层参数绑定，不纳入 Schema 模块 Frozen API。

    Attributes:
        result: 检测结论（passed 或 failed）。
        failure_reason: 不合格原因（result=failed 时必填）。
    """

    result: InspectionResult = Field(
        ...,
        description="检测结论（passed 或 failed）",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="不合格原因（result=failed 时必填）",
    )


# ============================================================
# Router 定义
# ============================================================


router = APIRouter(
    prefix="/api/inspection",
    tags=["Inspection"],
)

# ============================================================
# 服务实例
# ============================================================

_inspection_service = InspectionService()

# ============================================================
# GET /api/inspection — 检测记录列表
# ============================================================


@router.get(
    "",
    response_model=InspectionListResponse,
    status_code=status.HTTP_200_OK,
    summary="检测记录列表",
    description="分页查询检测记录列表，支持按 task_id、inspector_id、result 筛选。",
)
def list_inspections(
    task_id: Optional[int] = Query(
        default=None,
        description="关联试磨任务 ID",
    ),
    inspector_id: Optional[int] = Query(
        default=None,
        description="检测人 ID",
    ),
    result: Optional[InspectionResult] = Query(
        default=None,
        description="检测结论筛选",
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
    _: None = Depends(require_permission("inspection:view")),
) -> InspectionListResponse:
    """检测记录列表接口。

    调用 InspectionService.list_inspections() 查询检测记录列表。

    Args:
        task_id: 关联试磨任务 ID（可选）。
        inspector_id: 检测人 ID（可选）。
        result: 检测结论筛选（可选）。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（inspection:view）。

    Returns:
        InspectionListResponse: 分页检测记录列表。
    """
    return _inspection_service.list_inspections(
        db,
        task_id=task_id,
        inspector_id=inspector_id,
        result=result,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET /api/inspection/{inspection_id} — 检测记录详情
# ============================================================


@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse,
    status_code=status.HTTP_200_OK,
    summary="检测记录详情",
    description="根据检测记录 ID 查询检测记录详情。",
)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("inspection:view")),
) -> InspectionResponse:
    """检测记录详情接口。

    调用 InspectionService.get_inspection() 查询检测记录。

    Args:
        inspection_id: 检测记录 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（inspection:view）。

    Returns:
        InspectionResponse: 检测记录详情。

    Raises:
        NotFoundException: 检测记录不存在（由全局异常处理器处理）。
    """
    return _inspection_service.get_inspection(db, inspection_id)


# ============================================================
# POST /api/inspection — 创建检测记录（上传检测报告）
# ============================================================


@router.post(
    "",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建检测记录",
    description=(
        "创建检测记录。校验 TrialTask 存在且已开始试磨，一个任务仅允许一条检测记录。"
    ),
)
def create_inspection(
    data: InspectionCreate = Body(..., description="检测创建数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("inspection:create")),
) -> InspectionResponse:
    """创建检测记录接口。

    调用 InspectionService.create_inspection() 完成创建流程：
        ① 校验 TrialTask 存在且已开始试磨
        ② 校验 task_id 未重复创建检测记录
        ③ 创建 InspectionRecord ORM
        ④ 写入 SystemLog

    Args:
        data: 检测创建数据（InspectionCreate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（inspection:create）。

    Returns:
        InspectionResponse: 新创建的检测记录。

    Raises:
        NotFoundException: 试磨任务不存在或未开始试磨（由全局异常处理器处理）。
        BusinessLogicException: 已存在检测记录（由全局异常处理器处理）。
    """
    return _inspection_service.create_inspection(
        db,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# POST /api/inspection/{inspection_id}/finish — 完成检测
# ============================================================


@router.post(
    "/{inspection_id}/finish",
    response_model=InspectionResponse,
    status_code=status.HTTP_200_OK,
    summary="完成检测",
    description=(
        "完成检测。设置检测结论（passed/failed），推进 TrialTask process_status → DISPATCHED。"
    ),
)
def finish_inspection(
    inspection_id: int,
    data: InspectionFinishRequest = Body(
        ..., description="完成检测请求数据"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("inspection:edit")),
) -> InspectionResponse:
    """完成检测接口。

    调用 InspectionService.finish_inspection() 完成检测流程：
        ① 校验 InspectionRecord 存在
        ② 校验 TrialTask 当前 process_status 为 GRINDING
        ③ 校验 result=failed 时 failure_reason 必填
        ④ 更新 InspectionRecord (result)
        ⑤ 设置 TrialTask.result_status (PASSED/FAILED)
        ⑥ 推进 TrialTask.process_status → DISPATCHED
        ⑦ 写入 SystemLog

    Args:
        inspection_id: 检测记录 ID。
        data: 完成检测请求数据（InspectionFinishRequest）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（inspection:edit）。

    Returns:
        InspectionResponse: 更新后的检测记录。

    Raises:
        NotFoundException: 检测记录或任务不存在（由全局异常处理器处理）。
        BusinessLogicException: 状态非法或 failure_reason 缺失（由全局异常处理器处理）。
    """
    return _inspection_service.finish_inspection(
        db,
        inspection_id=inspection_id,
        result=data.result,
        failure_reason=data.failure_reason,
        operator_id=current_user.id,
    )


# ============================================================
# PUT /api/inspection/{inspection_id} — 修改检测记录
# ============================================================


@router.put(
    "/{inspection_id}",
    response_model=InspectionResponse,
    status_code=status.HTTP_200_OK,
    summary="修改检测记录",
    description="修改检测记录。仅更新传入的非 None 字段。",
)
def update_inspection(
    inspection_id: int,
    data: InspectionUpdate = Body(..., description="检测记录更新数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("inspection:edit")),
) -> InspectionResponse:
    """修改检测记录接口。

    调用 InspectionService.update_inspection() 完成更新流程：
        ① 查询检测记录
        ② 仅更新传入字段（exclude_unset）
        ③ 写入 SystemLog

    Args:
        inspection_id: 目标检测记录 ID。
        data: 更新数据（InspectionUpdate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（inspection:edit）。

    Returns:
        InspectionResponse: 更新后的检测记录。

    Raises:
        NotFoundException: 检测记录不存在（由全局异常处理器处理）。
    """
    return _inspection_service.update_inspection(
        db,
        inspection_id=inspection_id,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# DELETE /api/inspection/{inspection_id} — 删除检测记录
# ============================================================


@router.delete(
    "/{inspection_id}",
    status_code=status.HTTP_200_OK,
    summary="删除检测记录",
    description="软删除检测记录（设置 is_deleted=True）。",
)
def delete_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("inspection:delete")),
) -> dict:
    """删除检测记录接口。

    调用 InspectionService.delete_inspection() 完成软删除。

    Args:
        inspection_id: 目标检测记录 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（inspection:delete）。

    Returns:
        dict: {"message": "检测记录已删除"}。

    Raises:
        NotFoundException: 检测记录不存在（由全局异常处理器处理）。
    """
    _inspection_service.delete_inspection(
        db,
        inspection_id=inspection_id,
        operator_id=current_user.id,
    )
    return {"message": "检测记录已删除"}


__all__ = [
    "router",
]
