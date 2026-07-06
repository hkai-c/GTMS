"""
server.services 包

GTMS 业务服务层，包含：
    - task_service:      试磨任务业务逻辑
    - receipt_service:   收件记录业务逻辑
    - grinding_service:  试磨记录业务逻辑
    - inspection_service: 检测记录业务逻辑
    - dispatch_service:  工件去向业务逻辑
    - auth_service:      认证业务逻辑
    - user_service:      用户业务逻辑
"""

from server.services.task_service import TaskService
from server.services.receipt_service import ReceiptService
from server.services.grinding_service import GrindingService
from server.services.inspection_service import InspectionService
from server.services.dispatch_service import DispatchService
from server.services.auth_service import AuthService
from server.services.user_service import UserService

__all__ = [
    "TaskService",
    "ReceiptService",
    "GrindingService",
    "InspectionService",
    "DispatchService",
    "AuthService",
    "UserService",
]