"""GTMS 桌面端主窗口 (MainWindow)

Sprint 3 — Task 3.10
严格依据 UI_PROTOTYPE §3、Development Roadmap、Sprint 3 Frozen API。

提供桌面端主窗口框架：
    - 标题栏显示当前用户信息
    - 左侧导航菜单（QListWidget）
    - 右侧内容区（QStackedWidget）
    - 权限过滤菜单显示
    - 退出登录

所有业务逻辑委托 AuthService。
禁止直接 HTTP / requests / ORM / Database / JWT。
"""

import logging
from typing import Any

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from client.services.auth_service import AuthService

logger = logging.getLogger("gtms.client")


# ============================================================
# 菜单权限映射（冻结）
# ============================================================

# 每个菜单项可访问的角色列表（role name 小写）
MENU_PERMISSIONS: dict[str, list[str]] = {
    "首页":     ["administrator", "manager", "technician", "sales", "viewer"],
    "试磨任务": ["administrator", "manager", "technician", "sales"],
    "检测报告": ["administrator", "manager", "technician", "sales"],
    "工件去向": ["administrator", "manager", "technician"],
    "用户管理": ["administrator"],
    "角色权限": ["administrator"],
    "系统日志": ["administrator", "manager"],
    "设置":     ["administrator", "manager", "technician"],
    "退出登录": ["administrator", "manager", "technician", "sales", "viewer"],
}

# 菜单项显示顺序（冻结）
MENU_ORDER: list[str] = [
    "首页",
    "试磨任务",
    "检测报告",
    "工件去向",
    "用户管理",
    "角色权限",
    "系统日志",
    "设置",
    "退出登录",
]


