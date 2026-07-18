"""操作日志 Schema 自检 (Log Schema Self-Test)

Sprint 11 — Task 11.1
严格依据 CODE_WIKI.md 15.15 Audit Logging Principle。

测试覆盖:
    - py_compile / import / Schema 导出
    - LogBase 字段验证、枚举、空字符串
    - LogResponse 继承 + id 字段
    - LogListResponse 列表响应
    - LogQuery 查询参数验证、分页、排序
    - model_dump / JSON / Type Hint / Docstring / PEP8
    - Zero Workflow / Zero Status Machine
    - 无循环导入 / Frozen API / __init__.py 导出
"""

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestLogSchema(unittest.TestCase):
    """操作日志 Schema 自检。"""

    @classmethod
    def setUpClass(cls):
        cls._source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server", "schemas", "log_schema.py",
        )

    def test_py_compile(self):
        import py_compile
        try:
            py_compile.compile(self._source_path, doraise=True)
        except py_compile.PyCompileError as e:
            self.fail(f"compile: {e}")

    def test_import(self):
        from server.schemas.log_schema import (
            LogBase, LogResponse, LogListResponse, LogQuery,
        )
        self.assertIsNotNone(LogBase)
        self.assertIsNotNone(LogResponse)
        self.assertIsNotNone(LogListResponse)
        self.assertIsNotNone(LogQuery)

    def test_schema_count(self):
        from server.schemas import log_schema
        self.assertEqual(len(log_schema.__all__), 4)

    def test_schema_export(self):
        from server.schemas.log_schema import __all__
        expected = {"LogBase", "LogResponse", "LogListResponse", "LogQuery"}
        self.assertEqual(set(__all__), expected)

    def test_log_base_valid(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        log = LogBase(operator_id=1, operation=ActionType.CREATE,
                       module="customer", target_type="Customer",
                       target_id=5, description="create customer",
                       created_at=datetime(2026, 1, 1, 12, 0, 0))
        self.assertEqual(log.operator_id, 1)
        self.assertEqual(log.operation, ActionType.CREATE)
        self.assertEqual(log.module, "customer")
        self.assertEqual(log.target_type, "Customer")
        self.assertEqual(log.target_id, 5)
        self.assertEqual(log.description, "create customer")

    def test_log_base_operator_id_zero(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogBase(operator_id=0, operation=ActionType.CREATE,
                    module="customer", target_type="Customer",
                    description="test",
                    created_at=datetime(2026, 1, 1, 12, 0, 0))

    def test_log_base_module_empty(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogBase(operator_id=1, operation=ActionType.CREATE,
                    module="", target_type="Customer",
                    description="test",
                    created_at=datetime(2026, 1, 1, 12, 0, 0))

    def test_log_base_target_type_empty(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogBase(operator_id=1, operation=ActionType.CREATE,
                    module="customer", target_type="",
                    description="test",
                    created_at=datetime(2026, 1, 1, 12, 0, 0))

    def test_log_base_description_too_long(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogBase(operator_id=1, operation=ActionType.CREATE,
                    module="customer", target_type="Customer",
                    description="x" * 1001,
                    created_at=datetime(2026, 1, 1, 12, 0, 0))

    def test_log_base_target_id_negative(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogBase(operator_id=1, operation=ActionType.CREATE,
                    module="customer", target_type="Customer",
                    target_id=-1, description="test",
                    created_at=datetime(2026, 1, 1, 12, 0, 0))

    def test_log_base_operation_enum(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        for op in [ActionType.CREATE, ActionType.UPDATE,
                    ActionType.DELETE, ActionType.STATUS_CHANGE]:
            log = LogBase(operator_id=1, operation=op,
                          module="customer", target_type="Customer",
                          description="test",
                          created_at=datetime(2026, 1, 1, 12, 0, 0))
            self.assertEqual(log.operation, op)

    def test_log_base_target_id_default_none(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        log = LogBase(operator_id=1, operation=ActionType.CREATE,
                      module="customer", target_type="Customer",
                      description="test",
                      created_at=datetime(2026, 1, 1, 12, 0, 0))
        self.assertIsNone(log.target_id)

    def test_log_response_inherits(self):
        from server.schemas.log_schema import LogBase, LogResponse
        self.assertTrue(issubclass(LogResponse, LogBase))

    def test_log_response_has_id(self):
        from server.schemas.log_schema import LogResponse
        self.assertIn("id", LogResponse.model_fields)

    def test_log_response_valid(self):
        from server.schemas.log_schema import LogResponse
        from server.enums.action_type import ActionType
        from datetime import datetime
        log = LogResponse(id=1, operator_id=1, operation=ActionType.CREATE,
                          module="customer", target_type="Customer",
                          description="test",
                          created_at=datetime(2026, 1, 1, 12, 0, 0))
        self.assertEqual(log.id, 1)

    def test_log_list_response_valid(self):
        from server.schemas.log_schema import LogListResponse, LogResponse
        from server.enums.action_type import ActionType
        from datetime import datetime
        item = LogResponse(id=1, operator_id=1, operation=ActionType.CREATE,
                           module="customer", target_type="Customer",
                           description="test",
                           created_at=datetime(2026, 1, 1, 12, 0, 0))
        resp = LogListResponse(items=[item], total=1)
        self.assertEqual(resp.total, 1)
        self.assertEqual(len(resp.items), 1)

    def test_log_list_response_empty(self):
        from server.schemas.log_schema import LogListResponse
        resp = LogListResponse(items=[], total=0)
        self.assertEqual(resp.total, 0)
        self.assertEqual(len(resp.items), 0)

    def test_log_query_defaults(self):
        from server.schemas.log_schema import LogQuery
        q = LogQuery()
        self.assertEqual(q.page, 1)
        self.assertEqual(q.page_size, 20)
        self.assertEqual(q.sort_by, "created_at")
        self.assertEqual(q.sort_order, "desc")
        self.assertIsNone(q.operator_id)
        self.assertIsNone(q.operation)

    def test_log_query_page_zero(self):
        from server.schemas.log_schema import LogQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogQuery(page=0)

    def test_log_query_page_size_zero(self):
        from server.schemas.log_schema import LogQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogQuery(page_size=0)

    def test_log_query_page_size_201(self):
        from server.schemas.log_schema import LogQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogQuery(page_size=201)

    def test_log_query_sort_order_invalid(self):
        from server.schemas.log_schema import LogQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LogQuery(sort_order="invalid")

    def test_log_query_sort_order_asc(self):
        from server.schemas.log_schema import LogQuery
        q = LogQuery(sort_order="asc")
        self.assertEqual(q.sort_order, "asc")

    def test_log_query_sort_order_desc(self):
        from server.schemas.log_schema import LogQuery
        q = LogQuery(sort_order="desc")
        self.assertEqual(q.sort_order, "desc")

    def test_log_query_operation_enum(self):
        from server.schemas.log_schema import LogQuery
        from server.enums.action_type import ActionType
        q = LogQuery(operation=ActionType.CREATE)
        self.assertEqual(q.operation, ActionType.CREATE)

    def test_log_query_time_range(self):
        from server.schemas.log_schema import LogQuery
        from datetime import datetime
        q = LogQuery(start_time=datetime(2026, 1, 1),
                     end_time=datetime(2026, 12, 31))
        self.assertEqual(q.start_time, datetime(2026, 1, 1))
        self.assertEqual(q.end_time, datetime(2026, 12, 31))

    def test_log_base_model_dump(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        log = LogBase(operator_id=1, operation=ActionType.CREATE,
                      module="customer", target_type="Customer",
                      target_id=5, description="create",
                      created_at=datetime(2026, 1, 1, 12, 0, 0))
        d = log.model_dump()
        self.assertEqual(d["operator_id"], 1)
        self.assertEqual(d["operation"], "create")
        self.assertEqual(d["module"], "customer")
        self.assertEqual(d["target_type"], "Customer")
        self.assertEqual(d["target_id"], 5)

    def test_log_query_model_dump_exclude_none(self):
        from server.schemas.log_schema import LogQuery
        q = LogQuery(page=1, page_size=10, sort_by="created_at",
                     sort_order="desc")
        d = q.model_dump(exclude_none=True)
        self.assertNotIn("operator_id", d)
        self.assertNotIn("operation", d)
        self.assertNotIn("module", d)
        self.assertNotIn("keyword", d)

    def test_log_base_json(self):
        from server.schemas.log_schema import LogBase
        from server.enums.action_type import ActionType
        from datetime import datetime
        import json
        log = LogBase(operator_id=1, operation=ActionType.CREATE,
                      module="customer", target_type="Customer",
                      description="create",
                      created_at=datetime(2026, 1, 1, 12, 0, 0))
        d = json.loads(log.model_dump_json())
        self.assertEqual(d["operator_id"], 1)
        self.assertEqual(d["operation"], "create")

    def test_type_hints(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn(": int", source)
        self.assertIn(": str", source)
        self.assertIn(": datetime", source)
        self.assertIn(": ActionType", source)
        self.assertIn(": Optional[int]", source)

    def test_docstrings(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn("操作日志基础字段", source)
        self.assertIn("操作日志响应", source)
        self.assertIn("操作日志列表响应", source)
        self.assertIn("操作日志查询参数", source)

    def test_pep8(self):
        result = subprocess.run(
            ["python", "-m", "flake8", "--select=E,W,F,N",
             self._source_path],
            capture_output=True, text=True,
        )
        if result.returncode != 0 and result.stdout:
            self.fail(f"PEP8: {result.stdout.strip()}")

    def test_zero_workflow(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("TrialTaskProcessStatus", source)
        self.assertNotIn("process_status", source)

    def test_zero_status_machine(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("TrialTaskResultStatus", source)
        self.assertNotIn("result_status", source)

    def test_no_circular_import(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("from server.schemas.log_schema import", source)

    def test_frozen_api(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("Session", source)
        self.assertNotIn("commit", source)
        self.assertNotIn("rollback", source)
        self.assertNotIn("router", source.lower())
        self.assertNotIn("api_client", source.lower())

    def test_init_export(self):
        init_path = os.path.join(
            os.path.dirname(self._source_path), "__init__.py")
        with open(init_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn("LogBase", source)
        self.assertIn("LogResponse", source)
        self.assertIn("LogListResponse", source)
        self.assertIn("LogQuery", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
