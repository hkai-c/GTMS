"""客户服务 (Customer Service)

Sprint 4 — Task 4.2
严格依据 SRS §4.2、CODE_WIKI、Sprint 1 ORM、Sprint 2 Frozen API、Sprint 4 Task 4.1 Schemas。

提供客户查询、创建、更新业务逻辑。
Customer 不提供删除功能（按 Roadmap 设计）。

公开 API:
    - list_customers(db, *, company_name, page, page_size) -> CustomerListResponse
    - get_customer(db, customer_id) -> CustomerResponse
    - create_customer(db, data, operator_id) -> CustomerResponse
    - update_customer(db, customer_id, data, operator_id) -> CustomerResponse

使用方式:
    from server.services.customer_service import CustomerService

    service = CustomerService()
    result = service.list_customers(db, company_name="XX公司")
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from server.schemas.log_schema import LogBase
from server.services.log_service import LogService
from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
)
from server.enums.action_type import ActionType
from server.models import Customer
from server.schemas.customer_schema import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
)

logger = logging.getLogger(__name__)


class CustomerService:

    """客户服务。

    提供客户查询、创建、更新业务逻辑。
    不提供删除功能（按 Roadmap 设计）。
    """

    _log_service = LogService()

    # ============================================================
    # 公开 API
    # ============================================================

    def list_customers(
        self,
        db: Session,
        *,
        company_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> CustomerListResponse:
        """客户列表查询（分页 + 模糊搜索 + 排序）。

        支持按 company_name 模糊搜索（LIKE %xxx%），按 company_name 升序排列。

        Args:
            db: 数据库会话。
            company_name: 公司名称模糊搜索（可选）。
            page: 页码（从 1 开始）。
            page_size: 每页条数。

        Returns:
            CustomerListResponse: 包含 items 与 total。
        """
        query = db.query(Customer).filter(Customer.is_deleted == False)

        # 模糊搜索
        if company_name:
            query = query.filter(Customer.company_name.like(f"%{company_name}%"))

        # 总数
        total = query.count()

        # 分页 + 排序
        offset = (page - 1) * page_size
        items = (
            query.order_by(Customer.company_name.asc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # 转换为响应
        responses = [self._to_response(c) for c in items]

        return CustomerListResponse(items=responses, total=total)

    def get_customer(
        self,
        db: Session,
        customer_id: int,
    ) -> CustomerResponse:
        """根据 ID 查询客户。

        过滤 is_deleted=False 的记录。

        Args:
            db: 数据库会话。
            customer_id: 客户 ID。

        Returns:
            CustomerResponse: 客户信息。

        Raises:
            NotFoundException: 客户不存在或已删除。
        """
        customer = (
            db.query(Customer)
            .filter(Customer.id == customer_id, Customer.is_deleted == False)
            .first()
        )
        if customer is None:
            raise NotFoundException(
                "客户不存在",
                detail={"customer_id": customer_id},
            )

        return self._to_response(customer)

    def create_customer(
        self,
        db: Session,
        data: CustomerCreate,
        operator_id: int,
    ) -> CustomerResponse:
        """创建客户。

        流程:
            ① 自动 strip company_name
            ② 检查 company_name 全库唯一
            ③ 创建 Customer ORM
            ④ 提交事务
            ⑤ 写入 SystemLog（Customer Created）

        Args:
            db: 数据库会话。
            data: 客户创建数据（CustomerCreate Schema）。
            operator_id: 操作人 ID。

        Returns:
            CustomerResponse: 新创建的客户。

        Raises:
            BusinessLogicException: company_name 已存在。
        """
        # ① 自动 strip
        company_name = data.company_name.strip()

        # ② 检查 company_name 唯一
        existing = (
            db.query(Customer)
            .filter(
                Customer.company_name == company_name,
                Customer.is_deleted == False,
            )
            .first()
        )
        if existing is not None:
            raise BusinessLogicException(
                "客户名称已存在。",
                detail={"company_name": company_name},
            )

        # ③ 创建 Customer ORM
        # Schema contact_person → ORM contact
        customer = Customer(
            company_name=company_name,
            contact=data.contact_person,
            phone=data.phone,
            address=data.address,
            created_by=operator_id,
        )
        db.add(customer)
        db.flush()

        try:
            # ④ 提交事务
            db.commit()

            # ⑤ 写入 SystemLog
            self._write_log(
                db,
                operator_id=operator_id,
                action=ActionType.CREATE,
                target_type="Customer",
                target_id=customer.id,
                changes={"company_name": company_name},
            )

            db.refresh(customer)
            logger.info(
                "客户创建成功: customer_id=%d, company_name=%s",
                customer.id,
                company_name,
            )
            return self._to_response(customer)

        except Exception:
            db.rollback()
            logger.exception(
                "客户创建失败: company_name=%s", company_name
            )
            raise

    def update_customer(
        self,
        db: Session,
        customer_id: int,
        data: CustomerUpdate,
        operator_id: int,
    ) -> CustomerResponse:
        """更新客户信息。

        仅更新传入的非 None 字段（exclude_unset）。
        修改 company_name 时自动 strip() 并检查唯一性。

        流程:
            ① 查询客户（不存在则 NotFoundException）
            ② 更新允许的字段
            ③ 提交事务
            ④ 写入 SystemLog（Customer Updated）

        Args:
            db: 数据库会话。
            customer_id: 目标客户 ID。
            data: 更新数据（CustomerUpdate Schema）。
            operator_id: 操作人 ID。

        Returns:
            CustomerResponse: 更新后的客户。

        Raises:
            NotFoundException: 客户不存在。
            BusinessLogicException: company_name 与其它客户重复。
        """
        # ① 查询客户
        customer = (
            db.query(Customer)
            .filter(
                Customer.id == customer_id,
                Customer.is_deleted == False,
            )
            .first()
        )
        if customer is None:
            raise NotFoundException(
                "客户不存在",
                detail={"customer_id": customer_id},
            )

        # ② 记录变更
        changes: dict = {}

        # 仅更新传入的字段（exclude_unset=True）
        update_data = data.model_dump(exclude_unset=True)

        if "company_name" in update_data:
            new_name = update_data["company_name"].strip()
            # 检查唯一性（排除自身）
            existing = (
                db.query(Customer)
                .filter(
                    Customer.company_name == new_name,
                    Customer.is_deleted == False,
                    Customer.id != customer_id,
                )
                .first()
            )
            if existing is not None:
                raise BusinessLogicException(
                    "客户名称已存在。",
                    detail={"company_name": new_name},
                )
            changes["company_name"] = {
                "old": customer.company_name,
                "new": new_name,
            }
            customer.company_name = new_name

        if "contact_person" in update_data:
            changes["contact"] = {
                "old": customer.contact,
                "new": update_data["contact_person"],
            }
            customer.contact = update_data["contact_person"]

        if "phone" in update_data:
            changes["phone"] = {
                "old": customer.phone,
                "new": update_data["phone"],
            }
            customer.phone = update_data["phone"]

        if "address" in update_data:
            changes["address"] = {
                "old": customer.address,
                "new": update_data["address"],
            }
            customer.address = update_data["address"]

        try:
            # ③ 提交事务
            db.commit()

            # ④ 写入 SystemLog
            if changes:
                self._write_log(
                    db,
                    operator_id=operator_id,
                    action=ActionType.UPDATE,
                    target_type="Customer",
                    target_id=customer_id,
                    changes=changes,
                )

            db.refresh(customer)
            logger.info("客户更新成功: customer_id=%d", customer_id)
            return self._to_response(customer)

        except Exception:
            db.rollback()
            logger.exception("客户更新失败: customer_id=%d", customer_id)
            raise

    # ============================================================
    # 私有方法
    # ============================================================

    def _to_response(self, customer: Customer) -> CustomerResponse:
        """将 Customer ORM 实例转换为 CustomerResponse。

        处理 ORM contact 字段 → Schema contact_person 字段的映射。
        email 和 remark 为预留字段，ORM 中无对应列，固定返回 None。

        Args:
            customer: Customer ORM 实例。

        Returns:
            CustomerResponse: 客户响应 Schema。
        """
        return CustomerResponse(
            id=customer.id,
            company_name=customer.company_name,
            contact_person=customer.contact,
            phone=customer.phone,
            email=None,
            address=customer.address,
            remark=None,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )

    def _write_log(
        self,
        db: Session,
        *,
        operator_id: int,
        action: ActionType,
        target_type: str,
        target_id: int,
        changes: Optional[dict] = None,
    ) -> None:
        """写入系统操作日志（委托 LogService）。

        Args:
            db: 数据库会话。
            operator_id: 操作人 ID。
            action: 操作类型。
            target_type: 操作对象类型。
            target_id: 操作对象 ID。
            changes: 变更内容（可选）。
        """
        import json
        log_base = LogBase(
            operator_id=operator_id,
            operation=action,
            module=target_type,
            target_type=target_type,
            target_id=target_id,
            description=(
                json.dumps(changes, ensure_ascii=False, default=str)
                if changes else None
            ),
        )
        self._log_service.create_log(db, log_base)


__all__ = [
    "CustomerService",
]
