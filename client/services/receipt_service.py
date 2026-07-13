"""GTMS 桌面端收件记录管理服务 (Desktop ReceiptService)

Sprint 6 — Task 6.5
严格依据 Development Roadmap、Sprint 6 Receipt Router、Sprint 6 Upload Router。

提供桌面端收件记录 HTTP 请求封装：
    - create_receipt()       — 创建收件记录
    - list_receipts()        — 收件记录列表（分页+多条件筛选）
    - get_receipt()          — 收件记录详情
    - update_receipt()       — 修改收件记录
    - delete_receipt()       — 删除收件记录（软删除）
    - upload_receipt_image() — 上传收件图片

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有校验由 Server ReceiptService 负责。
客户端仅负责：
    - HTTP 请求封装（URL、Query、Body）
    - 将服务器返回的 JSON 原样返回
    - 将服务器异常原样抛出
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from client.services.api_client import ApiClient

logger = logging.getLogger("gtms.client")


class ReceiptService:
    """GTMS 桌面端收件记录管理服务。

    封装收件记录查询/创建/修改/删除/图片上传的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        receipt_service = ReceiptService(client)
        receipts = receipt_service.list_receipts()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化收件记录管理服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("ReceiptService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_receipts(
        self,
        task_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        customer_id: int | None = None,
        sales_id: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """查询收件记录列表（分页+多条件筛选）。

        调用 GET /api/receipts。

        Args:
            task_id: 关联试磨任务 ID（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。
            keyword: 关键字搜索（可选）。
            customer_id: 客户 ID（可选）。
            sales_id: 销售 ID（可选）。
            start_date: 开始日期（可选，格式 YYYY-MM-DD）。
            end_date: 结束日期（可选，格式 YYYY-MM-DD）。

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
        if keyword is not None:
            params["keyword"] = keyword
        if customer_id is not None:
            params["customer_id"] = customer_id
        if sales_id is not None:
            params["sales_id"] = sales_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date

        resp = self._api_client.get("/api/receipts", params=params)
        data = resp.json()
        logger.debug("收件记录列表查询: total=%d", data.get("total", 0))
        return data

    def get_receipt(
        self,
        receipt_id: int,
    ) -> dict[str, Any]:
        """获取收件记录详情。

        调用 GET /api/receipts/{receipt_id}。

        Args:
            receipt_id: 收件记录 ID。

        Returns:
            dict: 收件记录信息。

        Raises:
            requests.HTTPError: 请求失败（收件记录不存在等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        resp = self._api_client.get(f"/api/receipts/{receipt_id}")
        data = resp.json()
        logger.debug("收件记录详情查询: receipt_id=%d", receipt_id)
        return data

    def create_receipt(
        self,
        task_id: int,
        received_at: datetime,
        receiver_id: int,
        image_paths: str | None = None,
    ) -> dict[str, Any]:
        """创建收件记录。

        调用 POST /api/receipts。
        由 Server 推进 TrialTask.process_status 至 RECEIVED。

        Args:
            task_id: 关联试磨任务 ID（必填）。
            received_at: 收件日期时间（必填）。
            receiver_id: 收件人 ID（必填）。
            image_paths: 工件图片路径（可选，JSON 数组文本）。

        Returns:
            dict: 新创建的收件记录信息。

        Raises:
            requests.HTTPError: 请求失败（任务不存在/状态不合法/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {
            "task_id": task_id,
            "received_at": received_at.isoformat(),
            "receiver_id": receiver_id,
        }
        if image_paths is not None:
            body["image_paths"] = image_paths

        resp = self._api_client.post("/api/receipts", json=body)
        data = resp.json()
        logger.info("收件记录创建成功: task_id=%d", task_id)
        return data

    def update_receipt(
        self,
        receipt_id: int,
        task_id: int | None = None,
        received_at: datetime | None = None,
        receiver_id: int | None = None,
        image_paths: str | None = None,
    ) -> dict[str, Any]:
        """修改收件记录。

        调用 PUT /api/receipts/{receipt_id}。
        仅提交非 None 字段。

        Args:
            receipt_id: 收件记录 ID。
            task_id: 关联试磨任务 ID（可选，None 不更新）。
            received_at: 收件日期时间（可选，None 不更新）。
            receiver_id: 收件人 ID（可选，None 不更新）。
            image_paths: 工件图片路径（可选，None 不更新）。

        Returns:
            dict: 更新后的收件记录信息。

        Raises:
            requests.HTTPError: 请求失败（收件记录不存在/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {}
        if task_id is not None:
            body["task_id"] = task_id
        if received_at is not None:
            body["received_at"] = received_at.isoformat()
        if receiver_id is not None:
            body["receiver_id"] = receiver_id
        if image_paths is not None:
            body["image_paths"] = image_paths

        resp = self._api_client.put(f"/api/receipts/{receipt_id}", json=body)
        data = resp.json()
        logger.info("收件记录更新成功: receipt_id=%d", receipt_id)
        return data

    def delete_receipt(
        self,
        receipt_id: int,
    ) -> dict[str, Any]:
        """删除收件记录（软删除）。

        调用 DELETE /api/receipts/{receipt_id}。

        Args:
            receipt_id: 收件记录 ID。

        Returns:
            dict: {"message": "收件记录已删除"}

        Raises:
            requests.HTTPError: 请求失败（收件记录不存在/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        resp = self._api_client.delete(f"/api/receipts/{receipt_id}")
        data = resp.json()
        logger.info("收件记录删除成功: receipt_id=%d", receipt_id)
        return data

    def upload_receipt_image(
        self,
        task_no: str,
        file_path: str,
    ) -> dict[str, Any]:
        """上传收件图片。

        调用 POST /api/upload/image。
        通过 multipart/form-data 上传图片文件。

        Args:
            task_no: 任务编号（如 "20260701-1"）。
            file_path: 图片文件路径。

        Returns:
            dict: {"filename": ..., "url": ..., "content_type": ..., "size": ...}

        Raises:
            requests.HTTPError: 请求失败（文件校验失败等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
            FileNotFoundError: 文件不存在。
        """
        path = Path(file_path)
        filename = path.name
        content_type = _get_content_type(path)

        with open(file_path, "rb") as f:
            resp = self._api_client.post(
                "/api/upload/image",
                data={"task_no": task_no},
                files={"file": (filename, f, content_type)},
            )

        data = resp.json()
        logger.info(
            "图片上传成功: task_no=%s, filename=%s, size=%d",
            task_no, data.get("filename"), data.get("size", 0),
        )
        return data


# ============================================================
# 私有函数
# ============================================================


def _get_content_type(file_path: Path) -> str:
    """根据文件扩展名获取 MIME 类型。

    Args:
        file_path: 文件路径。

    Returns:
        MIME 类型字符串，如 "image/jpeg"、"image/png"。
    """
    suffix = file_path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }
    return mime_map.get(suffix, "application/octet-stream")


__all__ = [
    "ReceiptService",
]
