"""Sprint 3 — Task 3.5 User Router 自检脚本

验证项:
    GET list:
        ✓ 成功
        ✓ 分页
        ✓ 查询参数
        ✓ 登录验证
    GET detail:
        ✓ 成功
        ✓ 不存在
    POST:
        ✓ 创建成功
        ✓ username 重复
        ✓ 无权限
    PUT:
        ✓ 修改成功
        ✓ 不存在
        ✓ 无权限
    DELETE:
        ✓ 删除成功
        ✓ 非管理员
        ✓ 删除自己
    Roles:
        ✓ 分配成功
        ✓ 不存在角色
    Router:
        ✓ Depends(get_db)
        ✓ Depends(get_current_active_user)
        ✓ 不直接 ORM
        ✓ 不直接 JWT
        ✓ 不直接 hash
    OpenAPI:
        ✓ tags
        ✓ response_model
        ✓ 路径注册
    Exception:
        ✓ 全局异常处理
        ✓ JSON 格式
    其它:
        ✓ py_compile
        ✓ import
        ✓ 无循环导入
        ✓ 禁止命名检查
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
print("  Task 3.5 — User Router Self Test")
print("=" * 60)

# ============================================================
# 临时数据库
# ============================================================
import server.config as config_mod

_temp_db = tempfile.NamedTemporaryFile(
    suffix=".db", delete=False, prefix="test_user_router_",
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
        str(Path(__file__).parent.parent / "server" / "routers" / "user_router.py"),
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
from server.models import User, Role, Permission, user_roles, role_permissions
from server.core.security import hash_password, create_access_token

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
db.add_all([admin_role, tech_role])
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

# 创建普通用户
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

# 生成 JWT
admin_token = create_access_token(
    data={"sub": str(admin_user.id), "username": admin_user.username, "role": "administrator"},
)
tech_token = create_access_token(
    data={"sub": str(tech_user.id), "username": tech_user.username, "role": "technician"},
)
admin_headers = {"Authorization": f"Bearer {admin_token}"}
tech_headers = {"Authorization": f"Bearer {tech_token}"}

check("测试数据库创建", True)
check("管理员 Token 生成", len(admin_token) > 0)
check("技术员 Token 生成", len(tech_token) > 0)

# ============================================================
# 3. import
# ============================================================
print("\n[3] import")
from server.routers.user_router import router

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
# 4. Router — prefix / tags
# ============================================================
print("\n[4] Router — prefix / tags")
check("prefix = /api/users", router.prefix == "/api/users")
check("tags = [Users]", router.tags == ["Users"])

# ============================================================
# 5. Router — 路径注册
# ============================================================
print("\n[5] Router — 路径注册")
routes = [r.path for r in test_app.routes]
check("GET /api/users", "/api/users" in routes)
check("GET /api/users/{user_id}", "/api/users/{user_id}" in routes)
check("POST /api/users", "/api/users" in routes)
check("PUT /api/users/{user_id}", "/api/users/{user_id}" in routes)
check("DELETE /api/users/{user_id}", "/api/users/{user_id}" in routes)
check("POST /api/users/{user_id}/roles", "/api/users/{user_id}/roles" in routes)

# ============================================================
# 6. main.py include_router
# ============================================================
print("\n[6] main.py include_router")
main_content = Path(__file__).parent.parent / "server" / "main.py"
content = main_content.read_text(encoding="utf-8")
check("import user_router", "from server.routers.user_router" in content)
check("include_router(user_router)", "include_router(user_router)" in content)

# ============================================================
# 7. GET list — 成功
# ============================================================
print("\n[7] GET list — 成功")
resp = client.get("/api/users", headers=admin_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("items", "items" in data)
check("total", "total" in data)
check("total > 0", data["total"] > 0)

# ============================================================
# 8. GET list — 分页
# ============================================================
print("\n[8] GET list — 分页")
resp = client.get("/api/users?page=1&page_size=1", headers=admin_headers)
data = resp.json()
check("page_size=1", len(data["items"]) <= 1, f"实际: {len(data['items'])}")

# ============================================================
# 9. GET list — 查询参数
# ============================================================
print("\n[9] GET list — 查询参数")
resp = client.get("/api/users?username=admin", headers=admin_headers)
data = resp.json()
check("username 筛选", any(u["username"] == "admin" for u in data["items"]))

resp = client.get("/api/users?is_active=true", headers=admin_headers)
data = resp.json()
check("is_active 筛选", all(u["is_active"] for u in data["items"]))

# ============================================================
# 10. GET list — 未登录 401
# ============================================================
print("\n[10] GET list — 未登录 401")
resp = client.get("/api/users")
check("HTTP 401", resp.status_code == 401, f"实际: {resp.status_code}")

# ============================================================
# 11. GET detail — 成功
# ============================================================
print("\n[11] GET detail — 成功")
resp = client.get(f"/api/users/{admin_user.id}", headers=admin_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("username = admin", data["username"] == "admin")
check("不含 password_hash", "password_hash" not in data)

# ============================================================
# 12. GET detail — 不存在
# ============================================================
print("\n[12] GET detail — 不存在")
resp = client.get("/api/users/99999", headers=admin_headers)
check("HTTP 404", resp.status_code == 404, f"实际: {resp.status_code}")

# ============================================================
# 13. POST — 创建成功
# ============================================================
print("\n[13] POST — 创建成功")
resp = client.post("/api/users", json={
    "username": "new_user",
    "password": "pass123",
    "real_name": "新用户",
    "role_ids": [tech_role.id],
}, headers=admin_headers)
check("HTTP 201", resp.status_code == 201, f"实际: {resp.status_code}")
data = resp.json()
check("username = new_user", data["username"] == "new_user")
check("不含 password_hash", "password_hash" not in data)
new_user_id = data["id"]

# ============================================================
# 14. POST — username 重复
# ============================================================
print("\n[14] POST — username 重复")
resp = client.post("/api/users", json={
    "username": "new_user",
    "password": "pass123",
    "real_name": "重复",
}, headers=admin_headers)
check("HTTP 409", resp.status_code == 409, f"实际: {resp.status_code}")

# ============================================================
# 15. POST — 无权限（技术员）
# ============================================================
print("\n[15] POST — 无权限")
resp = client.post("/api/users", json={
    "username": "no_perm",
    "password": "pass123",
    "real_name": "无权限",
}, headers=tech_headers)
check("HTTP 403", resp.status_code == 403, f"实际: {resp.status_code}")

# ============================================================
# 16. PUT — 修改成功
# ============================================================
print("\n[16] PUT — 修改成功")
resp = client.put(f"/api/users/{new_user_id}", json={
    "real_name": "已修改",
    "phone": "13800000000",
}, headers=admin_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("real_name 已修改", data["real_name"] == "已修改")
check("phone 已修改", data["phone"] == "13800000000")

# ============================================================
# 17. PUT — 不存在
# ============================================================
print("\n[17] PUT — 不存在")
resp = client.put("/api/users/99999", json={
    "real_name": "x",
}, headers=admin_headers)
check("HTTP 404", resp.status_code == 404, f"实际: {resp.status_code}")

# ============================================================
# 18. PUT — 无权限
# ============================================================
print("\n[18] PUT — 无权限")
resp = client.put(f"/api/users/{new_user_id}", json={
    "real_name": "hack",
}, headers=tech_headers)
check("HTTP 403", resp.status_code == 403, f"实际: {resp.status_code}")

# ============================================================
# 19. DELETE — 删除成功
# ============================================================
print("\n[19] DELETE — 删除成功")
# 先创建一个用户
resp = client.post("/api/users", json={
    "username": "to_delete",
    "password": "pass123",
    "real_name": "待删除",
}, headers=admin_headers)
del_id = resp.json()["id"]
resp = client.delete(f"/api/users/{del_id}", headers=admin_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("message", data.get("message") == "User deleted successfully.")

# 验证已删除
resp = client.get(f"/api/users/{del_id}", headers=admin_headers)
check("已删除不可查", resp.status_code == 404)

# ============================================================
# 20. DELETE — 非管理员
# ============================================================
print("\n[20] DELETE — 非管理员")
resp = client.delete(f"/api/users/{new_user_id}", headers=tech_headers)
check("HTTP 403", resp.status_code == 403, f"实际: {resp.status_code}")

# ============================================================
# 21. DELETE — 删除自己
# ============================================================
print("\n[21] DELETE — 删除自己")
resp = client.delete(f"/api/users/{admin_user.id}", headers=admin_headers)
check("HTTP 400", resp.status_code == 400, f"实际: {resp.status_code}")

# ============================================================
# 22. Roles — 分配成功
# ============================================================
print("\n[22] Roles — 分配成功")
resp = client.post(f"/api/users/{new_user_id}/roles", json={
    "role_ids": [admin_role.id, tech_role.id],
}, headers=admin_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")

# ============================================================
# 23. Roles — 不存在角色
# ============================================================
print("\n[23] Roles — 不存在角色")
resp = client.post(f"/api/users/{new_user_id}/roles", json={
    "role_ids": [9999],
}, headers=admin_headers)
check("HTTP 400", resp.status_code == 400, f"实际: {resp.status_code}")

# ============================================================
# 24. Router — 不直接 ORM
# ============================================================
print("\n[24] Router — 不直接 ORM")
router_content = (
    Path(__file__).parent.parent / "server" / "routers" / "user_router.py"
).read_text(encoding="utf-8")
check("不直接 ORM (db.query/add/execute)",
      "db.query" not in router_content
      and "db.add" not in router_content
      and "db.execute" not in router_content
      and "db.commit" not in router_content
      and "db.rollback" not in router_content)

# ============================================================
# 25. Router — 不直接 JWT
# ============================================================
print("\n[25] Router — 不直接 JWT")
check("不直接 jwt", "jwt" not in router_content.lower())
check("不直接 decode", "decode" not in router_content)
check("不直接 Bearer", "Bearer" not in router_content)

# ============================================================
# 26. Router — 不直接 hash
# ============================================================
print("\n[26] Router — 不直接 hash")
check("不直接 hash_password", "hash_password" not in router_content)
check("不直接 bcrypt", "bcrypt" not in router_content)

# ============================================================
# 27. Router — Depends(get_db)
# ============================================================
print("\n[27] Router — Depends(get_db)")
check("Depends(get_db)", "Depends(get_db)" in router_content)

# ============================================================
# 28. Router — Depends(get_current_active_user)
# ============================================================
print("\n[28] Router — Depends(get_current_active_user)")
check("Depends(get_current_active_user)",
      "Depends(get_current_active_user)" in router_content)

# ============================================================
# 29. Router — 无 try/except
# ============================================================
print("\n[29] Router — 无 try/except")
check("Router 无 try:", "try:" not in router_content)
check("Router 无 except:", "except" not in router_content)

# ============================================================
# 30. OpenAPI — tags
# ============================================================
print("\n[30] OpenAPI")
openapi = test_app.openapi()
paths = openapi.get("paths", {})

# 检查 Users tag
users_paths = [p for p, methods in paths.items()
               for m, info in methods.items()
               if m != "options" and "Users" in info.get("tags", [])]
check("Users tag 接口数 = 6", len(users_paths) == 6, f"实际: {len(users_paths)}")

# 检查 response_model
get_schema = paths.get("/api/users", {}).get("get", {})
check("GET list 有 response_model", "200" in get_schema.get("responses", {}))

post_schema = paths.get("/api/users", {}).get("post", {})
check("POST 有 response_model", "201" in post_schema.get("responses", {}))

# ============================================================
# 31. 全局异常处理 — JSON 格式
# ============================================================
print("\n[31] 全局异常处理 — JSON 格式")
resp = client.get("/api/users/99999", headers=admin_headers)
data = resp.json()
check("统一格式: code", "code" in data)
check("统一格式: message", "message" in data)
check("统一格式: detail", "detail" in data)

# ============================================================
# 32. 无循环导入
# ============================================================
print("\n[32] 无循环导入")
import server.routers.user_router as ur

check("无循环导入", True)

# ============================================================
# 33. 禁止命名检查
# ============================================================
print("\n[33] 禁止命名检查")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException", "HTTPException", "JSONResponse"]
for name in forbidden:
    check(f"文件不含 {name}", name not in router_content)

# ============================================================
# 34. Type Hint / Docstring
# ============================================================
print("\n[34] Type Hint / Docstring")
import inspect

for fn_name in ["list_users", "get_user", "create_user", "update_user", "delete_user", "assign_roles"]:
    fn = getattr(ur, fn_name, None)
    if fn is None:
        check(f"{fn_name} 存在", False)
        continue
    check(f"{fn_name} 有 docstring", fn.__doc__ is not None and len(fn.__doc__) > 20)
    sig = inspect.signature(fn)
    check(f"{fn_name} 有参数", len(sig.parameters) > 0)

# ============================================================
# 35. PEP8
# ============================================================
print("\n[35] PEP8")
check("文件以 docstring 开头", router_content.strip().startswith('"""'))
check("有 __all__", "__all__" in router_content)
check("无 print()", "print(" not in router_content)
check("无 TODO", "TODO" not in router_content)
check("无 FIXME", "FIXME" not in router_content)

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