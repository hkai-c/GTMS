"""GTMS 安全模块 (Security Module)

Sprint 2 — Task 2.2
严格依据 CODE_WIKI.md §6.2.1、SRS.md、Sprint 1 ORM。

功能：
    - Password Hash:           bcrypt 加密与验证
    - JWT:                     HS256 创建与解析
    - Role-Permission Mapping: 基于 RBAC 的角色权限映射
    - Permission Check:        权限检查
    - Role Check:              角色判断

使用方式:
    from server.core.security import hash_password, create_access_token

    hashed = hash_password("admin123")
    token = create_access_token({"sub": "1", "username": "admin", "role": "administrator"})
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.hash import bcrypt

from server.config import settings
from server.core.exceptions import (
    AuthenticationException,
    BusinessLogicException,
    PermissionDeniedException,
)

# ============================================================
# 密码加密与验证
# ============================================================


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希。

    bcrypt 自动生成随机 salt，不可逆。

    Args:
        password: 明文密码。

    Returns:
        bcrypt 哈希字符串。

    Raises:
        BusinessLogicException: 密码为空时抛出。
    """
    if not password:
        raise BusinessLogicException("密码不能为空")
    return bcrypt.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与 bcrypt 哈希是否匹配。

    Args:
        plain_password: 明文密码。
        hashed_password: bcrypt 哈希字符串。

    Returns:
        True 如果匹配，否则 False。
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.verify(plain_password, hashed_password)
    except ValueError:
        return False


# ============================================================
# JWT Token 管理
# ============================================================


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """创建 JWT 访问令牌（HS256 签名）。

    自动注入 iat（签发时间）和 exp（过期时间）。

    Args:
        data: Payload 数据，必须包含 sub、username、role。
        expires_delta: 自定义过期时间，默认使用 settings.ACCESS_TOKEN_EXPIRE_MINUTES。

    Returns:
        JWT 字符串。

    Raises:
        BusinessLogicException: data 缺少必需字段时抛出。
    """
    required_fields = {"sub", "username", "role"}
    missing = required_fields - set(data.keys())
    if missing:
        raise BusinessLogicException(
            f"Token payload 缺少必需字段: {', '.join(sorted(missing))}"
        )

    to_encode = dict(data)
    now = datetime.now(timezone.utc)
    to_encode["iat"] = now
    to_encode["exp"] = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["type"] = "access"

    return jwt.encode(
        to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """解析并验证 JWT 访问令牌。

    验证签名、过期时间、载荷格式。

    Args:
        token: JWT 字符串。

    Returns:
        解析后的 payload dict。

    Raises:
        AuthenticationException: Token 无效、过期或签名错误时抛出。
    """
    if not token:
        raise AuthenticationException("Token 不能为空")

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Token 已过期")
    except jwt.InvalidSignatureError:
        raise AuthenticationException("Token 签名无效")
    except jwt.InvalidTokenError as e:
        raise AuthenticationException(f"Token 无效: {str(e)}")

    # 验证必需字段
    required_fields = {"sub", "username", "role", "exp", "iat"}
    missing = required_fields - set(payload.keys())
    if missing:
        raise AuthenticationException(
            f"Token payload 缺少必需字段: {', '.join(sorted(missing))}"
        )

    return payload


# ============================================================
# 角色-权限映射（基于 RBAC）
# ============================================================

# 全部权限代码（Router 规范: view/create/edit/delete）
# BUG-PERM-001/002 修复: 统一为 Router 规范，废弃 read/write
_ALL_PERMISSIONS = {
    # 用户管理
    "user:view", "user:create", "user:edit", "user:delete",
    # 角色管理
    "role:view", "role:create", "role:edit",
    # 任务管理
    "task:view", "task:create", "task:edit", "task:delete",
    # 客户管理
    "customer:view", "customer:create", "customer:edit",
    # 收件管理
    "receipt:view", "receipt:create", "receipt:edit", "receipt:delete",
    # 试磨管理
    "grinding:view", "grinding:create", "grinding:edit", "grinding:delete",
    # 检测管理
    "inspection:view", "inspection:create", "inspection:edit", "inspection:delete",
    # 发货管理
    "dispatch:view", "dispatch:create", "dispatch:edit", "dispatch:delete",
    # 通知管理
    "notification:view", "notification:create", "notification:edit",
    # 查询统计
    "query:view", "query:export",
    # 审计日志
    "log:view", "system",
    # 设置
    "settings:view", "settings:edit",
}

ROLE_PERMISSION_MAP: dict[str, set[str]] = {
    "administrator": _ALL_PERMISSIONS,
    "manager": {
        "task:view", "task:create", "task:edit", "task:delete",
        "customer:view", "customer:create", "customer:edit",
        "receipt:view", "receipt:create", "receipt:edit", "receipt:delete",
        "grinding:view", "grinding:create", "grinding:edit", "grinding:delete",
        "inspection:view", "inspection:create", "inspection:edit", "inspection:delete",
        "dispatch:view", "dispatch:create", "dispatch:edit", "dispatch:delete",
        "notification:view", "notification:create", "notification:edit",
        "query:view", "query:export",
        "log:view",
    },
    "technician": {
        "task:view",
        "grinding:view", "grinding:create", "grinding:edit",
        "inspection:view", "inspection:create", "inspection:edit",
        "notification:view",
    },
    "viewer": {
        "task:view",
        "receipt:view",
        "grinding:view",
        "inspection:view",
        "dispatch:view",
        "customer:view",
        "query:view",
        "notification:view",
    },
}

# ============================================================
# 权限检查
# ============================================================


def has_permission(role: str, permission: str) -> bool:
    """检查指定角色是否拥有指定权限。

    Args:
        role: 角色名称（如 "administrator"）。
        permission: 权限代码（如 "task:write"）。

    Returns:
        True 如果角色拥有该权限，否则 False。
    """
    permissions = ROLE_PERMISSION_MAP.get(role)
    if permissions is None:
        return False
    return permission in permissions


def check_permission(role: str, permission: str) -> None:
    """检查权限，无权限时抛出 PermissionDeniedException。

    Args:
        role: 角色名称。
        permission: 权限代码。

    Raises:
        PermissionDeniedException: 角色无此权限时抛出。
    """
    if not has_permission(role, permission):
        raise PermissionDeniedException(
            f"角色 '{role}' 没有权限 '{permission}'",
            detail={"role": role, "permission": permission},
        )


# ============================================================
# 角色检查
# ============================================================


def is_admin(role: str) -> bool:
    """检查是否为管理员角色。

    Args:
        role: 角色名称。

    Returns:
        True 如果 role == "administrator"。
    """
    return role == "administrator"


def is_manager(role: str) -> bool:
    """检查是否为经理角色。

    Args:
        role: 角色名称。

    Returns:
        True 如果 role == "manager"。
    """
    return role == "manager"


def is_technician(role: str) -> bool:
    """检查是否为技术员角色。

    Args:
        role: 角色名称。

    Returns:
        True 如果 role == "technician"。
    """
    return role == "technician"


def is_viewer(role: str) -> bool:
    """检查是否为查看者角色。

    Args:
        role: 角色名称。

    Returns:
        True 如果 role == "viewer"。
    """
    return role == "viewer"


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "ROLE_PERMISSION_MAP",
    "has_permission",
    "check_permission",
    "is_admin",
    "is_manager",
    "is_technician",
    "is_viewer",
]