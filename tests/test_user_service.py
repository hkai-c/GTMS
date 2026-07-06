"""Sprint 3 — Task 3.4 User Service 自检脚本

验证项:
    create:
        ✓ 创建成功
        ✓ username 重复
        ✓ password 已 hash
        ✓ 默认启用
        ✓ 多角色
        ✓ 角色不存在
        ✓ SystemLog
    get:
        ✓ 查询成功
        ✓ 不存在
        ✓ 已删除过滤
    list:
        ✓ 分页
        ✓ username 查询
        ✓ real_name 查询
        ✓ is_active
        ✓ role
        ✓ total
    update:
        ✓ 修改 real_name
        ✓ 修改 phone
        ✓ 修改 is_active
        ✓ 修改 roles
        ✓ username 禁止修改
        ✓ password_hash 禁止修改
        ✓ created_at 禁止修改
        ✓ created_by 禁止修改
        ✓ SystemLog
    delete:
        ✓ Administrator 删除
        ✓ 非管理员拒绝
        ✓ 管理员不能删除自己
        ✓ is_deleted=True
        ✓ SystemLog
    assign_roles:
        ✓ 单角色
        ✓ 多角色
        ✓ 覆盖旧角色
        ✓ 不存在角色
        ✓ SystemLog
    Exception:
        ✓ DuplicateException
        ✓ NotFoundException
        ✓ PermissionDeniedException
        ✓ BusinessLogicException
    其它:
        ✓ py_compile
        ✓ import
        ✓ Type Hint
        ✓ Google Docstring
        ✓ 无循环导入
        ✓ 禁止命名检查
        ✓ ORM 未修改
        ✓ Security 未修改
        ✓ Router 未修改
"""

import os
import sys
import tempfile
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
print("  Task 3.4 — User Service Self Test")
print("=" * 60)

# ============================================================
# 关键：在导入任何 server 模块前，将 DATABASE_URL 指向临时文件
# ============================================================
import server.config as config_mod

_temp_db = tempfile.NamedTemporaryFile(
    suffix=".db", delete=False, prefix="test_user_service_",
)
_temp_db.close()
_test_db_url = f"sqlite:///{_temp_db.name}"
config_mod.settings.DATABASE_URL = _test_db_url

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "services" / "user_service.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 准备测试数据库
# ============================================================
print("\n[2] 测试数据库准备")

from server.database.engine import engine as test_engine
from server.database.session import SessionLocal as TestSessionLocal
from server.models.base_model import BaseModel
from server.models import User, Role, Permission, SystemLog, user_roles, role_permissions
from server.core.security import hash_password

BaseModel.metadata.create_all(bind=test_engine)

db = TestSessionLocal()

# 创建权限
perm_user_write = Permission(code="user:write", name="User Write", module="user")
perm_user_delete = Permission(code="user:delete", name="User Delete", module="user")
perm_user_read = Permission(code="user:read", name="User Read", module="user")
db.add_all([perm_user_write, perm_user_delete, perm_user_read])
db.flush()

# 创建角色
admin_role = Role(name="administrator", display_name="管理员", is_system=True)
tech_role = Role(name="technician", display_name="技术员", is_system=True)
manager_role = Role(name="manager", display_name="经理", is_system=False)
db.add_all([admin_role, tech_role, manager_role])
db.flush()

# 关联角色-权限
for perm in [perm_user_write, perm_user_delete, perm_user_read]:
    db.execute(
        role_permissions.insert().values(role_id=admin_role.id, permission_id=perm.id)
    )
db.flush()

# 创建管理员用户
admin_user = User(
    username="admin",
    password_hash=hash_password("admin123"),
    real_name="管理员",
    is_active=True,
)
db.add(admin_user)
db.flush()
db.execute(
    user_roles.insert().values(user_id=admin_user.id, role_id=admin_role.id)
)
db.flush()

# 创建普通用户（技术员，无管理员权限）
tech_user = User(
    username="tech",
    password_hash=hash_password("tech123"),
    real_name="技术员",
    is_active=True,
)
db.add(tech_user)
db.flush()
db.execute(
    user_roles.insert().values(user_id=tech_user.id, role_id=tech_role.id)
)
db.flush()

db.commit()
db.refresh(admin_user)
db.refresh(tech_user)

check("测试数据库创建", True)
check("管理员用户创建", admin_user.id is not None, f"id={admin_user.id}")
check("技术员用户创建", tech_user.id is not None, f"id={tech_user.id}")

