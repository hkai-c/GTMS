"""GTMS 桌面端工件派发管理服务 (Desktop DispatchService)

Sprint 9 — Task 9.4
依据 SRS §4.7、Dispatch Router (Task 9.3)、
    Desktop Service Development Standard (§15.10)。

提供桌面端工件派发 HTTP 请求封装：
    - list_dispatches()   — 派发记录列表（分页+筛选）
    - get_dispatch()      — 派发记录详情
    - create_dispatch()   — 创建派发记录
    - update_dispatch()   — 修改派发记录
    - delete_dispatch()   — 删除派发记录（软删除）

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有校验由 Server DispatchService 负责。
客户端仅负责：
    - HTTP 请求封装（URL、Query、Body）
    - 将服务器返回的 JSON 原样返回
    - 将服务器异常原样抛出
"""

import logging
from typing import Any, Optional

from client.services.api_client import ApiClient


logger = logging.getLogger("gtms.client")


class DispatchService:
    """GTMS 桌面端工件派发管理服务。

    封装派发记录查询/创建/修改/删除的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        dispatch_service = DispatchService(client)
        dispatches = dispatch_service.list_dispatches()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化工件派发管理服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("DispatchService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_dispatches(
        self,
        direction: Optional[str] = None,
        task_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """查询派发记录列表（分页+筛选）。

        调用 GET /api/dispatch。

        Args:
            direction: 去向方向筛选（可选）。
            task_id: 关联试磨任务 ID（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            dict: {"items": [...], "total": N}

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        if direction is not None:
            params["direction"] = direction
        if task_id is not None:
            params["task_id"] = task_id

        resp = self._api_client.get("/api/dispatch", params=params)
        data = resp.json()
        logger.debug(
            "派发记录列表查询: total=%d",
            data.get("total", 0),
        )
        return data

    def get_dispatch(
        self,
        dispatch_id: int,
    ) -> dict[str, Any]:
        """获取派发记录详情。

        调用 GET /api/dispatch/{dispatch_id}。

        Args:
            dispatch_id: 派发记录 ID。

        Returns:
            dict: 派发记录信息。

        Raises:
            Exception: 请求失败（派发记录不存在等），由 ApiClient 抛出。
        """
        resp = self._api_client.get(f"/api/dispatch/{dispatch_id}")
        data = resp.json()
        logger.debug(
            "派发记录详情查询: dispatch_id=%d",
            dispatch_id,
        )
        return data

    def create_dispatch(
        self,
        task_id: int,
        direction: str,
        dispatch_date: str,
        operator_id: int,
    ) -> dict[str, Any]:
        """创建派发记录。

        调用 POST /api/dispatch。
        由 Server 校验 TrialTask 存在、result_status=PASSED、
        process_status=GRINDING。

        Args:
            task_id: 关联试磨任务 ID（必填）。
            direction: 去向方向（必填，DestinationType 值）。
            dispatch_date: 去向日期（必填，ISO 格式）。
            operator_id: 操作人 ID（必填）。

        Returns:
            dict: 新创建的派发记录信息。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {
            "task_id": task_id,
            "direction": direction,
            "dispatch_date": dispatch_date,
            "operator_id": operator_id,
        }

        resp = self._api_client.post("/api/dispatch", json=body)
        data = resp.json()
        logger.info(
            "派发记录创建成功: task_id=%d",
            task_id,
        )
        return data

    def update_dispatch(
        self,
        dispatch_id: int,
        direction: Optional[str] = None,
        dispatch_date: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """修改派发记录。

        调用 PUT /api/dispatch/{dispatch_id}。
        仅提交非 None 字段。

        Args:
            dispatch_id: 派发记录 ID。
            direction: 去向方向（可选，None 不更新）。
            dispatch_date: 去向日期（可选，None 不更新）。
            operator_id: 操作人 ID（可选，None 不更新）。

        Returns:
            dict: 更新后的派发记录信息。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {}
        if direction is not None:
            body["direction"] = direction
        if dispatch_date is not None:
            body["dispatch_date"] = dispatch_date
        if operator_id is not None:
            body["operator_id"] = operator_id

        resp = self._api_client.put(
            f"/api/dispatch/{dispatch_id}", json=body
        )
        data = resp.json()
        logger.info(
            "派发记录更新成功: dispatch_id=%d",
            dispatch_id,
        )
        return data

    def delete_dispatch(
        self,
        dispatch_id: int,
    ) -> dict[str, Any]:
        """删除派发记录（软删除）。

        调用 DELETE /api/dispatch/{dispatch_id}。

        Args:
            dispatch_id: 派发记录 ID。

        Returns:
            dict: {"message": "派发记录已删除"}

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.delete(f"/api/dispatch/{dispatch_id}")
        data = resp.json()
        logger.info(
            "派发记录删除成功: dispatch_id=%d",
            dispatch_id,
        )
        return data


__all__ = [
    "DispatchService",
]
