"""试磨任务 Schema 测试

Sprint 5 — Task 5.1
测试 server/schemas/trial_task_schema.py 的全部 Schema 类。

测试架构说明：
    本测试运行于测试环境，不依赖 PySide6 DLL。
    采用纯 Python 测试，直接 import Schema 类进行验证。

覆盖范围：
    - py_compile
    - import
    - Schema 导出（__all__）
    - TrialTaskCreate 必填字段
    - TrialTaskUpdate 全部 Optional
    - TrialTaskResponse 字段 & from_attributes
    - TrialTaskListResponse 结构
    - 字段数量、字段类型
    - Optional / 必填
    - ConfigDict(from_attributes=True)
    - model_validate()
    - model_dump()
    - model_dump_json()
    - datetime
    - date
    - exclude_unset()
    - 禁止字段
    - Pydantic v2
    - 无循环导入
    - PEP8
"""

import os
import re
import sys
import py_compile
import importlib
from datetime import date, datetime

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# 辅助函数
# ============================================================


def extract_code_text(file_path: str) -> str:
    """提取 Python 文件中的代码文本（排除 docstring 和注释）。"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 移除多行字符串（docstring）
    content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", "", content, flags=re.DOTALL)
    # 移除单行注释
    content = re.sub(r"#.*$", "", content, flags=re.MULTILINE)
    return content


# ============================================================
# 1. py_compile
# ============================================================


def test_py_compile():
    """py_compile: 验证 trial_task_schema.py 可以被 Python 编译器编译。"""
    schema_path = os.path.join(
        PROJECT_ROOT, "server", "schemas", "trial_task_schema.py"
    )
    py_compile.compile(schema_path, doraise=True)
    assert True


# ============================================================
# 2. import
# ============================================================


def test_import_all_schemas():
    """import: 验证全部 5 个 Schema 类可以正常导入。"""
    from server.schemas.trial_task_schema import (
        TrialTaskBase,
        TrialTaskCreate,
        TrialTaskUpdate,
        TrialTaskResponse,
        TrialTaskListResponse,
    )
    assert TrialTaskBase is not None
    assert TrialTaskCreate is not None
    assert TrialTaskUpdate is not None
    assert TrialTaskResponse is not None
    assert TrialTaskListResponse is not None


def test_import_from_package():
    """import: 验证从 server.schemas 包导入。"""
    from server.schemas import (
        TrialTaskBase,
        TrialTaskCreate,
        TrialTaskUpdate,
        TrialTaskResponse,
        TrialTaskListResponse,
    )
    assert TrialTaskBase is not None
    assert TrialTaskCreate is not None
    assert TrialTaskUpdate is not None
    assert TrialTaskResponse is not None
    assert TrialTaskListResponse is not None


# ============================================================
# 3. Schema 导出（__all__）
# ============================================================


def test_all_exports():
    """__all__: 验证 __all__ 包含全部 5 个 Schema 类名。"""
    from server.schemas import trial_task_schema
    assert hasattr(trial_task_schema, "__all__")
    assert "TrialTaskBase" in trial_task_schema.__all__
    assert "TrialTaskCreate" in trial_task_schema.__all__
    assert "TrialTaskUpdate" in trial_task_schema.__all__
    assert "TrialTaskResponse" in trial_task_schema.__all__
    assert "TrialTaskListResponse" in trial_task_schema.__all__


# ============================================================
# 4. TrialTaskCreate — 必填字段
# ============================================================


def test_create_required_fields():
    """TrialTaskCreate: 验证必填字段（customer_id, requirement, sales_id）。"""
    from server.schemas.trial_task_schema import TrialTaskCreate

    # 缺少必填字段应抛出 ValidationError
    from pydantic import ValidationError

    try:
        TrialTaskCreate()
        assert False, "缺少必填字段应抛出 ValidationError"
    except ValidationError:
        pass

    # 填写必填字段应成功
    task = TrialTaskCreate(
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
    )
    assert task.customer_id == 1
    assert task.requirement == "加工要求"
    assert task.sales_id == 1


def test_create_default_values():
    """TrialTaskCreate: 验证默认值。"""
    from server.schemas.trial_task_schema import TrialTaskCreate
    from server.enums import TrialTaskProcessStatus, TrialTaskResultStatus

    task = TrialTaskCreate(
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
    )
    assert task.process_status == TrialTaskProcessStatus.CREATED
    assert task.result_status == TrialTaskResultStatus.PENDING
    assert task.tracking_no is None
    assert task.destination is None
    assert task.destination_date is None
    assert task.failure_reason is None


def test_create_all_fields():
    """TrialTaskCreate: 验证填写全部字段。"""
    from server.schemas.trial_task_schema import TrialTaskCreate
    from server.enums import (
        TrialTaskProcessStatus,
        TrialTaskResultStatus,
        DestinationType,
    )

    task = TrialTaskCreate(
        customer_id=1,
        requirement="加工要求",
        tracking_no="SF1234567890",
        sales_id=1,
        process_status=TrialTaskProcessStatus.CREATED,
        result_status=TrialTaskResultStatus.PENDING,
        destination=DestinationType.RETURNED_CUSTOMER,
        destination_date=date(2026, 7, 7),
        failure_reason="不满足要求",
    )
    assert task.customer_id == 1
    assert task.requirement == "加工要求"
    assert task.tracking_no == "SF1234567890"
    assert task.sales_id == 1
    assert task.process_status == TrialTaskProcessStatus.CREATED
    assert task.result_status == TrialTaskResultStatus.PENDING
    assert task.destination == DestinationType.RETURNED_CUSTOMER
    assert task.destination_date == date(2026, 7, 7)
    assert task.failure_reason == "不满足要求"


def test_create_disallowed_fields():
    """TrialTaskCreate: 验证禁止字段（id, task_no, created_at 等不在字段列表中）。"""
    from server.schemas.trial_task_schema import TrialTaskCreate

    fields = TrialTaskCreate.model_fields
    # id 不在 Create 中
    assert "id" not in fields, "Create 不应包含 id 字段"
    # task_no 不在 Create 中（系统自动生成）
    assert "task_no" not in fields, "Create 不应包含 task_no 字段"
    # created_at 不在 Create 中
    assert "created_at" not in fields, "Create 不应包含 created_at 字段"
    # updated_at 不在 Create 中
    assert "updated_at" not in fields, "Create 不应包含 updated_at 字段"
    # created_by 不在 Create 中
    assert "created_by" not in fields, "Create 不应包含 created_by 字段"
    # updated_by 不在 Create 中
    assert "updated_by" not in fields, "Create 不应包含 updated_by 字段"
    # is_deleted 不在 Create 中
    assert "is_deleted" not in fields, "Create 不应包含 is_deleted 字段"


# ============================================================
# 5. TrialTaskUpdate — 全部 Optional
# ============================================================


def test_update_all_optional():
    """TrialTaskUpdate: 验证全部字段 Optional。"""
    from server.schemas.trial_task_schema import TrialTaskUpdate

    # 全部字段为空应成功
    update = TrialTaskUpdate()
    assert update.customer_id is None
    assert update.requirement is None
    assert update.tracking_no is None
    assert update.sales_id is None
    assert update.process_status is None
    assert update.result_status is None
    assert update.destination is None
    assert update.destination_date is None
    assert update.failure_reason is None


def test_update_exclude_unset():
    """TrialTaskUpdate: 验证 exclude_unset() 行为。"""
    from server.schemas.trial_task_schema import TrialTaskUpdate

    update = TrialTaskUpdate(requirement="新要求")
    dumped = update.model_dump(exclude_unset=True)
    assert dumped == {"requirement": "新要求"}
    assert "customer_id" not in dumped


def test_update_partial():
    """TrialTaskUpdate: 验证部分字段更新。"""
    from server.schemas.trial_task_schema import TrialTaskUpdate

    update = TrialTaskUpdate(
        tracking_no="SF0987654321",
        failure_reason="试磨失败",
    )
    assert update.tracking_no == "SF0987654321"
    assert update.failure_reason == "试磨失败"
    assert update.customer_id is None


# ============================================================
# 6. TrialTaskResponse — 字段 & from_attributes
# ============================================================


def test_response_config_dict():
    """TrialTaskResponse: 验证 ConfigDict(from_attributes=True)。"""
    from server.schemas.trial_task_schema import TrialTaskResponse

    assert hasattr(TrialTaskResponse, "model_config")
    assert TrialTaskResponse.model_config.get("from_attributes") is True


def test_response_fields():
    """TrialTaskResponse: 验证字段列表。"""
    from server.schemas.trial_task_schema import TrialTaskResponse

    fields = TrialTaskResponse.model_fields
    assert "id" in fields
    assert "task_no" in fields
    assert "customer_id" in fields
    assert "requirement" in fields
    assert "tracking_no" in fields
    assert "sales_id" in fields
    assert "process_status" in fields
    assert "result_status" in fields
    assert "destination" in fields
    assert "destination_date" in fields
    assert "failure_reason" in fields
    assert "created_at" in fields
    assert "updated_at" in fields


def test_response_excluded_fields():
    """TrialTaskResponse: 验证排除了敏感字段。"""
    from server.schemas.trial_task_schema import TrialTaskResponse

    fields = TrialTaskResponse.model_fields
    assert "created_by" not in fields
    assert "updated_by" not in fields
    assert "is_deleted" not in fields
    assert "password_hash" not in fields


def test_response_field_count():
    """TrialTaskResponse: 验证字段数量（13 个 = 11 业务 + id + created_at + updated_at + task_no）。"""
    from server.schemas.trial_task_schema import TrialTaskResponse

    # 13 个字段: id, task_no, customer_id, requirement, tracking_no, sales_id,
    # process_status, result_status, destination, destination_date, failure_reason,
    # created_at, updated_at
    assert len(TrialTaskResponse.model_fields) == 13


def test_response_field_types():
    """TrialTaskResponse: 验证字段类型。"""
    from server.schemas.trial_task_schema import TrialTaskResponse
    from server.enums import (
        TrialTaskProcessStatus,
        TrialTaskResultStatus,
        DestinationType,
    )

    fields = TrialTaskResponse.model_fields

    # 检查字段类型注解
    assert fields["id"].annotation == int
    assert fields["task_no"].annotation == str
    assert fields["customer_id"].annotation == int
    assert fields["requirement"].annotation == str
    assert fields["sales_id"].annotation == int
    assert fields["process_status"].annotation == TrialTaskProcessStatus
    assert fields["result_status"].annotation == TrialTaskResultStatus
    # Optional 字段在 annotation 中会以 Union 形式出现
    # 检查 Optional 字段
    from typing import get_origin, Union

    for field_name in ["tracking_no", "destination", "destination_date", "failure_reason"]:
        ann = fields[field_name].annotation
        assert get_origin(ann) is Union, f"{field_name} 应为 Optional"
        assert type(None) in ann.__args__, f"{field_name} 应为 Optional"


# ============================================================
# 7. TrialTaskListResponse — 结构
# ============================================================


def test_list_response_structure():
    """TrialTaskListResponse: 验证结构（items + total）。"""
    from server.schemas.trial_task_schema import (
        TrialTaskListResponse,
        TrialTaskResponse,
    )

    resp = TrialTaskListResponse(
        items=[
            TrialTaskResponse(
                id=1,
                task_no="20260707-1",
                customer_id=1,
                requirement="加工要求",
                sales_id=1,
                process_status="created",
                result_status="pending",
                created_at=datetime(2026, 7, 7, 12, 0, 0),
                updated_at=datetime(2026, 7, 7, 12, 0, 0),
            )
        ],
        total=1,
    )
    assert len(resp.items) == 1
    assert resp.total == 1
    assert resp.items[0].id == 1
    assert resp.items[0].task_no == "20260707-1"


def test_list_response_empty():
    """TrialTaskListResponse: 验证空列表。"""
    from server.schemas.trial_task_schema import TrialTaskListResponse

    resp = TrialTaskListResponse(items=[], total=0)
    assert resp.items == []
    assert resp.total == 0


# ============================================================
# 8. model_validate() / model_dump()
# ============================================================


def test_model_validate_create():
    """model_validate: TrialTaskCreate 从 dict 构造。"""
    from server.schemas.trial_task_schema import TrialTaskCreate

    data = {
        "customer_id": 1,
        "requirement": "加工要求",
        "sales_id": 1,
    }
    task = TrialTaskCreate.model_validate(data)
    assert task.customer_id == 1
    assert task.requirement == "加工要求"
    assert task.sales_id == 1


def test_model_dump_create():
    """model_dump: TrialTaskCreate 序列化。"""
    from server.schemas.trial_task_schema import TrialTaskCreate

    task = TrialTaskCreate(
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
    )
    dumped = task.model_dump()
    assert dumped["customer_id"] == 1
    assert dumped["requirement"] == "加工要求"
    assert dumped["sales_id"] == 1
    assert dumped["process_status"] == "created"
    assert dumped["result_status"] == "pending"


def test_model_dump_json():
    """model_dump_json: TrialTaskCreate JSON 序列化。"""
    from server.schemas.trial_task_schema import TrialTaskCreate

    task = TrialTaskCreate(
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
    )
    json_str = task.model_dump_json()
    assert isinstance(json_str, str)
    assert '"customer_id":1' in json_str
    assert '"requirement":"加工要求"' in json_str


# ============================================================
# 9. datetime / date 字段
# ============================================================


def test_date_fields():
    """date: 验证 destination_date 为 date 类型。"""
    from server.schemas.trial_task_schema import (
        TrialTaskCreate,
        TrialTaskResponse,
    )

    # Create 中 date 类型
    task = TrialTaskCreate(
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
        destination_date=date(2026, 7, 7),
    )
    assert task.destination_date == date(2026, 7, 7)
    assert isinstance(task.destination_date, date)

    # Response 中 date 类型
    resp = TrialTaskResponse(
        id=1,
        task_no="20260707-1",
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
        process_status="created",
        result_status="pending",
        destination_date=date(2026, 7, 7),
        created_at=datetime(2026, 7, 7, 12, 0, 0),
        updated_at=datetime(2026, 7, 7, 12, 0, 0),
    )
    assert isinstance(resp.destination_date, date)


def test_datetime_fields():
    """datetime: 验证 created_at/updated_at 为 datetime 类型。"""
    from server.schemas.trial_task_schema import TrialTaskResponse

    resp = TrialTaskResponse(
        id=1,
        task_no="20260707-1",
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
        process_status="created",
        result_status="pending",
        created_at=datetime(2026, 7, 7, 12, 0, 0),
        updated_at=datetime(2026, 7, 7, 12, 0, 0),
    )
    assert isinstance(resp.created_at, datetime)
    assert isinstance(resp.updated_at, datetime)


# ============================================================
# 10. Enum 字段
# ============================================================


def test_enum_fields():
    """Enum: 验证 process_status/result_status/destination 使用正确枚举。"""
    from server.schemas.trial_task_schema import TrialTaskCreate
    from server.enums import (
        TrialTaskProcessStatus,
        TrialTaskResultStatus,
        DestinationType,
    )

    task = TrialTaskCreate(
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
        process_status=TrialTaskProcessStatus.CREATED,
        result_status=TrialTaskResultStatus.PENDING,
        destination=DestinationType.RETURNED_CUSTOMER,
    )
    assert task.process_status == TrialTaskProcessStatus.CREATED
    assert task.result_status == TrialTaskResultStatus.PENDING
    assert task.destination == DestinationType.RETURNED_CUSTOMER


def test_enum_string_coercion():
    """Enum: 验证字符串自动转换为枚举值。"""
    from server.schemas.trial_task_schema import TrialTaskCreate
    from server.enums import TrialTaskProcessStatus, TrialTaskResultStatus

    task = TrialTaskCreate(
        customer_id=1,
        requirement="加工要求",
        sales_id=1,
        process_status="created",
        result_status="pending",
    )
    assert task.process_status == TrialTaskProcessStatus.CREATED
    assert task.result_status == TrialTaskResultStatus.PENDING


# ============================================================
# 11. Pydantic v2
# ============================================================


def test_pydantic_v2():
    """Pydantic v2: 验证使用 Pydantic v2 特性（model_fields, model_config）。"""
    from server.schemas.trial_task_schema import (
        TrialTaskBase,
        TrialTaskResponse,
    )

    # 使用 model_fields (v2) 属性
    assert hasattr(TrialTaskBase, "model_fields")

    # 使用 model_config (v2) 而非 Config (v1)
    assert hasattr(TrialTaskResponse, "model_config")
    assert not hasattr(TrialTaskResponse, "Config")

    # 确认 model_config 使用 from_attributes (v2 替代 orm_mode)
    assert TrialTaskResponse.model_config.get("from_attributes") is True


# ============================================================
# 12. 无循环导入
# ============================================================


def test_no_circular_import():
    """循环导入: 验证 server.schemas 包无循环导入。"""
    importlib.reload(sys.modules.get("server.schemas.trial_task_schema", importlib.import_module("server.schemas.trial_task_schema")))


# ============================================================
# 13. PEP8
# ============================================================


def test_pep8_compliance():
    """PEP8: 验证代码符合 PEP8 规范。"""
    schema_path = os.path.join(
        PROJECT_ROOT, "server", "schemas", "trial_task_schema.py"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 无 tab 缩进
    assert "\t" not in content, "文件中不应使用 tab 缩进"

    # 文件以换行结尾
    assert content.endswith("\n"), "文件应以换行结尾"


# ============================================================
# 14. 代码规范
# ============================================================


def test_no_print():
    """print(): 验证无 print() 语句。"""
    schema_path = os.path.join(
        PROJECT_ROOT, "server", "schemas", "trial_task_schema.py"
    )
    code = extract_code_text(schema_path)
    assert "print(" not in code, "不应包含 print() 语句"


def test_no_todo():
    """TODO: 验证无 TODO 注释。"""
    schema_path = os.path.join(
        PROJECT_ROOT, "server", "schemas", "trial_task_schema.py"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "TODO" not in content, "不应包含 TODO"


def test_no_fixme():
    """FIXME: 验证无 FIXME 注释。"""
    schema_path = os.path.join(
        PROJECT_ROOT, "server", "schemas", "trial_task_schema.py"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "FIXME" not in content, "不应包含 FIXME"


# ============================================================
# 15. Docstring
# ============================================================


def test_class_docstrings():
    """Docstring: 验证所有 Schema 类有 Google 风格 docstring。"""
    schema_path = os.path.join(
        PROJECT_ROOT, "server", "schemas", "trial_task_schema.py"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()

    for class_name in [
        "TrialTaskBase",
        "TrialTaskCreate",
        "TrialTaskUpdate",
        "TrialTaskResponse",
        "TrialTaskListResponse",
    ]:
        # 每个类定义后应有 docstring
        pattern = rf"class {class_name}\(\w+\):\s*\n\s*\"\"\""
        assert re.search(pattern, content), f"{class_name} 缺少 docstring"


def test_type_hints():
    """Type Hint: 验证所有字段有类型注解。"""
    from server.schemas.trial_task_schema import (
        TrialTaskCreate,
        TrialTaskUpdate,
        TrialTaskResponse,
    )

    # 所有字段应有类型注解
    for cls in [TrialTaskCreate, TrialTaskUpdate, TrialTaskResponse]:
        for field_name, field_info in cls.model_fields.items():
            assert field_info.annotation is not None, (
                f"{cls.__name__}.{field_name} 缺少类型注解"
            )


# ============================================================
# 16. 不得重新定义 Enum
# ============================================================


def test_no_redefined_enum():
    """Enum: 验证 Schema 未重新定义枚举类。"""
    from server.schemas.trial_task_schema import (
        TrialTaskCreate,
        TrialTaskResponse,
    )
    from server.enums import (
        TrialTaskProcessStatus,
        TrialTaskResultStatus,
        DestinationType,
    )

    # process_status 使用导入的枚举
    assert TrialTaskCreate.model_fields["process_status"].annotation == TrialTaskProcessStatus
    assert TrialTaskResponse.model_fields["process_status"].annotation == TrialTaskProcessStatus

    # result_status 使用导入的枚举
    assert TrialTaskCreate.model_fields["result_status"].annotation == TrialTaskResultStatus
    assert TrialTaskResponse.model_fields["result_status"].annotation == TrialTaskResultStatus

    # destination 使用导入的枚举
    assert TrialTaskCreate.model_fields["destination"].annotation is not None
    assert TrialTaskResponse.model_fields["destination"].annotation is not None


# ============================================================
# 17. 字段数量验证
# ============================================================


def test_create_field_count():
    """TrialTaskCreate: 验证字段数量（9 个业务字段）。"""
    from server.schemas.trial_task_schema import TrialTaskCreate

    # 9 个字段: customer_id, requirement, tracking_no, sales_id,
    # process_status, result_status, destination, destination_date, failure_reason
    assert len(TrialTaskCreate.model_fields) == 9


def test_update_field_count():
    """TrialTaskUpdate: 验证字段数量（9 个，全部 Optional）。"""
    from server.schemas.trial_task_schema import TrialTaskUpdate

    assert len(TrialTaskUpdate.model_fields) == 9


def test_base_field_count():
    """TrialTaskBase: 验证字段数量（9 个）。"""
    from server.schemas.trial_task_schema import TrialTaskBase

    assert len(TrialTaskBase.model_fields) == 9