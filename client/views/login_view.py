"""GTMS 桌面端登录窗口 (LoginView)

Sprint 3 — Task 3.9
严格依据 UI_PROTOTYPE §2、Development Roadmap、Sprint 3 Frozen API。

提供桌面端登录界面：
    - 用户名输入
    - 密码输入
    - 登录按钮
    - 状态提示
    - 发送登录成功 / 失败 Signal

所有业务逻辑委托 AuthService。
禁止直接 HTTP / requests / ORM / Database / JWT。
"""

import logging
from typing import Any

import requests
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from client.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class LoginView(QWidget):
    """GTMS 桌面端登录窗口。

    遵循 UI_PROTOTYPE §2 布局，提供用户名、密码输入和登录功能。
    所有业务逻辑通过 AuthService 完成。

    Signals:
        login_success(object): 登录成功，携带用户信息 dict。
        login_failed(str): 登录失败，携带错误消息字符串。

    Attributes:
        _auth_service: AuthService 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        auth = AuthService(client)
        login_view = LoginView(auth)
        login_view.login_success.connect(on_login_success)
        login_view.show()
    """

    # ============================================================
    # Signals（冻结）
    # ============================================================

    login_success = Signal(object)  # 携带 user dict
    login_failed = Signal(str)      # 携带错误消息

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        auth_service: AuthService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化登录窗口。

        Args:
            auth_service: AuthService 实例（用于登录认证）。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._auth_service: AuthService = auth_service

        # 窗口属性
        self._setup_window()

        # 构建 UI
        self._setup_ui()

        # 快捷键
        self._setup_shortcuts()

        logger.debug("LoginView 初始化完成")

    # ============================================================
    # 窗口设置
    # ============================================================

    def _setup_window(self) -> None:
        """设置窗口基本属性。

        标题: GTMS 登录
        固定大小: 420 × 280
        自动居中。
        """
        self.setWindowTitle("GTMS 登录")
        self.setFixedSize(420, 280)
        self._center_on_screen()

    def _center_on_screen(self) -> None:
        """将窗口居中显示在主屏幕中央。"""
        screen = QApplication.primaryScreen()
        if screen is not None:
            center = screen.availableGeometry().center()
            frame_geom = self.frameGeometry()
            frame_geom.moveCenter(center)
            self.move(frame_geom.topLeft())

    # ============================================================
    # UI 构建（严格遵循 UI_PROTOTYPE §2）
    # ============================================================

    def _setup_ui(self) -> None:
        """构建登录窗口 UI。

        布局结构:
            - 主布局 (QVBoxLayout)
              - 容器卡片 (QFrame, border)
                - Logo 文字
                - 标题 "磨床试磨管理系统"
                - 副标题 "GTMS V1.0"
                - 表单区域 (QFrame, box)
                  - 用户名
                  - 密码
                  - 记住密码
                  - 登录按钮
                - 服务器地址
              - 状态标签 (status_label)
              - 版本信息
        """
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- 容器卡片 ---
        card = QFrame()
        card.setStyleSheet(
            "QFrame#login_card {"
            "  background-color: #ffffff;"
            "  border: 1px solid #e8e8e8;"
            "  border-radius: 8px;"
            "}"
        )
        card.setObjectName("login_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 24, 40, 20)
        card_layout.setSpacing(6)

        # Logo 文字（代替图标）
        logo_label = QLabel("GTMS")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_font = QFont("Microsoft YaHei", 18, QFont.Weight.Bold)
        logo_label.setFont(logo_font)
        logo_label.setStyleSheet("color: #1890FF;")
        card_layout.addWidget(logo_label)

        # 标题
        title_label = QLabel("磨床试磨管理系统")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Microsoft YaHei", 11)
        title_label.setFont(title_font)
        card_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("GTMS V1.0")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #888888; font-size: 10px;")
        card_layout.addWidget(subtitle_label)

        card_layout.addSpacing(10)

        # --- 表单区域 ---
        form_frame = QFrame()
        form_frame.setStyleSheet(
            "QFrame#form_frame {"
            "  border: 1px solid #d9d9d9;"
            "  border-radius: 4px;"
            "  padding: 10px;"
            "}"
        )
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(14, 10, 14, 10)
        form_layout.setSpacing(6)

        # 用户名
        username_label = QLabel("用户名")
        username_label.setStyleSheet("font-size: 11px;")
        form_layout.addWidget(username_label)

        self.username_edit = QLineEdit()
        self.username_edit.setObjectName("username_edit")
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setFixedHeight(28)
        form_layout.addWidget(self.username_edit)

        # 密码
        password_label = QLabel("密码")
        password_label.setStyleSheet("font-size: 11px;")
        form_layout.addWidget(password_label)

        self.password_edit = QLineEdit()
        self.password_edit.setObjectName("password_edit")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setFixedHeight(28)
        form_layout.addWidget(self.password_edit)

        # 记住密码
        self.remember_checkbox = QCheckBox("记住密码")
        self.remember_checkbox.setChecked(True)
        self.remember_checkbox.setStyleSheet("font-size: 11px;")
        form_layout.addWidget(self.remember_checkbox)

        form_layout.addSpacing(2)

        # 登录按钮
        self.login_button = QPushButton("登 录")
        self.login_button.setObjectName("login_button")
        self.login_button.setFixedHeight(32)
        self.login_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #1890FF;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 4px;"
            "  font-size: 13px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover { background-color: #40A9FF; }"
            "QPushButton:pressed { background-color: #096DD9; }"
            "QPushButton:disabled {"
            "  background-color: #d9d9d9;"
            "  color: #999999;"
            "}"
        )
        self.login_button.clicked.connect(self._on_login_clicked)
        form_layout.addWidget(self.login_button)

        card_layout.addWidget(form_frame)

        card_layout.addSpacing(6)

        # --- 服务器地址 ---
        server_layout = QHBoxLayout()
        server_layout.setSpacing(6)
        server_label = QLabel("服务器地址:")
        server_label.setStyleSheet("font-size: 10px; color: #666666;")
        server_layout.addWidget(server_label)

        self.server_edit = QLineEdit()
        self.server_edit.setPlaceholderText("http://localhost:8000")
        self.server_edit.setText("http://localhost:8000")
        self.server_edit.setFixedHeight(24)
        self.server_edit.setStyleSheet("font-size: 10px;")
        server_layout.addWidget(self.server_edit)
        card_layout.addLayout(server_layout)

        # 主布局添加卡片（居中）
        main_layout.addStretch()
        main_layout.addWidget(card)
        main_layout.addSpacing(8)

        # --- 状态标签（冻结 ObjectName） ---
        self.status_label = QLabel("")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #FF4D4F; font-size: 11px;")
        self.status_label.setFixedHeight(20)
        main_layout.addWidget(self.status_label)

        # --- 版本信息 ---
        version_label = QLabel("v1.0.0  © 2026")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")
        main_layout.addWidget(version_label)

        main_layout.addStretch()

    # ============================================================
    # 快捷键
    # ============================================================

    def _setup_shortcuts(self) -> None:
        """设置键盘快捷键。

        Enter → 触发登录。
        Esc  → 关闭窗口。
        """
        self.username_edit.returnPressed.connect(self._on_login_clicked)
        self.password_edit.returnPressed.connect(self._on_login_clicked)

    def keyPressEvent(self, event: Any) -> None:
        """处理键盘事件。

        Esc 键关闭窗口。

        Args:
            event: 键盘事件对象。
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    # ============================================================
    # 登录流程
    # ============================================================

    def _on_login_clicked(self) -> None:
        """处理登录按钮点击事件。

        流程:
            ① 基本校验（用户名/密码非空）
            ② 禁用登录按钮，显示"登录中..."
            ③ 调用 AuthService.login()
            ④ 成功: 显示"登录成功"，emit login_success，关闭窗口
            ⑤ 失败: 恢复按钮，显示错误消息，emit login_failed
        """
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        # 基本校验
        if not username:
            self._show_error("请输入用户名")
            return
        if not password:
            self._show_error("请输入密码")
            return

        # 禁用按钮，显示加载状态
        self.login_button.setEnabled(False)
        self.status_label.setStyleSheet("color: #1890FF; font-size: 11px;")
        self.status_label.setText("登录中...")

        try:
            result = self._auth_service.login(username, password)
        except requests.HTTPError as e:
            status_code = ""
            if hasattr(e, "response") and e.response is not None:
                status_code = str(e.response.status_code)
            self._handle_login_error(f"用户名或密码错误 ({status_code})")
        except requests.ConnectionError:
            self._handle_login_error("网络连接失败，请检查服务器地址")
        except requests.Timeout:
            self._handle_login_error("连接超时，请检查网络")
        except requests.RequestException as e:
            self._handle_login_error(f"请求异常: {e}")
        else:
            # 登录成功
            self.status_label.setStyleSheet("color: #52C41A; font-size: 11px;")
            self.status_label.setText("登录成功")
            user = result.get("user", {})
            logger.info("用户登录成功: username=%s", username)
            self.login_success.emit(user)
            self.close()

    def _handle_login_error(self, message: str) -> None:
        """处理登录失败。

        恢复按钮状态，显示错误消息，发送 login_failed 信号。

        Args:
            message: 错误消息（用于 UI 显示）。
        """
        self._show_error(message)
        self.login_button.setEnabled(True)
        logger.warning("登录失败: %s", message)
        self.login_failed.emit(message)

    def _show_error(self, message: str) -> None:
        """在状态标签中显示错误消息。

        Args:
            message: 错误消息文本。
        """
        self.status_label.setStyleSheet("color: #FF4D4F; font-size: 11px;")
        self.status_label.setText(message)


__all__ = [
    "LoginView",
]