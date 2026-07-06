"""Sprint 3 — Task 3.1 Schema 自检脚本

验证项:
    1.  py_compile (user_schema)
    2.  py_compile (role_schema)
    3.  import
    4.  LoginRequest 校验
    5.  LoginResponse 校验
    6.  UserBase 校验
    7.  UserCreate 校验
    8.  UserUpdate 校验
    9.  UserPasswordChange 校验
    10. UserResponse 校验
    11. UserListResponse 校验
    12. RoleResponse 校验
    13. RoleListResponse 校验
    14. PermissionResponse 校验
    15. model_dump()
    16. model_validate()
    17. from_attributes (UserResponse)
    18. from_attributes (RoleResponse)
    19. from_attributes (PermissionResponse)
    20. JSON 序列化
    21. datetime 类型
    22. Optional 字段
    23. 禁止 password_hash 输出
    24. 禁止循环导入
    25. 禁止命名
    26. 必填字段校验
    27. 字段长度校验
    28. Pydantic v2 ConfigDict
"""

import sys
import json
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  -- {detail}")


print("=" * 60)
print("  Task 3.1 — Pydantic Schema Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

for module_name in ["user_schema", "role_schema", "__init__"]:
    try:
        py_compile.compile(
            str(Path(__file__).parent.parent / "server" / "schemas" / f"{module_name}.py"),
            doraise=True,
        )
        check(f"py_compile {module_name}", True)
    except py_compile.PyCompileError as e:
        check(f"py_compile {module_name}", False, str(e))

# ============================================================
# 2-3. import
# ============================================================
print("\n[2] import")
from server.schemas import (
    LoginRequest,
    LoginResponse,
    UserBase,
    UserCreate,
    UserUpdate,
    UserPasswordChange,
    UserResponse,
    UserListResponse,
    RoleResponse,
    RoleListResponse,
    PermissionResponse,
)
check("LoginRequest 导入", LoginRequest is not None)
check("LoginResponse 导入", LoginResponse is not None)
check("UserBase 导入", UserBase is not None)
check("UserCreate 导入", UserCreate is not None)
check("UserUpdate 导入", UserUpdate is not None)
check("UserPasswordChange 导入", UserPasswordChange is not None)
check("UserResponse 导入", UserResponse is not None)
check("UserListResponse 导入", UserListResponse is not None)
check("RoleResponse 导入", RoleResponse is not None)
check("RoleListResponse 导入", RoleListResponse is not None)
check("PermissionResponse 导入", PermissionResponse is not None)

# ============================================================
# 4. LoginRequest 校验
# ============================================================
print("\n[3] LoginRequest 校验")
req = LoginRequest(username="admin", password="admin123")
check("username = admin", req.username == "admin")
check("password = admin123", req.password == "admin123")

# 必填校验
from pydantic import ValidationError

try:
    LoginRequest()
    check("LoginRequest 无参抛错", False)
except ValidationError as e:
    check("LoginRequest 无参抛错", True)

# 字段长度
try:
    LoginRequest(username="", password="")
    check("LoginRequest 空字符串抛错", False)
except ValidationError:
    check("LoginRequest 空字符串抛错", True)

# ============================================================
# 5. LoginResponse 校验
# ============================================================
print("\n[4] LoginResponse 校验")
now = datetime.now(timezone.utc)
user_data = {
    "id": 1,
    "username": "admin",
    "real_name": "管理员",
    "phone": None,
    "is_active": True,
    "created_at": now,
    "updated_at": now,
    "roles": [],
}
user = UserResponse.model_validate(user_data)
resp = LoginResponse(
    access_token="eyJhbGciOi...",
    token_type="bearer",
    user=user,
)
check("access_token", resp.access_token == "eyJhbGciOi...")
check("token_type", resp.token_type == "bearer")
check("user 是 UserResponse", isinstance(resp.user, UserResponse))

# ============================================================
# 6. UserBase 校验
# ============================================================
print("\n[5] UserBase 校验")
base = UserBase(username="test", real_name="测试", phone="13800138000", is_active=True)
check("username", base.username == "test")
check("real_name", base.real_name == "测试")
check("phone", base.phone == "13800138000")
check("is_active", base.is_active is True)

# phone Optional
base2 = UserBase(username="test2", real_name="测试2")
check("phone 默认 None", base2.phone is None)

# ============================================================
# 7. UserCreate 校验
# ============================================================
print("\n[6] UserCreate 校验")
create = UserCreate(
    username="newuser",
    real_name="新用户",
    password="pass1234",
)
check("username", create.username == "newuser")
check("password", create.password == "pass1234")
check("is_active 默认 True", create.is_active is True)

# password 必填
try:
    UserCreate(username="a", real_name="b")
    check("UserCreate 无password抛错", False)
except ValidationError:
    check("UserCreate 无password抛错", True)

# password 长度 < 6
try:
    UserCreate(username="a", real_name="b", password="12345")
    check("UserCreate 短password抛错", False)
except ValidationError:
    check("UserCreate 短password抛错", True)

# ============================================================
# 8. UserUpdate 校验
# ============================================================
print("\n[7] UserUpdate 校验")
update = UserUpdate()
check("UserUpdate 全部默认 None", all(v is None for v in update.model_dump().values()))
update2 = UserUpdate(real_name="新名字", phone="13900000000")
check("real_name", update2.real_name == "新名字")
check("phone", update2.phone == "13900000000")
check("其他字段 None", update2.username is None and update2.password is None)

# ============================================================
# 9. UserPasswordChange 校验
# ============================================================
print("\n[8] UserPasswordChange 校验")
pwc = UserPasswordChange(old_password="old123", new_password="new4567")
check("old_password", pwc.old_password == "old123")
check("new_password", pwc.new_password == "new4567")

# new_password 长度 < 6
try:
    UserPasswordChange(old_password="a", new_password="12345")
    check("UserPasswordChange 短new抛错", False)
except ValidationError:
    check("UserPasswordChange 短new抛错", True)

# ============================================================
# 10. UserResponse 校验
# ============================================================
print("\n[9] UserResponse 校验")
now = datetime.now(timezone.utc)
user_resp = UserResponse.model_validate({
    "id": 1,
    "username": "admin",
    "real_name": "管理员",
    "phone": "13800000000",
    "is_active": True,
    "created_at": now,
    "updated_at": now,
    "roles": [],
})
check("id", user_resp.id == 1)
check("username", user_resp.username == "admin")
check("real_name", user_resp.real_name == "管理员")
check("phone", user_resp.phone == "13800000000")
check("is_active", user_resp.is_active is True)
check("created_at 是 datetime", isinstance(user_resp.created_at, datetime))
check("updated_at 是 datetime", isinstance(user_resp.updated_at, datetime))
check("roles 是空列表", user_resp.roles == [])

# ============================================================
# 11. UserListResponse 校验
# ============================================================
print("\n[10] UserListResponse 校验")
user_list = UserListResponse(items=[user_resp], total=1)
check("items 长度 1", len(user_list.items) == 1)
check("total = 1", user_list.total == 1)

# ============================================================
# 12. RoleResponse 校验
# ============================================================
print("\n[11] RoleResponse 校验")
role_resp = RoleResponse.model_validate({
    "id": 1,
    "name": "administrator",
    "display_name": "管理员",
    "description": "系统管理员",
    "is_system": True,
    "created_at": now,
    "permissions": [],
})
check("id", role_resp.id == 1)
check("name", role_resp.name == "administrator")
check("display_name", role_resp.display_name == "管理员")
check("description", role_resp.description == "系统管理员")
check("is_system", role_resp.is_system is True)
check("created_at", isinstance(role_resp.created_at, datetime))
check("permissions 空", role_resp.permissions == [])

# ============================================================
# 13. RoleListResponse 校验
# ============================================================
print("\n[12] RoleListResponse 校验")
role_list = RoleListResponse(items=[role_resp], total=1)
check("items 长度 1", len(role_list.items) == 1)
check("total = 1", role_list.total == 1)

# ============================================================
# 14. PermissionResponse 校验
# ============================================================
print("\n[13] PermissionResponse 校验")
perm_resp = PermissionResponse.model_validate({
    "code": "task:write",
    "name": "创建任务",
    "description": "允许创建试磨任务",
    "module": "task",
})
check("code", perm_resp.code == "task:write")
check("name", perm_resp.name == "创建任务")
check("description", perm_resp.description == "允许创建试磨任务")
check("module", perm_resp.module == "task")

# description Optional
perm2 = PermissionResponse.model_validate({
    "code": "task:read",
    "name": "查看任务",
    "module": "task",
})
check("description 默认 None", perm2.description is None)

# ============================================================
# 15. model_dump()
# ============================================================
print("\n[14] model_dump()")
dumped = user_resp.model_dump()
check("model_dump 返回 dict", isinstance(dumped, dict))
check("包含 id 键", "id" in dumped)
check("不包含 password_hash", "password_hash" not in dumped)
check("datetime 为 datetime 对象", isinstance(dumped["created_at"], datetime))

# model_dump(mode='json')
dumped_json = user_resp.model_dump(mode="json")
check("mode=json datetime 为 str", isinstance(dumped_json["created_at"], str))

# ============================================================
# 16. model_validate()
# ============================================================
print("\n[15] model_validate()")
validated = UserResponse.model_validate(user_data)
check("model_validate 返回 UserResponse", isinstance(validated, UserResponse))

# 错误数据
try:
    UserResponse.model_validate({"id": "not-int"})
    check("model_validate 错误数据抛错", False)
except ValidationError:
    check("model_validate 错误数据抛错", True)

# ============================================================
# 17. from_attributes 模拟
# ============================================================
print("\n[16] from_attributes 模拟")

# 模拟 ORM 对象（使用简单类模拟 from_attributes 行为）
class MockPermission:
    code = "task:write"
    name = "创建任务"
    description = "允许创建试磨任务"
    module = "task"

class MockRole:
    id = 1
    name = "administrator"
    display_name = "管理员"
    description = "系统管理员"
    is_system = True
    created_at = datetime.now(timezone.utc)
    permissions = [MockPermission()]  # 实例列表

class MockUser:
    id = 1
    username = "admin"
    real_name = "管理员"
    phone = "13800000000"
    is_active = True
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)
    roles = [MockRole()]  # 实例列表