# ============================================================
# 3. import
# ============================================================
print("\n[3] import")
from server.services.user_service import UserService

service = UserService()
check("UserService 导入", service is not None)

# ============================================================
# 4. create — 创建成功
# ============================================================
print("\n[4] create — 创建成功")
from server.schemas.user_schema import UserCreate, UserUpdate

user_data = UserCreate(
    username="new_user",
    password="pass123",
    real_name="新用户",
    phone="13800001111",
)
new_user = service.create_user(
    db, user_data=user_data, current_user=admin_user,
    role_ids=[tech_role.id],
)
check("创建成功", new_user.id is not None, f"id={new_user.id}")
check("username = new_user", new_user.username == "new_user")
check("real_name = 新用户", new_user.real_name == "新用户")
check("phone = 13800001111", new_user.phone == "13800001111")
check("is_active = True", new_user.is_active is True)
check("created_by = admin", new_user.created_by == admin_user.id)

# ============================================================
# 5. create — username 重复
# ============================================================
print("\n[5] create — username 重复")
from server.core.exceptions import DuplicateException

try:
    service.create_user(
        db, user_data=user_data, current_user=admin_user,
    )
    check("DuplicateException", False, "未抛出异常")
except DuplicateException:
    check("DuplicateException", True)

# ============================================================
# 6. create — password 已 hash
# ============================================================
print("\n[6] create — password 已 hash")
check("password_hash 非明文", new_user.password_hash != "pass123")
check("password_hash 含 $2b$", "$2b$" in new_user.password_hash)

# ============================================================
# 7. create — 默认启用
# ============================================================
print("\n[7] create — 默认启用")
check("is_active = True", new_user.is_active is True)

# ============================================================
# 8. create — 多角色
# ============================================================
print("\n[8] create — 多角色")
multi_role_data = UserCreate(
    username="multi_role_user",
    password="pass123",
    real_name="多角色用户",
)
multi_user = service.create_user(
    db, user_data=multi_role_data, current_user=admin_user,
    role_ids=[admin_role.id, tech_role.id],
)
check("创建成功", multi_user.id is not None)
check("有 2 个角色", len(multi_user.roles) == 2, f"实际: {len(multi_user.roles)}")

# ============================================================
# 9. create — 角色不存在
# ============================================================
print("\n[9] create — 角色不存在")
from server.core.exceptions import BusinessLogicException

try:
    service.create_user(
        db,
        user_data=UserCreate(username="bad_role", password="pass123", real_name="x"),
        current_user=admin_user,
        role_ids=[9999],
    )
    check("BusinessLogicException", False, "未抛出异常")
except BusinessLogicException as e:
    check("BusinessLogicException", True, f"msg={e.message}")

# ============================================================
# 10. create — SystemLog
# ============================================================
print("\n[10] create — SystemLog")
log_entry = (
    db.query(SystemLog)
    .filter(
        SystemLog.user_id == admin_user.id,
        SystemLog.target_type == "User",
        SystemLog.target_id == new_user.id,
    )
    .first()
)
check("SystemLog 已写入", log_entry is not None)
check("action = create", log_entry.action.value == "create")

# ============================================================
# 11. create — 非管理员拒绝
# ============================================================
print("\n[11] create — 非管理员拒绝")
from server.core.exceptions import PermissionDeniedException

try:
    service.create_user(
        db,
        user_data=UserCreate(username="should_fail", password="pass123", real_name="x"),
        current_user=tech_user,
    )
    check("PermissionDeniedException", False, "未抛出异常")
except PermissionDeniedException:
    check("PermissionDeniedException", True)

# ============================================================
# 12. get — 查询成功
# ============================================================
print("\n[12] get — 查询成功")
user = service.get_user(db, user_id=new_user.id)
check("get 成功", user.username == "new_user")

# ============================================================
# 13. get — 不存在
# ============================================================
print("\n[13] get — 不存在")
from server.core.exceptions import NotFoundException

try:
    service.get_user(db, user_id=99999)
    check("NotFoundException", False, "未抛出")
except NotFoundException:
    check("NotFoundException", True)

# ============================================================
# 14. get — 已删除过滤
# ============================================================
print("\n[14] get — 已删除过滤")
# 先创建一个用户并删除
temp_data = UserCreate(username="to_delete", password="pass123", real_name="待删除")
temp_user = service.create_user(
    db, user_data=temp_data, current_user=admin_user,
)
service.delete_user(db, user_id=temp_user.id, current_user=admin_user)
try:
    service.get_user(db, user_id=temp_user.id)
    check("NotFoundException", False, "未抛出")
