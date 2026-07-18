"""检测记录业务层 (Inspection Service)

Sprint 8 — Task 8.2
依据 SRS §4.6、InspectionRecord ORM、Inspection Schema (Task 8.1)、
    Sprint 1~7 Frozen API。

提供 Inspection 的完整 CRUD 业务逻辑，包括：
    - 创建检测记录（上传检测报告：校验 GrindingRecord 存在）
    - 完成检测（设置 InspectionResult + 推进 GRINDING → DISPATCHED）
    - 更新检测记录（无需状态变更的字段修改）
    - 查询检测记录（分页、筛选、排序）
    - 删除检测记录（软删除）
    - 所有写操作自动记录 SystemLog

公开 API:
    - list_inspections(db, *, task_id, inspector_id, result, page, page_size)
        -> InspectionListResponse
    - get_inspection(db, inspection_id) -> InspectionResponse
    - create_inspection(db, data, operator_id) -> InspectionResponse
    - finish_inspection(db, inspection_id, result, failure_reason,
        operator_id) -> InspectionResponse
    - update_inspection(db, inspection_id, data, operator_id)
        -> InspectionResponse
    - delete_inspection(db, inspection_id, operator_id) -> None

使用方式:
    from server.services.inspection_service import InspectionService

    service = InspectionService()
    result = service.create_inspection(db, data, operator_id=1)
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from server.schemas.log_schema import LogBase
from server.services.log_service import LogService
from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
)
from server.enums.action_type import ActionType
from server.enums.inspection_result import InspectionResult
from server.enums.task_process_status import TrialTaskProcessStatus
from server.enums.task_result_status import TrialTaskResultStatus
from server.models import (
    GrindingRecord,
    InspectionRecord,
    TrialTask,
)
from server.schemas.inspection_schema import (
    InspectionCreate,
    InspectionUpdate,
    InspectionResponse,
    InspectionListResponse,
)

logger = logging.getLogger("gtms.server")


# ============================================================
# InspectionService
# ============================================================


class InspectionService:

    """检测记录业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    权限检查由 Router 层负责，本层不处理权限。
    状态流转由本层统一负责，外部不得绕过。
    """

    _log_service = LogService()

    # ============================================================
    # 公开 API：列表查询
    # ============================================================

    def list_inspections(
        self,
        db: Session,
        *,
        task_id: Optional[int] = None,
        inspector_id: Optional[int] = None,
        result: Optional[InspectionResult] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> InspectionListResponse:
        """分页查询检测记录列表。

        支持按 task_id、inspector_id、result 筛选，按 created_at DESC 排序。

        Args:
            db: 数据库会话。
            task_id: 关联试磨任务 ID（可选）。
            inspector_id: 检测人 ID（可选）。
            result: 检测结论筛选（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            InspectionListResponse: 包含 items 与 total。
        """
        query = db.query(InspectionRecord).filter(
            InspectionRecord.is_deleted.is_(False)
        )

        # 按 task_id 筛选
        if task_id is not None:
            query = query.filter(InspectionRecord.task_id == task_id)

        # 按 inspector_id 筛选
        if inspector_id is not None:
            query = query.filter(
                InspectionRecord.inspector_id == inspector_id
            )

        # 按 result 筛选
        if result is not None:
            query = query.filter(InspectionRecord.result == result)

        # 总数
        total = query.count()

        # 分页 + 排序（created_at DESC）
        offset = (page - 1) * page_size
        items = (
            query.order_by(InspectionRecord.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # 转换为响应
        responses = [self._to_response(item) for item in items]

        return InspectionListResponse(items=responses, total=total)

    # ============================================================
    # 公开 API：查询单个检测记录
    # ============================================================

    def get_inspection(
        self,
        db: Session,
        inspection_id: int,
    ) -> InspectionResponse:
        """根据 ID 查询检测记录。

        过滤 is_deleted=False 的记录。

        Args:
            db: 数据库会话。
            inspection_id: 检测记录 ID。

        Returns:
            InspectionResponse: 检测记录信息。

        Raises:
            NotFoundException: 检测记录不存在或已删除。
        """
        inspection = self._get_inspection_orm(db, inspection_id)
        return self._to_response(inspection)

    # ============================================================
    # 公开 API：创建检测记录（上传检测报告）
    # ============================================================

    def create_inspection(
        self,
        db: Session,
        data: InspectionCreate,
        operator_id: int,
    ) -> InspectionResponse:
        """创建检测记录（上传检测报告）。

        流程:
            ① 校验 TrialTask 存在且未删除
            ② 校验 GrindingRecord 存在（必须先完成试磨开始）
            ③ 校验 task_id 未重复创建检测记录（UNIQUE 约束）
            ④ 创建 InspectionRecord ORM
            ⑤ 提交事务
            ⑥ 写入 SystemLog（Inspection Created）

        Args:
            db: 数据库会话。
            data: 检测创建数据（InspectionCreate Schema）。
            operator_id: 操作人 ID。

        Returns:
            InspectionResponse: 新创建的检测记录。

        Raises:
            NotFoundException: 试磨任务不存在或未开始试磨。
            BusinessLogicException: 已存在检测记录。
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

        # ② 校验 GrindingRecord 存在
        grinding = (
            db.query(GrindingRecord)
            .filter(
                GrindingRecord.task_id == data.task_id,
                GrindingRecord.is_deleted.is_(False),
            )
            .first()
        )
        if grinding is None:
            raise BusinessLogicException(
                "该任务尚未开始试磨，无法创建检测记录",
                detail={"task_id": data.task_id},
            )

        # ③ 校验 task_id 未重复创建检测记录
        existing = (
            db.query(InspectionRecord)
            .filter(
                InspectionRecord.task_id == data.task_id,
                InspectionRecord.is_deleted.is_(False),
            )
            .first()
        )
        if existing is not None:
            raise BusinessLogicException(
                "该任务已创建检测记录，不可重复创建",
                detail={"task_id": data.task_id},
            )

        # ④ 创建 InspectionRecord ORM
        inspection = InspectionRecord(
            task_id=data.task_id,
            report_path=data.report_path,
            accuracy=data.accuracy,
            roughness=data.roughness,
            result=data.result,
            inspector_id=data.inspector_id,
            created_by=operator_id,
        )
        db.add(inspection)
        db.flush()

        try:
            # ⑤ 提交事务
            db.commit()

            # ⑥ 写入 SystemLog
            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.CREATE,
                target_type="Inspection",
                target_id=inspection.id,
                changes={
                    "task_id": data.task_id,
                    "inspector_id": data.inspector_id,
                },
            )

            db.refresh(inspection)
            logger.info(
                "检测记录创建成功: inspection_id=%s, task_id=%s, operator_id=%s",
                inspection.id, data.task_id, operator_id,
            )
            return self._to_response(inspection)

        except Exception:
            db.rollback()
            logger.exception(
                "检测记录创建失败: task_id=%s", data.task_id
            )
            raise

    # ============================================================
    # 公开 API：完成检测
    # ============================================================

    def finish_inspection(
        self,
        db: Session,
        inspection_id: int,
        result: InspectionResult,
        failure_reason: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> InspectionResponse:
        """完成检测并推进任务状态至 DISPATCHED。

        流程:
            ① 校验 InspectionRecord 存在
            ② 校验 TrialTask 当前 process_status 为 GRINDING
            ③ 校验 result=FAIL 时 failure_reason 必填
            ④ 更新 InspectionRecord（result, failure_reason）
            ⑤ 设置 TrialTask.result_status
            ⑥ 推进 TrialTask.process_status → DISPATCHED
            ⑦ 提交事务
            ⑧ 写入 SystemLog

        Args:
            db: 数据库会话。
            inspection_id: 检测记录 ID。
            result: 检测结论（PASS 或 FAIL）。
            failure_reason: 不合格原因（result=FAIL 时必填）。
            operator_id: 操作人 ID。

        Returns:
            InspectionResponse: 更新后的检测记录。

        Raises:
            NotFoundException: 检测记录或任务不存在。
            BusinessLogicException: 状态非法或 failure_reason 缺失。
        """
        # ① 校验 InspectionRecord 存在
        inspection = self._get_inspection_orm(db, inspection_id)

        # ② 校验 TrialTask 存在且 process_status 为 GRINDING
        task = (
            db.query(TrialTask)
            .filter(
                TrialTask.id == inspection.task_id,
                TrialTask.is_deleted.is_(False),
            )
            .first()
        )
        if task is None:
            raise NotFoundException(
                "关联试磨任务不存在",
                detail={"task_id": inspection.task_id},
            )

        if task.process_status != TrialTaskProcessStatus.GRINDING:
            raise BusinessLogicException(
                "仅试磨中状态的任务可完成检测，"
                f"当前状态: {task.process_status.value}",
                detail={
                    "task_id": task.id,
                    "current_status": task.process_status.value,
                },
            )

        # ③ 校验 result=FAIL 时 failure_reason 必填
        if result == InspectionResult.FAIL:
            if not failure_reason or not failure_reason.strip():
                raise BusinessLogicException(
                    "检测不合格时 failure_reason 必须填写",
                    detail={"inspection_id": inspection_id},
                )

        # ④ 更新 InspectionRecord
        changes: dict = {}
        old_result = inspection.result
        if old_result != result:
            changes["result"] = {
                "old": old_result.value if old_result else None,
                "new": result.value,
            }
            inspection.result = result

        if failure_reason is not None:
            changes["failure_reason"] = {
                "old": None,
                "new": failure_reason,
            }

        if operator_id is not None:
            inspection.updated_by = operator_id

        # ⑤ 设置 TrialTask.result_status
        old_result_status = task.result_status
        if result == InspectionResult.PASS:
            task.result_status = TrialTaskResultStatus.PASSED
        else:
            task.result_status = TrialTaskResultStatus.FAILED

        # ⑥ 推进 TrialTask.process_status → DISPATCHED
        old_process_status = task.process_status
        task.process_status = TrialTaskProcessStatus.DISPATCHED
        if operator_id is not None:
            task.updated_by = operator_id

        try:
            # ⑦ 提交事务
            db.commit()

            # ⑧ 写入 SystemLog
            changes["result_status"] = {
                "old": old_result_status.value,
                "new": task.result_status.value,
            }
            self._write_log(
                db,
                operator_id=operator_id or 0,
                action=ActionType.UPDATE,
                target_type="Inspection",
                target_id=inspection.id,
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
                        "new": task.result_status.value,
                    },
                },
            )

            db.refresh(inspection)
            logger.info(
                "检测完成: inspection_id=%s, task_id=%s, result=%s",
                inspection_id, task.id, result.value,
            )
            return self._to_response(inspection)

        except Exception:
            db.rollback()
            logger.exception(
                "检测完成失败: inspection_id=%s", inspection_id
            )
            raise

    # ============================================================
    # 公开 API：更新检测记录
    # ============================================================

    def update_inspection(
        self,
        db: Session,
        inspection_id: int,
        data: InspectionUpdate,
        operator_id: int,
    ) -> InspectionResponse:
        """更新检测记录（不涉及状态流转）。

        仅更新传入的非 None 字段（exclude_unset）。
        如需完成检测，请使用 finish_inspection()。

        Args:
            db: 数据库会话。
            inspection_id: 检测记录 ID。
            data: 更新数据（InspectionUpdate Schema）。
            operator_id: 操作人 ID。

        Returns:
            InspectionResponse: 更新后的检测记录。

        Raises:
            NotFoundException: 检测记录不存在。
        """
        inspection = self._get_inspection_orm(db, inspection_id)

        # 记录变更
        changes: dict = {}
        update_data = data.model_dump(exclude_unset=True)

        for field_name, new_value in update_data.items():
            old_value = getattr(inspection, field_name)
            if new_value is not None and new_value != old_value:
                changes[field_name] = {
                    "old": (
                        old_value.value
                        if isinstance(old_value, InspectionResult)
                        else old_value
                    ),
                    "new": (
                        new_value.value
                        if isinstance(new_value, InspectionResult)
                        else new_value
                    ),
                }
                setattr(inspection, field_name, new_value)

        if not changes:
            return self._to_response(inspection)

        try:
            inspection.updated_by = operator_id
            db.flush()

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.UPDATE,
                target_type="Inspection",
                target_id=inspection.id,
                changes=changes,
            )

            db.commit()
            db.refresh(inspection)
            logger.info(
                "检测记录更新成功: inspection_id=%s, fields=%s",
                inspection_id, list(changes.keys()),
            )
            return self._to_response(inspection)

        except Exception:
            db.rollback()
            logger.exception(
                "检测记录更新失败: inspection_id=%s", inspection_id
            )
            raise

    # ============================================================
    # 公开 API：删除检测记录
    # ============================================================

    def delete_inspection(
        self,
        db: Session,
        inspection_id: int,
        operator_id: int,
    ) -> None:
        """软删除检测记录。

        设置 is_deleted=True，不物理删除。

        Args:
            db: 数据库会话。
            inspection_id: 检测记录 ID。
            operator_id: 操作人 ID。

        Raises:
            NotFoundException: 检测记录不存在。
        """
        inspection = self._get_inspection_orm(db, inspection_id)

        try:
            inspection.is_deleted = True
            inspection.updated_by = operator_id
            db.flush()

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.DELETE,
                target_type="Inspection",
                target_id=inspection.id,
                changes={"task_id": inspection.task_id},
            )

            db.commit()
            logger.info(
                "检测记录已删除: inspection_id=%s, task_id=%s, operator_id=%s",
                inspection_id, inspection.task_id, operator_id,
            )

        except Exception:
            db.rollback()
            logger.exception(
                "检测记录删除失败: inspection_id=%s", inspection_id
            )
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    def _get_inspection_orm(
        self, db: Session, inspection_id: int
    ) -> InspectionRecord:
        """获取 ORM 实例（内部使用）。

        Args:
            db: 数据库会话。
            inspection_id: 检测记录 ID。

        Returns:
            InspectionRecord ORM 实例。

        Raises:
            NotFoundException: 检测记录不存在或已删除。
        """
        inspection = (
            db.query(InspectionRecord)
            .filter(
                InspectionRecord.id == inspection_id,
                InspectionRecord.is_deleted.is_(False),
            )
            .first()
        )
        if inspection is None:
            raise NotFoundException(
                "检测记录不存在",
                detail={"inspection_id": inspection_id},
            )
        return inspection

    def _to_response(
        self, inspection: InspectionRecord
    ) -> InspectionResponse:
        """将 InspectionRecord ORM 实例转换为 InspectionResponse。

        Args:
            inspection: InspectionRecord ORM 实例。

        Returns:
            InspectionResponse: 检测记录响应 Schema。
        """
        return InspectionResponse(
            id=inspection.id,
            task_id=inspection.task_id,
            report_path=inspection.report_path,
            accuracy=inspection.accuracy,
            roughness=inspection.roughness,
            result=inspection.result,
            inspector_id=inspection.inspector_id,
            created_at=inspection.created_at,
            updated_at=inspection.updated_at,
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
        """写入系统操作日志（委托 LogService）。

        Args:
            db: 数据库会话。
            operator_id: 操作人 ID。
            action: 操作类型。
            target_type: 操作对象类型。
            target_id: 操作对象 ID。
            changes: 变更内容（可选）。
        """
        import json
        log_base = LogBase(
            operator_id=operator_id,
            operation=action,
            module=target_type,
            target_type=target_type,
            target_id=target_id,
            description=(
                json.dumps(changes, ensure_ascii=False, default=str)
                if changes else None
            ),
        )
        self._log_service.create_log(db, log_base)


__all__ = [
    "InspectionService",
]