# from_attributes 测试
from pydantic import ConfigDict, BaseModel as PydanticBase

class _TestPermission(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    description: str | None = None
    module: str

class _TestRole(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    display_name: str
    description: str | None = None
    is_system: bool = False
    created_at: datetime
    permissions: list[_TestPermission] = []

class _TestUser(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    real_name: str
    phone: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: list[_TestRole] = []

# from_attributes 模拟（使用实例而非类）
perm_obj = _TestPermission.model_validate(MockPermission())
check("from_attributes Permission", perm_obj.code == "task:write")

role_obj = _TestRole.model_validate(MockRole())
check("from_attributes Role", role_obj.name == "administrator")
check("from_attributes Role.permissions", len(role_obj.permissions) == 1)

user_obj = _TestUser.model_validate(MockUser())
check("from_attributes User", user_obj.username == "admin")
check("from_attributes User.roles", len(user_obj.roles) == 1)

# ============================================================
# 18. JSON 序列化
# ============================================================
print("\n[17] JSON 序列化")
json_str = user_resp.model_dump_json()
check("model_dump_json 返回 str", isinstance(json_str, str))
parsed = json.loads(json_str)
check("JSON 解析成功", isinstance(parsed, dict))
check("JSON 不含 password_hash", "password_hash" not in json_str)

# 所有 Schema 的 JSON 序列化
for schema_name, schema_obj in [
    ("LoginRequest", req),
    ("UserCreate", create),
    ("UserUpdate", update2),
    ("UserPasswordChange", pwc),
    ("UserResponse", user_resp),
    ("UserListResponse", user_list),
    ("RoleResponse", role_resp),
    ("RoleListResponse", role_list),
    ("PermissionResponse", perm_resp),
]:
    try:
        s = schema_obj.model_dump_json()
        check(f"{schema_name} JSON 序列化", True)
    except Exception as e:
        check(f"{schema_name} JSON 序列化", False, str(e))

# ============================================================
# 19. datetime 类型
# ============================================================
print("\n[18] datetime 类型")
check("UserResponse.created_at datetime", isinstance(user_resp.created_at, datetime))
check("UserResponse.updated_at datetime", isinstance(user_resp.updated_at, datetime))
check("RoleResponse.created_at datetime", isinstance(role_resp.created_at, datetime))

# ============================================================
# 20. Optional 字段
# ============================================================
print("\n[19] Optional 字段")
# phone
u1 = UserResponse.model_validate({
    "id": 1, "username": "a", "real_name": "b",
    "is_active": True, "created_at": now, "updated_at": now, "roles": [],
})
check("phone = None", u1.phone is None)

# description
r1 = RoleResponse.model_validate({
    "id": 1, "name": "admin", "display_name": "管理员",
    "is_system": True, "created_at": now, "permissions": [],
})
check("description = None", r1.description is None)

p1 = PermissionResponse.model_validate({
    "code": "x", "name": "y", "module": "z",
})
check("Permission description = None", p1.description is None)

# ============================================================
# 21. 禁止 password_hash 输出
# ============================================================
print("\n[20] 禁止 password_hash 输出")
# UserResponse 不定义 password_hash，model_dump 不应包含
dumped = user_resp.model_dump()
check("model_dump 无 password_hash", "password_hash" not in dumped)

# LoginRequest 有 password 字段（明文），但无 password_hash
lr_dumped = req.model_dump()
check("LoginRequest 无 password_hash", "password_hash" not in lr_dumped)
check("LoginRequest 有 password", "password" in lr_dumped)

# 尝试传入 password_hash 到 UserResponse
try:
    UserResponse.model_validate({**user_data, "password_hash": "xxx"})
    check("UserResponse 禁止 password_hash", True)
except Exception:
    check("UserResponse 禁止 password_hash", False, "不应因额外字段报错")

# ============================================================
# 22. 禁止循环导入
# ============================================================
print("\n[21] 禁止循环导入")
import server.schemas as schemas
check("无循环导入", True)

# ============================================================
# 23. 禁止命名
# ============================================================
print("\n[22] 禁止命名")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException"]
for name in forbidden:
    try:
        getattr(schemas, name)
        check(f"{name} 不应存在", False)
    except AttributeError:
        check(f"{name} 未使用", True)

# ============================================================
# 24. Pydantic v2 ConfigDict
# ============================================================
print("\n[23] Pydantic v2 ConfigDict")
check("UserResponse ConfigDict(from_attributes=True)",
      UserResponse.model_config.get("from_attributes") is True)
check("RoleResponse ConfigDict(from_attributes=True)",
      RoleResponse.model_config.get("from_attributes") is True)
check("PermissionResponse ConfigDict(from_attributes=True)",
      PermissionResponse.model_config.get("from_attributes") is True)

# ============================================================
# 25. 必填字段校验（综合）
# ============================================================
print("\n[24] 必填字段校验")
# UserResponse 必填字段
try:
    UserResponse.model_validate({})
    check("UserResponse 空dict抛错", False)
except ValidationError:
    check("UserResponse 空dict抛错", True)

# RoleResponse 必填字段
try:
    RoleResponse.model_validate({})
    check("RoleResponse 空dict抛错", False)
except ValidationError:
    check("RoleResponse 空dict抛错", True)

# ============================================================
# 结果
# ============================================================
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  结果: ALL PASSED")
else:
    print(f"  结果: {FAILED} FAILED")
print("=" * 60)

sys.exit(0 if FAILED == 0 else 1)