class MainWindow(QMainWindow):
    """GTMS 桌面端主窗口。

    遵循 UI_PROTOTYPE §3 布局：左侧导航 + 右侧内容区。
    菜单根据用户角色动态过滤，页面通过 QStackedWidget 切换。

    Signals:
        logout_requested: 退出登录请求，外部代码应显示 LoginView。

    Attributes:
        _auth_service: AuthService 实例。
        _current_user: 当前登录用户信息（dict）。
        _role_name: 当前用户角色名称（小写）。
        _pages: 已创建的页面缓存 {name: QWidget}。

    Usage:
        window = MainWindow()
        window.set_auth_service(auth_service)
        window.refresh_permissions()
        window.show()
    """

    # ============================================================
    # Signals（冻结）
    # ============================================================

    logout_requested = Signal()

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        auth_service: AuthService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """初始化主窗口。

        Args:
            auth_service: AuthService 实例（可选，可通过 set_auth_service 设置）。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._auth_service: AuthService | None = auth_service
        self._current_user: dict[str, Any] | None = None
        self._role_name: str = ""
        self._pages: dict[str, QWidget] = {}

        # 窗口属性
        self._setup_window()

        # 构建 UI
        self._setup_ui()

        # 如果初始化时已提供 auth_service，自动刷新权限
        if self._auth_service is not None:
            self.refresh_permissions()

        logger.debug("MainWindow 初始化完成")

    # ============================================================
    # 公开 API（冻结）
    # ============================================================

    def set_auth_service(self, auth_service: AuthService) -> None:
        """设置认证服务实例。

        不依赖全局变量，每个 MainWindow 绑定一个 AuthService。

        Args:
            auth_service: AuthService 实例。
        """
        self._auth_service = auth_service
        logger.debug("AuthService 已设置")

    def refresh_permissions(self) -> None:
        """刷新权限。

        重新获取当前用户信息，更新标题栏和菜单可见性。
        用于重新登录、切换用户后刷新权限，不重新创建窗口。
        """
        if self._auth_service is None:
            logger.warning("refresh_permissions: AuthService 未设置")
            return

        try:
            self._current_user = self._auth_service.get_current_user()
        except Exception as e:
            logger.error("获取用户信息失败: %s", e)
            return

        # 提取角色名称（小写，用于权限比较）
        role = self._current_user.get("role", {})
        self._role_name = role.get("name", "").lower() if isinstance(role, dict) else ""

        # 更新标题栏
        self._update_title()

        # 更新菜单可见性
        self._update_menu_visibility()

        logger.info("权限已刷新: username=%s, role=%s",
                    self._current_user.get("username"), self._role_name)

    def show_page(self, name: str) -> None:
        """切换到指定页面。

        页面实例缓存，首次访问时创建，后续复用。

        Args:
            name: 页面名称（如 "首页"、"试磨任务" 等）。
        """
        if name not in MENU_ORDER:
            logger.warning("未知页面: %s", name)
            return

        # 首次访问：创建页面并缓存
        if name not in self._pages:
            page = self._create_page(name)
            self._pages[name] = page
            self._stacked_widget.addWidget(page)

        # 切换到目标页面
        page = self._pages[name]
        self._stacked_widget.setCurrentWidget(page)

        logger.debug("切换到页面: %s", name)

    # ============================================================
    # 退出登录
    # ============================================================

    def logout(self) -> None:
        """退出登录。

        流程:
            ① 调用 AuthService.logout()
            ② 关闭 MainWindow
            ③ 发射 logout_requested 信号
        """
        if self._auth_service is not None:
            self._auth_service.logout()

        logger.info("用户退出登录")
        self.logout_requested.emit()
        self.close()

    # ============================================================
    # 窗口设置
    # ============================================================

    def _setup_window(self) -> None:
        """设置窗口基本属性。

        最小尺寸: 1280 × 720（遵循 UI_PROTOTYPE §1.2）。
        标题在 refresh_permissions() 中动态更新。
        """
        self.setWindowTitle("GTMS")
        self.setMinimumSize(1280, 720)

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建主窗口 UI。

        布局结构:
            - 中央区域 (QWidget)
              - QHBoxLayout
                - 左侧导航 (QFrame)
                  - QListWidget (菜单列表)
                - 右侧内容区 (QStackedWidget)
            - 状态栏 (QStatusBar)
        """
        # --- 中央区域 ---
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 左侧导航栏 ---
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # 分隔线
        splitter_line = QFrame()
        splitter_line.setFrameShape(QFrame.Shape.VLine)
        splitter_line.setStyleSheet("background-color: #e8e8e8; max-width: 1px;")
        main_layout.addWidget(splitter_line)

        # --- 右侧内容区 ---
        self._stacked_widget = QStackedWidget()
        self._stacked_widget.setStyleSheet("background-color: #f5f5f5;")
        main_layout.addWidget(self._stacked_widget, 1)

        # --- 状态栏 ---
        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet(
            "QStatusBar { background-color: #fafafa; border-top: 1px solid #e8e8e8; "
            "font-size: 11px; color: #888888; }"
        )
        self.setStatusBar(self._status_bar)
        self._status_label = QLabel("就绪")
        self._status_bar.addWidget(self._status_label)

    # ============================================================
    # 侧边栏
    # ============================================================

    def _create_sidebar(self) -> QFrame:
        """创建左侧导航栏。

        Returns:
            QFrame: 包含菜单列表的侧边栏容器。
        """
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(
            "QFrame#sidebar {"
            "  background-color: #ffffff;"
            "  border-right: 1px solid #e8e8e8;"
            "}"
        )

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 菜单列表
        self._menu_list = QListWidget()
        self._menu_list.setObjectName("menu_list")
        self._menu_list.setStyleSheet(
            "QListWidget {"
            "  border: none;"
            "  background-color: #ffffff;"
            "  font-size: 13px;"
            "  outline: none;"
            "}"
            "QListWidget::item {"
            "  padding: 12px 20px;"
            "  border: none;"
            "  color: #333333;"
            "}"
            "QListWidget::item:hover {"
            "  background-color: #e6f7ff;"
            "  color: #1890FF;"
            "}"
            "QListWidget::item:selected {"
            "  background-color: #e6f7ff;"
            "  color: #1890FF;"
            "  border-left: 3px solid #1890FF;"
            "}"
        )

        # 添加所有菜单项（默认全部可见，调用 _update_menu_visibility 后过滤）
        for name in MENU_ORDER:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)  # 存储菜单名称
            self._menu_list.addItem(item)

        self._menu_list.currentItemChanged.connect(self._on_menu_changed)
        sidebar_layout.addWidget(self._menu_list)

        return sidebar

    # ============================================================
    # 菜单交互
    # ============================================================

    def _on_menu_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        """处理菜单切换事件。

        Args:
            current: 当前选中的菜单项。
            previous: 之前选中的菜单项。
        """
        if current is None:
            return

        name = current.data(Qt.ItemDataRole.UserRole)
        if name is None:
            return

        if name == "退出登录":
            self.logout()
        else:
            self.show_page(name)

    # ============================================================
    # 权限过滤
    # ============================================================

    def _update_menu_visibility(self) -> None:
        """更新菜单可见性（统一入口，不在多处重复判断）。

        根据当前用户角色，隐藏无权限的菜单项。
        """
        if not self._role_name:
            return

        for i in range(self._menu_list.count()):
            item = self._menu_list.item(i)
            name = item.data(Qt.ItemDataRole.UserRole)
            if name is None:
                continue

            allowed_roles = MENU_PERMISSIONS.get(name, [])
            item.setHidden(self._role_name not in allowed_roles)

        logger.debug("菜单可见性已更新: role=%s", self._role_name)

    # ============================================================
    # 标题栏
    # ============================================================

    def _update_title(self) -> None:
        """更新窗口标题栏。

        格式: GTMS - {角色名}：{用户名}
        例如: GTMS - 管理员：admin
        """
        if self._current_user is None:
            return

        username = self._current_user.get("username", "")
        role_display = self._role_name.capitalize() if self._role_name else ""

        if role_display and username:
            self.setWindowTitle(f"GTMS - {role_display}：{username}")
        elif username:
            self.setWindowTitle(f"GTMS - {username}")

        # 更新状态栏用户信息
        status_text = f"用户: {username}"
        if role_display:
            status_text += f" | 角色: {role_display}"
        status_text += " | v1.0.0"
        self._status_label.setText(status_text)

    # ============================================================
    # 页面创建
    # ============================================================

    def _create_page(self, name: str) -> QWidget:
        """创建占位页面。

        后续 Sprint 将替换为实际页面组件。

        Args:
            name: 页面名称。

        Returns:
            QWidget: 占位页面。
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #bbbbbb;")
        label.setFont(QFont("Microsoft YaHei", 16))
        layout.addWidget(label)

        logger.debug("创建占位页面: %s", name)
        return page


__all__ = [
    "MainWindow",
    "MENU_PERMISSIONS",
    "MENU_ORDER",
]