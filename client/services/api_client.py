"""GTMS 桌面端统一 API 客户端 (ApiClient)

Sprint 3 — Task 3.7
严格依据 Development Roadmap、CODE_WIKI、Sprint 2 Frozen API、Sprint 3 Server API。

桌面端唯一 HTTP 入口。所有后续 Service（AuthService、TaskService 等）
均通过本客户端发起 HTTP 请求，禁止 View 直接调用 requests/httpx/urllib。

公开 API（冻结）:
    - __init__(base_url)     — 初始化客户端
    - set_token(token)       — 设置 Bearer Token
    - clear_token()          — 清除 Token
    - get(url, **kwargs)     — GET 请求
    - post(url, **kwargs)    — POST 请求
    - put(url, **kwargs)     — PUT 请求
    - delete(url, **kwargs)  — DELETE 请求

特性:
    - 统一使用 requests.Session（单实例，Connection Keep-Alive）
    - 自动拼接 base_url + path
    - 统一 30s 超时（kwargs 可覆盖）
    - 统一返回 requests.Response（不自动 json()）
    - 统一 raise_for_status()（错误由上层 Service 处理）
    - 网络异常原样抛出（不包装）
"""

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

# 默认超时（秒）
DEFAULT_TIMEOUT = 30


class ApiClient:
    """GTMS 桌面端统一 API 客户端。

    封装 requests.Session，提供 get/post/put/delete 方法。
    自动管理 Bearer Token、超时、base_url 拼接。

    Attributes:
        _base_url: API 基础地址（不含尾部斜杠）。
        _session: requests.Session 单实例。
        _default_timeout: 默认超时秒数。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        client.set_token("eyJhbGci...")
        resp = client.get("/api/users")
        resp = client.post("/api/auth/login", json={"username": "admin", "password": "123"})
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        """初始化 API 客户端。

        Args:
            base_url: API 服务基础地址（如 http://127.0.0.1:8000）。
                      不包含尾部斜杠和 /api 前缀。
                      示例: "http://127.0.0.1:8000"
        """
        self._base_url: str = base_url.rstrip("/")
        self._session: requests.Session = requests.Session()
        self._default_timeout: int = DEFAULT_TIMEOUT
        self._token: str | None = None

        logger.debug("ApiClient 初始化: base_url=%s", self._base_url)

    # ============================================================
    # Token 管理
    # ============================================================

    def set_token(self, token: str | None) -> None:
        """设置 Bearer Token。

        自动在 Session Headers 中设置 Authorization: Bearer <token>。
        传入 None 时等同于 clear_token()。

        Args:
            token: JWT Token 字符串，或 None 以清除 Token。
        """
        self._token = token
        if token is not None:
            self._session.headers.update({"Authorization": f"Bearer {token}"})
            logger.debug("Token 已设置")
        else:
            self._session.headers.pop("Authorization", None)
            logger.debug("Token 已清除")

    def clear_token(self) -> None:
        """清除 Bearer Token。

        从 Session Headers 中移除 Authorization 字段。
        """
        self.set_token(None)

    # ============================================================
    # HTTP 方法（公开 API，冻结）
    # ============================================================

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 GET 请求。

        Args:
            url: 请求路径（如 /api/users），自动拼接 base_url。
            **kwargs: 透传给 requests.Session.request() 的参数。

        Returns:
            requests.Response: HTTP 响应对象。

        Raises:
            requests.HTTPError: HTTP 4xx/5xx 错误。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
            requests.RequestException: 其他请求异常。
        """
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 POST 请求。

        Args:
            url: 请求路径。
            **kwargs: 透传给 requests.Session.request() 的参数。

        Returns:
            requests.Response: HTTP 响应对象。
        """
        return self._request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 PUT 请求。

        Args:
            url: 请求路径。
            **kwargs: 透传给 requests.Session.request() 的参数。

        Returns:
            requests.Response: HTTP 响应对象。
        """
        return self._request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 DELETE 请求。

        Args:
            url: 请求路径。
            **kwargs: 透传给 requests.Session.request() 的参数。

        Returns:
            requests.Response: HTTP 响应对象。
        """
        return self._request("DELETE", url, **kwargs)

    # ============================================================
    # 私有方法
    # ============================================================

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """统一发送 HTTP 请求。

        处理 base_url 拼接、超时设置、raise_for_status()。

        Args:
            method: HTTP 方法（GET/POST/PUT/DELETE）。
            url: 请求路径（如 /api/auth/login）。
            **kwargs: 透传给 requests.Session.request() 的参数。

        Returns:
            requests.Response: HTTP 响应对象。

        Raises:
            requests.HTTPError: 响应状态码 4xx/5xx。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        # 拼接完整 URL
        full_url = f"{self._base_url}{url}"

        # 默认超时（kwargs 可覆盖）
        if "timeout" not in kwargs:
            kwargs["timeout"] = self._default_timeout

        logger.debug("%s %s", method, full_url)

        # 发送请求
        resp = self._session.request(method, full_url, **kwargs)

        # 统一错误检查（不吞异常，由上层 Service 处理）
        resp.raise_for_status()

        return resp


__all__ = [
    "ApiClient",
]