"""GTMS 桌面端服务层 (Client Services)

Sprint 3 — Task 3.7, 3.8, 3.12 / Sprint 4 — Task 4.4 / Sprint 5 — Task 5.4 / Sprint 6 — Task 6.5 / Sprint 7 — Task 7.4 / Sprint 8 — Task 8.4 / Sprint 9 — Task 9.4

提供桌面端业务服务：
    - api_client:           统一 HTTP API 客户端（桌面端唯一 HTTP 入口）
    - auth_service:         桌面端认证服务
    - user_service:         桌面端用户管理服务
    - customer_service:     桌面端客户管理服务
    - task_service:         桌面端试磨任务管理服务
    - receipt_service:      桌面端收件记录管理服务
    - grinding_service:     桌面端试磨记录管理服务
    - inspection_service:   桌面端检测记录管理服务
    - dispatch_service:   桌面端工件派发管理服务
    - query_service:     桌面端查询统计管理服务
"""

from client.services.api_client import ApiClient
from client.services.auth_service import AuthService
from client.services.customer_service import CustomerService
from client.services.receipt_service import ReceiptService
from client.services.grinding_service import GrindingService
from client.services.inspection_service import InspectionService
from client.services.dispatch_service import DispatchService
from client.services.query_service import QueryService
from client.services.log_service import LogService
from client.services.notification_service import NotificationService
from client.services.settings_service import SettingsService
from client.services.task_service import TaskService
from client.services.user_service import UserService

__all__ = [
    "ApiClient",
    "AuthService",
    "CustomerService",
    "ReceiptService",
    "GrindingService",
    "InspectionService",
    "DispatchService",
    "QueryService",
    "LogService",
    "TaskService",
    "UserService",
    "NotificationService",
    "SettingsService",
]