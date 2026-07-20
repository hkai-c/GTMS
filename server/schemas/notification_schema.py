"""消息提醒 Schema (Notification Schema)

Sprint 12 — Task 12.1
严格依据 SRS §4.9、DB_DESIGN §4.11、CODE_WIKI §15.17。
使用 Pydantic v2 Field()、field_validator、ConfigDict。

Schema 列表:
    - NotificationBase:         消息提醒基础字段
    - NotificationCreate:       消息提醒创建
    - NotificationUpdate:       消息提醒更新（仅 is_read）
    - NotificationResponse:     消息提醒响应
    - NotificationListResponse: 消息提醒列表响应
    - NotificationQuery:        消息提醒查询参数

注意: 消息提醒模块为通知模块，不涉及 Workflow 和 Status Machine。
      Schema 仅定义数据结构，不包含业务逻辑。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from server.enums.notify_type import NotifyType


# ============================================================
# 消息提醒基础 Schema
# ============================================================


class NotificationBase(BaseModel):
    """消息提醒基础字段。

    对应 DB_DESIGN §4.11 notifications 表结构。

    Attributes:
        user_id: 目标用户 ID（> 0）。
        notification_type: 提醒类型（receipt_delay/grinding_delay/report_missing）。
        title: 提醒标题（不能为空）。
        content: 提醒内容（不能为空）。
        target_type: 关联对象类型。
        target_id: 关联对象 ID（>= 0）。
        is_read: 是否已读。
        created_at: 创建时间。
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: int = Field(
        ...,
        gt=0,
        description="目标用户 ID（> 0）",
    )
    notification_type: NotifyType = Field(
        ...,
        description="提醒类型",
    )
    title: str = Field(
        ...,
        min_length=1,
        description="提醒标题",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="提醒内容",
    )
    target_type: str = Field(
        default="trial_task",
        min_length=1,
        description="关联对象类型",
    )
    target_id: int = Field(
        ...,
        ge=0,
        description="关联对象 ID（>= 0）",
    )
    is_read: bool = Field(
        default=False,
        description="是否已读",
    )
    created_at: datetime = Field(
        ...,
        description="创建时间",
    )

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """验证 title 不能为空字符串。"""
        if not v.strip():
            raise ValueError("title 不能为空")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        """验证 content 不能为空字符串。"""
        if not v.strip():
            raise ValueError("content 不能为空")
        return v.strip()

    @field_validator("target_type")
    @classmethod
    def validate_target_type_not_empty(cls, v: str) -> str:
        """验证 target_type 不能为空字符串。"""
        if not v.strip():
            raise ValueError("target_type 不能为空")
        return v.strip()


# ============================================================
# 消息提醒创建 Schema
# ============================================================


class NotificationCreate(NotificationBase):
    """消息提醒创建请求。

    继承 NotificationBase 全部字段。
    创建时允许写入所有基础字段。
    """

    pass


# ============================================================
# 消息提醒更新 Schema
# ============================================================


class NotificationUpdate(BaseModel):
    """消息提醒更新请求。

    仅允许更新 is_read 字段。
    全部字段 Optional，仅提交需要更新的字段。

    Attributes:
        is_read: 是否已读。
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    is_read: Optional[bool] = Field(
        default=None,
        description="是否已读",
    )


# ============================================================
# 消息提醒响应 Schema
# ============================================================


class NotificationResponse(NotificationBase):
    """消息提醒响应。

    继承 NotificationBase 全部字段，新增 id、read_time、updated_at。

    Attributes:
        id: 消息提醒 ID。
        read_time: 已读时间。
        updated_at: 更新时间。
    """

    id: int = Field(
        ...,
        ge=1,
        description="消息提醒 ID",
    )
    read_time: Optional[datetime] = Field(
        default=None,
        description="已读时间",
    )
    updated_at: datetime = Field(
        ...,
        description="更新时间",
    )


# ============================================================
# 消息提醒列表响应 Schema
# ============================================================


class NotificationListResponse(BaseModel):
    """消息提醒列表响应。

    Attributes:
        items: 消息提醒列表。
        total: 总记录数。
    """

    items: list[NotificationResponse] = Field(
        default_factory=list,
        description="消息提醒列表",
    )
    total: int = Field(
        ...,
        ge=0,
        description="总记录数",
    )


# ============================================================
# 消息提醒查询参数 Schema
# ============================================================


class NotificationQuery(BaseModel):
    """消息提醒查询参数。

    支持分页、排序、多条件筛选。
    符合 §15.17 Notification Principle：只读查询，支持分页/筛选/排序。

    Attributes:
        page: 页码（>= 1）。
        page_size: 每页条数（1~200）。
        user_id: 目标用户 ID 筛选。
        notification_type: 提醒类型筛选。
        is_read: 已读状态筛选。
        keyword: 关键字搜索。
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
    user_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="目标用户 ID 筛选",
    )
    notification_type: Optional[NotifyType] = Field(
        default=None,
        description="提醒类型筛选",
    )
    is_read: Optional[bool] = Field(
        default=None,
        description="已读状态筛选",
    )
    keyword: Optional[str] = Field(
        default=None,
        description="关键字搜索",
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
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationQuery",
]
