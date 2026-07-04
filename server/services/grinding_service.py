"""试磨服务 (Grinding Service)

Sprint 2 — Task 2.7
严格依据 DB_DESIGN.md、SRS.md、CODE_WIKI.md §6.6.3。

提供试磨记录的完整业务逻辑，包括：
    - 开始试磨（创建 GrindingRecord + 状态流转 RECEIVED → GRINDING）
    - 完成试磨（写入结果 + 绑定附件 + 状态流转 PENDING → PASSED/FAILED）
    - 查询试磨
    - 修改试磨
    - 删除试磨（软删除，仅管理员）
    - 所有写操作自动记录 SystemLog

状态流转：
    process_status: RECEIVED → GRINDING（开始试磨）
    result_status:  PENDING → PASSED/FAILED（完成试磨）

权限规则（依据 CODE_WIKI §6.6.3）：
    - 开始试磨: 任意具有 Grinding 权限的 Technician 或 Administrator
    - 完成试磨: GrindingRecord.operator_id 或 Administrator
    - 修改试磨: GrindingRecord.operator_id 或 Administrator
    - 删除试磨: 仅 Administrator

异常体系：
    使用 Task 2.1 冻结异常类。

使用方式:
    from server.services.grinding_service import GrindingService

    service = GrindingService()
    record = service.start_grinding(db, task_id=1, current_user=user)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from server.core.security import has_permission, is_admin
from server.enums import (
    ActionType,
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
)
from server.models import (
    Attachment,
    GrindingRecord,
    SystemLog,
    TrialTask,
    User,
)

logger = logging.getLogger(__name__)


# ============================================================
# 输入 Schema
# ============================================================


@dataclass
class GrindingUpdate:
    """试磨修改输入。

    允许修改的字段（与 ORM 字段名一致）:
        machine_type: 试磨机型。
        wheel_type: 砂轮型号。
        params: 加工参数。
        end_time: 完成时间。
        fail_reason: 失败原因。
        image_paths: 试磨图片路径（JSON 数组文本）。

    禁止修改的字段:
        operator_id, start_time, task_id
    """

    machine_type: Optional[str] = None
    wheel_type: Optional[str] = None
    params: Optional[str] = None
    end_time: Optional[datetime] = None
    fail_reason: Optional[str] = None
    image_paths: Optional[str] = None


# ============================================================
# GrindingService
# ============================================================


class GrindingService:
    """试磨业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    """

    # ============================================================
    # 开始试磨
    # ============================================================

    def start_grinding(
        self,
        db: Session,
        *,
        task_id: int,
        current_user: User,
    ) -> GrindingRecord:
        """开始试磨。

        业务流程:
            1. 查询 TrialTask，验证 process_status == RECEIVED
            2. 权限检查：Technician（grinding:write）或 Administrator
            3. 创建 GrindingRecord（operator_id=current_user.id, start_time=now()）
            4. 更新 TrialTask.process_status: RECEIVED → GRINDING
            5. 写入 SystemLog（START_GRINDING）
            6. commit 并返回 GrindingRecord

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            current_user: 当前登录用户。

        Returns:
            新创建的 GrindingRecord 实例。

        Raises:
            NotFoundException: 任务不存在或已删除。
            BusinessLogicException: 任务状态不是 RECEIVED。
            PermissionDeniedException: 用户无 Grinding 权限。
        """
        task = self._get_task_or_raise(db, task_id)

        # ① 状态检查：仅 RECEIVED 可开始试磨
        if task.process_status != TrialTaskProcessStatus.RECEIVED:
            raise BusinessLogicException(
                f"仅已收件状态的任务可开始试磨，当前状态: {task.process_status.value}",
                detail={
                    "task_id": task_id,
                    "current_status": task.process_status.value,
                },
            )

        # ② 权限检查：Technician（grinding:write）或 Administrator
        self._check_grinding_permission(current_user)

        try:
            # ③ 创建 GrindingRecord
            now = datetime.now()
            grinding = GrindingRecord(
                task_id=task_id,
                operator_id=current_user.id,
                start_time=now,
                created_by=current_user.id,
            )
            db.add(grinding)
            db.flush()

            # ④ 更新任务状态: RECEIVED → GRINDING
            task.process_status = TrialTaskProcessStatus.GRINDING
            task.updated_by = current_user.id

            # ⑤ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.STATUS_CHANGE,
                target_type="GrindingRecord",
                target_id=grinding.id,
                changes={
                    "task_id": task_id,
                    "task_no": task.task_no,
                    "operator_id": current_user.id,
                    "from_status": TrialTaskProcessStatus.RECEIVED.value,
                    "to_status": TrialTaskProcessStatus.GRINDING.value,
                    "action": "START_GRINDING",
                },
            )

            db.commit()
            logger.info(
                "开始试磨成功: task_no=%s, grinding_id=%s, operator=%s",
                task.task_no, grinding.id, current_user.username,
            )
            return grinding

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 完成试磨
    # ============================================================

    def finish_grinding(
        self,
        db: Session,
        *,
        task_id: int,
        machine_model: Optional[str],
        wheel_model: Optional[str],
        process_parameter: Optional[str],
        result_status: TrialTaskResultStatus,
        failure_reason: Optional[str],
        attachment_ids: list[int],
        current_user: User,
    ) -> GrindingRecord:
        """完成试磨。

        业务流程:
            1. 查询 GrindingRecord（is_deleted=False）
            2. 权限检查：operator_id 或 Administrator
            3. 验证 attachment_ids（全部存在且属于当前任务）
            4. 写入 finish_time、machine_model、wheel_model、process_parameter
            5. 设置 TrialTask.result_status（PASSED/FAILED）
            6. 失败时 failure_reason 必填
            7. 绑定附件路径到 image_paths
            8. 写入 SystemLog（FINISH_GRINDING）
            9. commit 并返回 GrindingRecord

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            machine_model: 试磨机型（对应 ORM machine_type）。
            wheel_model: 砂轮型号（对应 ORM wheel_type）。
            process_parameter: 加工参数（对应 ORM params）。
            result_status: 试磨结果状态（PASSED 或 FAILED）。
            failure_reason: 失败原因（仅 result_status=FAILED 时填写）。
            attachment_ids: 已有附件 ID 列表。
            current_user: 当前登录用户。

        Returns:
            更新后的 GrindingRecord 实例。

        Raises:
            NotFoundException: 试磨记录不存在或已删除。
            PermissionDeniedException: 非 operator 且非管理员。
            BusinessLogicException: 参数校验失败。
        """
        grinding = self.get_grinding(db, task_id)
        task = self._get_task_or_raise(db, task_id)

        # ⑤ 权限检查：仅 operator 或 Administrator
        self._check_operator_or_admin(grinding, current_user, "完成试磨")

        # ⑥ 验证 result_status
        if result_status not in (
            TrialTaskResultStatus.PASSED,
            TrialTaskResultStatus.FAILED,
        ):
            raise BusinessLogicException(
                f"无效的结果状态: {result_status.value}，仅允许 passed 或 failed",
                detail={"result_status": result_status.value},
            )

        # ⑦ 失败时 failure_reason 必填
        if result_status == TrialTaskResultStatus.FAILED:
            if not failure_reason:
                raise BusinessLogicException(
                    "试磨失败时必须填写失败原因",
                    detail={"task_id": task_id, "result_status": "failed"},
                )

        # ⑧ 验证 attachment_ids：全部存在且属于当前任务
        image_paths_json = None
        if attachment_ids:
            image_paths_json = self._validate_and_collect_attachments(
                db, task_id, attachment_ids
            )

        try:
            now = datetime.now()

            # 写入试磨结果
            grinding.machine_type = machine_model
            grinding.wheel_type = wheel_model
            grinding.params = process_parameter
            grinding.end_time = now
            grinding.fail_reason = failure_reason
            grinding.image_paths = image_paths_json
            grinding.updated_by = current_user.id

            # ⑦ 更新任务结果状态
            task.result_status = result_status
            if result_status == TrialTaskResultStatus.FAILED:
                task.failure_reason = failure_reason
            task.updated_by = current_user.id

            db.flush()

            # ⑬ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.STATUS_CHANGE,
                target_type="GrindingRecord",
                target_id=grinding.id,
                changes={
                    "task_id": task_id,
                    "task_no": task.task_no,
                    "result_status": result_status.value,
                    "machine_type": machine_model,
                    "wheel_type": wheel_model,
                    "attachment_count": len(attachment_ids),
                    "action": "FINISH_GRINDING",
                },
            )

            db.commit()
            logger.info(
                "完成试磨成功: task_no=%s, result=%s, operator=%s",
                task.task_no, result_status.value, current_user.username,
            )
            return grinding

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 查询试磨
    # ============================================================

    def get_grinding(self, db: Session, task_id: int) -> GrindingRecord:
        """根据任务 ID 查询试磨记录。

        自动过滤 is_deleted=True 的记录。

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。

        Returns:
            GrindingRecord 实例。

        Raises:
            NotFoundException: 试磨记录不存在或已删除。
        """
        grinding = (
            db.query(GrindingRecord)
            .filter(
                GrindingRecord.task_id == task_id,
                GrindingRecord.is_deleted == False,  # noqa: E712
            )
            .first()
        )
        if grinding is None:
            raise NotFoundException(
                f"试磨记录不存在: task_id={task_id}",
                detail={"task_id": task_id},
            )
        return grinding

    # ============================================================
    # 修改试磨
    # ============================================================

    def update_grinding(
        self,
        db: Session,
        task_id: int,
        **kwargs: Any,
    ) -> GrindingRecord:
        """修改试磨记录。

        权限规则:
            - 仅 GrindingRecord.operator_id 或 Administrator 可修改

        允许修改的字段:
            - machine_type: 试磨机型
            - wheel_type: 砂轮型号
            - params: 加工参数
            - end_time: 完成时间
            - fail_reason: 失败原因
            - image_paths: 试磨图片路径

        禁止修改的字段:
            - operator_id
            - start_time
            - task_id

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            **kwargs: 要修改的字段键值对。

        Returns:
            更新后的 GrindingRecord 实例。

        Raises:
            NotFoundException: 试磨记录不存在。
            PermissionDeniedException: 非 operator 且非管理员。
            BusinessLogicException: 尝试修改禁止字段或传入未知字段。
        """
        grinding = self.get_grinding(db, task_id)

        # ⑪ 权限检查：仅 operator 或 Administrator
        self._check_operator_or_admin(grinding, kwargs.get("current_user"), "修改试磨")

        # 提取 current_user（不从 kwargs 写入 ORM）
        current_user = kwargs.pop("current_user", None)

        # 禁止修改的字段
        forbidden = {"operator_id", "start_time", "task_id"}
        invalid = forbidden & set(kwargs.keys())
        if invalid:
            raise BusinessLogicException(
                f"禁止修改以下字段: {', '.join(sorted(invalid))}",
                detail={"forbidden_fields": sorted(invalid)},
            )

        # 允许修改的字段
        allowed = {
            "machine_type", "wheel_type", "params",
            "end_time", "fail_reason", "image_paths",
        }

        changes = {}
        for key, value in kwargs.items():
            if key not in allowed:
                raise BusinessLogicException(
                    f"未知字段: {key}，允许修改的字段: {', '.join(sorted(allowed))}",
                    detail={"unknown_field": key, "allowed_fields": sorted(allowed)},
                )
            old_value = getattr(grinding, key, None)
            if old_value != value:
                changes[key] = {"old": str(old_value), "new": str(value)}
                setattr(grinding, key, value)

        if not changes:
            return grinding

        try:
            grinding.updated_by = current_user.id if current_user else None
            db.flush()

            # ⑬ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id if current_user else 0,
                action=ActionType.UPDATE,
                target_type="GrindingRecord",
                target_id=grinding.id,
                changes={
                    "task_id": task_id,
                    "updated_fields": changes,
                    "action": "UPDATE_GRINDING",
                },
            )

            db.commit()
            logger.info(
                "试磨修改成功: task_id=%s, fields=%s",
                task_id, list(changes.keys()),
            )
            return grinding

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 删除试磨（软删除）
    # ============================================================

    def delete_grinding(
        self,
        db: Session,
        task_id: int,
        current_user: User,
    ) -> None:
        """软删除试磨记录。

        ⑫ 仅 Administrator 可执行删除操作。

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            current_user: 当前登录用户。

        Raises:
            NotFoundException: 试磨记录不存在。
            PermissionDeniedException: 非管理员用户。
        """
        grinding = self.get_grinding(db, task_id)

        # ⑫ 管理员权限检查
        user_role_names = {role.name for role in current_user.roles}
        if "administrator" not in user_role_names:
            raise PermissionDeniedException(
                "仅管理员可删除试磨记录",
                detail={
                    "task_id": task_id,
                    "user_roles": sorted(user_role_names),
                },
            )

        try:
            grinding.is_deleted = True
            grinding.updated_by = current_user.id
            db.flush()

            # ⑬ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.DELETE,
                target_type="GrindingRecord",
                target_id=grinding.id,
                changes={
                    "task_id": task_id,
                    "action": "DELETE_GRINDING",
                },
            )

            db.commit()
            logger.info(
                "试磨记录已删除: task_id=%s, user=%s",
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
    def _check_grinding_permission(user: User) -> None:
        """检查用户是否具有试磨权限。

        允许：Administrator 或具有 grinding:write 权限的角色。

        Args:
            user: 当前用户。

        Raises:
            PermissionDeniedException: 用户无试磨权限。
        """
        user_role_names = {role.name for role in user.roles}

        # Administrator 拥有全部权限
        if "administrator" in user_role_names:
            return

        # 检查是否有角色拥有 grinding:write 权限
        for role_name in user_role_names:
            if has_permission(role_name, "grinding:write"):
                return

        raise PermissionDeniedException(
            "您没有试磨操作权限，需要 grinding:write 权限",
            detail={
                "user_roles": sorted(user_role_names),
                "required_permission": "grinding:write",
            },
        )

    @staticmethod
    def _check_operator_or_admin(
        grinding: GrindingRecord,
        user: User,
        action: str,
    ) -> None:
        """检查用户是否为试磨操作人或管理员。

        Args:
            grinding: 试磨记录。
            user: 当前用户。
            action: 操作名称（用于异常消息）。

        Raises:
            PermissionDeniedException: 非 operator 且非管理员。
        """
        user_role_names = {role.name for role in user.roles}

        # Administrator 可以执行所有操作
        if "administrator" in user_role_names:
            return

        # 检查是否为试磨操作人
        if grinding.operator_id == user.id:
            return

        raise PermissionDeniedException(
            f"仅试磨责任人或管理员可{action}",
            detail={
                "operator_id": grinding.operator_id,
                "current_user_id": user.id,
                "action": action,
            },
        )

    @staticmethod
    def _validate_and_collect_attachments(
        db: Session,
        task_id: int,
        attachment_ids: list[int],
    ) -> str:
        """验证附件 ID 列表并收集路径。

        验证规则:
            1. 所有 attachment_id 必须存在（is_deleted=False）
            2. 所有附件必须属于当前任务

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            attachment_ids: 附件 ID 列表。

        Returns:
            JSON 序列化的图片路径字符串。

        Raises:
            BusinessLogicException: 附件不存在或不属于当前任务。
        """
        if not attachment_ids:
            return "[]"

        attachments = (
            db.query(Attachment)
            .filter(
                Attachment.id.in_(attachment_ids),
                Attachment.is_deleted == False,  # noqa: E712
            )
            .all()
        )

        # 检查是否全部存在
        found_ids = {a.id for a in attachments}
        missing_ids = set(attachment_ids) - found_ids
        if missing_ids:
            raise BusinessLogicException(
                f"附件不存在或已删除: ids={sorted(missing_ids)}",
                detail={"missing_attachment_ids": sorted(missing_ids)},
            )

        # 检查是否全部属于当前任务
        wrong_task_ids = {
            a.id for a in attachments if a.task_id != task_id
        }
        if wrong_task_ids:
            raise BusinessLogicException(
                f"附件不属于当前任务: ids={sorted(wrong_task_ids)}",
                detail={
                    "wrong_attachment_ids": sorted(wrong_task_ids),
                    "expected_task_id": task_id,
                },
            )

        # 收集图片路径
        paths = [a.file_path for a in attachments]
        return json.dumps(paths)

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
    "GrindingService",
    "GrindingUpdate",
]