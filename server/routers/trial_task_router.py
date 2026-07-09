"""试磨任务路由 (TrialTask Router)

Sprint 5 — Task 5.3
严格依据 SRS §4.3、Sprint 2 Frozen API、Sprint 5 Task 5.1/5.2。

提供试磨任务 HTTP 接口：
    - GET    /api/tasks                  — 任务列表（分页+多条件筛选）
    - GET    /api/tasks/{task_id}        — 任务详情
    - POST   /api/tasks                  — 创建任务
    - PUT    /api/tasks/{task_id}        — 修改任务（含状态流转）
    - DELETE /api/tasks/{task_id}        — 删除任务（软删除）

Router 不实现任何业务逻辑，所有能力委托给 TaskService。
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
from server.enums.task_process_status import TrialTaskProcessStatus
from server.enums.task_result_status import TrialTaskResultStatus
from server.models.user import User
from server.schemas.trial_task_schema import (
    TrialTaskCreate,
    TrialTaskUpdate,
    TrialTaskResponse,
    TrialTaskListResponse,
)
from server.services.task_service import TaskService

# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/tasks",
    tags=["Task"],
)

# ============================================================
# 服务实例
# ============================================================

_task_service = TaskService()


# ============================================================
# GET /api/tasks — 任务列表
# ============================================================


@router.get(
    "",
    response_model=TrialTaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="任务列表",
    description="分页查询试磨任务列表，支持多条件筛选（task_no、customer_id、sales_id、process_status、result_status）。",
)
def list_tasks(
    task_no: Optional[str] = Query(
        default=None,
        description="任务编号（模糊搜索）",
    ),
    customer_id: Optional[int] = Query(
        default=None,
        description="客户 ID",
    ),
    process_status: Optional[TrialTaskProcessStatus] = Query(
        default=None,
        description="流程状态",
    ),
    result_status: Optional[TrialTaskResultStatus] = Query(
        default=None,
        description="结果状态",
    ),
    sales_id: Optional[int] = Query(
        default=None,
        description="销售 ID",
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
    _: None = Depends(require_permission("task:view")),
) -> TrialTaskListResponse:
    """任务列表接口。

    调用 TaskService.list_tasks() 查询任务列表。

    Args:
        task_no: 任务编号模糊搜索（可选）。
        customer_id: 客户 ID（可选）。
        process_status: 流程状态（可选）。
        result_status: 结果状态（可选）。
        sales_id: 销售 ID（可选）。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（task:view）。

    Returns:
        TrialTaskListResponse: 分页任务列表。
    """
    return _task_service.list_tasks(
        db,
        task_no=task_no,
        customer_id=customer_id,
        process_status=process_status,
        result_status=result_status,
        sales_id=sales_id,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET /api/tasks/{task_id} — 任务详情
# ============================================================


@router.get(
    "/{task_id}",
    response_model=TrialTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="任务详情",
    description="根据任务 ID 查询试磨任务详情。",
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("task:view")),
) -> TrialTaskResponse:
    """任务详情接口。

    调用 TaskService.get_task() 查询任务。

    Args:
        task_id: 任务 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（task:view）。

    Returns:
        TrialTaskResponse: 任务详情。

    Raises:
        NotFoundException: 任务不存在（由全局异常处理器处理）。
    """
    return _task_service.get_task(db, task_id)


# ============================================================
# POST /api/tasks — 创建任务
# ============================================================


@router.post(
    "",
    response_model=TrialTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建任务",
    description="创建试磨任务。自动生成任务编号（YYYYMMDD-N），校验客户与销售存在，默认状态为 CREATED。",
)
def create_task(
    data: TrialTaskCreate = Body(..., description="任务创建数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("task:create")),
) -> TrialTaskResponse:
    """创建任务接口。

    调用 TaskService.create_task() 完成创建流程：
        ① 调用 generate_task_no(db) 生成唯一编号
        ② 校验 customer_id 存在
        ③ 校验 sales_id 存在
        ④ 创建 TrialTask ORM（process_status=CREATED, result_status=PENDING）
        ⑤ 提交事务
        ⑥ 写入 SystemLog

    Args:
        data: 任务创建数据（TrialTaskCreate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（task:create）。

    Returns:
        TrialTaskResponse: 新创建的任务。

    Raises:
        BusinessLogicException: 客户或销售不存在（由全局异常处理器处理）。
    """
    return _task_service.create_task(
        db,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# PUT /api/tasks/{task_id} — 修改任务
# ============================================================


@router.put(
    "/{task_id}",
    response_model=TrialTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="修改任务",
    description="修改试磨任务。仅更新传入的非 None 字段。仅 CREATED 状态可编辑基本信息。支持状态流转。",
)
def update_task(
    task_id: int,
    data: TrialTaskUpdate = Body(..., description="任务更新数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("task:edit")),
) -> TrialTaskResponse:
    """修改任务接口。

    调用 TaskService.update_task() 完成更新流程：
        ① 查询任务
        ② 仅更新传入字段（exclude_unset）
        ③ 仅 CREATED 状态可编辑基本信息
        ④ 状态流转校验
        ⑤ 写入 SystemLog

    Args:
        task_id: 目标任务 ID。
        data: 更新数据（TrialTaskUpdate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（task:edit）。

    Returns:
        TrialTaskResponse: 更新后的任务。

    Raises:
        NotFoundException: 任务不存在（由全局异常处理器处理）。
        BusinessLogicException: 状态不允许编辑或非法状态流转（由全局异常处理器处理）。
    """
    return _task_service.update_task(
        db,
        task_id=task_id,
        data=data,
        operator_id=current_user.id,
    )


# ============================================================
# DELETE /api/tasks/{task_id} — 删除任务
# ============================================================


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="删除任务",
    description="软删除试磨任务（设置 is_deleted=True）。",
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("task:delete")),
) -> dict:
    """删除任务接口。

    调用 TaskService.delete_task() 完成软删除。

    Args:
        task_id: 目标任务 ID。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（task:delete）。

    Returns:
        dict: {"message": "任务已删除"}。

    Raises:
        NotFoundException: 任务不存在（由全局异常处理器处理）。
    """
    _task_service.delete_task(
        db,
        task_id=task_id,
        operator_id=current_user.id,
    )
    return {"message": "任务已删除"}


__all__ = [
    "router",
]
