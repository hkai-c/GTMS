"""GTMS 桌面端系统设置服务 (Desktop SettingsService)

Sprint 13 — Task 13.6
依据 SRS §4.12 FR-SETTINGS、Settings Router (Task 13.5)、
    §15.20 Desktop HTTP Mapping Principle、§15.22 Settings Principle。

提供桌面端系统设置 HTTP 请求封装：
    - get_settings()    — 读取系统配置
    - update_settings() — 更新系统配置

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有设置操作由 Server SettingsService 负责。
客户端仅：
    - HTTP 请求封装（URL、Body）
    - 将服务器返回的 JSON 原样返回
    - 将服务器异常原样抛出
"""

import logging
from typing import Any

from client.services.api_client import ApiClient


# ============================================================
# 常量
# ============================================================

SETTINGS_PATH: str = "/api/settings"

logger = logging.getLogger("gtms.client")


class SettingsService:
    """GTMS 桌面端系统设置服务。

    封装系统设置的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        settings_service = SettingsService(client)
        result = settings_service.get_settings()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化系统设置服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("SettingsService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def get_settings(self) -> dict[str, Any]:
        """读取系统配置。

        调用 GET /api/settings。

        Returns:
            dict: 系统配置 JSON。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.get(SETTINGS_PATH)
        data = resp.json()
        logger.debug("系统配置读取完成")
        return data

    def update_settings(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """更新系统配置。

        调用 PUT /api/settings。
        仅发送非 None 的字段。

        Args:
            **kwargs: 待更新的配置字段（仅非 None 字段生效）。

        Returns:
            dict: 更新后的完整配置 JSON。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body = {k: v for k, v in kwargs.items() if v is not None}
        resp = self._api_client.put(SETTINGS_PATH, json=body)
        data = resp.json()
        logger.debug("系统配置更新完成")
        return data


__all__ = [
    "SettingsService",
]
