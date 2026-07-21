"""Test: Settings Router (Sprint 13 — Task 13.5)

严格依据 DEVELOPMENT_ROADMAP.md Task 13.5 验收标准。
测试 server/routers/settings_router.py 全部公开接口与代码规范。

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
print("  Task 13.5 — Settings Router Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "routers", "settings_router.py")

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
    from server.routers.settings_router import router
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
check("2 个路由", len(routes) == 2)

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
check("PUT 路由", ["PUT"] in methods_list)
get_count = sum(1 for m in methods_list if m == ["GET"])
check("1 个 GET 路由", get_count == 1)
put_count = sum(1 for m in methods_list if m == ["PUT"])
check("1 个 PUT 路由", put_count == 1)

# 禁止的 HTTP 方法
check("无 POST 路由", sum(1 for m in methods_list if m == ["POST"]) == 0)
check("无 DELETE 路由",
      sum(1 for m in methods_list if m == ["DELETE"]) == 0)
check("无 PATCH 路由",
      sum(1 for m in methods_list if m == ["PATCH"]) == 0)

# ----------------------------------------------------------
# [6] 路由路径
# ----------------------------------------------------------
print("\n[6] 路由路径")
paths = [r.path for r in routes if hasattr(r, "path")]
check("GET /api/settings 路径",
      "/api/settings" in paths)
check("PUT /api/settings 路径",
      "/api/settings" in paths)

# 禁止的路径
check("无 /api/settings/{id} 路径",
      "/api/settings/{id}" not in paths)
check("无 /api/settings/{settings_id} 路径",
      "/api/settings/{settings_id}" not in paths)

# ----------------------------------------------------------
# [7] Endpoint 函数
# ----------------------------------------------------------
print("\n[7] Endpoint 函数")
check("get_settings 存在", "def get_settings" in source_full)
check("update_settings 存在", "def update_settings" in source_full)

# 禁止多余的 endpoint
check("仅 2 个 endpoint 函数",
      source_full.count("def ") == 2)

# ----------------------------------------------------------
# [8] HTTP 映射
# ----------------------------------------------------------
print("\n[8] HTTP 映射")
check("get_settings → SettingsService.get_settings",
      "_settings_service.get_settings" in source)
check("update_settings → SettingsService.update_settings",
      "_settings_service.update_settings" in source)

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
check("settings:view 权限", "settings:view" in source_full)
check("settings:edit 权限", "settings:edit" in source_full)

# ----------------------------------------------------------
# [11] response_model
# ----------------------------------------------------------
print("\n[11] response_model")
check("get_settings response_model=SettingsResponse",
      "response_model=SettingsResponse" in source_full)
check("update_settings response_model=SettingsResponse",
      "response_model=SettingsResponse" in source_full)

# ----------------------------------------------------------
# [12] status_code
# ----------------------------------------------------------
print("\n[12] status_code")
check("get_settings 200_OK",
      "status.HTTP_200_OK" in source_full)
check("update_settings 200_OK",
      "status.HTTP_200_OK" in source_full)

# ----------------------------------------------------------
# [13] OpenAPI metadata
# ----------------------------------------------------------
print("\n[13] OpenAPI metadata")
check("summary 存在", "summary" in source_full)
check("description 存在", "description" in source_full)
check("tags=['Settings']", "Settings" in source_full)

# ----------------------------------------------------------
# [14] 零业务逻辑
# ----------------------------------------------------------
print("\n[14] 零业务逻辑")
check("零 ORM 操作（无 Session()）", "Session(" not in source)
check("零 Workflow（无 process_status 赋值）",
      "process_status = " not in source)
check("零 Status Machine（无 result_status 赋值）",
      "result_status = " not in source)
check("零 SystemLog", "SystemLog" not in source)
check("零事务（无 db.commit）", "db.commit" not in source)
check("零事务（无 db.rollback）", "db.rollback" not in source)
check("零 Aggregation", "func." not in source)
check("零 Audit Log", "_write_log" not in source)
check("零 LogService", "LogService" not in source)

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
# [17] 无 print / 无 logger
# ----------------------------------------------------------
print("\n[17] 无 print / 无 logger")
check("无 print()", "print(" not in source)
check("无 logger", "logger" not in source)

# ----------------------------------------------------------
# [18] 依赖
# ----------------------------------------------------------
print("\n[18] 依赖")
check("导入 SettingsService", "SettingsService" in source_full)
check("导入 SettingsResponse", "SettingsResponse" in source_full)
check("导入 SettingsUpdate", "SettingsUpdate" in source_full)
check("导入 get_db", "get_db" in source_full)
check("导入 get_current_active_user",
      "get_current_active_user" in source_full)
check("导入 require_permission", "require_permission" in source_full)
check("导入 User", "from server.models.user import User" in source_full)

# ----------------------------------------------------------
# [19] 禁止依赖
# ----------------------------------------------------------
print("\n[19] 禁止依赖")
check("无 requests", "requests" not in source_full)
check("无 httpx", "httpx" not in source_full)
check("无 SQLAlchemy ORM 直接操作", "Session(" not in source)
check("无 Desktop 导入", "from client." not in source_full)
check("无 View 导入", "from client.views" not in source_full)
check("无 NotificationService", "NotificationService" not in source_full)
check("无 BackupManager", "BackupManager" not in source_full)
check("无 Scheduler", "BackgroundScheduler" not in source_full)

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
check("__init__.py 导出 settings_router",
      "settings_router" in init_code)

# ----------------------------------------------------------
# [25] main.py 注册
# ----------------------------------------------------------
print("\n[25] main.py 注册")
MAIN_PATH = os.path.join("server", "main.py")
main_code = extract_code_text(MAIN_PATH)
check("main.py 导入 settings_router",
      "settings_router" in main_code)
check("main.py 注册 settings_router",
      "settings_router" in main_code)

# ----------------------------------------------------------
# [26] 无循环导入
# ----------------------------------------------------------
print("\n[26] 无循环导入")
check("无自身导入",
      "from server.routers.settings_router" not in source_full)
check("无 Service 交叉导入",
      "TaskService" not in source_full)

# ----------------------------------------------------------
# [27] Frozen API
# ----------------------------------------------------------
print("\n[27] Frozen API")
check("User 仅用于类型注解，无 User()", "User(" not in source)
check("未导入 Desktop 层",
      "from client." not in source_full)

# ----------------------------------------------------------
# [28] body 参数
# ----------------------------------------------------------
print("\n[28] body 参数")
check("update_settings body",
      "data: SettingsUpdate = Body" in source_full)

# ----------------------------------------------------------
# [29] 当前用户注入
# ----------------------------------------------------------
print("\n[29] 当前用户注入")
check("update_settings 使用 current_user.id",
      "current_user.id" in source_full)

# ----------------------------------------------------------
# [30] 历史路由未破坏
# ----------------------------------------------------------
print("\n[30] 历史路由未破坏")
check("__init__.py 导出 auth_router",
      "auth_router" in init_code)
check("__init__.py 导出 notification_router",
      "notification_router" in init_code)
check("__init__.py 导出 log_router",
      "log_router" in init_code)
check("__init__.py 导出 query_router",
      "query_router" in init_code)

# ----------------------------------------------------------
# [31] 代码行宽
# ----------------------------------------------------------
print("\n[31] 代码行宽")
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
# [32] 文件末尾换行
# ----------------------------------------------------------
print("\n[32] 文件末尾换行")
with open(SOURCE_PATH, "rb") as f:
    f.seek(-1, 2)
    last_char = f.read(1)
check("文件以换行符结尾", last_char == b"\n")

# ----------------------------------------------------------
# [33] Router 前缀
# ----------------------------------------------------------
print("\n[33] Router 前缀")
check("prefix='/api/settings'",
      "/api/settings" in source_full)

# ----------------------------------------------------------
# [34] 禁止 create/delete/list/search/batch endpoint
# ----------------------------------------------------------
print("\n[34] 禁止多余 endpoint")
check("无 create_settings endpoint",
      "def create_settings" not in source_full)
check("无 delete_settings endpoint",
      "def delete_settings" not in source_full)
check("无 list_settings endpoint",
      "def list_settings" not in source_full)
check("无 search_settings endpoint",
      "def search_settings" not in source_full)
check("无 batch_update endpoint",
      "def batch_update" not in source_full)
check("无 reset_settings endpoint",
      "def reset_settings" not in source_full)

# ----------------------------------------------------------
# [35] 100% 委托 SettingsService
# ----------------------------------------------------------
print("\n[35] 100% 委托 SettingsService")
check("get_settings 委托",
      "_settings_service.get_settings()" in source)
check("update_settings 委托",
      "_settings_service.update_settings" in source)
check("无其他方法调用",
      source.count("_settings_service.") == 2)

# ----------------------------------------------------------
# [36] 回归测试
# ----------------------------------------------------------
print("\n[36] 回归测试")
tests_dir = os.path.dirname(os.path.abspath(__file__))

# Settings Service 回归
service_result = subprocess.run(
    [sys.executable, os.path.join(tests_dir, "test_settings_service.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_settings_service.py 回归",
      service_result.returncode == 0)

# Settings Schema 回归
schema_result = subprocess.run(
    [sys.executable, os.path.join(tests_dir, "test_settings_schema.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_settings_schema.py 回归",
      schema_result.returncode == 0)

# Notification Router 回归
notify_result = subprocess.run(
    [sys.executable,
     os.path.join(tests_dir, "test_notification_router.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_notification_router.py 回归",
      notify_result.returncode == 0)

# Scheduler 回归
scheduler_result = subprocess.run(
    [sys.executable, os.path.join(tests_dir, "test_scheduler.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_scheduler.py 回归",
      scheduler_result.returncode == 0)

# Backup Scheduler 回归
backup_result = subprocess.run(
    [sys.executable,
     os.path.join(tests_dir, "test_backup_scheduler.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_backup_scheduler.py 回归",
      backup_result.returncode == 0)

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