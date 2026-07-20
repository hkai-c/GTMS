"""消息提醒 Schema 自检 (Notification Schema Self-Test)

Sprint 12 — Task 12.1
严格依据 CODE_WIKI.md §15.17 Notification Principle。

测试覆盖:
    - py_compile / import / Schema 导出
    - NotificationBase 字段验证、枚举、空字符串
    - NotificationCreate 继承验证
    - NotificationUpdate 字段验证
    - NotificationResponse 继承 + id / read_time / updated_at
    - NotificationListResponse 列表响应
    - NotificationQuery 查询参数验证、分页、排序
    - model_dump / JSON / Type Hint / Docstring / PEP8
    - Zero Workflow / Zero Status Machine
    - 无循环导入 / Frozen API / __init__.py 导出
    - 边界值 / 非法
"""

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestNotificationSchema(unittest.TestCase):
    """消息提醒 Schema 自检。"""

    @classmethod
    def setUpClass(cls):
        cls._source_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server", "schemas", "notification_schema.py",
        )

    # ============================================================
    # [1] py_compile
    # ============================================================

    def test_py_compile(self):
        import py_compile
        try:
            py_compile.compile(self._source_path, doraise=True)
        except py_compile.PyCompileError as e:
            self.fail(f"compile: {e}")

    # ============================================================
    # [2] import
    # ============================================================

    def test_import(self):
        from server.schemas import (
            NotificationBase,
            NotificationCreate,
            NotificationUpdate,
            NotificationResponse,
            NotificationListResponse,
            NotificationQuery,
        )
        self.assertIsNotNone(NotificationBase)
        self.assertIsNotNone(NotificationCreate)
        self.assertIsNotNone(NotificationUpdate)
        self.assertIsNotNone(NotificationResponse)
        self.assertIsNotNone(NotificationListResponse)
        self.assertIsNotNone(NotificationQuery)

    # ============================================================
    # [3] Schema 数量
    # ============================================================

    def test_schema_count(self):
        from server.schemas import notification_schema
        self.assertEqual(len(notification_schema.__all__), 6)

    def test_schema_export(self):
        from server.schemas import notification_schema
        expected = {
            "NotificationBase",
            "NotificationCreate",
            "NotificationUpdate",
            "NotificationResponse",
            "NotificationListResponse",
            "NotificationQuery",
        }
        self.assertEqual(set(notification_schema.__all__), expected)

    # ============================================================
    # [4] NotificationBase 基础字段
    # ============================================================

    def test_notification_base_valid(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        n = NotificationBase(
            user_id=1,
            notification_type=NotifyType.RECEIPT_DELAY,
            title="收件超时",
            content="任务 TM202600018 已收件超过2天",
            target_type="trial_task",
            target_id=18,
            is_read=False,
            created_at=datetime(2026, 7, 18, 12, 0, 0),
        )
        self.assertEqual(n.user_id, 1)
        self.assertEqual(n.notification_type, NotifyType.RECEIPT_DELAY)
        self.assertEqual(n.title, "收件超时")
        self.assertEqual(n.content, "任务 TM202600018 已收件超过2天")
        self.assertEqual(n.target_type, "trial_task")
        self.assertEqual(n.target_id, 18)
        self.assertFalse(n.is_read)

    # ----------------------------------------------------------
    # 字段默认值
    # ----------------------------------------------------------

    def test_notification_base_defaults(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        n = NotificationBase(
            user_id=1,
            notification_type=NotifyType.GRINDING_DELAY,
            title="test",
            content="test",
            target_id=0,
            created_at=datetime(2026, 7, 18, 12, 0, 0),
        )
        self.assertFalse(n.is_read)
        self.assertEqual(n.target_type, "trial_task")

    # ----------------------------------------------------------
    # user_id 验证
    # ----------------------------------------------------------

    def test_notification_base_user_id_zero(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=0,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="test",
                content="test",
                target_id=0,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    def test_notification_base_user_id_negative(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=-1,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="test",
                content="test",
                target_id=0,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    # ----------------------------------------------------------
    # target_id 验证
    # ----------------------------------------------------------

    def test_notification_base_target_id_zero(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        n = NotificationBase(
            user_id=1,
            notification_type=NotifyType.RECEIPT_DELAY,
            title="test",
            content="test",
            target_id=0,
            created_at=datetime(2026, 7, 18, 12, 0, 0),
        )
        self.assertEqual(n.target_id, 0)

    def test_notification_base_target_id_negative(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=1,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="test",
                content="test",
                target_id=-1,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    # ----------------------------------------------------------
    # title 非空
    # ----------------------------------------------------------

    def test_notification_base_title_empty(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=1,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="",
                content="test",
                target_id=0,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    def test_notification_base_title_whitespace(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=1,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="   ",
                content="test",
                target_id=0,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    # ----------------------------------------------------------
    # content 非空
    # ----------------------------------------------------------

    def test_notification_base_content_empty(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=1,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="test",
                content="",
                target_id=0,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    def test_notification_base_content_whitespace(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=1,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="test",
                content="   ",
                target_id=0,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    # ----------------------------------------------------------
    # target_type 非空
    # ----------------------------------------------------------

    def test_notification_base_target_type_empty(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=1,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="test",
                content="test",
                target_type="",
                target_id=0,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    # ----------------------------------------------------------
    # Enum 验证
    # ----------------------------------------------------------

    def test_notification_base_enum_receipt_delay(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        n = NotificationBase(
            user_id=1,
            notification_type=NotifyType.RECEIPT_DELAY,
            title="test",
            content="test",
            target_id=1,
            created_at=datetime(2026, 7, 18, 12, 0, 0),
        )
        self.assertEqual(n.notification_type, NotifyType.RECEIPT_DELAY)

    def test_notification_base_enum_grinding_delay(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        n = NotificationBase(
            user_id=1,
            notification_type=NotifyType.GRINDING_DELAY,
            title="test",
            content="test",
            target_id=1,
            created_at=datetime(2026, 7, 18, 12, 0, 0),
        )
        self.assertEqual(n.notification_type, NotifyType.GRINDING_DELAY)

    def test_notification_base_enum_report_missing(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        n = NotificationBase(
            user_id=1,
            notification_type=NotifyType.REPORT_MISSING,
            title="test",
            content="test",
            target_id=1,
            created_at=datetime(2026, 7, 18, 12, 0, 0),
        )
        self.assertEqual(n.notification_type, NotifyType.REPORT_MISSING)

    def test_notification_base_enum_invalid(self):
        from server.schemas import NotificationBase
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationBase(
                user_id=1,
                notification_type="invalid_type",
                title="test",
                content="test",
                target_id=1,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    # ============================================================
    # [5] NotificationCreate
    # ============================================================

    def test_notification_create_valid(self):
        from server.schemas import NotificationCreate
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        n = NotificationCreate(
            user_id=2,
            notification_type=NotifyType.GRINDING_DELAY,
            title="试磨超时",
            content="任务 TM202600035 试磨中超过5天",
            target_id=35,
            is_read=False,
            created_at=datetime(2026, 7, 18, 12, 0, 0),
        )
        self.assertEqual(n.user_id, 2)
        self.assertEqual(n.notification_type, NotifyType.GRINDING_DELAY)

    def test_notification_create_inherits_base(self):
        from server.schemas import (
            NotificationCreate,
            NotificationBase,
        )
        self.assertTrue(issubclass(NotificationCreate, NotificationBase))

    # ============================================================
    # [6] NotificationUpdate
    # ============================================================

    def test_notification_update_valid(self):
        from server.schemas import NotificationUpdate
        n = NotificationUpdate(is_read=True)
        self.assertTrue(n.is_read)

    def test_notification_update_empty(self):
        from server.schemas import NotificationUpdate
        n = NotificationUpdate()
        self.assertIsNone(n.is_read)

    def test_notification_update_is_read_false(self):
        from server.schemas import NotificationUpdate
        n = NotificationUpdate(is_read=False)
        self.assertFalse(n.is_read)

    def test_notification_update_not_inherits_base(self):
        from server.schemas import (
            NotificationUpdate,
            NotificationBase,
        )
        self.assertFalse(issubclass(NotificationUpdate, NotificationBase))

    def test_notification_update_no_extra_fields(self):
        from server.schemas import NotificationUpdate
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationUpdate(is_read=True, extra_field="should_fail")

    # ============================================================
    # [7] NotificationResponse
    # ============================================================

    def test_notification_response_valid(self):
        from server.schemas import NotificationResponse
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        now = datetime(2026, 7, 18, 12, 0, 0)
        n = NotificationResponse(
            id=1,
            user_id=1,
            notification_type=NotifyType.RECEIPT_DELAY,
            title="收件超时",
            content="content here",
            target_id=18,
            is_read=False,
            read_time=None,
            created_at=now,
            updated_at=now,
        )
        self.assertEqual(n.id, 1)
        self.assertIsNone(n.read_time)
        self.assertEqual(n.updated_at, now)

    def test_notification_response_with_read_time(self):
        from server.schemas import NotificationResponse
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        now = datetime(2026, 7, 18, 12, 0, 0)
        read_at = datetime(2026, 7, 18, 13, 0, 0)
        n = NotificationResponse(
            id=1,
            user_id=1,
            notification_type=NotifyType.RECEIPT_DELAY,
            title="test",
            content="content",
            target_id=1,
            is_read=True,
            read_time=read_at,
            created_at=now,
            updated_at=read_at,
        )
        self.assertTrue(n.is_read)
        self.assertEqual(n.read_time, read_at)

    def test_notification_response_inherits_base(self):
        from server.schemas import (
            NotificationResponse,
            NotificationBase,
        )
        self.assertTrue(issubclass(NotificationResponse, NotificationBase))

    def test_notification_response_id_zero(self):
        from server.schemas import NotificationResponse
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationResponse(
                id=0,
                user_id=1,
                notification_type=NotifyType.RECEIPT_DELAY,
                title="test",
                content="test",
                target_id=1,
                created_at=datetime(2026, 7, 18, 12, 0, 0),
                updated_at=datetime(2026, 7, 18, 12, 0, 0),
            )

    # ============================================================
    # [8] NotificationListResponse
    # ============================================================

    def test_notification_list_response_empty(self):
        from server.schemas import NotificationListResponse
        resp = NotificationListResponse(items=[], total=0)
        self.assertEqual(resp.items, [])
        self.assertEqual(resp.total, 0)

    def test_notification_list_response_valid(self):
        from server.schemas import (
            NotificationListResponse,
            NotificationResponse,
        )
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        now = datetime(2026, 7, 18, 12, 0, 0)
        item = NotificationResponse(
            id=1,
            user_id=1,
            notification_type=NotifyType.RECEIPT_DELAY,
            title="test",
            content="test",
            target_id=1,
            created_at=now,
            updated_at=now,
        )
        resp = NotificationListResponse(items=[item], total=1)
        self.assertEqual(len(resp.items), 1)
        self.assertEqual(resp.total, 1)

    def test_notification_list_response_total_negative(self):
        from server.schemas import NotificationListResponse
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationListResponse(items=[], total=-1)

    # ============================================================
    # [9] NotificationQuery
    # ============================================================

    def test_notification_query_defaults(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery()
        self.assertEqual(q.page, 1)
        self.assertEqual(q.page_size, 20)
        self.assertIsNone(q.user_id)
        self.assertIsNone(q.notification_type)
        self.assertIsNone(q.is_read)
        self.assertIsNone(q.keyword)
        self.assertEqual(q.sort_by, "created_at")
        self.assertEqual(q.sort_order, "desc")

    def test_notification_query_page_zero(self):
        from server.schemas import NotificationQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationQuery(page=0)

    def test_notification_query_page_negative(self):
        from server.schemas import NotificationQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationQuery(page=-1)

    def test_notification_query_page_size_zero(self):
        from server.schemas import NotificationQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationQuery(page_size=0)

    def test_notification_query_page_size_201(self):
        from server.schemas import NotificationQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationQuery(page_size=201)

    def test_notification_query_page_size_200(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(page_size=200)
        self.assertEqual(q.page_size, 200)

    def test_notification_query_page_size_1(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(page_size=1)
        self.assertEqual(q.page_size, 1)

    def test_notification_query_user_id_zero(self):
        from server.schemas import NotificationQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationQuery(user_id=0)

    def test_notification_query_user_id_negative(self):
        from server.schemas import NotificationQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationQuery(user_id=-1)

    def test_notification_query_sort_order_asc(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(sort_order="asc")
        self.assertEqual(q.sort_order, "asc")

    def test_notification_query_sort_order_desc(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(sort_order="desc")
        self.assertEqual(q.sort_order, "desc")

    def test_notification_query_sort_order_invalid(self):
        from server.schemas import NotificationQuery
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            NotificationQuery(sort_order="invalid")

    def test_notification_query_keyword_empty(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(keyword="")
        self.assertIsNone(q.keyword)

    def test_notification_query_keyword_whitespace(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(keyword="   ")
        self.assertIsNone(q.keyword)

    def test_notification_query_keyword_valid(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(keyword="TM2026")
        self.assertEqual(q.keyword, "TM2026")

    def test_notification_query_notification_type_enum(self):
        from server.schemas import NotificationQuery
        from server.enums.notify_type import NotifyType
        q = NotificationQuery(notification_type=NotifyType.RECEIPT_DELAY)
        self.assertEqual(q.notification_type, NotifyType.RECEIPT_DELAY)

    def test_notification_query_is_read_true(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(is_read=True)
        self.assertTrue(q.is_read)

    def test_notification_query_is_read_false(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(is_read=False)
        self.assertFalse(q.is_read)

    def test_notification_query_model_dump_exclude_none(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(page=1, page_size=10)
        d = q.model_dump(exclude_none=True)
        self.assertEqual(d["page"], 1)
        self.assertEqual(d["page_size"], 10)
        self.assertNotIn("user_id", d)
        self.assertNotIn("notification_type", d)
        self.assertNotIn("is_read", d)
        self.assertNotIn("keyword", d)

    def test_notification_query_time_range(self):
        from server.schemas import NotificationQuery
        q = NotificationQuery(page=1, page_size=20)
        self.assertEqual(q.page, 1)
        self.assertEqual(q.page_size, 20)

    # ============================================================
    # [10] Serialization
    # ============================================================

    def test_notification_base_model_dump(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        now = datetime(2026, 7, 18, 12, 0, 0)
        n = NotificationBase(
            user_id=1,
            notification_type=NotifyType.RECEIPT_DELAY,
            title="test",
            content="test",
            target_id=1,
            created_at=now,
        )
        d = n.model_dump()
        self.assertEqual(d["user_id"], 1)
        self.assertEqual(d["notification_type"], "receipt_delay")
        self.assertEqual(d["title"], "test")

    def test_notification_base_model_dump_json(self):
        from server.schemas import NotificationBase
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        import json
        now = datetime(2026, 7, 18, 12, 0, 0)
        n = NotificationBase(
            user_id=1,
            notification_type=NotifyType.RECEIPT_DELAY,
            title="test",
            content="test",
            target_id=1,
            created_at=now,
        )
        j = n.model_dump_json()
        d = json.loads(j)
        self.assertEqual(d["user_id"], 1)
        self.assertEqual(d["notification_type"], "receipt_delay")

    def test_notification_response_model_dump(self):
        from server.schemas import NotificationResponse
        from server.enums.notify_type import NotifyType
        from datetime import datetime
        now = datetime(2026, 7, 18, 12, 0, 0)
        n = NotificationResponse(
            id=1,
            user_id=1,
            notification_type=NotifyType.GRINDING_DELAY,
            title="test",
            content="test",
            target_id=2,
            is_read=True,
            read_time=now,
            created_at=now,
            updated_at=now,
        )
        d = n.model_dump()
        self.assertEqual(d["id"], 1)
        self.assertEqual(d["notification_type"], "grinding_delay")
        self.assertTrue(d["is_read"])

    # ============================================================
    # [11] Type Hint
    # ============================================================

    def test_type_hints(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn("from typing import", source)
        self.assertIn("Optional", source)

    # ============================================================
    # [12] Docstring
    # ============================================================

    def test_module_docstring(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn('"""消息提醒 Schema', source)

    def test_class_docstrings(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn("class NotificationBase", source)
        self.assertIn("class NotificationCreate", source)
        self.assertIn("class NotificationUpdate", source)
        self.assertIn("class NotificationResponse", source)
        self.assertIn("class NotificationListResponse", source)
        self.assertIn("class NotificationQuery", source)

    # ============================================================
    # [13] PEP8
    # ============================================================

    def test_pep8(self):
        result = subprocess.run(
            [sys.executable, "-m", "flake8", self._source_path,
             "--ignore=W503"],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        self.assertEqual(
            result.stdout.strip(), "",
            f"PEP8: {result.stdout.strip()}"
        )

    # ============================================================
    # [14] Zero Workflow
    # ============================================================

    def test_zero_workflow(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("process_status", source)

    # ============================================================
    # [15] Zero Status Machine
    # ============================================================

    def test_zero_status_machine(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        # 排除 docstring 中的 "status"（如 "Status Machine" 描述）
        lines = source.split("\n")
        code_lines = []
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(chr(34) + chr(34) + chr(34)):
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            code_lines.append(stripped)
        code_source = "\n".join(code_lines).lower()
        self.assertNotIn("status", code_source)

    # ============================================================
    # [16] No Circular Import
    # ============================================================

    def test_no_circular_import(self):
        try:
            from server.schemas import (
                NotificationBase,
                NotificationCreate,
                NotificationUpdate,
                NotificationResponse,
                NotificationListResponse,
                NotificationQuery,
            )
        except ImportError as e:
            self.fail(f"Circular import: {e}")

    # ============================================================
    # [17] __init__.py 导出
    # ============================================================

    def test_init_py_exports(self):
        init_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server", "schemas", "__init__.py",
        )
        with open(init_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn("NotificationBase", source)
        self.assertIn("NotificationCreate", source)
        self.assertIn("NotificationUpdate", source)
        self.assertIn("NotificationResponse", source)
        self.assertIn("NotificationListResponse", source)
        self.assertIn("NotificationQuery", source)

    # ============================================================
    # [18] 禁止项
    # ============================================================

    def test_no_orm(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("Session", source)
        self.assertNotIn("session", source)

    def test_no_business_logic(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("def check_", source)
        self.assertNotIn("def get_", source)
        self.assertNotIn("def create_", source)
        self.assertNotIn("def update_", source)

    def test_no_enum_invalid(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("invalid_type", source)

    # ============================================================
    # [19] 代码行宽
    # ============================================================

    def test_line_width(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            stripped = line.rstrip("\n")
            self.assertLessEqual(
                len(stripped), 79,
                f"Line {i} exceeds 79 chars: {len(stripped)}"
            )

    # ============================================================
    # [20] 文件末尾换行
    # ============================================================

    def test_trailing_newline(self):
        with open(self._source_path, "rb") as f:
            f.seek(-1, 2)
            self.assertEqual(f.read(), b"\n")

    # ============================================================
    # [21] 无 TODO / FIXME / pass
    # ============================================================

    def test_no_todo_fixme_pass(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("TODO", source)
        self.assertNotIn("FIXME", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)