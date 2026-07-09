"""试磨任务业务层 (Task Service)

Sprint 5 — Task 5.2
严格依据 SRS §4.3、TrialTask ORM、TrialTask Schema (Task 5.1)、Sprint 2 Frozen API。

提供 TrialTask 的完整 CRUD 业务逻辑，包括：
    - 创建任务（自动生成编号、校验客户与销售存在）
    - 查询任务（分页、多条件筛选、排序）
    - 更新任务（仅 CREATED 状态可编辑基本信息）
    - 删除任务（软删除）
    - 状态流转校验（使用枚举 next_statuses）
    - 所有写操作自动记录 SystemLog

公开 API:
    - list_tasks(db, *, task_no, customer_id, process_status, result_status, sales_id, page, page_size) -> TrialTaskListResponse
    - get_task(db, task_id) -> TrialTaskResponse
    - create_task(db, data, operator_id) -> TrialTaskResponse
    - update_task(db, task_id, data, operator_id) -> TrialTaskResponse
    - delete_task(db, task_id, operator_id) -> None

使用方式:
    from server.services.task_service import TaskService

    service = TaskService()
    result = service.list_tasks(db, process_status=TrialTaskProcessStatus.CREATED)
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
from server.enums.task_result_status import TrialTaskResultStatus
from server.models import Customer, SystemLog, TrialTask, User
from server.schemas.trial_task_schema import (
    TrialTaskCreate,
    TrialTaskUpdate,
    TrialTaskResponse,
    TrialTaskListResponse,
)
from server.utils.id_generator import generate_task_no

logger = logging.getLogger("gtms.server")


# ============================================================
# TaskService
# ============================================================


class TaskService:
    """试磨任务业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback。
    权限检查由 Router 层负责，本层不处理权限。
    """

    # ============================================================
    # 公开 API：列表查询
    # ============================================================

    def list_tasks(
        self,
        db: Session,
        *,
        task_no: Optional[str] = None,
        customer_id: Optional[int] = None,
        process_status: Optional[TrialTaskProcessStatus] = None,
        result_status: Optional[TrialTaskResultStatus] = None,
        sales_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TrialTaskListResponse:
        """分页查询试磨任务列表。

        支持多条件筛选和排序（created_at DESC）。

        Args:
            db: 数据库会话。
            task_no: 任务编号模糊搜索（可选）。
            customer_id: 客户 ID（可选）。
            process_status: 流程状态（可选）。
            result_status: 结果状态（可选）。
            sales_id: 销售 ID（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            TrialTaskListResponse: 包含 items 与 total。
        """
        query = db.query(TrialTask).filter(TrialTask.is_deleted == False)

        # 多条件筛选
        if task_no:
            query = query.filter(TrialTask.task_no.like(f"%{task_no}%"))
        if customer_id is not None:
            query = query.filter(TrialTask.customer_id == customer_id)
        if process_status is not None:
            query = query.filter(TrialTask.process_status == process_status)
        if result_status is not None:
            query = query.filter(TrialTask.result_status == result_status)
        if sales_id is not None:
            query = query.filter(TrialTask.sales_id == sales_id)

        # 总数
        total = query.count()

        # 分页 + 排序（created_at DESC）
        offset = (page - 1) * page_size
        items = (
            query.order_by(TrialTask.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # 转换为响应
        responses = [self._to_response(task) for task in items]

        return TrialTaskListResponse(items=responses, total=total)

    # ============================================================
    # 公开 API：查询单个任务
    # ============================================================

    def get_task(
        self,
        db: Session,
        task_id: int,
    ) -> TrialTaskResponse:
        """根据 ID 查询试磨任务。

        过滤 is_deleted=False 的记录。

        Args:
            db: 数据库会话。
            task_id: 任务 ID。

        Returns:
            TrialTaskResponse: 任务信息。

        Raises:
            NotFoundException: 任务不存在或已删除。
        """
        task = (
            db.query(TrialTask)
            .filter(
                TrialTask.id == task_id,
                TrialTask.is_deleted == False,
            )
            .first()
        )
        if task is None:
            raise NotFoundException(
                "任务不存在",
                detail={"task_id": task_id},
            )

        return self._to_response(task)

    # ============================================================
    # 公开 API：创建任务
    # ============================================================

    def create_task(
        self,
        db: Session,
        data: TrialTaskCreate,
        operator_id: int,
    ) -> TrialTaskResponse:
        """创建试磨任务。

        流程:
            ① 调用 generate_task_no(db) 生成唯一编号
            ② 校验 customer_id 存在
            ③ 校验 sales_id 存在
            ④ 创建 TrialTask ORM（process_status=CREATED, result_status=PENDING）
            ⑤ 提交事务
            ⑥ 写入 SystemLog（TrialTask Created）

        Args:
            db: 数据库会话。
            data: 任务创建数据（TrialTaskCreate Schema）。
            operator_id: 操作人 ID。

        Returns:
            TrialTaskResponse: 新创建的任务。

        Raises:
            BusinessLogicException: 客户或销售不存在。
        """
        # ① 生成任务编号
        task_no = generate_task_no(db)

        # ② 校验客户存在
        customer = (
            db.query(Customer)
            .filter(Customer.id == data.customer_id, Customer.is_deleted == False)
            .first()
        )
        if customer is None:
            raise BusinessLogicException(
                "客户不存在或已删除",
                detail={"customer_id": data.customer_id},
            )

        # ③ 校验销售存在
        sales = (
            db.query(User)
            .filter(User.id == data.sales_id, User.is_deleted == False)
            .first()
        )
        if sales is None:
            raise BusinessLogicException(
                "销售不存在或已禁用",
                detail={"sales_id": data.sales_id},
            )

        # ④ 创建 TrialTask ORM
        task = TrialTask(
            task_no=task_no,
            customer_id=data.customer_id,
            requirement=data.requirement,
            tracking_no=data.tracking_no,
            sales_id=data.sales_id,
            process_status=TrialTaskProcessStatus.CREATED,
            result_status=TrialTaskResultStatus.PENDING,
            destination=data.destination,
            destination_date=data.destination_date,
            failure_reason=data.failure_reason,
            created_by=operator_id,
        )
        db.add(task)
        db.flush()

        try:
            # ⑤ 提交事务
            db.commit()

            # ⑥ 写入 SystemLog
            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.CREATE,
                target_type="TrialTask",
                target_id=task.id,
                changes={"task_no": task_no, "customer_id": data.customer_id},
            )

            db.refresh(task)
            logger.info(
                "任务创建成功: task_no=%s, id=%s, operator_id=%s",
                task_no, task.id, operator_id,
            )
            return self._to_response(task)

        except Exception:
            db.rollback()
            logger.exception("任务创建失败: task_no=%s", task_no)
            raise

    # ============================================================
    # 公开 API：更新任务
    # ============================================================

    def update_task(
        self,
        db: Session,
        task_id: int,
        data: TrialTaskUpdate,
        operator_id: int,
    ) -> TrialTaskResponse:
        """更新试磨任务。

        业务规则:
            - 仅 process_status=CREATED 时可编辑基本信息
            - 可修改: customer_id, requirement, tracking_no, sales_id
            - 修改 customer_id 时校验目标客户存在
            - 修改 sales_id 时校验目标销售存在
            - 支持状态流转（process_status/result_status 变更需校验合法性）
            - 自动写入 SystemLog

        Args:
            db: 数据库会话。
            task_id: 任务 ID。
            data: 更新数据（TrialTaskUpdate Schema）。
            operator_id: 操作人 ID。

        Returns:
            TrialTaskResponse: 更新后的任务。

        Raises:
            NotFoundException: 任务不存在。
            BusinessLogicException: 状态不允许编辑或非法状态流转。
        """
        task = self._get_task_orm(db, task_id)

        # 记录变更
        changes: dict = {}
        update_data = data.model_dump(exclude_unset=True)

        # 区分状态变更与基本信息编辑
        status_fields = {"process_status", "result_status", "destination", "destination_date", "failure_reason"}
        basic_fields = {"customer_id", "requirement", "tracking_no", "sales_id"}

        # 处理基本信息编辑（仅 CREATED 状态允许）
        for field_name in basic_fields & set(update_data):
            if task.process_status != TrialTaskProcessStatus.CREATED:
                raise BusinessLogicException(
                    f"仅创建状态的任务可编辑基本信息，当前状态: {task.process_status.value}",
                    detail={
                        "task_id": task_id,
                        "current_status": task.process_status.value,
                        "attempted_field": field_name,
                    },
                )

            new_value = update_data[field_name]
            old_value = getattr(task, field_name)

            if new_value is not None and new_value != old_value:
                # 校验 customer_id 存在
                if field_name == "customer_id":
                    customer = (
                        db.query(Customer)
                        .filter(Customer.id == new_value, Customer.is_deleted == False)
                        .first()
                    )
                    if customer is None:
                        raise BusinessLogicException(
                            "客户不存在或已删除",
                            detail={"customer_id": new_value},
                        )

                # 校验 sales_id 存在
                if field_name == "sales_id":
                    sales = (
                        db.query(User)
                        .filter(User.id == new_value, User.is_deleted == False)
                        .first()
                    )
                    if sales is None:
                        raise BusinessLogicException(
                            "销售不存在或已禁用",
                            detail={"sales_id": new_value},
                        )

                changes[field_name] = {"old": old_value, "new": new_value}
                setattr(task, field_name, new_value)

        # 处理状态变更
        if "process_status" in update_data:
            new_status = update_data["process_status"]
            if new_status is not None and new_status != task.process_status:
                self._validate_process_status_change(task, new_status)
                changes["process_status"] = {
                    "old": task.process_status.value,
                    "new": new_status.value,
                }
                task.process_status = new_status

        if "result_status" in update_data:
            new_status = update_data["result_status"]
            if new_status is not None and new_status != task.result_status:
                self._validate_result_status_change(task, new_status)
                changes["result_status"] = {
                    "old": task.result_status.value,
                    "new": new_status.value,
                }
                task.result_status = new_status

        # 处理其他状态相关字段
        for field_name in ("destination", "destination_date", "failure_reason"):
            if field_name in update_data:
                new_value = update_data[field_name]
                old_value = getattr(task, field_name)
                if new_value != old_value:
                    changes[field_name] = {"old": old_value, "new": new_value}
                    setattr(task, field_name, new_value)

        if not changes:
            return self._to_response(task)

        try:
            task.updated_by = operator_id
            db.flush()

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.UPDATE,
                target_type="TrialTask",
                target_id=task.id,
                changes=changes,
            )

            db.commit()
            db.refresh(task)
            logger.info(
                "任务更新成功: task_id=%s, fields=%s, operator_id=%s",
                task_id, list(changes.keys()), operator_id,
            )
            return self._to_response(task)

        except Exception:
            db.rollback()
            logger.exception("任务更新失败: task_id=%s", task_id)
            raise

    # ============================================================
    # 公开 API：删除任务
    # ============================================================

    def delete_task(
        self,
        db: Session,
        task_id: int,
        operator_id: int,
    ) -> None:
        """软删除试磨任务。

        设置 is_deleted=True，不物理删除。
        权限检查由 Router 层负责。

        Args:
            db: 数据库会话。
            task_id: 任务 ID。
            operator_id: 操作人 ID。

        Raises:
            NotFoundException: 任务不存在。
        """
        task = self._get_task_orm(db, task_id)

        try:
            task.is_deleted = True
            task.updated_by = operator_id
            db.flush()

            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.DELETE,
                target_type="TrialTask",
                target_id=task.id,
                changes={"task_no": task.task_no},
            )

            db.commit()
            logger.info(
                "任务已删除: task_id=%s, task_no=%s, operator_id=%s",
                task_id, task.task_no, operator_id,
            )

        except Exception:
            db.rollback()
            logger.exception("任务删除失败: task_id=%s", task_id)
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    def _get_task_orm(self, db: Session, task_id: int) -> TrialTask:
        """获取 ORM 实例（内部使用）。

        Args:
            db: 数据库会话。
            task_id: 任务 ID。

        Returns:
            TrialTask ORM 实例。

        Raises:
            NotFoundException: 任务不存在或已删除。
        """
        task = (
            db.query(TrialTask)
            .filter(
                TrialTask.id == task_id,
                TrialTask.is_deleted == False,
            )
            .first()
        )
        if task is None:
            raise NotFoundException(
                "任务不存在",
                detail={"task_id": task_id},
            )
        return task

    def _to_response(self, task: TrialTask) -> TrialTaskResponse:
        """将 TrialTask ORM 实例转换为 TrialTaskResponse。

        Args:
            task: TrialTask ORM 实例。

        Returns:
            TrialTaskResponse: 任务响应 Schema。
        """
        return TrialTaskResponse(
            id=task.id,
            task_no=task.task_no,
            customer_id=task.customer_id,
            requirement=task.requirement,
            tracking_no=task.tracking_no,
            sales_id=task.sales_id,
            process_status=task.process_status,
            result_status=task.result_status,
            destination=task.destination,
            destination_date=task.destination_date,
            failure_reason=task.failure_reason,
            created_at=task.created_at,
            updated_at=task.updated_at,
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

    def _validate_process_status_change(
        self,
        task: TrialTask,
        new_status: TrialTaskProcessStatus,
    ) -> None:
        """校验流程状态流转合法性。

        使用枚举 next_statuses 属性进行检查。

        Args:
            task: 当前 TrialTask ORM 实例。
            new_status: 目标流程状态。

        Raises:
            BusinessLogicException: 非法状态流转。
        """
        allowed = task.process_status.next_statuses
        if new_status not in allowed:
            raise BusinessLogicException(
                f"非法状态流转: {task.process_status.value} → {new_status.value}",
                detail={
                    "task_id": task.id,
                    "current_status": task.process_status.value,
                    "target_status": new_status.value,
                    "allowed_statuses": [s.value for s in allowed],
                },
            )

    def _validate_result_status_change(
        self,
        task: TrialTask,
        new_status: TrialTaskResultStatus,
    ) -> None:
        """校验结果状态流转合法性。

        Args:
            task: 当前 TrialTask ORM 实例。
            new_status: 目标结果状态。

        Raises:
            BusinessLogicException: 非法结果状态流转。
        """
        allowed = task.result_status.next_statuses
        if new_status not in allowed:
            raise BusinessLogicException(
                f"非法结果状态流转: {task.result_status.value} → {new_status.value}",
                detail={
                    "task_id": task.id,
                    "current_result_status": task.result_status.value,
                    "target_result_status": new_status.value,
                    "allowed_statuses": [s.value for s in allowed],
                },
            )


__all__ = [
    "TaskService",
]