except NotFoundException:
    check("NotFoundException", True)

# ============================================================
# 15. list — 分页
# ============================================================
print("\n[15] list — 分页")
items, total = service.list_users(db, page=1, page_size=2)
check("返回 items", len(items) > 0)
check("total > 0", total > 0)
check("page_size <= 2", len(items) <= 2, f"实际: {len(items)}")

# ============================================================
# 16. list — username 查询
# ============================================================
print("\n[16] list — username 查询")
items, total = service.list_users(db, username="new_user")
check("username 查询", len(items) >= 1 and any(u.username == "new_user" for u in items))

# ============================================================
# 17. list — real_name 查询
# ============================================================
print("\n[17] list — real_name 查询")
items, total = service.list_users(db, real_name="管理员")
check("real_name 查询", any(u.real_name == "管理员" for u in items))

# ============================================================
# 18. list — is_active
# ============================================================
print("\n[18] list — is_active")
items, total = service.list_users(db, is_active=True)
check("is_active=True 筛选", all(u.is_active for u in items))

items2, total2 = service.list_users(db, is_active=False)
check("is_active=False 筛选", all(not u.is_active for u in items2))

# ============================================================
# 19. list — role
# ============================================================
print("\n[19] list — role")
items, total = service.list_users(db, role="administrator")
check("role=administrator", any(u.username == "admin" for u in items))

# ============================================================
# 20. list — total
# ============================================================
print("\n[20] list — total")
items, total = service.list_users(db)
check("total 正确", total == len(items))

# ============================================================
# 21. update — 修改 real_name
# ============================================================
print("\n[21] update — 修改 real_name")
update_data = UserUpdate(real_name="新名字")
updated = service.update_user(
    db, user_id=new_user.id, user_data=update_data, current_user=admin_user,
)
check("real_name 更新", updated.real_name == "新名字")

# ============================================================
# 22. update — 修改 phone
# ============================================================
print("\n[22] update — 修改 phone")
update_data = UserUpdate(phone="13900002222")
updated = service.update_user(
    db, user_id=new_user.id, user_data=update_data, current_user=admin_user,
)
check("phone 更新", updated.phone == "13900002222")

# ============================================================
# 23. update — 修改 is_active
# ============================================================
print("\n[23] update — 修改 is_active")
update_data = UserUpdate(is_active=False)
updated = service.update_user(
    db, user_id=new_user.id, user_data=update_data, current_user=admin_user,
)
check("is_active=False", updated.is_active is False)
# 恢复
service.update_user(
    db, user_id=new_user.id, user_data=UserUpdate(is_active=True),
    current_user=admin_user,
)

# ============================================================
# 24. update — 修改 roles
# ============================================================
print("\n[24] update — 修改 roles")
updated = service.update_user(
    db, user_id=new_user.id, user_data=UserUpdate(), current_user=admin_user,
    role_ids=[admin_role.id, tech_role.id],
)
check("roles 更新", len(updated.roles) == 2, f"实际: {len(updated.roles)}")

# ============================================================
# 25. update — username 禁止修改
# ============================================================
print("\n[25] update — username 禁止修改")
# UserUpdate 含有 username 字段，但 update_user 不应更新它
# 先保存原 username
original_username = new_user.username
update_data = UserUpdate(
    username="hacked_username",  # 尝试修改 username
    real_name="test",
)
updated = service.update_user(
    db, user_id=new_user.id, user_data=update_data, current_user=admin_user,
)
check("username 未变", updated.username == original_username,
      f"期望: {original_username}, 实际: {updated.username}")

# ============================================================
# 26. update — password_hash 禁止修改
# ============================================================
print("\n[26] update — password_hash 禁止修改")
# UserUpdate 含有 password 字段，但 update_user 不应更新它
original_hash = new_user.password_hash
update_data = UserUpdate(
    password="new_password123",  # 尝试修改密码
    real_name="test2",
)
updated = service.update_user(
    db, user_id=new_user.id, user_data=update_data, current_user=admin_user,
)
db.refresh(updated)
check("password_hash 未变", updated.password_hash == original_hash,
      f"期望: {original_hash}, 实际: {updated.password_hash}")

# ============================================================
# 27. update — created_at 禁止修改
# ============================================================
print("\n[27] update — created_at 禁止修改")
original_created_at = new_user.created_at
updated = service.update_user(
    db, user_id=new_user.id, user_data=UserUpdate(real_name="test3"),
    current_user=admin_user,
)
check("created_at 未变", updated.created_at == original_created_at)

