"""去向服务 (Dispatch Service)

Sprint 2 — Task 2.9
严格依据 DB_DESIGN.md、SRS.md、CODE_WIKI.md §6.6.3。

提供工件去向记录的完整业务逻辑，包括：
    - 创建去向记录（创建 Dispatch + 状态流转 GRINDING → DISPATCHED）
    - 查询去向
    - 修改去向
    - 删除去向（软删除，仅管理员）
    - 所有写操作自动记录 SystemLog

权限规则（依据 CODE_WIKI §6.6.3）：
    - 创建去向: 任意具有 Dispatch 权限的 Technician 或 Administrator
    - 修改去向: Dispatch.created_by 或 Administrator
    - 删除去向: 仅 Administrator

状态流转：
    process_status: GRINDING → DISPATCHED（创建去向）
    result_status:  保持 PASSED

异常体系：
    使用 Task 2.1 冻结异常类。

使用方式:
    from server.services.dispatch_service import DispatchService

    service = DispatchService()
    dispatch = service.create_dispatch(db, task_id=1, destination="客户A", ...)
"""

import logging
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from server.core.security import has_permission
from server.enums import (
    ActionType,
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
)
from server.models import (
    Dispatch,
    SystemLog,
    TrialTask,
    User,
)

logger = logging.getLogger(__name__)


# ============================================================
# DispatchService
# ============================================================


