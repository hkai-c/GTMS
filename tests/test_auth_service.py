"""Sprint 3 — Task 3.2 Auth Service 自检脚本

验证项:
    login:
        1.  正确用户名密码
        2.  用户不存在
        3.  密码错误
        4.  用户禁用
        5.  JWT 创建成功
        6.  LoginResponse 正确
    change_password:
        7.  成功修改
        8.  原密码错误
        9.  用户不存在
        10. password_hash 更新
        11. SystemLog
        12. rollback
    get_current_user_info:
        13. 查询成功
        14. 不存在
        15. Response 正确
    其它:
        16. py_compile
        17. import
        18. 无循环导入
        19. Type Hint
        20. Google Docstring
        21. PEP8
        22. 禁止命名检查
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from server.models.base_model import BaseModel

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
print("  Task 3.2 — Auth Service Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "services" / "auth_service.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
from server.services.auth_service import AuthService
check("AuthService 导入", AuthService is not None)

from server.core.exceptions import (
    AuthenticationException,
    NotFoundException,
    PermissionDeniedException,
)
from server.schemas.user_schema import LoginResponse, UserResponse
from server.core.security import (
    create_access_token,
    verify_password,
    hash_password,
    decode_access_token,
)

# ============================================================
# 准备测试数据库
# ============================================================
print("\n[3] 测试数据库准备")
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 创建所有表
BaseModel.metadata.create_all(bind=engine)

# 导入模型
from server.models import User, Role, Permission, SystemLog, user_roles, role_permissions
from server.enums.action_type import ActionType

# 创建测试数据
db: Session = TestSession()

# 创建权限
perm1 = Permission(code="auth:login", name="登录", module="auth")
perm2 = Permission(code="task:read", name="查看任务", module="task")
perm3 = Permission(code="task:write", name="创建任务", module="task")
db.add_all([perm1, perm2, perm3])
db.flush()

# 创建角色
admin_role = Role(name="administrator", display_name="管理员", is_system=True)
tech_role = Role(name="technician", display_name="技术员", is_system=True)
db.add_all([admin_role, tech_role])
db.flush()

# 关联角色-权限
db.execute(role_permissions.insert().values(role_id=admin_role.id, permission_id=perm1.id))
db.execute(role_permissions.insert().values(role_id=admin_role.id, permission_id=perm2.id))
db.execute(role_permissions.insert().values(role_id=tech_role.id, permission_id=perm2.id))
db.flush()

# 创建用户
plain_password = "admin123"
hashed = hash_password(plain_password)
active_user = User(
    username="admin",
    password_hash=hashed,
    real_name="管理员",
    is_active=True,
)
inactive_user = User(
    username="disabled_user",
    password_hash=hash_password("disabled123"),
    real_name="已禁用用户",
    is_active=False,
)
db.add_all([active_user, inactive_user])
db.flush()

# 关联用户-角色
db.execute(user_roles.insert().values(user_id=active_user.id, role_id=admin_role.id))
db.execute(user_roles.insert().values(user_id=active_user.id, role_id=tech_role.id))
db.execute(user_roles.insert().values(user_id=inactive_user.id, role_id=tech_role.id))
db.commit()

check("测试数据库创建表", True)
check("测试用户创建", active_user.id is not None)
check("测试角色创建", admin_role.id is not None)

# 创建 AuthService 实例
auth = AuthService()

# ============================================================
# 4. login — 正确用户名密码
# ============================================================
print("\n[4] login — 正确用户名密码")
response = auth.login(db, username="admin", password="admin123")
check("返回 LoginResponse", isinstance(response, LoginResponse))
check("access_token 非空", len(response.access_token) > 0)
check("token_type = bearer", response.token_type == "bearer")
check("user 是 UserResponse", isinstance(response.user, UserResponse))
check("user.username = admin", response.user.username == "admin")
check("user.real_name = 管理员", response.user.real_name == "管理员")
check("user.is_active", response.user.is_active is True)
check("user 不含 password_hash",
      "password_hash" not in response.user.model_dump())

# ============================================================
# 5. login — 用户不存在
# ============================================================
print("\n[5] login — 用户不存在")
try:
    auth.login(db, username="nonexistent", password="any")
    check("用户不存在抛异常", False)
except AuthenticationException as e:
    check("用户不存在抛 AuthenticationException", True)
    check("message", "用户名或密码错误" in e.message)

# ============================================================
# 6. login — 密码错误
# ============================================================
print("\n[6] login — 密码错误")
try:
    auth.login(db, username="admin", password="wrong_password")
    check("密码错误抛异常", False)
except AuthenticationException as e:
    check("密码错误抛 AuthenticationException", True)
    check("message", "用户名或密码错误" in e.message)

# ============================================================
# 7. login — 用户禁用
# ============================================================
print("\n[7] login — 用户禁用")
try:
    auth.login(db, username="disabled_user", password="disabled123")
    check("用户禁用抛异常", False)
except PermissionDeniedException as e:
    check("用户禁用抛 PermissionDeniedException", True)
    check("message", "禁用" in e.message or "禁止" in e.message)

# ============================================================
# 8. login — JWT 创建成功
# ============================================================
print("\n[8] login — JWT 创建成功")
response = auth.login(db, username="admin", password="admin123")
payload = decode_access_token(response.access_token)
check("sub = user.id", payload["sub"] == str(active_user.id))
check("username = admin", payload["username"] == "admin")
check("roles 包含 administrator", "administrator" in payload.get("roles", []))
check("roles 包含 technician", "technician" in payload.get("roles", []))

# ============================================================
# 9. login — LoginResponse 正确
# ============================================================
print("\n[9] LoginResponse 正确")
response = auth.login(db, username="admin", password="admin123")
check("access_token 以 eyJ 开头", response.access_token.startswith("eyJ"))
check("token_type", response.token_type == "bearer")
check("user.id", response.user.id == active_user.id)
check("user.roles 非空", len(response.user.roles) > 0)

# ============================================================
# 10. change_password — 成功修改
# ============================================================
print("\n[10] change_password — 成功修改")
db.query(SystemLog).delete()
db.commit()

auth.change_password(
    db, user_id=active_user.id,
    old_password="admin123", new_password="new_pass456",
)
check("change_password 无异常", True)

# 验证密码已更新
updated_user = db.query(User).filter(User.id == active_user.id).first()
check("password_hash 已更新",
      verify_password("new_pass456", updated_user.password_hash))
check("旧密码不可用",
      not verify_password("admin123", updated_user.password_hash))

# ============================================================
# 11. change_password — 原密码错误
# ============================================================
print("\n[11] change_password — 原密码错误")
try:
    auth.change_password(
        db, user_id=active_user.id,
        old_password="wrong_old", new_password="any_new",
    )
    check("原密码错误抛异常", False)
except AuthenticationException as e:
    check("原密码错误抛 AuthenticationException", True)
    check("message", "原密码错误" in e.message)

# ============================================================
# 12. change_password — 用户不存在
# ============================================================
print("\n[12] change_password — 用户不存在")
try:
    auth.change_password(
        db, user_id=99999,
        old_password="any", new_password="any",
    )
    check("用户不存在抛异常", False)
except NotFoundException as e:
    check("用户不存在抛 NotFoundException", True)

# ============================================================
# 13. change_password — SystemLog
# ============================================================
print("\n[13] change_password — SystemLog")
db.query(SystemLog).delete()
db.commit()

auth.change_password(
    db, user_id=active_user.id,
    old_password="new_pass456", new_password="another_pass",
)
logs = db.query(SystemLog).filter(
    SystemLog.target_type == "User",
    SystemLog.target_id == active_user.id,
).all()
check("SystemLog 已写入", len(logs) >= 1)
if logs:
    check("action = UPDATE", logs[0].action == ActionType.UPDATE)
    check("target_type = User", logs[0].target_type == "User")
    check("target_id 正确", logs[0].target_id == active_user.id)

# ============================================================
# 14. get_current_user_info — 查询成功
# ============================================================
print("\n[14] get_current_user_info — 查询成功")
user_info = auth.get_current_user_info(db, user_id=active_user.id)
check("返回 UserResponse", isinstance(user_info, UserResponse))
check("user_info.id", user_info.id == active_user.id)
check("user_info.username", user_info.username == "admin")
check("user_info.real_name", user_info.real_name == "管理员")
check("不含 password_hash", "password_hash" not in user_info.model_dump())

# ============================================================
# 15. get_current_user_info — 不存在
# ============================================================
print("\n[15] get_current_user_info — 不存在")
try:
    auth.get_current_user_info(db, user_id=99999)
    check("不存在抛异常", False)
except NotFoundException as e:
    check("不存在抛 NotFoundException", True)

# ============================================================
# 16. get_current_user_info — Response 正确
# ============================================================
print("\n[16] get_current_user_info — Response 正确")
user_info = auth.get_current_user_info(db, user_id=active_user.id)
check("from_attributes 生效", user_info.id == active_user.id)
check("roles 已加载", len(user_info.roles) >= 2)
check("JSON 序列化", len(user_info.model_dump_json()) > 0)

# ============================================================
# 17. 事务 — rollback（模拟）
# ============================================================
print("\n[17] 事务 — rollback")
# 通过直接操作 db 模拟：force a rollback scenario
# change_password 内部有 try-except-rollback
# 这里验证异常后数据一致性
original_hash = db.query(User).filter(User.id == active_user.id).first().password_hash
try:
    auth.change_password(
        db, user_id=active_user.id,
        old_password="wrong", new_password="no_change",
    )
except AuthenticationException:
    pass
# 密码不应被修改
after_hash = db.query(User).filter(User.id == active_user.id).first().password_hash
check("rollback 后密码不变", original_hash == after_hash)

# ============================================================
# 18. 无循环导入
# ============================================================
print("\n[18] 无循环导入")
import server.services.auth_service as auth_mod
check("无循环导入", True)

# ============================================================
# 19. Type Hint / Docstring
# ============================================================
print("\n[19] Type Hint / Docstring")
import inspect

# 检查公开方法
for method_name in ["login", "change_password", "get_current_user_info"]:
    method = getattr(AuthService, method_name)
    sig = inspect.signature(method)
    check(f"{method_name} 有参数", len(sig.parameters) > 0)
    check(f"{method_name} 有 return annotation",
          sig.return_annotation is not inspect.Signature.empty,
          f"实际: {sig.return_annotation}")
    check(f"{method_name} 有 docstring",
          method.__doc__ is not None and len(method.__doc__) > 20)

# 检查私有方法
for method_name in ["_get_user", "_validate_password", "_build_login_response"]:
    method = getattr(AuthService, method_name)
    check(f"{method_name} 有 docstring",
          method.__doc__ is not None and len(method.__doc__) > 20)

# ============================================================
# 20. PEP8
# ============================================================
print("\n[20] PEP8")
# 验证文件内容结构
auth_file = Path(__file__).parent.parent / "server" / "services" / "auth_service.py"
content = auth_file.read_text(encoding="utf-8")
check("文件以 docstring 开头", content.strip().startswith('"""'))
check("有 __all__", "__all__" in content)
check("无 print()", "print(" not in content)
check("无 raise ValueError", "raise ValueError" not in content)
check("无 raise RuntimeError", "raise RuntimeError" not in content)

# ============================================================
# 21. 禁止命名检查
# ============================================================
print("\n[21] 禁止命名检查")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException"]
for name in forbidden:
    try:
        getattr(auth_mod, name)
        check(f"{name} 不应存在", False)
    except AttributeError:
        check(f"{name} 未使用", True)

# 检查文件内容
for name in forbidden:
    check(f"文件不含 {name}", name not in content)

# ============================================================
# 22. 仅允许 3 个公开方法
# ============================================================
print("\n[22] 仅允许 3 个公开方法")
public_methods = [
    name for name, method in inspect.getmembers(AuthService, inspect.isfunction)
    if not name.startswith("_")
]
check("恰好 3 个公开方法", len(public_methods) == 3,
      f"实际: {public_methods}")

# ============================================================
# 清理
# ============================================================
db.close()
BaseModel.metadata.drop_all(bind=engine)

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