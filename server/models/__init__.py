"""
server.models 包

GTMS 数据库 ORM 模型层。
所有模型继承自 BaseModel → Base。

模型清单（按 DB_DESIGN.md 定义）：
    User             - 用户模型
    Role             - 角色模型
    Permission       - 权限模型
    Customer         - 客户模型
    TrialTask        - 试磨任务模型
    Receipt          - 收件记录模型
    GrindingRecord   - 试磨记录模型
    InspectionRecord - 检测记录模型
    Dispatch         - 工件去向模型
    Attachment       - 附件模型
    Notification     - 消息提醒模型
    SystemLog        - 系统日志模型

关联表：
    user_roles        - 用户 ↔ 角色 多对多
    role_permissions  - 角色 ↔ 权限 多对多
"""

from server.models.base_model import BaseModel
from server.database.base import Base
from server.models.user import User, user_roles, role_permissions
from server.models.role import Role
from server.models.permission import Permission
from server.models.customer import Customer
from server.models.trial_task import TrialTask
from server.models.receipt import Receipt
from server.models.grinding_record import GrindingRecord
from server.models.inspection_record import InspectionRecord
from server.models.dispatch import Dispatch
from server.models.attachment import Attachment
from server.models.notification import Notification
from server.models.system_log import SystemLog

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "Role",
    "Permission",
    "Customer",
    "TrialTask",
    "Receipt",
    "GrindingRecord",
    "InspectionRecord",
    "Dispatch",
    "Attachment",
    "SystemLog",
    "Notification",
    "user_roles",
    "role_permissions",
]