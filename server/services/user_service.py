"""用户服务 (User Service)

Sprint 3 — Task 3.4
严格依据 SRS §4.1、CODE_WIKI、Sprint 1 ORM、Sprint 2 Frozen API、Sprint 3 Task 3.1 Schemas。

提供用户 CRUD 与角色分配业务逻辑。

公开 API:
    - create_user(db, *, user_data, current_user, role_ids=None) -> User
    - get_user(db, *, user_id) -> User
    - list_users(db, *, page, page_size, **filters) -> (items, total)
    - update_user(db, *, user_id, user_data, current_user, role_ids=None) -> User
    - delete_user(db, *, user_id, current_user) -> None
    - assign_roles(db, *, user_id, role_ids, current_user) -> User

必须调用 Sprint 2 已冻结 API（禁止重复实现）:
    - hash_password() / verify_password()
    - has_permission() / check_permission()
    - ROLE_PERMISSION_MAP

使用方式:
    from server.services.user_service import UserService

    service = UserService()
    user = service.create_user(db, user_data=data, current_user=admin, role_ids=[1, 2])
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    DuplicateException,
    NotFoundException,
    PermissionDeniedException,
)
from server.core.security import has_permission, hash_password
from server.enums.action_type import ActionType
from server.models import Role, SystemLog, User, user_roles
from server.schemas.user_schema import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """用户服务。

    提供用户创建、查询、更新、删除、角色分配等业务逻辑。
    所有密码处理委托给 security.hash_password()。
    所有权限检查委托给 security.has_permission()。
    """

    # ============================================================
    # 公开 API
    # ============================================================

    def create_user(
        self,
        db: Session,
        *,
        user_data: UserCreate,
        current_user: User,
        role_ids: Optional[list[int]] = None,
    ) -> User:
        """创建用户。

        流程:
            ① 检查权限（仅 Administrator）
            ② 检查 username 唯一性
            ③ 校验角色存在性
            ④ 哈希密码（hash_password）
            ⑤ 创建 User ORM
            ⑥ 分配角色
            ⑦ 提交事务
            ⑧ 写入 SystemLog（CREATE_USER）

        Args:
            db: 数据库会话。
            user_data: 用户创建数据（UserCreate Schema）。
            current_user: 当前登录用户（用于权限检查与 created_by）。
            role_ids: 角色 ID 列表（可选）。

        Returns:
            User ORM 实例。

        Raises:
            PermissionDeniedException: 当前用户非管理员。
            DuplicateException: username 已存在。
            BusinessLogicException: 角色不存在。
        """
        # ① 权限检查
        self._check_admin(current_user, "user:write")

        # ② 检查 username 唯一性
        existing = db.query(User).filter(User.username == user_data.username).first()
        if existing is not None:
            raise DuplicateException(
                f"用户名 '{user_data.username}' 已存在",
                detail={"username": user_data.username},
            )

        # ③ 校验角色
        roles = self._get_roles(db, role_ids or [])

        # ④ 哈希密码
        hashed = hash_password(user_data.password)

        # ⑤ 创建 User ORM
        user = User(
            username=user_data.username,
            password_hash=hashed,
            real_name=user_data.real_name,
            phone=user_data.phone,
            is_active=True,
            created_by=current_user.id,
        )
        db.add(user)
        db.flush()

        # ⑥ 分配角色
        for role in roles:
            db.execute(
                user_roles.insert().values(
                    user_id=user.id,
                    role_id=role.id,
                )
            )
        db.flush()

        try:
            # ⑦ 提交事务
            db.commit()

            # ⑧ 写入 SystemLog
            self._write_log(
                db,
                operator=current_user,
                action=ActionType.CREATE,
                target_type="User",
                target_id=user.id,
                changes={
                    "username": user_data.username,
                    "real_name": user_data.real_name,
                    "role_ids": role_ids,
                },
            )

            # 刷新以加载关联关系
            db.refresh(user)
            logger.info("用户创建成功: user_id=%d, username=%s", user.id, user.username)
            return user

        except Exception:
            db.rollback()
            logger.exception("用户创建失败: username=%s", user_data.username)
            raise

    def get_user(
        self,
        db: Session,
        *,
        user_id: int,
    ) -> User:
        """根据 ID 查询用户。

        过滤 is_deleted=False 的记录。

        Args:
            db: 数据库会话。
            user_id: 用户 ID。

        Returns:
            User ORM 实例。

        Raises:
            NotFoundException: 用户不存在或已删除。
        """
        user = (
            db.query(User)
            .filter(User.id == user_id, User.is_deleted == False)
            .first()
        )
        if user is None:
            raise NotFoundException(
                "用户不存在",
                detail={"user_id": user_id},
            )
        return user

    def list_users(
        self,
        db: Session,
        *,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        real_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        role: Optional[str] = None,
    ) -> tuple[list[User], int]:
        """用户列表查询（分页 + 筛选）。

        所有查询过滤 is_deleted=False。

        Args:
            db: 数据库会话。
            page: 页码（从 1 开始）。
            page_size: 每页条数。
            username: 用户名模糊查询（可选）。
            real_name: 真实姓名模糊查询（可选）。
            is_active: 启用状态筛选（可选）。
            role: 角色名筛选（可选）。

        Returns:
            (items, total): 用户列表与总数。
        """
        query = db.query(User).filter(User.is_deleted == False)

        # 筛选条件
        if username:
            query = query.filter(User.username.like(f"%{username}%"))
        if real_name:
            query = query.filter(User.real_name.like(f"%{real_name}%"))
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if role:
            query = (
                query.join(user_roles, User.id == user_roles.c.user_id)
                .join(Role, Role.id == user_roles.c.role_id)
                .filter(Role.name == role)
            )

        # 总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        items = query.order_by(User.id.desc()).offset(offset).limit(page_size).all()

        return items, total

    def update_user(
        self,
        db: Session,
        *,
        user_id: int,
        user_data: UserUpdate,
        current_user: User,
        role_ids: Optional[list[int]] = None,
    ) -> User:
        """更新用户信息。

        允许修改: real_name, phone, is_active, roles。
        禁止修改: username, password_hash, created_at, created_by。

        流程:
            ① 检查权限（仅 Administrator）
            ② 查询用户（过滤已删除）
            ③ 更新允许的字段
            ④ 更新角色（如传入）
            ⑤ 提交事务
            ⑥ 写入 SystemLog（UPDATE_USER）

        Args:
            db: 数据库会话。
            user_id: 目标用户 ID。
            user_data: 更新数据（UserUpdate Schema）。
            current_user: 当前登录用户。
            role_ids: 新角色 ID 列表（可选，传入时覆盖）。

        Returns:
            User ORM 实例。

        Raises:
            PermissionDeniedException: 当前用户非管理员。
            NotFoundException: 用户不存在。
            BusinessLogicException: 角色不存在。
        """
        # ① 权限检查
        self._check_admin(current_user, "user:write")

        # ② 查询用户
        user = self.get_user(db, user_id=user_id)

        # ③ 记录变更
        changes = {}

        # 仅更新允许的字段
        if user_data.real_name is not None:
            changes["real_name"] = {"old": user.real_name, "new": user_data.real_name}
            user.real_name = user_data.real_name

        if user_data.phone is not None:
            changes["phone"] = {"old": user.phone, "new": user_data.phone}
            user.phone = user_data.phone

        if user_data.is_active is not None:
            changes["is_active"] = {"old": user.is_active, "new": user_data.is_active}
            user.is_active = user_data.is_active

        # ④ 更新角色
        if role_ids is not None:
            roles = self._get_roles(db, role_ids)
            # 清除旧关联
            db.execute(
                user_roles.delete().where(user_roles.c.user_id == user_id)
            )
            db.flush()
            # 添加新关联
            for role in roles:
                db.execute(
                    user_roles.insert().values(
                        user_id=user_id,
                        role_id=role.id,
                    )
                )
            changes["roles"] = {"new": role_ids}

        try:
            # ⑤ 提交事务
            db.commit()

            # ⑥ 写入 SystemLog
            if changes:
                self._write_log(
                    db,
                    operator=current_user,
                    action=ActionType.UPDATE,
                    target_type="User",
                    target_id=user_id,
                    changes=changes,
                )

            db.refresh(user)
            logger.info("用户更新成功: user_id=%d", user_id)
            return user

        except Exception:
            db.rollback()
            logger.exception("用户更新失败: user_id=%d", user_id)
            raise

    def delete_user(
        self,
        db: Session,
        *,
        user_id: int,
        current_user: User,
    ) -> None:
        """软删除用户。

        仅 Administrator 可删除，管理员不能删除自己。

        流程:
            ① 检查权限（仅 Administrator）
            ② 禁止管理员删除自己
            ③ 查询用户（过滤已删除）
            ④ 设置 is_deleted=True
            ⑤ 提交事务
            ⑥ 写入 SystemLog（DELETE_USER）

        Args:
            db: 数据库会话。
            user_id: 目标用户 ID。
            current_user: 当前登录用户。

        Raises:
            PermissionDeniedException: 当前用户非管理员。
            BusinessLogicException: 管理员尝试删除自己。
            NotFoundException: 用户不存在。
        """
        # ① 权限检查
        self._check_admin(current_user, "user:delete")

        # ② 禁止管理员删除自己
        if user_id == current_user.id:
            raise BusinessLogicException(
                "管理员不能删除自己",
                detail={"user_id": user_id},
            )

        # ③ 查询用户
        user = self.get_user(db, user_id=user_id)

        # ④ 软删除
        user.is_deleted = True

        try:
            # ⑤ 提交事务
            db.commit()

            # ⑥ 写入 SystemLog
            self._write_log(
                db,
                operator=current_user,
                action=ActionType.DELETE,
                target_type="User",
                target_id=user_id,
                changes={"username": user.username},
            )

            logger.info("用户删除成功: user_id=%d, username=%s", user_id, user.username)

        except Exception:
            db.rollback()
            logger.exception("用户删除失败: user_id=%d", user_id)
            raise

    def assign_roles(
        self,
        db: Session,
        *,
        user_id: int,
        role_ids: list[int],
        current_user: User,
    ) -> User:
        """重新分配用户角色（覆盖原有关联）。

        流程:
            ① 检查权限（仅 Administrator）
            ② 校验角色存在性
            ③ 查询用户
            ④ 清除旧角色关联
            ⑤ 添加新角色关联
            ⑥ 提交事务
            ⑦ 写入 SystemLog（ASSIGN_ROLE）

        Args:
            db: 数据库会话。
            user_id: 目标用户 ID。
            role_ids: 新角色 ID 列表。
            current_user: 当前登录用户。

        Returns:
            User ORM 实例（含刷新后的角色）。

        Raises:
            PermissionDeniedException: 当前用户非管理员。
            BusinessLogicException: 角色不存在。
            NotFoundException: 用户不存在。
        """
        # ① 权限检查
        self._check_admin(current_user, "user:write")

        # ② 校验角色
        roles = self._get_roles(db, role_ids)

        # ③ 查询用户
        user = self.get_user(db, user_id=user_id)

        # ④ 清除旧关联
        db.execute(
            user_roles.delete().where(user_roles.c.user_id == user_id)
        )
        db.flush()

        # ⑤ 添加新关联
        for role in roles:
            db.execute(
                user_roles.insert().values(
                    user_id=user_id,
                    role_id=role.id,
                )
            )
        db.flush()

        try:
            # ⑥ 提交事务
            db.commit()

            # ⑦ 写入 SystemLog
            self._write_log(
                db,
                operator=current_user,
                action=ActionType.UPDATE,
                target_type="User",
                target_id=user_id,
                changes={
                    "action": "ASSIGN_ROLE",
                    "role_ids": role_ids,
                },
            )

            db.refresh(user)
            logger.info(
                "角色分配成功: user_id=%d, role_ids=%s", user_id, role_ids
            )
            return user

        except Exception:
            db.rollback()
            logger.exception("角色分配失败: user_id=%d", user_id)
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    def _check_admin(self, current_user: User, permission: str) -> None:
        """检查当前用户是否拥有指定权限。

        遍历用户的所有角色，任一角色拥有权限即通过。

        Args:
            current_user: 当前用户。
            permission: 权限代码（如 "user:write"）。

        Raises:
            PermissionDeniedException: 所有角色均无此权限。
        """
        role_names = [role.name for role in current_user.roles]
        for rn in role_names:
            if has_permission(rn, permission):
                return

        raise PermissionDeniedException(
            f"仅管理员可执行此操作（需要权限 '{permission}'）",
            detail={
                "required_permission": permission,
                "user_roles": role_names,
            },
        )

    def _get_roles(self, db: Session, role_ids: list[int]) -> list[Role]:
        """批量查询角色并校验存在性。

        Args:
            db: 数据库会话。
            role_ids: 角色 ID 列表。

        Returns:
            Role ORM 列表。

        Raises:
            BusinessLogicException: 部分角色不存在。
        """
        if not role_ids:
            return []

        roles = (
            db.query(Role)
            .filter(Role.id.in_(role_ids), Role.is_deleted == False)
            .all()
        )

        if len(roles) != len(role_ids):
            found_ids = {r.id for r in roles}
            missing = set(role_ids) - found_ids
            raise BusinessLogicException(
                f"角色不存在: {sorted(missing)}",
                detail={"missing_role_ids": sorted(missing)},
            )

        return roles

    def _write_log(
        self,
        db: Session,
        *,
        operator: User,
        action: ActionType,
        target_type: str,
        target_id: int,
        changes: Optional[dict] = None,
    ) -> None:
        """写入系统日志。

        Args:
            db: 数据库会话。
            operator: 操作人用户。
            action: 操作类型。
            target_type: 操作对象类型。
            target_id: 操作对象 ID。
            changes: 变更内容（可选）。
        """
        log_entry = SystemLog(
            user_id=operator.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            changes=changes,
        )
        db.add(log_entry)
        db.commit()


__all__ = [
    "UserService",
]