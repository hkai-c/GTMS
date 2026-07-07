"""客户 Schema (Customer Schema)

Sprint 4 — Task 4.1
严格依据 Sprint 1 Customer ORM 模型、SRS §4.2、CODE_WIKI.md。

全部字段来自 Sprint 1 ORM Customer 模型，使用 Pydantic v2 ConfigDict(from_attributes=True)。
email 和 remark 为预留字段（ORM 中暂无对应列，始终返回 None）。

Schema 列表:
    - CustomerBase:          客户公共字段
    - CustomerCreate:        创建客户
    - CustomerUpdate:        更新客户
    - CustomerResponse:      客户响应
    - CustomerListResponse:  客户列表响应
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# 客户公共字段
# ============================================================


class CustomerBase(BaseModel):
    """客户公共字段（创建和响应共用）。

    Attributes:
        company_name: 公司名称。
        contact_person: 联系人（映射 ORM contact 列）。
        phone: 联系电话（可选）。
        email: 邮箱（预留字段，可选）。
        address: 地址（可选）。
        remark: 备注（预留字段，可选）。
    """

    company_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="公司名称",
    )
    contact_person: Optional[str] = Field(
        default=None,
        max_length=50,
        description="联系人",
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="联系电话",
    )
    email: Optional[str] = Field(
        default=None,
        max_length=200,
        description="邮箱（预留字段）",
    )
    address: Optional[str] = Field(
        default=None,
        description="地址",
    )
    remark: Optional[str] = Field(
        default=None,
        description="备注（预留字段）",
    )


# ============================================================
# 创建客户
# ============================================================


class CustomerCreate(CustomerBase):
    """创建客户 Schema。

    继承 CustomerBase，company_name 必填。
    """

    pass


# ============================================================
# 更新客户
# ============================================================


class CustomerUpdate(BaseModel):
    """更新客户 Schema。

    所有字段均为可选，仅更新传入的非 None 字段。

    Attributes:
        company_name: 公司名称（可选）。
        contact_person: 联系人（可选）。
        phone: 联系电话（可选）。
        email: 邮箱（可选）。
        address: 地址（可选）。
        remark: 备注（可选）。
    """

    company_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="公司名称",
    )
    contact_person: Optional[str] = Field(
        default=None,
        max_length=50,
        description="联系人",
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="联系电话",
    )
    email: Optional[str] = Field(
        default=None,
        max_length=200,
        description="邮箱",
    )
    address: Optional[str] = Field(
        default=None,
        description="地址",
    )
    remark: Optional[str] = Field(
        default=None,
        description="备注",
    )


# ============================================================
# 客户响应
# ============================================================


class CustomerResponse(BaseModel):
    """客户响应 Schema。

    包含 ORM 全部可读字段，不含 created_by、updated_by、is_deleted。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        id: 客户 ID。
        company_name: 公司名称。
        contact_person: 联系人。
        phone: 联系电话。
        email: 邮箱。
        address: 地址。
        remark: 备注。
        created_at: 创建时间。
        updated_at: 更新时间。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="客户 ID")
    company_name: str = Field(..., description="公司名称")
    contact_person: Optional[str] = Field(
        default=None,
        description="联系人",
    )
    phone: Optional[str] = Field(default=None, description="联系电话")
    email: Optional[str] = Field(default=None, description="邮箱")
    address: Optional[str] = Field(default=None, description="地址")
    remark: Optional[str] = Field(default=None, description="备注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ============================================================
# 客户列表响应
# ============================================================


class CustomerListResponse(BaseModel):
    """客户列表响应 Schema。

    Attributes:
        items: 客户列表。
        total: 总数。
    """

    items: list[CustomerResponse] = Field(
        default_factory=list,
        description="客户列表",
    )
    total: int = Field(..., description="总数")


__all__ = [
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerListResponse",
]