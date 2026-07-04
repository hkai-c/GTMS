"""
server.core 包

GTMS 核心模块，包含：
    - exceptions: 统一异常体系
    - security:   认证与权限（Sprint 2）
    - dependencies: 依赖注入（Sprint 2）
"""

from server.core.exceptions import (
    BaseAppException,
    AuthenticationException,
    BusinessLogicException,
    DuplicateException,
    NotFoundException,
    PermissionDeniedException,
)

from server.core.security import (
    ROLE_PERMISSION_MAP,
    check_permission,
    create_access_token,
    decode_access_token,
    hash_password,
    has_permission,
    is_admin,
    is_manager,
    is_technician,
    is_viewer,
    verify_password,
)

from server.core.dependencies import (
    get_current_active_user,
    get_current_user,
    get_db,
    get_optional_user,
    oauth2_scheme,
    require_permission,
    require_role,
)

__all__ = [
    # 异常
    "BaseAppException",
    "AuthenticationException",
    "BusinessLogicException",
    "DuplicateException",
    "NotFoundException",
    "PermissionDeniedException",
    # 安全
    "ROLE_PERMISSION_MAP",
    "check_permission",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "has_permission",
    "is_admin",
    "is_manager",
    "is_technician",
    "is_viewer",
    "verify_password",
    # 依赖注入
    "get_current_active_user",
    "get_current_user",
    "get_db",
    "get_optional_user",
    "oauth2_scheme",
    "require_permission",
    "require_role",
]