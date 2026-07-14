"""工件派发 Schema (Dispatch Schema)

Sprint 9 — Task 9.1
严格依据 Sprint 1 Dispatch ORM 模型、DB_DESIGN.md §4.8、SRS §4.7。
使用 Pydantic v2 ConfigDict(from_attributes=True)。

Schema 列表:
    - DispatchBase:         工件派发公共字段
    - DispatchCreate:       创建工件派发记录
    - DispatchUpdate:       更新工件派发记录
    - DispatchResponse:     工件派发记录响应
    - DispatchListResponse: 工件派发记录列表响应
    - DispatchQuery:        工件派发记录查询参数

注意: 字段命名严格遵循 DB_DESIGN.md §4.8 dispatches 表结构,
      与 SRS §4.7 的语义一致（direction=去向方向, dispatch_date=去向日期,
      operator_id=操作人）。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from server.enums import DestinationType


# ============================================================
# 工件派发公共字段
# ============================================================


class DispatchBase(BaseModel):
    """工件派发公共字段（创建和更新共用）。

    字段基于 Sprint 1 Dispatch ORM 模型 (DB_DESIGN.md §4.8)。

    Attributes:
        task_id: 关联试磨任务 ID（UNIQUE）。
        direction: 去向方向（DestinationType 枚举）。
        dispatch_date: 去向日期。
        operator_id: 操作人 ID。
    """

    task_id: int = Field(
        ...,
        description="关联试磨任务 ID",
    )
    direction: DestinationType = Field(
        ...,
        description="去向方向",
    )
    dispatch_date: datetime = Field(
        ...,
        description="去向日期",
    )
    operator_id: int = Field(
        ...,
        description="操作人 ID",
    )


# ============================================================
# 创建工件派发记录
# ============================================================


class DispatchCreate(DispatchBase):
    """创建工件派发记录 Schema。

    继承 DispatchBase。全部 4 个字段均为必填。
    无额外校验——业务校验（result_status=passed + process_status=grinding）
    由 Service 层负责。
    """

    pass


# ============================================================
# 更新工件派发记录
# ============================================================


class DispatchUpdate(BaseModel):
    """更新工件派发记录 Schema。

    所有字段均为可选，仅更新传入的非 None 字段。

    Attributes:
        direction: 去向方向（可选）。
        dispatch_date: 去向日期（可选）。
        operator_id: 操作人 ID（可选）。
    """

    direction: Optional[DestinationType] = Field(
        default=None,
        description="去向方向",
    )
    dispatch_date: Optional[datetime] = Field(
        default=None,
        description="去向日期",
    )
    operator_id: Optional[int] = Field(
        default=None,
        description="操作人 ID",
    )


# ============================================================
# 工件派发记录响应
# ============================================================


class DispatchResponse(BaseModel):
    """工件派发记录响应 Schema。

    包含 ORM 全部可读字段，不含 created_by、updated_by、is_deleted。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        id: 派发记录 ID。
        task_id: 关联试磨任务 ID。
        direction: 去向方向。
        dispatch_date: 去向日期。
        operator_id: 操作人 ID。
        created_at: 创建时间。
        updated_at: 更新时间。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="派发记录 ID")
    task_id: int = Field(..., description="关联试磨任务 ID")
    direction: DestinationType = Field(..., description="去向方向")
    dispatch_date: datetime = Field(..., description="去向日期")
    operator_id: int = Field(..., description="操作人 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ============================================================
# 工件派发记录列表响应
# ============================================================


class DispatchListResponse(BaseModel):
    """工件派发记录列表响应 Schema。

    Attributes:
        items: 派发记录列表。
        total: 总数。
    """

    items: list[DispatchResponse] = Field(
        default_factory=list,
        description="派发记录列表",
    )
    total: int = Field(..., description="总数")


# ============================================================
# 工件派发记录查询参数
# ============================================================


class DispatchQuery(BaseModel):
    """工件派发记录查询参数 Schema。

    支持分页、关键词搜索、去向筛选、排序。
    符合 §15.9.20 Performance Standard。

    Attributes:
        page: 页码（从 1 开始）。
        page_size: 每页条数。
        keyword: 关键词搜索（任务编号）。
        direction: 去向方向筛选。
        sort_by: 排序字段。
        sort_order: 排序方向（asc / desc）。
    """

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
    keyword: Optional[str] = Field(
        default=None,
        description="关键词搜索（任务编号）",
    )
    direction: Optional[DestinationType] = Field(
        default=None,
        description="去向方向筛选",
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


__all__ = [
    "DispatchBase",
    "DispatchCreate",
    "DispatchUpdate",
    "DispatchResponse",
    "DispatchListResponse",
    "DispatchQuery",
]
