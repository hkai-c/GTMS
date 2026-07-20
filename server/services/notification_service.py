"""消息提醒业务层 (Notification Service)

Sprint 12 — Task 12.2
依据 SRS §4.9、DB_DESIGN §4.11、CODE_WIKI §15.17。

提供消息提醒的完整业务逻辑：
    - 消息查询（分页、排序、筛选）
    - 消息创建（含重复检查、审计日志）
    - 消息标记已读
    - 自动消息生成（扫描业务数据、规则匹配、幂等）

公开 API:
    - list_notifications(db, *, user_id, ...) -> NotificationListResponse
    - get_notification(db, notification_id) -> NotificationResponse
    - create_notification(db, data) -> NotificationResponse
    - mark_as_read(db, notification_id, operator_id) -> NotificationResponse
    - mark_all_as_read(db, user_id) -> int
    - generate_notifications(db) -> int

约束:
    - 唯一消息生成入口: generate_notifications()
    - 唯一写入口: create_notification() / generate_notifications()
    - 唯一重复检查: NotificationService
    - 唯一 Audit Log 入口: LogService.create_log()
    - 幂等: generate_notifications() 连续执行不重复
    - 禁止 try/except
    - 禁止直接 ORM 写入
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.orm import Session

from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
)
from server.enums.action_type import ActionType
from server.enums.notify_type import NotifyType
from server.enums.task_process_status import TrialTaskProcessStatus
from server.enums.task_result_status import TrialTaskResultStatus
from server.models.grinding_record import GrindingRecord
from server.models.notification import Notification
from server.models.receipt import Receipt
from server.models.role import Role
from server.models.trial_task import TrialTask
from server.models.user import User
from server.schemas.log_schema import LogBase
from server.schemas.notification_schema import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
)
from server.services.log_service import LogService

logger = logging.getLogger("gtms.server")


class NotificationService:
    """消息提醒业务服务。

    独立业务模块，负责消息提醒的查询、创建、标记已读和自动生成。
    所有写操作统一事务，统一通过 LogService 记录审计日志。
    generate_notifications() 为幂等方法，依赖统一重复检查。
    """

    _log_service = LogService()

    # ============================================================
    # Public API (1): 分页查询消息提醒
    # ============================================================

    def list_notifications(
        self,
        db: Session,
        *,
        user_id: int,
        is_read: bool | None = None,
        notification_type: NotifyType | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> NotificationListResponse:
        """分页查询消息提醒列表。

        Args:
            db: 数据库会话。
            user_id: 目标用户 ID（必填，用于权限隔离）。
            is_read: 已读状态筛选。
            notification_type: 提醒类型筛选。
            page: 页码（>= 1）。
            page_size: 每页条数（1~200）。

        Returns:
            NotificationListResponse: 分页结果。
        """
        query = db.query(Notification).filter(
            Notification.is_deleted.is_(False),
            Notification.target_user_id == user_id,
        )
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        if notification_type is not None:
            query = query.filter(
                Notification.type == notification_type
            )
        total = query.count()
        query = query.order_by(desc(Notification.created_at))
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        notifications = query.all()
        items = [
            self._to_notification_response(n) for n in notifications
        ]
        logger.info(
            "list_notifications: user_id=%d, page=%d, total=%d, items=%d",
            user_id, page, total, len(items),
        )
        return NotificationListResponse(items=items, total=total)

    # ============================================================
    # Public API (2): 获取单条消息提醒
    # ============================================================

    def get_notification(
        self,
        db: Session,
        notification_id: int,
    ) -> NotificationResponse:
        """获取单条消息提醒。

        Args:
            db: 数据库会话。
            notification_id: 消息提醒 ID。

        Returns:
            NotificationResponse: 消息提醒详情。

        Raises:
            NotFoundException: 消息提醒不存在。
        """
        notification = (
            db.query(Notification)
            .filter(
                Notification.is_deleted.is_(False),
                Notification.id == notification_id,
            )
            .first()
        )
        if notification is None:
            raise NotFoundException(
                f"消息提醒不存在: id={notification_id}",
                detail={"notification_id": notification_id},
            )
        logger.debug("get_notification: id=%d", notification_id)
        return self._to_notification_response(notification)

    # ============================================================
    # Public API (3): 创建消息提醒
    # ============================================================

    def create_notification(
        self,
        db: Session,
        data: NotificationCreate,
    ) -> NotificationResponse:
        """创建消息提醒。

        包含重复检查、ORM 创建、审计日志记录。
        重复创建（相同 user_id + notification_type + target_type +
        target_id + is_read=False）抛出 BusinessLogicException。

        Args:
            db: 数据库会话。
            data: 消息提醒创建数据。

        Returns:
            NotificationResponse: 创建的消息提醒。

        Raises:
            BusinessLogicException: 重复消息提醒。
        """
        duplicate = self._find_duplicate(
            db,
            target_user_id=data.user_id,
            notification_type=data.notification_type,
            task_id=data.target_id,
        )
        if duplicate is not None:
            raise BusinessLogicException(
                "相同消息提醒已存在",
                detail={
                    "user_id": data.user_id,
                    "notification_type": data.notification_type.value,
                    "target_id": data.target_id,
                },
            )
        notification = Notification(
            task_id=data.target_id,
            type=data.notification_type,
            message=data.content,
            is_read=data.is_read,
            target_user_id=data.user_id,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        self._write_log(
            db,
            operator_id=data.user_id,
            action="create",
            target_id=notification.id,
            description=f"创建消息提醒: {data.notification_type.display_name}",
        )
        logger.info(
            "create_notification: id=%d, user_id=%d, type=%s, task_id=%d",
            notification.id,
            data.user_id,
            data.notification_type.value,
            data.target_id,
        )
        return self._to_notification_response(notification)

    # ============================================================
    # Public API (4): 标记单条消息已读
    # ============================================================

    def mark_as_read(
        self,
        db: Session,
        notification_id: int,
        operator_id: int,
    ) -> NotificationResponse:
        """标记单条消息提醒为已读。

        仅修改 is_read 和 read_time（通过 updated_at 体现），
        禁止修改任何业务状态。

        Args:
            db: 数据库会话。
            notification_id: 消息提醒 ID。
            operator_id: 操作人 ID。

        Returns:
            NotificationResponse: 更新后的消息提醒。

        Raises:
            NotFoundException: 消息提醒不存在。
        """
        notification = (
            db.query(Notification)
            .filter(
                Notification.is_deleted.is_(False),
                Notification.id == notification_id,
            )
            .first()
        )
        if notification is None:
            raise NotFoundException(
                f"消息提醒不存在: id={notification_id}",
                detail={"notification_id": notification_id},
            )
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        self._write_log(
            db,
            operator_id=operator_id,
            action="update",
            target_id=notification_id,
            description="标记消息已读",
        )
        logger.info(
            "mark_as_read: id=%d, operator_id=%d",
            notification_id, operator_id,
        )
        return self._to_notification_response(notification)

    # ============================================================
    # Public API (5): 标记全部消息已读
    # ============================================================

    def mark_all_as_read(
        self,
        db: Session,
        user_id: int,
    ) -> int:
        """标记用户全部未读消息为已读。

        Args:
            db: 数据库会话。
            user_id: 用户 ID。

        Returns:
            int: 已更新数量。
        """
        count = (
            db.query(Notification)
            .filter(
                Notification.is_deleted.is_(False),
                Notification.target_user_id == user_id,
                Notification.is_read.is_(False),
            )
            .update(
                {Notification.is_read: True},
                synchronize_session=False,
            )
        )
        db.commit()
        self._write_log(
            db,
            operator_id=user_id,
            action="update",
            target_id=0,
            description=f"标记全部消息已读: {count} 条",
        )
        logger.info(
            "mark_all_as_read: user_id=%d, count=%d", user_id, count,
        )
        return count

    # ============================================================
    # Public API (6): 自动生成消息提醒（幂等）
    # ============================================================

    def generate_notifications(
        self,
        db: Session,
    ) -> int:
        """自动生成消息提醒（幂等方法）。

        扫描业务数据，按照 §15.17 Notification Principle 中定义的
        三条规则生成消息提醒。

        规则:
            RULE-01: process_status=received 超过 48h
            RULE-02: process_status=grinding 超过 120h
            RULE-03: process_status=grinding 且 result_status=pending 超过 72h

        幂等保证: 相同用户 + 相同类型 + 相同任务 + 未读 = 仅创建一条。

        Args:
            db: 数据库会话。

        Returns:
            int: 新增消息数量。
        """
        now = datetime.now()
        new_count = 0

        # RULE-01: 收件超时（received 超 48h）
        new_count += self._generate_rule_01(db, now)

        # RULE-02: 试磨超时（grinding 超 120h）
        new_count += self._generate_rule_02(db, now)

        # RULE-03: 报告缺失（grinding + pending 超 72h）
        new_count += self._generate_rule_03(db, now)

        logger.info(
            "generate_notifications: new_count=%d", new_count,
        )
        return new_count

    # ============================================================
    # Private: 规则生成
    # ============================================================

    def _generate_rule_01(
        self, db: Session, now: datetime,
    ) -> int:
        """RULE-01: 收件超时提醒。

        process_status=received 且收件时间超过 48h。
        通知: 技术员 + 销售 + 管理员。
        """
        threshold = now - timedelta(hours=48)
        tasks = (
            db.query(TrialTask)
            .join(Receipt, TrialTask.id == Receipt.task_id)
            .filter(
                TrialTask.is_deleted.is_(False),
                TrialTask.process_status == (
                    TrialTaskProcessStatus.RECEIVED
                ),
                Receipt.created_at <= threshold,
            )
            .all()
        )
        new_count = 0
        for task in tasks:
            users = self._get_rule_01_users(db, task)
            for user_id in users:
                if self._create_if_not_exists(
                    db,
                    target_user_id=user_id,
                    notification_type=NotifyType.RECEIPT_DELAY,
                    task_id=task.id,
                    message=(
                        f"任务 {task.task_no} 已收件超过2天，"
                        f"请尽快安排试磨"
                    ),
                ):
                    new_count += 1
        return new_count

    def _generate_rule_02(
        self, db: Session, now: datetime,
    ) -> int:
        """RULE-02: 试磨超时提醒。

        process_status=grinding 且试磨开始时间超过 120h。
        通知: 试磨责任人 + 销售 + 管理员。
        """
        threshold = now - timedelta(hours=120)
        tasks = (
            db.query(TrialTask)
            .join(
                GrindingRecord,
                TrialTask.id == GrindingRecord.task_id,
            )
            .filter(
                TrialTask.is_deleted.is_(False),
                TrialTask.process_status == (
                    TrialTaskProcessStatus.GRINDING
                ),
                GrindingRecord.created_at <= threshold,
            )
            .all()
        )
        new_count = 0
        for task in tasks:
            grinding = (
                db.query(GrindingRecord)
                .filter(
                    GrindingRecord.task_id == task.id,
                    GrindingRecord.is_deleted.is_(False),
                )
                .first()
            )
            users = self._get_rule_02_users(db, task, grinding)
            for user_id in users:
                if self._create_if_not_exists(
                    db,
                    target_user_id=user_id,
                    notification_type=NotifyType.GRINDING_DELAY,
                    task_id=task.id,
                    message=(
                        f"任务 {task.task_no} 试磨中超过5天，"
                        f"请确认进度"
                    ),
                ):
                    new_count += 1
        return new_count

    def _generate_rule_03(
        self, db: Session, now: datetime,
    ) -> int:
        """RULE-03: 报告缺失提醒。

        process_status=grinding 且 result_status=pending 且
        试磨开始时间超过 72h。
        通知: 技术员 + 销售 + 管理员。
        """
        threshold = now - timedelta(hours=72)
        tasks = (
            db.query(TrialTask)
            .join(
                GrindingRecord,
                TrialTask.id == GrindingRecord.task_id,
            )
            .filter(
                TrialTask.is_deleted.is_(False),
                TrialTask.process_status == (
                    TrialTaskProcessStatus.GRINDING
                ),
                TrialTask.result_status == (
                    TrialTaskResultStatus.PENDING
                ),
                GrindingRecord.created_at <= threshold,
            )
            .all()
        )
        new_count = 0
        for task in tasks:
            users = self._get_rule_03_users(db, task)
            for user_id in users:
                if self._create_if_not_exists(
                    db,
                    target_user_id=user_id,
                    notification_type=NotifyType.REPORT_MISSING,
                    task_id=task.id,
                    message=(
                        f"任务 {task.task_no} 待检测超过3天，"
                        f"请尽快上传检测报告"
                    ),
                ):
                    new_count += 1
        return new_count

    # ============================================================
    # Private: 用户获取
    # ============================================================

    def _get_users_by_role(
        self, db: Session, role_name: str,
    ) -> list[int]:
        """获取指定角色的所有用户 ID。

        Args:
            db: 数据库会话。
            role_name: 角色名称（如 "technician"、"admin"）。

        Returns:
            list[int]: 用户 ID 列表。
        """
        role = (
            db.query(Role)
            .filter(Role.name == role_name)
            .first()
        )
        if role is None:
            return []
        user_ids = (
            db.query(User.id)
            .join(User.roles)
            .filter(
                Role.id == role.id,
                User.is_deleted.is_(False),
            )
            .all()
        )
        return [uid for (uid,) in user_ids]

    def _get_rule_01_users(
        self, db: Session, task: TrialTask,
    ) -> set[int]:
        """RULE-01 通知用户: 技术员 + 销售 + 管理员。"""
        user_ids = set()
        user_ids.update(self._get_users_by_role(db, "technician"))
        user_ids.add(task.sales_id)
        user_ids.update(self._get_users_by_role(db, "admin"))
        return user_ids

    def _get_rule_02_users(
        self,
        db: Session,
        task: TrialTask,
        grinding: GrindingRecord | None,
    ) -> set[int]:
        """RULE-02 通知用户: 试磨责任人 + 销售 + 管理员。"""
        user_ids = set()
        if grinding is not None:
            user_ids.add(grinding.operator_id)
        user_ids.add(task.sales_id)
        user_ids.update(self._get_users_by_role(db, "admin"))
        return user_ids

    def _get_rule_03_users(
        self, db: Session, task: TrialTask,
    ) -> set[int]:
        """RULE-03 通知用户: 技术员 + 销售 + 管理员。"""
        user_ids = set()
        user_ids.update(self._get_users_by_role(db, "technician"))
        user_ids.add(task.sales_id)
        user_ids.update(self._get_users_by_role(db, "admin"))
        return user_ids

    # ============================================================
    # Private: 幂等创建
    # ============================================================

    def _create_if_not_exists(
        self,
        db: Session,
        target_user_id: int,
        notification_type: NotifyType,
        task_id: int,
        message: str,
    ) -> bool:
        """幂等创建消息提醒。

        检查是否存在相同未读提醒，不存在则创建。

        Args:
            db: 数据库会话。
            target_user_id: 目标用户 ID。
            notification_type: 提醒类型。
            task_id: 关联任务 ID。
            message: 提醒内容。

        Returns:
            bool: True 表示新创建，False 表示已存在（跳过）。
        """
        duplicate = self._find_duplicate(
            db,
            target_user_id=target_user_id,
            notification_type=notification_type,
            task_id=task_id,
        )
        if duplicate is not None:
            return False
        notification = Notification(
            task_id=task_id,
            type=notification_type,
            message=message,
            is_read=False,
            target_user_id=target_user_id,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        logger.debug(
            "generate: id=%d, user_id=%d, type=%s, task_id=%d",
            notification.id,
            target_user_id,
            notification_type.value,
            task_id,
        )
        return True

    # ============================================================
    # Private: 重复检查
    # ============================================================

    def _find_duplicate(
        self,
        db: Session,
        target_user_id: int,
        notification_type: NotifyType,
        task_id: int,
    ) -> Notification | None:
        """查找重复的未读消息提醒。

        相同 user_id + notification_type + target_type +
        target_id + is_read=False 仅允许存在一条。

        Args:
            db: 数据库会话。
            target_user_id: 目标用户 ID。
            notification_type: 提醒类型。
            task_id: 关联任务 ID。

        Returns:
            Notification | None: 重复消息提醒，不存在则返回 None。
        """
        return (
            db.query(Notification)
            .filter(
                Notification.is_deleted.is_(False),
                Notification.target_user_id == target_user_id,
                Notification.type == notification_type,
                Notification.task_id == task_id,
                Notification.is_read.is_(False),
            )
            .first()
        )

    # ============================================================
    # Private: 审计日志
    # ============================================================

    def _write_log(
        self,
        db: Session,
        operator_id: int,
        action: str,
        target_id: int,
        description: str,
    ) -> None:
        """记录审计日志。

        统一调用 LogService.create_log()，禁止直接写入 SystemLog。

        Args:
            db: 数据库会话。
            operator_id: 操作人 ID。
            action: 操作类型（create/update/delete）。
            target_id: 目标 ID。
            description: 操作描述。
        """
        self._log_service.create_log(
            db,
            LogBase(
                operator_id=operator_id,
                operation=ActionType(action),
                target_type="notification",
                target_id=target_id,
                module="notification",
                description=description,
                created_at=datetime.now(),
            ),
        )

    # ============================================================
    # Private: ORM → Schema 映射
    # ============================================================

    def _to_notification_response(
        self, notification: Notification,
    ) -> NotificationResponse:
        """Notification ORM → NotificationResponse Schema。

        Args:
            notification: Notification ORM 实例。

        Returns:
            NotificationResponse: 消息提醒响应。
        """
        return NotificationResponse(
            id=notification.id,
            user_id=notification.target_user_id,
            notification_type=notification.type,
            title=notification.type.display_name,
            content=notification.message,
            target_type="trial_task",
            target_id=notification.task_id,
            is_read=notification.is_read,
            read_time=(
                notification.updated_at
                if notification.is_read else None
            ),
            created_at=notification.created_at,
            updated_at=notification.updated_at,
        )


__all__ = [
    "NotificationService",
]
