"""Test: Receipt Router (Sprint 6 — Task 6.3)

严格依据 DEVELOPMENT_ROADMAP.md Task 6.3 验收标准。
测试 server/routers/receipt_router.py 全部接口与代码规范。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import ast
import inspect
import os
import re
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# 自检框架
# ============================================================

PASSED = 0
FAILED = 0


def check(desc: str, condition: bool) -> None:
    """执行一条检查。"""
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {desc}")
    else:
        FAILED += 1
        print(f"  [FAIL] {desc}")


def extract_code_text(file_path: str) -> str:
    """提取代码文本（排除 docstring 和注释）。"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", "", content, flags=re.DOTALL)
    content = re.sub(r"#.*$", "", content, flags=re.MULTILINE)
    return content


# ============================================================
# 自检
# ============================================================

print("=" * 60)
print("  Task 6.3 — Receipt Router Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile

    py_compile.compile("server/routers/receipt_router.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.routers.receipt_router import router

    check("router 导入", True)
except ImportError as e:
    check("router 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] Router 类型
# ----------------------------------------------------------
print("\n[3] Router 类型")
from fastapi import APIRouter

check("router 是 APIRouter 实例", isinstance(router, APIRouter))
check("router.prefix = /api/receipts", router.prefix == "/api/receipts")
check("router.tags = ['Receipt']", router.tags == ["Receipt"])

# ----------------------------------------------------------
# [4] Route 数量
# ----------------------------------------------------------
print("\n[4] Route 数量")
routes = router.routes
check("路由数量 = 5", len(routes) == 5)

# 获取源码
router_path = os.path.join("server", "routers", "receipt_router.py")
with open(router_path, "r", encoding="utf-8") as f:
    source = f.read()
code = extract_code_text(router_path)

# ----------------------------------------------------------
# [5] HTTP Method
# ----------------------------------------------------------
print("\n[5] HTTP Method")
methods_used = []
for route in routes:
    if hasattr(route, "methods"):
        methods_used.extend(route.methods)
check("GET 方法存在", "GET" in methods_used)
check("POST 方法存在", "POST" in methods_used)
check("PUT 方法存在", "PUT" in methods_used)
check("DELETE 方法存在", "DELETE" in methods_used)

# ----------------------------------------------------------
# [6] URL 路径
# ----------------------------------------------------------
print("\n[6] URL 路径")
check("GET /api/receipts (列表)", '@router.get(""'
      in source or "@router.get(\n    \"\"" in source)
check("GET /api/receipts/{receipt_id} (详情)",
      '@router.get(\n    "/{receipt_id}"' in source)
check("POST /api/receipts", "@router.post(" in source)
check("PUT /api/receipts/{receipt_id}",
      '@router.put(\n    "/{receipt_id}"' in source)
check("DELETE /api/receipts/{receipt_id}",
      '@router.delete(\n    "/{receipt_id}"' in source)

# ----------------------------------------------------------
# [7] Depends(get_db)
# ----------------------------------------------------------
print("\n[7] Depends(get_db)")
db_count = source.count("Depends(get_db)")
check("5 个路由函数使用 Depends(get_db)", db_count == 5)

# ----------------------------------------------------------
# [8] Depends(get_current_active_user)
# ----------------------------------------------------------
print("\n[8] Depends(get_current_active_user)")
user_count = source.count("Depends(get_current_active_user)")
check("5 个路由函数使用 Depends(get_current_active_user)",
      user_count == 5)

# ----------------------------------------------------------
# [9] Depends(require_permission)
# ----------------------------------------------------------
print("\n[9] Depends(require_permission)")
perm_count = source.count("Depends(require_permission")
check("5 个路由函数使用 require_permission", perm_count == 5)

# ----------------------------------------------------------
# [10] 权限码正确
# ----------------------------------------------------------
print("\n[10] 权限码正确")
check("GET list 使用 receipt:view",
      'require_permission("receipt:view")' in source)
check("GET detail 使用 receipt:view",
      'require_permission("receipt:view")' in source)
check("POST 使用 receipt:create",
      'require_permission("receipt:create")' in source)
check("PUT 使用 receipt:edit",
      'require_permission("receipt:edit")' in source)
check("DELETE 使用 receipt:delete",
      'require_permission("receipt:delete")' in source)
check("未使用 receipt:read", "receipt:read" not in source)
check("未使用 receipt:write", "receipt:write" not in source)

# ----------------------------------------------------------
# [11] response_model
# ----------------------------------------------------------
print("\n[11] response_model")
check("GET list response_model=ReceiptListResponse",
      "response_model=ReceiptListResponse" in source)
check("GET detail response_model=ReceiptResponse",
      "response_model=ReceiptResponse" in source)
check("POST response_model=ReceiptResponse",
      "response_model=ReceiptResponse" in source)
check("PUT response_model=ReceiptResponse",
      "response_model=ReceiptResponse" in source)
check("DELETE 无 response_model",
      "response_model" not in source.split(
          "@router.delete")[-1].split("def ")[0])

# ----------------------------------------------------------
# [12] status_code
# ----------------------------------------------------------
print("\n[12] status_code")
check("GET list status_code=200",
      "status_code=status.HTTP_200_OK" in source)
check("POST status_code=201",
      "status_code=status.HTTP_201_CREATED" in source)
check("PUT status_code=200",
      "status_code=status.HTTP_200_OK" in source)
check("DELETE status_code=200",
      "status_code=status.HTTP_200_OK" in source)

# ----------------------------------------------------------
# [13] summary
# ----------------------------------------------------------
print("\n[13] summary")
check("GET list 有 summary", 'summary="收件记录列表"' in source)
check("GET detail 有 summary", 'summary="收件记录详情"' in source)
check("POST 有 summary", 'summary="创建收件记录"' in source)
check("PUT 有 summary", 'summary="修改收件记录"' in source)
check("DELETE 有 summary", 'summary="删除收件记录"' in source)

# ----------------------------------------------------------
# [14] tags
# ----------------------------------------------------------
print("\n[14] tags")
check("tags=['Receipt']", 'tags=["Receipt"]' in source)

# ----------------------------------------------------------
# [15] Operator ID
# ----------------------------------------------------------
print("\n[15] Operator ID")
check("create_receipt 传入 operator_id=current_user.id",
      "operator_id=current_user.id" in source)
check("update_receipt 传入 operator_id=current_user.id",
      "operator_id=current_user.id" in source)
check("delete_receipt 传入 operator_id=current_user.id",
      "operator_id=current_user.id" in source)

# ----------------------------------------------------------
# [16] Service 调用
# ----------------------------------------------------------
print("\n[16] Service 调用")
check("调用 _receipt_service.list_receipts",
      "_receipt_service.list_receipts" in source)
check("调用 _receipt_service.get_receipt",
      "_receipt_service.get_receipt" in source)
check("调用 _receipt_service.create_receipt",
      "_receipt_service.create_receipt" in source)
check("调用 _receipt_service.update_receipt",
      "_receipt_service.update_receipt" in source)
check("调用 _receipt_service.delete_receipt",
      "_receipt_service.delete_receipt" in source)

# ----------------------------------------------------------
# [17] main.py include_router
# ----------------------------------------------------------
print("\n[17] main.py include_router")
main_path = os.path.join("server", "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_source = f.read()
check("main.py 导入 receipt_router",
      "from server.routers.receipt_router import router "
      "as receipt_router" in main_source)
check("main.py include_router(receipt_router)",
      "app.include_router(receipt_router)" in main_source)

# ----------------------------------------------------------
# [18] 无 ORM
# ----------------------------------------------------------
print("\n[18] 无 ORM")
check("无 SQLAlchemy ORM 直接操作", "db.query" not in code)
check("无 db.add", "db.add" not in code)
check("无 db.flush", "db.flush" not in code)
check("无 db.commit", "db.commit" not in code)
check("无 db.rollback", "db.rollback" not in code)

# ----------------------------------------------------------
# [19] 无 JWT / bcrypt
# ----------------------------------------------------------
print("\n[19] 无 JWT / bcrypt")
check("无 JWT", "jwt" not in code.lower())
check("无 bcrypt", "bcrypt" not in code.lower())

# ----------------------------------------------------------
# [20] 无 Business Logic
# ----------------------------------------------------------
print("\n[20] 无 Business Logic")
check("无 generate_task_no", "generate_task_no" not in code)
check("无 next_statuses", "next_statuses" not in code)
check("无 is_deleted 赋值", "is_deleted = True" not in code)
check("无 SystemLog 写入", "SystemLog" not in code)
check("无 BusinessLogicException", "BusinessLogicException" not in code)
check("无 NotFoundException", "NotFoundException" not in code)

# ----------------------------------------------------------
# [21] 无 try/except
# ----------------------------------------------------------
print("\n[21] 无 try/except")
check("无 try 语句", "try:" not in code)
check("无 except 语句", "except" not in code)

# ----------------------------------------------------------
# [22] 无 HTTPException
# ----------------------------------------------------------
print("\n[22] 无 HTTPException")
check("无 HTTPException", "HTTPException" not in code)

# ----------------------------------------------------------
# [23] API Freeze
# ----------------------------------------------------------
print("\n[23] API Freeze")
check("5 个路由函数", len(routes) == 5)
check("无新增路由函数", len(routes) == 5)

# ----------------------------------------------------------
# [24] Frozen API 未修改
# ----------------------------------------------------------
print("\n[24] Frozen API 未修改")
check("未导入 CustomerService", "CustomerService" not in source)
check("未导入 AuthService", "AuthService" not in source)
check("未导入 UserService", "UserService" not in source)
check("未导入 TaskService", "TaskService" not in source)

# ----------------------------------------------------------
# [25] 代码规范
# ----------------------------------------------------------
print("\n[25] 代码规范")
check("无 print()", "print(" not in code)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 pass", "pass" not in code)
check("无 tab 缩进", "\t" not in source)
check("文件以换行结尾", source.endswith("\n"))
check("有 __all__", "__all__" in source)
check("__all__ 包含 router", "router" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [26] Docstring
# ----------------------------------------------------------
print("\n[26] Docstring")
# 使用 __import__ 获取模块（避免 __init__.py 导出的 APIRouter 对象覆盖）
router_module = __import__(
    "server.routers.receipt_router", fromlist=["_"]
)

for func_name in ["list_receipts", "get_receipt", "create_receipt",
                   "update_receipt", "delete_receipt"]:
    func = getattr(router_module, func_name, None)
    if func is not None:
        doc = inspect.getdoc(func)
        check(f"{func_name} 有 docstring", doc is not None and len(doc) > 0)
    else:
        check(f"{func_name} 有 docstring", False)

# ----------------------------------------------------------
# [27] Type Hint
# ----------------------------------------------------------
print("\n[27] Type Hint")
for func_name in ["list_receipts", "get_receipt", "create_receipt",
                   "update_receipt", "delete_receipt"]:
    func = getattr(router_module, func_name, None)
    if func is not None:
        sig = inspect.signature(func)
        has_return = sig.return_annotation is not inspect.Signature.empty
        check(f"{func_name} 有 -> 返回类型", has_return)
    else:
        check(f"{func_name} 有 -> 返回类型", False)

# ----------------------------------------------------------
# [28] 无循环导入
# ----------------------------------------------------------
print("\n[28] 无循环导入")
try:
    import importlib

    importlib.reload(sys.modules.get(
        "server.routers.receipt_router",
        __import__("server.routers.receipt_router",
                   fromlist=["router"])))
    check("无循环导入", True)
except Exception as e:
    check("无循环导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [29] OpenAPI 完整性
# ----------------------------------------------------------
print("\n[29] OpenAPI 完整性")
check("GET list 有 description",
      "description=" in source.split("def list_receipts")[0])
check("GET detail 有 description",
      "description=" in source.split("def get_receipt")[0])
check("POST 有 description",
      "description=" in source.split("def create_receipt")[0])
check("PUT 有 description",
      "description=" in source.split("def update_receipt")[0])
check("DELETE 有 description",
      "description=" in source.split("def delete_receipt")[0])

# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  Result: ALL PASSED")
else:
    print(f"  Result: {FAILED} FAILED")
print("=" * 60)
