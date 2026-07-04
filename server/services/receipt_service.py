"""收件服务 (Receipt Service)

Sprint 2 — Task 2.6
严格依据 DB_DESIGN.md、SRS.md、CODE_WIKI.md。

提供收件记录的完整 CRUD 业务逻辑，包括：
    - 收件登记（创建 Receipt + Attachment + 状态流转）
    - 查询收件（含附件）
    - 修改收件
    - 删除收件（软删除，需管理员权限）
    - 所有写操作自动记录 SystemLog

状态流转：
    CREATED → RECEIVED（收件登记后自动触发）

异常体系：
    使用 Task 2.1 冻结异常类。

使用方式:
    from server.services.receipt_service import ReceiptService

    service = ReceiptService()
    receipt = service.create_receipt(db, task_id, data, receiver_user)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from server.enums import (
    ActionType,
    FileType,
    TrialTaskProcessStatus,
)
from server.models import Attachment, Receipt, SystemLog, TrialTask, User

logger = logging.getLogger(__name__)


# ============================================================
# 输入 Schema
# ============================================================


@dataclass
class ReceiptCreate:
    """收件登记输入。

    Attributes:
        task_id: 试磨任务 ID。
        receipt_date: 收件日期。
        receiver_id: 收件人 ID。
        images: 图片文件名列表（如 ["img1.jpg", "img2.jpg"]）。
    """

    task_id: int
    receipt_date: datetime
    receiver_id: int
    images: list[str] = field(default_factory=list)


@dataclass
class ReceiptUpdate:
    """收件修改输入。

    允许修改收件日期和新增图片。
    不允许修改 task_id 和 receiver_id。

    Attributes:
        receipt_date: 收件日期（可选）。
        images: 新增图片文件名列表（可选）。
    """

    receipt_date: Optional[datetime] = None
    images: Optional[list[str]] = None


# ============================================================
# ReceiptService
# ============================================================


class ReceiptService:
    """收件业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    """

    # ============================================================
    # 收件登记
    # ============================================================

    def create_receipt(
        self,
        db: Session,
        data: ReceiptCreate,
        operator: User,
    ) -> Receipt:
        """收件登记。

        业务流程:
            1. 检查 TrialTask 存在且 is_deleted=False
            2. 检查 process_status == CREATED
            3. 创建 Receipt 记录
            4. 为每张图片创建 Attachment 记录
            5. 更新 TrialTask.process_status: CREATED → RECEIVED
            6. 写入 SystemLog
            7. commit 并返回 Receipt

        Args:
            db: 数据库会话。
            data: 收件登记数据。
            operator: 操作人。

        Returns:
            新创建的 Receipt 实例。

        Raises:
            NotFoundException: 任务不存在或已删除。
            BusinessLogicException: 任务状态不允许收件。
        """
        # 检查任务存在
        task = self._get_task_or_raise(db, data.task_id)

        # 检查状态：仅 CREATED 可收件
        if task.process_status != TrialTaskProcessStatus.CREATED:
            raise BusinessLogicException(
                f"仅创建状态的任务可收件，当前状态: {task.process_status.value}",
                detail={
                    "task_id": data.task_id,
                    "current_status": task.process_status.value,
                },
            )

        try:
            # 生成图片路径
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d%H%M%S")
            image_paths = []
            for i, img_name in enumerate(data.images):
                path = (
                    f"uploads/images/{task.task_no}_receipt_"
                    f"{timestamp}_{i}.jpg"
                )
                image_paths.append(path)

            # 创建 Receipt
            receipt = Receipt(
                task_id=data.task_id,
                received_at=data.receipt_date,
                receiver_id=data.receiver_id,
                image_paths=json.dumps(image_paths) if image_paths else None,
                created_by=operator.id,
            )
            db.add(receipt)
            db.flush()

            # 创建 Attachment 记录
            for i, img_name in enumerate(data.images):
                attachment = Attachment(
                    task_id=data.task_id,
                    file_type=FileType.IMAGE,
                    file_name=img_name,
                    file_path=image_paths[i],
                    file_size=0,
                    uploaded_by=operator.id,
                    created_by=operator.id,
                )
                db.add(attachment)

            # 更新任务状态: CREATED → RECEIVED
            task.process_status = TrialTaskProcessStatus.RECEIVED
            task.updated_by = operator.id

            # 写入 SystemLog
            self._log_action(
                db=db,
                user_id=operator.id,
                action=ActionType.STATUS_CHANGE,
                target_type="Receipt",
                target_id=receipt.id,
                changes={
                    "task_id": data.task_id,
                    "task_no": task.task_no,
                    "from_status": TrialTaskProcessStatus.CREATED.value,
                    "to_status": TrialTaskProcessStatus.RECEIVED.value,
                    "image_count": len(data.images),
                },
            )

            db.commit()
            logger.info(
                "收件登记成功: task_no=%s, receipt_id=%s, images=%d",
                task.task_no, receipt.id, len(data.images),
            )
            return receipt

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 查询收件
    # ============================================================

    def get_receipt(self, db: Session, task_id: int) -> Receipt:
        """根据任务 ID 查询收件记录。

        自动过滤 is_deleted=True 的记录。

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。

        Returns:
            Receipt 实例。

        Raises:
            NotFoundException: 收件记录不存在或已删除。
        """
        receipt = (
            db.query(Receipt)
            .filter(
                Receipt.task_id == task_id,
                Receipt.is_deleted == False,  # noqa: E712
            )
            .first()
        )
        if receipt is None:
            raise NotFoundException(
                f"收件记录不存在: task_id={task_id}",
                detail={"task_id": task_id},
            )
        return receipt

    # ============================================================
    # 修改收件
    # ============================================================

    def update_receipt(
        self,
        db: Session,
        task_id: int,
        data: ReceiptUpdate,
        operator: User,
    ) -> Receipt:
        """修改收件记录。

        允许修改:
            - receipt_date（收件日期）
            - 新增图片（追加 Attachment）

        不允许修改:
            - task_id
            - receiver_id

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            data: 修改数据。
            operator: 操作人。

        Returns:
            更新后的 Receipt 实例。

        Raises:
            NotFoundException: 收件记录不存在。
        """
        receipt = self.get_receipt(db, task_id)
        changes = {}

        try:
            # 修改收件日期
            if data.receipt_date is not None:
                old_date = receipt.received_at.isoformat() if receipt.received_at else None
                receipt.received_at = data.receipt_date
                changes["receipt_date"] = {
                    "old": old_date,
                    "new": data.receipt_date.isoformat(),
                }

            # 新增图片
            if data.images:
                task = self._get_task_or_raise(db, task_id)
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d%H%M%S")

                # 读取现有图片路径
                existing_paths = []
                if receipt.image_paths:
                    try:
                        existing_paths = json.loads(receipt.image_paths)
                    except json.JSONDecodeError:
                        pass

                new_paths = []
                for i, img_name in enumerate(data.images):
                    path = (
                        f"uploads/images/{task.task_no}_receipt_"
                        f"{timestamp}_add_{i}.jpg"
                    )
                    new_paths.append(path)

                    attachment = Attachment(
                        task_id=task_id,
                        file_type=FileType.IMAGE,
                        file_name=img_name,
                        file_path=path,
                        file_size=0,
                        uploaded_by=operator.id,
                        created_by=operator.id,
                    )
                    db.add(attachment)

                # 更新 image_paths
                all_paths = existing_paths + new_paths
                receipt.image_paths = json.dumps(all_paths)
                changes["images"] = {"added": len(new_paths)}

            if not changes:
                return receipt

            receipt.updated_by = operator.id
            db.flush()

            self._log_action(
                db=db,
                user_id=operator.id,
                action=ActionType.UPDATE,
                target_type="Receipt",
                target_id=receipt.id,
                changes=changes,
            )

            db.commit()
            logger.info(
                "收件修改成功: task_id=%s, fields=%s", task_id, list(changes.keys())
            )
            return receipt

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 删除收件（软删除）
    # ============================================================

    def delete_receipt(
        self,
        db: Session,
        task_id: int,
        operator: User,
    ) -> None:
        """软删除收件记录（含关联附件）。

        仅管理员可执行删除操作。

        Args:
            db: 数据库会话。
            task_id: 试磨任务 ID。
            operator: 操作人。

        Raises:
            NotFoundException: 收件记录不存在。
            PermissionDeniedException: 非管理员用户。
        """
        receipt = self.get_receipt(db, task_id)

        # 管理员权限检查
        user_role_names = {role.name for role in operator.roles}
        if "administrator" not in user_role_names:
            raise PermissionDeniedException(
                "仅管理员可删除收件记录",
                detail={
                    "task_id": task_id,
                    "user_roles": sorted(user_role_names),
                },
            )

        try:
            # 软删除 Receipt
            receipt.is_deleted = True
            receipt.updated_by = operator.id

            # 软删除关联的 Attachment
            db.query(Attachment).filter(
                Attachment.task_id == task_id,
                Attachment.file_type == FileType.IMAGE,
                Attachment.is_deleted == False,  # noqa: E712
            ).update(
                {"is_deleted": True, "updated_by": operator.id},
                synchronize_session=False,
            )

            db.flush()

            self._log_action(
                db=db,
                user_id=operator.id,
                action=ActionType.DELETE,
                target_type="Receipt",
                target_id=receipt.id,
                changes={"task_id": task_id},
            )

            db.commit()
            logger.info(
                "收件已删除: task_id=%s, user=%s",
                task_id, operator.username,
            )

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    @staticmethod
    def _get_task_or_raise(db: Session, task_id: int) -> TrialTask:
        """获取任务，不存在或已删除时抛出 NotFoundException。"""
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
    def _log_action(
        db: Session,
        user_id: int,
        action: ActionType,
        target_type: str,
        target_id: int,
        changes: Optional[dict[str, Any]] = None,
    ) -> None:
        """写入系统操作日志。"""
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
    "ReceiptService",
    "ReceiptCreate",
    "ReceiptUpdate",
]