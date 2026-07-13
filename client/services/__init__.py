"""GTMS 桌面端服务层 (Client Services)

Sprint 3 — Task 3.7, 3.8, 3.12 / Sprint 4 — Task 4.4 / Sprint 5 — Task 5.4 / Sprint 6 — Task 6.5

提供桌面端业务服务：
    - api_client:       统一 HTTP API 客户端（桌面端唯一 HTTP 入口）
    - auth_service:     桌面端认证服务
    - user_service:     桌面端用户管理服务
    - customer_service: 桌面端客户管理服务
    - task_service:     桌面端试磨任务管理服务
    - receipt_service:  桌面端收件记录管理服务
"""

from client.services.api_client import ApiClient
from client.services.auth_service import AuthService
from client.services.customer_service import CustomerService
from client.services.receipt_service import ReceiptService
from client.services.task_service import TaskService
from client.services.user_service import UserService

__all__ = [
    "ApiClient",
    "AuthService",
    "CustomerService",
    "ReceiptService",
    "TaskService",
    "UserService",
]