"""Test: Customer Schema (Sprint 4 — Task 4.1)

严格依据 DEVELOPMENT_ROADMAP.md Task 4.1 验收标准。
测试 server/schemas/customer_schema.py 全部 Schema 类。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import json
import sys
from datetime import datetime

from pydantic import BaseModel


# ============================================================
# 自检框架
# ============================================================

PASSED = 0
FAILED = 0


def check(desc: str, condition: bool) -> None:
    """执行一条检查。

    Args:
        desc: 检查描述。
        condition: 检查条件。
    """
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {desc}")
    else:
        FAILED += 1
        print(f"  [FAIL] {desc}")


# ============================================================
# 自检
# ============================================================

print("=" * 60)
print("  Task 4.1 — Customer Schema Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile("server/schemas/customer_schema.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.schemas.customer_schema import (
        CustomerBase,
        CustomerCreate,
        CustomerUpdate,
        CustomerResponse,
        CustomerListResponse,
    )
    check("CustomerBase 导入", True)
    check("CustomerCreate 导入", True)
    check("CustomerUpdate 导入", True)
    check("CustomerResponse 导入", True)
    check("CustomerListResponse 导入", True)
except ImportError as e:
    check("import", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] __init__ 导出
# ----------------------------------------------------------
print("\n[3] __init__ 导出")
from server.schemas import (
    CustomerBase as InitCustomerBase,
    CustomerCreate as InitCustomerCreate,
    CustomerUpdate as InitCustomerUpdate,
    CustomerResponse as InitCustomerResponse,
    CustomerListResponse as InitCustomerListResponse,
)
check("__init__ 导出 CustomerBase", InitCustomerBase is CustomerBase)
check("__init__ 导出 CustomerCreate", InitCustomerCreate is CustomerCreate)
check("__init__ 导出 CustomerUpdate", InitCustomerUpdate is CustomerUpdate)
check("__init__ 导出 CustomerResponse", InitCustomerResponse is CustomerResponse)
check("__init__ 导出 CustomerListResponse", InitCustomerListResponse is CustomerListResponse)

# ----------------------------------------------------------
# [4] CustomerBase — 实例化
# ----------------------------------------------------------
print("\n[4] CustomerBase — 实例化")
try:
    base = CustomerBase(company_name="测试公司")
    check("company_name 正确", base.company_name == "测试公司")
    check("contact_person 默认 None", base.contact_person is None)
    check("phone 默认 None", base.phone is None)
    check("email 默认 None", base.email is None)
    check("address 默认 None", base.address is None)
    check("remark 默认 None", base.remark is None)
except Exception as e:
    check("CustomerBase 实例化", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [5] CustomerBase — company_name 必填
# ----------------------------------------------------------
print("\n[5] CustomerBase — company_name 必填")
try:
    from pydantic import ValidationError as PydanticValidationError
    CustomerBase()
    check("缺少 company_name 应报错", False)
except PydanticValidationError:
    check("缺少 company_name 抛出 ValidationError", True)
except Exception as e:
    check(f"缺少 company_name 应报错: {e}", False)

# ----------------------------------------------------------
# [6] CustomerBase — 全字段赋值
# ----------------------------------------------------------
print("\n[6] CustomerBase — 全字段赋值")
try:
    base = CustomerBase(
        company_name="测试公司",
        contact_person="张三",
        phone="13800138000",
        email="test@example.com",
        address="北京市朝阳区",
        remark="测试备注",
    )
    check("company_name", base.company_name == "测试公司")
    check("contact_person", base.contact_person == "张三")
    check("phone", base.phone == "13800138000")
    check("email", base.email == "test@example.com")
    check("address", base.address == "北京市朝阳区")
    check("remark", base.remark == "测试备注")
except Exception as e:
    check("全字段赋值", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [7] CustomerBase — 长度限制
# ----------------------------------------------------------
print("\n[7] CustomerBase — 长度限制")
try:
    CustomerBase(company_name="A" * 201)
    check("company_name > 200 应报错", False)
except PydanticValidationError:
    check("company_name > 200 抛出 ValidationError", True)

try:
    CustomerBase(company_name="A", contact_person="B" * 51)
    check("contact_person > 50 应报错", False)
except PydanticValidationError:
    check("contact_person > 50 抛出 ValidationError", True)

try:
    CustomerBase(company_name="A", phone="C" * 21)
    check("phone > 20 应报错", False)
except PydanticValidationError:
    check("phone > 20 抛出 ValidationError", True)

# ----------------------------------------------------------
# [8] CustomerBase — company_name 空字符串
# ----------------------------------------------------------
print("\n[8] CustomerBase — company_name 空字符串")
try:
    CustomerBase(company_name="")
    check("company_name 空字符串应报错", False)
except PydanticValidationError:
    check("company_name 空字符串抛出 ValidationError", True)

# ----------------------------------------------------------
# [9] CustomerCreate — 继承
# ----------------------------------------------------------
print("\n[9] CustomerCreate — 继承")
try:
    create = CustomerCreate(company_name="新客户")
    check("CustomerCreate 继承 CustomerBase", isinstance(create, CustomerBase))
    check("company_name", create.company_name == "新客户")
except Exception as e:
    check("CustomerCreate 实例化", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [10] CustomerCreate — 全字段
# ----------------------------------------------------------
print("\n[10] CustomerCreate — 全字段")
try:
    create = CustomerCreate(
        company_name="新客户",
        contact_person="李四",
        phone="13900139000",
        email="new@example.com",
        address="上海市浦东新区",
        remark="新客户备注",
    )
    check("company_name", create.company_name == "新客户")
    check("contact_person", create.contact_person == "李四")
    check("phone", create.phone == "13900139000")
    check("email", create.email == "new@example.com")
    check("address", create.address == "上海市浦东新区")
    check("remark", create.remark == "新客户备注")
except Exception as e:
    check("全字段创建", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [11] CustomerUpdate — 全部 Optional
# ----------------------------------------------------------
print("\n[11] CustomerUpdate — 全部 Optional")
try:
    update = CustomerUpdate()
    check("空构造成功", True)
    check("company_name None", update.company_name is None)
    check("contact_person None", update.contact_person is None)
    check("phone None", update.phone is None)
    check("email None", update.email is None)
    check("address None", update.address is None)
    check("remark None", update.remark is None)
except Exception as e:
    check("CustomerUpdate 空构造", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [12] CustomerUpdate — 部分字段
# ----------------------------------------------------------
print("\n[12] CustomerUpdate — 部分字段")
try:
    update = CustomerUpdate(
        company_name="更新公司名",
        phone="13700137000",
    )
    check("company_name", update.company_name == "更新公司名")
    check("phone", update.phone == "13700137000")
    check("contact_person None", update.contact_person is None)
except Exception as e:
    check("部分字段更新", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [13] CustomerResponse — from_attributes
# ----------------------------------------------------------
print("\n[13] CustomerResponse — from_attributes")
check(
    "ConfigDict from_attributes=True",
    CustomerResponse.model_config.get("from_attributes") is True,
)

# ----------------------------------------------------------
# [14] CustomerResponse — 字段数量
# ----------------------------------------------------------
print("\n[14] CustomerResponse — 字段数量")
fields = CustomerResponse.model_fields
field_names = set(fields.keys())
expected = {"id", "company_name", "contact_person", "phone", "email", "address", "remark", "created_at", "updated_at"}
check("字段数量 = 9", len(field_names) == 9)
check("字段名称正确", field_names == expected)

# ----------------------------------------------------------
# [15] CustomerResponse — 字段类型
# ----------------------------------------------------------
print("\n[15] CustomerResponse — 字段类型")
from datetime import datetime as dt

check("id 类型 int", fields["id"].annotation is int)
check("company_name 类型 str", fields["company_name"].annotation is str)
check("created_at 类型 datetime", fields["created_at"].annotation is dt)
check("updated_at 类型 datetime", fields["updated_at"].annotation is dt)

# ----------------------------------------------------------
# [16] CustomerResponse — 不含 password_hash
# ----------------------------------------------------------
print("\n[16] CustomerResponse — 不含内部字段")
check("不含 password_hash", "password_hash" not in field_names)
check("不含 created_by", "created_by" not in field_names)
check("不含 updated_by", "updated_by" not in field_names)
check("不含 is_deleted", "is_deleted" not in field_names)

# ----------------------------------------------------------
# [17] CustomerResponse — model_validate
# ----------------------------------------------------------
print("\n[17] CustomerResponse — model_validate")
try:
    data = {
        "id": 1,
        "company_name": "测试公司",
        "phone": "13800138000",
        "created_at": "2026-07-01T10:00:00",
        "updated_at": "2026-07-01T10:00:00",
    }
    resp = CustomerResponse.model_validate(data)
    check("id", resp.id == 1)
    check("company_name", resp.company_name == "测试公司")
    check("created_at 是 datetime", isinstance(resp.created_at, dt))
    check("updated_at 是 datetime", isinstance(resp.updated_at, dt))
    check("contact_person 默认 None", resp.contact_person is None)
except Exception as e:
    check("model_validate", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [18] CustomerResponse — model_dump
# ----------------------------------------------------------
print("\n[18] CustomerResponse — model_dump")
try:
    resp = CustomerResponse(
        id=1,
        company_name="测试公司",
        created_at=dt(2026, 7, 1, 10, 0, 0),
        updated_at=dt(2026, 7, 1, 10, 0, 0),
    )
    d = resp.model_dump()
    check("model_dump 返回 dict", isinstance(d, dict))
    check("id 在 dump 中", d["id"] == 1)
    check("company_name 在 dump 中", d["company_name"] == "测试公司")
    check("created_at 是 datetime", isinstance(d["created_at"], dt))
    check("contact_person None", d["contact_person"] is None)
except Exception as e:
    check("model_dump", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [19] CustomerResponse — model_dump(mode="json")
# ----------------------------------------------------------
print("\n[19] CustomerResponse — JSON 序列化")
try:
    resp = CustomerResponse(
        id=1,
        company_name="测试公司",
        created_at=dt(2026, 7, 1, 10, 0, 0),
        updated_at=dt(2026, 7, 1, 10, 0, 0),
    )
    d = resp.model_dump(mode="json")
    check("JSON dump 返回 dict", isinstance(d, dict))
    check("created_at 是字符串", isinstance(d["created_at"], str))
    check("updated_at 是字符串", isinstance(d["updated_at"], str))
    check("created_at 格式", d["created_at"] == "2026-07-01T10:00:00")
except Exception as e:
    check("JSON 序列化", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [20] CustomerResponse — json()
# ----------------------------------------------------------
print("\n[20] CustomerResponse — json()")
try:
    resp = CustomerResponse(
        id=1,
        company_name="测试公司",
        created_at=dt(2026, 7, 1, 10, 0, 0),
        updated_at=dt(2026, 7, 1, 10, 0, 0),
    )
    json_str = resp.model_dump_json()
    check("json 返回 str", isinstance(json_str, str))
    parsed = json.loads(json_str)
    check("json 可解析", parsed["id"] == 1)
    check("json company_name", parsed["company_name"] == "测试公司")
    check("json created_at", parsed["created_at"] == "2026-07-01T10:00:00")
except Exception as e:
    check("json()", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [21] CustomerListResponse
# ----------------------------------------------------------
print("\n[21] CustomerListResponse")
try:
    resp1 = CustomerResponse(
        id=1,
        company_name="公司A",
        created_at=dt(2026, 7, 1),
        updated_at=dt(2026, 7, 1),
    )
    resp2 = CustomerResponse(
        id=2,
        company_name="公司B",
        created_at=dt(2026, 7, 2),
        updated_at=dt(2026, 7, 2),
    )
    list_resp = CustomerListResponse(items=[resp1, resp2], total=2)
    check("items 长度", len(list_resp.items) == 2)
    check("total", list_resp.total == 2)
    check("items[0] 是 CustomerResponse", isinstance(list_resp.items[0], CustomerResponse))
    check("items[0].id", list_resp.items[0].id == 1)
    check("items[1].company_name", list_resp.items[1].company_name == "公司B")
except Exception as e:
    check("CustomerListResponse", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [22] CustomerListResponse — 空列表
# ----------------------------------------------------------
print("\n[22] CustomerListResponse — 空列表")
try:
    list_resp = CustomerListResponse(items=[], total=0)
    check("items 空列表", list_resp.items == [])
    check("total 0", list_resp.total == 0)
except Exception as e:
    check("空列表", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [23] Pydantic v2 检查
# ----------------------------------------------------------
print("\n[23] Pydantic v2 检查")
check("CustomerBase 是 BaseModel 子类", issubclass(CustomerBase, BaseModel))
check("CustomerResponse 有 model_config", hasattr(CustomerResponse, "model_config"))
check("CustomerResponse model_config 是 dict", isinstance(CustomerResponse.model_config, dict))
check("未使用 class Config", not hasattr(CustomerResponse, "Config"))

# 检查是否存在 class Config (orm_mode 旧写法)
import inspect
src = inspect.getsource(CustomerResponse)
check("不含 orm_mode", "orm_mode" not in src)
check("不含 class Config:", "class Config:" not in src)

# ----------------------------------------------------------
# [24] __all__
# ----------------------------------------------------------
print("\n[24] __all__")
from server.schemas import customer_schema as cs
check("__all__ 存在", hasattr(cs, "__all__"))
check("__all__ 包含 CustomerBase", "CustomerBase" in cs.__all__)
check("__all__ 包含 CustomerCreate", "CustomerCreate" in cs.__all__)
check("__all__ 包含 CustomerUpdate", "CustomerUpdate" in cs.__all__)
check("__all__ 包含 CustomerResponse", "CustomerResponse" in cs.__all__)
check("__all__ 包含 CustomerListResponse", "CustomerListResponse" in cs.__all__)
check("__all__ 长度 = 5", len(cs.__all__) == 5)

# ----------------------------------------------------------
# [25] 无循环导入
# ----------------------------------------------------------
print("\n[25] 无循环导入")
import ast
with open("server/schemas/customer_schema.py", "r", encoding="utf-8") as f:
    source = f.read()
tree = ast.parse(source)
imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
from_imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module]
all_imports = imports + [m for m in from_imports if m]
check("不导入 server.services", "server.services" not in str(all_imports))
check("不导入 server.routers", "server.routers" not in str(all_imports))
check("不导入 client", "client" not in str(all_imports))

# ----------------------------------------------------------
# [26] 禁止命名检查
# ----------------------------------------------------------
print("\n[26] 禁止命名检查")
src_lower = source.lower()
check("不含 ValidationException", "validationexception" not in src_lower)
check("不含 AuthorizationException", "authorizationexception" not in src_lower)
check("不含 ConflictException", "conflictexception" not in src_lower)
check("不含 print(", "print(" not in source)

# ----------------------------------------------------------
# [27] PEP8
# ----------------------------------------------------------
print("\n[27] PEP8")
check("文件以 docstring 开头", source.strip().startswith('"""'))
check("有 __all__", "__all__" in source)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 class Config:", "class Config:" not in source)

