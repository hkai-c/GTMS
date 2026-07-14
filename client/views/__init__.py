"""GTMS 桌面端视图层 (Client Views)

Sprint 3 — Task 3.9, 3.10, 3.12 / Sprint 4 — Task 4.5 / Sprint 5 — Task 5.7, 5.8, 5.9 / Sprint 6 — Task 6.8 / Sprint 7 — Task 7.5 / Sprint 8 — Task 8.5 / Sprint 9 — Task 9.5

提供桌面端 UI 界面：
    - login_view:            桌面端登录窗口
    - main_window:           桌面端主窗口
    - user_manage_view:      用户管理页面
    - user_edit_dialog:      用户编辑对话框
    - customer_view:         客户管理页面
    - customer_edit_dialog:  客户编辑对话框
    - trial_task_view:       试磨任务管理页面
    - task_edit_dialog:      试磨任务编辑对话框
    - task_detail_view:      试磨任务详情页
    - receipt_view:          收件登记管理页面
    - grinding_view:         试磨管理页面
    - inspection_view:       检测管理页面
    - dispatch_view:         派发管理页面
"""

from client.views.login_view import LoginView
from client.views.main_window import MainWindow
from client.views.receipt_view import ReceiptView
from client.views.grinding_view import GrindingView
from client.views.inspection_view import InspectionView
from client.views.dispatch_view import DispatchView
from client.views.user_manage_view import UserManageView
from client.views.user_edit_dialog import UserEditDialog
from client.views.customer_view import CustomerView
from client.views.customer_edit_dialog import CustomerEditDialog
from client.views.trial_task_view import TrialTaskView
from client.views.task_edit_dialog import TaskEditDialog
from client.views.task_detail_view import TaskDetailView

__all__ = [
    "LoginView",
    "MainWindow",
    "ReceiptView",
    "GrindingView",
    "InspectionView",
    "DispatchView",
    "UserManageView",
    "UserEditDialog",
    "CustomerView",
    "CustomerEditDialog",
    "TrialTaskView",
    "TaskEditDialog",
    "TaskDetailView",
]