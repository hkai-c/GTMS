"""
客户模型 (Customer)

对应 DB_DESIGN.md §4.3。

字段（严格对照 DB_DESIGN.md）：
    - id:           主键
    - company_name: 公司名称
    - contact:      联系人
    - phone:        联系电话
    - address:      地址
    - created_by:   创建人 ID（FK → users.id）

使用方式:
    from server.models import Customer
    customer = Customer(company_name="XX公司", contact="张三")
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.trial_task import TrialTask


class Customer(BaseModel):
    """客户模型"""

    __tablename__ = "customers"

    # FK 约束：created_by 列由 BaseModel 提供，此处仅添加 FK 约束
    __table_args__ = (
        ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="SET NULL",
            name="fk_customers_created_by",
        ),
        Index("ix_customers_company_name", "company_name"),
    )

    # ============================================================
    # 业务字段
    # ============================================================

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="公司名称",
    )

    contact: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=None,
        comment="联系人",
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default=None,
        comment="联系电话",
    )

    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="地址",
    )

    # ============================================================
    # 关联关系
    # ============================================================

    # 创建人
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys="Customer.created_by",
        lazy="selectin",
    )

    # 客户下的试磨任务（一对多）
    tasks: Mapped[list["TrialTask"]] = relationship(
        "TrialTask",
        back_populates="customer",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, company_name='{self.company_name}')>"