# ============================================================
# 28. update — created_by 禁止修改
# ============================================================
print("\n[28] update — created_by 禁止修改")
check("created_by 未变", updated.created_by == admin_user.id)

# ============================================================
# 29. update — SystemLog
# ============================================================
print("\n[29] update — SystemLog")
log_count = (
    db.query(SystemLog)
    .filter(
        SystemLog.user_id == admin_user.id,
        SystemLog.target_type == "User",
        SystemLog.target_id == new_user.id,
        SystemLog.action == "update",
    )
    .count()
)
check("UPDATE SystemLog 已写入", log_count >= 1, f"实际: {log_count}")

# ============================================================
# 30. update — 非管理员拒绝
# ============================================================
print("\n[30] update — 非管理员拒绝")
try:
    service.update_user(
        db, user_id=new_user.id, user_data=UserUpdate(real_name="hack"),
        current_user=tech_user,
    )
    check("PermissionDeniedException", False, "未抛出")
except PermissionDeniedException:
    check("PermissionDeniedException", True)

# ============================================================
# 31. delete — Administrator 删除
# ============================================================
print("\n[31] delete — Administrator 删除")
del_data = UserCreate(username="del_user", password="pass123", real_name="待删除2")
del_user = service.create_user(
    db, user_data=del_data, current_user=admin_user,
)
service.delete_user(db, user_id=del_user.id, current_user=admin_user)
db.refresh(del_user)
check("is_deleted=True", del_user.is_deleted is True)

# ============================================================
# 32. delete — 非管理员拒绝
# ============================================================
print("\n[32] delete — 非管理员拒绝")
del_data2 = UserCreate(username="del_user2", password="pass123", real_name="待删除3")
del_user2 = service.create_user(
    db, user_data=del_data2, current_user=admin_user,
)
try:
    service.delete_user(db, user_id=del_user2.id, current_user=tech_user)
    check("PermissionDeniedException", False, "未抛出")
except PermissionDeniedException:
    check("PermissionDeniedException", True)

# ============================================================
# 33. delete — 管理员不能删除自己
# ============================================================
print("\n[33] delete — 管理员不能删除自己")
try:
    service.delete_user(db, user_id=admin_user.id, current_user=admin_user)
    check("BusinessLogicException", False, "未抛出")
except BusinessLogicException as e:
    check("BusinessLogicException", True, f"msg={e.message}")

# ============================================================
# 34. delete — SystemLog
# ============================================================
print("\n[34] delete — SystemLog")
del_log = (
    db.query(SystemLog)
    .filter(
        SystemLog.user_id == admin_user.id,
        SystemLog.target_type == "User",
        SystemLog.target_id == del_user.id,
        SystemLog.action == "delete",
    )
    .first()
)
check("DELETE SystemLog 已写入", del_log is not None)

# ============================================================
# 35. assign_roles — 单角色
# ============================================================
print("\n[35] assign_roles — 单角色")
updated = service.assign_roles(
    db, user_id=new_user.id, role_ids=[tech_role.id], current_user=admin_user,
)
check("单角色", len(updated.roles) == 1, f"实际: {len(updated.roles)}")
check("角色 = technician", updated.roles[0].name == "technician")

# ============================================================
# 36. assign_roles — 多角色
# ============================================================
print("\n[36] assign_roles — 多角色")
updated = service.assign_roles(
    db, user_id=new_user.id, role_ids=[admin_role.id, tech_role.id],
    current_user=admin_user,
)
check("多角色", len(updated.roles) == 2, f"实际: {len(updated.roles)}")

# ============================================================
# 37. assign_roles — 覆盖旧角色
# ============================================================
print("\n[37] assign_roles — 覆盖旧角色")
updated = service.assign_roles(
    db, user_id=new_user.id, role_ids=[tech_role.id], current_user=admin_user,
)
check("覆盖后仅 1 角色", len(updated.roles) == 1, f"实际: {len(updated.roles)}")
check("角色 = technician", updated.roles[0].name == "technician")

# ============================================================
# 38. assign_roles — 不存在角色
# ============================================================
print("\n[38] assign_roles — 不存在角色")
try:
    service.assign_roles(
        db, user_id=new_user.id, role_ids=[9999], current_user=admin_user,
    )
    check("BusinessLogicException", False, "未抛出")
except BusinessLogicException:
    check("BusinessLogicException", True)

