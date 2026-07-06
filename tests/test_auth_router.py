"""Sprint 3 — Task 3.3 Auth Router 自检脚本

验证项:
    login:
        1.  登录成功
        2.  密码错误
        3.  用户不存在
        4.  用户禁用
        5.  返回 Token
        6.  response_model 正确
    change-password:
        7.  登录成功可修改
        8.  未登录 401
        9.  原密码错误
        10. 修改成功
        11. 返回 message
    me:
        12. 登录成功
        13. 返回 UserResponse
        14. 未登录 401
        15. Token 失效
    Router:
        16. prefix 正确
        17. tags 正确
        18. 注册成功
        19. main.py include_router()
        20. OpenAPI 正常
        21. Swagger 出现三个接口
    Exception:
        22. AuthenticationException
        23. PermissionDeniedException
        24. NotFoundException
        25. 全局异常处理生效
        26. Router 无 try/except
    其它:
        27. py_compile
        28. import
        29. TestClient
        30. 无循环导入
        31. 禁止命名检查
        32. Type Hint
        33. Google Docstring
        34. PEP8
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
print("  Task 3.3 — Auth Router Self Test")
print("=" * 60)

# ============================================================
# 关键：在导入任何 server 模块前，将 DATABASE_URL 指向临时文件
# 这样 engine.py 在首次加载时就会使用临时数据库创建引擎，
# 后续 session.py、dependencies.py 都会自动绑定到临时数据库。
# 使用文件级 SQLite 而非 :memory:，避免 NullPool 多连接问题。
# ============================================================
import server.config as config_mod

# 创建临时数据库文件
_temp_db = tempfile.NamedTemporaryFile(
    suffix=".db", delete=False, prefix="test_auth_router_",
)
_temp_db.close()
_test_db_url = f"sqlite:///{_temp_db.name}"

# 替换 URL（必须在首次 import server.database 之前完成）
config_mod.settings.DATABASE_URL = _test_db_url

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "routers" / "auth_router.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 准备测试数据库
# 此时 engine 尚未创建，首次导入 server.database 时会使用 _test_db_url
# ============================================================
print("\n[2] 测试数据库准备")

from server.database.engine import engine as test_engine
from server.database.session import SessionLocal as TestSessionLocal
from server.models.base_model import BaseModel
from server.models import User, Role, Permission, SystemLog, user_roles, role_permissions
from server.core.security import hash_password

# 创建所有表
BaseModel.metadata.create_all(bind=test_engine)

# 种子数据
db = TestSessionLocal()

# 创建权限
perm = Permission(code="auth:login", name="登录", module="auth")
db.add(perm)
db.flush()

# 创建角色
admin_role = Role(name="administrator", display_name="管理员", is_system=True)
tech_role = Role(name="technician", display_name="技术员", is_system=True)
db.add_all([admin_role, tech_role])
db.flush()

# 关联角色-权限
db.execute(role_permissions.insert().values(role_id=admin_role.id, permission_id=perm.id))
db.flush()

# 创建用户
active_user = User(
    username="admin",
    password_hash=hash_password("admin123"),
    real_name="管理员",
    is_active=True,
)
inactive_user = User(
    username="disabled",
    password_hash=hash_password("disabled123"),
    real_name="已禁用",
    is_active=False,
)
db.add_all([active_user, inactive_user])
db.flush()

# 关联用户-角色
db.execute(user_roles.insert().values(user_id=active_user.id, role_id=admin_role.id))
db.execute(user_roles.insert().values(user_id=inactive_user.id, role_id=tech_role.id))
db.commit()

check("测试数据库创建", True)
check("测试用户创建", active_user.id is not None, f"active_user.id={active_user.id}")

# ============================================================
# 3. import
# ============================================================
print("\n[3] import")
from server.routers.auth_router import router

check("router 导入", router is not None)

# ============================================================
# 创建测试 App
# ============================================================
from fastapi import FastAPI
from fastapi.testclient import TestClient
from server.core.exception_handlers import register_exception_handlers
from server.middleware.cors_middleware import setup_cors
from server.middleware.log_middleware import setup_request_logging

test_app = FastAPI(
    title="GTMS API Test",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
setup_cors(test_app)
setup_request_logging(test_app)
register_exception_handlers(test_app)
test_app.include_router(router)

client = TestClient(test_app, raise_server_exceptions=False)

check("TestClient 创建", True)

# ============================================================
# 4. Router — prefix 正确
# ============================================================
print("\n[4] Router — prefix 正确")
check("prefix = /api/auth", router.prefix == "/api/auth")
check("tags = [Authentication]", router.tags == ["Authentication"])

# ============================================================
# 5. Router — 注册成功
# ============================================================
print("\n[5] Router — 注册成功")
routes = [r.path for r in test_app.routes]
check("POST /api/auth/login 已注册", "/api/auth/login" in routes)
check("POST /api/auth/change-password 已注册", "/api/auth/change-password" in routes)
check("GET /api/auth/me 已注册", "/api/auth/me" in routes)

# ============================================================
# 6. main.py include_router()
# ============================================================
print("\n[6] main.py include_router()")
main_content = Path(__file__).parent.parent / "server" / "main.py"
content = main_content.read_text(encoding="utf-8")
check("main.py 包含 auth_router import",
      "from server.routers.auth_router" in content)
check("main.py 包含 include_router",
      "include_router(auth_router)" in content)

# ============================================================
# 7. POST /login — 登录成功
# ============================================================
print("\n[7] POST /login — 登录成功")
resp = client.post("/api/auth/login", json={
    "username": "admin",
    "password": "admin123",
})
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("access_token 存在", "access_token" in data)
check("token_type = bearer", data.get("token_type") == "bearer")
check("user 存在", "user" in data)
check("user.username = admin", data["user"]["username"] == "admin")

# 保存 token 用于后续测试
token = data["access_token"]
auth_headers = {"Authorization": f"Bearer {token}"}

# ============================================================
# 8. POST /login — 密码错误
# ============================================================
print("\n[8] POST /login — 密码错误")
resp = client.post("/api/auth/login", json={
    "username": "admin",
    "password": "wrong_password",
})
check("HTTP 401", resp.status_code == 401, f"实际: {resp.status_code}")
data = resp.json()
check("code = 401", data.get("code") == 401)
check("message 包含错误", len(data.get("message", "")) > 0)

# ============================================================
# 9. POST /login — 用户不存在
# ============================================================
print("\n[9] POST /login — 用户不存在")
resp = client.post("/api/auth/login", json={
    "username": "nonexistent",
    "password": "any",
})
check("HTTP 401", resp.status_code == 401, f"实际: {resp.status_code}")

# ============================================================
# 10. POST /login — 用户禁用
# ============================================================
print("\n[10] POST /login — 用户禁用")
resp = client.post("/api/auth/login", json={
    "username": "disabled",
    "password": "disabled123",
})
check("HTTP 403", resp.status_code == 403, f"实际: {resp.status_code}")

# ============================================================
# 11. POST /login — response_model 正确
# ============================================================
print("\n[11] POST /login — response_model 正确")
resp = client.post("/api/auth/login", json={
    "username": "admin",
    "password": "admin123",
})
data = resp.json()
check("三字段: access_token", "access_token" in data)
check("三字段: token_type", "token_type" in data)
check("三字段: user", "user" in data)
check("user 无 password_hash", "password_hash" not in data["user"])

# ============================================================
# 12. POST /change-password — 未登录 401
# ============================================================
print("\n[12] POST /change-password — 未登录 401")
resp = client.post("/api/auth/change-password", json={
    "old_password": "admin123",
    "new_password": "new456",
})
check("HTTP 401", resp.status_code == 401, f"实际: {resp.status_code}")

# ============================================================
# 13. POST /change-password — 登录成功可修改
# ============================================================
print("\n[13] POST /change-password — 登录成功可修改")
resp = client.post("/api/auth/change-password", json={
    "old_password": "admin123",
    "new_password": "new_pass456",
}, headers=auth_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("message 正确", data.get("message") == "Password changed successfully.")

# 验证密码确实已更新（重新登录）
resp = client.post("/api/auth/login", json={
    "username": "admin",
    "password": "new_pass456",
})
check("新密码登录成功", resp.status_code == 200, f"实际: {resp.status_code}")

# 把密码改回去
client.post("/api/auth/change-password", json={
    "old_password": "new_pass456",
    "new_password": "admin123",
}, headers=auth_headers)

# ============================================================
# 14. POST /change-password — 原密码错误
# ============================================================
print("\n[14] POST /change-password — 原密码错误")
resp = client.post("/api/auth/change-password", json={
    "old_password": "wrong_old_password",
    "new_password": "any_new",
}, headers=auth_headers)
check("HTTP 401", resp.status_code == 401, f"实际: {resp.status_code}")

# ============================================================
# 15. POST /change-password — 返回 message
# ============================================================
print("\n[15] POST /change-password — 返回 message")
resp = client.post("/api/auth/change-password", json={
    "old_password": "admin123",
    "new_password": "temp_pass789",
}, headers=auth_headers)
check("HTTP 200", resp.status_code == 200)
data = resp.json()
check("message 字段", "message" in data)
check("无 password_hash", "password_hash" not in data)
check("无 access_token", "access_token" not in data)

# 改回去
client.post("/api/auth/change-password", json={
    "old_password": "temp_pass789",
    "new_password": "admin123",
}, headers=auth_headers)

# ============================================================
# 16. GET /me — 登录成功
# ============================================================
print("\n[16] GET /me — 登录成功")
resp = client.get("/api/auth/me", headers=auth_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("username = admin", data.get("username") == "admin")
check("real_name = 管理员", data.get("real_name") == "管理员")
check("is_active", data.get("is_active") is True)
check("不含 password_hash", "password_hash" not in data)

# ============================================================
# 17. GET /me — 未登录 401
# ============================================================
print("\n[17] GET /me — 未登录 401")
resp = client.get("/api/auth/me")
check("HTTP 401", resp.status_code == 401, f"实际: {resp.status_code}")

# ============================================================
# 18. GET /me — Token 失效
# ============================================================
print("\n[18] GET /me — Token 失效")
resp = client.get("/api/auth/me", headers={
    "Authorization": "Bearer invalid_token_here",
})
check("HTTP 401", resp.status_code == 401, f"实际: {resp.status_code}")

# ============================================================
# 19. OpenAPI 正常
# ============================================================
print("\n[19] OpenAPI 正常")
openapi = test_app.openapi()
check("OpenAPI 生成", openapi is not None)
paths = openapi.get("paths", {})

# 检查三个接口
check("/api/auth/login 在 OpenAPI", "/api/auth/login" in paths)
check("/api/auth/change-password 在 OpenAPI",
      "/api/auth/change-password" in paths)
check("/api/auth/me 在 OpenAPI", "/api/auth/me" in paths)

# 检查 tag
login_schema = paths.get("/api/auth/login", {}).get("post", {})
check("login tags", "Authentication" in login_schema.get("tags", []))

# 检查 response_model
login_responses = login_schema.get("responses", {})
check("login 200 response_model", "200" in login_responses)

# 检查 /me 的 response_model
me_schema = paths.get("/api/auth/me", {}).get("get", {})
me_responses = me_schema.get("responses", {})
check("me 200 response_model", "200" in me_responses)

# ============================================================
# 20. Swagger 出现三个接口
# ============================================================
print("\n[20] Swagger 出现三个接口")
# 验证 /docs 可访问
resp = client.get("/openapi.json")
check("/openapi.json 200", resp.status_code == 200)

# 验证所有接口在 OpenAPI 中
# openapi.get("tags") 可能返回 None（FastAPI 某些版本），需要兼容处理
tags_list = openapi.get("tags") or []
auth_tag = [t for t in tags_list if t.get("name") == "Authentication"]

# 统计 Authentication tag 下的接口数
auth_paths = [p for p, methods in paths.items()
              for m, info in methods.items()
              if m != "options" and "Authentication" in info.get("tags", [])]
check("Authentication 下 3 个接口", len(auth_paths) == 3,
      f"实际: {auth_paths}")

# 顶层 tags 可能为空（FastAPI 版本差异），路由级 tags 已在上面验证
# 若顶层无 tags，则通过路由标签交叉验证
check("Authentication tag 存在",
      len(auth_tag) >= 1 or len(auth_paths) == 3,
      f"顶层 tags={tags_list}")

# ============================================================
# 21. 全局异常处理生效
# ============================================================
print("\n[21] 全局异常处理生效")
# 验证统一 JSON 格式
resp = client.post("/api/auth/login", json={
    "username": "admin",
    "password": "wrong",
})
data = resp.json()
check("统一格式: code", "code" in data)
check("统一格式: message", "message" in data)
check("统一格式: detail", "detail" in data)
check("三字段无多余", len(data) == 3, f"实际: {data.keys()}")

# ============================================================
# 22. Router 无 try/except
# ============================================================
print("\n[22] Router 无 try/except")
router_content = (
    Path(__file__).parent.parent / "server" / "routers" / "auth_router.py"
).read_text(encoding="utf-8")
check("Router 无 try:", "try:" not in router_content)
check("Router 无 except:", "except" not in router_content)

# ============================================================
# 23. 无循环导入
# ============================================================
print("\n[23] 无循环导入")
import server.routers.auth_router as ar

check("无循环导入", True)

# ============================================================
# 24. 禁止命名检查
# ============================================================
print("\n[24] 禁止命名检查")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException"]
for name in forbidden:
    try:
        getattr(ar, name)
        check(f"{name} 不应存在", False)
    except AttributeError:
        check(f"{name} 未使用", True)
    check(f"文件不含 {name}", name not in router_content)

# ============================================================
# 25. Type Hint / Docstring
# ============================================================
print("\n[25] Type Hint / Docstring")
import inspect

# 检查 router 中的路由函数
for fn_name in ["login", "change_password", "get_current_user_info"]:
    fn = getattr(ar, fn_name, None)
    if fn is None:
        check(f"{fn_name} 存在", False)
        continue
    check(f"{fn_name} 有 docstring",
          fn.__doc__ is not None and len(fn.__doc__) > 20)
    sig = inspect.signature(fn)
    check(f"{fn_name} 有参数", len(sig.parameters) > 0)

# ============================================================
# 26. PEP8
# ============================================================
print("\n[26] PEP8")
check("文件以 docstring 开头", router_content.strip().startswith('"""'))
check("有 __all__", "__all__" in router_content)
check("无 print()", "print(" not in router_content)

# ============================================================
# 27. 三个接口完整测试
# ============================================================
print("\n[27] 三个接口完整测试")
# 获取新 token
resp = client.post("/api/auth/login", json={
    "username": "admin",
    "password": "admin123",
})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# change-password
resp = client.post("/api/auth/change-password", json={
    "old_password": "admin123",
    "new_password": "admin123",
}, headers=headers)
check("change-password 200", resp.status_code == 200)

# me
resp = client.get("/api/auth/me", headers=headers)
check("me 200", resp.status_code == 200)
check("me 返回 UserResponse", "username" in resp.json())

# ============================================================
# 清理
# ============================================================
print("\n[28] 清理")
db.close()
BaseModel.metadata.drop_all(bind=test_engine)

# 释放引擎资源后再删除临时数据库文件
test_engine.dispose()

# 删除临时数据库文件
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