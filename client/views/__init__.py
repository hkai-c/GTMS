"""GTMS 桌面端视图层 (Client Views)

Sprint 3 — Task 3.9, 3.10, 3.12

提供桌面端 UI 界面：
    - login_view: 桌面端登录窗口
    - main_window: 桌面端主窗口
    - user_manage_view: 用户管理页面
    - user_edit_dialog: 用户编辑对话框
"""

from client.views.login_view import LoginView
from client.views.main_window import MainWindow
from client.views.user_manage_view import UserManageView
from client.views.user_edit_dialog import UserEditDialog

__all__ = [
    "LoginView",
    "MainWindow",
    "UserManageView",
    "UserEditDialog",
]