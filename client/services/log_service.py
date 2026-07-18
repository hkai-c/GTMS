"""GTMS 桌面端操作日志服务 (Desktop LogService)

Sprint 11 — Task 11.5
依据 SRS §4.10、Log Router (Task 11.3)、
    §15.15 Audit Logging Principle。

提供桌面端操作日志 HTTP 请求封装：
    - list_logs()   — 分页查询日志
    - get_log()     — 查询单条日志
    - create_log()  — 创建日志（系统内部）
    - export_logs() — 导出数据准备

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有日志操作由 Server LogService。
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


class LogService:
    """GTMS 桌面端操作日志服务。

    封装操作日志的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        log_service = LogService(client)
        result = log_service.list_logs()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化操作日志服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("LogService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_logs(
        self,
        operator_id: Optional[int] = None,
        operation: Optional[str] = None,
        module: Optional[str] = None,
        keyword: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """分页查询操作日志。

        调用 GET /api/log。
        仅提交非 None 的筛选参数。

        Args:
            operator_id: 操作人 ID 筛选（可选）。
            operation: 操作类型筛选（可选，create/update/delete/status_change）。
            module: 模块名称筛选（可选）。
            keyword: 关键字搜索（可选，匹配操作对象和描述）。
            start_time: 开始时间（可选）。
            end_time: 结束时间（可选）。
            sort_by: 排序字段。
            sort_order: 排序方向（asc/desc）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            dict: {"items": [...], "total": N, "page": N, "page_size": N}

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "page": page,
            "page_size": page_size,
        }
        if operator_id is not None:
            params["operator_id"] = operator_id
        if operation is not None:
            params["operation"] = operation
        if module is not None:
            params["module"] = module
        if keyword is not None:
            params["keyword"] = keyword
        if start_time is not None:
            params["start_time"] = start_time.isoformat()
        if end_time is not None:
            params["end_time"] = end_time.isoformat()

        resp = self._api_client.get("/api/log", params=params)
        data = resp.json()
        logger.debug(
            "日志查询完成: page=%d, total=%d",
            page, data.get("total", 0),
        )
        return data

    def get_log(self, log_id: int) -> dict[str, Any]:
        """查询单条操作日志。

        调用 GET /api/log/{log_id}。

        Args:
            log_id: 日志 ID（>= 1）。

        Returns:
            dict: 日志详情。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.get(f"/api/log/{log_id}")
        data = resp.json()
        logger.debug("日志查询完成: id=%d", log_id)
        return data

    def create_log(
        self,
        operator_id: int,
        operation: str,
        module: str,
        target_type: str,
        target_id: int,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """创建操作日志（系统内部调用）。

        调用 POST /api/log。

        Args:
            operator_id: 操作人 ID。
            operation: 操作类型（create/update/delete/status_change）。
            module: 模块名称。
            target_type: 操作对象类型。
            target_id: 操作对象 ID。
            description: 变更描述（可选）。

        Returns:
            dict: 创建的日志记录。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {
            "operator_id": operator_id,
            "operation": operation,
            "module": module,
            "target_type": target_type,
            "target_id": target_id,
        }
        if description is not None:
            body["description"] = description

        resp = self._api_client.post("/api/log", json=body)
        data = resp.json()
        logger.debug(
            "日志创建完成: id=%d, op=%s, module=%s",
            data.get("id", 0), operation, module,
        )
        return data

    def export_logs(
        self,
        operator_id: Optional[int] = None,
        operation: Optional[str] = None,
        module: Optional[str] = None,
        keyword: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[dict[str, Any]]:
        """导出日志数据准备。

        调用 POST /api/log/export。
        仅提交非 None 的筛选参数。

        Args:
            operator_id: 操作人 ID 筛选（可选）。
            operation: 操作类型筛选（可选）。
            module: 模块名称筛选（可选）。
            keyword: 关键字搜索（可选）。
            start_time: 开始时间（可选）。
            end_time: 结束时间（可选）。
            sort_by: 排序字段。
            sort_order: 排序方向。

        Returns:
            list[dict]: 导出数据列表。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if operator_id is not None:
            body["operator_id"] = operator_id
        if operation is not None:
            body["operation"] = operation
        if module is not None:
            body["module"] = module
        if keyword is not None:
            body["keyword"] = keyword
        if start_time is not None:
            body["start_time"] = start_time.isoformat()
        if end_time is not None:
            body["end_time"] = end_time.isoformat()
        # page and page_size for export
        body["page"] = 1
        body["page_size"] = 10000

        resp = self._api_client.post("/api/log/export", json=body)
        data = resp.json()
        logger.debug(
            "日志导出数据准备完成: total=%d",
            len(data),
        )
        return data


__all__ = [
    "LogService",
]
