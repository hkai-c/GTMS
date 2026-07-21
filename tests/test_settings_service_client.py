"""Test: Desktop SettingsService (Sprint 13 — Task 13.6)

严格依据 DEVELOPMENT_ROADMAP.md Task 13.6 验收标准。
测试 client/services/settings_service.py 全部公开 API 与代码规范。

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
print("  Task 13.6 — Desktop SettingsService Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join(
    "client", "services", "settings_service.py"
)

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
    from client.services.settings_service import (
        SettingsService,
    )
    check("SettingsService 导入", True)
except ImportError as e:
    check("SettingsService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
import inspect
check("SettingsService 是 class",
      inspect.isclass(SettingsService))
check("SettingsService 有 __init__",
      hasattr(SettingsService, "__init__"))

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(SettingsService)
    if not m.startswith("_") and callable(
        getattr(SettingsService, m, None)
    )
]
check("get_settings", "get_settings" in public_methods)
check("update_settings", "update_settings" in public_methods)
check("公开 API 数量 = 2", len(public_methods) == 2)

# ----------------------------------------------------------
# [5] 禁止 create/delete/list/search
# ----------------------------------------------------------
print("\n[5] 禁止 create/delete/list/search")
check("无 create_settings", "create_settings" not in public_methods)
check("无 delete_settings", "delete_settings" not in public_methods)
check("无 list_settings", "list_settings" not in public_methods)
check("无 search_settings", "search_settings" not in public_methods)
check("无 batch_update", "batch_update" not in public_methods)

# ----------------------------------------------------------
# [6] HTTP 映射
# ----------------------------------------------------------
print("\n[6] HTTP 映射")

# GET
check("get_settings → GET /api/settings",
      "self._api_client.get(SETTINGS_PATH)" in source
      or "self._api_client.get(\"/api/settings\")" in source)

# PUT
check("update_settings → PUT /api/settings",
      "self._api_client.put(SETTINGS_PATH" in source
      or "self._api_client.put(\"/api/settings\"" in source)

# 仅调用 2 次 ApiClient
api_client_calls = (
    source.count("self._api_client.get")
    + source.count("self._api_client.put")
    + source.count("self._api_client.post")
    + source.count("self._api_client.delete")
)
check("仅 2 次 ApiClient 调用", api_client_calls == 2)

# ----------------------------------------------------------
# [7] GET 实现
# ----------------------------------------------------------
print("\n[7] GET 实现")
check("get_settings 无 query 参数", "params=" not in source)
check("get_settings 返回 resp.json()",
      "resp.json()" in source_full)

# ----------------------------------------------------------
# [8] PUT 实现
# ----------------------------------------------------------
print("\n[8] PUT 实现")
check("update_settings 使用 json=body",
      "json=body" in source)
check("update_settings 返回 resp.json()",
      "resp.json()" in source_full)
check("update_settings 过滤 None 字段",
      "v is not None" in source)
check("update_settings 使用 **kwargs",
      "**kwargs" in source_full)

# ----------------------------------------------------------
# [9] Query Rules
# ----------------------------------------------------------
print("\n[9] Query Rules")
check("GET 仅发送非 None 参数", "params=" not in source)

# ----------------------------------------------------------
# [10] Body Rules
# ----------------------------------------------------------
print("\n[10] Body Rules")
check("PUT 仅发送非 None 字段",
      "v is not None" in source)

# ----------------------------------------------------------
# [11] Return Rules
# ----------------------------------------------------------
print("\n[11] Return Rules")
check("统一 return resp.json()",
      source_full.count("return ") == 2)
check("无转换对象",
      "SettingsResponse" not in source_full)
check("无包装返回值",
      "return {" not in source)

# ----------------------------------------------------------
# [12] 依赖
# ----------------------------------------------------------
print("\n[12] 依赖")
check("导入 ApiClient", "ApiClient" in source_full)
check("导入 logging", "logging" in source_full)
check("__init__ 接受 ApiClient",
      "api_client: ApiClient" in source_full)

# ----------------------------------------------------------
# [13] 禁止依赖
# ----------------------------------------------------------
print("\n[13] 禁止依赖")
check("无 Router", "APIRouter" not in source_full)
check("无 ORM", "Session" not in source_full)
check("无 Scheduler", "BackgroundScheduler" not in source_full)
check("无 Notification", "NotificationService" not in source_full)
check("无 Backup", "BackupManager" not in source_full)
check("无 View", "PySide6" not in source_full)
check("无 QtWidgets", "QtWidgets" not in source_full)

# ----------------------------------------------------------
# [14] Logging
# ----------------------------------------------------------
print("\n[14] Logging")
check("gtms.client logger",
      'getLogger("gtms.client")' in source_full)
check("logger.debug()", "logger.debug(" in source_full)
check("禁止 print()", "print(" not in source)

# ----------------------------------------------------------
# [15] Exception
# ----------------------------------------------------------
print("\n[15] Exception")
check("无 try/except", "try:" not in source)

# ----------------------------------------------------------
# [16] Zero Workflow
# ----------------------------------------------------------
print("\n[16] Zero Workflow")
check("无 process_status", "process_status" not in source)
check("无 workflow", "workflow" not in source.lower())

# ----------------------------------------------------------
# [17] Zero Status Machine
# ----------------------------------------------------------
print("\n[17] Zero Status Machine")
check("无 result_status", "result_status" not in source)
check("无 status_machine", "status_machine" not in source.lower())

# ----------------------------------------------------------
# [18] Zero Aggregation
# ----------------------------------------------------------
print("\n[18] Zero Aggregation")
check("无 count(", "count(" not in source.lower())
check("无 sum(", "sum(" not in source.lower())
check("无 aggregate", "aggregate" not in source.lower())

# ----------------------------------------------------------
# [19] Constants
# ----------------------------------------------------------
print("\n[19] Constants")
check("SETTINGS_PATH 常量", "SETTINGS_PATH" in source_full)
check("无 Magic String /api/settings",
      "\"/api/settings\"" in source_full
      or "SETTINGS_PATH" in source_full)

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
check("类 docstring 存在",
      SettingsService.__doc__ is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        doc = ast.get_docstring(node)
        check(f"{node.name} docstring 存在",
              doc is not None)

# ----------------------------------------------------------
# [22] Type Hint
# ----------------------------------------------------------
print("\n[22] Type Hint")
for node in ast.walk(tree):
    if (isinstance(node, ast.FunctionDef)
            and not node.name.startswith("_")):
        check(f"{node.name} 返回类型注解",
              node.returns is not None)
check("__init__ 有 api_client 类型注解",
      "api_client: ApiClient" in source_full)

# ----------------------------------------------------------
# [23] __all__ 导出
# ----------------------------------------------------------
print("\n[23] __all__ 导出")
check("__all__ 包含 SettingsService",
      "SettingsService" in source_full.split("__all__")[-1])

# ----------------------------------------------------------
# [24] __init__.py 导出
# ----------------------------------------------------------
print("\n[24] __init__.py 导出")
INIT_PATH = os.path.join("client", "services", "__init__.py")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导入 SettingsService",
      "SettingsService" in init_code)

# 验证可导入
from client.services import SettingsService as SS2
check("从 services 包导入", SS2 is SettingsService)

# ----------------------------------------------------------
# [25] 代码行宽
# ----------------------------------------------------------
print("\n[25] 代码行宽")
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
# [26] 文件末尾换行
# ----------------------------------------------------------
print("\n[26] 文件末尾换行")
with open(SOURCE_PATH, "rb") as f:
    f.seek(-1, 2)
    last_char = f.read(1)
check("文件以换行符结尾", last_char == b"\n")

# ----------------------------------------------------------
# [27] 无 TODO/FIXME
# ----------------------------------------------------------
print("\n[27] 无 TODO/FIXME")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)

# ----------------------------------------------------------
# [28] 回归测试
# ----------------------------------------------------------
print("\n[28] 回归测试")
tests_dir = os.path.dirname(os.path.abspath(__file__))

# Settings Router 回归
router_result = subprocess.run(
    [sys.executable,
     os.path.join(tests_dir, "test_settings_router.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_settings_router.py 回归",
      router_result.returncode == 0)

# Settings Service 回归
service_result = subprocess.run(
    [sys.executable,
     os.path.join(tests_dir, "test_settings_service.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_settings_service.py 回归",
      service_result.returncode == 0)

# Settings Schema 回归
schema_result = subprocess.run(
    [sys.executable,
     os.path.join(tests_dir, "test_settings_schema.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_settings_schema.py 回归",
      schema_result.returncode == 0)

# Notification Service Client 回归
notify_result = subprocess.run(
    [sys.executable,
     os.path.join(tests_dir,
                  "test_notification_service_client.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_notification_service_client.py 回归",
      notify_result.returncode == 0)

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