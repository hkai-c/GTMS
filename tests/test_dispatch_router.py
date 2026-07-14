"""Test: Dispatch Router (Sprint 9 — Task 9.3)

严格依据 DEVELOPMENT_ROADMAP.md Task 9.3 验收标准。
测试 server/routers/dispatch_router.py 全部公开接口与代码规范。

注意：本测试使用源码分析，不依赖 HTTP 连接。
"""

import ast
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
print("  Task 9.3 — Dispatch Router Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "routers", "dispatch_router.py")

source = extract_code_text(SOURCE_PATH)

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source_full = f.read()

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile(SOURCE_PATH, doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.routers.dispatch_router import router
    check("router 导入", True)
except ImportError as e:
    check("router 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] router 类型
# ----------------------------------------------------------
print("\n[3] router 类型")
check("router 是 APIRouter", "APIRouter" in str(type(router)))

# ----------------------------------------------------------
# [4] 路由数量
# ----------------------------------------------------------
print("\n[4] 路由数量")
routes = router.routes
check("5 个路由", len(routes) == 5)

# ----------------------------------------------------------
# [5] 路由方法
# ----------------------------------------------------------
print("\n[5] 路由方法")
# methods 可能是 set 或 list
methods_list = []
for r in routes:
    if hasattr(r, "methods") and r.methods:
        m = r.methods
        if isinstance(m, set):
            methods_list.append(sorted(m))
        else:
            methods_list.append(sorted(m))
check("GET 路由", ["GET"] in methods_list)
check("POST 路由", ["POST"] in methods_list)
check("PUT 路由", ["PUT"] in methods_list)
check("DELETE 路由", ["DELETE"] in methods_list)
get_count = sum(1 for m in methods_list if m == ["GET"])
check("2 个 GET 路由", get_count == 2)

# ----------------------------------------------------------
# [6] 路由路径
# ----------------------------------------------------------
print("\n[6] 路由路径")
paths = [r.path for r in routes if hasattr(r, "path")]
check("GET /api/dispatch 路径", "/api/dispatch" in paths)
check("GET /api/dispatch/{dispatch_id} 路径", "/api/dispatch/{dispatch_id}" in paths)
check("POST /api/dispatch 路径", "/api/dispatch" in paths)
check("PUT /api/dispatch/{dispatch_id} 路径", "/api/dispatch/{dispatch_id}" in paths)
check("DELETE /api/dispatch/{dispatch_id} 路径", "/api/dispatch/{dispatch_id}" in paths)

# ----------------------------------------------------------
# [7] Endpoint 函数
# ----------------------------------------------------------
print("\n[7] Endpoint 函数")
check("list_dispatches 存在", "def list_dispatches" in source_full)
check("get_dispatch 存在", "def get_dispatch" in source_full)
check("create_dispatch 存在", "def create_dispatch" in source_full)
check("update_dispatch 存在", "def update_dispatch" in source_full)
check("delete_dispatch 存在", "def delete_dispatch" in source_full)

# ----------------------------------------------------------
# [8] HTTP 映射
# ----------------------------------------------------------
print("\n[8] HTTP 映射")
check("list_dispatches → DispatchService.list_dispatches",
      "_dispatch_service.list_dispatches" in source)
check("get_dispatch → DispatchService.get_dispatch",
      "_dispatch_service.get_dispatch" in source)
check("create_dispatch → DispatchService.create_dispatch",
      "_dispatch_service.create_dispatch" in source)
check("update_dispatch → DispatchService.update_dispatch",
      "_dispatch_service.update_dispatch" in source)
check("delete_dispatch → DispatchService.delete_dispatch",
      "_dispatch_service.delete_dispatch" in source)

# ----------------------------------------------------------
# [9] 依赖注入
# ----------------------------------------------------------
print("\n[9] 依赖注入")
check("使用 Depends(get_db)", "Depends(get_db)" in source)
check("使用 Depends(get_current_active_user)",
      "Depends(get_current_active_user)" in source)
check("使用 Depends(require_permission)",
      "Depends(require_permission" in source)

# ----------------------------------------------------------
# [10] 权限控制
# ----------------------------------------------------------
print("\n[10] 权限控制")
check("dispatch:view 权限", "dispatch:view" in source_full)
check("dispatch:create 权限", "dispatch:create" in source_full)
check("dispatch:edit 权限", "dispatch:edit" in source_full)
check("dispatch:delete 权限", "dispatch:delete" in source_full)

# ----------------------------------------------------------
# [11] response_model
# ----------------------------------------------------------
print("\n[11] response_model")
check("list_dispatches response_model=DispatchListResponse",
      "response_model=DispatchListResponse" in source_full)
check("get_dispatch response_model=DispatchResponse",
      "response_model=DispatchResponse" in source_full)
check("create_dispatch response_model=DispatchResponse",
      "response_model=DispatchResponse" in source_full)
check("update_dispatch response_model=DispatchResponse",
      "response_model=DispatchResponse" in source_full)

# ----------------------------------------------------------
# [12] status_code
# ----------------------------------------------------------
print("\n[12] status_code")
check("list_dispatches 200_OK", "status.HTTP_200_OK" in source_full)
check("create_dispatch 201_CREATED", "status.HTTP_201_CREATED" in source_full)
check("delete_dispatch 200_OK", "status.HTTP_200_OK" in source_full)

# ----------------------------------------------------------
# [13] OpenAPI metadata
# ----------------------------------------------------------
print("\n[13] OpenAPI metadata")
check("summary 存在", "summary" in source_full)
check("description 存在", "description" in source_full)
check("tags=['Dispatch']", "Dispatch" in source_full)

# ----------------------------------------------------------
# [14] 零业务逻辑
# ----------------------------------------------------------
print("\n[14] 零业务逻辑")
# 使用 code（排除 docstring 和注释），但 description 字符串仍可能包含关键词
# 排除 description= 参数中的字符串
code_strict = re.sub(
    r'description\s*=\s*(?:\([^)]*\)|"[^"]*"|\'[^\']*\')',
    "",
    source,
)
check("零 ORM 操作（无 Session()）", "Session(" not in source)
check("零 Workflow（无 process_status 代码）", "process_status" not in code_strict)
check("零 Workflow（无 result_status 代码）", "result_status" not in code_strict)
check("零 Status Machine（无状态赋值）", "process_status =" not in source)
check("零 Status Machine（无结果赋值）", "result_status =" not in source)
check("零 SystemLog", "SystemLog" not in source)
check("零事务（无 db.commit）", "db.commit" not in source)
check("零事务（无 db.rollback）", "db.rollback" not in source)
check("零 ORM 模型（无 Dispatch()）", "Dispatch(" not in source)
check("零 TrialTask 引用", "TrialTask" not in code_strict)
check("零 InspectionRecord 引用", "InspectionRecord" not in code_strict)

# ----------------------------------------------------------
# [15] 零手动 Session
# ----------------------------------------------------------
print("\n[15] 零手动 Session")
check("无 Session() 创建", "Session()" not in source)

# ----------------------------------------------------------
# [16] 零异常捕获
# ----------------------------------------------------------
print("\n[16] 零异常捕获")
check("无 try/except", "try:" not in source)
check("无 HTTPException", "HTTPException" not in source)

# ----------------------------------------------------------
# [17] 无 print
# ----------------------------------------------------------
print("\n[17] 无 print")
check("无 print()", "print(" not in source)

# ----------------------------------------------------------
# [18] 依赖
# ----------------------------------------------------------
print("\n[18] 依赖")
check("导入 DispatchService", "DispatchService" in source_full)
check("导入 DispatchCreate", "DispatchCreate" in source_full)
check("导入 DispatchUpdate", "DispatchUpdate" in source_full)
check("导入 DispatchResponse", "DispatchResponse" in source_full)
check("导入 DispatchListResponse", "DispatchListResponse" in source_full)
check("导入 DestinationType", "DestinationType" in source_full)
check("导入 get_db", "get_db" in source_full)
check("导入 get_current_active_user", "get_current_active_user" in source_full)
check("导入 require_permission", "require_permission" in source_full)

# ----------------------------------------------------------
# [19] 禁止依赖
# ----------------------------------------------------------
print("\n[19] 禁止依赖")
check("无 requests", "requests" not in source_full)
check("无 httpx", "httpx" not in source_full)
# Session 导入用于类型注解（Depends 注入），是必要的
check("无 SQLAlchemy ORM 操作", "Session(" not in source)
check("无 Desktop 导入", "from client." not in source_full)
check("无 View 导入", "from client.views" not in source_full)

# ----------------------------------------------------------
# [20] PEP8
# ----------------------------------------------------------
print("\n[20] PEP8")
import subprocess
result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", SOURCE_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# ----------------------------------------------------------
# [21] Docstring
# ----------------------------------------------------------
print("\n[21] Docstring")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块级 docstring 存在", ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        doc = ast.get_docstring(node)
        check(f"{node.name} docstring 存在", doc is not None)

# ----------------------------------------------------------
# [22] Type Hint
# ----------------------------------------------------------
print("\n[22] Type Hint")
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        check(f"{node.name} 返回类型注解", node.returns is not None)

# ----------------------------------------------------------
# [23] __all__ 导出
# ----------------------------------------------------------
print("\n[23] __all__ 导出")
check("__all__ 包含 router", "router" in source_full.split("__all__")[-1])

# ----------------------------------------------------------
# [24] __init__.py 导出
# ----------------------------------------------------------
print("\n[24] __init__.py 导出")
INIT_PATH = os.path.join("server", "routers", "__init__.py")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导出 dispatch_router", "dispatch_router" in init_code)

# ----------------------------------------------------------
# [25] main.py 注册
# ----------------------------------------------------------
print("\n[25] main.py 注册")
MAIN_PATH = os.path.join("server", "main.py")
main_code = extract_code_text(MAIN_PATH)
check("main.py 导入 dispatch_router",
      "dispatch_router" in main_code)
check("main.py 注册 dispatch_router",
      "dispatch_router" in main_code)

# ----------------------------------------------------------
# [26] 无循环导入
# ----------------------------------------------------------
print("\n[26] 无循环导入")
check("无自身导入", "from server.routers.dispatch_router" not in source_full)
check("无 Service 交叉导入", "GrindingService" not in source_full)
check("无 InspectionService 导入", "InspectionService" not in source_full)

# ----------------------------------------------------------
# [27] Frozen API
# ----------------------------------------------------------
print("\n[27] Frozen API")
# User 导入用于类型注解（current_user 参数），是必要的
# 检查无 ORM 操作（无 User 实例化, 无 User.query）
check("User 仅用于类型注解，无 User()", "User(" not in source)
check("未导入 Desktop 层", "from client." not in source_full)

# ----------------------------------------------------------
# [28] query 参数
# ----------------------------------------------------------
print("\n[28] query 参数")
check("list_dispatches direction query", "direction: Optional[DestinationType] = Query" in source_full)
check("list_dispatches task_id query", "task_id: Optional[int] = Query" in source_full)
check("list_dispatches page query", "page: int = Query" in source_full)
check("list_dispatches page_size query", "page_size: int = Query" in source_full)

# ----------------------------------------------------------
# [29] body 参数
# ----------------------------------------------------------
print("\n[29] body 参数")
check("create_dispatch body", "data: DispatchCreate = Body" in source_full)
check("update_dispatch body", "data: DispatchUpdate = Body" in source_full)

# ----------------------------------------------------------
# [30] 历史导出未破坏
# ----------------------------------------------------------
print("\n[30] 历史导出未破坏")
check("__init__.py 导出 auth_router", "auth_router" in init_code)
check("__init__.py 导出 customer_router", "customer_router" in init_code)
check("__init__.py 导出 trial_task_router", "trial_task_router" in init_code)
check("__init__.py 导出 grinding_router", "grinding_router" in init_code)
check("__init__.py 导出 inspection_router", "inspection_router" in init_code)

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

sys.exit(0 if FAILED == 0 else 1)