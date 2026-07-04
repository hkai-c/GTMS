"""试磨任务业务层 (Task Service)

Sprint 2 — Task 2.5
严格依据 DB_DESIGN.md、SRS.md、CODE_WIKI.md。

提供 TrialTask 的完整 CRUD 业务逻辑，包括：
    - 创建任务（自动生成编号）
    - 查询任务（分页、筛选）
    - 更新任务（仅 CREATED 状态可编辑）
    - 删除任务（软删除，需管理员权限）
    - 所有操作自动记录 SystemLog

异常体系：
    使用 Task 2.1 冻结的异常类：
    - BusinessLogicException (400) — 替代 ValidationException
    - PermissionDeniedException (403) — 替代 AuthorizationException
    - NotFoundException (404)
    - DuplicateException (409) — 替代 ConflictException

使用方式:
    from server.services import TaskService

    service = TaskService()
    task = service.create_task(db, current_user, data)
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from server.enums import (
    ActionType,
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
)
from server.models import Customer, SystemLog, TrialTask, User
from server.utils.id_generator import generate_task_no

logger = logging.getLogger(__name__)


# ============================================================
# 输入 Schema（dataclass，后续 Sprint 3 迁移到 Pydantic）
# ============================================================


@dataclass
class TaskCreate:
    """创建任务输入。

    Attributes:
        customer_id: 客户 ID。
        requirement: 加工要求。
        tracking_no: 快递单号（可选）。
    """

    customer_id: int
    requirement: str
    tracking_no: Optional[str] = None


@dataclass
class TaskUpdate:
    """更新任务输入。

    仅 process_status=CREATED 时可编辑。

    Attributes:
        customer_id: 客户 ID（可选）。
        requirement: 加工要求（可选）。
        tracking_no: 快递单号（可选）。
    """

    customer_id: Optional[int] = None
    requirement: Optional[str] = None
    tracking_no: Optional[str] = None


@dataclass
class TaskFilter:
    """任务列表筛选条件。

    Attributes:
        task_no: 任务编号（模糊匹配）。
        customer_id: 客户 ID。
        process_status: 流程状态。
        result_status: 结果状态。
        date_from: 创建日期起。
        date_to: 创建日期止。
    """

    task_no: Optional[str] = None
    customer_id: Optional[int] = None
    process_status: Optional[TrialTaskProcessStatus] = None
    result_status: Optional[TrialTaskResultStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


# ============================================================
# TaskService
# ============================================================


class TaskService:
    """试磨任务业务服务。

    所有数据库操作均通过 SQLAlchemy Session 进行。
    事务管理：try → commit → except rollback → finally 不自动 close。
    """

    # ============================================================
    # 创建任务
    # ============================================================

    def create_task(
        self,
        db: Session,
        current_user: User,
        data: TaskCreate,
    ) -> TrialTask:
        """创建试磨任务。

        业务流程:
            1. 调用 generate_task_no(db) 自动生成任务编号
            2. 设置 process_status=CREATED, result_status=PENDING
            3. 设置 created_by=current_user.id
            4. 自动写入 SystemLog
            5. commit 并返回 TrialTask

        Args:
            db: 数据库会话。
            current_user: 当前登录用户。
            data: 任务创建数据。

        Returns:
            新创建的 TrialTask 实例。

        Raises:
            BusinessLogicException: 客户不存在或参数无效时抛出。
        """
        # 验证客户存在
        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if customer is None:
            raise BusinessLogicException(
                f"客户不存在: id={data.customer_id}",
                detail={"customer_id": data.customer_id},
            )

        try:
            # 生成任务编号
            task_no = generate_task_no(db)

            task = TrialTask(
                task_no=task_no,
                customer_id=data.customer_id,
                requirement=data.requirement,
                tracking_no=data.tracking_no,
                sales_id=current_user.id,
                process_status=TrialTaskProcessStatus.CREATED,
                result_status=TrialTaskResultStatus.PENDING,
                created_by=current_user.id,
            )
            db.add(task)
            db.flush()  # 获取 task.id

            # 写入操作日志
            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.CREATE,
                target_type="TrialTask",
                target_id=task.id,
                changes={"task_no": task_no, "customer_id": data.customer_id},
            )

            db.commit()
            logger.info(
                "任务创建成功: task_no=%s, id=%s, user=%s",
                task_no, task.id, current_user.username,
            )
            return task

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 查询单个任务
    # ============================================================

    def get_task(self, db: Session, task_id: int) -> TrialTask:
        """根据 ID 查询试磨任务。

        自动过滤 is_deleted=True 的记录。

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

    # ============================================================
    # 查询任务列表
    # ============================================================

    def list_tasks(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[TaskFilter] = None,
    ) -> tuple[list[TrialTask], int]:
        """分页查询试磨任务列表。

        支持多条件筛选: task_no, customer_id, process_status,
        result_status, date_from, date_to。

        自动过滤 is_deleted=True 的记录。

        Args:
            db: 数据库会话。
            page: 页码（从 1 开始）。
            page_size: 每页条数。
            filters: 筛选条件。

        Returns:
            (items, total) 元组。
        """
        conditions = [TrialTask.is_deleted == False]  # noqa: E712

        if filters is not None:
            if filters.task_no:
                conditions.append(
                    TrialTask.task_no.like(f"%{filters.task_no}%")
                )
            if filters.customer_id is not None:
                conditions.append(TrialTask.customer_id == filters.customer_id)
            if filters.process_status is not None:
                conditions.append(
                    TrialTask.process_status == filters.process_status
                )
            if filters.result_status is not None:
                conditions.append(
                    TrialTask.result_status == filters.result_status
                )
            if filters.date_from is not None:
                conditions.append(
                    TrialTask.created_at >= filters.date_from
                )
            if filters.date_to is not None:
                conditions.append(
                    TrialTask.created_at <= filters.date_to
                )

        query = db.query(TrialTask).filter(and_(*conditions))

        total = query.count()
        items = (
            query
            .order_by(TrialTask.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    # ============================================================
    # 更新任务
    # ============================================================

    def update_task(
        self,
        db: Session,
        task_id: int,
        current_user: User,
        data: TaskUpdate,
    ) -> TrialTask:
        """更新试磨任务。

        业务规则:
            - 仅 process_status=CREATED 状态允许编辑
            - 可修改: customer_id, requirement, tracking_no
            - 禁止修改: task_no
            - 自动写入 SystemLog

        Args:
            db: 数据库会话。
            task_id: 任务 ID。
            current_user: 当前登录用户。
            data: 更新数据。

        Returns:
            更新后的 TrialTask 实例。

        Raises:
            NotFoundException: 任务不存在。
            BusinessLogicException: 状态不允许编辑。
        """
        task = self.get_task(db, task_id)

        if task.process_status != TrialTaskProcessStatus.CREATED:
            raise BusinessLogicException(
                f"仅创建状态的任务可编辑，当前状态: {task.process_status.value}",
                detail={
                    "task_id": task_id,
                    "current_status": task.process_status.value,
                },
            )

        changes = {}

        if data.customer_id is not None and data.customer_id != task.customer_id:
            # 验证客户存在
            customer = (
                db.query(Customer)
                .filter(Customer.id == data.customer_id)
                .first()
            )
            if customer is None:
                raise BusinessLogicException(
                    f"客户不存在: id={data.customer_id}",
                    detail={"customer_id": data.customer_id},
                )
            changes["customer_id"] = {"old": task.customer_id, "new": data.customer_id}
            task.customer_id = data.customer_id

        if data.requirement is not None and data.requirement != task.requirement:
            changes["requirement"] = {"old": task.requirement, "new": data.requirement}
            task.requirement = data.requirement

        if data.tracking_no is not None and data.tracking_no != task.tracking_no:
            changes["tracking_no"] = {"old": task.tracking_no, "new": data.tracking_no}
            task.tracking_no = data.tracking_no

        if not changes:
            return task  # 无变更

        try:
            task.updated_by = current_user.id
            db.flush()

            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.UPDATE,
                target_type="TrialTask",
                target_id=task.id,
                changes=changes,
            )

            db.commit()
            logger.info(
                "任务更新成功: task_id=%s, fields=%s, user=%s",
                task_id, list(changes.keys()), current_user.username,
            )
            return task

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 删除任务（软删除）
    # ============================================================

    def delete_task(
        self,
        db: Session,
        task_id: int,
        current_user: User,
    ) -> None:
        """软删除试磨任务。

        仅管理员可执行删除操作。
        软删除: 设置 is_deleted=True。

        Args:
            db: 数据库会话。
            task_id: 任务 ID。
            current_user: 当前登录用户。

        Raises:
            NotFoundException: 任务不存在。
            PermissionDeniedException: 非管理员用户。
        """
        task = self.get_task(db, task_id)

        # 管理员权限检查
        user_role_names = {role.name for role in current_user.roles}
        if "administrator" not in user_role_names:
            raise PermissionDeniedException(
                "仅管理员可删除任务",
                detail={
                    "task_id": task_id,
                    "user_roles": sorted(user_role_names),
                },
            )

        try:
            task.is_deleted = True
            task.updated_by = current_user.id
            db.flush()

            self._log_action(
                db=db,
                user_id=current_user.id,
                action=ActionType.DELETE,
                target_type="TrialTask",
                target_id=task.id,
                changes={"task_no": task.task_no},
            )

            db.commit()
            logger.info(
                "任务已删除: task_id=%s, task_no=%s, user=%s",
                task_id, task.task_no, current_user.username,
            )

        except Exception:
            db.rollback()
            raise

    # ============================================================
    # 私有方法
    # ============================================================

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
    "TaskService",
    "TaskCreate",
    "TaskUpdate",
    "TaskFilter",
]