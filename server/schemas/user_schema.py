"""用户 Schema (User Schema)

Sprint 3 — Task 3.1
严格依据 Sprint 1 User ORM 模型、CODE_WIKI.md。

全部字段来自 Sprint 1 ORM，使用 Pydantic v2 ConfigDict(from_attributes=True)。
密码字段仅在 create/update 时写入，response 不返回 password_hash。

Schema 列表:
    - LoginRequest:       登录请求
    - LoginResponse:      登录响应
    - UserBase:           用户公共字段
    - UserCreate:         创建用户
    - UserUpdate:         更新用户
    - UserPasswordChange: 修改密码
    - UserResponse:       用户响应
    - UserListResponse:   用户列表响应
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from server.schemas.role_schema import RoleResponse


# ============================================================
# 登录
# ============================================================


class LoginRequest(BaseModel):
    """登录请求 Schema。

    Attributes:
        username: 登录用户名。
        password: 明文密码。
    """

    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="登录用户名",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="明文密码",
    )


class LoginResponse(BaseModel):
    """登录响应 Schema。

    Attributes:
        access_token: JWT 访问令牌。
        token_type: 令牌类型（固定 "bearer"）。
        user: 当前用户信息。
    """

    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: "UserResponse" = Field(..., description="当前用户信息")


# ============================================================
# 用户公共字段
# ============================================================


class UserBase(BaseModel):
    """用户公共字段（创建和响应共用）。

    Attributes:
        username: 登录用户名。
        real_name: 真实姓名。
        phone: 联系电话（可选）。
        is_active: 启用状态。
    """

    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="登录用户名",
    )
    real_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="真实姓名",
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="联系电话",
    )
    is_active: bool = Field(
        default=True,
        description="启用状态",
    )


# ============================================================
# 创建用户
# ============================================================


class UserCreate(UserBase):
    """创建用户 Schema。

    继承 UserBase，额外增加密码字段（仅创建时可写）。
    """

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="明文密码（存储前会 bcrypt 哈希）",
    )


# ============================================================
# 更新用户
# ============================================================


class UserUpdate(BaseModel):
    """更新用户 Schema。

    所有字段均为可选，仅更新传入的非 None 字段。

    Attributes:
        username: 登录用户名（可选）。
        real_name: 真实姓名（可选）。
        phone: 联系电话（可选）。
        is_active: 启用状态（可选）。
        password: 新密码（可选，仅更新时传入）。
    """

    username: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="登录用户名",
    )
    real_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="真实姓名",
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="联系电话",
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="启用状态",
    )
    password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=128,
        description="新密码（bcrypt 哈希后存储）",
    )


# ============================================================
# 修改密码
# ============================================================


class UserPasswordChange(BaseModel):
    """修改密码 Schema。

    Attributes:
        old_password: 当前密码（验证用）。
        new_password: 新密码。
    """

    old_password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="当前密码",
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="新密码",
    )


# ============================================================
# 用户响应
# ============================================================


class UserResponse(BaseModel):
    """用户响应 Schema。

    包含 ORM 全部可读字段，不含 password_hash。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        id: 用户 ID。
        username: 登录用户名。
        real_name: 真实姓名。
        phone: 联系电话。
        is_active: 启用状态。
        created_at: 创建时间。
        updated_at: 更新时间。
        roles: 关联角色列表。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户 ID")
    username: str = Field(..., description="登录用户名")
    real_name: str = Field(..., description="真实姓名")
    phone: Optional[str] = Field(default=None, description="联系电话")
    is_active: bool = Field(..., description="启用状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    roles: list[RoleResponse] = Field(
        default_factory=list,
        description="关联角色列表",
    )


# ============================================================
# 用户列表响应
# ============================================================


class UserListResponse(BaseModel):
    """用户列表响应 Schema。

    Attributes:
        items: 用户列表。
        total: 总数。
    """

    items: list[UserResponse] = Field(
        default_factory=list,
        description="用户列表",
    )
    total: int = Field(..., description="总数")


__all__ = [
    "LoginRequest",
    "LoginResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPasswordChange",
    "UserResponse",
    "UserListResponse",
]