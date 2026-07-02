"""
工件去向枚举 (DestinationType)

对应 DB_DESIGN.md trial_tasks.destination。

表示试磨完成后的工件最终去向。

可选值：
    RETURNED_CUSTOMER — 寄回客户
    RETAINED_COMPANY  — 公司留样
    SCRAPPED          — 报废
    RETURNED_SALES    — 返回销售
    OTHER             — 其他
"""

from enum import Enum


class DestinationType(str, Enum):
    """工件去向类型"""

    RETURNED_CUSTOMER = "returned_customer"
    """寄回客户 — 工件寄回客户"""

    RETAINED_COMPANY = "retained_company"
    """公司留样 — 公司保留样件"""

    SCRAPPED = "scrapped"
    """报废 — 工件报废"""

    RETURNED_SALES = "returned_sales"
    """返回销售 — 返回销售人员"""

    OTHER = "other"
    """其他 — 其它情况"""