class DispatchService:
    """工件去向业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    """

    # ============================================================
    # 创建去向
    # ============================================================

    def create_dispatch(
        self,
        db: Session,
        *,
        task_id: int,
        destination: str,
        dispatch_date: datetime,
        remark: Optional[str],
        current_user: User,
    ) -> Dispatch:
        """创建工件去向记录。

        业务流程:
            1. 查询 TrialTask，验证 result_status == PASSED 且 process_status == GRINDING
            2. 权限检查：Technician（dispatch:write）或 Administrator
            3. 创建 Dispatch（direction=destination, operator_id=current_user.id）
            4. 更新 TrialTask.process_status: GRINDING → DISPATCHED
            5. 写入 SystemLog（CREATE_DISPATCH）
            6. commit 并返回 Dispatch

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            destination: 去向描述（对应 ORM direction）。
            dispatch_date: 去向日期。
            remark: 备注信息（记录于 SystemLog，Dispatch ORM 暂无 remark 字段）。
            current_user: 当前登录用户。

        Returns:
            新创建的 Dispatch 实例。

        Raises:
            NotFoundException: 任务不存在或已删除。
            BusinessLogicException: 状态不符合条件（需 result_status=PASSED 且 process_status=GRINDING）。
            PermissionDeniedException: 用户无 Dispatch 权限。
        """
        task = self._get_task_or_raise(db, task_id)

        # ① 状态检查：result_status == PASSED 且 process_status == GRINDING
        if task.result_status != TrialTaskResultStatus.PASSED:
            raise BusinessLogicException(
                f"仅检测合格的任务可填写去向，当前结果: {task.result_status.value}",
                detail={
                    "task_id": task_id,
                    "current_result": task.result_status.value,
                },
            )
        if task.process_status != TrialTaskProcessStatus.GRINDING:
            raise BusinessLogicException(
                f"仅试磨中状态的任务可填写去向，当前状态: {task.process_status.value}",
                detail={
                    "task_id": task_id,
                    "current_status": task.process_status.value,
                },
            )

        # ② 权限检查：Technician（dispatch:write）或 Administrator
        self._check_dispatch_permission(current_user)

        try:
            # ③ 创建 Dispatch
            dispatch = Dispatch(
                task_id=task_id,
                direction=destination,
                dispatch_date=dispatch_date,
                operator_id=current_user.id,
                created_by=current_user.id,
            )
            db.add(dispatch)
            db.flush()

            # ④ 更新任务状态: GRINDING → DISPATCHED
            task.process_status = TrialTaskProcessStatus.DISPATCHED
            task.updated_by = current_user.id

            # ⑧ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.CREATE,
                target_type="Dispatch",
                target_id=dispatch.id,
                changes={
                    "task_id": task_id,
                    "task_no": task.task_no,
                    "destination": destination,
                    "dispatch_date": dispatch_date.isoformat(),
                    "remark": remark,
                    "from_status": TrialTaskProcessStatus.GRINDING.value,
                    "to_status": TrialTaskProcessStatus.DISPATCHED.value,
                    "action": "CREATE_DISPATCH",
                },
            )

            db.commit()
            logger.info(
                "去向创建成功: task_no=%s, dispatch_id=%s, destination=%s, user=%s",
                task.task_no, dispatch.id, destination, current_user.username,
            )
            return dispatch

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 查询去向
    # ============================================================

    def get_dispatch(self, db: Session, task_id: int) -> Dispatch:
        """根据任务 ID 查询去向记录。

        自动过滤 is_deleted=True 的记录。

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。

        Returns:
            Dispatch 实例。

        Raises:
            NotFoundException: 去向记录不存在或已删除。
        """
        dispatch = (
            db.query(Dispatch)
            .filter(
                Dispatch.task_id == task_id,
                Dispatch.is_deleted == False,  # noqa: E712
            )
            .first()
        )
        if dispatch is None:
            raise NotFoundException(
                f"去向记录不存在: task_id={task_id}",
                detail={"task_id": task_id},
            )
        return dispatch

    # ============================================================
    # 修改去向
    # ============================================================

    def update_dispatch(
        self,
        db: Session,
        task_id: int,
        **kwargs: Any,
    ) -> Dispatch:
        """修改去向记录。

        权限规则:
            - Administrator 或 Dispatch.created_by 可修改

        允许修改的字段:
            - direction: 去向描述
            - dispatch_date: 去向日期
            - operator_id: 操作人

        禁止修改的字段:
            - task_id
            - created_by
            - created_at

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            **kwargs: 要修改的字段键值对（需包含 current_user）。

        Returns:
            更新后的 Dispatch 实例。

        Raises:
            NotFoundException: 去向记录不存在。
            PermissionDeniedException: 非 created_by 且非管理员。
            BusinessLogicException: 尝试修改禁止字段或传入未知字段。
        """
        dispatch = self.get_dispatch(db, task_id)

        # 提取 current_user（不从 kwargs 写入 ORM）
        current_user = kwargs.pop("current_user", None)

        # ⑥ 权限检查：Administrator 或 created_by
        self._check_creator_or_admin(dispatch, current_user, "修改去向")

        # 禁止修改的字段
        forbidden = {"task_id", "created_by", "created_at"}
        invalid = forbidden & set(kwargs.keys())
        if invalid:
            raise BusinessLogicException(
                f"禁止修改以下字段: {', '.join(sorted(invalid))}",
                detail={"forbidden_fields": sorted(invalid)},
            )

        # 允许修改的字段
        allowed = {"direction", "dispatch_date", "operator_id"}

        changes = {}
        for key, value in kwargs.items():
            if key not in allowed:
                raise BusinessLogicException(
                    f"未知字段: {key}，允许修改的字段: {', '.join(sorted(allowed))}",
                    detail={"unknown_field": key, "allowed_fields": sorted(allowed)},
                )
            old_value = getattr(dispatch, key, None)
            if old_value != value:
                changes[key] = {"old": str(old_value), "new": str(value)}
                setattr(dispatch, key, value)

        if not changes:
            return dispatch

        try:
            dispatch.updated_by = current_user.id if current_user else None
            db.flush()

            # ⑧ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id if current_user else 0,
                action=ActionType.UPDATE,
                target_type="Dispatch",
                target_id=dispatch.id,
                changes={
                    "task_id": task_id,
                    "updated_fields": changes,
                    "action": "UPDATE_DISPATCH",
                },
            )

            db.commit()
            logger.info(
                "去向修改成功: task_id=%s, fields=%s",
                task_id, list(changes.keys()),
            )
            return dispatch

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 删除去向（软删除）
    # ============================================================

    def delete_dispatch(
        self,
        db: Session,
        task_id: int,
        current_user: User,
    ) -> None:
        """软删除去向记录。

        ⑦ 仅 Administrator 可执行删除操作。

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            current_user: 当前登录用户。

        Raises:
            NotFoundException: 去向记录不存在。
            PermissionDeniedException: 非管理员用户。
        """
        dispatch = self.get_dispatch(db, task_id)

        # ⑦ 管理员权限检查
        user_role_names = {role.name for role in current_user.roles}
        if "administrator" not in user_role_names:
            raise PermissionDeniedException(
                "仅管理员可删除去向记录",
                detail={
                    "task_id": task_id,
                    "user_roles": sorted(user_role_names),
                },
            )

        try:
            dispatch.is_deleted = True
            dispatch.updated_by = current_user.id
            db.flush()

            # ⑧ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.DELETE,
                target_type="Dispatch",
                target_id=dispatch.id,
                changes={
                    "task_id": task_id,
                    "action": "DELETE_DISPATCH",
                },
            )

            db.commit()
            logger.info(
                "去向记录已删除: task_id=%s, user=%s",
                task_id, current_user.username,
            )

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    @staticmethod
    def _get_task_or_raise(db: Session, task_id: int) -> TrialTask:
        """获取任务，不存在或已删除时抛出 NotFoundException。

        Args:
            db: 数据库会话。
            task_id: 任务 ID。

        Returns:
            TrialTask 实例。

        Raises:
            NotFoundException: 任务不存在或已删除。
        """
        task = (
            db.query(TrialTask)
            .filter(
                TrialTask.id == task_id,
                TrialTask.is_deleted == False,  # noqa: E712
            )
            .first()
        )
        if task is None:
            raise NotFoundException(
                f"任务不存在: id={task_id}",
                detail={"task_id": task_id},
            )
        return task

    @staticmethod
    def _check_dispatch_permission(user: User) -> None:
        """检查用户是否具有去向操作权限。

        允许：Administrator 或具有 dispatch:write 权限的角色。

        Args:
            user: 当前用户。

        Raises:
            PermissionDeniedException: 用户无去向操作权限。
        """
        user_role_names = {role.name for role in user.roles}

        # Administrator 拥有全部权限
        if "administrator" in user_role_names:
            return

        # 检查是否有角色拥有 dispatch:write 权限
        for role_name in user_role_names:
            if has_permission(role_name, "dispatch:write"):
                return

        raise PermissionDeniedException(
            "您没有去向操作权限，需要 dispatch:write 权限",
            detail={
                "user_roles": sorted(user_role_names),
                "required_permission": "dispatch:write",
            },
        )

    @staticmethod
    def _check_creator_or_admin(
        dispatch: Dispatch,
        user: User,
        action: str,
    ) -> None:
        """检查用户是否为去向记录创建人或管理员。

        Args:
            dispatch: 去向记录。
            user: 当前用户。
            action: 操作名称（用于异常消息）。

        Raises:
            PermissionDeniedException: 非 created_by 且非管理员。
        """
        user_role_names = {role.name for role in user.roles}

        # Administrator 可以执行所有操作
        if "administrator" in user_role_names:
            return

        # 检查是否为创建人
        if dispatch.created_by == user.id:
            return

        raise PermissionDeniedException(
            f"仅去向记录创建人或管理员可{action}",
            detail={
                "created_by": dispatch.created_by,
                "current_user_id": user.id,
                "action": action,
            },
        )

    @staticmethod
    def _log_action(
        db: Session,
        user_id: int,
        action: ActionType,
        target_type: str,
        target_id: int,
        changes: Optional[dict[str, Any]] = None,
    ) -> None:
        """写入系统操作日志。

        Args:
            db: 数据库会话。
            user_id: 操作用户 ID。
            action: 操作类型。
            target_type: 操作对象类型。
            target_id: 操作对象 ID。
            changes: 变更内容（可选）。
        """
        log_entry = SystemLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            changes=changes,
        )
        db.add(log_entry)
        db.flush()


__all__ = [
    "DispatchService",
]