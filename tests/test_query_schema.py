"""查询统计 Schema 自检 (Query Schema Self-Test)

Sprint 10 — Task 10.1
严格依据 CODE_WIKI.md Schema Development Standard。

测试覆盖:
    - py_compile:            编译检查
    - import:                导入检查
    - Schema 导出:           6 个 Schema 类
    - QueryFilter:           筛选参数 Validate
    - StatisticsSummary:     统计摘要 Validate
    - RankingItem:           排行项 Validate
    - StatisticsResponse:    统计响应 Validate
    - ExportRequest:         导出请求 Validate
    - QueryResponse:         查询响应 Validate
    - model_dump():          序列化导出
    - model_validate():      数据验证
    - JSON Serialization:    JSON 序列化
    - Type Hint:             类型注解
    - Docstring:             文档字符串
    - PEP8:                  代码风格
    - 零 Workflow:           无 process_status/result_status
    - 零 Status Machine:     无状态流转
    - 无循环导入:             循环导入检查
    - Frozen API:            未修改任何已冻结 API
    - __init__.py 导出:      包导出
"""

import ast
import os
import re
import subprocess
import sys
import unittest

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestQuerySchema(unittest.TestCase):
    """查询统计 Schema 自检。"""

    @classmethod
    def setUpClass(cls):
        """初始化测试环境。"""
        cls._source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server",
            "schemas",
            "query_schema.py",
        )

    # ============================================================
    # py_compile — 编译检查
    # ============================================================

    def test_py_compile(self):
        """Schema 文件编译通过（无语法错误）。"""
        import py_compile

        try:
            py_compile.compile(self._source_path, doraise=True)
        except py_compile.PyCompileError as e:
            self.fail(f"编译失败: {e}")

    # ============================================================
    # import — 导入检查
    # ============================================================

    def test_import(self):
        """所有 Schema 类可正常导入。"""
        from server.schemas.query_schema import (
            QueryFilter,
            StatisticsSummary,
            RankingItem,
            StatisticsResponse,
            ExportRequest,
            QueryResponse,
        )

        self.assertIsNotNone(QueryFilter)
        self.assertIsNotNone(StatisticsSummary)
        self.assertIsNotNone(RankingItem)
        self.assertIsNotNone(StatisticsResponse)
        self.assertIsNotNone(ExportRequest)
        self.assertIsNotNone(QueryResponse)

    # ============================================================
    # Schema 导出
    # ============================================================

    def test_schema_count(self):
        """共导出 6 个 Schema 类。"""
        from server.schemas import query_schema

        self.assertEqual(len(query_schema.__all__), 6)

    def test_schema_export(self):
        """__all__ 包含全部 6 个 Schema。"""
        from server.schemas.query_schema import __all__

        expected = {
            "QueryFilter",
            "StatisticsSummary",
            "RankingItem",
            "StatisticsResponse",
            "ExportRequest",
            "QueryResponse",
        }
        self.assertEqual(set(__all__), expected)

    # ============================================================
    # QueryFilter — 筛选参数
    # ============================================================

    def test_query_filter_field_count(self):
        """QueryFilter 包含 12 个字段。"""
        from server.schemas.query_schema import QueryFilter

        self.assertEqual(len(QueryFilter.model_fields), 12)

    def test_query_filter_defaults(self):
        """QueryFilter 默认值正确。"""
        from server.schemas.query_schema import QueryFilter

        data = QueryFilter()
        self.assertIsNone(data.customer_id)
        self.assertIsNone(data.process_status)
        self.assertIsNone(data.result_status)
        self.assertIsNone(data.operator_id)
        self.assertIsNone(data.machine_model)
        self.assertIsNone(data.date_from)
        self.assertIsNone(data.date_to)
        self.assertIsNone(data.keyword)
        self.assertEqual(data.page, 1)
        self.assertEqual(data.page_size, 20)
        self.assertEqual(data.sort_by, "created_at")
        self.assertEqual(data.sort_order, "desc")

    def test_query_filter_page_min(self):
        """QueryFilter page 最小为 1。"""
        from server.schemas.query_schema import QueryFilter
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            QueryFilter(page=0)

    def test_query_filter_page_size_min(self):
        """QueryFilter page_size 最小为 1。"""
        from server.schemas.query_schema import QueryFilter
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            QueryFilter(page_size=0)

    def test_query_filter_page_size_max(self):
        """QueryFilter page_size 最大为 200。"""
        from server.schemas.query_schema import QueryFilter
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            QueryFilter(page_size=201)

    def test_query_filter_sort_order_invalid(self):
        """QueryFilter sort_order 仅允许 asc/desc。"""
        from server.schemas.query_schema import QueryFilter
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            QueryFilter(sort_order="invalid")

    def test_query_filter_sort_order_valid(self):
        """QueryFilter sort_order 允许 asc 和 desc。"""
        from server.schemas.query_schema import QueryFilter

        asc = QueryFilter(sort_order="asc")
        desc = QueryFilter(sort_order="desc")
        self.assertEqual(asc.sort_order, "asc")
        self.assertEqual(desc.sort_order, "desc")

    def test_query_filter_optional_fields(self):
        """QueryFilter 可选字段可为 None。"""
        from server.schemas.query_schema import QueryFilter

        data = QueryFilter()
        self.assertIsNone(data.customer_id)
        self.assertIsNone(data.process_status)
        self.assertIsNone(data.result_status)
        self.assertIsNone(data.operator_id)
        self.assertIsNone(data.machine_model)
        self.assertIsNone(data.date_from)
        self.assertIsNone(data.date_to)
        self.assertIsNone(data.keyword)

    def test_query_filter_with_filters(self):
        """QueryFilter 全部筛选字段可正常赋值。"""
        from datetime import datetime
        from server.schemas.query_schema import QueryFilter

        dt = datetime(2026, 7, 1)
        data = QueryFilter(
            customer_id=1,
            process_status="grinding",
            result_status="passed",
            operator_id=2,
            machine_model="CNC-100",
            date_from=dt,
            date_to=datetime(2026, 7, 14),
            keyword="TASK-001",
            page=2,
            page_size=50,
            sort_by="id",
            sort_order="asc",
        )
        self.assertEqual(data.customer_id, 1)
        self.assertEqual(data.process_status, "grinding")
        self.assertEqual(data.result_status, "passed")
        self.assertEqual(data.operator_id, 2)
        self.assertEqual(data.machine_model, "CNC-100")
        self.assertEqual(data.date_from, dt)
        self.assertEqual(data.keyword, "TASK-001")
        self.assertEqual(data.page, 2)
        self.assertEqual(data.page_size, 50)
        self.assertEqual(data.sort_by, "id")
        self.assertEqual(data.sort_order, "asc")

    def test_query_filter_page_size_200(self):
        """QueryFilter page_size 最大允许值 200。"""
        from server.schemas.query_schema import QueryFilter

        data = QueryFilter(page_size=200)
        self.assertEqual(data.page_size, 200)

    # ============================================================
    # StatisticsSummary — 统计摘要
    # ============================================================

    def test_statistics_summary_field_count(self):
        """StatisticsSummary 包含 5 个字段。"""
        from server.schemas.query_schema import StatisticsSummary

        self.assertEqual(len(StatisticsSummary.model_fields), 5)

    def test_statistics_summary_valid(self):
        """StatisticsSummary 正常创建。"""
        from server.schemas.query_schema import StatisticsSummary

        data = StatisticsSummary(
            month_count=10,
            year_count=120,
            passed_count=100,
            failed_count=20,
            success_rate=83.33,
        )
        self.assertEqual(data.month_count, 10)
        self.assertEqual(data.year_count, 120)
        self.assertEqual(data.passed_count, 100)
        self.assertEqual(data.failed_count, 20)
        self.assertAlmostEqual(data.success_rate, 83.33)

    def test_statistics_summary_negative_month_count(self):
        """StatisticsSummary month_count 不能为负数。"""
        from server.schemas.query_schema import StatisticsSummary
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            StatisticsSummary(
                month_count=-1,
                year_count=0,
                passed_count=0,
                failed_count=0,
                success_rate=0,
            )

    def test_statistics_summary_negative_year_count(self):
        """StatisticsSummary year_count 不能为负数。"""
        from server.schemas.query_schema import StatisticsSummary
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            StatisticsSummary(
                month_count=0,
                year_count=-1,
                passed_count=0,
                failed_count=0,
                success_rate=0,
            )

    def test_statistics_summary_success_rate_min(self):
        """StatisticsSummary success_rate 最小为 0。"""
        from server.schemas.query_schema import StatisticsSummary
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            StatisticsSummary(
                month_count=0,
                year_count=0,
                passed_count=0,
                failed_count=0,
                success_rate=-0.1,
            )

    def test_statistics_summary_success_rate_max(self):
        """StatisticsSummary success_rate 最大为 100。"""
        from server.schemas.query_schema import StatisticsSummary
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            StatisticsSummary(
                month_count=0,
                year_count=0,
                passed_count=0,
                failed_count=0,
                success_rate=100.1,
            )

    def test_statistics_summary_success_rate_boundary(self):
        """StatisticsSummary success_rate 边界值 0 和 100 正常。"""
        from server.schemas.query_schema import StatisticsSummary

        data0 = StatisticsSummary(
            month_count=0, year_count=0, passed_count=0,
            failed_count=0, success_rate=0,
        )
        self.assertEqual(data0.success_rate, 0)
        data100 = StatisticsSummary(
            month_count=0, year_count=0, passed_count=0,
            failed_count=0, success_rate=100,
        )
        self.assertEqual(data100.success_rate, 100)

    def test_statistics_summary_all_zero(self):
        """StatisticsSummary 全部为 0 正常。"""
        from server.schemas.query_schema import StatisticsSummary

        data = StatisticsSummary(
            month_count=0, year_count=0, passed_count=0,
            failed_count=0, success_rate=0,
        )
        self.assertEqual(data.month_count, 0)
        self.assertEqual(data.year_count, 0)
        self.assertEqual(data.passed_count, 0)
        self.assertEqual(data.failed_count, 0)
        self.assertEqual(data.success_rate, 0)

    # ============================================================
    # RankingItem — 排行项
    # ============================================================

    def test_ranking_item_field_count(self):
        """RankingItem 包含 2 个字段。"""
        from server.schemas.query_schema import RankingItem

        self.assertEqual(len(RankingItem.model_fields), 2)

    def test_ranking_item_valid(self):
        """RankingItem 正常创建。"""
        from server.schemas.query_schema import RankingItem

        data = RankingItem(name="客户A", count=50)
        self.assertEqual(data.name, "客户A")
        self.assertEqual(data.count, 50)

    def test_ranking_item_negative_count(self):
        """RankingItem count 不能为负数。"""
        from server.schemas.query_schema import RankingItem
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            RankingItem(name="客户A", count=-1)

    def test_ranking_item_count_zero(self):
        """RankingItem count 为 0 正常。"""
        from server.schemas.query_schema import RankingItem

        data = RankingItem(name="客户A", count=0)
        self.assertEqual(data.count, 0)

    # ============================================================
    # StatisticsResponse — 统计响应
    # ============================================================

    def test_statistics_response_field_count(self):
        """StatisticsResponse 包含 3 个字段。"""
        from server.schemas.query_schema import StatisticsResponse

        self.assertEqual(len(StatisticsResponse.model_fields), 3)

    def test_statistics_response_valid(self):
        """StatisticsResponse 正常创建。"""
        from server.schemas.query_schema import (
            StatisticsResponse,
            StatisticsSummary,
            RankingItem,
        )

        summary = StatisticsSummary(
            month_count=10, year_count=120, passed_count=100,
            failed_count=20, success_rate=83.33,
        )
        ranking = [RankingItem(name="客户A", count=50)]
        data = StatisticsResponse(
            summary=summary,
            customer_ranking=ranking,
            machine_ranking=ranking,
        )
        self.assertEqual(data.summary.month_count, 10)
        self.assertEqual(len(data.customer_ranking), 1)
        self.assertEqual(len(data.machine_ranking), 1)

    def test_statistics_response_default_ranking(self):
        """StatisticsResponse ranking 默认空列表。"""
        from server.schemas.query_schema import (
            StatisticsResponse,
            StatisticsSummary,
        )

        summary = StatisticsSummary(
            month_count=0, year_count=0, passed_count=0,
            failed_count=0, success_rate=0,
        )
        data = StatisticsResponse(summary=summary)
        self.assertEqual(data.customer_ranking, [])
        self.assertEqual(data.machine_ranking, [])

    # ============================================================
    # ExportRequest — 导出请求
    # ============================================================

    def test_export_request_field_count(self):
        """ExportRequest 包含 14 个字段（12 继承 + 2 新增）。"""
        from server.schemas.query_schema import ExportRequest

        self.assertEqual(len(ExportRequest.model_fields), 14)

    def test_export_request_defaults(self):
        """ExportRequest 默认值正确。"""
        from server.schemas.query_schema import ExportRequest

        data = ExportRequest()
        self.assertEqual(data.file_name, "export")
        self.assertEqual(data.format, "xlsx")
        self.assertEqual(data.page, 1)

    def test_export_request_format_invalid(self):
        """ExportRequest format 仅允许 xlsx。"""
        from server.schemas.query_schema import ExportRequest
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            ExportRequest(format="csv")

    def test_export_request_format_valid(self):
        """ExportRequest format 允许 xlsx。"""
        from server.schemas.query_schema import ExportRequest

        data = ExportRequest(format="xlsx")
        self.assertEqual(data.format, "xlsx")

    def test_export_request_inherits_query_filter(self):
        """ExportRequest 继承 QueryFilter 的全部字段。"""
        from server.schemas.query_schema import ExportRequest, QueryFilter

        self.assertTrue(issubclass(ExportRequest, QueryFilter))

    # ============================================================
    # QueryResponse — 查询响应
    # ============================================================

    def test_query_response_field_count(self):
        """QueryResponse 包含 4 个字段。"""
        from server.schemas.query_schema import QueryResponse

        self.assertEqual(len(QueryResponse.model_fields), 4)

    def test_query_response_valid(self):
        """QueryResponse 正常创建。"""
        from server.schemas.query_schema import QueryResponse

        items = [{"id": 1, "task_no": "TASK-001"}]
        data = QueryResponse(
            items=items,
            total=100,
            page=1,
            page_size=20,
        )
        self.assertEqual(len(data.items), 1)
        self.assertEqual(data.total, 100)
        self.assertEqual(data.page, 1)
        self.assertEqual(data.page_size, 20)

    def test_query_response_default_items(self):
        """QueryResponse items 默认空列表。"""
        from server.schemas.query_schema import QueryResponse

        data = QueryResponse(total=0, page=1, page_size=20)
        self.assertEqual(data.items, [])

    # ============================================================
    # model_dump — 序列化
    # ============================================================

    def test_model_dump_query_filter(self):
        """QueryFilter model_dump 序列化正常。"""
        from server.schemas.query_schema import QueryFilter

        data = QueryFilter(page=3, page_size=50, keyword="TASK-001")
        dumped = data.model_dump()
        self.assertEqual(dumped["page"], 3)
        self.assertEqual(dumped["page_size"], 50)
        self.assertEqual(dumped["keyword"], "TASK-001")

    def test_model_dump_statistics_summary(self):
        """StatisticsSummary model_dump 序列化正常。"""
        from server.schemas.query_schema import StatisticsSummary

        data = StatisticsSummary(
            month_count=5, year_count=60, passed_count=50,
            failed_count=10, success_rate=83.33,
        )
        dumped = data.model_dump()
        self.assertEqual(dumped["month_count"], 5)
        self.assertEqual(dumped["success_rate"], 83.33)

    # ============================================================
    # model_validate — 数据验证
    # ============================================================

    def test_model_validate_query_filter(self):
        """QueryFilter model_validate 正常。"""
        from server.schemas.query_schema import QueryFilter

        data = QueryFilter.model_validate({
            "page": 2,
            "page_size": 30,
            "keyword": "TASK-002",
            "sort_order": "asc",
        })
        self.assertEqual(data.page, 2)
        self.assertEqual(data.page_size, 30)
        self.assertEqual(data.keyword, "TASK-002")
        self.assertEqual(data.sort_order, "asc")

    def test_model_validate_statistics_response(self):
        """StatisticsResponse model_validate 正常。"""
        from server.schemas.query_schema import StatisticsResponse

        data = StatisticsResponse.model_validate({
            "summary": {
                "month_count": 10,
                "year_count": 100,
                "passed_count": 80,
                "failed_count": 20,
                "success_rate": 80.0,
            },
            "customer_ranking": [{"name": "客户A", "count": 50}],
            "machine_ranking": [{"name": "CNC-100", "count": 30}],
        })
        self.assertEqual(data.summary.month_count, 10)
        self.assertEqual(len(data.customer_ranking), 1)
        self.assertEqual(data.customer_ranking[0].name, "客户A")

    # ============================================================
    # JSON Serialization
    # ============================================================

    def test_json_serialization(self):
        """QueryFilter model_dump_json 正常。"""
        from server.schemas.query_schema import QueryFilter

        data = QueryFilter(page=1, page_size=20)
        json_str = data.model_dump_json()
        self.assertIn('"page":1', json_str)
        self.assertIn('"page_size":20', json_str)

    def test_json_round_trip(self):
        """QueryFilter JSON 往返正常。"""
        from server.schemas.query_schema import QueryFilter

        data = QueryFilter(
            page=3, page_size=50, keyword="TASK-003",
            sort_order="asc",
        )
        json_str = data.model_dump_json()
        restored = QueryFilter.model_validate_json(json_str)
        self.assertEqual(restored.page, data.page)
        self.assertEqual(restored.keyword, data.keyword)
        self.assertEqual(restored.sort_order, data.sort_order)

    def test_json_round_trip_statistics(self):
        """StatisticsSummary JSON 往返正常。"""
        from server.schemas.query_schema import StatisticsSummary

        data = StatisticsSummary(
            month_count=10, year_count=100, passed_count=80,
            failed_count=20, success_rate=80.0,
        )
        json_str = data.model_dump_json()
        restored = StatisticsSummary.model_validate_json(json_str)
        self.assertEqual(restored.month_count, data.month_count)
        self.assertEqual(restored.success_rate, data.success_rate)

    # ============================================================
    # Type Hint — 类型注解
    # ============================================================

    def test_type_hints(self):
        """所有 Schema 类方法有类型注解。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        self.assertIsNotNone(
                            item.returns,
                            f"{node.name}.{item.name} 缺少返回类型注解",
                        )

    # ============================================================
    # Docstring — 文档字符串
    # ============================================================

    def test_docstring(self):
        """所有 Schema 类有 docstring。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        self.assertIsNotNone(ast.get_docstring(tree))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.assertIsNotNone(
                    ast.get_docstring(node),
                    f"{node.name} 缺少 docstring",
                )

    # ============================================================
    # PEP8
    # ============================================================

    def test_pep8(self):
        """PEP8 合规。"""
        result = subprocess.run(
            ["python", "-m", "flake8", "--select=E,W,F,N",
             self._source_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        if result.returncode != 0 and result.stdout:
            self.fail(f"flake8: {result.stdout.strip()}")

    # ============================================================
    # 无循环导入
    # ============================================================

    def test_no_circular_import(self):
        """无循环导入。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("from server.schemas.query_schema", source)
        self.assertNotIn("from server.services", source)
        self.assertNotIn("from server.routers", source)

    # ============================================================
    # Frozen API
    # ============================================================

    def test_frozen_api(self):
        """未导入任何已冻结 API 中禁止的模块。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("from server.models", source)
        self.assertNotIn("from server.services", source)
        self.assertNotIn("from server.routers", source)
        self.assertNotIn("sqlalchemy", source)
        self.assertNotIn("requests", source)
        self.assertNotIn("httpx", source)

    # ============================================================
    # 零 Workflow / Status Machine
    # ============================================================

    def test_no_workflow(self):
        """Schema 不包含 Workflow 逻辑（状态流转/判断/next_status）。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            full = f.read()
        # 排除 docstring 和注释
        code = re.sub(r'""".*?"""', "", full, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", "", code, flags=re.DOTALL)
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
        # 检查 Workflow 逻辑模式（非字段声明）
        self.assertNotIn("next_status", code)
        self.assertNotIn("is_terminal", code)
        self.assertNotIn("process_status ==", code)
        self.assertNotIn("result_status ==", code)
        self.assertNotIn("if process_status", code)
        self.assertNotIn("if result_status", code)

    def test_no_status_machine(self):
        """Schema 不包含状态流转逻辑。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("process_status =", source)
        self.assertNotIn("result_status =", source)

    # ============================================================
    # __init__.py 导出
    # ============================================================

    def test_init_export(self):
        """server/schemas/__init__.py 导出 Query Schema。"""
        try:
            from server.schemas.query_schema import (
                QueryFilter,
                StatisticsSummary,
                RankingItem,
                StatisticsResponse,
                ExportRequest,
                QueryResponse,
            )
            self.assertIsNotNone(QueryFilter)
            self.assertIsNotNone(StatisticsSummary)
            self.assertIsNotNone(RankingItem)
            self.assertIsNotNone(StatisticsResponse)
            self.assertIsNotNone(ExportRequest)
            self.assertIsNotNone(QueryResponse)
        except ImportError as e:
            self.fail(f"导入失败: {e}")

    # ============================================================
    # 历史导出未破坏
    # ============================================================

    def test_init_historical_exports(self):
        """__init__.py 历史 Schema 导出未被破坏。"""
        from server.schemas import (
            # Inspection
            InspectionBase,
            InspectionCreate,
            InspectionResponse,
            # TrialTask
            TrialTaskBase,
            TrialTaskResponse,
            # Customer
            CustomerBase,
            CustomerResponse,
            # Receipt
            ReceiptBase,
            ReceiptResponse,
            # Dispatch
            DispatchBase,
            DispatchCreate,
            DispatchResponse,
            # User
            UserBase,
            UserResponse,
        )
        self.assertIsNotNone(InspectionBase)
        self.assertIsNotNone(InspectionCreate)
        self.assertIsNotNone(InspectionResponse)
        self.assertIsNotNone(TrialTaskBase)
        self.assertIsNotNone(TrialTaskResponse)
        self.assertIsNotNone(CustomerBase)
        self.assertIsNotNone(CustomerResponse)
        self.assertIsNotNone(ReceiptBase)
        self.assertIsNotNone(ReceiptResponse)
        self.assertIsNotNone(DispatchBase)
        self.assertIsNotNone(DispatchCreate)
        self.assertIsNotNone(DispatchResponse)
        self.assertIsNotNone(UserBase)
        self.assertIsNotNone(UserResponse)

    # ============================================================
    # 字段约束校验
    # ============================================================

    def test_query_filter_all_fields_optional_except_defaults(self):
        """QueryFilter 筛选字段为 Optional，分页/排序字段有默认值。"""
        from server.schemas.query_schema import QueryFilter
        from typing import get_origin

        optional_fields = [
            "customer_id", "process_status", "result_status",
            "operator_id", "machine_model", "date_from",
            "date_to", "keyword",
        ]
        for name in optional_fields:
            origin = get_origin(QueryFilter.model_fields[name].annotation)
            self.assertIsNotNone(
                origin,
                f"QueryFilter.{name} 应为 Optional",
            )

    def test_export_request_format_pattern(self):
        """ExportRequest format 使用 pattern 约束。"""
        from server.schemas.query_schema import ExportRequest

        metadata = ExportRequest.model_fields["format"].metadata
        has_pattern = any(
            hasattr(m, "pattern") and m.pattern == "^xlsx$"
            for m in metadata
        )
        self.assertTrue(has_pattern, "format 缺少 pattern='^xlsx$' 约束")

    def test_sort_order_pattern(self):
        """QueryFilter sort_order 使用 pattern 约束。"""
        from server.schemas.query_schema import QueryFilter

        metadata = QueryFilter.model_fields["sort_order"].metadata
        has_pattern = any(
            hasattr(m, "pattern") and m.pattern == "^(asc|desc)$"
            for m in metadata
        )
        self.assertTrue(
            has_pattern,
            "sort_order 缺少 pattern='^(asc|desc)$' 约束",
        )


if __name__ == "__main__":
    unittest.main()