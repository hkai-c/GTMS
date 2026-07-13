"""收件记录业务层 (Receipt Service)

Sprint 6 — Task 6.2
依据 SRS §4.4、Receipt ORM、Receipt Schema (Task 6.1)、Sprint 2/5 Frozen API。

提供 Receipt 的完整 CRUD 业务逻辑，包括：
    - 创建收件记录（校验 TrialTask 存在、状态流转 CREATED → RECEIVED）
    - 查询收件记录（分页、筛选、排序）
    - 更新收件记录
    - 删除收件记录（软删除）
    - 所有写操作自动记录 SystemLog

公开 API:
    - list_receipts(db, *, task_id, page, page_size) -> ReceiptListResponse
    - get_receipt(db, receipt_id) -> ReceiptResponse
    - create_receipt(db, data, operator_id) -> ReceiptResponse
    - update_receipt(db, receipt_id, data, operator_id) -> ReceiptResponse
    - delete_receipt(db, receipt_id, operator_id) -> None

使用方式:
    from server.services.receipt_service import ReceiptService

    service = ReceiptService()
    result = service.create_receipt(db, data, operator_id=1)
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
)
from server.enums.action_type import ActionType
from server.enums.task_process_status import TrialTaskProcessStatus
from server.models import Receipt, SystemLog, TrialTask, User
from server.schemas.receipt_schema import (
    ReceiptCreate,
    ReceiptUpdate,
    ReceiptResponse,
    ReceiptListResponse,
)

logger = logging.getLogger("gtms.server")


# ============================================================
# ReceiptService
# ============================================================


class ReceiptService:
    """收件记录业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    权限检查由 Router 层负责，本层不处理权限。
    文件上传由 Upload Router 负责，本层仅接收上传元数据。
    """

    # ============================================================
    # 公开 API：列表查询
    # ============================================================

    def list_receipts(
        self,
        db: Session,
        *,
        task_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ReceiptListResponse:
        """分页查询收件记录列表。

        支持按 task_id 筛选，按 created_at DESC 排序。

        Args:
            db: 数据库会话。
            task_id: 关联试磨任务 ID（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            ReceiptListResponse: 包含 items 与 total。
        """
        query = db.query(Receipt).filter(Receipt.is_deleted == False)

        # 按 task_id 筛选
        if task_id is not None:
            query = query.filter(Receipt.task_id == task_id)

        # 总数
        total = query.count()

        # 分页 + 排序（created_at DESC）
        offset = (page - 1) * page_size
        items = (
            query.order_by(Receipt.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # 转换为响应
        responses = [self._to_response(receipt) for receipt in items]

        return ReceiptListResponse(items=responses, total=total)

    # ============================================================
    # 公开 API：查询单个收件记录
    # ============================================================

    def get_receipt(
        self,
        db: Session,
        receipt_id: int,
    ) -> ReceiptResponse:
        """根据 ID 查询收件记录。

        过滤 is_deleted=False 的记录。

        Args:
            db: 数据库会话。
            receipt_id: 收件记录 ID。

        Returns:
            ReceiptResponse: 收件记录信息。

        Raises:
            NotFoundException: 收件记录不存在或已删除。
        """
        receipt = (
            db.query(Receipt)
            .filter(
                Receipt.id == receipt_id,
                Receipt.is_deleted == False,
            )
            .first()
        )
        if receipt is None:
            raise NotFoundException(
                "收件记录不存在",
                detail={"receipt_id": receipt_id},
            )

        return self._to_response(receipt)

    # ============================================================
    # 公开 API：创建收件记录
    # ============================================================

    def create_receipt(
        self,
        db: Session,
        data: ReceiptCreate,
        operator_id: int,
    ) -> ReceiptResponse:
        """创建收件记录并推进任务状态至 RECEIVED。

        流程:
            ① 校验 TrialTask 存在且未删除
            ② 校验 TrialTask 当前状态为 CREATED
            ③ 校验 receiver_id 存在
            ④ 校验 task_id 未重复收件
            ⑤ 创建 Receipt ORM
            ⑥ 推进 TrialTask.process_status → RECEIVED
            ⑦ 提交事务
            ⑧ 写入 SystemLog（Receipt Created + TrialTask Status Change）

        Args:
            db: 数据库会话。
            data: 收件创建数据（ReceiptCreate Schema）。
            operator_id: 操作人 ID。

        Returns:
            ReceiptResponse: 新创建的收件记录。

        Raises:
            NotFoundException: 试磨任务或收件人不存在。
            BusinessLogicException: 任务状态非 CREATED 或已收件。
        """
        # ① 校验 TrialTask 存在
        task = (
            db.query(TrialTask)
            .filter(
                TrialTask.id == data.task_id,
                TrialTask.is_deleted == False,
            )
            .first()
        )
        if task is None:
            raise NotFoundException(
                "试磨任务不存在",
                detail={"task_id": data.task_id},
            )

        # ② 校验 TrialTask 当前状态为 CREATED
        if task.process_status != TrialTaskProcessStatus.CREATED:
            raise BusinessLogicException(
                f"仅创建状态的任务可收件，当前状态: {task.process_status.value}",
                detail={
                    "task_id": data.task_id,
                    "current_status": task.process_status.value,
                },
            )

        # ③ 校验 receiver_id 存在
        receiver = (
            db.query(User)
            .filter(User.id == data.receiver_id, User.is_deleted == False)
            .first()
        )
        if receiver is None:
            raise NotFoundException(
                "收件人不存在或已禁用",
                detail={"receiver_id": data.receiver_id},
            )

        # ④ 校验 task_id 未重复收件
        existing = (
            db.query(Receipt)
            .filter(
                Receipt.task_id == data.task_id,
                Receipt.is_deleted == False,
            )
            .first()
        )
        if existing is not None:
            raise BusinessLogicException(
                "该任务已收件，不可重复收件",
                detail={"task_id": data.task_id},
            )

        # ⑤ 创建 Receipt ORM
        receipt = Receipt(
            task_id=data.task_id,
            received_at=data.received_at,
            receiver_id=data.receiver_id,
            image_paths=data.image_paths,
            created_by=operator_id,
        )
        db.add(receipt)
        db.flush()

        # ⑥ 推进 TrialTask.process_status → RECEIVED
        old_status = task.process_status
        task.process_status = TrialTaskProcessStatus.RECEIVED
        task.updated_by = operator_id

        try:
            # ⑦ 提交事务
            db.commit()

            # ⑧ 写入 SystemLog
            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.CREATE,
                target_type="Receipt",
                target_id=receipt.id,
                changes={
                    "task_id": data.task_id,
                    "receiver_id": data.receiver_id,
                },
            )

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.STATUS_CHANGE,
                target_type="TrialTask",
                target_id=task.id,
                changes={
                    "process_status": {
                        "old": old_status.value,
                        "new": task.process_status.value,
                    },
                },
            )

            db.refresh(receipt)
            logger.info(
                "收件记录创建成功: receipt_id=%s, task_id=%s, operator_id=%s",
                receipt.id, data.task_id, operator_id,
            )
            return self._to_response(receipt)

        except Exception:
            db.rollback()
            logger.exception(
                "收件记录创建失败: task_id=%s", data.task_id
            )
            raise

    # ============================================================
    # 公开 API：更新收件记录
    # ============================================================

    def update_receipt(
        self,
        db: Session,
        receipt_id: int,
        data: ReceiptUpdate,
        operator_id: int,
    ) -> ReceiptResponse:
        """更新收件记录。

        仅更新传入的非 None 字段（exclude_unset）。

        Args:
            db: 数据库会话。
            receipt_id: 收件记录 ID。
            data: 更新数据（ReceiptUpdate Schema）。
            operator_id: 操作人 ID。

        Returns:
            ReceiptResponse: 更新后的收件记录。

        Raises:
            NotFoundException: 收件记录不存在。
        """
        receipt = self._get_receipt_orm(db, receipt_id)

        # 记录变更
        changes: dict = {}
        update_data = data.model_dump(exclude_unset=True)

        for field_name, new_value in update_data.items():
            old_value = getattr(receipt, field_name)
            if new_value is not None and new_value != old_value:
                changes[field_name] = {"old": old_value, "new": new_value}
                setattr(receipt, field_name, new_value)

        if not changes:
            return self._to_response(receipt)

        try:
            receipt.updated_by = operator_id
            db.flush()

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.UPDATE,
                target_type="Receipt",
                target_id=receipt.id,
                changes=changes,
            )

            db.commit()
            db.refresh(receipt)
            logger.info(
                "收件记录更新成功: receipt_id=%s, fields=%s",
                receipt_id, list(changes.keys()),
            )
            return self._to_response(receipt)

        except Exception:
            db.rollback()
            logger.exception(
                "收件记录更新失败: receipt_id=%s", receipt_id
            )
            raise

    # ============================================================
    # 公开 API：删除收件记录
    # ============================================================

    def delete_receipt(
        self,
        db: Session,
        receipt_id: int,
        operator_id: int,
    ) -> None:
        """软删除收件记录。

        设置 is_deleted=True，不物理删除。

        Args:
            db: 数据库会话。
            receipt_id: 收件记录 ID。
            operator_id: 操作人 ID。

        Raises:
            NotFoundException: 收件记录不存在。
        """
        receipt = self._get_receipt_orm(db, receipt_id)

        try:
            receipt.is_deleted = True
            receipt.updated_by = operator_id
            db.flush()

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.DELETE,
                target_type="Receipt",
                target_id=receipt.id,
                changes={"task_id": receipt.task_id},
            )

            db.commit()
            logger.info(
                "收件记录已删除: receipt_id=%s, task_id=%s, operator_id=%s",
                receipt_id, receipt.task_id, operator_id,
            )

        except Exception:
            db.rollback()
            logger.exception(
                "收件记录删除失败: receipt_id=%s", receipt_id
            )
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    def _get_receipt_orm(self, db: Session, receipt_id: int) -> Receipt:
        """获取 ORM 实例（内部使用）。

        Args:
            db: 数据库会话。
            receipt_id: 收件记录 ID。

        Returns:
            Receipt ORM 实例。

        Raises:
            NotFoundException: 收件记录不存在或已删除。
        """
        receipt = (
            db.query(Receipt)
            .filter(
                Receipt.id == receipt_id,
                Receipt.is_deleted == False,
            )
            .first()
        )
        if receipt is None:
            raise NotFoundException(
                "收件记录不存在",
                detail={"receipt_id": receipt_id},
            )
        return receipt

    def _to_response(self, receipt: Receipt) -> ReceiptResponse:
        """将 Receipt ORM 实例转换为 ReceiptResponse。

        Args:
            receipt: Receipt ORM 实例。

        Returns:
            ReceiptResponse: 收件记录响应 Schema。
        """
        return ReceiptResponse(
            id=receipt.id,
            task_id=receipt.task_id,
            received_at=receipt.received_at,
            receiver_id=receipt.receiver_id,
            image_paths=receipt.image_paths,
            created_at=receipt.created_at,
            updated_at=receipt.updated_at,
        )

    def _write_log(
        self,
        db: Session,
        *,
        operator_id: int,
        action: ActionType,
        target_type: str,
        target_id: int,
        changes: Optional[dict] = None,
    ) -> None:
        """写入系统操作日志。

        Args:
            db: 数据库会话。
            operator_id: 操作人 ID。
            action: 操作类型。
            target_type: 操作对象类型。
            target_id: 操作对象 ID。
            changes: 变更内容（可选）。
        """
        log_entry = SystemLog(
            user_id=operator_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            changes=changes,
        )
        db.add(log_entry)
        db.commit()


__all__ = [
    "ReceiptService",
]
