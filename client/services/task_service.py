"""GTMS 桌面端试磨任务管理服务 (Desktop TaskService)

Sprint 5 — Task 5.4
严格依据 Development Roadmap、Sprint 5 Server TrialTask Router API。

提供桌面端试磨任务 HTTP 请求封装：
    - list_tasks()    — 任务列表（分页+多条件筛选）
    - get_task()      — 任务详情
    - create_task()   — 创建任务
    - update_task()   — 修改任务（含状态流转）
    - delete_task()   — 删除任务（软删除）

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有校验由 Server TaskService 负责。
客户端仅负责：
    - HTTP 请求封装（URL、Query、Body）
    - 将服务器返回的 JSON 原样返回
    - 将服务器异常原样抛出
"""

import logging
from typing import Any

from client.services.api_client import ApiClient

logger = logging.getLogger("gtms.client")


class TaskService:
    """GTMS 桌面端试磨任务管理服务。

    封装试磨任务查询/创建/修改/删除的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        task_service = TaskService(client)
        tasks = task_service.list_tasks()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化试磨任务管理服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("TaskService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_tasks(
        self,
        task_no: str | None = None,
        customer_id: int | None = None,
        process_status: str | None = None,
        result_status: str | None = None,
        sales_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """查询试磨任务列表（分页+多条件筛选）。

        调用 GET /api/tasks。

        Args:
            task_no: 任务编号模糊搜索（可选）。
            customer_id: 客户 ID（可选）。
            process_status: 流程状态（可选）。
            result_status: 结果状态（可选）。
            sales_id: 销售 ID（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            dict: {"items": [...], "total": N}

        Raises:
            requests.HTTPError: 请求失败。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        if task_no is not None:
            params["task_no"] = task_no
        if customer_id is not None:
            params["customer_id"] = customer_id
        if process_status is not None:
            params["process_status"] = process_status
        if result_status is not None:
            params["result_status"] = result_status
        if sales_id is not None:
            params["sales_id"] = sales_id

        resp = self._api_client.get("/api/tasks", params=params)
        data = resp.json()
        logger.debug("任务列表查询: total=%d", data.get("total", 0))
        return data

    def get_task(
        self,
        task_id: int,
    ) -> dict[str, Any]:
        """获取试磨任务详情。

        调用 GET /api/tasks/{task_id}。

        Args:
            task_id: 任务 ID。

        Returns:
            dict: 任务信息。

        Raises:
            requests.HTTPError: 请求失败（任务不存在等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        resp = self._api_client.get(f"/api/tasks/{task_id}")
        data = resp.json()
        logger.debug("任务详情查询: task_id=%d", task_id)
        return data

    def create_task(
        self,
        customer_id: int,
        requirement: str,
        sales_id: int,
        tracking_no: str | None = None,
    ) -> dict[str, Any]:
        """创建试磨任务。

        调用 POST /api/tasks。
        任务编号由 Server 自动生成（YYYYMMDD-N）。

        Args:
            customer_id: 客户 ID（必填）。
            requirement: 加工要求（必填）。
            sales_id: 销售 ID（必填）。
            tracking_no: 快递单号（可选）。

        Returns:
            dict: 新创建的任务信息。

        Raises:
            requests.HTTPError: 请求失败（客户/销售不存在/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {
            "customer_id": customer_id,
            "requirement": requirement,
            "sales_id": sales_id,
        }
        if tracking_no is not None:
            body["tracking_no"] = tracking_no

        resp = self._api_client.post("/api/tasks", json=body)
        data = resp.json()
        logger.info("任务创建成功: customer_id=%d", customer_id)
        return data

    def update_task(
        self,
        task_id: int,
        requirement: str | None = None,
        tracking_no: str | None = None,
        process_status: str | None = None,
        result_status: str | None = None,
        destination: str | None = None,
        destination_date: str | None = None,
        failure_reason: str | None = None,
    ) -> dict[str, Any]:
        """修改试磨任务。

        调用 PUT /api/tasks/{task_id}。
        仅提交非 None 字段。

        Args:
            task_id: 任务 ID。
            requirement: 加工要求（可选，None 不更新）。
            tracking_no: 快递单号（可选，None 不更新）。
            process_status: 流程状态（可选，None 不更新）。
            result_status: 结果状态（可选，None 不更新）。
            destination: 工件去向（可选，None 不更新）。
            destination_date: 工件去向日期（可选，None 不更新）。
            failure_reason: 失败原因（可选，None 不更新）。

        Returns:
            dict: 更新后的任务信息。

        Raises:
            requests.HTTPError: 请求失败（任务不存在/状态不允许编辑/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {}
        if requirement is not None:
            body["requirement"] = requirement
        if tracking_no is not None:
            body["tracking_no"] = tracking_no
        if process_status is not None:
            body["process_status"] = process_status
        if result_status is not None:
            body["result_status"] = result_status
        if destination is not None:
            body["destination"] = destination
        if destination_date is not None:
            body["destination_date"] = destination_date
        if failure_reason is not None:
            body["failure_reason"] = failure_reason

        resp = self._api_client.put(f"/api/tasks/{task_id}", json=body)
        data = resp.json()
        logger.info("任务更新成功: task_id=%d", task_id)
        return data

    def delete_task(
        self,
        task_id: int,
    ) -> dict[str, Any]:
        """删除试磨任务（软删除）。

        调用 DELETE /api/tasks/{task_id}。

        Args:
            task_id: 任务 ID。

        Returns:
            dict: {"message": "任务已删除"}

        Raises:
            requests.HTTPError: 请求失败（任务不存在/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        resp = self._api_client.delete(f"/api/tasks/{task_id}")
        data = resp.json()
        logger.info("任务删除成功: task_id=%d", task_id)
        return data


__all__ = [
    "TaskService",
]
