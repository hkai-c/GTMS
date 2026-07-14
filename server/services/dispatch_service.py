"""工件派发业务层 (Dispatch Service)

Sprint 9 — Task 9.2
依据 SRS §4.7、Dispatch ORM、Dispatch Schema (Task 9.1)、
    Sprint 1~9 Frozen API。

提供 Dispatch 的完整 CRUD 业务逻辑，包括：
    - 创建派发记录（校验 TrialTask + InspectionRecord + 状态机）
    - 更新派发记录（无需状态变更的字段修改）
    - 查询派发记录（分页、筛选、排序）
    - 删除派发记录（软删除）
    - 所有写操作自动记录 SystemLog

公开 API:
    - list_dispatches(db, *, direction, task_id, page, page_size)
        -> DispatchListResponse
    - get_dispatch(db, dispatch_id) -> DispatchResponse
    - create_dispatch(db, data, operator_id) -> DispatchResponse
    - update_dispatch(db, dispatch_id, data, operator_id) -> DispatchResponse
    - delete_dispatch(db, dispatch_id, operator_id) -> None

使用方式:
    from server.services.dispatch_service import DispatchService

    service = DispatchService()
    result = service.create_dispatch(db, data, operator_id=1)
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
)
from server.enums import (
    ActionType,
    DestinationType,
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
)
from server.models import (
    Dispatch,
    InspectionRecord,
    SystemLog,
    TrialTask,
)
from server.schemas.dispatch_schema import (
    DispatchCreate,
    DispatchUpdate,
    DispatchResponse,
    DispatchListResponse,
)

logger = logging.getLogger("gtms.server")


# ============================================================
# DispatchService
# ============================================================


class DispatchService:
    """工件派发业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    权限检查由 Router 层负责，本层不处理权限。
    状态流转由本层统一负责，外部不得绕过。
    """

    # ============================================================
    # 公开 API：列表查询
    # ============================================================

    def list_dispatches(
        self,
        db: Session,
        *,
        direction: Optional[DestinationType] = None,
        task_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> DispatchListResponse:
        """分页查询派发记录列表。

        支持按 direction、task_id 筛选，按 created_at DESC 排序。

        Args:
            db: 数据库会话。
            direction: 去向方向筛选（可选）。
            task_id: 关联试磨任务 ID（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            DispatchListResponse: 包含 items 与 total。
        """
        query = db.query(Dispatch).filter(
            Dispatch.is_deleted.is_(False)
        )

        # 按 direction 筛选
        if direction is not None:
            query = query.filter(Dispatch.direction == direction)

        # 按 task_id 筛选
        if task_id is not None:
            query = query.filter(Dispatch.task_id == task_id)

        # 总数
        total = query.count()

        # 分页 + 排序（created_at DESC）
        offset = (page - 1) * page_size
        items = (
            query.order_by(Dispatch.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # 转换为响应
        responses = [self._to_response(item) for item in items]

        return DispatchListResponse(items=responses, total=total)

    # ============================================================
    # 公开 API：查询单个派发记录
    # ============================================================

    def get_dispatch(
        self,
        db: Session,
        dispatch_id: int,
    ) -> DispatchResponse:
        """根据 ID 查询派发记录。

        过滤 is_deleted=False 的记录。

        Args:
            db: 数据库会话。
            dispatch_id: 派发记录 ID。

        Returns:
            DispatchResponse: 派发记录信息。

        Raises:
            NotFoundException: 派发记录不存在或已删除。
        """
        dispatch = self._get_dispatch_orm(db, dispatch_id)
        return self._to_response(dispatch)

    # ============================================================
    # 公开 API：创建派发记录
    # ============================================================

    def create_dispatch(
        self,
        db: Session,
        data: DispatchCreate,
        operator_id: int,
    ) -> DispatchResponse:
        """创建工件派发记录。

        流程:
            ① 校验 TrialTask 存在且未删除
            ② 校验 InspectionRecord 存在（必须已完成检测）
            ③ 校验 Dispatch 不重复（task_id UNIQUE）
            ④ 校验 result_status == PASSED
            ⑤ 校验 process_status == GRINDING
            ⑥ 创建 DispatchRecord ORM
            ⑦ 推进 TrialTask.process_status → DISPATCHED
            ⑧ 提交事务
            ⑨ 写入 SystemLog（CREATE + STATUS_CHANGE）

        Args:
            db: 数据库会话。
            data: 派发创建数据（DispatchCreate Schema）。
            operator_id: 操作人 ID。

        Returns:
            DispatchResponse: 新创建的派发记录。

        Raises:
            NotFoundException: 试磨任务不存在或检测记录不存在。
            BusinessLogicException: 状态不符合条件或已存在派发记录。
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

        # ② 校验 InspectionRecord 存在
        inspection = (
            db.query(InspectionRecord)
            .filter(
                InspectionRecord.task_id == data.task_id,
                InspectionRecord.is_deleted.is_(False),
            )
            .first()
        )
        if inspection is None:
            raise BusinessLogicException(
                "该任务尚未完成检测，无法派发",
                detail={"task_id": data.task_id},
            )

        # ③ 校验 Dispatch 不重复
        existing = (
            db.query(Dispatch)
            .filter(
                Dispatch.task_id == data.task_id,
                Dispatch.is_deleted.is_(False),
            )
            .first()
        )
        if existing is not None:
            raise BusinessLogicException(
                "该任务已创建派发记录，不可重复创建",
                detail={"task_id": data.task_id},
            )

        # ④ 校验 result_status == PASSED
        if task.result_status != TrialTaskResultStatus.PASSED:
            raise BusinessLogicException(
                "仅检测合格的任务可派发，"
                f"当前结果: {task.result_status.value}",
                detail={
                    "task_id": data.task_id,
                    "current_result": task.result_status.value,
                },
            )

        # ⑤ 校验 process_status == GRINDING
        if task.process_status != TrialTaskProcessStatus.GRINDING:
            raise BusinessLogicException(
                "仅试磨中状态的任务可派发，"
                f"当前状态: {task.process_status.value}",
                detail={
                    "task_id": data.task_id,
                    "current_status": task.process_status.value,
                },
            )

        # ⑥ 创建 DispatchRecord ORM
        dispatch = Dispatch(
            task_id=data.task_id,
            direction=data.direction.value,
            dispatch_date=data.dispatch_date,
            operator_id=data.operator_id,
            created_by=operator_id,
        )
        db.add(dispatch)
        db.flush()

        # ⑦ 推进 TrialTask.process_status → DISPATCHED
        old_process_status = task.process_status
        task.process_status = TrialTaskProcessStatus.DISPATCHED
        task.updated_by = operator_id

        try:
            # ⑧ 提交事务
            db.commit()

            # ⑨ 写入 SystemLog（CREATE + STATUS_CHANGE）
            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.CREATE,
                target_type="Dispatch",
                target_id=dispatch.id,
                changes={
                    "task_id": data.task_id,
                    "direction": data.direction.value,
                    "dispatch_date": data.dispatch_date.isoformat(),
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
                        "old": old_process_status.value,
                        "new": task.process_status.value,
                    },
                },
            )

            db.refresh(dispatch)
            logger.info(
                "派发记录创建成功: dispatch_id=%s, task_id=%s, operator_id=%s",
                dispatch.id, data.task_id, operator_id,
            )
            return self._to_response(dispatch)

        except Exception:
            db.rollback()
            logger.exception(
                "派发记录创建失败: task_id=%s", data.task_id
            )
            raise

    # ============================================================
    # 公开 API：更新派发记录
    # ============================================================

    def update_dispatch(
        self,
        db: Session,
        dispatch_id: int,
        data: DispatchUpdate,
        operator_id: int,
    ) -> DispatchResponse:
        """更新派发记录（不涉及状态流转）。

        仅更新传入的非 None 字段（exclude_unset）。

        Args:
            db: 数据库会话。
            dispatch_id: 派发记录 ID。
            data: 更新数据（DispatchUpdate Schema）。
            operator_id: 操作人 ID。

        Returns:
            DispatchResponse: 更新后的派发记录。

        Raises:
            NotFoundException: 派发记录不存在。
        """
        dispatch = self._get_dispatch_orm(db, dispatch_id)

        # 记录变更
        changes: dict = {}
        update_data = data.model_dump(exclude_unset=True)

        for field_name, new_value in update_data.items():
            old_value = getattr(dispatch, field_name)
            if new_value is not None and new_value != old_value:
                changes[field_name] = {
                    "old": (
                        old_value.value
                        if isinstance(old_value, DestinationType)
                        else (
                            old_value.isoformat()
                            if hasattr(old_value, "isoformat")
                            else old_value
                        )
                    ),
                    "new": (
                        new_value.value
                        if isinstance(new_value, DestinationType)
                        else (
                            new_value.isoformat()
                            if hasattr(new_value, "isoformat")
                            else new_value
                        )
                    ),
                }
                setattr(dispatch, field_name, new_value)

        if not changes:
            return self._to_response(dispatch)

        try:
            dispatch.updated_by = operator_id
            db.flush()

            # 写入 SystemLog
            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.UPDATE,
                target_type="Dispatch",
                target_id=dispatch.id,
                changes=changes,
            )

            db.commit()
            db.refresh(dispatch)
            logger.info(
                "派发记录更新成功: dispatch_id=%s, fields=%s",
                dispatch_id, list(changes.keys()),
            )
            return self._to_response(dispatch)

        except Exception:
            db.rollback()
            logger.exception(
                "派发记录更新失败: dispatch_id=%s", dispatch_id
            )
            raise

    # ============================================================
    # 公开 API：删除派发记录
    # ============================================================

    def delete_dispatch(
        self,
        db: Session,
        dispatch_id: int,
        operator_id: int,
    ) -> None:
        """软删除派发记录。

        设置 is_deleted=True，不物理删除。

        Args:
            db: 数据库会话。
            dispatch_id: 派发记录 ID。
            operator_id: 操作人 ID。

        Raises:
            NotFoundException: 派发记录不存在。
        """
        dispatch = self._get_dispatch_orm(db, dispatch_id)

        try:
            dispatch.is_deleted = True
            dispatch.updated_by = operator_id
            db.flush()

            # 写入 SystemLog
            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.DELETE,
                target_type="Dispatch",
                target_id=dispatch.id,
                changes={"task_id": dispatch.task_id},
            )

            db.commit()
            logger.info(
                "派发记录已删除: dispatch_id=%s, task_id=%s, operator_id=%s",
                dispatch_id, dispatch.task_id, operator_id,
            )

        except Exception:
            db.rollback()
            logger.exception(
                "派发记录删除失败: dispatch_id=%s", dispatch_id
            )
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    def _get_dispatch_orm(
        self, db: Session, dispatch_id: int
    ) -> Dispatch:
        """获取 ORM 实例（内部使用）。

        Args:
            db: 数据库会话。
            dispatch_id: 派发记录 ID。

        Returns:
            Dispatch ORM 实例。

        Raises:
            NotFoundException: 派发记录不存在或已删除。
        """
        dispatch = (
            db.query(Dispatch)
            .filter(
                Dispatch.id == dispatch_id,
                Dispatch.is_deleted.is_(False),
            )
            .first()
        )
        if dispatch is None:
            raise NotFoundException(
                "派发记录不存在",
                detail={"dispatch_id": dispatch_id},
            )
        return dispatch

    def _to_response(
        self, dispatch: Dispatch
    ) -> DispatchResponse:
        """将 Dispatch ORM 实例转换为 DispatchResponse。

        Args:
            dispatch: Dispatch ORM 实例。

        Returns:
            DispatchResponse: 派发记录响应 Schema。
        """
        return DispatchResponse(
            id=dispatch.id,
            task_id=dispatch.task_id,
            direction=DestinationType(dispatch.direction),
            dispatch_date=dispatch.dispatch_date,
            operator_id=dispatch.operator_id,
            created_at=dispatch.created_at,
            updated_at=dispatch.updated_at,
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
    "DispatchService",
]
