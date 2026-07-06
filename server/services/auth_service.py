"""认证服务 (Auth Service)

Sprint 3 — Task 3.2
严格依据 SRS §4.1、CODE_WIKI §6、Sprint 2 Frozen API、Sprint 3 Task 3.1 Schemas。

提供用户认证、密码修改、当前用户信息查询等业务逻辑。

公开 API:
    - login(db, username, password) -> LoginResponse
    - change_password(db, user_id, old_password, new_password) -> None
    - get_current_user_info(db, user_id) -> UserResponse

必须调用 Sprint 2 已冻结 API（禁止重复实现）:
    - verify_password() / hash_password() / create_access_token()
    - decode_access_token() / check_permission() / is_admin()

使用方式:
    from server.services.auth_service import AuthService

    auth = AuthService()
    response = auth.login(db, username="admin", password="admin123")
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from server.core.exceptions import (
    AuthenticationException,
    NotFoundException,
    PermissionDeniedException,
)
from server.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from server.enums.action_type import ActionType
from server.models import SystemLog, User
from server.schemas.user_schema import LoginResponse, UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务。

    提供登录、密码修改、用户信息查询等认证相关业务逻辑。
    所有安全能力（JWT、bcrypt、权限检查）均调用 Sprint 2 已冻结 API。
    """

    # ============================================================
    # 公开 API
    # ============================================================

    def login(
        self,
        db: Session,
        *,
        username: str,
        password: str,
    ) -> LoginResponse:
        """用户登录认证。

        流程:
            ① 查询用户（按 username）
            ② 检查用户是否禁用
            ③ 校验密码（verify_password）
            ④ 创建 JWT（create_access_token）
            ⑤ 返回 LoginResponse

        Args:
            db: 数据库会话。
            username: 登录用户名。
            password: 明文密码。

        Returns:
            LoginResponse: 包含 access_token、token_type、user。

        Raises:
            AuthenticationException: 用户不存在或密码错误。
            PermissionDeniedException: 用户已被禁用。
        """
        # ① 查询用户
        user = self._get_user(db, username=username)
        if user is None:
            raise AuthenticationException("用户名或密码错误")

        # ② 检查用户是否禁用
        if not user.is_active:
            raise PermissionDeniedException(
                "用户已被禁用，请联系管理员",
                detail={"user_id": user.id, "username": user.username},
            )

        # ③ 校验密码
        if not verify_password(password, user.password_hash):
            raise AuthenticationException("用户名或密码错误")

        # ④ 创建 JWT
        role_names = [role.name for role in user.roles]
        primary_role = role_names[0] if role_names else "viewer"

        token = create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "role": primary_role,
                "roles": role_names,
            }
        )

        # ⑤ 返回 LoginResponse
        return self._build_login_response(token, user)

    def change_password(
        self,
        db: Session,
        *,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> None:
        """修改用户密码。

        流程:
            ① 查询用户
            ② 验证旧密码（verify_password）
            ③ 哈希新密码（hash_password）
            ④ 更新 password_hash
            ⑤ 提交事务
            ⑥ 写入 SystemLog（CHANGE_PASSWORD）

        Args:
            db: 数据库会话。
            user_id: 用户 ID。
            old_password: 当前密码（验证用）。
            new_password: 新密码（bcrypt 哈希后存储）。

        Raises:
            NotFoundException: 用户不存在。
            AuthenticationException: 旧密码错误。
        """
        # ① 查询用户
        user = self._get_user(db, user_id=user_id)
        if user is None:
            raise NotFoundException(
                "用户不存在",
                detail={"user_id": user_id},
            )

        # ② 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise AuthenticationException("原密码错误")

        # ③ 哈希新密码
        new_hash = hash_password(new_password)

        # ④ 更新 password_hash
        user.password_hash = new_hash

        try:
            # ⑤ 提交事务
            db.commit()

            # ⑥ 写入 SystemLog
            log_entry = SystemLog(
                user_id=user_id,
                action=ActionType.UPDATE,
                target_type="User",
                target_id=user_id,
                changes={"field": "password_hash"},
            )
            db.add(log_entry)
            db.commit()

            logger.info("密码修改成功: user_id=%d", user_id)

        except Exception:
            db.rollback()
            logger.exception("密码修改失败: user_id=%d", user_id)
            raise

    def get_current_user_info(
        self,
        db: Session,
        *,
        user_id: int,
    ) -> UserResponse:
        """获取当前用户信息。

        Args:
            db: 数据库会话。
            user_id: 用户 ID。

        Returns:
            UserResponse: 用户信息（不含 password_hash）。

        Raises:
            NotFoundException: 用户不存在。
        """
        user = self._get_user(db, user_id=user_id)
        if user is None:
            raise NotFoundException(
                "用户不存在",
                detail={"user_id": user_id},
            )

        return UserResponse.model_validate(user)

    # ============================================================
    # 私有方法
    # ============================================================

    def _get_user(
        self,
        db: Session,
        *,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
    ) -> Optional[User]:
        """查询用户（按 ID 或用户名）。

        Args:
            db: 数据库会话。
            user_id: 用户 ID（可选）。
            username: 用户名（可选）。

        Returns:
            User ORM 实例，不存在时返回 None。
        """
        query = db.query(User)

        if user_id is not None:
            query = query.filter(User.id == user_id)
        elif username is not None:
            query = query.filter(User.username == username)
        else:
            return None

        return query.first()

    def _validate_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        """验证密码（内部委托给 security.verify_password）。

        Args:
            plain_password: 明文密码。
            hashed_password: bcrypt 哈希。

        Returns:
            True 如果匹配。
        """
        return verify_password(plain_password, hashed_password)

    def _build_login_response(
        self,
        token: str,
        user: User,
    ) -> LoginResponse:
        """构建登录响应。

        Args:
            token: JWT 访问令牌。
            user: User ORM 实例。

        Returns:
            LoginResponse: 包含 token、token_type、user 信息。
        """
        user_response = UserResponse.model_validate(user)
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=user_response,
        )


__all__ = [
    "AuthService",
]