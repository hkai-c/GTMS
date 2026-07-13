"""试磨记录 Schema 自检 (Grinding Schema Self-Test)

Sprint 7 — Task 7.1
严格依据 CODE_WIKI.md Schema Development Standard。

测试覆盖:
    - py_compile:        编译检查
    - import:            导入检查
    - Schema 导出:       5 个 Schema 类
    - Create:            创建 Schema
    - Update:            更新 Schema
    - Response:          响应 Schema
    - ListResponse:      列表响应 Schema
    - exclude_unset():   部分更新
    - model_dump():      序列化导出
    - model_validate():  数据验证
    - JSON Serialization: JSON 序列化
    - date/datetime:     日期时间字段
    - Type Hint:         类型注解
    - Docstring:         文档字符串
    - PEP8:              代码风格
    - 字段数量:           字段数量校验
    - 字段类型:           字段类型校验
    - Response 排除:     排除 created_by/updated_by/is_deleted
    - 无循环导入:         循环导入检查
"""

import os
import sys
import unittest

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestGrindingSchema(unittest.TestCase):
    """试磨记录 Schema 自检。"""

    @classmethod
    def setUpClass(cls):
        """初始化测试环境。"""
        cls._source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server",
            "schemas",
            "grinding_schema.py",
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
        from server.schemas.grinding_schema import (
            GrindingBase,
            GrindingCreate,
            GrindingUpdate,
            GrindingResponse,
            GrindingListResponse,
        )
        self.assertIsNotNone(GrindingBase)
        self.assertIsNotNone(GrindingCreate)
        self.assertIsNotNone(GrindingUpdate)
        self.assertIsNotNone(GrindingResponse)
        self.assertIsNotNone(GrindingListResponse)

    # ============================================================
    # Schema 导出
    # ============================================================

    def test_schema_count(self):
        """共导出 5 个 Schema 类。"""
        from server.schemas import grinding_schema
        self.assertEqual(len(grinding_schema.__all__), 5)

    def test_schema_export(self):
        """__all__ 包含全部 5 个 Schema。"""
        from server.schemas.grinding_schema import __all__
        expected = {
            "GrindingBase",
            "GrindingCreate",
            "GrindingUpdate",
            "GrindingResponse",
            "GrindingListResponse",
        }
        self.assertEqual(set(__all__), expected)

    # ============================================================
    # Create — 创建 Schema
    # ============================================================

    def test_create_field_count(self):
        """GrindingCreate 包含 9 个业务字段（3 必填 + 6 可选）。"""
        from server.schemas.grinding_schema import GrindingCreate
        fields = GrindingCreate.model_fields
        self.assertEqual(len(fields), 9)

    def test_create_field_types(self):
        """GrindingCreate 必填字段类型正确。"""
        from server.schemas.grinding_schema import GrindingCreate
        from datetime import datetime
        fields = GrindingCreate.model_fields
        self.assertTrue(issubclass(fields["task_id"].annotation, int))
        self.assertTrue(issubclass(fields["operator_id"].annotation, int))
        self.assertTrue(issubclass(fields["start_time"].annotation, datetime))

    def test_create_valid(self):
        """GrindingCreate 最小必填字段创建成功。"""
        from server.schemas.grinding_schema import GrindingCreate
        from datetime import datetime
        data = GrindingCreate(
            task_id=1,
            operator_id=2,
            start_time=datetime(2026, 7, 11, 10, 0, 0),
        )
        self.assertEqual(data.task_id, 1)
        self.assertEqual(data.operator_id, 2)
        self.assertIsNone(data.machine_type)
        self.assertIsNone(data.end_time)

    def test_create_minimal(self):
        """GrindingCreate 仅必填字段可创建。"""
        from server.schemas.grinding_schema import GrindingCreate
        from datetime import datetime
        data = GrindingCreate(
            task_id=1,
            operator_id=2,
            start_time=datetime(2026, 7, 11, 10, 0, 0),
        )
        dumped = data.model_dump()
        self.assertEqual(dumped["task_id"], 1)
        self.assertEqual(dumped["operator_id"], 2)

    def test_create_no_id(self):
        """GrindingCreate 不包含 id 字段。"""
        from server.schemas.grinding_schema import GrindingCreate
        self.assertNotIn("id", GrindingCreate.model_fields)

    def test_create_no_created_at(self):
        """GrindingCreate 不包含 created_at 字段。"""
        from server.schemas.grinding_schema import GrindingCreate
        self.assertNotIn("created_at", GrindingCreate.model_fields)

    def test_create_no_system_fields(self):
        """GrindingCreate 不含系统字段（created_by, updated_by, is_deleted）。"""
        from server.schemas.grinding_schema import GrindingCreate
        for field in ("created_by", "updated_by", "is_deleted"):
            self.assertNotIn(field, GrindingCreate.model_fields)

    # ============================================================
    # Update — 更新 Schema
    # ============================================================

    def test_update_field_count(self):
        """GrindingUpdate 包含 6 个可选字段。"""
        from server.schemas.grinding_schema import GrindingUpdate
        fields = GrindingUpdate.model_fields
        self.assertEqual(len(fields), 6)

    def test_update_all_optional(self):
        """GrindingUpdate 所有字段均为 Optional。"""
        from server.schemas.grinding_schema import GrindingUpdate
        from typing import get_origin, Union
        for field_name, field_info in GrindingUpdate.model_fields.items():
            origin = get_origin(field_info.annotation)
            self.assertIn(
                origin,
                (Union, type(None)),
                f"GrindingUpdate.{field_name} 应为 Optional",
            )

    def test_update_empty(self):
        """GrindingUpdate 空对象创建成功。"""
        from server.schemas.grinding_schema import GrindingUpdate
        data = GrindingUpdate()
        self.assertIsNone(data.machine_type)
        self.assertIsNone(data.end_time)
        self.assertIsNone(data.fail_reason)

    def test_update_exclude_unset(self):
        """GrindingUpdate 支持 exclude_unset 部分更新。"""
        from server.schemas.grinding_schema import GrindingUpdate
        from datetime import datetime
        data = GrindingUpdate(end_time=datetime(2026, 7, 11, 12, 0, 0))
        unset = data.model_dump(exclude_unset=True)
        self.assertIn("end_time", unset)
        self.assertNotIn("machine_type", unset)
        self.assertNotIn("fail_reason", unset)

    # ============================================================
    # Response — 响应 Schema
    # ============================================================

    def test_response_field_count(self):
        """GrindingResponse 包含 12 个字段（10 业务 + 2 时间戳）。"""
        from server.schemas.grinding_schema import GrindingResponse
        fields = GrindingResponse.model_fields
        self.assertEqual(len(fields), 12)

    def test_response_exclude_system_fields(self):
        """GrindingResponse 不含 created_by/updated_by/is_deleted。"""
        from server.schemas.grinding_schema import GrindingResponse
        for field in ("created_by", "updated_by", "is_deleted"):
            self.assertNotIn(field, GrindingResponse.model_fields)

    def test_response_include_system_fields(self):
        """GrindingResponse 包含 id, created_at, updated_at。"""
        from server.schemas.grinding_schema import GrindingResponse
        for field in ("id", "created_at", "updated_at"):
            self.assertIn(field, GrindingResponse.model_fields)

    def test_response_from_attributes(self):
        """GrindingResponse 使用 from_attributes=True。"""
        from server.schemas.grinding_schema import GrindingResponse
        config = GrindingResponse.model_config
        self.assertTrue(config.get("from_attributes"))

    def test_response_model_validate(self):
        """GrindingResponse model_validate 正常。"""
        from server.schemas.grinding_schema import GrindingResponse
        from datetime import datetime
        now = datetime(2026, 7, 11, 10, 0, 0)
        data = {
            "id": 1,
            "task_id": 1,
            "operator_id": 2,
            "start_time": now,
            "machine_type": None,
            "wheel_type": None,
            "params": None,
            "end_time": None,
            "image_paths": None,
            "fail_reason": None,
            "created_at": now,
            "updated_at": now,
        }
        resp = GrindingResponse.model_validate(data)
        self.assertEqual(resp.id, 1)
        self.assertEqual(resp.task_id, 1)

    # ============================================================
    # ListResponse — 列表响应 Schema
    # ============================================================

    def test_list_response_items(self):
        """GrindingListResponse 包含 items 和 total。"""
        from server.schemas.grinding_schema import GrindingListResponse
        from datetime import datetime
        now = datetime(2026, 7, 11, 10, 0, 0)
        item = {
            "id": 1,
            "task_id": 1,
            "operator_id": 2,
            "start_time": now,
            "machine_type": None,
            "wheel_type": None,
            "params": None,
            "end_time": None,
            "image_paths": None,
            "fail_reason": None,
            "created_at": now,
            "updated_at": now,
        }
        resp = GrindingListResponse(items=[item], total=1)
        self.assertEqual(len(resp.items), 1)
        self.assertEqual(resp.total, 1)

    def test_list_response_default_factory(self):
        """GrindingListResponse items 默认值为空列表。"""
        from server.schemas.grinding_schema import GrindingListResponse
        resp = GrindingListResponse(total=0)
        self.assertEqual(resp.items, [])
        self.assertEqual(resp.total, 0)

    # ============================================================
    # model_dump — 序列化
    # ============================================================

    def test_model_dump(self):
        """GrindingCreate model_dump 序列化正常。"""
        from server.schemas.grinding_schema import GrindingCreate
        from datetime import datetime
        data = GrindingCreate(
            task_id=1,
            operator_id=2,
            start_time=datetime(2026, 7, 11, 10, 0, 0),
        )
        dumped = data.model_dump()
        self.assertEqual(dumped["task_id"], 1)
        self.assertEqual(dumped["operator_id"], 2)
        self.assertIsNone(dumped["machine_type"])
        self.assertIsNone(dumped["fail_reason"])

    # ============================================================
    # JSON Serialization
    # ============================================================

    def test_json_serialization(self):
        """GrindingCreate model_dump(mode='json') 正常。"""
        from server.schemas.grinding_schema import GrindingCreate
        from datetime import datetime
        data = GrindingCreate(
            task_id=1,
            operator_id=2,
            start_time=datetime(2026, 7, 11, 10, 0, 0),
        )
        json_data = data.model_dump(mode="json")
        self.assertEqual(json_data["task_id"], 1)
        self.assertIsInstance(json_data["start_time"], str)

    def test_json_round_trip(self):
        """GrindingCreate JSON 往返正常。"""
        from server.schemas.grinding_schema import GrindingCreate
        from datetime import datetime
        data = GrindingCreate(
            task_id=1,
            operator_id=2,
            start_time=datetime(2026, 7, 11, 10, 0, 0),
        )
        json_str = data.model_dump_json()
        restored = GrindingCreate.model_validate_json(json_str)
        self.assertEqual(restored.task_id, data.task_id)
        self.assertEqual(restored.operator_id, data.operator_id)

    # ============================================================
    # datetime — 日期时间字段
    # ============================================================

    def test_datetime_field(self):
        """datetime 字段正确处理。"""
        from server.schemas.grinding_schema import GrindingCreate
        from datetime import datetime
        dt = datetime(2026, 7, 11, 10, 0, 0)
        data = GrindingCreate(task_id=1, operator_id=2, start_time=dt)
        self.assertEqual(data.start_time, dt)

    # ============================================================
    # Type Hint — 类型注解
    # ============================================================

    def test_type_hints(self):
        """所有 Schema 类方法有类型注解。"""
        import ast
        with open(self._source_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith("Grinding"):
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
            if isinstance(node, ast.ClassDef) and node.name.startswith("Grinding"):
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
        # 检查是否导入了自身或同层模块
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("from server.schemas.grinding_schema", source)
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
    # __init__.py 导出
    # ============================================================

    def test_init_export(self):
        """server/schemas/__init__.py 导出 Grinding Schema。"""
        try:
            from server.schemas.grinding_schema import (
                GrindingBase,
                GrindingCreate,
                GrindingUpdate,
                GrindingResponse,
                GrindingListResponse,
            )
            self.assertIsNotNone(GrindingBase)
            self.assertIsNotNone(GrindingCreate)
            self.assertIsNotNone(GrindingUpdate)
            self.assertIsNotNone(GrindingResponse)
            self.assertIsNotNone(GrindingListResponse)
        except ImportError as e:
            self.fail(f"导入失败: {e}")


if __name__ == "__main__":
    unittest.main()