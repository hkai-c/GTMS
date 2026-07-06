"""GTMS 桌面端认证服务 (Desktop AuthService)

Sprint 3 — Task 3.8
严格依据 Development Roadmap、Sprint 3 Server Auth API、ApiClient (Task 3.7)。

提供桌面端认证业务逻辑：
    - login()              — 用户登录
    - logout()             — 退出登录
    - get_current_user()   — 获取当前用户信息
    - change_password()    — 修改密码
    - is_authenticated     — 认证状态

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何 UI。

公开 API（冻结）:
    - __init__(api_client)
    - login(username, password)
    - logout()
    - get_current_user()
    - change_password(old_password, new_password)
    - is_authenticated (property)
"""

import logging
from typing import Any

from client.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class AuthService:
    """GTMS 桌面端认证服务。

    封装登录、登出、Token 生命周期管理、当前用户缓存。
    所有 HTTP 请求通过 ApiClient 发起。

    Attributes:
        _api_client: ApiClient 实例。
        _token: 当前 JWT Token。
        _current_user: 当前登录用户信息（dict）。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        auth = AuthService(client)
        auth.login("admin", "admin123")
        user = auth.get_current_user()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化认证服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        self._token: str | None = None
        self._current_user: dict[str, Any] | None = None

        logger.debug("AuthService 初始化")

    # ============================================================
    # 公开 API（冻结）
    # ============================================================

    def login(self, username: str, password: str) -> dict[str, Any]:
        """用户登录。

        流程:
            ① 调用 ApiClient.post("/api/auth/login", json={...})
            ② 成功：保存 access_token，调用 ApiClient.set_token()
            ③ 缓存当前用户信息（UserResponse）
            ④ 返回 LoginResponse

        Args:
            username: 用户名。
            password: 密码。

        Returns:
            dict: LoginResponse（access_token, token_type, user）。

        Raises:
            requests.HTTPError: 登录失败（401/403 等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        resp = self._api_client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )
        data = resp.json()

        # 保存 Token 和用户信息
        self._token = data["access_token"]
        self._current_user = data.get("user")

        # 设置 ApiClient 的 Authorization Header（后续请求自动携带）
        self._api_client.set_token(self._token)

        logger.info("用户登录成功: username=%s", username)
        return data

    def logout(self) -> None:
        """退出登录。

        流程:
            ① 调用 ApiClient.clear_token() 清除 Header
            ② 清空本地 token 和 current_user
            ③ 不请求服务器
        """
        self._api_client.clear_token()
        self._token = None
        self._current_user = None

        logger.info("用户已退出登录")

    def get_current_user(self) -> dict[str, Any]:
        """获取当前用户信息。

        调用 GET /api/auth/me 获取最新用户信息，更新本地缓存。

        Returns:
            dict: UserResponse（不含 password_hash）。

        Raises:
            requests.HTTPError: 请求失败（401 等）。
            requests.ConnectionError: 网络连接失败。
        """
        resp = self._api_client.get("/api/auth/me")
        self._current_user = resp.json()

        logger.debug("当前用户信息已更新: username=%s",
                     self._current_user.get("username"))
        return self._current_user

    def change_password(
        self,
        old_password: str,
        new_password: str,
    ) -> dict[str, Any]:
        """修改当前用户密码。

        调用 POST /api/auth/change-password，成功不自动退出登录。

        Args:
            old_password: 旧密码。
            new_password: 新密码。

        Returns:
            dict: {"message": "Password changed successfully."}

        Raises:
            requests.HTTPError: 密码修改失败（401 等）。
            requests.ConnectionError: 网络连接失败。
        """
        resp = self._api_client.post(
            "/api/auth/change-password",
            json={
                "old_password": old_password,
                "new_password": new_password,
            },
        )
        logger.info("密码修改成功")
        return resp.json()

    # ============================================================
    # Property
    # ============================================================

    @property
    def is_authenticated(self) -> bool:
        """认证状态。

        规则: token != None，不请求服务器。

        Returns:
            bool: 是否已认证。
        """
        return self._token is not None


__all__ = [
    "AuthService",
]