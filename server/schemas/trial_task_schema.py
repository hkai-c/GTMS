"""试磨任务 Schema (TrialTask Schema)

Sprint 5 — Task 5.1
严格依据 Sprint 1 TrialTask ORM 模型、SRS §4.3、CODE_WIKI.md。

全部字段来自 Sprint 1 ORM TrialTask 模型，使用 Pydantic v2 ConfigDict(from_attributes=True)。
任务编号 task_no 格式: YYYYMMDD-N (如 20260707-1)，由 generate_task_no() 自动生成。

Schema 列表:
    - TrialTaskBase:      试磨任务公共字段
    - TrialTaskCreate:    创建试磨任务
    - TrialTaskUpdate:    更新试磨任务
    - TrialTaskResponse:  试磨任务响应
    - TrialTaskListResponse: 试磨任务列表响应
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from server.enums import (
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
    DestinationType,
)


# ============================================================
# 试磨任务公共字段
# ============================================================


class TrialTaskBase(BaseModel):
    """试磨任务公共字段（创建和响应共用）。

    Attributes:
        customer_id: 客户 ID。
        requirement: 加工要求。
        tracking_no: 快递单号（可选）。
        sales_id: 销售 ID。
        process_status: 流程状态（默认 CREATED）。
        result_status: 结果状态（默认 PENDING）。
        destination: 工件去向（可选）。
        destination_date: 工件去向日期（可选）。
        failure_reason: 失败原因（result_status=failed 时填写，可选）。
    """

    customer_id: int = Field(
        ...,
        description="客户 ID",
    )
    requirement: str = Field(
        ...,
        min_length=1,
        description="加工要求",
    )
    tracking_no: Optional[str] = Field(
        default=None,
        max_length=100,
        description="快递单号",
    )
    sales_id: int = Field(
        ...,
        description="销售 ID",
    )
    process_status: TrialTaskProcessStatus = Field(
        default=TrialTaskProcessStatus.CREATED,
        description="流程状态",
    )
    result_status: TrialTaskResultStatus = Field(
        default=TrialTaskResultStatus.PENDING,
        description="结果状态",
    )
    destination: Optional[DestinationType] = Field(
        default=None,
        description="工件去向",
    )
    destination_date: Optional[date] = Field(
        default=None,
        description="工件去向日期",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="失败原因（result_status=failed 时填写）",
    )


# ============================================================
# 创建试磨任务
# ============================================================


class TrialTaskCreate(TrialTaskBase):
    """创建试磨任务 Schema。

    继承 TrialTaskBase，包含所有可填写字段。
    task_no 由系统自动生成，不允许用户创建时指定。
    """

    pass


# ============================================================
# 更新试磨任务
# ============================================================


class TrialTaskUpdate(BaseModel):
    """更新试磨任务 Schema。

    所有字段均为可选，仅更新传入的非 None 字段。

    Attributes:
        customer_id: 客户 ID（可选）。
        requirement: 加工要求（可选）。
        tracking_no: 快递单号（可选）。
        sales_id: 销售 ID（可选）。
        process_status: 流程状态（可选）。
        result_status: 结果状态（可选）。
        destination: 工件去向（可选）。
        destination_date: 工件去向日期（可选）。
        failure_reason: 失败原因（可选）。
    """

    customer_id: Optional[int] = Field(
        default=None,
        description="客户 ID",
    )
    requirement: Optional[str] = Field(
        default=None,
        min_length=1,
        description="加工要求",
    )
    tracking_no: Optional[str] = Field(
        default=None,
        max_length=100,
        description="快递单号",
    )
    sales_id: Optional[int] = Field(
        default=None,
        description="销售 ID",
    )
    process_status: Optional[TrialTaskProcessStatus] = Field(
        default=None,
        description="流程状态",
    )
    result_status: Optional[TrialTaskResultStatus] = Field(
        default=None,
        description="结果状态",
    )
    destination: Optional[DestinationType] = Field(
        default=None,
        description="工件去向",
    )
    destination_date: Optional[date] = Field(
        default=None,
        description="工件去向日期",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="失败原因（result_status=failed 时填写）",
    )


# ============================================================
# 试磨任务响应
# ============================================================


class TrialTaskResponse(BaseModel):
    """试磨任务响应 Schema。

    包含 ORM 全部可读字段，不含 created_by、updated_by、is_deleted。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        id: 试磨任务 ID。
        task_no: 任务编号。
        customer_id: 客户 ID。
        requirement: 加工要求。
        tracking_no: 快递单号。
        sales_id: 销售 ID。
        process_status: 流程状态。
        result_status: 结果状态。
        destination: 工件去向。
        destination_date: 工件去向日期。
        failure_reason: 失败原因。
        created_at: 创建时间。
        updated_at: 更新时间。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="试磨任务 ID")
    task_no: str = Field(..., description="任务编号 (YYYYMMDD-N)")
    customer_id: int = Field(..., description="客户 ID")
    requirement: str = Field(..., description="加工要求")
    tracking_no: Optional[str] = Field(default=None, description="快递单号")
    sales_id: int = Field(..., description="销售 ID")
    process_status: TrialTaskProcessStatus = Field(..., description="流程状态")
    result_status: TrialTaskResultStatus = Field(..., description="结果状态")
    destination: Optional[DestinationType] = Field(default=None, description="工件去向")
    destination_date: Optional[date] = Field(default=None, description="工件去向日期")
    failure_reason: Optional[str] = Field(default=None, description="失败原因")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ============================================================
# 试磨任务列表响应
# ============================================================


class TrialTaskListResponse(BaseModel):
    """试磨任务列表响应 Schema。

    Attributes:
        items: 试磨任务列表。
        total: 总数。
    """

    items: list[TrialTaskResponse] = Field(
        default_factory=list,
        description="试磨任务列表",
    )
    total: int = Field(..., description="总数")


__all__ = [
    "TrialTaskBase",
    "TrialTaskCreate",
    "TrialTaskUpdate",
    "TrialTaskResponse",
    "TrialTaskListResponse",
]
