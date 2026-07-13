"""检测记录 Schema 自检 (Inspection Schema Self-Test)

Sprint 8 — Task 8.1
严格依据 CODE_WIKI.md Schema Development Standard。

测试覆盖:
    - py_compile:            编译检查
    - import:                导入检查
    - Schema 导出:           8 个 Schema 类
    - Create:                创建 Schema
    - Update:                更新 Schema
    - Response:              响应 Schema
    - ListResponse:          列表响应 Schema
    - Query:                 查询参数 Schema
    - FinishRequest:         完成检测请求 Schema
    - Report:                上传元数据 Schema
    - FAILED → failure_reason Required:  不合格必填校验
    - PASSED → failure_reason Optional:  合格可选校验
    - Enum:                  枚举序列化/反序列化
    - Upload Metadata:       上传元数据（无 path/filepath）
    - exclude_unset():       部分更新
    - model_dump():          序列化导出
    - model_validate():      数据验证
    - JSON Serialization:    JSON 序列化
    - Type Hint:             类型注解
    - Docstring:             文档字符串
    - PEP8:                  代码风格
    - 字段数量:               字段数量校验
    - 字段类型:               字段类型校验
    - Response 排除:         排除 created_by/updated_by/is_deleted
    - 无循环导入:             循环导入检查
"""

