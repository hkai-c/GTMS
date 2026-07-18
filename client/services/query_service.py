"""GTMS 桌面端查询统计服务 (Desktop QueryService)

Sprint 10 — Task 10.4
依据 SRS §4.8、Query Router (Task 10.3)、
    Desktop Service Standard (§15.10)、§15.13 Query Aggregation Principle。

提供桌面端查询统计 HTTP 请求封装：
    - list_tasks()          — 多条件组合查询
    - get_statistics()      — 统计汇总
    - get_customer_ranking() — 客户排行
    - get_machine_ranking()  — 机型排行
    - export_excel()        — 导出数据准备

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有统计/排行/导出由 Server QueryService。
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


class QueryService:
    """GTMS 桌面端查询统计服务。

    封装查询统计的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        query_service = QueryService(client)
        result = query_service.list_tasks()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化查询统计服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("QueryService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_tasks(
        self,
        customer_id: Optional[int] = None,
        process_status: Optional[str] = None,
        result_status: Optional[str] = None,
        operator_id: Optional[int] = None,
        machine_model: Optional[str] = None,
        keyword: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """多条件组合查询试磨任务列表。

        调用 GET /api/query。
        仅提交非 None 的筛选参数。

        Args:
            customer_id: 客户 ID 筛选（可选）。
            process_status: 流程状态筛选（可选，逗号分隔多值）。
            result_status: 结果状态筛选（可选，逗号分隔多值）。
            operator_id: 操作员 ID 筛选（可选）。
            machine_model: 试磨机型模糊匹配（可选）。
            keyword: 任务编号精确匹配（可选）。
            date_from: 创建日期起始（可选）。
            date_to: 创建日期截止（可选）。
            sort_by: 排序字段。
            sort_order: 排序方向。
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
        if customer_id is not None:
            params["customer_id"] = customer_id
        if process_status is not None:
            params["process_status"] = process_status
        if result_status is not None:
            params["result_status"] = result_status
        if operator_id is not None:
            params["operator_id"] = operator_id
        if machine_model is not None:
            params["machine_model"] = machine_model
        if keyword is not None:
            params["keyword"] = keyword
        if date_from is not None:
            params["date_from"] = date_from.isoformat()
        if date_to is not None:
            params["date_to"] = date_to.isoformat()

        resp = self._api_client.get("/api/query", params=params)
        data = resp.json()
        logger.debug(
            "查询完成: page=%d, total=%d",
            page, data.get("total", 0),
        )
        return data

    def get_statistics(self) -> dict[str, Any]:
        """获取统计摘要数据。

        调用 GET /api/query/statistics。

        Returns:
            dict: 包含 summary + customer_ranking + machine_ranking。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.get("/api/query/statistics")
        data = resp.json()
        logger.debug("统计查询完成")
        return data

    def get_customer_ranking(self) -> list[dict[str, Any]]:
        """获取客户排行。

        调用 GET /api/query/ranking/customers。

        Returns:
            list[dict]: 客户排行列表。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.get("/api/query/ranking/customers")
        data = resp.json()
        logger.debug("客户排行查询完成")
        return data

    def get_machine_ranking(self) -> list[dict[str, Any]]:
        """获取机型排行。

        调用 GET /api/query/ranking/machines。

        Returns:
            list[dict]: 机型排行列表。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.get("/api/query/ranking/machines")
        data = resp.json()
        logger.debug("机型排行查询完成")
        return data

    def export_excel(
        self,
        customer_id: Optional[int] = None,
        process_status: Optional[str] = None,
        result_status: Optional[str] = None,
        operator_id: Optional[int] = None,
        machine_model: Optional[str] = None,
        keyword: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        file_name: str = "export",
    ) -> list[dict[str, Any]]:
        """准备导出数据。

        调用 POST /api/query/export。
        仅提交非 None 的筛选参数。

        Args:
            customer_id: 客户 ID 筛选（可选）。
            process_status: 流程状态筛选（可选）。
            result_status: 结果状态筛选（可选）。
            operator_id: 操作员 ID 筛选（可选）。
            machine_model: 试磨机型模糊匹配（可选）。
            keyword: 任务编号精确匹配（可选）。
            date_from: 创建日期起始（可选）。
            date_to: 创建日期截止（可选）。
            sort_by: 排序字段。
            sort_order: 排序方向。
            file_name: 导出文件名。

        Returns:
            list[dict]: 导出数据列表。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "file_name": file_name,
        }
        if customer_id is not None:
            body["customer_id"] = customer_id
        if process_status is not None:
            body["process_status"] = process_status
        if result_status is not None:
            body["result_status"] = result_status
        if operator_id is not None:
            body["operator_id"] = operator_id
        if machine_model is not None:
            body["machine_model"] = machine_model
        if keyword is not None:
            body["keyword"] = keyword
        if date_from is not None:
            body["date_from"] = date_from.isoformat()
        if date_to is not None:
            body["date_to"] = date_to.isoformat()

        resp = self._api_client.post("/api/query/export", json=body)
        data = resp.json()
        logger.debug(
            "导出数据准备完成: total=%d, file_name=%s",
            len(data), file_name,
        )
        return data


__all__ = [
    "QueryService",
]
