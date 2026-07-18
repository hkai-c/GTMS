"""查询统计 Schema (Query Schema)

Sprint 10 — Task 10.1
严格依据 SRS §4.8、DB_DESIGN、§15.9.20 Performance Standard。
使用 Pydantic v2 Field() 和 ConfigDict。

Schema 列表:
    - QueryFilter:        多条件查询筛选参数
    - StatisticsSummary:  统计摘要
    - RankingItem:        排行项
    - StatisticsResponse: 统计响应
    - ExportRequest:      导出请求
    - QueryResponse:      查询响应

注意: 查询统计模块为只读模块，不涉及 Workflow 和 Status Machine。
      Schema 仅定义数据结构，不包含业务逻辑。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# 多条件查询筛选参数
# ============================================================


class QueryFilter(BaseModel):
    """多条件查询筛选参数。

    支持分页、排序、多条件组合查询。
    符合 §15.9.20 Performance Standard：全部过滤转化为数据库 WHERE 子句，
    禁止 Python 内存过滤。

    Attributes:
        customer_id: 客户 ID 筛选。
        process_status: 流程状态筛选（多选，逗号分隔）。
        result_status: 结果状态筛选（多选，逗号分隔）。
        operator_id: 试磨责任人 ID 筛选。
        machine_model: 试磨机型模糊匹配。
        date_from: 创建日期起。
        date_to: 创建日期止。
        keyword: 任务编号精确匹配。
        page: 页码（从 1 开始）。
        page_size: 每页条数（1~200）。
        sort_by: 排序字段。
        sort_order: 排序方向（asc / desc）。
    """

    customer_id: Optional[int] = Field(
        default=None,
        description="客户 ID 筛选",
    )
    process_status: Optional[str] = Field(
        default=None,
        description="流程状态筛选（多选，逗号分隔）",
    )
    result_status: Optional[str] = Field(
        default=None,
        description="结果状态筛选（多选，逗号分隔）",
    )
    operator_id: Optional[int] = Field(
        default=None,
        description="试磨责任人 ID 筛选",
    )
    machine_model: Optional[str] = Field(
        default=None,
        description="试磨机型模糊匹配",
    )
    date_from: Optional[datetime] = Field(
        default=None,
        description="创建日期起",
    )
    date_to: Optional[datetime] = Field(
        default=None,
        description="创建日期止",
    )
    keyword: Optional[str] = Field(
        default=None,
        description="任务编号精确匹配",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="页码（从 1 开始）",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=200,
        description="每页条数",
    )
    sort_by: str = Field(
        default="created_at",
        description="排序字段",
    )
    sort_order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="排序方向（asc / desc）",
    )


# ============================================================
# 统计摘要
# ============================================================


class StatisticsSummary(BaseModel):
    """统计摘要。

    包含本月/年度任务数、通过/未通过数量、成功率等统计指标。
    全部字段 >= 0，success_rate 范围 0~100。

    Attributes:
        month_count: 本月任务总数。
        year_count: 年度任务总数。
        passed_count: 通过数量。
        failed_count: 未通过数量。
        success_rate: 成功率（百分比，0~100）。
    """

    month_count: int = Field(
        ...,
        ge=0,
        description="本月任务总数",
    )
    year_count: int = Field(
        ...,
        ge=0,
        description="年度任务总数",
    )
    passed_count: int = Field(
        ...,
        ge=0,
        description="通过数量",
    )
    failed_count: int = Field(
        ...,
        ge=0,
        description="未通过数量",
    )
    success_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="成功率（百分比，0~100）",
    )


# ============================================================
# 排行项
# ============================================================


class RankingItem(BaseModel):
    """排行项。

    Attributes:
        name: 排行名称（客户名称 / 机型名称）。
        count: 数量（>= 0）。
    """

    name: str = Field(
        ...,
        description="排行名称",
    )
    count: int = Field(
        ...,
        ge=0,
        description="数量",
    )


# ============================================================
# 统计响应
# ============================================================


class StatisticsResponse(BaseModel):
    """统计响应。

    Attributes:
        summary: 统计摘要。
        customer_ranking: 客户排行（Top 10）。
        machine_ranking: 机型排行（Top 10）。
    """

    summary: StatisticsSummary = Field(
        ...,
        description="统计摘要",
    )
    customer_ranking: list[RankingItem] = Field(
        default_factory=list,
        description="客户排行",
    )
    machine_ranking: list[RankingItem] = Field(
        default_factory=list,
        description="机型排行",
    )


# ============================================================
# 导出请求
# ============================================================


class ExportRequest(QueryFilter):
    """导出请求。

    继承 QueryFilter 的全部筛选参数，新增导出相关字段。

    Attributes:
        file_name: 导出文件名。
        format: 导出格式（仅允许 xlsx）。
    """

    file_name: str = Field(
        default="export",
        description="导出文件名",
    )
    format: str = Field(
        default="xlsx",
        pattern="^xlsx$",
        description="导出格式（仅允许 xlsx）",
    )


# ============================================================
# 查询响应
# ============================================================


class QueryResponse(BaseModel):
    """查询响应。

    Attributes:
        items: 查询结果列表。
        total: 总记录数。
        page: 当前页码。
        page_size: 每页条数。
    """

    items: list[dict] = Field(
        default_factory=list,
        description="查询结果列表",
    )
    total: int = Field(
        ...,
        description="总记录数",
    )
    page: int = Field(
        ...,
        description="当前页码",
    )
    page_size: int = Field(
        ...,
        description="每页条数",
    )


__all__ = [
    "QueryFilter",
    "StatisticsSummary",
    "RankingItem",
    "StatisticsResponse",
    "ExportRequest",
    "QueryResponse",
]
