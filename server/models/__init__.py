"""
server.models 包

GTMS 数据库 ORM 模型层。
所有模型继承自 BaseModel → Base。

模型清单（按 DB_DESIGN.md 定义）：
    User             - 用户模型
    Role             - 角色模型
    Permission       - 权限模型
    Customer         - 客户模型（待开发）
    TrialTask        - 试磨任务模型（待开发）
    Receipt          - 收件记录模型（待开发）
    GrindingRecord   - 试磨记录模型（待开发）
    InspectionRecord - 检测记录模型（待开发）
    Dispatch         - 工件去向模型（待开发）
    Attachment       - 附件模型（待开发）
    SystemLog        - 系统日志模型（待开发）
    Notification     - 消息提醒模型（待开发）

关联表：
    user_roles        - 用户 ↔ 角色 多对多
    role_permissions  - 角色 ↔ 权限 多对多
"""

from server.models.base_model import BaseModel
from server.models.user import User, user_roles, role_permissions
from server.models.role import Role
from server.models.permission import Permission
from server.models.customer import Customer
from server.models.trial_task import TrialTask

__all__ = [
    "BaseModel",
    "User",
    "Role",
    "Permission",
    "Customer",
    "TrialTask",
    "user_roles",
    "role_permissions",
]