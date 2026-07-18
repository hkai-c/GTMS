"""
server.routers 包

GTMS API 路由层，包含：
    - auth_router: 认证接口（登录、修改密码、当前用户）
    - customer_router: 客户管理接口
    - trial_task_router: 试磨任务管理接口
    - receipt_router: 收件记录管理接口
    - upload_router: 通用文件上传接口
    - grinding_router: 试磨记录管理接口
    - inspection_router: 检测记录管理接口
    - dispatch_router: 工件派发管理接口
    - query_router: 查询统计管理接口
"""

from server.routers.auth_router import router as auth_router
from server.routers.customer_router import router as customer_router
from server.routers.receipt_router import router as receipt_router
from server.routers.grinding_router import router as grinding_router
from server.routers.inspection_router import router as inspection_router
from server.routers.dispatch_router import router as dispatch_router
from server.routers.query_router import router as query_router
from server.routers.log_router import router as log_router
from server.routers.role_router import router as role_router
from server.routers.trial_task_router import router as trial_task_router
from server.routers.upload_router import router as upload_router
from server.routers.user_router import router as user_router

__all__ = [
    "auth_router",
    "customer_router",
    "receipt_router",
    "grinding_router",
    "inspection_router",
    "dispatch_router",
    "query_router",
    "log_router",
    "role_router",
    "trial_task_router",
    "upload_router",
    "user_router",
]