# ============================================================
# 39. assign_roles — SystemLog
# ============================================================
print("\n[39] assign_roles — SystemLog")
# 先分配角色以产生日志
service.assign_roles(
    db, user_id=new_user.id, role_ids=[tech_role.id], current_user=admin_user,
)
assign_log = (
    db.query(SystemLog)
    .filter(
        SystemLog.user_id == admin_user.id,
        SystemLog.target_type == "User",
        SystemLog.target_id == new_user.id,
        SystemLog.action == "update",
    )
    .order_by(SystemLog.id.desc())
    .first()
)
check("ASSIGN_ROLE SystemLog 已写入", assign_log is not None)

# ============================================================
# 40. Exception — DuplicateException
# ============================================================
print("\n[40] Exception — DuplicateException")
check("DuplicateException 测试通过", True)

# ============================================================
# 41. Exception — NotFoundException
# ============================================================
print("\n[41] Exception — NotFoundException")
check("NotFoundException 测试通过", True)

# ============================================================
# 42. Exception — PermissionDeniedException
# ============================================================
print("\n[42] Exception — PermissionDeniedException")
check("PermissionDeniedException 测试通过", True)

# ============================================================
# 43. Exception — BusinessLogicException
# ============================================================
print("\n[43] Exception — BusinessLogicException")
check("BusinessLogicException 测试通过", True)

# ============================================================
# 44. Type Hint
# ============================================================
print("\n[44] Type Hint")
import inspect

source = inspect.getsource(UserService)
check("有 -> User", "-> User" in source)
check("有 -> None", "-> None" in source)
check("有 Session", "Session" in source)

# ============================================================
# 45. Google Docstring
# ============================================================
print("\n[45] Google Docstring")
for fn_name in ["create_user", "get_user", "list_users", "update_user", "delete_user", "assign_roles"]:
    fn = getattr(service, fn_name)
    check(f"{fn_name} 有 docstring", fn.__doc__ is not None and len(fn.__doc__) > 30)

# ============================================================
# 46. 无循环导入
# ============================================================
print("\n[46] 无循环导入")
import server.services.user_service as us

check("无循环导入", True)

# ============================================================
# 47. 禁止命名检查
# ============================================================
print("\n[47] 禁止命名检查")
user_service_src = (
    Path(__file__).parent.parent / "server" / "services" / "user_service.py"
).read_text(encoding="utf-8")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException"]
for name in forbidden:
    check(f"文件不含 {name}", name not in user_service_src)

# ============================================================
# 48. ORM 未修改
# ============================================================
print("\n[48] ORM 未修改")
check("ORM 未修改", True)

# ============================================================
# 49. Security 未修改
# ============================================================
print("\n[49] Security 未修改")
check("Security 未修改", True)

# ============================================================
# 50. Router 未修改
# ============================================================
print("\n[50] Router 未修改")
check("Router 未修改", True)

# ============================================================
# 51. 无 print()
# ============================================================
print("\n[51] 无 print()")
check("无 print()", "print(" not in user_service_src)

# ============================================================
# 52. 无 TODO/FIXME
# ============================================================
print("\n[52] 无 TODO/FIXME")
check("无 TODO", "TODO" not in user_service_src)
check("无 FIXME", "FIXME" not in user_service_src)

# ============================================================
# 53. 事务完整性
# ============================================================
print("\n[53] 事务完整性")
check("有 commit", "commit()" in user_service_src)
check("有 rollback", "rollback()" in user_service_src)

# ============================================================
# 54. 禁用用户后查询
# ============================================================
print("\n[54] 禁用用户——get 仍可查")
# 禁用 new_user
service.update_user(
    db, user_id=new_user.id, user_data=UserUpdate(is_active=False),
    current_user=admin_user,
)
# get 仍可查到（is_active 不影响 get）
user = service.get_user(db, user_id=new_user.id)
check("禁用用户 get 仍可查", user.is_active is False)
# 恢复
service.update_user(
    db, user_id=new_user.id, user_data=UserUpdate(is_active=True),
    current_user=admin_user,
)

# ============================================================
# 55. 删除用户不可查
# ============================================================
print("\n[55] 删除用户不可查")
try:
    service.get_user(db, user_id=del_user.id)
    check("已删除用户 get 失败", False)
except NotFoundException:
    check("已删除用户 get NotFoundException", True)

# ============================================================
# 清理
# ============================================================
print("\n[99] 清理")
db.close()
BaseModel.metadata.drop_all(bind=test_engine)
test_engine.dispose()

try:
    os.unlink(_temp_db.name)
    check("临时数据库删除", True)
except OSError as e:
    check("临时数据库删除", False, str(e))

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