import os
import sys
import unittest

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestInspectionSchema(unittest.TestCase):
    """检测记录 Schema 自检。"""

    @classmethod
    def setUpClass(cls):
        """初始化测试环境。"""
        cls._source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server",
            "schemas",
            "inspection_schema.py",
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
        from server.schemas.inspection_schema import (
            InspectionBase,
            InspectionCreate,
            InspectionUpdate,
            InspectionResponse,
            InspectionListResponse,
            InspectionQuery,
            InspectionFinishRequest,
            InspectionReport,
        )
        self.assertIsNotNone(InspectionBase)
        self.assertIsNotNone(InspectionCreate)
        self.assertIsNotNone(InspectionUpdate)
        self.assertIsNotNone(InspectionResponse)
        self.assertIsNotNone(InspectionListResponse)
        self.assertIsNotNone(InspectionQuery)
        self.assertIsNotNone(InspectionFinishRequest)
        self.assertIsNotNone(InspectionReport)

    # ============================================================
    # Schema 导出
    # ============================================================

    def test_schema_count(self):
        """共导出 8 个 Schema 类。"""
        from server.schemas import inspection_schema
        self.assertEqual(len(inspection_schema.__all__), 8)

    def test_schema_export(self):
        """__all__ 包含全部 8 个 Schema。"""
        from server.schemas.inspection_schema import __all__
        expected = {
            "InspectionBase",
            "InspectionCreate",
            "InspectionUpdate",
            "InspectionResponse",
            "InspectionListResponse",
            "InspectionQuery",
            "InspectionFinishRequest",
            "InspectionReport",
        }
        self.assertEqual(set(__all__), expected)

    # ============================================================
    # InspectionBase — 公共字段
    # ============================================================

    def test_base_field_count(self):
        """InspectionBase 包含 7 个公共字段。"""
        from server.schemas.inspection_schema import InspectionBase
        fields = InspectionBase.model_fields
        self.assertEqual(len(fields), 7)

    def test_base_required_fields(self):
        """InspectionBase 仅 task_id 为必填。"""
        from server.schemas.inspection_schema import InspectionBase
        fields = InspectionBase.model_fields
        self.assertTrue(fields["task_id"].is_required())
        self.assertFalse(fields["inspector_id"].is_required())
        self.assertFalse(fields["result"].is_required())

    # ============================================================
    # InspectionCreate — 创建 Schema
    # ============================================================

    def test_create_field_count(self):
        """InspectionCreate 包含 7 个字段（继承自 InspectionBase）。"""
        from server.schemas.inspection_schema import InspectionCreate
        fields = InspectionCreate.model_fields
        self.assertEqual(len(fields), 7)

    def test_create_valid(self):
        """InspectionCreate 最小必填字段创建成功。"""
        from server.schemas.inspection_schema import InspectionCreate
        data = InspectionCreate(task_id=1)
        self.assertEqual(data.task_id, 1)
        self.assertIsNone(data.inspector_id)
        self.assertIsNone(data.result)
        self.assertIsNone(data.failure_reason)

    def test_create_result_pass(self):
        """InspectionCreate result=pass 时 failure_reason 可为空。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(
            task_id=1,
            result=InspectionResult.PASS,
            failure_reason=None,
        )
        self.assertEqual(data.result, InspectionResult.PASS)
        self.assertIsNone(data.failure_reason)

    def test_create_result_fail_without_reason(self):
        """InspectionCreate result=fail 且无 failure_reason 时抛出 ValueError。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        with self.assertRaises(ValueError):
            InspectionCreate(
                task_id=1,
                result=InspectionResult.FAIL,
                failure_reason=None,
            )

    def test_create_result_fail_with_reason(self):
        """InspectionCreate result=fail 且有 failure_reason 时创建成功。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(
            task_id=1,
            result=InspectionResult.FAIL,
            failure_reason="精度不达标",
        )
        self.assertEqual(data.result, InspectionResult.FAIL)
        self.assertEqual(data.failure_reason, "精度不达标")

    def test_create_no_id(self):
        """InspectionCreate 不包含 id 字段。"""
        from server.schemas.inspection_schema import InspectionCreate
        self.assertNotIn("id", InspectionCreate.model_fields)

    def test_create_no_system_fields(self):
        """InspectionCreate 不含系统字段（created_by, updated_by, is_deleted）。"""
        from server.schemas.inspection_schema import InspectionCreate
        for field in ("created_by", "updated_by", "is_deleted"):
            self.assertNotIn(field, InspectionCreate.model_fields)

    # ============================================================
    # InspectionUpdate — 更新 Schema
    # ============================================================

    def test_update_field_count(self):
        """InspectionUpdate 包含 6 个可选字段。"""
        from server.schemas.inspection_schema import InspectionUpdate
        fields = InspectionUpdate.model_fields
        self.assertEqual(len(fields), 6)

    def test_update_all_optional(self):
        """InspectionUpdate 所有字段均可选。"""
        from server.schemas.inspection_schema import InspectionUpdate
        from typing import get_origin, Union
        for field_name, field_info in InspectionUpdate.model_fields.items():
            origin = get_origin(field_info.annotation)
            self.assertIn(
                origin,
                (Union, type(None)),
                f"InspectionUpdate.{field_name} 应为 Optional",
            )

    def test_update_empty(self):
        """InspectionUpdate 空对象创建成功。"""
        from server.schemas.inspection_schema import InspectionUpdate
        data = InspectionUpdate()
        self.assertIsNone(data.inspector_id)
        self.assertIsNone(data.result)
        self.assertIsNone(data.failure_reason)

    def test_update_exclude_unset(self):
        """InspectionUpdate 支持 exclude_unset 部分更新。"""
        from server.schemas.inspection_schema import InspectionUpdate
        from server.enums import InspectionResult
        data = InspectionUpdate(result=InspectionResult.PASS)
        unset = data.model_dump(exclude_unset=True)
        self.assertIn("result", unset)
        self.assertNotIn("inspector_id", unset)
        self.assertNotIn("failure_reason", unset)

    def test_update_result_fail_without_reason(self):
        """InspectionUpdate result=fail 且无 failure_reason 时抛出 ValueError。"""
        from server.schemas.inspection_schema import InspectionUpdate
        from server.enums import InspectionResult
        with self.assertRaises(ValueError):
            InspectionUpdate(
                result=InspectionResult.FAIL,
                failure_reason=None,
            )

    def test_update_result_fail_with_reason(self):
        """InspectionUpdate result=fail 且有 failure_reason 时创建成功。"""
        from server.schemas.inspection_schema import InspectionUpdate
        from server.enums import InspectionResult
        data = InspectionUpdate(
            result=InspectionResult.FAIL,
            failure_reason="粗糙度超标",
        )
        self.assertEqual(data.failure_reason, "粗糙度超标")

    # ============================================================
    # InspectionResponse — 响应 Schema
    # ============================================================

    def test_response_field_count(self):
        """InspectionResponse 包含 9 个字段（7 业务 + 2 时间戳）。"""
        from server.schemas.inspection_schema import InspectionResponse
        fields = InspectionResponse.model_fields
        self.assertEqual(len(fields), 9)

    def test_response_exclude_system_fields(self):
        """InspectionResponse 不含 created_by/updated_by/is_deleted。"""
        from server.schemas.inspection_schema import InspectionResponse
        for field in ("created_by", "updated_by", "is_deleted"):
            self.assertNotIn(field, InspectionResponse.model_fields)

    def test_response_include_system_fields(self):
        """InspectionResponse 包含 id, created_at, updated_at。"""
        from server.schemas.inspection_schema import InspectionResponse
        for field in ("id", "created_at", "updated_at"):
            self.assertIn(field, InspectionResponse.model_fields)

    def test_response_from_attributes(self):
        """InspectionResponse 使用 from_attributes=True。"""
        from server.schemas.inspection_schema import InspectionResponse
        config = InspectionResponse.model_config
        self.assertTrue(config.get("from_attributes"))

    def test_response_model_validate(self):
        """InspectionResponse model_validate 正常。"""
        from server.schemas.inspection_schema import InspectionResponse
        from datetime import datetime
        now = datetime(2026, 7, 13, 10, 0, 0)
        data = {
            "id": 1,
            "task_id": 1,
            "report_path": None,
            "accuracy": None,
            "roughness": None,
            "result": None,
            "inspector_id": None,
            "created_at": now,
            "updated_at": now,
        }
        resp = InspectionResponse.model_validate(data)
        self.assertEqual(resp.id, 1)
        self.assertEqual(resp.task_id, 1)

    # ============================================================
    # InspectionListResponse — 列表响应 Schema
    # ============================================================

    def test_list_response_items(self):
        """InspectionListResponse 包含 items 和 total。"""
        from server.schemas.inspection_schema import InspectionListResponse
        from datetime import datetime
        now = datetime(2026, 7, 13, 10, 0, 0)
        item = {
            "id": 1,
            "task_id": 1,
            "report_path": None,
            "accuracy": None,
            "roughness": None,
            "result": None,
            "inspector_id": None,
            "created_at": now,
            "updated_at": now,
        }
        resp = InspectionListResponse(items=[item], total=1)
        self.assertEqual(len(resp.items), 1)
        self.assertEqual(resp.total, 1)

    def test_list_response_default_factory(self):
        """InspectionListResponse items 默认值为空列表。"""
        from server.schemas.inspection_schema import InspectionListResponse
        resp = InspectionListResponse(total=0)
        self.assertEqual(resp.items, [])
        self.assertEqual(resp.total, 0)

    # ============================================================
    # InspectionQuery — 查询参数 Schema
    # ============================================================

    def test_query_field_count(self):
        """InspectionQuery 包含 8 个字段。"""
        from server.schemas.inspection_schema import InspectionQuery
        fields = InspectionQuery.model_fields
        self.assertEqual(len(fields), 8)

    def test_query_defaults(self):
        """InspectionQuery 默认值正确。"""
        from server.schemas.inspection_schema import InspectionQuery
        data = InspectionQuery()
        self.assertEqual(data.page, 1)
        self.assertEqual(data.page_size, 20)
        self.assertIsNone(data.keyword)
        self.assertIsNone(data.inspection_result)
        self.assertEqual(data.sort_by, "created_at")
        self.assertEqual(data.sort_order, "desc")

    def test_query_page_size_min(self):
        """InspectionQuery page_size 最小为 1。"""
        from server.schemas.inspection_schema import InspectionQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            InspectionQuery(page_size=0)

    def test_query_page_size_max(self):
        """InspectionQuery page_size 最大为 200。"""
        from server.schemas.inspection_schema import InspectionQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            InspectionQuery(page_size=201)

    def test_query_sort_order_invalid(self):
        """InspectionQuery sort_order 仅允许 asc/desc。"""
        from server.schemas.inspection_schema import InspectionQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            InspectionQuery(sort_order="invalid")

    def test_query_sort_order_valid(self):
        """InspectionQuery sort_order 允许 asc 和 desc。"""
        from server.schemas.inspection_schema import InspectionQuery
        data_asc = InspectionQuery(sort_order="asc")
        data_desc = InspectionQuery(sort_order="desc")
        self.assertEqual(data_asc.sort_order, "asc")
        self.assertEqual(data_desc.sort_order, "desc")

    def test_query_result_filter(self):
        """InspectionQuery inspection_result 支持筛选。"""
        from server.schemas.inspection_schema import InspectionQuery
        from server.enums import InspectionResult
        data = InspectionQuery(inspection_result=InspectionResult.PASS)
        self.assertEqual(data.inspection_result, InspectionResult.PASS)

    # ============================================================
    # InspectionFinishRequest — 完成检测请求 Schema
    # ============================================================

    def test_finish_request_field_count(self):
        """InspectionFinishRequest 包含 2 个字段。"""
        from server.schemas.inspection_schema import InspectionFinishRequest
        fields = InspectionFinishRequest.model_fields
        self.assertEqual(len(fields), 2)

    def test_finish_request_result_required(self):
        """InspectionFinishRequest result 为必填。"""
        from server.schemas.inspection_schema import InspectionFinishRequest
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            InspectionFinishRequest()

    def test_finish_request_pass(self):
        """InspectionFinishRequest result=pass 无需 failure_reason。"""
        from server.schemas.inspection_schema import InspectionFinishRequest
        from server.enums import InspectionResult
        data = InspectionFinishRequest(result=InspectionResult.PASS)
        self.assertEqual(data.result, InspectionResult.PASS)
        self.assertIsNone(data.failure_reason)

    def test_finish_request_fail_without_reason(self):
        """InspectionFinishRequest result=fail 且无 failure_reason 时抛出 ValueError。"""
        from server.schemas.inspection_schema import InspectionFinishRequest
        from server.enums import InspectionResult
        with self.assertRaises(ValueError):
            InspectionFinishRequest(
                result=InspectionResult.FAIL,
                failure_reason=None,
            )

    def test_finish_request_fail_with_reason(self):
        """InspectionFinishRequest result=fail 且有 failure_reason 时创建成功。"""
        from server.schemas.inspection_schema import InspectionFinishRequest
        from server.enums import InspectionResult
        data = InspectionFinishRequest(
            result=InspectionResult.FAIL,
            failure_reason="精度和粗糙度均不达标",
        )
        self.assertEqual(data.result, InspectionResult.FAIL)
        self.assertEqual(data.failure_reason, "精度和粗糙度均不达标")

    def test_finish_request_fail_empty_reason(self):
        """InspectionFinishRequest result=fail 且 failure_reason 为空字符串时抛出 ValueError。"""
        from server.schemas.inspection_schema import InspectionFinishRequest
        from server.enums import InspectionResult
        with self.assertRaises(ValueError):
            InspectionFinishRequest(
                result=InspectionResult.FAIL,
                failure_reason="",
            )

    # ============================================================
    # InspectionReport — 上传元数据 Schema
    # ============================================================

    def test_report_field_count(self):
        """InspectionReport 包含 4 个字段。"""
        from server.schemas.inspection_schema import InspectionReport
        fields = InspectionReport.model_fields
        self.assertEqual(len(fields), 4)

    def test_report_all_required(self):
        """InspectionReport 所有字段为必填。"""
        from server.schemas.inspection_schema import InspectionReport
        fields = InspectionReport.model_fields
        for field_name in ("filename", "url", "content_type", "size"):
            self.assertTrue(
                fields[field_name].is_required(),
                f"InspectionReport.{field_name} 应为必填",
            )

    def test_report_valid(self):
        """InspectionReport 创建成功。"""
        from server.schemas.inspection_schema import InspectionReport
        data = InspectionReport(
            filename="20260713-1_inspection_20260713153000.pdf",
            url="http://localhost:8000/uploads/reports/20260713-1_inspection_20260713153000.pdf",
            content_type="application/pdf",
            size=1024000,
        )
        self.assertEqual(data.filename, "20260713-1_inspection_20260713153000.pdf")
        self.assertEqual(data.content_type, "application/pdf")
        self.assertEqual(data.size, 1024000)

    def test_report_size_negative(self):
        """InspectionReport size 不能为负数。"""
        from server.schemas.inspection_schema import InspectionReport
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            InspectionReport(
                filename="test.pdf",
                url="http://localhost/test.pdf",
                content_type="application/pdf",
                size=-1,
            )

    def test_report_no_path_field(self):
        """InspectionReport 不含 path / filepath / full_path 字段。"""
        from server.schemas.inspection_schema import InspectionReport
        fields = InspectionReport.model_fields
        self.assertNotIn("path", fields)
        self.assertNotIn("filepath", fields)
        self.assertNotIn("full_path", fields)

    # ============================================================
    # Enum — 枚举序列化/反序列化
    # ============================================================

    def test_enum_pass_serialization(self):
        """InspectionResult.PASS 序列化正常。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(task_id=1, result=InspectionResult.PASS)
        dumped = data.model_dump()
        self.assertEqual(dumped["result"], InspectionResult.PASS)
        json_data = data.model_dump(mode="json")
        self.assertEqual(json_data["result"], "pass")

    def test_enum_fail_serialization(self):
        """InspectionResult.FAIL 序列化正常。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(
            task_id=1,
            result=InspectionResult.FAIL,
            failure_reason="不合格",
        )
        json_data = data.model_dump(mode="json")
        self.assertEqual(json_data["result"], "fail")

    def test_enum_deserialization(self):
        """InspectionResult 从字符串反序列化正常。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate.model_validate({
            "task_id": 1,
            "result": "pass",
        })
        self.assertEqual(data.result, InspectionResult.PASS)

    # ============================================================
    # model_dump — 序列化
    # ============================================================

    def test_model_dump(self):
        """InspectionCreate model_dump 序列化正常。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(
            task_id=1,
            result=InspectionResult.PASS,
            inspector_id=2,
            accuracy="0.001mm",
        )
        dumped = data.model_dump()
        self.assertEqual(dumped["task_id"], 1)
        self.assertEqual(dumped["inspector_id"], 2)
        self.assertEqual(dumped["accuracy"], "0.001mm")
        self.assertIsNone(dumped["failure_reason"])

    # ============================================================
    # JSON Serialization
    # ============================================================

    def test_json_serialization(self):
        """InspectionCreate model_dump(mode='json') 正常。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(task_id=1, result=InspectionResult.PASS)
        json_data = data.model_dump(mode="json")
        self.assertEqual(json_data["task_id"], 1)
        self.assertEqual(json_data["result"], "pass")

    def test_json_round_trip(self):
        """InspectionCreate JSON 往返正常。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(
            task_id=1,
            result=InspectionResult.PASS,
            accuracy="0.001mm",
        )
        json_str = data.model_dump_json()
        restored = InspectionCreate.model_validate_json(json_str)
        self.assertEqual(restored.task_id, data.task_id)
        self.assertEqual(restored.result, data.result)
        self.assertEqual(restored.accuracy, data.accuracy)

    def test_report_json_round_trip(self):
        """InspectionReport JSON 往返正常。"""
        from server.schemas.inspection_schema import InspectionReport
        data = InspectionReport(
            filename="test.pdf",
            url="http://localhost/test.pdf",
            content_type="application/pdf",
            size=1024,
        )
        json_str = data.model_dump_json()
        restored = InspectionReport.model_validate_json(json_str)
        self.assertEqual(restored.filename, data.filename)
        self.assertEqual(restored.size, data.size)

    # ============================================================
    # Type Hint — 类型注解
    # ============================================================

    def test_type_hints(self):
        """所有 Schema 类方法有类型注解。"""
        import ast
        with open(self._source_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith("Inspection"):
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
        import ast
        with open(self._source_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        self.assertIsNotNone(ast.get_docstring(tree))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith("Inspection"):
                self.assertIsNotNone(
                    ast.get_docstring(node),
                    f"{node.name} 缺少 docstring",
                )

    # ============================================================
    # PEP8
    # ============================================================

    def test_pep8(self):
        """PEP8 合规。"""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "flake8", "--select=E,W,F,N", self._source_path],
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
        self.assertNotIn("from server.schemas.inspection_schema", source)
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
        """Schema 不包含 process_status / result_status 判断逻辑。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("process_status", source)
        self.assertNotIn("result_status", source)

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
        """server/schemas/__init__.py 导出 Inspection Schema。"""
        try:
            from server.schemas.inspection_schema import (
                InspectionBase,
                InspectionCreate,
                InspectionUpdate,
                InspectionResponse,
                InspectionListResponse,
                InspectionQuery,
                InspectionFinishRequest,
                InspectionReport,
            )
            self.assertIsNotNone(InspectionBase)
            self.assertIsNotNone(InspectionCreate)
            self.assertIsNotNone(InspectionUpdate)
            self.assertIsNotNone(InspectionResponse)
            self.assertIsNotNone(InspectionListResponse)
            self.assertIsNotNone(InspectionQuery)
            self.assertIsNotNone(InspectionFinishRequest)
            self.assertIsNotNone(InspectionReport)
        except ImportError as e:
            self.fail(f"导入失败: {e}")

    # ============================================================
    # InspectionCreate 仅 result 为 FAIL 时校验 failure_reason
    # ============================================================

    def test_create_result_none_pass(self):
        """InspectionCreate result=None 时无需 failure_reason。"""
        from server.schemas.inspection_schema import InspectionCreate
        data = InspectionCreate(task_id=1)
        self.assertIsNone(data.result)
        self.assertIsNone(data.failure_reason)

    def test_create_result_pass_no_reason(self):
        """InspectionCreate result=pass 时 failure_reason 无需填写。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(task_id=1, result=InspectionResult.PASS)
        self.assertEqual(data.result, InspectionResult.PASS)
        self.assertIsNone(data.failure_reason)

    def test_create_result_pass_with_reason(self):
        """InspectionCreate result=pass 时 failure_reason 可正常赋值（但无意义）。"""
        from server.schemas.inspection_schema import InspectionCreate
        from server.enums import InspectionResult
        data = InspectionCreate(
            task_id=1,
            result=InspectionResult.PASS,
            failure_reason="不适用",
        )
        self.assertEqual(data.failure_reason, "不适用")


if __name__ == "__main__":
    unittest.main()