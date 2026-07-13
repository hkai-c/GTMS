"""GTMS 桌面端试磨记录管理服务 (Desktop GrindingService)

Sprint 7 — Task 7.4
严格依据 Development Roadmap、Sprint 7 Grinding Router (Task 7.3)。

提供桌面端试磨记录 HTTP 请求封装：
    - list_grindings()   — 试磨记录列表（分页+筛选）
    - get_grinding()     — 试磨记录详情
    - create_grinding()  — 创建试磨记录（开始试磨）
    - finish_grinding()  — 完成试磨
    - update_grinding()  — 修改试磨记录
    - delete_grinding()  — 删除试磨记录（软删除）

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有校验由 Server GrindingService 负责。
客户端仅负责：
    - HTTP 请求封装（URL、Query、Body）
    - 将服务器返回的 JSON 原样返回
    - 将服务器异常原样抛出
"""

import logging
from datetime import datetime
from typing import Any

from client.services.api_client import ApiClient

logger = logging.getLogger("gtms.client")


class GrindingService:
    """GTMS 桌面端试磨记录管理服务。

    封装试磨记录查询/创建/完成/修改/删除的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        grinding_service = GrindingService(client)
        grindings = grinding_service.list_grindings()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化试磨记录管理服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("GrindingService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_grindings(
        self,
        task_id: int | None = None,
        operator_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """查询试磨记录列表（分页+筛选）。

        调用 GET /api/grinding。

        Args:
            task_id: 关联试磨任务 ID（可选）。
            operator_id: 试磨责任人 ID（可选）。
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
        if task_id is not None:
            params["task_id"] = task_id
        if operator_id is not None:
            params["operator_id"] = operator_id

        resp = self._api_client.get("/api/grinding", params=params)
        data = resp.json()
        logger.debug("试磨记录列表查询: total=%d", data.get("total", 0))
        return data

    def get_grinding(
        self,
        grinding_id: int,
    ) -> dict[str, Any]:
        """获取试磨记录详情。

        调用 GET /api/grinding/{grinding_id}。

        Args:
            grinding_id: 试磨记录 ID。

        Returns:
            dict: 试磨记录信息。

        Raises:
            requests.HTTPError: 请求失败（试磨记录不存在等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        resp = self._api_client.get(f"/api/grinding/{grinding_id}")
        data = resp.json()
        logger.debug("试磨记录详情查询: grinding_id=%d", grinding_id)
        return data

    def create_grinding(
        self,
        task_id: int,
        operator_id: int,
        start_time: datetime,
        machine_type: str | None = None,
        wheel_type: str | None = None,
        params: str | None = None,
        image_paths: str | None = None,
    ) -> dict[str, Any]:
        """创建试磨记录（开始试磨）。

        调用 POST /api/grinding。
        由 Server 推进 TrialTask.process_status 至 GRINDING。

        Args:
            task_id: 关联试磨任务 ID（必填）。
            operator_id: 试磨责任人 ID（必填）。
            start_time: 工件领出时间（必填）。
            machine_type: 试磨机型（可选）。
            wheel_type: 砂轮型号（可选）。
            params: 加工参数（可选）。
            image_paths: 试磨图片路径（可选）。

        Returns:
            dict: 新创建的试磨记录信息。

        Raises:
            requests.HTTPError: 请求失败（任务不存在/状态不合法/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {
            "task_id": task_id,
            "operator_id": operator_id,
            "start_time": start_time.isoformat(),
        }
        if machine_type is not None:
            body["machine_type"] = machine_type
        if wheel_type is not None:
            body["wheel_type"] = wheel_type
        if params is not None:
            body["params"] = params
        if image_paths is not None:
            body["image_paths"] = image_paths

        resp = self._api_client.post("/api/grinding", json=body)
        data = resp.json()
        logger.info("试磨开始成功: task_id=%d", task_id)
        return data

    def finish_grinding(
        self,
        grinding_id: int,
        result_status: str,
        failure_reason: str | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        """完成试磨。

        调用 POST /api/grinding/{grinding_id}/finish。
        由 Server 设置 result_status 并推进 process_status 至 DISPATCHED。

        Args:
            grinding_id: 试磨记录 ID。
            result_status: 试磨结果（passed 或 failed）。
            failure_reason: 失败原因（result_status=failed 时必填，可选）。
            end_time: 完成时间（可选，默认当前时间）。

        Returns:
            dict: 更新后的试磨记录信息。

        Raises:
            requests.HTTPError: 请求失败（状态不合法/参数缺失等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {
            "result_status": result_status,
        }
        if failure_reason is not None:
            body["failure_reason"] = failure_reason
        if end_time is not None:
            body["end_time"] = end_time.isoformat()

        resp = self._api_client.post(
            f"/api/grinding/{grinding_id}/finish", json=body
        )
        data = resp.json()
        logger.info(
            "试磨完成: grinding_id=%d, result=%s",
            grinding_id, result_status,
        )
        return data

    def update_grinding(
        self,
        grinding_id: int,
        machine_type: str | None = None,
        wheel_type: str | None = None,
        params: str | None = None,
        end_time: datetime | None = None,
        image_paths: str | None = None,
        fail_reason: str | None = None,
    ) -> dict[str, Any]:
        """修改试磨记录。

        调用 PUT /api/grinding/{grinding_id}。
        仅提交非 None 字段。

        Args:
            grinding_id: 试磨记录 ID。
            machine_type: 试磨机型（可选，None 不更新）。
            wheel_type: 砂轮型号（可选，None 不更新）。
            params: 加工参数（可选，None 不更新）。
            end_time: 完成时间（可选，None 不更新）。
            image_paths: 试磨图片路径（可选，None 不更新）。
            fail_reason: 失败原因（可选，None 不更新）。

        Returns:
            dict: 更新后的试磨记录信息。

        Raises:
            requests.HTTPError: 请求失败（试磨记录不存在/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {}
        if machine_type is not None:
            body["machine_type"] = machine_type
        if wheel_type is not None:
            body["wheel_type"] = wheel_type
        if params is not None:
            body["params"] = params
        if end_time is not None:
            body["end_time"] = end_time.isoformat()
        if image_paths is not None:
            body["image_paths"] = image_paths
        if fail_reason is not None:
            body["fail_reason"] = fail_reason

        resp = self._api_client.put(
            f"/api/grinding/{grinding_id}", json=body
        )
        data = resp.json()
        logger.info("试磨记录更新成功: grinding_id=%d", grinding_id)
        return data

    def delete_grinding(
        self,
        grinding_id: int,
    ) -> dict[str, Any]:
        """删除试磨记录（软删除）。

        调用 DELETE /api/grinding/{grinding_id}。

        Args:
            grinding_id: 试磨记录 ID。

        Returns:
            dict: {"message": "试磨记录已删除"}

        Raises:
            requests.HTTPError: 请求失败（试磨记录不存在/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        resp = self._api_client.delete(f"/api/grinding/{grinding_id}")
        data = resp.json()
        logger.info("试磨记录删除成功: grinding_id=%d", grinding_id)
        return data


__all__ = [
    "GrindingService",
]
