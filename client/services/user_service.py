"""GTMS 桌面端用户管理服务 (Desktop UserService)

Sprint 3 — Task 3.12
严格依据 Development Roadmap、Sprint 3 Server User Router API。

提供桌面端用户管理业务逻辑：
    - list_users()        — 用户列表（分页+搜索）
    - create_user()       — 创建用户
    - update_user()       — 更新用户
    - delete_user()       — 删除用户
    - get_roles()         — 角色列表

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何 UI。
"""

import logging
from typing import Any

from client.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class UserService:
    """GTMS 桌面端用户管理服务。

    封装用户 CRUD 操作，所有 HTTP 请求通过 ApiClient 发起。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        user_service = UserService(client)
        users = user_service.list_users()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化用户管理服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("UserService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_users(
        self,
        username: str | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """查询用户列表（分页+搜索）。

        调用 GET /api/users。

        Args:
            username: 用户名模糊搜索（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            dict: {"items": [...], "total": N, "page": N, "page_size": N}

        Raises:
            requests.HTTPError: 请求失败。
            requests.ConnectionError: 网络连接失败。
        """
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        if username:
            params["username"] = username

        resp = self._api_client.get("/api/users", params=params)
        data = resp.json()
        logger.debug("用户列表查询: total=%d", data.get("total", 0))
        return data

    def create_user(
        self,
        username: str,
        password: str,
        real_name: str,
        phone: str | None = None,
        role_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        """创建用户。

        调用 POST /api/users。

        Args:
            username: 用户名。
            password: 密码。
            real_name: 真实姓名。
            phone: 联系电话（可选）。
            role_ids: 角色 ID 列表（可选）。

        Returns:
            dict: 用户信息（UserResponse）。

        Raises:
            requests.HTTPError: 请求失败（权限不足/用户名重复等）。
            requests.ConnectionError: 网络连接失败。
        """
        body: dict[str, Any] = {
            "username": username,
            "password": password,
            "real_name": real_name,
        }
        if phone:
            body["phone"] = phone
        if role_ids:
            body["role_ids"] = role_ids

        resp = self._api_client.post("/api/users", json=body)
        data = resp.json()
        logger.info("用户创建成功: username=%s", username)
        return data

    def update_user(
        self,
        user_id: int,
        real_name: str | None = None,
        phone: str | None = None,
        is_active: bool | None = None,
        password: str | None = None,
        role_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        """更新用户信息。

        调用 PUT /api/users/{user_id}。

        Args:
            user_id: 用户 ID。
            real_name: 真实姓名（可选，None 不更新）。
            phone: 联系电话（可选，None 不更新）。
            is_active: 启用状态（可选，None 不更新）。
            password: 新密码（可选，None 不更新）。
            role_ids: 角色 ID 列表（可选，None 不更新）。

        Returns:
            dict: 更新后的用户信息。

        Raises:
            requests.HTTPError: 请求失败。
            requests.ConnectionError: 网络连接失败。
        """
        body: dict[str, Any] = {}
        if real_name is not None:
            body["real_name"] = real_name
        if phone is not None:
            body["phone"] = phone
        if is_active is not None:
            body["is_active"] = is_active
        if password:
            body["password"] = password
        if role_ids is not None:
            body["role_ids"] = role_ids

        resp = self._api_client.put(f"/api/users/{user_id}", json=body)
        data = resp.json()
        logger.info("用户更新成功: user_id=%d", user_id)
        return data

    def delete_user(self, user_id: int) -> dict[str, Any]:
        """删除用户（软删除）。

        调用 DELETE /api/users/{user_id}。

        Args:
            user_id: 用户 ID。

        Returns:
            dict: {"message": "User deleted successfully."}

        Raises:
            requests.HTTPError: 请求失败。
            requests.ConnectionError: 网络连接失败。
        """
        resp = self._api_client.delete(f"/api/users/{user_id}")
        data = resp.json()
        logger.info("用户删除成功: user_id=%d", user_id)
        return data

    def get_roles(self) -> dict[str, Any]:
        """获取角色列表。

        调用 GET /api/roles。

        Returns:
            dict: {"items": [...], "total": N}

        Raises:
            requests.HTTPError: 请求失败。
            requests.ConnectionError: 网络连接失败。
        """
        resp = self._api_client.get("/api/roles")
        data = resp.json()
        logger.debug("角色列表查询: total=%d", data.get("total", 0))
        return data


__all__ = [
    "UserService",
]