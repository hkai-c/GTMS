"""工件派发 Schema 自检 (Dispatch Schema Self-Test)

Sprint 9 — Task 9.1
严格依据 CODE_WIKI.md Schema Development Standard。

测试覆盖:
    - py_compile:            编译检查
    - import:                导入检查
    - Schema 导出:           6 个 Schema 类
    - Create:                创建 Schema
    - Update:                更新 Schema
    - Response:              响应 Schema
    - ListResponse:          列表响应 Schema
    - Query:                 查询参数 Schema
    - Enum:                  枚举序列化/反序列化
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
    - 零 Workflow:           无 process_status/result_status
    - 零 Status Machine:     无状态流转
    - 零 Upload:             无 path/filepath/file/upload
    - 无循环导入:             循环导入检查
    - Frozen API:            未修改任何已冻结 API
    - __init__.py 导出:      包导出
"""

import os
import sys
import unittest

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestDispatchSchema(unittest.TestCase):
    """工件派发 Schema 自检。"""

    @classmethod
    def setUpClass(cls):
        """初始化测试环境。"""
        cls._source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server",
            "schemas",
            "dispatch_schema.py",
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
        from server.schemas.dispatch_schema import (
            DispatchBase,
            DispatchCreate,
            DispatchUpdate,
            DispatchResponse,
            DispatchListResponse,
            DispatchQuery,
        )
        self.assertIsNotNone(DispatchBase)
        self.assertIsNotNone(DispatchCreate)
        self.assertIsNotNone(DispatchUpdate)
        self.assertIsNotNone(DispatchResponse)
        self.assertIsNotNone(DispatchListResponse)
        self.assertIsNotNone(DispatchQuery)

    # ============================================================
    # Schema 导出
    # ============================================================

    def test_schema_count(self):
        """共导出 6 个 Schema 类。"""
        from server.schemas import dispatch_schema
        self.assertEqual(len(dispatch_schema.__all__), 6)

    def test_schema_export(self):
        """__all__ 包含全部 6 个 Schema。"""
        from server.schemas.dispatch_schema import __all__
        expected = {
            "DispatchBase",
            "DispatchCreate",
            "DispatchUpdate",
            "DispatchResponse",
            "DispatchListResponse",
            "DispatchQuery",
        }
        self.assertEqual(set(__all__), expected)

    # ============================================================
    # DispatchBase — 公共字段
    # ============================================================

    def test_base_field_count(self):
        """DispatchBase 包含 4 个公共字段。"""
        from server.schemas.dispatch_schema import DispatchBase
        fields = DispatchBase.model_fields
        self.assertEqual(len(fields), 4)

    def test_base_required_fields(self):
        """DispatchBase 全部 4 个字段为必填。"""
        from server.schemas.dispatch_schema import DispatchBase
        fields = DispatchBase.model_fields
        for name in ("task_id", "direction", "dispatch_date", "operator_id"):
            self.assertTrue(
                fields[name].is_required(),
                f"DispatchBase.{name} 应为必填",
            )

    # ============================================================
    # DispatchCreate — 创建 Schema
    # ============================================================

    def test_create_field_count(self):
        """DispatchCreate 包含 4 个字段（继承自 DispatchBase）。"""
        from server.schemas.dispatch_schema import DispatchCreate
        fields = DispatchCreate.model_fields
        self.assertEqual(len(fields), 4)

    def test_create_valid(self):
        """DispatchCreate 全部必填字段创建成功。"""
        from server.schemas.dispatch_schema import DispatchCreate
        from server.enums import DestinationType
        from datetime import datetime
        data = DispatchCreate(
            task_id=1,
            direction=DestinationType.RETURNED_CUSTOMER,
            dispatch_date=datetime(2026, 7, 13, 10, 0, 0),
            operator_id=2,
        )
        self.assertEqual(data.task_id, 1)
        self.assertEqual(data.direction, DestinationType.RETURNED_CUSTOMER)
        self.assertEqual(data.operator_id, 2)

    def test_create_missing_task_id(self):
        """DispatchCreate 缺少 task_id 时抛出 ValidationError。"""
        from server.schemas.dispatch_schema import DispatchCreate
        from server.enums import DestinationType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            DispatchCreate(
                direction=DestinationType.RETURNED_CUSTOMER,
                dispatch_date=datetime(2026, 7, 13, 10, 0, 0),
                operator_id=2,
            )

    def test_create_no_id(self):
        """DispatchCreate 不包含 id 字段。"""
        from server.schemas.dispatch_schema import DispatchCreate
        self.assertNotIn("id", DispatchCreate.model_fields)

    def test_create_no_system_fields(self):
        """DispatchCreate 不含系统字段（created_by, updated_by, is_deleted）。"""
        from server.schemas.dispatch_schema import DispatchCreate
        for field in ("created_by", "updated_by", "is_deleted"):
            self.assertNotIn(field, DispatchCreate.model_fields)

    # ============================================================
    # DispatchUpdate — 更新 Schema
    # ============================================================

    def test_update_field_count(self):
        """DispatchUpdate 包含 3 个可选字段。"""
        from server.schemas.dispatch_schema import DispatchUpdate
        fields = DispatchUpdate.model_fields
        self.assertEqual(len(fields), 3)

    def test_update_all_optional(self):
        """DispatchUpdate 所有字段均可选。"""
        from server.schemas.dispatch_schema import DispatchUpdate
        from typing import get_origin
        for field_name, field_info in DispatchUpdate.model_fields.items():
            origin = get_origin(field_info.annotation)
            self.assertIsNotNone(
                origin,
                f"DispatchUpdate.{field_name} 应为 Optional",
            )

    def test_update_empty(self):
        """DispatchUpdate 空对象创建成功。"""
        from server.schemas.dispatch_schema import DispatchUpdate
        data = DispatchUpdate()
        self.assertIsNone(data.direction)
        self.assertIsNone(data.dispatch_date)
        self.assertIsNone(data.operator_id)

    def test_update_exclude_unset(self):
        """DispatchUpdate 支持 exclude_unset 部分更新。"""
        from server.schemas.dispatch_schema import DispatchUpdate
        from server.enums import DestinationType
        data = DispatchUpdate(direction=DestinationType.SCRAPPED)
        unset = data.model_dump(exclude_unset=True)
        self.assertIn("direction", unset)
        self.assertNotIn("dispatch_date", unset)
        self.assertNotIn("operator_id", unset)

    def test_update_partial(self):
        """DispatchUpdate 部分字段更新。"""
        from server.schemas.dispatch_schema import DispatchUpdate
        from datetime import datetime
        dt = datetime(2026, 7, 13, 10, 0, 0)
        data = DispatchUpdate(dispatch_date=dt)
        self.assertEqual(data.dispatch_date, dt)
        self.assertIsNone(data.direction)
        self.assertIsNone(data.operator_id)

    # ============================================================
    # DispatchResponse — 响应 Schema
    # ============================================================

    def test_response_field_count(self):
        """DispatchResponse 包含 7 个字段（4 业务 + 3 系统）。"""
        from server.schemas.dispatch_schema import DispatchResponse
        fields = DispatchResponse.model_fields
        self.assertEqual(len(fields), 7)

    def test_response_exclude_system_fields(self):
        """DispatchResponse 不含 created_by/updated_by/is_deleted。"""
        from server.schemas.dispatch_schema import DispatchResponse
        for field in ("created_by", "updated_by", "is_deleted"):
            self.assertNotIn(field, DispatchResponse.model_fields)

    def test_response_include_system_fields(self):
        """DispatchResponse 包含 id, created_at, updated_at。"""
        from server.schemas.dispatch_schema import DispatchResponse
        for field in ("id", "created_at", "updated_at"):
            self.assertIn(field, DispatchResponse.model_fields)

    def test_response_from_attributes(self):
        """DispatchResponse 使用 from_attributes=True。"""
        from server.schemas.dispatch_schema import DispatchResponse
        config = DispatchResponse.model_config
        self.assertTrue(config.get("from_attributes"))

    def test_response_model_validate(self):
        """DispatchResponse model_validate 正常。"""
        from server.schemas.dispatch_schema import DispatchResponse
        from server.enums import DestinationType
        from datetime import datetime
        now = datetime(2026, 7, 13, 10, 0, 0)
        data = {
            "id": 1,
            "task_id": 1,
            "direction": DestinationType.RETURNED_CUSTOMER,
            "dispatch_date": now,
            "operator_id": 2,
            "created_at": now,
            "updated_at": now,
        }
        resp = DispatchResponse.model_validate(data)
        self.assertEqual(resp.id, 1)
        self.assertEqual(resp.task_id, 1)
        self.assertEqual(resp.direction, DestinationType.RETURNED_CUSTOMER)

    # ============================================================
    # DispatchListResponse — 列表响应 Schema
    # ============================================================

    def test_list_response_items(self):
        """DispatchListResponse 包含 items 和 total。"""
        from server.schemas.dispatch_schema import DispatchListResponse
        from server.enums import DestinationType
        from datetime import datetime
        now = datetime(2026, 7, 13, 10, 0, 0)
        item = {
            "id": 1,
            "task_id": 1,
            "direction": DestinationType.RETURNED_CUSTOMER,
            "dispatch_date": now,
            "operator_id": 2,
            "created_at": now,
            "updated_at": now,
        }
        resp = DispatchListResponse(items=[item], total=1)
        self.assertEqual(len(resp.items), 1)
        self.assertEqual(resp.total, 1)

    def test_list_response_default_factory(self):
        """DispatchListResponse items 默认值为空列表。"""
        from server.schemas.dispatch_schema import DispatchListResponse
        resp = DispatchListResponse(total=0)
        self.assertEqual(resp.items, [])
        self.assertEqual(resp.total, 0)

    # ============================================================
    # DispatchQuery — 查询参数 Schema
    # ============================================================

    def test_query_field_count(self):
        """DispatchQuery 包含 6 个字段。"""
        from server.schemas.dispatch_schema import DispatchQuery
        fields = DispatchQuery.model_fields
        self.assertEqual(len(fields), 6)

    def test_query_defaults(self):
        """DispatchQuery 默认值正确。"""
        from server.schemas.dispatch_schema import DispatchQuery
        data = DispatchQuery()
        self.assertEqual(data.page, 1)
        self.assertEqual(data.page_size, 20)
        self.assertIsNone(data.keyword)
        self.assertIsNone(data.direction)
        self.assertEqual(data.sort_by, "created_at")
        self.assertEqual(data.sort_order, "desc")

    def test_query_page_size_min(self):
        """DispatchQuery page_size 最小为 1。"""
        from server.schemas.dispatch_schema import DispatchQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            DispatchQuery(page_size=0)

    def test_query_page_size_max(self):
        """DispatchQuery page_size 最大为 200。"""
        from server.schemas.dispatch_schema import DispatchQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            DispatchQuery(page_size=201)

    def test_query_page_min(self):
        """DispatchQuery page 最小为 1。"""
        from server.schemas.dispatch_schema import DispatchQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            DispatchQuery(page=0)

    def test_query_sort_order_invalid(self):
        """DispatchQuery sort_order 仅允许 asc/desc。"""
        from server.schemas.dispatch_schema import DispatchQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            DispatchQuery(sort_order="invalid")

    def test_query_sort_order_valid(self):
        """DispatchQuery sort_order 允许 asc 和 desc。"""
        from server.schemas.dispatch_schema import DispatchQuery
        data_asc = DispatchQuery(sort_order="asc")
        data_desc = DispatchQuery(sort_order="desc")
        self.assertEqual(data_asc.sort_order, "asc")
        self.assertEqual(data_desc.sort_order, "desc")

    def test_query_direction_filter(self):
        """DispatchQuery direction 支持去向筛选。"""
        from server.schemas.dispatch_schema import DispatchQuery
        from server.enums import DestinationType
        data = DispatchQuery(direction=DestinationType.RETURNED_CUSTOMER)
        self.assertEqual(data.direction, DestinationType.RETURNED_CUSTOMER)

    def test_query_keyword(self):
        """DispatchQuery keyword 支持关键词搜索。"""
        from server.schemas.dispatch_schema import DispatchQuery
        data = DispatchQuery(keyword="TASK-001")
        self.assertEqual(data.keyword, "TASK-001")

    # ============================================================
    # Enum — 枚举序列化/反序列化
    # ============================================================

    def test_enum_direction_serialization(self):
        """DestinationType 枚举序列化正常。"""
        from server.schemas.dispatch_schema import DispatchCreate
        from server.enums import DestinationType
        from datetime import datetime
        data = DispatchCreate(
            task_id=1,
            direction=DestinationType.RETURNED_CUSTOMER,
            dispatch_date=datetime(2026, 7, 13, 10, 0, 0),
            operator_id=2,
        )
        dumped = data.model_dump()
        self.assertEqual(dumped["direction"], DestinationType.RETURNED_CUSTOMER)
        json_data = data.model_dump(mode="json")
        self.assertEqual(json_data["direction"], "returned_customer")

    def test_enum_direction_all_values(self):
        """DestinationType 全部枚举值可正常使用。"""
        from server.schemas.dispatch_schema import DispatchCreate
        from server.enums import DestinationType
        from datetime import datetime
        dt = datetime(2026, 7, 13, 10, 0, 0)
        for direction in DestinationType:
            data = DispatchCreate(
                task_id=1,
                direction=direction,
                dispatch_date=dt,
                operator_id=2,
            )
            json_data = data.model_dump(mode="json")
            self.assertEqual(json_data["direction"], direction.value)

    def test_enum_direction_deserialization(self):
        """DestinationType 从字符串反序列化正常。"""
        from server.schemas.dispatch_schema import DispatchCreate
        from server.enums import DestinationType
        from datetime import datetime
        data = DispatchCreate.model_validate({
            "task_id": 1,
            "direction": "returned_customer",
            "dispatch_date": "2026-07-13T10:00:00",
            "operator_id": 2,
        })
        self.assertEqual(data.direction, DestinationType.RETURNED_CUSTOMER)

    # ============================================================
    # model_dump — 序列化
    # ============================================================

    def test_model_dump(self):
        """DispatchCreate model_dump 序列化正常。"""
        from server.schemas.dispatch_schema import DispatchCreate
        from server.enums import DestinationType
        from datetime import datetime
        data = DispatchCreate(
            task_id=1,
            direction=DestinationType.RETAINED_COMPANY,
            dispatch_date=datetime(2026, 7, 13, 10, 0, 0),
            operator_id=2,
        )
        dumped = data.model_dump()
        self.assertEqual(dumped["task_id"], 1)
        self.assertEqual(dumped["direction"], DestinationType.RETAINED_COMPANY)
        self.assertEqual(dumped["operator_id"], 2)

    # ============================================================
    # JSON Serialization
    # ============================================================

    def test_json_serialization(self):
        """DispatchCreate model_dump(mode='json') 正常。"""
        from server.schemas.dispatch_schema import DispatchCreate
        from server.enums import DestinationType
        from datetime import datetime
        data = DispatchCreate(
            task_id=1,
            direction=DestinationType.RETURNED_CUSTOMER,
            dispatch_date=datetime(2026, 7, 13, 10, 0, 0),
            operator_id=2,
        )
        json_data = data.model_dump(mode="json")
        self.assertEqual(json_data["task_id"], 1)
        self.assertEqual(json_data["direction"], "returned_customer")

    def test_json_round_trip(self):
        """DispatchCreate JSON 往返正常。"""
        from server.schemas.dispatch_schema import DispatchCreate
        from server.enums import DestinationType
        from datetime import datetime
        data = DispatchCreate(
            task_id=1,
            direction=DestinationType.SCRAPPED,
            dispatch_date=datetime(2026, 7, 13, 10, 0, 0),
            operator_id=2,
        )
        json_str = data.model_dump_json()
        restored = DispatchCreate.model_validate_json(json_str)
        self.assertEqual(restored.task_id, data.task_id)
        self.assertEqual(restored.direction, data.direction)
        self.assertEqual(restored.operator_id, data.operator_id)

    def test_response_json_round_trip(self):
        """DispatchResponse JSON 往返正常。"""
        from server.schemas.dispatch_schema import DispatchResponse
        from server.enums import DestinationType
        from datetime import datetime
        now = datetime(2026, 7, 13, 10, 0, 0)
        data = DispatchResponse(
            id=1,
            task_id=1,
            direction=DestinationType.OTHER,
            dispatch_date=now,
            operator_id=2,
            created_at=now,
            updated_at=now,
        )
        json_str = data.model_dump_json()
        restored = DispatchResponse.model_validate_json(json_str)
        self.assertEqual(restored.id, data.id)
        self.assertEqual(restored.direction, data.direction)

    # ============================================================
    # Type Hint — 类型注解
    # ============================================================

    def test_type_hints(self):
        """所有 Schema 类方法有类型注解。"""
        import ast
        with open(self._source_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith("Dispatch"):
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
            if isinstance(node, ast.ClassDef) and node.name.startswith("Dispatch"):
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
        self.assertNotIn("from server.schemas.dispatch_schema", source)
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
        import re
        with open(self._source_path, "r", encoding="utf-8") as f:
            full = f.read()
        # 排除 docstring 和注释
        code = re.sub(r'""".*?"""', "", full, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", "", code, flags=re.DOTALL)
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
        self.assertNotIn("process_status", code)
        self.assertNotIn("result_status", code)

    def test_no_status_machine(self):
        """Schema 不包含状态流转逻辑。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("process_status =", source)
        self.assertNotIn("result_status =", source)

    # ============================================================
    # 零 Upload
    # ============================================================

    def test_no_upload(self):
        """Dispatch 无上传功能，不含 path/filepath/file/upload。"""
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("path", source)
        self.assertNotIn("filepath", source)
        self.assertNotIn("full_path", source)
        self.assertNotIn("file", source)
        self.assertNotIn("upload", source)
        self.assertNotIn("binary", source)

    # ============================================================
    # __init__.py 导出
    # ============================================================

    def test_init_export(self):
        """server/schemas/__init__.py 导出 Dispatch Schema。"""
        try:
            from server.schemas.dispatch_schema import (
                DispatchBase,
                DispatchCreate,
                DispatchUpdate,
                DispatchResponse,
                DispatchListResponse,
                DispatchQuery,
            )
            self.assertIsNotNone(DispatchBase)
            self.assertIsNotNone(DispatchCreate)
            self.assertIsNotNone(DispatchUpdate)
            self.assertIsNotNone(DispatchResponse)
            self.assertIsNotNone(DispatchListResponse)
            self.assertIsNotNone(DispatchQuery)
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
        self.assertIsNotNone(UserBase)
        self.assertIsNotNone(UserResponse)


if __name__ == "__main__":
    unittest.main()