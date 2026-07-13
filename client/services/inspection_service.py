"""GTMS 桌面端检测记录管理服务 (Desktop InspectionService)

Sprint 8 — Task 8.4
严格依据 SRS §4.6、Development Roadmap、Inspection Router (Task 8.3)。

提供桌面端检测记录 HTTP 请求封装：
    - list_inspections()   — 检测记录列表（分页+筛选）
    - get_inspection()     — 检测记录详情
    - create_inspection()  — 创建检测记录
    - finish_inspection()  — 完成检测
    - update_inspection()  — 修改检测记录
    - delete_inspection()  — 删除检测记录（软删除）

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有校验由 Server InspectionService 负责。
客户端仅负责：
    - HTTP 请求封装（URL、Query、Body）
    - 将服务器返回的 JSON 原样返回
    - 将服务器异常原样抛出
"""

import logging
from typing import Any, Optional

from client.services.api_client import ApiClient


logger = logging.getLogger("gtms.client")


class InspectionService:
    """GTMS 桌面端检测记录管理服务。

    封装检测记录查询/创建/完成/修改/删除的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        inspection_service = InspectionService(client)
        inspections = inspection_service.list_inspections()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化检测记录管理服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("InspectionService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_inspections(
        self,
        task_id: Optional[int] = None,
        inspector_id: Optional[int] = None,
        result: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """查询检测记录列表（分页+筛选）。

        调用 GET /api/inspection。

        Args:
            task_id: 关联试磨任务 ID（可选）。
            inspector_id: 检测人 ID（可选）。
            result: 检测结论筛选（可选，passed 或 failed）。
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
        if task_id is not None:
            params["task_id"] = task_id
        if inspector_id is not None:
            params["inspector_id"] = inspector_id
        if result is not None:
            params["inspection_result"] = result

        resp = self._api_client.get("/api/inspection", params=params)
        data = resp.json()
        logger.debug(
            "检测记录列表查询: total=%d",
            data.get("total", 0),
        )
        return data

    def get_inspection(
        self,
        inspection_id: int,
    ) -> dict[str, Any]:
        """获取检测记录详情。

        调用 GET /api/inspection/{inspection_id}。

        Args:
            inspection_id: 检测记录 ID。

        Returns:
            dict: 检测记录信息。

        Raises:
            Exception: 请求失败（检测记录不存在等），由 ApiClient 抛出。
        """
        resp = self._api_client.get(f"/api/inspection/{inspection_id}")
        data = resp.json()
        logger.debug(
            "检测记录详情查询: inspection_id=%d",
            inspection_id,
        )
        return data

    def create_inspection(
        self,
        task_id: int,
        report_path: Optional[str] = None,
        inspector_id: Optional[int] = None,
        accuracy: Optional[str] = None,
        roughness: Optional[str] = None,
        result: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> dict[str, Any]:
        """创建检测记录（上传检测报告）。

        调用 POST /api/inspection。
        由 Server 校验 TrialTask 存在且已开始试磨。

        Args:
            task_id: 关联试磨任务 ID（必填）。
            report_path: 检测报告文件路径（可选）。
            inspector_id: 检测人 ID（可选）。
            accuracy: 精度检测结果（可选）。
            roughness: 表面粗糙度检测结果（可选）。
            result: 检测结论（可选，passed 或 failed）。
            failure_reason: 不合格原因（result=failed 时必填，可选）。

        Returns:
            dict: 新创建的检测记录信息。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {
            "task_id": task_id,
        }
        if report_path is not None:
            body["report_path"] = report_path
        if inspector_id is not None:
            body["inspector_id"] = inspector_id
        if accuracy is not None:
            body["accuracy"] = accuracy
        if roughness is not None:
            body["roughness"] = roughness
        if result is not None:
            body["result"] = result
        if failure_reason is not None:
            body["failure_reason"] = failure_reason

        resp = self._api_client.post("/api/inspection", json=body)
        data = resp.json()
        logger.info(
            "检测记录创建成功: task_id=%d",
            task_id,
        )
        return data

    def finish_inspection(
        self,
        inspection_id: int,
        result: str,
        failure_reason: Optional[str] = None,
    ) -> dict[str, Any]:
        """完成检测。

        调用 POST /api/inspection/{inspection_id}/finish。
        由 Server 设置检测结论并推进 TrialTask.process_status → DISPATCHED。

        Args:
            inspection_id: 检测记录 ID。
            result: 检测结论（passed 或 failed）。
            failure_reason: 不合格原因（result=failed 时必填，可选）。

        Returns:
            dict: 更新后的检测记录信息。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {
            "result": result,
        }
        if failure_reason is not None:
            body["failure_reason"] = failure_reason

        resp = self._api_client.post(
            f"/api/inspection/{inspection_id}/finish", json=body
        )
        data = resp.json()
        logger.info(
            "检测完成: inspection_id=%d, result=%s",
            inspection_id, result,
        )
        return data

    def update_inspection(
        self,
        inspection_id: int,
        report_path: Optional[str] = None,
        accuracy: Optional[str] = None,
        roughness: Optional[str] = None,
        result: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> dict[str, Any]:
        """修改检测记录。

        调用 PUT /api/inspection/{inspection_id}。
        仅提交非 None 字段。

        Args:
            inspection_id: 检测记录 ID。
            report_path: 检测报告文件路径（可选，None 不更新）。
            accuracy: 精度检测结果（可选，None 不更新）。
            roughness: 表面粗糙度检测结果（可选，None 不更新）。
            result: 检测结论（可选，None 不更新）。
            failure_reason: 不合格原因（可选，None 不更新）。

        Returns:
            dict: 更新后的检测记录信息。

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        body: dict[str, Any] = {}
        if report_path is not None:
            body["report_path"] = report_path
        if accuracy is not None:
            body["accuracy"] = accuracy
        if roughness is not None:
            body["roughness"] = roughness
        if result is not None:
            body["result"] = result
        if failure_reason is not None:
            body["failure_reason"] = failure_reason

        resp = self._api_client.put(
            f"/api/inspection/{inspection_id}", json=body
        )
        data = resp.json()
        logger.info(
            "检测记录更新成功: inspection_id=%d",
            inspection_id,
        )
        return data

    def delete_inspection(
        self,
        inspection_id: int,
    ) -> dict[str, Any]:
        """删除检测记录（软删除）。

        调用 DELETE /api/inspection/{inspection_id}。

        Args:
            inspection_id: 检测记录 ID。

        Returns:
            dict: {"message": "检测记录已删除"}

        Raises:
            Exception: 请求失败，由 ApiClient 抛出。
        """
        resp = self._api_client.delete(f"/api/inspection/{inspection_id}")
        data = resp.json()
        logger.info(
            "检测记录删除成功: inspection_id=%d",
            inspection_id,
        )
        return data


__all__ = [
    "InspectionService",
]
