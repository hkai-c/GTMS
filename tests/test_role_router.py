"""Sprint 3 — Task 3.6 Role Router 自检脚本

验证项:
    GET list:
        ✓ 成功
        ✓ 登录验证
        ✓ 返回 RoleListResponse
    GET detail:
        ✓ 成功
        ✓ 不存在
    GET permissions:
        ✓ 成功
        ✓ 返回 PermissionResponse[]
        ✓ 不存在角色
    Router:
        ✓ Depends(get_db)
        ✓ Depends(get_current_active_user)
        ✓ 不直接 ORM
        ✓ 不直接 JWT
        ✓ 无业务逻辑
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
print("  Task 3.6 — Role Router Self Test")
print("=" * 60)

# ============================================================
# 临时数据库
# ============================================================
import server.config as config_mod

_temp_db = tempfile.NamedTemporaryFile(
    suffix=".db", delete=False, prefix="test_role_router_",
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
        str(Path(__file__).parent.parent / "server" / "routers" / "role_router.py"),
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
perm_task = Permission(code="task:read", name="Task Read", module="task")
perm_user = Permission(code="user:read", name="User Read", module="user")
perm_user_write = Permission(code="user:write", name="User Write", module="user")
db.add_all([perm_task, perm_user, perm_user_write])
db.flush()

# 创建角色
admin_role = Role(name="administrator", display_name="管理员", is_system=True)
tech_role = Role(name="technician", display_name="技术员", is_system=True)
db.add_all([admin_role, tech_role])
db.flush()

# 关联角色-权限
db.execute(
    role_permissions.insert().values(role_id=admin_role.id, permission_id=perm_task.id)
)
db.execute(
    role_permissions.insert().values(role_id=admin_role.id, permission_id=perm_user.id)
)
db.execute(
    role_permissions.insert().values(role_id=admin_role.id, permission_id=perm_user_write.id)
)
db.execute(
    role_permissions.insert().values(role_id=tech_role.id, permission_id=perm_task.id)
)
db.flush()

# 创建用户
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
db.commit()
db.refresh(admin_user)

# 生成 JWT
token = create_access_token(
    data={"sub": str(admin_user.id), "username": admin_user.username, "role": "administrator"},
)
auth_headers = {"Authorization": f"Bearer {token}"}

check("测试数据库创建", True)
check("Token 生成", len(token) > 0)

# ============================================================
# 3. import
# ============================================================
print("\n[3] import")
from server.routers.role_router import router

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
check("prefix = /api/roles", router.prefix == "/api/roles")
check("tags = [Roles]", router.tags == ["Roles"])

# ============================================================
# 5. Router — 路径注册
# ============================================================
print("\n[5] Router — 路径注册")
routes = [r.path for r in test_app.routes]
check("GET /api/roles", "/api/roles" in routes)
check("GET /api/roles/{role_id}", "/api/roles/{role_id}" in routes)
check("GET /api/roles/{role_id}/permissions",
      "/api/roles/{role_id}/permissions" in routes)

# ============================================================
# 6. main.py include_router
# ============================================================
print("\n[6] main.py include_router")
main_content = Path(__file__).parent.parent / "server" / "main.py"
content = main_content.read_text(encoding="utf-8")
check("import role_router", "from server.routers.role_router" in content)
check("include_router(role_router)", "include_router(role_router)" in content)

# ============================================================
# 7. GET list — 成功
# ============================================================
print("\n[7] GET list — 成功")
resp = client.get("/api/roles", headers=auth_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("items", "items" in data)
check("total", "total" in data)
check("total > 0", data["total"] > 0)
check("角色含 permissions", "permissions" in data["items"][0])

# ============================================================
# 8. GET list — 返回 RoleListResponse
# ============================================================
print("\n[8] GET list — 返回 RoleListResponse")
check("items 为 list", isinstance(data["items"], list))
check("total 为 int", isinstance(data["total"], int))
item = data["items"][0]
check("有 id", "id" in item)
check("有 name", "name" in item)
check("有 display_name", "display_name" in item)
check("有 is_system", "is_system" in item)
check("有 permissions", "permissions" in item)
check("无 password_hash", "password_hash" not in item)

# ============================================================
# 9. GET list — 未登录 401
# ============================================================
print("\n[9] GET list — 未登录 401")
resp = client.get("/api/roles")
check("HTTP 401", resp.status_code == 401, f"实际: {resp.status_code}")

# ============================================================
# 10. GET detail — 成功
# ============================================================
print("\n[10] GET detail — 成功")
resp = client.get(f"/api/roles/{admin_role.id}", headers=auth_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("name = administrator", data["name"] == "administrator")
check("display_name = 管理员", data["display_name"] == "管理员")
check("is_system = True", data["is_system"] is True)
check("有 permissions", "permissions" in data)
check("admin 有 3 个权限", len(data["permissions"]) == 3,
      f"实际: {len(data['permissions'])}")

# ============================================================
# 11. GET detail — 不存在
# ============================================================
print("\n[11] GET detail — 不存在")
resp = client.get("/api/roles/99999", headers=auth_headers)
check("HTTP 404", resp.status_code == 404, f"实际: {resp.status_code}")

# ============================================================
# 12. GET permissions — 成功
# ============================================================
print("\n[12] GET permissions — 成功")
resp = client.get(f"/api/roles/{tech_role.id}/permissions", headers=auth_headers)
check("HTTP 200", resp.status_code == 200, f"实际: {resp.status_code}")
data = resp.json()
check("返回 list", isinstance(data, list))
check("tech 有 1 个权限", len(data) == 1, f"实际: {len(data)}")
check("权限含 code", "code" in data[0])
check("权限含 name", "name" in data[0])
check("权限含 module", "module" in data[0])

# ============================================================
# 13. GET permissions — 返回 PermissionResponse[]
# ============================================================
print("\n[13] GET permissions — 返回 PermissionResponse[]")
perm = data[0]
check("code = task:read", perm["code"] == "task:read")
check("module = task", perm["module"] == "task")

# ============================================================
# 14. GET permissions — 不存在角色
# ============================================================
print("\n[14] GET permissions — 不存在角色")
resp = client.get("/api/roles/99999/permissions", headers=auth_headers)
check("HTTP 404", resp.status_code == 404, f"实际: {resp.status_code}")

# ============================================================
# 15. Router — Depends(get_db)
# ============================================================
print("\n[15] Router — Depends(get_db)")
router_content = (
    Path(__file__).parent.parent / "server" / "routers" / "role_router.py"
).read_text(encoding="utf-8")
check("Depends(get_db)", "Depends(get_db)" in router_content)

# ============================================================
# 16. Router — Depends(get_current_active_user)
# ============================================================
print("\n[16] Router — Depends(get_current_active_user)")
check("Depends(get_current_active_user)",
      "Depends(get_current_active_user)" in router_content)

# ============================================================
# 17. Router — 无 try/except
# ============================================================
print("\n[17] Router — 无 try/except")
check("Router 无 try:", "try:" not in router_content)
check("Router 无 except 块:", "except:" not in router_content
      and "except " not in router_content)

# ============================================================
# 18. Router — 不直接 JWT
# ============================================================
print("\n[18] Router — 不直接 JWT")
check("不直接 jwt", "jwt" not in router_content.lower())
check("不直接 decode", "decode" not in router_content)

# ============================================================
# 19. Router — 无业务逻辑
# ============================================================
print("\n[19] Router — 无业务逻辑")
check("不直接 hash_password", "hash_password" not in router_content)
check("不直接 create_access_token", "create_access_token" not in router_content)
check("不直接 import UserService", "UserService" not in router_content)
check("不直接 import AuthService", "AuthService" not in router_content)

# ============================================================
# 20. OpenAPI — tags
# ============================================================
print("\n[20] OpenAPI")
openapi = test_app.openapi()
paths = openapi.get("paths", {})

roles_paths = [p for p, methods in paths.items()
               for m, info in methods.items()
               if m != "options" and "Roles" in info.get("tags", [])]
check("Roles tag 接口数 = 3", len(roles_paths) == 3, f"实际: {len(roles_paths)}")

# ============================================================
# 21. OpenAPI — response_model
# ============================================================
print("\n[21] OpenAPI — response_model")
list_schema = paths.get("/api/roles", {}).get("get", {})
check("list 有 response_model", "200" in list_schema.get("responses", {}))

detail_schema = paths.get("/api/roles/{role_id}", {}).get("get", {})
check("detail 有 response_model", "200" in detail_schema.get("responses", {}))

perm_schema = paths.get("/api/roles/{role_id}/permissions", {}).get("get", {})
check("permissions 有 response_model", "200" in perm_schema.get("responses", {}))

# ============================================================
# 22. 全局异常处理 — JSON 格式
# ============================================================
print("\n[22] 全局异常处理 — JSON 格式")
resp = client.get("/api/roles/99999", headers=auth_headers)
data = resp.json()
check("统一格式: code", "code" in data)
check("统一格式: message", "message" in data)
check("统一格式: detail", "detail" in data)

# ============================================================
# 23. 无循环导入
# ============================================================
print("\n[23] 无循环导入")
import server.routers.role_router as rr

check("无循环导入", True)

# ============================================================
# 24. 禁止命名检查
# ============================================================
print("\n[24] 禁止命名检查")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException",
             "HTTPException", "JSONResponse"]
for name in forbidden:
    check(f"文件不含 {name}", name not in router_content)

# ============================================================
# 25. Type Hint / Docstring
# ============================================================
print("\n[25] Type Hint / Docstring")
import inspect

for fn_name in ["list_roles", "get_role", "get_role_permissions"]:
    fn = getattr(rr, fn_name, None)
    if fn is None:
        check(f"{fn_name} 存在", False)
        continue
    check(f"{fn_name} 有 docstring", fn.__doc__ is not None and len(fn.__doc__) > 20)
    sig = inspect.signature(fn)
    check(f"{fn_name} 有参数", len(sig.parameters) > 0)

# ============================================================
# 26. PEP8
# ============================================================
print("\n[26] PEP8")
check("文件以 docstring 开头", router_content.strip().startswith('"""'))
check("有 __all__", "__all__" in router_content)
check("无 print()", "print(" not in router_content)
check("无 TODO", "TODO" not in router_content)
check("无 FIXME", "FIXME" not in router_content)

# ============================================================
# 27. 仅 3 个接口
# ============================================================
print("\n[27] 仅 3 个接口")
# 计数非 OPTIONS 的接口
all_methods = []
for p, methods in paths.items():
    if p.startswith("/api/roles"):
        for m, info in methods.items():
            if m != "options":
                all_methods.append(f"{m.upper()} {p}")
check("仅 3 个接口", len(all_methods) == 3, f"实际: {all_methods}")

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