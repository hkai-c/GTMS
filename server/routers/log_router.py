"""操作日志路由 (Log Router)

Sprint 11 — Task 11.3
依据 SRS §4.10、Log Schema (Task 11.1)、Log Service (Task 11.2)、
    §15.15 Audit Logging Principle。

提供操作日志 HTTP 接口：
    - GET    /api/log          — 分页查询日志
    - GET    /api/log/{log_id} — 查询单条日志
    - POST   /api/log          — 创建日志（系统内部）
    - POST   /api/log/export   — 导出数据准备

Router 不实现任何业务逻辑，所有能力委托给 LogService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
Router 不使用 ORM、JWT、bcrypt、事务、SystemLog、HTTPException。
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from server.core.dependencies import (
    get_current_active_user,
    get_db,
    require_permission,
)
from server.enums.action_type import ActionType
from server.models.user import User
from server.schemas.log_schema import (
    LogBase,
    LogListResponse,
    LogQuery,
    LogResponse,
)
from server.services.log_service import LogService


# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/log",
    tags=["Log"],
)

# ============================================================
# 服务实例
# ============================================================

_log_service = LogService()

# ============================================================
# GET /api/log — 分页查询日志
# ============================================================


@router.get(
    "",
    response_model=LogListResponse,
    status_code=status.HTTP_200_OK,
    summary="分页查询日志",
    description=(
        "支持 operator_id、operation、module、keyword、"
        "start_time、end_time 多条件筛选，支持分页和排序。"
    ),
)
def list_logs(
    operator_id: Optional[int] = Query(
        default=None,
        description="操作人 ID 筛选",
    ),
    operation: Optional[ActionType] = Query(
        default=None,
        description="操作类型筛选（create/update/delete/status_change）",
    ),
    module: Optional[str] = Query(
        default=None,
        description="模块名称筛选",
    ),
    keyword: Optional[str] = Query(
        default=None,
        description="关键字搜索（匹配操作对象和描述）",
    ),
    start_time: Optional[datetime] = Query(
        default=None,
        description="开始时间",
    ),
    end_time: Optional[datetime] = Query(
        default=None,
        description="结束时间",
    ),
    sort_by: str = Query(
        default="created_at",
        description="排序字段",
    ),
    sort_order: str = Query(
        default="desc",
        description="排序方向（asc/desc）",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="页码（从 1 开始）",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=200,
        description="每页条数",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("log:view")),
) -> LogListResponse:
    """分页查询操作日志。

    调用 LogService.list_logs() 执行分页查询。

    Args:
        operator_id: 操作人 ID 筛选（可选）。
        operation: 操作类型筛选（可选）。
        module: 模块名称筛选（可选）。
        keyword: 关键字搜索（可选）。
        start_time: 开始时间（可选）。
        end_time: 结束时间（可选）。
        sort_by: 排序字段。
        sort_order: 排序方向。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（log:view）。

    Returns:
        LogListResponse: 分页查询结果。
    """
    log_query = LogQuery(
        operator_id=operator_id,
        operation=operation,
        module=module,
        keyword=keyword,
        start_time=start_time,
        end_time=end_time,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return _log_service.list_logs(db, log_query)


# ============================================================
# GET /api/log/{log_id} — 查询单条日志
# ============================================================


@router.get(
    "/{log_id}",
    response_model=LogResponse,
    status_code=status.HTTP_200_OK,
    summary="查询单条日志",
    description="根据日志 ID 查询单条操作日志详情。",
)
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("log:view")),
) -> LogResponse:
    """查询单条操作日志。

    调用 LogService.get_log() 获取日志详情。

    Args:
        log_id: 日志 ID（路径参数）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（log:view）。

    Returns:
        LogResponse: 日志详情。
    """
    return _log_service.get_log(db, log_id)


# ============================================================
# POST /api/log — 创建日志（系统内部）
# ============================================================


@router.post(
    "",
    response_model=LogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建日志",
    description="仅供系统内部调用，创建操作日志记录。",
)
def create_log(
    data: LogBase = Body(..., description="日志数据"),
    db: Session = Depends(get_db),
    _: None = Depends(require_permission("system")),
) -> LogResponse:
    """创建操作日志（系统内部调用）。

    调用 LogService.create_log() 创建日志记录。

    Args:
        data: 日志数据（LogBase Schema）。
        db: 数据库会话（依赖注入）。
        _: 权限检查（system）。

    Returns:
        LogResponse: 创建的日志记录。
    """
    return _log_service.create_log(db, data)


# ============================================================
# POST /api/log/export — 导出数据准备
# ============================================================


@router.post(
    "/export",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
    summary="导出数据准备",
    description=(
        "根据查询条件准备导出数据，返回字典列表。"
        "仅准备数据，不生成文件。"
    ),
)
def export_logs(
    data: LogQuery = Body(..., description="导出查询参数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("log:view")),
) -> list[dict]:
    """导出日志数据准备。

    调用 LogService.export_logs() 准备导出数据。

    Args:
        data: 导出查询参数（LogQuery Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（log:view）。

    Returns:
        list[dict]: 导出数据列表。
    """
    return _log_service.export_logs(db, data)


__all__ = [
    "router",
]
