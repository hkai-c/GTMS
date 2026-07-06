"""GTMS 桌面端启动入口 (Application Entry)

Sprint 3 — Task 3.11
严格依据 Development Roadmap、CODE_WIKI、UI_PROTOTYPE。

负责：
    - 程序启动
    - 创建 QApplication
    - 创建 ApiClient / AuthService 单实例
    - 创建 LoginView
    - 登录成功后打开 MainWindow
    - 退出登录后重新回到 LoginView
    - 整个生命周期只维护一个 QApplication

所有业务逻辑委托 AuthService。
禁止直接 HTTP / requests / ORM / Database / JWT。
"""

import logging
import sys
from typing import Any

from PySide6.QtWidgets import QApplication

from client.config import client_config
from client.services.api_client import ApiClient
from client.services.auth_service import AuthService
from client.views.login_view import LoginView
from client.views.main_window import MainWindow

logger = logging.getLogger("gtms.client")


def main() -> int:
    """GTMS 桌面端启动入口。

    启动流程:
        ① 创建 QApplication
        ② 创建 ApiClient（单实例）
        ③ 创建 AuthService（单实例）
        ④ 创建 LoginView，显示登录窗口
        ⑤ 登录成功 → 创建 MainWindow，隐藏 LoginView
        ⑥ 退出登录 → 关闭 MainWindow，重新显示 LoginView

    Returns:
        int: 0 表示正常退出，1 表示异常退出。
    """
    try:
        return _run()
    except Exception:
        logger.exception("Application crashed with unhandled exception")
        return 1


def _run() -> int:
    """执行主启动流程。

    内部函数，封装所有启动逻辑，使 main() 的异常边界清晰。

    Returns:
        int: 应用退出码。
    """
    # ① 创建 QApplication（单实例）
    app = QApplication(sys.argv)
    app.setApplicationName("GTMS")
    app.setApplicationVersion("1.0.0")
    logger.info("Application Started")

    # ② 创建 ApiClient（单实例）
    api_client = ApiClient(base_url=client_config.API_BASE_URL)

    # ③ 创建 AuthService（单实例，绑定 ApiClient）
    auth_service = AuthService(api_client)

    # ④ 创建 LoginView
    login_view = LoginView(auth_service)

    # ⑤ 连接 Signal
    _connect_signals(app, api_client, auth_service, login_view)

    # ⑥ 显示登录窗口
    login_view.show()
    logger.info("LoginView displayed")

    # ⑦ 进入事件循环
    exit_code = app.exec()
    logger.info("Application Exit (code=%d)", exit_code)
    return exit_code


def _connect_signals(
    app: QApplication,
    api_client: ApiClient,
    auth_service: AuthService,
    login_view: LoginView,
) -> None:
    """连接登录/退出 Signal。

    将 LoginView 的 login_success 和 MainWindow 的 logout_requested
    连接到对应处理函数，形成完整的登录-退出循环。

    Args:
        app: QApplication 实例。
        api_client: ApiClient 单实例。
        auth_service: AuthService 单实例。
        login_view: LoginView 实例。
    """
    # 用于存储当前 MainWindow 引用（闭包变量）
    main_window_ref: list[MainWindow | None] = [None]

    def on_login_success(user: dict[str, Any]) -> None:
        """登录成功回调。

        创建 MainWindow，设置 AuthService，刷新权限，显示主窗口，
        隐藏登录窗口。

        Args:
            user: 登录成功返回的用户信息 dict。
        """
        logger.info("Login Success: username=%s", user.get("username"))

        # 创建 MainWindow
        main_window = MainWindow()
        main_window.set_auth_service(auth_service)
        main_window.refresh_permissions()

        # 连接退出登录 Signal
        main_window.logout_requested.connect(on_logout_requested)

        # 保存引用
        main_window_ref[0] = main_window

        # 隐藏登录窗口，显示主窗口
        login_view.hide()
        main_window.show()
        logger.info("MainWindow Opened")

    def on_logout_requested() -> None:
        """退出登录回调。

        MainWindow 已自行调用 AuthService.logout() 和 close()，
        此处只需重新显示登录窗口。清理旧 MainWindow 引用。
        """
        logger.info("Logout")

        # 清理旧 MainWindow
        main_window_ref[0] = None

        # 重新显示登录窗口
        login_view.show()

    # 连接 Signal
    login_view.login_success.connect(on_login_success)


__all__ = [
    "main",
]