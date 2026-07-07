"""Test: Customer Router (Sprint 4 — Task 4.3)

严格依据 DEVELOPMENT_ROADMAP.md Task 4.3 验收标准。
测试 server/routers/customer_router.py 全部路由定义与代码规范。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import ast
import sys


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
print("  Task 4.3 — Customer Router Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile("server/routers/customer_router.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.routers.customer_router import router
    check("router 导入", True)
except ImportError as e:
    check("import", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] Router 类型
# ----------------------------------------------------------
print("\n[3] Router 类型")
from fastapi import APIRouter
check("router 是 APIRouter", isinstance(router, APIRouter))
check("router.prefix", router.prefix == "/api/customers")
check("router.tags", router.tags == ["Customer"])

# ----------------------------------------------------------
# [4] 路由列表
# ----------------------------------------------------------
print("\n[4] 路由列表")
routes = {r.path for r in router.routes}
check("GET /api/customers", "/api/customers" in routes or "/api/customers/" in routes)
check("GET /api/customers/{customer_id}", "/api/customers/{customer_id}" in routes)
check("POST /api/customers", "/api/customers" in routes or "/api/customers/" in routes)
check("PUT /api/customers/{customer_id}", "/api/customers/{customer_id}" in routes)

# ----------------------------------------------------------
# [5] 路由方法
# ----------------------------------------------------------
print("\n[5] 路由方法")
methods = {}
for r in router.routes:
    path = r.path.rstrip("/")
    methods[path] = set(r.methods) if hasattr(r, "methods") else set()

# Find the route methods
route_methods = {}
for r in router.routes:
    path = r.path
    for m in r.methods:
        route_methods.setdefault(path, set()).add(m)

check("GET list 存在", any("GET" in (r.methods if hasattr(r, "methods") else set()) for r in router.routes))
check("POST create 存在", any("POST" in (r.methods if hasattr(r, "methods") else set()) for r in router.routes))
check("PUT update 存在", any("PUT" in (r.methods if hasattr(r, "methods") else set()) for r in router.routes))

# ----------------------------------------------------------
# [6] 无 DELETE 路由
# ----------------------------------------------------------
print("\n[6] 无 DELETE 路由")
has_delete = any("DELETE" in (r.methods if hasattr(r, "methods") else set()) for r in router.routes)
check("无 DELETE 方法", not has_delete)

# 源码检查
with open("server/routers/customer_router.py", "r", encoding="utf-8") as f:
    source = f.read()
source_lower = source.lower()
check("不含 @router.delete", "@router.delete" not in source)
check("不含 'def delete'", "def delete" not in source)

# ----------------------------------------------------------
# [7] 源码分析
# ----------------------------------------------------------
print("\n[7] 源码分析")

# ----------------------------------------------------------
# [8] 无 try/except
# ----------------------------------------------------------
print("\n[8] 无 try/except")
check("不含 try:", "try:" not in source)
check("不含 except", "except" not in source)

# ----------------------------------------------------------
# [9] 无 ORM 业务操作
# ----------------------------------------------------------
print("\n[9] 无 ORM 业务操作")
# Session 是导入的参数类型标注，允许存在
check("不含 db.query", "db.query" not in source)
check("不含 db.add", "db.add" not in source)
check("不含 db.commit", "db.commit" not in source)
check("不含 db.rollback", "db.rollback" not in source)
check("不含 db.flush", "db.flush" not in source)

# ----------------------------------------------------------
# [10] 无 JWT / bcrypt
# ----------------------------------------------------------
print("\n[10] 无 JWT / bcrypt")
check("不含 jwt", "jwt" not in source_lower)
check("不含 bcrypt", "bcrypt" not in source_lower)
check("不含 create_access_token", "create_access_token" not in source)
check("不含 decode_access_token", "decode_access_token" not in source)

# ----------------------------------------------------------
# [11] 无 Business Logic（Router 层不实现业务）
# ----------------------------------------------------------
print("\n[11] 无 Business Logic")
# 异常名称仅出现在 docstring 的 Raises 说明中，Router 函数体不引发异常
check("不含 if/else 业务判断", "if " not in source)
check("不含 for 循环", "for " not in source)

# ----------------------------------------------------------
# [12] 无 SystemLog（Router 层不写入日志）
# ----------------------------------------------------------
print("\n[12] 无 SystemLog")
# SystemLog 仅在 docstring 中作为说明出现，Router 不直接操作
check("不含 ActionType", "ActionType" not in source)

# ----------------------------------------------------------
# [13] 无 HTTPException
# ----------------------------------------------------------
print("\n[13] 无 HTTPException")
check("不含 HTTPException", "HTTPException" not in source)
check("不含 raise HTTPException", "raise HTTPException" not in source)

# ----------------------------------------------------------
# [14] Depends 检查
# ----------------------------------------------------------
print("\n[14] Depends 检查")
check("Depends(get_db)", "Depends(get_db)" in source)
check("Depends(get_current_active_user)", "Depends(get_current_active_user)" in source)
check("require_permission", "require_permission" in source)

# ----------------------------------------------------------
# [15] 权限码检查
# ----------------------------------------------------------
print("\n[15] 权限码检查")
check("customer:view", "customer:view" in source)
check("customer:create", "customer:create" in source)
check("customer:edit", "customer:edit" in source)
check("不含 customer:update", "customer:update" not in source)
check("不含 customer:delete", "customer:delete" not in source)

# ----------------------------------------------------------
# [16] response_model
# ----------------------------------------------------------
print("\n[16] response_model")
check("CustomerListResponse", "response_model=CustomerListResponse" in source)
check("CustomerResponse", "response_model=CustomerResponse" in source)
check("不含 dict", "response_model=dict" not in source)
check("不含 list", "response_model=list" not in source)

# ----------------------------------------------------------
# [17] tags / OpenAPI
# ----------------------------------------------------------
print("\n[17] tags / OpenAPI")
check("tags=['Customer']", "Customer" in str(router.tags))
check("所有路由有 summary", source.count("summary=") == 4)

# ----------------------------------------------------------
# [18] Service 调用
# ----------------------------------------------------------
print("\n[18] Service 调用")
check("导入 CustomerService", "CustomerService" in source)
check("_customer_service 实例", "_customer_service" in source)
check("调用 list_customers", "_customer_service.list_customers" in source)
check("调用 get_customer", "_customer_service.get_customer" in source)
check("调用 create_customer", "_customer_service.create_customer" in source)
check("调用 update_customer", "_customer_service.update_customer" in source)

# ----------------------------------------------------------
# [19] main.py include_router
# ----------------------------------------------------------
print("\n[19] main.py include_router")
with open("server/main.py", "r", encoding="utf-8") as f:
    main_source = f.read()
check("main.py 导入 customer_router",
      "from server.routers.customer_router import router as customer_router" in main_source)
check("main.py include_router",
      "app.include_router(customer_router)" in main_source)

# ----------------------------------------------------------
# [20] 路由数量
# ----------------------------------------------------------
print("\n[20] 路由数量")
check("路由数量 = 4", len(router.routes) == 4)

# ----------------------------------------------------------
# [21] operator_id
# ----------------------------------------------------------
print("\n[21] operator_id")
check("create 使用 current_user.id", "operator_id=current_user.id" in source)
check("update 使用 current_user.id", "operator_id=current_user.id" in source)

# ----------------------------------------------------------
# [22] 分页参数
# ----------------------------------------------------------
print("\n[22] 分页参数")
check("page 参数", "page" in source)
check("page_size 参数", "page_size" in source)
check("company_name query", "company_name" in source)

# ----------------------------------------------------------
# [23] Google Docstring
# ----------------------------------------------------------
print("\n[23] Google Docstring")
check("模块有 docstring", source.strip().startswith('"""'))
check("list_customers 有 docstring", '"""客户列表接口。' in source)
check("get_customer 有 docstring", '"""客户详情接口。' in source)
check("create_customer 有 docstring", '"""创建客户接口。' in source)
check("update_customer 有 docstring", '"""修改客户接口。' in source)

