"""试磨记录业务层 (Grinding Service)

Sprint 7 — Task 7.2
依据 SRS §4.5、GrindingRecord ORM、Grinding Schema (Task 7.1)、Sprint 2~6 Frozen API。

提供 Grinding 的完整 CRUD 业务逻辑，包括：
    - 创建试磨记录（开始试磨：校验 TrialTask 状态、推进 RECEIVED → GRINDING）
    - 完成试磨（设置 result_status、推进 GRINDING → DISPATCHED）
    - 更新试磨记录（无需状态变更的字段修改）
    - 查询试磨记录（分页、筛选、排序）
    - 删除试磨记录（软删除）
    - 所有写操作自动记录 SystemLog

公开 API:
    - list_grindings(db, *, task_id, operator_id, page, page_size) -> GrindingListResponse
    - get_grinding(db, grinding_id) -> GrindingResponse
    - create_grinding(db, data, operator_id) -> GrindingResponse
    - finish_grinding(db, grinding_id, result_status, failure_reason,
                     operator_id) -> GrindingResponse
    - update_grinding(db, grinding_id, data, operator_id) -> GrindingResponse
    - delete_grinding(db, grinding_id, operator_id) -> None

使用方式:
    from server.services.grinding_service import GrindingService

    service = GrindingService()
    result = service.create_grinding(db, data, operator_id=1)
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
)
from server.enums.action_type import ActionType
from server.enums.task_process_status import TrialTaskProcessStatus
from server.enums.task_result_status import TrialTaskResultStatus
from server.models import GrindingRecord, SystemLog, TrialTask
from server.schemas.grinding_schema import (
    GrindingCreate,
    GrindingUpdate,
    GrindingResponse,
    GrindingListResponse,
)

logger = logging.getLogger("gtms.server")


# ============================================================
# GrindingService
# ============================================================


class GrindingService:
    """试磨记录业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    权限检查由 Router 层负责，本层不处理权限。
    状态流转由本层统一负责，外部不得绕过。
    """

    # ============================================================
    # 公开 API：列表查询
    # ============================================================

    def list_grindings(
        self,
        db: Session,
        *,
        task_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> GrindingListResponse:
        """分页查询试磨记录列表。

        支持按 task_id、operator_id 筛选，按 created_at DESC 排序。

        Args:
            db: 数据库会话。
            task_id: 关联试磨任务 ID（可选）。
            operator_id: 试磨责任人 ID（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            GrindingListResponse: 包含 items 与 total。
        """
        query = db.query(GrindingRecord).filter(
            GrindingRecord.is_deleted.is_(False)
        )

        # 按 task_id 筛选
        if task_id is not None:
            query = query.filter(GrindingRecord.task_id == task_id)

        # 按 operator_id 筛选
        if operator_id is not None:
            query = query.filter(
                GrindingRecord.operator_id == operator_id
            )

        # 总数
        total = query.count()

        # 分页 + 排序（created_at DESC）
        offset = (page - 1) * page_size
        items = (
            query.order_by(GrindingRecord.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # 转换为响应
        responses = [self._to_response(item) for item in items]

        return GrindingListResponse(items=responses, total=total)

    # ============================================================
    # 公开 API：查询单个试磨记录
    # ============================================================

    def get_grinding(
        self,
        db: Session,
        grinding_id: int,
    ) -> GrindingResponse:
        """根据 ID 查询试磨记录。

        过滤 is_deleted=False 的记录。

        Args:
            db: 数据库会话。
            grinding_id: 试磨记录 ID。

        Returns:
            GrindingResponse: 试磨记录信息。

        Raises:
            NotFoundException: 试磨记录不存在或已删除。
        """
        grinding = self._get_grinding_orm(db, grinding_id)
        return self._to_response(grinding)

    # ============================================================
    # 公开 API：创建试磨记录（开始试磨）
    # ============================================================

    def create_grinding(
        self,
        db: Session,
        data: GrindingCreate,
        operator_id: int,
    ) -> GrindingResponse:
        """创建试磨记录并推进任务状态至 GRINDING（开始试磨）。

        流程:
            ① 校验 TrialTask 存在且未删除
            ② 校验 TrialTask 当前 process_status 为 RECEIVED
            ③ 校验 task_id 未重复试磨（UNIQUE 约束）
            ④ 创建 GrindingRecord ORM
            ⑤ 推进 TrialTask.process_status → GRINDING
            ⑥ 提交事务
            ⑦ 写入 SystemLog（Grinding Created + TrialTask Status Change）

        Args:
            db: 数据库会话。
            data: 试磨创建数据（GrindingCreate Schema）。
            operator_id: 操作人 ID。

        Returns:
            GrindingResponse: 新创建的试磨记录。

        Raises:
            NotFoundException: 试磨任务不存在。
            BusinessLogicException: 任务状态非 RECEIVED 或已试磨。
        """
        # ① 校验 TrialTask 存在
        task = (
            db.query(TrialTask)
            .filter(
                TrialTask.id == data.task_id,
                TrialTask.is_deleted.is_(False),
            )
            .first()
        )
        if task is None:
            raise NotFoundException(
                "试磨任务不存在",
                detail={"task_id": data.task_id},
            )

        # ② 校验 TrialTask 当前 process_status 为 RECEIVED
        if task.process_status != TrialTaskProcessStatus.RECEIVED:
            raise BusinessLogicException(
                "仅已收件状态的任务可开始试磨，"
                f"当前状态: {task.process_status.value}",
                detail={
                    "task_id": data.task_id,
                    "current_status": task.process_status.value,
                },
            )

        # ③ 校验 task_id 未重复试磨
        existing = (
            db.query(GrindingRecord)
            .filter(
                GrindingRecord.task_id == data.task_id,
                GrindingRecord.is_deleted.is_(False),
            )
            .first()
        )
        if existing is not None:
            raise BusinessLogicException(
                "该任务已开始试磨，不可重复创建",
                detail={"task_id": data.task_id},
            )

        # ④ 创建 GrindingRecord ORM
        grinding = GrindingRecord(
            task_id=data.task_id,
            operator_id=data.operator_id,
            start_time=data.start_time,
            machine_type=data.machine_type,
            wheel_type=data.wheel_type,
            params=data.params,
            image_paths=data.image_paths,
            created_by=operator_id,
        )
        db.add(grinding)
        db.flush()

        # ⑤ 推进 TrialTask.process_status → GRINDING
        old_status = task.process_status
        task.process_status = TrialTaskProcessStatus.GRINDING
        task.updated_by = operator_id

        try:
            # ⑥ 提交事务
            db.commit()

            # ⑦ 写入 SystemLog
            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.CREATE,
                target_type="Grinding",
                target_id=grinding.id,
                changes={
                    "task_id": data.task_id,
                    "operator_id": data.operator_id,
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

            db.refresh(grinding)
            logger.info(
                "试磨开始成功: grinding_id=%s, task_id=%s, operator_id=%s",
                grinding.id, data.task_id, operator_id,
            )
            return self._to_response(grinding)

        except Exception:
            db.rollback()
            logger.exception(
                "试磨开始失败: task_id=%s", data.task_id
            )
            raise

    # ============================================================
    # 公开 API：完成试磨
    # ============================================================

    def finish_grinding(
        self,
        db: Session,
        grinding_id: int,
        result_status: TrialTaskResultStatus,
        failure_reason: Optional[str] = None,
        end_time: Optional[datetime] = None,
        operator_id: Optional[int] = None,
    ) -> GrindingResponse:
        """完成试磨并推进任务状态至 DISPATCHED。

        流程:
            ① 校验 GrindingRecord 存在
            ② 校验 TrialTask 当前 process_status 为 GRINDING
            ③ 校验 result_status 合法性（PASSED 或 FAILED）
            ④ 校验 result_status=failed 时 failure_reason 必填
            ⑤ 更新 GrindingRecord（end_time, fail_reason）
            ⑥ 设置 TrialTask.result_status
            ⑦ 推进 TrialTask.process_status → DISPATCHED
            ⑧ 提交事务
            ⑨ 写入 SystemLog

        Args:
            db: 数据库会话。
            grinding_id: 试磨记录 ID。
            result_status: 试磨结果（PASSED 或 FAILED）。
            failure_reason: 失败原因（result_status=failed 时必填）。
            end_time: 完成时间（可选，默认当前时间）。
            operator_id: 操作人 ID。

        Returns:
            GrindingResponse: 更新后的试磨记录。

        Raises:
            NotFoundException: 试磨记录或任务不存在。
            BusinessLogicException: 状态非法或 failure_reason 缺失。
        """
        # ① 校验 GrindingRecord 存在
        grinding = self._get_grinding_orm(db, grinding_id)

        # ② 校验 TrialTask 存在且 process_status 为 GRINDING
        task = (
            db.query(TrialTask)
            .filter(
                TrialTask.id == grinding.task_id,
                TrialTask.is_deleted.is_(False),
            )
            .first()
        )
        if task is None:
            raise NotFoundException(
                "关联试磨任务不存在",
                detail={"task_id": grinding.task_id},
            )

        if task.process_status != TrialTaskProcessStatus.GRINDING:
            raise BusinessLogicException(
                "仅试磨中状态的任务可完成试磨，"
                f"当前状态: {task.process_status.value}",
                detail={
                    "task_id": task.id,
                    "current_status": task.process_status.value,
                },
            )

        # ③ 校验 result_status 合法性
        if result_status not in (
            TrialTaskResultStatus.PASSED,
            TrialTaskResultStatus.FAILED,
        ):
            raise BusinessLogicException(
                f"非法的试磨结果: {result_status.value}，"
                "仅允许 passed 或 failed",
                detail={"result_status": result_status.value},
            )

        # ④ 校验 result_status=failed 时 failure_reason 必填
        if result_status == TrialTaskResultStatus.FAILED:
            if not failure_reason or not failure_reason.strip():
                raise BusinessLogicException(
                    "试磨失败时 failure_reason 必须填写",
                    detail={"grinding_id": grinding_id},
                )

        # ⑤ 更新 GrindingRecord
        changes: dict = {}
        actual_end_time = end_time or datetime.now()

        if grinding.end_time != actual_end_time:
            changes["end_time"] = {
                "old": grinding.end_time,
                "new": actual_end_time,
            }
            grinding.end_time = actual_end_time

        if failure_reason is not None and grinding.fail_reason != failure_reason:
            changes["fail_reason"] = {
                "old": grinding.fail_reason,
                "new": failure_reason,
            }
            grinding.fail_reason = failure_reason

        if operator_id is not None:
            grinding.updated_by = operator_id

        # ⑥ 设置 TrialTask.result_status
        old_result_status = task.result_status
        task.result_status = result_status

        # ⑦ 推进 TrialTask.process_status → DISPATCHED
        old_process_status = task.process_status
        task.process_status = TrialTaskProcessStatus.DISPATCHED
        if operator_id is not None:
            task.updated_by = operator_id

        try:
            # ⑧ 提交事务
            db.commit()

            # ⑨ 写入 SystemLog
            changes["result_status"] = {
                "old": old_result_status.value,
                "new": result_status.value,
            }
            self._write_log(
                db,
                operator_id=operator_id or 0,
                action=ActionType.UPDATE,
                target_type="Grinding",
                target_id=grinding.id,
                changes=changes,
            )

            self._write_log(
                db,
                operator_id=operator_id or 0,
                action=ActionType.STATUS_CHANGE,
                target_type="TrialTask",
                target_id=task.id,
                changes={
                    "process_status": {
                        "old": old_process_status.value,
                        "new": task.process_status.value,
                    },
                    "result_status": {
                        "old": old_result_status.value,
                        "new": result_status.value,
                    },
                },
            )

            db.refresh(grinding)
            logger.info(
                "试磨完成: grinding_id=%s, task_id=%s, result=%s",
                grinding_id, task.id, result_status.value,
            )
            return self._to_response(grinding)

        except Exception:
            db.rollback()
            logger.exception(
                "试磨完成失败: grinding_id=%s", grinding_id
            )
            raise

    # ============================================================
    # 公开 API：更新试磨记录
    # ============================================================

    def update_grinding(
        self,
        db: Session,
        grinding_id: int,
        data: GrindingUpdate,
        operator_id: int,
    ) -> GrindingResponse:
        """更新试磨记录（不涉及状态流转）。

        仅更新传入的非 None 字段（exclude_unset）。
        如需完成试磨，请使用 finish_grinding()。

        Args:
            db: 数据库会话。
            grinding_id: 试磨记录 ID。
            data: 更新数据（GrindingUpdate Schema）。
            operator_id: 操作人 ID。

        Returns:
            GrindingResponse: 更新后的试磨记录。

        Raises:
            NotFoundException: 试磨记录不存在。
        """
        grinding = self._get_grinding_orm(db, grinding_id)

        # 记录变更
        changes: dict = {}
        update_data = data.model_dump(exclude_unset=True)

        for field_name, new_value in update_data.items():
            old_value = getattr(grinding, field_name)
            if new_value is not None and new_value != old_value:
                changes[field_name] = {
                    "old": old_value,
                    "new": new_value,
                }
                setattr(grinding, field_name, new_value)

        if not changes:
            return self._to_response(grinding)

        try:
            grinding.updated_by = operator_id
            db.flush()

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.UPDATE,
                target_type="Grinding",
                target_id=grinding.id,
                changes=changes,
            )

            db.commit()
            db.refresh(grinding)
            logger.info(
                "试磨记录更新成功: grinding_id=%s, fields=%s",
                grinding_id, list(changes.keys()),
            )
            return self._to_response(grinding)

        except Exception:
            db.rollback()
            logger.exception(
                "试磨记录更新失败: grinding_id=%s", grinding_id
            )
            raise

    # ============================================================
    # 公开 API：删除试磨记录
    # ============================================================

    def delete_grinding(
        self,
        db: Session,
        grinding_id: int,
        operator_id: int,
    ) -> None:
        """软删除试磨记录。

        设置 is_deleted=True，不物理删除。

        Args:
            db: 数据库会话。
            grinding_id: 试磨记录 ID。
            operator_id: 操作人 ID。

        Raises:
            NotFoundException: 试磨记录不存在。
        """
        grinding = self._get_grinding_orm(db, grinding_id)

        try:
            grinding.is_deleted = True
            grinding.updated_by = operator_id
            db.flush()

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.DELETE,
                target_type="Grinding",
                target_id=grinding.id,
                changes={"task_id": grinding.task_id},
            )

            db.commit()
            logger.info(
                "试磨记录已删除: grinding_id=%s, task_id=%s, operator_id=%s",
                grinding_id, grinding.task_id, operator_id,
            )

        except Exception:
            db.rollback()
            logger.exception(
                "试磨记录删除失败: grinding_id=%s", grinding_id
            )
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    def _get_grinding_orm(
        self, db: Session, grinding_id: int
    ) -> GrindingRecord:
        """获取 ORM 实例（内部使用）。

        Args:
            db: 数据库会话。
            grinding_id: 试磨记录 ID。

        Returns:
            GrindingRecord ORM 实例。

        Raises:
            NotFoundException: 试磨记录不存在或已删除。
        """
        grinding = (
            db.query(GrindingRecord)
            .filter(
                GrindingRecord.id == grinding_id,
                GrindingRecord.is_deleted.is_(False),
            )
            .first()
        )
        if grinding is None:
            raise NotFoundException(
                "试磨记录不存在",
                detail={"grinding_id": grinding_id},
            )
        return grinding

    def _to_response(
        self, grinding: GrindingRecord
    ) -> GrindingResponse:
        """将 GrindingRecord ORM 实例转换为 GrindingResponse。

        Args:
            grinding: GrindingRecord ORM 实例。

        Returns:
            GrindingResponse: 试磨记录响应 Schema。
        """
        return GrindingResponse(
            id=grinding.id,
            task_id=grinding.task_id,
            operator_id=grinding.operator_id,
            start_time=grinding.start_time,
            machine_type=grinding.machine_type,
            wheel_type=grinding.wheel_type,
            params=grinding.params,
            end_time=grinding.end_time,
            image_paths=grinding.image_paths,
            fail_reason=grinding.fail_reason,
            created_at=grinding.created_at,
            updated_at=grinding.updated_at,
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
    "GrindingService",
]
