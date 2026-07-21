"""系统设置路由 (Settings Router)

Sprint 13 — Task 13.5
依据 SRS §4.12 FR-SETTINGS、Settings Service (Task 13.4)、
    §15.22 Settings Principle、§15.23 Singleton Configuration Principle。

提供系统设置 HTTP 接口：
    - GET /api/settings  — 读取系统配置
    - PUT /api/settings  — 更新系统配置

Router 不实现任何业务逻辑，所有能力委托给 SettingsService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
Router 不使用 ORM、JWT、bcrypt、事务、SystemLog、HTTPException。
"""

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from server.core.dependencies import (
    get_current_active_user,
    get_db,
    require_permission,
)
from server.models.user import User
from server.schemas.settings_schema import (
    SettingsResponse,
    SettingsUpdate,
)
from server.services.settings_service import SettingsService


# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"],
)

# ============================================================
# 服务实例
# ============================================================

_settings_service = SettingsService()

# ============================================================
# GET /api/settings — 读取系统配置
# ============================================================


@router.get(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="读取系统配置",
    description="获取当前系统唯一配置，包含数据库、备份、上传、通知、系统等全部设置项。",
)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("settings:view")),
) -> SettingsResponse:
    """读取系统配置。

    调用 SettingsService.get_settings() 获取当前系统唯一配置。

    Args:
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（settings:view）。

    Returns:
        SettingsResponse: 当前系统配置。
    """
    return _settings_service.get_settings()


# ============================================================
# PUT /api/settings — 更新系统配置
# ============================================================


@router.put(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="更新系统配置",
    description=(
        "更新系统配置项。仅更新传入的非 None 字段，"
        "保持其他字段不变。更新后自动持久化到 .env 文件。"
    ),
)
def update_settings(
    data: SettingsUpdate = Body(
        ...,
        description="待更新的配置数据（仅非 None 字段生效）",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("settings:edit")),
) -> SettingsResponse:
    """更新系统配置。

    调用 SettingsService.update_settings() 执行配置更新。
    自动以当前登录用户 ID 作为操作人。

    Args:
        data: 配置更新数据（SettingsUpdate Schema）。
        db: 数据库会话（依赖注入）。
        current_user: 当前登录用户（依赖注入）。
        _: 权限检查（settings:edit）。

    Returns:
        SettingsResponse: 更新后的完整配置。
    """
    return _settings_service.update_settings(
        db, data, current_user.id,
    )


__all__ = [
    "router",
]
