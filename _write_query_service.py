"""Helper script to write query_service.py."""
import pathlib

content = '''"""查询统计业务层 (Query Service)

Sprint 10 — Task 10.2
严格依据 SRS §4.8、DB_DESIGN、§15.9.20 Performance Standard、
    §15.11 Workflow Standard、§15.12 Status Machine Standard。

提供查询统计的完整只读业务逻辑，包括：
    - 多条件组合查询（分页、排序、筛选）
    - 统计摘要（本月/年度任务数、成功率）
    - 客户排行（按任务数倒序）
    - 机型排行（按任务数倒序）
    - 导出数据准备（仅返回数据，不生成文件）

注意: 本模块只读模块，禁止任何写操作（commit/rollback/flush/
      delete/update/insert），禁止修改 process_status 和 result_status。

公开 API:
    - list_tasks(db, query_filter) -> QueryResponse
    - get_statistics(db) -> StatisticsResponse
    - get_customer_ranking(db) -> list[RankingItem]
    - get_machine_ranking(db) -> list[RankingItem]
    - export_excel(db, export_request) -> list[dict]
"""

import logging
from datetime import datetime

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from server.models import (
    GrindingRecord,
    TrialTask,
)
from server.schemas.query_schema import (
    ExportRequest,
    QueryFilter,
    QueryResponse,
    RankingItem,
    StatisticsResponse,
    StatisticsSummary,
)

logger = logging.getLogger("gtms.server")


class QueryService:
    """查询统计业务服务。

    全部只读查询，不修改任何数据库记录。
    所有过滤、排序、分页均使用 SQLAlchemy ORM，禁止 Python 内存处理。
    统计优先使用 SQLAlchemy Aggregate 函数。
    """

    def list_tasks(
        self,
        db: Session,
        query_filter: QueryFilter,
    ) -> QueryResponse:
        """多条件组合查询试磨任务列表。

        支持 customer_id、process_status、result_status、operator_id、
        machine_model、keyword、date_from、date_to 组合筛选，
        支持分页（page/page_size）和排序（sort_by/sort_order）。

        Args:
            db: 数据库会话。
            query_filter: 查询筛选参数。

        Returns:
            QueryResponse: 包含 items、total、page、page_size。
        """
        query = db.query(TrialTask).filter(
            TrialTask.is_deleted.is_(False)
        )
        query = self._apply_filters(query, query_filter)
        total = query.count()
        query = self._apply_sorting(query, query_filter)
        offset = (query_filter.page - 1) * query_filter.page_size
        query = query.offset(offset).limit(query_filter.page_size)
        tasks = query.all()
        items = [self._task_to_dict(task) for task in tasks]

        logger.info(
            "查询完成: page=%s, page_size=%s, total=%s, returned=%s",
            query_filter.page, query_filter.page_size, total, len(items),
        )

        return QueryResponse(
            items=items, total=total,
            page=query_filter.page, page_size=query_filter.page_size,
        )

    def get_statistics(
        self,
        db: Session,
    ) -> StatisticsResponse:
        """获取统计摘要数据。

        统计本月任务数、年度任务数、通过/未通过数量、成功率。
        全部使用 SQLAlchemy Aggregate 函数，禁止 Python 内存计算。

        Args:
            db: 数据库会话。

        Returns:
            StatisticsResponse: 包含 summary + 排行数据。
        """
        now = datetime.now()
        month_start = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0,
        )
        year_start = now.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0,
        )

        base = db.query(TrialTask).filter(
            TrialTask.is_deleted.is_(False),
        )

        month_count = base.filter(
            TrialTask.created_at >= month_start,
        ).count()
        year_count = base.filter(
            TrialTask.created_at >= year_start,
        ).count()

        from server.enums import TrialTaskResultStatus

        passed_count = base.filter(
            TrialTask.result_status == TrialTaskResultStatus.PASSED,
        ).count()
        failed_count = base.filter(
            TrialTask.result_status == TrialTaskResultStatus.FAILED,
        ).count()

        total_evaluated = passed_count + failed_count
        if total_evaluated > 0:
            success_rate = round(
                (passed_count / total_evaluated) * 100, 2,
            )
        else:
            success_rate = 0.0

        summary = StatisticsSummary(
            month_count=month_count,
            year_count=year_count,
            passed_count=passed_count,
            failed_count=failed_count,
            success_rate=success_rate,
        )

        customer_ranking = self.get_customer_ranking(db)
        machine_ranking = self.get_machine_ranking(db)

        logger.info(
            "统计完成: month=%s, year=%s, passed=%s, failed=%s, rate=%s",
            month_count, year_count, passed_count, failed_count,
            success_rate,
        )

        return StatisticsResponse(
            summary=summary,
            customer_ranking=customer_ranking,
            machine_ranking=machine_ranking,
        )

    def get_customer_ranking(
        self,
        db: Session,
    ) -> list[RankingItem]:
        """获取客户排行（按任务数倒序）。

        GROUP BY customer_id + COUNT，按数量降序排列。

        Args:
            db: 数据库会话。

        Returns:
            list[RankingItem]: 客户排行列表。
        """
        from server.models import Customer

        results = (
            db.query(
                Customer.company_name,
                func.count(TrialTask.id).label("cnt"),
            )
            .join(TrialTask, TrialTask.customer_id == Customer.id)
            .filter(TrialTask.is_deleted.is_(False))
            .filter(Customer.is_deleted.is_(False))
            .group_by(Customer.id, Customer.company_name)
            .order_by(desc("cnt"))
            .limit(10)
            .all()
        )

        ranking = [
            RankingItem(name=name, count=cnt)
            for name, cnt in results
        ]

        logger.info("客户排行完成: returned=%s", len(ranking))
        return ranking

    def get_machine_ranking(
        self,
        db: Session,
    ) -> list[RankingItem]:
        """获取机型排行（按任务数倒序）。

        JOIN grinding_records，GROUP BY machine_type，按数量降序排列。

        Args:
            db: 数据库会话。

        Returns:
            list[RankingItem]: 机型排行列表。
        """
        results = (
            db.query(
                GrindingRecord.machine_type,
                func.count(TrialTask.id).label("cnt"),
            )
            .join(TrialTask, TrialTask.id == GrindingRecord.task_id)
            .filter(TrialTask.is_deleted.is_(False))
            .filter(GrindingRecord.is_deleted.is_(False))
            .group_by(GrindingRecord.machine_type)
            .order_by(desc("cnt"))
            .limit(10)
            .all()
        )

        ranking = [
            RankingItem(name=name, count=cnt)
            for name, cnt in results
        ]

        logger.info("机型排行完成: returned=%s", len(ranking))
        return ranking

    def export_excel(
        self,
        db: Session,
        export_request: ExportRequest,
    ) -> list[dict]:
        """准备导出数据（仅返回数据，不生成文件）。

        根据查询筛选条件获取全部匹配数据，返回二维字典列表。

        Args:
            db: 数据库会话。
            export_request: 导出请求参数。

        Returns:
            list[dict]: 导出数据列表。
        """
        query = db.query(TrialTask).filter(
            TrialTask.is_deleted.is_(False),
        )
        query = self._apply_filters(query, export_request)
        query = self._apply_sorting(query, export_request)
        tasks = query.all()
        items = [self._task_to_dict(task) for task in tasks]

        logger.info(
            "导出数据准备完成: total=%s, file_name=%s",
            len(items), export_request.file_name,
        )
        return items

    def _apply_filters(self, query, query_filter: QueryFilter):
        """应用查询筛选条件到 SQLAlchemy Query。

        全部过滤转化为数据库 WHERE 子句，禁止 Python 内存过滤。

        Args:
            query: SQLAlchemy Query 对象。
            query_filter: 查询筛选参数。

        Returns:
            应用筛选后的 Query 对象。
        """
        from server.enums import (
            TrialTaskProcessStatus,
            TrialTaskResultStatus,
        )

        if query_filter.customer_id is not None:
            query = query.filter(
                TrialTask.customer_id == query_filter.customer_id,
            )

        if query_filter.process_status is not None:
            statuses = [
                TrialTaskProcessStatus(s.strip())
                for s in query_filter.process_status.split(",")
                if s.strip()
            ]
            if statuses:
                query = query.filter(
                    TrialTask.process_status.in_(statuses),
                )

        if query_filter.result_status is not None:
            statuses = [
                TrialTaskResultStatus(s.strip())
                for s in query_filter.result_status.split(",")
                if s.strip()
            ]
            if statuses:
                query = query.filter(
                    TrialTask.result_status.in_(statuses),
                )

        if query_filter.operator_id is not None:
            query = query.filter(
                TrialTask.sales_id == query_filter.operator_id,
            )

        if query_filter.machine_model is not None:
            query = query.join(
                GrindingRecord,
                GrindingRecord.task_id == TrialTask.id,
                isouter=True,
            ).filter(
                GrindingRecord.machine_model.ilike(
                    f"%{query_filter.machine_model}%",
                ),
            )

        if query_filter.date_from is not None:
            query = query.filter(
                TrialTask.created_at >= query_filter.date_from,
            )
        if query_filter.date_to is not None:
            query = query.filter(
                TrialTask.created_at <= query_filter.date_to,
            )

        if query_filter.keyword is not None:
            query = query.filter(
                TrialTask.task_no == query_filter.keyword,
            )

        return query

    def _apply_sorting(self, query, query_filter: QueryFilter):
        """应用排序到 SQLAlchemy Query。

        支持按指定字段排序，默认按 created_at DESC。

        Args:
            query: SQLAlchemy Query 对象。
            query_filter: 查询筛选参数。

        Returns:
            应用排序后的 Query 对象。
        """
        sortable_fields = {
            "id": TrialTask.id,
            "task_no": TrialTask.task_no,
            "created_at": TrialTask.created_at,
            "updated_at": TrialTask.updated_at,
            "process_status": TrialTask.process_status,
            "result_status": TrialTask.result_status,
        }

        sort_column = sortable_fields.get(
            query_filter.sort_by, TrialTask.created_at,
        )

        if query_filter.sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        return query

    def _task_to_dict(self, task: TrialTask) -> dict:
        """将 TrialTask ORM 实例转换为字典。

        提取核心字段用于查询结果展示。

        Args:
            task: TrialTask ORM 实例。

        Returns:
            dict: 任务核心字段字典。
        """
        return {
            "id": task.id,
            "task_no": task.task_no,
            "customer_id": task.customer_id,
            "customer_name": (
                task.customer.company_name if task.customer else ""
            ),
            "requirement": task.requirement,
            "express_no": task.express_no,
            "sales_id": task.sales_id,
            "sales_name": (
                task.sales.username if task.sales else ""
            ),
            "process_status": (
                task.process_status.value
                if task.process_status else ""
            ),
            "result_status": (
                task.result_status.value
                if task.result_status else ""
            ),
            "destination": (
                task.destination.value if task.destination else ""
            ),
            "destination_date": (
                task.destination_date.isoformat()
                if task.destination_date else ""
            ),
            "failure_reason": task.failure_reason or "",
            "created_at": (
                task.created_at.isoformat()
                if task.created_at else ""
            ),
            "updated_at": (
                task.updated_at.isoformat()
                if task.updated_at else ""
            ),
        }


__all__ = [
    "QueryService",
]
'''

path = pathlib.Path("e:/data_control/server/services/query_service.py")
path.write_text(content, encoding="utf-8")
print("Written successfully:", path.stat().st_size, "bytes")