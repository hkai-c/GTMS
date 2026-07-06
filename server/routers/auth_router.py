"""认证路由 (Auth Router)

Sprint 3 — Task 3.3
严格依据 SRS §4.1、CODE_WIKI §6、Sprint 2 Frozen API、Sprint 3 Task 3.1/3.2。

提供认证相关 HTTP 接口：
    - POST /api/auth/login             — 用户登录
    - POST /api/auth/change-password   — 修改密码
    - GET  /api/auth/me                — 当前用户信息

Router 不实现任何业务逻辑，所有能力委托给 AuthService。
Router 不捕获业务异常，全部交由全局异常处理器统一处理。
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.core.dependencies import get_current_active_user, get_db
from server.models.user import User
from server.schemas.user_schema import (
    LoginRequest,
    LoginResponse,
    UserPasswordChange,
    UserResponse,
)
from server.services.auth_service import AuthService

# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

# ============================================================
# 服务实例
# ============================================================

_auth_service = AuthService()


# ============================================================
# POST /api/auth/login
# ============================================================


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="用户登录",
    description="使用用户名和密码进行登录认证，返回 JWT 访问令牌。",
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """用户登录接口。

    调用 AuthService.login() 完成认证流程：
        ① 查询用户
        ② 检查启用状态
        ③ 校验密码
        ④ 生成 JWT
        ⑤ 返回 LoginResponse

    Args:
        request: 登录请求体（username + password）。
        db: 数据库会话（依赖注入）。

    Returns:
        LoginResponse: 包含 access_token、token_type、user 信息。

    Raises:
        AuthenticationException: 用户名或密码错误（由全局异常处理器处理）。
        PermissionDeniedException: 用户已被禁用（由全局异常处理器处理）。
    """
    return _auth_service.login(
        db,
        username=request.username,
        password=request.password,
    )


# ============================================================
# POST /api/auth/change-password
# ============================================================


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="修改密码",
    description="登录后修改当前用户密码，需提供旧密码验证。",
)
def change_password(
    request: UserPasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """修改密码接口。

    调用 AuthService.change_password() 完成密码修改流程：
        ① 查询用户（按当前登录用户 ID）
        ② 验证旧密码
        ③ 哈希新密码
        ④ 更新 password_hash
        ⑤ 写入 SystemLog

    Args:
        request: 修改密码请求体（old_password + new_password）。
        current_user: 当前登录用户（依赖注入，需认证）。
        db: 数据库会话（依赖注入）。

    Returns:
        dict: {"message": "Password changed successfully."}

    Raises:
        AuthenticationException: 旧密码错误（由全局异常处理器处理）。
        NotFoundException: 用户不存在（由全局异常处理器处理）。
    """
    _auth_service.change_password(
        db,
        user_id=current_user.id,
        old_password=request.old_password,
        new_password=request.new_password,
    )
    return {"message": "Password changed successfully."}


# ============================================================
# GET /api/auth/me
# ============================================================


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="当前用户信息",
    description="获取当前登录用户的详细信息（不含密码）。",
)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """获取当前用户信息接口。

    调用 AuthService.get_current_user_info() 获取用户信息。

    Args:
        current_user: 当前登录用户（依赖注入，需认证）。
        db: 数据库会话（依赖注入）。

    Returns:
        UserResponse: 当前用户信息（不含 password_hash）。

    Raises:
        NotFoundException: 用户不存在（由全局异常处理器处理）。
    """
    return _auth_service.get_current_user_info(
        db,
        user_id=current_user.id,
    )


__all__ = [
    "router",
]