"""检测服务 (Inspection Service)

Sprint 2 — Task 2.8
严格依据 DB_DESIGN.md、SRS.md、CODE_WIKI.md §6.6.3。

提供检测记录的完整业务逻辑，包括：
    - 上传检测报告（创建 InspectionRecord + 绑定附件 + 更新 result_status）
    - 查询检测
    - 修改检测
    - 删除检测（软删除，仅管理员）
    - 所有写操作自动记录 SystemLog

权限规则（依据 CODE_WIKI §6.6.3）：
    - 上传检测报告: 任意具有 Inspection 权限的 Technician 或 Administrator
    - 修改检测: InspectionRecord.created_by 或 Administrator
    - 删除检测: 仅 Administrator

异常体系：
    使用 Task 2.1 冻结异常类。

使用方式:
    from server.services.inspection_service import InspectionService

    service = InspectionService()
    record = service.upload_report(db, task_id=1, inspection_result=InspectionResult.PASS, ...)
"""

import json
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
    InspectionResult,
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
)
from server.models import (
    Attachment,
    InspectionRecord,
    SystemLog,
    TrialTask,
    User,
)

logger = logging.getLogger(__name__)


# ============================================================
# InspectionService
# ============================================================


class InspectionService:
    """检测业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    """

    # ============================================================
    # 上传检测报告
    # ============================================================

    def upload_report(
        self,
        db: Session,
        *,
        task_id: int,
        inspection_result: InspectionResult,
        precision: Optional[str],
        roughness: Optional[str],
        attachment_ids: list[int],
        failure_reason: Optional[str],
        current_user: User,
    ) -> InspectionRecord:
        """上传检测报告。

        业务流程:
            1. 查询 TrialTask，验证 process_status == GRINDING
            2. 权限检查：Technician（inspection:write）或 Administrator
            3. 验证 attachment_ids（全部存在且属于当前任务）
            4. 若 inspection_result == FAILED，failure_reason 必填
            5. 创建 InspectionRecord
            6. 更新 TrialTask.result_status（PASSED/FAILED）
            7. 绑定附件路径到 report_path
            8. 写入 SystemLog（UPLOAD_INSPECTION）
            9. commit 并返回 InspectionRecord

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            inspection_result: 检测结论（PASS 或 FAIL）。
            precision: 精度检测结果（对应 ORM accuracy）。
            roughness: 表面粗糙度检测结果。
            attachment_ids: 已有附件 ID 列表。
            failure_reason: 失败原因（inspection_result=FAIL 时必填）。
            current_user: 当前登录用户。

        Returns:
            新创建的 InspectionRecord 实例。

        Raises:
            NotFoundException: 任务不存在或已删除。
            BusinessLogicException: 状态非 GRINDING、附件验证失败、失败无原因。
            PermissionDeniedException: 用户无 Inspection 权限。
        """
        task = self._get_task_or_raise(db, task_id)

        # ① 状态检查：仅 GRINDING 可上传检测报告
        if task.process_status != TrialTaskProcessStatus.GRINDING:
            raise BusinessLogicException(
                f"仅试磨中状态的任务可上传检测报告，当前状态: {task.process_status.value}",
                detail={
                    "task_id": task_id,
                    "current_status": task.process_status.value,
                },
            )

        # ② 权限检查：Technician（inspection:write）或 Administrator
        self._check_inspection_permission(current_user)

        # ④ 失败时 failure_reason 必填
        if inspection_result == InspectionResult.FAIL:
            if not failure_reason:
                raise BusinessLogicException(
                    "检测不合格时必须填写失败原因",
                    detail={"task_id": task_id, "inspection_result": "fail"},
                )

        # ⑤ 验证 attachment_ids：全部存在且属于当前任务
        report_path_json = None
        if attachment_ids:
            report_path_json = self._validate_and_collect_attachments(
                db, task_id, attachment_ids
            )

        try:
            # ③ 创建 InspectionRecord
            inspection = InspectionRecord(
                task_id=task_id,
                report_path=report_path_json,
                accuracy=precision,
                roughness=roughness,
                result=inspection_result,
                inspector_id=current_user.id,
                created_by=current_user.id,
            )
            db.add(inspection)
            db.flush()

            # ④ 更新任务结果状态
            if inspection_result == InspectionResult.PASS:
                task.result_status = TrialTaskResultStatus.PASSED
            else:
                task.result_status = TrialTaskResultStatus.FAILED
                task.failure_reason = failure_reason
            task.updated_by = current_user.id

            # ⑨ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.CREATE,
                target_type="InspectionRecord",
                target_id=inspection.id,
                changes={
                    "task_id": task_id,
                    "task_no": task.task_no,
                    "inspection_result": inspection_result.value,
                    "attachment_count": len(attachment_ids),
                    "action": "UPLOAD_INSPECTION",
                },
            )

            db.commit()
            logger.info(
                "检测报告上传成功: task_no=%s, inspection_id=%s, result=%s, user=%s",
                task.task_no, inspection.id, inspection_result.value, current_user.username,
            )
            return inspection

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 查询检测
    # ============================================================

    def get_inspection(self, db: Session, task_id: int) -> InspectionRecord:
        """根据任务 ID 查询检测记录。

        自动过滤 is_deleted=True 的记录。

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。

        Returns:
            InspectionRecord 实例。

        Raises:
            NotFoundException: 检测记录不存在或已删除。
        """
        inspection = (
            db.query(InspectionRecord)
            .filter(
                InspectionRecord.task_id == task_id,
                InspectionRecord.is_deleted == False,  # noqa: E712
            )
            .first()
        )
        if inspection is None:
            raise NotFoundException(
                f"检测记录不存在: task_id={task_id}",
                detail={"task_id": task_id},
            )
        return inspection

    # ============================================================
    # 修改检测
    # ============================================================

    def update_inspection(
        self,
        db: Session,
        task_id: int,
        **kwargs: Any,
    ) -> InspectionRecord:
        """修改检测记录。

        权限规则:
            - Administrator 或 InspectionRecord.created_by 可修改

        允许修改的字段:
            - report_path: 检测报告路径
            - accuracy: 精度检测结果
            - roughness: 表面粗糙度
            - result: 检测结论
            - inspector_id: 检测人

        禁止修改的字段:
            - task_id
            - created_by
            - created_at

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            **kwargs: 要修改的字段键值对（需包含 current_user）。

        Returns:
            更新后的 InspectionRecord 实例。

        Raises:
            NotFoundException: 检测记录不存在。
            PermissionDeniedException: 非 created_by 且非管理员。
            BusinessLogicException: 尝试修改禁止字段或传入未知字段。
        """
        inspection = self.get_inspection(db, task_id)

        # 提取 current_user（不从 kwargs 写入 ORM）
        current_user = kwargs.pop("current_user", None)

        # ⑦ 权限检查：Administrator 或 created_by
        self._check_creator_or_admin(inspection, current_user, "修改检测")

        # 禁止修改的字段
        forbidden = {"task_id", "created_by", "created_at"}
        invalid = forbidden & set(kwargs.keys())
        if invalid:
            raise BusinessLogicException(
                f"禁止修改以下字段: {', '.join(sorted(invalid))}",
                detail={"forbidden_fields": sorted(invalid)},
            )

        # 允许修改的字段
        allowed = {
            "report_path", "accuracy", "roughness", "result", "inspector_id",
        }

        changes = {}
        for key, value in kwargs.items():
            if key not in allowed:
                raise BusinessLogicException(
                    f"未知字段: {key}，允许修改的字段: {', '.join(sorted(allowed))}",
                    detail={"unknown_field": key, "allowed_fields": sorted(allowed)},
                )
            old_value = getattr(inspection, key, None)
            if old_value != value:
                changes[key] = {"old": str(old_value), "new": str(value)}
                setattr(inspection, key, value)

        if not changes:
            return inspection

        try:
            inspection.updated_by = current_user.id if current_user else None
            db.flush()

            # ⑨ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id if current_user else 0,
                action=ActionType.UPDATE,
                target_type="InspectionRecord",
                target_id=inspection.id,
                changes={
                    "task_id": task_id,
                    "updated_fields": changes,
                    "action": "UPDATE_INSPECTION",
                },
            )

            db.commit()
            logger.info(
                "检测修改成功: task_id=%s, fields=%s",
                task_id, list(changes.keys()),
            )
            return inspection

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 删除检测（软删除）
    # ============================================================

    def delete_inspection(
        self,
        db: Session,
        task_id: int,
        current_user: User,
    ) -> None:
        """软删除检测记录。

        ⑧ 仅 Administrator 可执行删除操作。

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            current_user: 当前登录用户。

        Raises:
            NotFoundException: 检测记录不存在。
            PermissionDeniedException: 非管理员用户。
        """
        inspection = self.get_inspection(db, task_id)

        # ⑧ 管理员权限检查
        user_role_names = {role.name for role in current_user.roles}
        if "administrator" not in user_role_names:
            raise PermissionDeniedException(
                "仅管理员可删除检测记录",
                detail={
                    "task_id": task_id,
                    "user_roles": sorted(user_role_names),
                },
            )

        try:
            inspection.is_deleted = True
            inspection.updated_by = current_user.id
            db.flush()

            # ⑨ 写入 SystemLog
            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.DELETE,
                target_type="InspectionRecord",
                target_id=inspection.id,
                changes={
                    "task_id": task_id,
                    "action": "DELETE_INSPECTION",
                },
            )

            db.commit()
            logger.info(
                "检测记录已删除: task_id=%s, user=%s",
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
    def _check_inspection_permission(user: User) -> None:
        """检查用户是否具有检测权限。

        允许：Administrator 或具有 inspection:write 权限的角色。

        Args:
            user: 当前用户。

        Raises:
            PermissionDeniedException: 用户无检测权限。
        """
        user_role_names = {role.name for role in user.roles}

        # Administrator 拥有全部权限
        if "administrator" in user_role_names:
            return

        # 检查是否有角色拥有 inspection:write 权限
        for role_name in user_role_names:
            if has_permission(role_name, "inspection:write"):
                return

        raise PermissionDeniedException(
            "您没有检测操作权限，需要 inspection:write 权限",
            detail={
                "user_roles": sorted(user_role_names),
                "required_permission": "inspection:write",
            },
        )

    @staticmethod
    def _check_creator_or_admin(
        inspection: InspectionRecord,
        user: User,
        action: str,
    ) -> None:
        """检查用户是否为检测记录创建人或管理员。

        Args:
            inspection: 检测记录。
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
        if inspection.created_by == user.id:
            return

        raise PermissionDeniedException(
            f"仅检测记录创建人或管理员可{action}",
            detail={
                "created_by": inspection.created_by,
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
            JSON 序列化的附件路径字符串。

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

        # 收集路径
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
    "InspectionService",
]