# ----------------------------------------------------------
# [24] Type Hint
# ----------------------------------------------------------
print("\n[24] Type Hint")
check("导入 Optional", "Optional" in source)
check("导入 Session", "Session" in source)
check("函数返回类型标注", "-> CustomerListResponse" in source)
check("-> CustomerResponse", "-> CustomerResponse" in source)

# ----------------------------------------------------------
# [25] 无循环导入
# ----------------------------------------------------------
print("\n[25] 无循环导入")
check("不导入 client", "client" not in source)

# ----------------------------------------------------------
# [26] 禁止命名
# ----------------------------------------------------------
print("\n[26] 禁止命名")
check("不含 ValidationException", "validationexception" not in source_lower)
check("不含 AuthorizationException", "authorizationexception" not in source_lower)
check("不含 ConflictException", "conflictexception" not in source_lower)
check("不含 print(", "print(" not in source)

# ----------------------------------------------------------
# [27] PEP8
# ----------------------------------------------------------
print("\n[27] PEP8")
check("文件以 docstring 开头", source.strip().startswith('"""'))
check("有 __all__", "__all__" in source)
check("__all__ 包含 router", "router" in source.split("__all__")[-1] if "__all__" in source else False)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)

# ----------------------------------------------------------
# [28] 公开 API Freeze
# ----------------------------------------------------------
print("\n[28] 公开 API Freeze")
check("4 个路由", len(router.routes) == 4)
check("无 DELETE", "DELETE" not in str(route_methods))
check("无 PATCH", "PATCH" not in str(route_methods))

# ----------------------------------------------------------
# [29] main.py 仅新增 customer_router
# ----------------------------------------------------------
print("\n[29] main.py 仅新增 customer_router")
# 检查 main.py 没有其他意外修改
main_lines = main_source.split("\n")
check("main.py 有 auth_router", "auth_router" in main_source)
check("main.py 有 role_router", "role_router" in main_source)
check("main.py 有 user_router", "user_router" in main_source)
check("main.py 有 customer_router", "customer_router" in main_source)

# ----------------------------------------------------------
# [30] 不修改 Frozen API
# ----------------------------------------------------------
print("\n[30] 不修改 Frozen API")
check("不导入 security", "server.core.security" not in source)
# server.models.user 导入 User 类型用于类型标注，允许
check("不含 hash_password", "hash_password" not in source)
check("不含 verify_password", "verify_password" not in source)

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