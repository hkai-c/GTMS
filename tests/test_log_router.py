"""Test: Log Router (Sprint 11 — Task 11.3)

严格依据 DEVELOPMENT_ROADMAP.md Task 11.3 验收标准。
测试 server/routers/log_router.py 全部公开接口与代码规范。

注意：本测试使用源码分析，不依赖 HTTP 连接。
"""

import ast
import os
import re
import subprocess
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
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
print("  Task 11.3 — Log Router Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "routers", "log_router.py")

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
    from server.routers.log_router import router
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
check("4 个路由", len(routes) == 4)

# ----------------------------------------------------------
# [5] 路由方法
# ----------------------------------------------------------
print("\n[5] 路由方法")
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
get_count = sum(1 for m in methods_list if m == ["GET"])
check("2 个 GET 路由", get_count == 2)
post_count = sum(1 for m in methods_list if m == ["POST"])
check("2 个 POST 路由", post_count == 2)

# ----------------------------------------------------------
# [6] 路由路径
# ----------------------------------------------------------
print("\n[6] 路由路径")
paths = [r.path for r in routes if hasattr(r, "path")]
check("GET /api/log 路径", "/api/log" in paths)
check("GET /api/log/{log_id} 路径",
      "/api/log/{log_id}" in paths)
check("POST /api/log 路径", "/api/log" in paths)
check("POST /api/log/export 路径",
      "/api/log/export" in paths)

# ----------------------------------------------------------
# [7] Endpoint 函数
# ----------------------------------------------------------
print("\n[7] Endpoint 函数")
check("list_logs 存在", "def list_logs" in source_full)
check("get_log 存在", "def get_log" in source_full)
check("create_log 存在", "def create_log" in source_full)
check("export_logs 存在", "def export_logs" in source_full)

# ----------------------------------------------------------
# [8] HTTP 映射
# ----------------------------------------------------------
print("\n[8] HTTP 映射")
check("list_logs → LogService.list_logs",
      "_log_service.list_logs" in source)
check("get_log → LogService.get_log",
      "_log_service.get_log" in source)
check("create_log → LogService.create_log",
      "_log_service.create_log" in source)
check("export_logs → LogService.export_logs",
      "_log_service.export_logs" in source)

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
check("log:view 权限", "log:view" in source_full)
check("system 权限（create_log）",
      '"system"' in source_full
      or "'system'" in source_full)

# ----------------------------------------------------------
# [11] response_model
# ----------------------------------------------------------
print("\n[11] response_model")
check("list_logs response_model=LogListResponse",
      "response_model=LogListResponse" in source_full)
check("get_log response_model=LogResponse",
      "response_model=LogResponse" in source_full)
check("create_log response_model=LogResponse",
      "response_model=LogResponse" in source_full)
check("export_logs response_model=list[dict]",
      "response_model=list[dict]" in source_full)

# ----------------------------------------------------------
# [12] status_code
# ----------------------------------------------------------
print("\n[12] status_code")
check("list_logs 200_OK",
      "status.HTTP_200_OK" in source_full)
check("get_log 200_OK",
      "status.HTTP_200_OK" in source_full)
check("create_log 201_CREATED",
      "status.HTTP_201_CREATED" in source_full)
check("export_logs 200_OK",
      "status.HTTP_200_OK" in source_full)

# ----------------------------------------------------------
# [13] OpenAPI metadata
# ----------------------------------------------------------
print("\n[13] OpenAPI metadata")
check("summary 存在", "summary" in source_full)
check("description 存在", "description" in source_full)
check("tags=['Log']", "Log" in source_full)

# ----------------------------------------------------------
# [14] 零业务逻辑
# ----------------------------------------------------------
print("\n[14] 零业务逻辑")
check("零 ORM 操作（无 Session()）", "Session(" not in source)
check("零 Workflow（无 process_status）",
      "process_status" not in source)
check("零 Status Machine（无 result_status）",
      "result_status" not in source)
check("零 SystemLog", "SystemLog" not in source)
check("零事务（无 db.commit）", "db.commit" not in source)
check("零事务（无 db.rollback）", "db.rollback" not in source)
check("零 Aggregation", "func." not in source)
check("零 Excel 导出", "openpyxl" not in source)
check("零 xlsxwriter", "xlsxwriter" not in source)
check("零 CSV", "csv" not in source)

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
check("导入 LogService", "LogService" in source_full)
check("导入 LogBase", "LogBase" in source_full)
check("导入 LogListResponse", "LogListResponse" in source_full)
check("导入 LogQuery", "LogQuery" in source_full)
check("导入 LogResponse", "LogResponse" in source_full)
check("导入 get_db", "get_db" in source_full)
check("导入 get_current_active_user",
      "get_current_active_user" in source_full)
check("导入 require_permission", "require_permission" in source_full)
check("导入 ActionType", "ActionType" in source_full)

# ----------------------------------------------------------
# [19] 禁止依赖
# ----------------------------------------------------------
print("\n[19] 禁止依赖")
check("无 requests", "requests" not in source_full)
check("无 httpx", "httpx" not in source_full)
check("无 SQLAlchemy ORM 操作", "Session(" not in source)
check("无 Desktop 导入", "from client." not in source_full)
check("无 View 导入", "from client.views" not in source_full)
check("无 logger.info", "logger.info" not in source)

# ----------------------------------------------------------
# [20] PEP8
# ----------------------------------------------------------
print("\n[20] PEP8")
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
check("模块级 docstring 存在",
      ast.get_docstring(tree) is not None)
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
        check(f"{node.name} 返回类型注解",
              node.returns is not None)

# ----------------------------------------------------------
# [23] __all__ 导出
# ----------------------------------------------------------
print("\n[23] __all__ 导出")
check("__all__ 包含 router",
      "router" in source_full.split("__all__")[-1])

# ----------------------------------------------------------
# [24] __init__.py 导出
# ----------------------------------------------------------
print("\n[24] __init__.py 导出")
INIT_PATH = os.path.join("server", "routers", "__init__.py")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导出 log_router", "log_router" in init_code)

# ----------------------------------------------------------
# [25] main.py 注册
# ----------------------------------------------------------
print("\n[25] main.py 注册")
MAIN_PATH = os.path.join("server", "main.py")
main_code = extract_code_text(MAIN_PATH)
check("main.py 导入 log_router", "log_router" in main_code)
check("main.py 注册 log_router",
      "log_router" in main_code)

# ----------------------------------------------------------
# [26] 无循环导入
# ----------------------------------------------------------
print("\n[26] 无循环导入")
check("无自身导入",
      "from server.routers.log_router" not in source_full)
check("无 Service 交叉导入",
      "TaskService" not in source_full)
check("无 DispatchService 导入",
      "DispatchService" not in source_full)

# ----------------------------------------------------------
# [27] Frozen API
# ----------------------------------------------------------
print("\n[27] Frozen API")
check("User 仅用于类型注解，无 User()", "User(" not in source)
check("未导入 Desktop 层",
      "from client." not in source_full)

# ----------------------------------------------------------
# [28] query 参数（list_logs）
# ----------------------------------------------------------
print("\n[28] query 参数（list_logs）")
check("operator_id query",
      "operator_id: Optional[int] = Query" in source_full)
check("operation query",
      "operation: Optional[ActionType] = Query" in source_full)
check("module query",
      "module: Optional[str] = Query" in source_full)
check("keyword query",
      "keyword: Optional[str] = Query" in source_full)
check("start_time query",
      "start_time: Optional[datetime] = Query" in source_full)
check("end_time query",
      "end_time: Optional[datetime] = Query" in source_full)
check("sort_by query",
      "sort_by: str = Query" in source_full)
check("sort_order query",
      "sort_order: str = Query" in source_full)
check("page query", "page: int = Query" in source_full)
check("page_size query",
      "page_size: int = Query" in source_full)

# ----------------------------------------------------------
# [29] body 参数
# ----------------------------------------------------------
print("\n[29] body 参数")
check("create_log body",
      "data: LogBase = Body" in source_full)
check("export_logs body",
      "data: LogQuery = Body" in source_full)

# ----------------------------------------------------------
# [30] LogQuery 构造
# ----------------------------------------------------------
print("\n[30] LogQuery 构造")
check("构造 LogQuery 对象", "LogQuery(" in source)
check("LogQuery 传入 operator_id",
      "operator_id=operator_id" in source)
check("LogQuery 传入 operation",
      "operation=operation" in source)
check("LogQuery 传入 page",
      "page=page" in source)
check("LogQuery 传入 page_size",
      "page_size=page_size" in source)

# ----------------------------------------------------------
# [31] 历史路由未破坏
# ----------------------------------------------------------
print("\n[31] 历史路由未破坏")
check("__init__.py 导出 auth_router",
      "auth_router" in init_code)
check("__init__.py 导出 customer_router",
      "customer_router" in init_code)
check("__init__.py 导出 trial_task_router",
      "trial_task_router" in init_code)
check("__init__.py 导出 grinding_router",
      "grinding_router" in init_code)
check("__init__.py 导出 inspection_router",
      "inspection_router" in init_code)
check("__init__.py 导出 dispatch_router",
      "dispatch_router" in init_code)
check("__init__.py 导出 query_router",
      "query_router" in init_code)

# ----------------------------------------------------------
# [32] 代码行宽
# ----------------------------------------------------------
print("\n[32] 代码行宽")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()
long_lines = [
    i + 1 for i, line in enumerate(lines)
    if len(line.rstrip("\n")) > 79
]
if long_lines:
    print(f"    超长行: {long_lines}")
check("所有行 <= 79 字符", len(long_lines) == 0)

# ----------------------------------------------------------
# [33] 文件末尾换行
# ----------------------------------------------------------
print("\n[33] 文件末尾换行")
with open(SOURCE_PATH, "rb") as f:
    f.seek(-1, 2)
    last_char = f.read(1)
check("文件以换行符结尾", last_char == b"\n")

# ----------------------------------------------------------
# [34] 禁止导出库
# ----------------------------------------------------------
print("\n[34] 禁止导出库")
check("无 openpyxl", "openpyxl" not in source_full)
check("无 xlsxwriter", "xlsxwriter" not in source_full)
check("无 csv", "csv" not in source_full)

# ----------------------------------------------------------
# [35] Router 前缀
# ----------------------------------------------------------
print("\n[35] Router 前缀")
check("prefix='/api/log'", "/api/log" in source_full)

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