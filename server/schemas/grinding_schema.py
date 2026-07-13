"""试磨记录 Schema (Grinding Schema)

Sprint 7 — Task 7.1
严格依据 Sprint 1 GrindingRecord ORM 模型、SRS §4.5、CODE_WIKI.md。

全部字段来自 Sprint 1 ORM GrindingRecord 模型。
使用 Pydantic v2 ConfigDict(from_attributes=True)。
image_paths 存储 JSON 数组文本（图片路径列表）。

Schema 列表:
    - GrindingBase:          试磨记录公共字段
    - GrindingCreate:        创建试磨记录（开始试磨）
    - GrindingUpdate:        更新试磨记录（完成试磨）
    - GrindingResponse:      试磨记录响应
    - GrindingListResponse:  试磨记录列表响应
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# 试磨记录公共字段
# ============================================================


class GrindingBase(BaseModel):
    """试磨记录公共字段（创建和响应共用）。

    Attributes:
        task_id: 关联试磨任务 ID。
        operator_id: 试磨责任人 ID。
        start_time: 工件领出时间。
        machine_type: 试磨机型（可选）。
        wheel_type: 砂轮型号（可选）。
        params: 加工参数（可选）。
        end_time: 完成时间（可选）。
        image_paths: 试磨图片路径（JSON 数组文本，可选）。
        fail_reason: 失败原因（result_status=failed 时填写，可选）。
    """

    task_id: int = Field(
        ...,
        description="关联试磨任务 ID",
    )
    operator_id: int = Field(
        ...,
        description="试磨责任人 ID",
    )
    start_time: datetime = Field(
        ...,
        description="工件领出时间",
    )
    machine_type: Optional[str] = Field(
        default=None,
        description="试磨机型",
    )
    wheel_type: Optional[str] = Field(
        default=None,
        description="砂轮型号",
    )
    params: Optional[str] = Field(
        default=None,
        description="加工参数",
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="完成时间",
    )
    image_paths: Optional[str] = Field(
        default=None,
        description="试磨图片路径（JSON 数组）",
    )
    fail_reason: Optional[str] = Field(
        default=None,
        description="失败原因（result_status=failed 时填写）",
    )


# ============================================================
# 创建试磨记录（开始试磨）
# ============================================================


class GrindingCreate(GrindingBase):
    """创建试磨记录 Schema（开始试磨）。

    继承 GrindingBase，包含所有可填写字段。
    必填: task_id, operator_id, start_time。
    """

    pass


# ============================================================
# 更新试磨记录（完成试磨）
# ============================================================


class GrindingUpdate(BaseModel):
    """更新试磨记录 Schema（完成试磨）。

    所有字段均为可选，仅更新传入的非 None 字段。

    Attributes:
        machine_type: 试磨机型（可选）。
        wheel_type: 砂轮型号（可选）。
        params: 加工参数（可选）。
        end_time: 完成时间（可选）。
        image_paths: 试磨图片路径（可选）。
        fail_reason: 失败原因（可选）。
    """

    machine_type: Optional[str] = Field(
        default=None,
        description="试磨机型",
    )
    wheel_type: Optional[str] = Field(
        default=None,
        description="砂轮型号",
    )
    params: Optional[str] = Field(
        default=None,
        description="加工参数",
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="完成时间",
    )
    image_paths: Optional[str] = Field(
        default=None,
        description="试磨图片路径（JSON 数组）",
    )
    fail_reason: Optional[str] = Field(
        default=None,
        description="失败原因（result_status=failed 时填写）",
    )


# ============================================================
# 试磨记录响应
# ============================================================


class GrindingResponse(BaseModel):
    """试磨记录响应 Schema。

    包含 ORM 全部可读字段，不含 created_by、updated_by、is_deleted。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        id: 试磨记录 ID。
        task_id: 关联试磨任务 ID。
        operator_id: 试磨责任人 ID。
        start_time: 工件领出时间。
        machine_type: 试磨机型。
        wheel_type: 砂轮型号。
        params: 加工参数。
        end_time: 完成时间。
        image_paths: 试磨图片路径。
        fail_reason: 失败原因。
        created_at: 创建时间。
        updated_at: 更新时间。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="试磨记录 ID")
    task_id: int = Field(..., description="关联试磨任务 ID")
    operator_id: int = Field(..., description="试磨责任人 ID")
    start_time: datetime = Field(..., description="工件领出时间")
    machine_type: Optional[str] = Field(
        default=None,
        description="试磨机型",
    )
    wheel_type: Optional[str] = Field(
        default=None,
        description="砂轮型号",
    )
    params: Optional[str] = Field(
        default=None,
        description="加工参数",
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="完成时间",
    )
    image_paths: Optional[str] = Field(
        default=None,
        description="试磨图片路径（JSON 数组）",
    )
    fail_reason: Optional[str] = Field(
        default=None,
        description="失败原因（result_status=failed 时填写）",
    )
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ============================================================
# 试磨记录列表响应
# ============================================================


class GrindingListResponse(BaseModel):
    """试磨记录列表响应 Schema。

    Attributes:
        items: 试磨记录列表。
        total: 总数。
    """

    items: list[GrindingResponse] = Field(
        default_factory=list,
        description="试磨记录列表",
    )
    total: int = Field(..., description="总数")


__all__ = [
    "GrindingBase",
    "GrindingCreate",
    "GrindingUpdate",
    "GrindingResponse",
    "GrindingListResponse",
]
