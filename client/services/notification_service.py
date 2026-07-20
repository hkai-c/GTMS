"""GTMS 桌面端消息提醒服务 (Desktop NotificationService)

Sprint 12 — Task 12.5
依据 SRS §4.9、Notification Router (Task 12.3)、
    §15.17 Notification Principle。

提供桌面端消息提醒 HTTP 请求封装：
    - list_notifications()    — 分页查询
    - get_notification()      — 查询单条
    - create_notification()   — 创建消息
    - mark_as_read()          — 标记已读
    - mark_all_as_read()      — 全部已读

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有消息提醒操作由 Server
NotificationService 负责。
客户端仅：
    - HTTP 请求封装（URL、Query、Body）
    - 将服务器返回的 JSON 原样返回
    - 将服务器异常原样抛出
"""

import logging
from datetime import datetime
from typing import Any, Optional

from client.services.api_client import ApiClient


logger = logging.getLogger("gtms.client")


class NotificationService:
    """GTMS 桌面端消息提醒服务。

    封装消息提醒的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        notification_service = NotificationService(client)
        result = notification_service.list_notifications()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化消息提醒服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("NotificationService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_notifications(
        self,
        is_read: Optional[bool] = None,
        notification_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """分页查询消息提醒。

        调用 GET /api/notifications。
        仅提交非 None 的筛选参数。

        Args:
            is_read: 已读状态筛选（可选，true/false）。
            notification_type: 提醒类型筛选（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            dict: {"items": [...], "total": N, "page": N, "page_size": N}

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        if is_read is not None:
            params["is_read"] = is_read
        if notification_type is not None:
            params["notification_type"] = notification_type

        resp = self._api_client.get("/api/notifications", params=params)
        data = resp.json()
        logger.debug(
            "消息查询完成: page=%d, total=%d",
            page, data.get("total", 0),
        )
        return data

    def get_notification(
        self,
        notification_id: int,
    ) -> dict[str, Any]:
        """查询单条消息提醒。

        调用 GET /api/notifications/{notification_id}。

        Args:
            notification_id: 消息提醒 ID（>= 1）。

        Returns:
            dict: 消息提醒详情。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.get(
            f"/api/notifications/{notification_id}",
        )
        data = resp.json()
        logger.debug("消息查询完成: id=%d", notification_id)
        return data

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        content: str,
        target_type: str,
        target_id: int,
        is_read: bool = False,
        created_at: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """创建消息提醒。

        调用 POST /api/notifications。

        Args:
            user_id: 目标用户 ID。
            notification_type: 提醒类型。
            title: 消息标题。
            content: 消息内容。
            target_type: 关联对象类型。
            target_id: 关联对象 ID。
            is_read: 是否已读（默认 False）。
            created_at: 创建时间（可选）。

        Returns:
            dict: 创建的消息提醒。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {
            "user_id": user_id,
            "notification_type": notification_type,
            "title": title,
            "content": content,
            "target_type": target_type,
            "target_id": target_id,
            "is_read": is_read,
        }
        if created_at is not None:
            body["created_at"] = created_at.isoformat()

        resp = self._api_client.post("/api/notifications", json=body)
        data = resp.json()
        logger.debug(
            "消息创建完成: id=%d, type=%s",
            data.get("id", 0), notification_type,
        )
        return data

    def mark_as_read(
        self,
        notification_id: int,
    ) -> dict[str, Any]:
        """标记消息已读。

        调用 PUT /api/notifications/{notification_id}/read。

        Args:
            notification_id: 消息提醒 ID（>= 1）。

        Returns:
            dict: 更新后的消息提醒。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.put(
            f"/api/notifications/{notification_id}/read",
        )
        data = resp.json()
        logger.debug("消息标记已读: id=%d", notification_id)
        return data

    def mark_all_as_read(
        self,
    ) -> int:
        """全部标记已读。

        调用 PUT /api/notifications/read-all。

        Returns:
            int: 已更新数量。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.put("/api/notifications/read-all")
        data = resp.json()
        logger.debug("全部消息标记已读: count=%d", data)
        return data


__all__ = [
    "NotificationService",
]