# ----------------------------------------------------------
# [28] 字段数量检查
# ----------------------------------------------------------
print("\n[28] 字段数量检查")
base_fields = CustomerBase.model_fields
create_fields = CustomerCreate.model_fields
update_fields = CustomerUpdate.model_fields
check("CustomerBase 字段数 = 6", len(base_fields) == 6)
check("CustomerCreate 字段数 = 6", len(create_fields) == 6)
check("CustomerUpdate 字段数 = 6", len(update_fields) == 6)

# ----------------------------------------------------------
# [29] CustomerUpdate 完全不传值
# ----------------------------------------------------------
print("\n[29] CustomerUpdate — 完全空")
try:
    update = CustomerUpdate()
    check("空实例化成功", True)
    dumped = update.model_dump()
    check("全部 None", all(v is None for v in dumped.values()))
except Exception as e:
    check("CustomerUpdate 空", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [30] CustomerResponse — 不含 ORM 内部对象
# ----------------------------------------------------------
print("\n[30] CustomerResponse — 不含 ORM 内部对象")
check("不含 _sa_instance_state", "_sa_instance_state" not in str(field_names))
check("不含 creator", "creator" not in field_names)
check("不含 tasks", "tasks" not in field_names)

# ============================================================
# 结果
# ============================================================
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  结果: ALL PASSED")
else:
    print("  结果: SOME FAILED")
print("=" * 60)

sys.exit(0 if FAILED == 0 else 1)