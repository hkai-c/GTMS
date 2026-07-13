"""收件记录 Schema (Receipt Schema)

Sprint 6 — Task 6.1
严格依据 Sprint 1 Receipt ORM 模型、SRS §4.4、CODE_WIKI.md。

全部字段来自 Sprint 1 ORM Receipt 模型，使用 Pydantic v2 ConfigDict(from_attributes=True)。
image_paths 存储 JSON 数组文本（图片路径列表）。

Schema 列表:
    - ReceiptBase:          收件记录公共字段
    - ReceiptCreate:        创建收件记录
    - ReceiptUpdate:        更新收件记录
    - ReceiptResponse:      收件记录响应
    - ReceiptListResponse:  收件记录列表响应
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# 收件记录公共字段
# ============================================================


class ReceiptBase(BaseModel):
    """收件记录公共字段（创建和响应共用）。

    Attributes:
        task_id: 关联试磨任务 ID。
        received_at: 收件日期时间。
        receiver_id: 收件人 ID。
        image_paths: 工件图片路径（JSON 数组文本，可选）。
    """

    task_id: int = Field(
        ...,
        description="关联试磨任务 ID",
    )
    received_at: datetime = Field(
        ...,
        description="收件日期时间",
    )
    receiver_id: int = Field(
        ...,
        description="收件人 ID",
    )
    image_paths: Optional[str] = Field(
        default=None,
        description="工件图片路径（JSON 数组）",
    )


# ============================================================
# 创建收件记录
# ============================================================


class ReceiptCreate(ReceiptBase):
    """创建收件记录 Schema。

    继承 ReceiptBase，包含所有可填写字段。
    """

    pass


# ============================================================
# 更新收件记录
# ============================================================


class ReceiptUpdate(BaseModel):
    """更新收件记录 Schema。

    所有字段均为可选，仅更新传入的非 None 字段。

    Attributes:
        task_id: 关联试磨任务 ID（可选）。
        received_at: 收件日期时间（可选）。
        receiver_id: 收件人 ID（可选）。
        image_paths: 工件图片路径（可选）。
    """

    task_id: Optional[int] = Field(
        default=None,
        description="关联试磨任务 ID",
    )
    received_at: Optional[datetime] = Field(
        default=None,
        description="收件日期时间",
    )
    receiver_id: Optional[int] = Field(
        default=None,
        description="收件人 ID",
    )
    image_paths: Optional[str] = Field(
        default=None,
        description="工件图片路径（JSON 数组）",
    )


# ============================================================
# 收件记录响应
# ============================================================


class ReceiptResponse(BaseModel):
    """收件记录响应 Schema。

    包含 ORM 全部可读字段，不含 created_by、updated_by、is_deleted。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        id: 收件记录 ID。
        task_id: 关联试磨任务 ID。
        received_at: 收件日期时间。
        receiver_id: 收件人 ID。
        image_paths: 工件图片路径。
        created_at: 创建时间。
        updated_at: 更新时间。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="收件记录 ID")
    task_id: int = Field(..., description="关联试磨任务 ID")
    received_at: datetime = Field(..., description="收件日期时间")
    receiver_id: int = Field(..., description="收件人 ID")
    image_paths: Optional[str] = Field(
        default=None,
        description="工件图片路径（JSON 数组）",
    )
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ============================================================
# 收件记录列表响应
# ============================================================


class ReceiptListResponse(BaseModel):
    """收件记录列表响应 Schema。

    Attributes:
        items: 收件记录列表。
        total: 总数。
    """

    items: list[ReceiptResponse] = Field(
        default_factory=list,
        description="收件记录列表",
    )
    total: int = Field(..., description="总数")


__all__ = [
    "ReceiptBase",
    "ReceiptCreate",
    "ReceiptUpdate",
    "ReceiptResponse",
    "ReceiptListResponse",
]
