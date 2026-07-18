"""操作日志 Schema (Log Schema)

Sprint 11 — Task 11.1
严格依据 SRS §4.10、DB_DESIGN §4.10、CODE_WIKI §15.15。
使用 Pydantic v2 Field()、field_validator、ConfigDict。

Schema 列表:
    - LogBase:         日志基础字段
    - LogResponse:     日志响应
    - LogListResponse: 日志列表响应
    - LogQuery:        日志查询参数

注意: 日志模块为只读查询模块，不涉及 Workflow 和 Status Machine。
      Schema 仅定义数据结构，不包含业务逻辑。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from server.enums.action_type import ActionType


# ============================================================
# 日志基础 Schema
# ============================================================


class LogBase(BaseModel):
    """操作日志基础字段。

    对应 DB_DESIGN §4.10 system_logs 表结构。

    Attributes:
        operator_id: 操作人 ID（> 0）。
        operation: 操作类型（create/update/delete/status_change）。
        module: 操作模块名称（不能为空）。
        target_type: 操作对象类型（不能为空）。
        target_id: 操作对象 ID（>= 0）。
        description: 操作描述（最长 1000 字符）。
        created_at: 操作时间。
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    operator_id: int = Field(
        ...,
        gt=0,
        description="操作人 ID（> 0）",
    )
    operation: ActionType = Field(
        ...,
        description="操作类型",
    )
    module: str = Field(
        ...,
        min_length=1,
        description="操作模块名称",
    )
    target_type: str = Field(
        ...,
        min_length=1,
        description="操作对象类型",
    )
    target_id: Optional[int] = Field(
        default=None,
        ge=0,
        description="操作对象 ID（>= 0）",
    )
    description: str = Field(
        ...,
        max_length=1000,
        description="操作描述",
    )
    created_at: datetime = Field(
        ...,
        description="操作时间",
    )

    @field_validator("module")
    @classmethod
    def validate_module_not_empty(cls, v: str) -> str:
        """验证 module 不能为空字符串。"""
        if not v.strip():
            raise ValueError("module 不能为空")
        return v.strip()

    @field_validator("target_type")
    @classmethod
    def validate_target_type_not_empty(cls, v: str) -> str:
        """验证 target_type 不能为空字符串。"""
        if not v.strip():
            raise ValueError("target_type 不能为空")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description_not_empty(cls, v: str) -> str:
        """验证 description 不能为空字符串。"""
        if not v.strip():
            raise ValueError("description 不能为空")
        return v.strip()


# ============================================================
# 日志响应 Schema
# ============================================================


class LogResponse(LogBase):
    """操作日志响应。

    继承 LogBase 全部字段，新增 id 字段。

    Attributes:
        id: 日志 ID。
    """

    id: int = Field(
        ...,
        ge=1,
        description="日志 ID",
    )


# ============================================================
# 日志列表响应 Schema
# ============================================================


class LogListResponse(BaseModel):
    """操作日志列表响应。

    Attributes:
        items: 日志列表。
        total: 总记录数。
    """

    items: list[LogResponse] = Field(
        default_factory=list,
        description="日志列表",
    )
    total: int = Field(
        ...,
        ge=0,
        description="总记录数",
    )


# ============================================================
# 日志查询参数 Schema
# ============================================================


class LogQuery(BaseModel):
    """操作日志查询参数。

    支持分页、排序、多条件筛选。
    符合 §15.15.11 Query Principle：只读查询，支持分页/筛选/排序。

    Attributes:
        page: 页码（>= 1）。
        page_size: 每页条数（1~200）。
        operator_id: 操作人 ID 筛选。
        operation: 操作类型筛选。
        module: 模块名称筛选。
        keyword: 关键字搜索。
        start_time: 开始时间。
        end_time: 结束时间。
        sort_by: 排序字段。
        sort_order: 排序方向（asc / desc）。
    """

    page: int = Field(
        default=1,
        ge=1,
        description="页码（>= 1）",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=200,
        description="每页条数（1~200）",
    )
    operator_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="操作人 ID 筛选",
    )
    operation: Optional[ActionType] = Field(
        default=None,
        description="操作类型筛选",
    )
    module: Optional[str] = Field(
        default=None,
        description="模块名称筛选",
    )
    keyword: Optional[str] = Field(
        default=None,
        description="关键字搜索",
    )
    start_time: Optional[datetime] = Field(
        default=None,
        description="开始时间",
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="结束时间",
    )
    sort_by: str = Field(
        default="created_at",
        description="排序字段",
    )
    sort_order: str = Field(
        default="desc",
        description="排序方向",
    )

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """验证 sort_order 仅允许 asc 或 desc。"""
        if v not in ("asc", "desc"):
            raise ValueError("sort_order 仅允许 asc 或 desc")
        return v

    @field_validator("keyword")
    @classmethod
    def validate_keyword_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """验证 keyword 不为空字符串。"""
        if v is not None and not v.strip():
            return None
        return v


__all__ = [
    "LogBase",
    "LogResponse",
    "LogListResponse",
    "LogQuery",
]
