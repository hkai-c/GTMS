"""操作日志业务层 (Log Service)

Sprint 11 — Task 11.2
依据 SRS 4.10、DB_DESIGN 4.10、CODE_WIKI 15.15。

提供操作日志的完整业务逻辑：
    - 日志查询（分页、排序、筛选）
    - 日志写入（供各业务 Service 调用）
    - 日志导出数据准备

公开 API:
    - list_logs(db, log_query) -> LogListResponse
    - get_log(db, log_id) -> LogResponse
    - create_log(db, log_base) -> LogResponse
    - export_logs(db, log_query) -> list[dict]
"""

import logging

from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from server.models.system_log import SystemLog
from server.schemas.log_schema import (
    LogBase,
    LogListResponse,
    LogQuery,
    LogResponse,
)

logger = logging.getLogger("gtms.server")


class LogService:
    """操作日志业务服务。

    基础设施服务，负责日志的创建、查询和导出数据准备。
    所有查询支持分页、排序、多条件筛选。
    创建日志需提交事务，查询和导出为只读操作。
    """

    def list_logs(
        self,
        db: Session,
        log_query: LogQuery,
    ) -> LogListResponse:
        """分页查询操作日志列表。"""
        query = db.query(SystemLog).filter(
            SystemLog.is_deleted.is_(False)
        )
        query = self._apply_filters(query, log_query)
        total = query.count()
        query = self._apply_sorting(query, log_query)
        offset = (log_query.page - 1) * log_query.page_size
        query = query.offset(offset).limit(log_query.page_size)
        logs = query.all()
        items = [self._to_log_response(log) for log in logs]
        logger.info(
            "list_logs: page=%d, total=%d, items=%d",
            log_query.page, total, len(items),
        )
        return LogListResponse(items=items, total=total)

    def _apply_filters(self, query, log_query: LogQuery):
        """应用筛选条件。"""
        if log_query.operator_id is not None:
            query = query.filter(
                SystemLog.user_id == log_query.operator_id
            )
        if log_query.operation is not None:
            query = query.filter(
                SystemLog.action == log_query.operation
            )
        if log_query.module is not None:
            query = query.filter(
                SystemLog.changes["module"].astext == log_query.module
            )
        if log_query.keyword is not None:
            keyword = f"%{log_query.keyword}%"
            query = query.filter(
                or_(
                    SystemLog.target_type.ilike(keyword),
                    SystemLog.changes["description"].astext.ilike(
                        keyword
                    ),
                )
            )
        if log_query.start_time is not None:
            query = query.filter(
                SystemLog.created_at >= log_query.start_time
            )
        if log_query.end_time is not None:
            query = query.filter(
                SystemLog.created_at <= log_query.end_time
            )
        return query

    def _apply_sorting(self, query, log_query: LogQuery):
        """应用排序。"""
        sort_column = getattr(
            SystemLog, log_query.sort_by, None
        )
        if sort_column is None:
            sort_column = SystemLog.created_at
        if log_query.sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(desc(sort_column))
        return query

    def get_log(
        self,
        db: Session,
        log_id: int,
    ) -> LogResponse:
        """获取单条操作日志。"""
        log = (
            db.query(SystemLog)
            .filter(
                SystemLog.is_deleted.is_(False),
                SystemLog.id == log_id,
            )
            .first()
        )
        if log is None:
            raise ValueError(
                f"日志不存在: id={log_id}"
            )
        logger.debug("get_log: id=%d", log_id)
        return self._to_log_response(log)

    def create_log(
        self,
        db: Session,
        log_base: LogBase,
    ) -> LogResponse:
        """创建操作日志（供各业务 Service 调用）。"""
        changes = {
            "module": log_base.module,
            "description": log_base.description,
        }
        log = SystemLog(
            user_id=log_base.operator_id,
            action=log_base.operation,
            target_type=log_base.target_type,
            target_id=log_base.target_id,
            changes=changes,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        logger.info(
            "create_log: id=%d, user_id=%d, action=%s, "
            "target_type=%s",
            log.id, log.user_id, log.action.value,
            log.target_type,
        )
        return self._to_log_response(log)

    def export_logs(
        self,
        db: Session,
        log_query: LogQuery,
    ) -> list[dict]:
        """导出日志数据准备（仅准备数据，不生成文件）。"""
        query = db.query(SystemLog).filter(
            SystemLog.is_deleted.is_(False)
        )
        query = self._apply_filters(query, log_query)
        query = self._apply_sorting(query, log_query)
        logs = query.all()
        data = [self._to_export_dict(log) for log in logs]
        logger.info(
            "export_logs: total=%d", len(data),
        )
        return data

    def _to_log_response(
        self, log: SystemLog
    ) -> LogResponse:
        """SystemLog -> LogResponse。"""
        changes = log.changes or {}
        return LogResponse(
            id=log.id,
            operator_id=log.user_id,
            operation=log.action,
            module=changes.get("module", ""),
            target_type=log.target_type,
            target_id=log.target_id,
            description=changes.get("description", ""),
            created_at=log.created_at,
        )

    def _to_export_dict(
        self, log: SystemLog
    ) -> dict:
        """SystemLog -> 导出字典。"""
        changes = log.changes or {}
        return {
            "id": log.id,
            "operator_id": log.user_id,
            "operation": log.action.value,
            "module": changes.get("module", ""),
            "target_type": log.target_type,
            "target_id": log.target_id,
            "description": changes.get("description", ""),
            "created_at": (
                log.created_at.isoformat()
                if log.created_at else ""
            ),
        }


__all__ = [
    "LogService",
]
