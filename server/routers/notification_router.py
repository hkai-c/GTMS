"""消息提醒路由 (Notification Router)

Sprint 12 — Task 12.3
依据 SRS §4.9、Notification Schema (Task 12.1)、
    Notification Service (Task 12.2)、§15.17 Notification Principle。

提供消息提醒 HTTP 接口：
    - GET    /api/notifications                         — 分页查询
    - GET    /api/notifications/{notification_id}       — 查询单条
    - POST   /api/notifications                         — 创建消息
    - PUT    /api/notifications/{notification_id}/read  — 标记已读
    - PUT    /api/notifications/read-all                — 全部已读

Router 不实现任何业务逻辑，所有能力委托给 NotificationService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
Router 不使用 ORM、JWT、bcrypt、事务、SystemLog、HTTPException。
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from server.core.dependencies import (
    get_current_active_user,
    get_db,
    require_permission,
)
from server.enums.notify_type import NotifyType
from server.models.user import User
from server.schemas.notification_schema import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
)
from server.services.notification_service import NotificationService


# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notification"],
)

# ============================================================
# 服务实例
# ============================================================

_notification_service = NotificationService()

# ============================================================
# GET /api/notifications — 分页查询消息提醒
# ============================================================


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="分页查询消息提醒",
    description=(
        "查询当前用户的消息提醒列表。"
        "支持 is_read、notification_type 筛选，"
        "支持分页。"
    ),
)
def list_notifications(
    is_read: Optional[bool] = Query(
        default=None,
        description="已读状态筛选（true/false）",
    ),
    notification_type: Optional[NotifyType] = Query(
        default=None,
        description="提醒类型筛选",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="页码（从 1 开始）",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=200,
        description="每页条数",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("notification:view")),
) -> NotificationListResponse:
    """分页查询消息提醒。

    调用 NotificationService.list_notifications() 执行分页查询。
    自动以当前登录用户 ID 进行权限隔离。

    Args:
        is_read: 已读状态筛选（可选）。
        notification_type: 提醒类型筛选（可选）。
        page: 页码。
        page_size: 每页条数。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（notification:view）。

    Returns:
        NotificationListResponse: 分页查询结果。
    """
    return _notification_service.list_notifications(
        db,
        user_id=current_user.id,
        is_read=is_read,
        notification_type=notification_type,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET /api/notifications/{notification_id} — 查询单条消息
# ============================================================


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="查询单条消息提醒",
    description="根据消息提醒 ID 查询单条消息提醒详情。",
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("notification:view")),
) -> NotificationResponse:
    """查询单条消息提醒。

    调用 NotificationService.get_notification() 获取消息详情。

    Args:
        notification_id: 消息提醒 ID（路径参数）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（notification:view）。

    Returns:
        NotificationResponse: 消息提醒详情。
    """
    return _notification_service.get_notification(
        db, notification_id,
    )


# ============================================================
# POST /api/notifications — 创建消息提醒
# ============================================================


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建消息提醒",
    description="创建一条消息提醒记录。",
)
def create_notification(
    data: NotificationCreate = Body(..., description="消息提醒数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("notification:create")),
) -> NotificationResponse:
    """创建消息提醒。

    调用 NotificationService.create_notification() 创建消息。

    Args:
        data: 消息提醒数据（NotificationCreate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（notification:create）。

    Returns:
        NotificationResponse: 创建的消息提醒。
    """
    return _notification_service.create_notification(db, data)


# ============================================================
# PUT /api/notifications/{notification_id}/read — 标记已读
# ============================================================


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="标记消息已读",
    description="将指定消息提醒标记为已读。",
)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("notification:edit")),
) -> NotificationResponse:
    """标记单条消息提醒为已读。

    调用 NotificationService.mark_as_read() 标记已读。
    自动以当前登录用户 ID 作为操作人。

    Args:
        notification_id: 消息提醒 ID（路径参数）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（notification:edit）。

    Returns:
        NotificationResponse: 更新后的消息提醒。
    """
    return _notification_service.mark_as_read(
        db, notification_id, current_user.id,
    )


# ============================================================
# PUT /api/notifications/read-all — 全部已读
# ============================================================


@router.put(
    "/read-all",
    response_model=int,
    status_code=status.HTTP_200_OK,
    summary="全部标记已读",
    description="将当前用户全部未读消息标记为已读。",
)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("notification:edit")),
) -> int:
    """标记当前用户全部未读消息为已读。

    调用 NotificationService.mark_all_as_read() 批量标记。
    自动以当前登录用户 ID 为目标用户。

    Args:
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（notification:edit）。

    Returns:
        int: 已更新数量。
    """
    return _notification_service.mark_all_as_read(
        db, current_user.id,
    )


__all__ = [
    "router",
]
