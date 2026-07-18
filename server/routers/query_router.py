"""查询统计路由 (Query Router)

Sprint 10 — Task 10.3
依据 SRS §4.8、Query Schema (Task 10.1)、Query Service (Task 10.2)、
    §15.13 Query Aggregation Principle、Sprint 1~10 Frozen API。

提供查询统计 HTTP 接口：
    - GET    /api/query                   — 多条件组合查询
    - GET    /api/query/statistics        — 统计汇总
    - GET    /api/query/ranking/customers — 客户排行
    - GET    /api/query/ranking/machines  — 机型排行
    - POST   /api/query/export            — 导出数据准备

Router 不实现任何业务逻辑，所有能力委托给 QueryService。
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
from server.models.user import User
from server.schemas.query_schema import (
    ExportRequest,
    QueryFilter,
    QueryResponse,
    RankingItem,
    StatisticsResponse,
)
from server.services.query_service import QueryService


# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/query",
    tags=["Query"],
)

# ============================================================
# 服务实例
# ============================================================

_query_service = QueryService()

# ============================================================
# GET /api/query — 多条件组合查询
# ============================================================


@router.get(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="多条件组合查询",
    description=(
        "支持 customer_id、process_status、result_status、"
        "operator_id、machine_model、keyword、date_from、date_to "
        "多条件组合筛选，支持分页和排序。"
    ),
)
def list_tasks(
    customer_id: Optional[int] = Query(
        default=None,
        description="客户 ID 筛选",
    ),
    process_status: Optional[str] = Query(
        default=None,
        description="流程状态筛选（逗号分隔多值）",
    ),
    result_status: Optional[str] = Query(
        default=None,
        description="结果状态筛选（逗号分隔多值）",
    ),
    operator_id: Optional[int] = Query(
        default=None,
        description="操作员 ID 筛选",
    ),
    machine_model: Optional[str] = Query(
        default=None,
        description="试磨机型模糊匹配",
    ),
    keyword: Optional[str] = Query(
        default=None,
        description="任务编号精确匹配",
    ),
    date_from: Optional[datetime] = Query(
        default=None,
        description="创建日期起始",
    ),
    date_to: Optional[datetime] = Query(
        default=None,
        description="创建日期截止",
    ),
    sort_by: str = Query(
        default="created_at",
        description="排序字段（id/task_no/created_at/updated_at/"
                    "process_status/result_status）",
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
        le=100,
        description="每页条数",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("query:view")),
) -> QueryResponse:
    """多条件组合查询接口。

    调用 QueryService.list_tasks() 执行组合查询，返回分页结果。

    Args:
        customer_id: 客户 ID 筛选（可选）。
        process_status: 流程状态筛选（可选，逗号分隔多值）。
        result_status: 结果状态筛选（可选，逗号分隔多值）。
        operator_id: 操作员 ID 筛选（可选）。
        machine_model: 试磨机型模糊匹配（可选）。
        keyword: 任务编号精确匹配（可选）。
        date_from: 创建日期起始（可选）。
        date_to: 创建日期截止（可选）。
        sort_by: 排序字段。
        sort_order: 排序方向。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（query:view）。

    Returns:
        QueryResponse: 分页查询结果。
    """
    query_filter = QueryFilter(
        customer_id=customer_id,
        process_status=process_status,
        result_status=result_status,
        operator_id=operator_id,
        machine_model=machine_model,
        keyword=keyword,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return _query_service.list_tasks(db, query_filter)


# ============================================================
# GET /api/query/statistics — 统计汇总
# ============================================================


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="统计汇总",
    description=(
        "获取统计摘要数据，包括本月任务数、年度任务数、"
        "通过/失败数量、成功率、客户排行、机型排行。"
    ),
)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("query:view")),
) -> StatisticsResponse:
    """统计汇总接口。

    调用 QueryService.get_statistics() 获取统计摘要。

    Args:
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（query:view）。

    Returns:
        StatisticsResponse: 统计摘要数据。
    """
    return _query_service.get_statistics(db)


# ============================================================
# GET /api/query/ranking/customers — 客户排行
# ============================================================


@router.get(
    "/ranking/customers",
    response_model=list[RankingItem],
    status_code=status.HTTP_200_OK,
    summary="客户排行",
    description="按试磨任务数量倒序排列的客户 Top 10 排行。",
)
def get_customer_ranking(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("query:view")),
) -> list[RankingItem]:
    """客户排行接口。

    调用 QueryService.get_customer_ranking() 获取客户排行。

    Args:
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（query:view）。

    Returns:
        list[RankingItem]: 客户排行列表。
    """
    return _query_service.get_customer_ranking(db)


# ============================================================
# GET /api/query/ranking/machines — 机型排行
# ============================================================


@router.get(
    "/ranking/machines",
    response_model=list[RankingItem],
    status_code=status.HTTP_200_OK,
    summary="机型排行",
    description="按试磨任务数量倒序排列的机型 Top 10 排行。",
)
def get_machine_ranking(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("query:view")),
) -> list[RankingItem]:
    """机型排行接口。

    调用 QueryService.get_machine_ranking() 获取机型排行。

    Args:
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（query:view）。

    Returns:
        list[RankingItem]: 机型排行列表。
    """
    return _query_service.get_machine_ranking(db)


# ============================================================
# POST /api/query/export — 导出数据准备
# ============================================================


@router.post(
    "/export",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
    summary="导出数据准备",
    description=(
        "根据查询筛选条件准备导出数据，返回二维字典列表。"
        "仅准备数据，不生成文件。"
    ),
)
def export_excel(
    data: ExportRequest = Body(..., description="导出请求参数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("query:export")),
) -> list[dict]:
    """导出数据准备接口。

    调用 QueryService.export_excel() 准备导出数据。

    Args:
        data: 导出请求参数（ExportRequest Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（query:export）。

    Returns:
        list[dict]: 导出数据列表。
    """
    return _query_service.export_excel(db, data)


__all__ = [
    "router",
]
