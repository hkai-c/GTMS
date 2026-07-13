"""收件记录 Schema 自检 (Receipt Schema Self-Test)

Sprint 6 — Task 6.1
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


class TestReceiptSchema(unittest.TestCase):
    """收件记录 Schema 自检。"""

    @classmethod
    def setUpClass(cls):
        """初始化测试环境。"""
        cls._source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server",
            "schemas",
            "receipt_schema.py",
        )

    # ============================================================
    # py_compile — 编译检查
    # ============================================================

    def test_py_compile(self):
        """py_compile: 确保文件可正常编译。"""
        import py_compile

        result = py_compile.compile(self._source_path, doraise=True)
        self.assertIsNotNone(result)

    # ============================================================
    # import — 导入检查
    # ============================================================

    def test_import(self):
        """import: 确保模块可正常导入。"""
        try:
            from server.schemas.receipt_schema import (  # noqa: F401
                ReceiptBase,
                ReceiptCreate,
                ReceiptUpdate,
                ReceiptResponse,
                ReceiptListResponse,
            )
        except Exception as e:
            self.fail(f"导入失败: {e}")

    # ============================================================
    # Schema 导出 — 5 个 Schema 类
    # ============================================================

    def test_schema_export(self):
        """Schema 导出: 确保 5 个 Schema 类均导出。"""
        from server.schemas.receipt_schema import __all__

        expected = [
            "ReceiptBase",
            "ReceiptCreate",
            "ReceiptUpdate",
            "ReceiptResponse",
            "ReceiptListResponse",
        ]
        for name in expected:
            self.assertIn(name, __all__, f"__all__ 缺少 {name}")

    def test_schema_count(self):
        """Schema 数量: 确保 __all__ 包含 5 个 Schema。"""
        from server.schemas.receipt_schema import __all__

        self.assertEqual(len(__all__), 5, f"期望 5 个 Schema，实际 {len(__all__)}")

    # ============================================================
    # Create — 创建 Schema
    # ============================================================

    def test_create_valid(self):
        """Create: 有效数据创建成功。"""
        from server.schemas.receipt_schema import ReceiptCreate
        from datetime import datetime, timezone

        data = {
            "task_id": 1,
            "received_at": datetime.now(timezone.utc),
            "receiver_id": 1,
            "image_paths": '["path/to/img1.jpg", "path/to/img2.jpg"]',
        }
        obj = ReceiptCreate(**data)
        self.assertEqual(obj.task_id, 1)
        self.assertEqual(obj.receiver_id, 1)
        self.assertEqual(obj.image_paths, '["path/to/img1.jpg", "path/to/img2.jpg"]')

    def test_create_minimal(self):
        """Create: 最小字段创建成功（image_paths 可选）。"""
        from server.schemas.receipt_schema import ReceiptCreate
        from datetime import datetime, timezone

        data = {
            "task_id": 1,
            "received_at": datetime.now(timezone.utc),
            "receiver_id": 1,
        }
        obj = ReceiptCreate(**data)
        self.assertIsNone(obj.image_paths)

    def test_create_no_id(self):
        """Create: 不包含 id 字段。"""
        from server.schemas.receipt_schema import ReceiptCreate

        fields = ReceiptCreate.model_fields
        self.assertNotIn("id", fields, "ReceiptCreate 不应包含 id 字段")

    def test_create_no_created_at(self):
        """Create: 不包含 created_at 字段。"""
        from server.schemas.receipt_schema import ReceiptCreate

        fields = ReceiptCreate.model_fields
        self.assertNotIn(
            "created_at", fields, "ReceiptCreate 不应包含 created_at 字段"
        )

    def test_create_no_system_fields(self):
        """Create: 不包含系统字段。"""
        from server.schemas.receipt_schema import ReceiptCreate

        fields = ReceiptCreate.model_fields
        for f in ["id", "created_at", "updated_at", "created_by", "updated_by",
                   "is_deleted"]:
            self.assertNotIn(
                f, fields, f"ReceiptCreate 不应包含 {f} 字段"
            )

    def test_create_field_count(self):
        """Create: 字段数量为 4。"""
        from server.schemas.receipt_schema import ReceiptCreate

        fields = ReceiptCreate.model_fields
        self.assertEqual(len(fields), 4, f"期望 4 个字段，实际 {len(fields)}")

    def test_create_field_types(self):
        """Create: 字段类型正确。"""
        from server.schemas.receipt_schema import ReceiptCreate
        from datetime import datetime
        from typing import Optional

        fields = ReceiptCreate.model_fields
        self.assertTrue(issubclass(fields["task_id"].annotation, int))
        self.assertTrue(issubclass(fields["received_at"].annotation, datetime))
        self.assertTrue(issubclass(fields["receiver_id"].annotation, int))
        # image_paths 是 Optional[str]
        self.assertEqual(fields["image_paths"].annotation, Optional[str])

    # ============================================================
    # Update — 更新 Schema
    # ============================================================

    def test_update_all_optional(self):
        """Update: 所有字段均为 Optional。"""
        from server.schemas.receipt_schema import ReceiptUpdate

        fields = ReceiptUpdate.model_fields
        for name, f in fields.items():
            self.assertFalse(
                f.is_required(),
                f"ReceiptUpdate.{name} 应为 Optional 字段",
            )

    def test_update_exclude_unset(self):
        """Update: exclude_unset=True 排除未设置字段。"""
        from server.schemas.receipt_schema import ReceiptUpdate

        obj = ReceiptUpdate(task_id=1)
        data = obj.model_dump(exclude_unset=True)
        self.assertIn("task_id", data)
        self.assertNotIn("received_at", data)
        self.assertNotIn("receiver_id", data)
        self.assertNotIn("image_paths", data)

    def test_update_empty(self):
        """Update: 空 Update 创建成功。"""
        from server.schemas.receipt_schema import ReceiptUpdate

        obj = ReceiptUpdate()
        data = obj.model_dump(exclude_unset=True)
        self.assertEqual(data, {})

    def test_update_field_count(self):
        """Update: 字段数量为 4。"""
        from server.schemas.receipt_schema import ReceiptUpdate

        fields = ReceiptUpdate.model_fields
        self.assertEqual(len(fields), 4, f"期望 4 个字段，实际 {len(fields)}")

    # ============================================================
    # Response — 响应 Schema
    # ============================================================

    def test_response_from_attributes(self):
        """Response: ConfigDict(from_attributes=True)。"""
        from server.schemas.receipt_schema import ReceiptResponse

        self.assertTrue(
            ReceiptResponse.model_config.get("from_attributes"),
            "ReceiptResponse 应设置 from_attributes=True",
        )

    def test_response_field_count(self):
        """Response: 字段数量为 7。"""
        from server.schemas.receipt_schema import ReceiptResponse

        fields = ReceiptResponse.model_fields
        self.assertEqual(
            len(fields), 7, f"期望 7 个字段（4 业务 + 3 系统），实际 {len(fields)}"
        )

    def test_response_exclude_system_fields(self):
        """Response: 排除 created_by/updated_by/is_deleted。"""
        from server.schemas.receipt_schema import ReceiptResponse

        fields = ReceiptResponse.model_fields
        for f in ["created_by", "updated_by", "is_deleted"]:
            self.assertNotIn(
                f, fields, f"ReceiptResponse 不应包含 {f} 字段"
            )

    def test_response_include_system_fields(self):
        """Response: 包含 id/created_at/updated_at。"""
        from server.schemas.receipt_schema import ReceiptResponse

        fields = ReceiptResponse.model_fields
        for f in ["id", "created_at", "updated_at"]:
            self.assertIn(
                f, fields, f"ReceiptResponse 应包含 {f} 字段"
            )

    def test_response_model_validate(self):
        """Response: model_validate() 数据验证。"""
        from server.schemas.receipt_schema import ReceiptResponse
        from datetime import datetime, timezone

        data = {
            "id": 1,
            "task_id": 1,
            "received_at": datetime.now(timezone.utc),
            "receiver_id": 1,
            "image_paths": '["path/to/img.jpg"]',
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        obj = ReceiptResponse.model_validate(data)
        self.assertEqual(obj.id, 1)
        self.assertEqual(obj.task_id, 1)

    # ============================================================
    # ListResponse — 列表响应 Schema
    # ============================================================

    def test_list_response_items(self):
        """ListResponse: items 字段类型为 list[ReceiptResponse]。"""
        from server.schemas.receipt_schema import ReceiptListResponse

        obj = ReceiptListResponse(items=[], total=0)
        self.assertEqual(obj.items, [])
        self.assertEqual(obj.total, 0)

    def test_list_response_default_factory(self):
        """ListResponse: items 默认值为空列表。"""
        from server.schemas.receipt_schema import ReceiptListResponse

        obj = ReceiptListResponse(total=0)
        self.assertEqual(obj.items, [])

    # ============================================================
    # model_dump() — 序列化导出
    # ============================================================

    def test_model_dump(self):
        """model_dump(): 序列化导出。"""
        from server.schemas.receipt_schema import ReceiptCreate
        from datetime import datetime, timezone

        obj = ReceiptCreate(
            task_id=1,
            received_at=datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc),
            receiver_id=1,
        )
        data = obj.model_dump()
        self.assertEqual(data["task_id"], 1)
        self.assertEqual(data["receiver_id"], 1)
        self.assertIsNone(data["image_paths"])

    # ============================================================
    # JSON Serialization — JSON 序列化
    # ============================================================

    def test_json_serialization(self):
        """JSON Serialization: 序列化并反序列化。"""
        from server.schemas.receipt_schema import ReceiptCreate
        from datetime import datetime, timezone

        obj = ReceiptCreate(
            task_id=1,
            received_at=datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc),
            receiver_id=1,
        )
        json_str = obj.model_dump_json()
        self.assertIsInstance(json_str, str)
        self.assertIn("task_id", json_str)
        self.assertIn("receiver_id", json_str)

    def test_json_round_trip(self):
        """JSON Round Trip: 序列化再反序列化一致。"""
        from server.schemas.receipt_schema import ReceiptCreate
        from datetime import datetime, timezone

        original = ReceiptCreate(
            task_id=1,
            received_at=datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc),
            receiver_id=1,
        )
        json_str = original.model_dump_json()
        restored = ReceiptCreate.model_validate_json(json_str)
        self.assertEqual(original.task_id, restored.task_id)
        self.assertEqual(original.receiver_id, restored.receiver_id)

    # ============================================================
    # date/datetime — 日期时间字段
    # ============================================================

    def test_datetime_field(self):
        """datetime: received_at 字段为 datetime 类型。"""
        from server.schemas.receipt_schema import ReceiptCreate
        from datetime import datetime

        fields = ReceiptCreate.model_fields
        self.assertTrue(
            issubclass(fields["received_at"].annotation, datetime),
            "received_at 应为 datetime 类型",
        )

    # ============================================================
    # Type Hint — 类型注解
    # ============================================================

    def test_type_hints(self):
        """Type Hint: 所有公共方法有类型注解。"""
        import ast

        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        schema_classes = {
            "ReceiptBase",
            "ReceiptCreate",
            "ReceiptUpdate",
            "ReceiptResponse",
            "ReceiptListResponse",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in schema_classes:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if not item.name.startswith("_"):
                            self.assertIsNotNone(
                                item.returns,
                                f"{node.name}.{item.name}() 缺少返回类型注解",
                            )

    # ============================================================
    # Docstring — 文档字符串
    # ============================================================

    def test_docstring(self):
        """Docstring: 所有 Schema 类有文档字符串。"""
        import ast

        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        schema_classes = {
            "ReceiptBase",
            "ReceiptCreate",
            "ReceiptUpdate",
            "ReceiptResponse",
            "ReceiptListResponse",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in schema_classes:
                docstring = ast.get_docstring(node)
                self.assertIsNotNone(
                    docstring,
                    f"{node.name} 缺少 Docstring",
                )

    # ============================================================
    # PEP8 — 代码风格
    # ============================================================

    def test_pep8(self):
        """PEP8: 代码风格合规。"""
        import pycodestyle

        style = pycodestyle.StyleGuide(quiet=True)
        report = style.check_files([self._source_path])
        self.assertEqual(
            report.total_errors,
            0,
            f"PEP8 违规 {report.total_errors} 处",
        )

    # ============================================================
    # 无循环导入
    # ============================================================

    def test_no_circular_import(self):
        """无循环导入: 确保无循环导入。"""
        import importlib

        try:
            importlib.reload(
                __import__("server.schemas.receipt_schema", fromlist=["_"])
            )
        except Exception as e:
            self.fail(f"循环导入: {e}")

    # ============================================================
    # __init__.py 导出
    # ============================================================

    def test_init_export(self):
        """__init__.py: 确保 Receipt Schema 在 __init__.py 中导出。"""
        from server.schemas import (
            ReceiptBase,
            ReceiptCreate,
            ReceiptUpdate,
            ReceiptResponse,
            ReceiptListResponse,
        )

        self.assertIsNotNone(ReceiptBase)
        self.assertIsNotNone(ReceiptCreate)
        self.assertIsNotNone(ReceiptUpdate)
        self.assertIsNotNone(ReceiptResponse)
        self.assertIsNotNone(ReceiptListResponse)

    # ============================================================
    # Frozen API — 不修改已有 Schema
    # ============================================================

    def test_frozen_api(self):
        """Frozen API: 确保不修改已有 Schema 文件。"""
        import importlib

        frozen_modules = [
            "server.schemas.user_schema",
            "server.schemas.role_schema",
            "server.schemas.customer_schema",
            "server.schemas.trial_task_schema",
        ]
        for mod in frozen_modules:
            try:
                importlib.reload(__import__(mod, fromlist=["_"]))
            except Exception as e:
                self.fail(f"Frozen API 受损: {mod} — {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)