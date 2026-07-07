"""GTMS 桌面端客户管理服务 (Desktop CustomerService)

Sprint 4 — Task 4.4
严格依据 Development Roadmap、Sprint 4 Server Customer Router API。

提供桌面端客户管理 HTTP 请求封装：
    - list_customers()    — 客户列表（分页+搜索）
    - get_customer()      — 客户详情
    - create_customer()   — 创建客户
    - update_customer()   — 修改客户

所有 HTTP 请求通过 ApiClient 发起，禁止直接使用 requests。
不实现任何业务规则，所有校验由 Server CustomerService 负责。
不实现删除功能（Customer 永久保留）。

客户端仅负责：
    - HTTP 请求封装（URL、Query、Body）
    - 将服务器返回的 JSON 原样返回
    - 将服务器异常原样抛出
"""

import logging
from typing import Any

from client.services.api_client import ApiClient

logger = logging.getLogger("gtms.client")


class CustomerService:
    """GTMS 桌面端客户管理服务。

    封装客户查询/创建/修改的 HTTP 请求。
    不实现任何业务规则，不缓存数据，不校验参数。

    Attributes:
        _api_client: ApiClient 实例。

    Usage:
        client = ApiClient("http://127.0.0.1:8000")
        customer_service = CustomerService(client)
        customers = customer_service.list_customers()
    """

    def __init__(self, api_client: ApiClient) -> None:
        """初始化客户管理服务。

        Args:
            api_client: ApiClient 实例（用于发起 HTTP 请求）。
        """
        self._api_client: ApiClient = api_client
        logger.debug("CustomerService 初始化")

    # ============================================================
    # 公开 API
    # ============================================================

    def list_customers(
        self,
        company_name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """查询客户列表（分页+搜索）。

        调用 GET /api/customers。

        Args:
            company_name: 公司名称模糊搜索（可选）。
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
        if company_name:
            params["company_name"] = company_name

        resp = self._api_client.get("/api/customers", params=params)
        data = resp.json()
        logger.debug("客户列表查询: total=%d", data.get("total", 0))
        return data

    def get_customer(
        self,
        customer_id: int,
    ) -> dict[str, Any]:
        """获取客户详情。

        调用 GET /api/customers/{customer_id}。

        Args:
            customer_id: 客户 ID。

        Returns:
            dict: 客户信息。

        Raises:
            requests.HTTPError: 请求失败（客户不存在等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        resp = self._api_client.get(f"/api/customers/{customer_id}")
        data = resp.json()
        logger.debug("客户详情查询: customer_id=%d", customer_id)
        return data

    def create_customer(
        self,
        company_name: str,
        contact_person: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """创建客户。

        调用 POST /api/customers。

        Args:
            company_name: 公司名称（必填）。
            contact_person: 联系人（可选）。
            phone: 联系电话（可选）。
            email: 邮箱（可选）。
            address: 地址（可选）。
            remark: 备注（可选）。

        Returns:
            dict: 新创建的客户信息。

        Raises:
            requests.HTTPError: 请求失败（公司名称重复/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {
            "company_name": company_name,
        }
        if contact_person is not None:
            body["contact_person"] = contact_person
        if phone is not None:
            body["phone"] = phone
        if email is not None:
            body["email"] = email
        if address is not None:
            body["address"] = address
        if remark is not None:
            body["remark"] = remark

        resp = self._api_client.post("/api/customers", json=body)
        data = resp.json()
        logger.info("客户创建成功: company_name=%s", company_name)
        return data

    def update_customer(
        self,
        customer_id: int,
        company_name: str | None = None,
        contact_person: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """修改客户信息。

        调用 PUT /api/customers/{customer_id}。
        仅提交非 None 字段。

        Args:
            customer_id: 客户 ID。
            company_name: 公司名称（可选，None 不更新）。
            contact_person: 联系人（可选，None 不更新）。
            phone: 联系电话（可选，None 不更新）。
            email: 邮箱（可选，None 不更新）。
            address: 地址（可选，None 不更新）。
            remark: 备注（可选，None 不更新）。

        Returns:
            dict: 更新后的客户信息。

        Raises:
            requests.HTTPError: 请求失败（客户不存在/名称重复/权限不足等）。
            requests.ConnectionError: 网络连接失败。
            requests.Timeout: 请求超时。
        """
        body: dict[str, Any] = {}
        if company_name is not None:
            body["company_name"] = company_name
        if contact_person is not None:
            body["contact_person"] = contact_person
        if phone is not None:
            body["phone"] = phone
        if email is not None:
            body["email"] = email
        if address is not None:
            body["address"] = address
        if remark is not None:
            body["remark"] = remark

        resp = self._api_client.put(f"/api/customers/{customer_id}", json=body)
        data = resp.json()
        logger.info("客户更新成功: customer_id=%d", customer_id)
        return data


__all__ = [
    "CustomerService",
]