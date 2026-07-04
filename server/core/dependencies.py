"""GTMS 依赖注入模块 (Dependency Injection)

Sprint 2 — Task 2.3
严格依据 CODE_WIKI.md §6.2.2、SRS.md、Task 2.1 异常体系、Task 2.2 安全模块。

提供所有 FastAPI 路由所需的依赖注入函数。
后续所有 Router 必须统一使用本模块，不得自行实现认证/权限逻辑。

依赖注入函数:
    - get_db:                    数据库会话（自动关闭）
    - oauth2_scheme:             OAuth2 密码凭证方案
    - get_current_user:          当前用户（从 JWT 解析）
    - get_current_active_user:   当前激活用户
    - get_optional_user:         可选用户（Token 不存在返回 None）
    - require_role:              角色检查工厂
    - require_permission:        权限检查工厂

使用方式:
    from server.core.dependencies import get_current_user, require_role

    @router.get("/admin")
    def admin_endpoint(
        user: User = Depends(get_current_user),
        _: None = Depends(require_role("administrator")),
    ):
        ...
"""

from typing import Any, Callable

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from server.core.exceptions import (
    AuthenticationException,
    PermissionDeniedException,
)
from server.core.security import (
    check_permission,
    decode_access_token,
    has_permission,
)
from server.database.session import get_db as _get_db
from server.models import User

# ============================================================
# 数据库会话
# ============================================================

# 重新导出，保持统一入口
get_db = _get_db

# ============================================================
# OAuth2 方案
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=True,
)


# 可选 Token 方案（不自动报错）
_optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,
)


# ============================================================
# 用户依赖
# ============================================================


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从 JWT 令牌解析当前用户。

    流程:
        1. 读取 Bearer Token
        2. 调用 decode_access_token() 解析 JWT
        3. 读取 payload.sub 作为 user_id
        4. 查询数据库获取 User ORM
        5. 返回 User 实例

    Args:
        token: Bearer Token（由 OAuth2PasswordBearer 自动提取）。
        db: 数据库会话（由 get_db 注入）。

    Returns:
        User ORM 实例。

    Raises:
        AuthenticationException: Token 无效、过期或用户不存在。
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise AuthenticationException("Token 缺少 sub 字段")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise AuthenticationException("用户不存在")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前激活用户。

    在 get_current_user 基础上额外检查用户是否启用。

    Args:
        current_user: 当前用户（由 get_current_user 注入）。

    Returns:
        User ORM 实例。

    Raises:
        AuthenticationException: 用户已被禁用。
    """
    if not current_user.is_active:
        raise AuthenticationException("用户已被禁用")
    return current_user


def get_optional_user(
    token: str | None = Depends(_optional_oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """可选用户：Token 存在时返回 User，否则返回 None。

    用于公开接口中可选的身份信息。

    Args:
        token: Bearer Token（不存在时为 None）。
        db: 数据库会话。

    Returns:
        User ORM 实例或 None。
    """
    if token is None:
        return None

    try:
        payload = decode_access_token(token)
    except AuthenticationException:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return db.query(User).filter(User.id == int(user_id)).first()


# ============================================================
# 角色检查
# ============================================================


def require_role(*roles: str) -> Callable[[User], None]:
    """角色检查工厂函数。

    生成 FastAPI Depends，检查当前用户是否拥有指定角色之一。

    使用方式:
        @router.get("/admin")
        def admin(user: User = Depends(get_current_user),
                  _: None = Depends(require_role("administrator"))):
            ...

        @router.get("/manage")
        def manage(user: User = Depends(get_current_user),
                   _: None = Depends(require_role("administrator", "manager"))):
            ...

    Args:
        *roles: 允许的角色名称列表。

    Returns:
        FastAPI Depends 可调用对象。
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> None:
        """内部角色检查函数。"""
        user_role_names = {role.name for role in current_user.roles}
        allowed = set(roles)

        if not user_role_names & allowed:
            raise PermissionDeniedException(
                f"需要角色 {', '.join(sorted(allowed))}，"
                f"当前角色 {', '.join(sorted(user_role_names)) if user_role_names else '无'}",
                detail={
                    "required_roles": sorted(allowed),
                    "user_roles": sorted(user_role_names),
                },
            )

    return role_checker


# ============================================================
# 权限检查
# ============================================================


def require_permission(permission: str) -> Callable[[User], None]:
    """权限检查工厂函数。

    生成 FastAPI Depends，检查当前用户是否拥有指定权限。

    内部调用 security.py 的 has_permission() / check_permission()。

    使用方式:
        @router.post("/tasks")
        def create_task(user: User = Depends(get_current_user),
                        _: None = Depends(require_permission("task:write"))):
            ...

    Args:
        permission: 权限代码（如 "task:write"）。

    Returns:
        FastAPI Depends 可调用对象。
    """

    def permission_checker(current_user: User = Depends(get_current_user)) -> None:
        """内部权限检查函数。"""
        user_role_names = {role.name for role in current_user.roles}

        # 遍历用户的所有角色，检查是否有任一角色拥有该权限
        for role_name in user_role_names:
            if has_permission(role_name, permission):
                return

        raise PermissionDeniedException(
            f"缺少权限 '{permission}'",
            detail={
                "required_permission": permission,
                "user_roles": sorted(user_role_names),
            },
        )

    return permission_checker


__all__ = [
    "get_db",
    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "require_role",
    "require_permission",
]