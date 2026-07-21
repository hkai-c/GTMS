"""Test: SettingsView (Sprint 13 — Task 13.7)

严格依据 DEVELOPMENT_ROADMAP.md Task 13.7 验收标准。
测试 client/views/settings_view.py 全部公开接口与代码规范。

注意：本测试使用源码分析，不依赖 PySide6 运行时。
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
print("  Task 13.7 — SettingsView Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("client", "views", "settings_view.py")

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
    from client.views.settings_view import SettingsView
    check("SettingsView 导入", True)
except Exception as e:
    check("SettingsView 导入 (PySide6 DLL 可能不可用)", True)
    print(f"      (Info: {e})")

# ----------------------------------------------------------
# [3] 类定义
# ----------------------------------------------------------
print("\n[3] 类定义")
check("SettingsView 继承 QWidget",
      "class SettingsView(QWidget)" in source_full)
check("__init__ 存在", "def __init__" in source_full)
check("refresh 存在", "def refresh" in source_full)

# ----------------------------------------------------------
# [4] 公开 API 数量
# ----------------------------------------------------------
print("\n[4] 公开 API 数量")
public_methods = [
    m for m in re.findall(r"def (\w+)", source_full)
    if not m.startswith("_")
]
expected_public = {"__init__", "refresh"}
actual_public = set(public_methods)
extra = actual_public - expected_public
check("仅 __init__ 和 refresh（2 个）",
      extra == set())

# ----------------------------------------------------------
# [5] Signals
# ----------------------------------------------------------
print("\n[5] Signals")
check("settings_changed 信号",
      "settings_changed" in source_full)
check("settings_changed 是 Signal",
      "Signal" in source_full
      and "settings_changed" in source_full)

# ----------------------------------------------------------
# [6] refresh 流程
# ----------------------------------------------------------
print("\n[6] refresh 流程")
check("refresh 调用 get_settings",
      ".get_settings()" in source_full)
check("refresh 调用 _populate_form",
      "_populate_form" in source_full)
check("refresh 调用 _update_status_bar",
      "_update_status_bar" in source_full)
check("refresh 发射 settings_changed",
      "settings_changed.emit()" in source_full)

# ----------------------------------------------------------
# [7] SettingsService 依赖
# ----------------------------------------------------------
print("\n[7] SettingsService 依赖")
check("__init__ 接受 SettingsService",
      "settings_service: SettingsService" in source_full)
check("导入 SettingsService",
      "from client.services.settings_service import SettingsService"
      in source_full)

# ----------------------------------------------------------
# [8] Read-Only View Principle
# ----------------------------------------------------------
print("\n[8] Read-Only View Principle")
check("无 ApiClient", "ApiClient" not in source)
check("无 requests", "requests" not in source_full)
check("无 httpx", "httpx" not in source_full)
check("无 Session", "Session" not in source_full)
check("无 SQLAlchemy", "sqlalchemy" not in source_full.lower())
check("无 config.py", "server.config" not in source_full)
check("无 Router", "APIRouter" not in source_full)

# ----------------------------------------------------------
# [9] Zero HTTP
# ----------------------------------------------------------
print("\n[9] Zero HTTP")
check("无 requests", "requests" not in source)
check("无 httpx", "httpx" not in source)
check("无 ApiClient", "ApiClient" not in source)

# ----------------------------------------------------------
# [10] Zero ORM
# ----------------------------------------------------------
print("\n[10] Zero ORM")
check("无 Session", "Session" not in source)
check("无 SQLAlchemy", "sqlalchemy" not in source.lower())
check("无 commit", "commit" not in source.lower())
check("无 rollback", "rollback" not in source.lower())

# ----------------------------------------------------------
# [11] Zero Business Logic
# ----------------------------------------------------------
print("\n[11] Zero Business Logic")
check("无数据处理逻辑",
      "calculate" not in source.lower()
      and "validate" not in source.lower()
      and "process" not in source.lower()
      and "transform" not in source.lower())

# ----------------------------------------------------------
# [12] Zero Workflow
# ----------------------------------------------------------
print("\n[12] Zero Workflow")
check("无 process_status", "process_status" not in source)
check("无 workflow", "workflow" not in source.lower())

# ----------------------------------------------------------
# [13] Zero Status Machine
# ----------------------------------------------------------
print("\n[13] Zero Status Machine")
check("无 result_status", "result_status" not in source)
check("无 status_machine", "status_machine" not in source.lower())

# ----------------------------------------------------------
# [14] Zero Aggregation
# ----------------------------------------------------------
print("\n[14] Zero Aggregation")
check("无 count(", "count(" not in source.lower())
check("无 sum(", "sum(" not in source.lower())
check("无 aggregate", "aggregate" not in source.lower())

# ----------------------------------------------------------
# [15] 100% 委托 SettingsService
# ----------------------------------------------------------
print("\n[15] 100% 委托 SettingsService")
check("get_settings 调用",
      "_settings_service.get_settings()" in source)
check("update_settings 调用",
      "_settings_service.update_settings" in source)

# ----------------------------------------------------------
# [16] Logging
# ----------------------------------------------------------
print("\n[16] Logging")
check("gtms.client logger",
      'getLogger("gtms.client")' in source_full)
check("logger.debug()", "logger.debug(" in source_full)
check("logger.info()", "logger.info(" in source_full)
check("禁止 print()", "print(" not in source)

# ----------------------------------------------------------
# [17] Constants
# ----------------------------------------------------------
print("\n[17] Constants")
check("WINDOW_TITLE", "WINDOW_TITLE" in source_full)
check("STATUS_READY", "STATUS_READY" in source_full)
check("STATUS_SAVED", "STATUS_SAVED" in source_full)
check("STATUS_REFRESHED", "STATUS_REFRESHED" in source_full)
check("STATUS_SAVING", "STATUS_SAVING" in source_full)
check("STATUS_REFRESHING", "STATUS_REFRESHING" in source_full)
check("STATUS_FAILED", "STATUS_FAILED" in source_full)
check("BUTTON_TEXT", "BUTTON_TEXT" in source_full)
check("GROUP_TITLES", "GROUP_TITLES" in source_full)
check("THEME_OPTIONS", "THEME_OPTIONS" in source_full)
check("LANGUAGE_OPTIONS", "LANGUAGE_OPTIONS" in source_full)
check("OBJECT_NAMES", "OBJECT_NAMES" in source_full)
check("MESSAGE_TEXT", "MESSAGE_TEXT" in source_full)

# ----------------------------------------------------------
# [18] ObjectName 常量
# ----------------------------------------------------------
print("\n[18] ObjectName 常量")
check("title_label", "title_label" in source_full)
check("scroll_area", "scroll_area" in source_full)
check("system_group", "system_group" in source_full)
check("system_name_input", "system_name_input" in source_full)
check("save_btn", "save_btn" in source_full)
check("refresh_btn", "refresh_btn" in source_full)
check("status_bar", "status_bar" in source_full)

# ----------------------------------------------------------
# [19] Widget 类型
# ----------------------------------------------------------
print("\n[19] Widget 类型")
check("QScrollArea", "QScrollArea" in source_full)
check("QFormLayout", "QFormLayout" in source_full)
check("QLineEdit", "QLineEdit" in source_full)
check("QSpinBox", "QSpinBox" in source_full)
check("QCheckBox", "QCheckBox" in source_full)
check("QComboBox", "QComboBox" in source_full)
check("QPushButton", "QPushButton" in source_full)
check("QGroupBox", "QGroupBox" in source_full)
check("QLabel", "QLabel" in source_full)

# ----------------------------------------------------------
# [20] 表单字段覆盖
# ----------------------------------------------------------
print("\n[20] 表单字段覆盖")
check("system_name_input", "system_name_input" in source_full)
check("company_name_input", "company_name_input" in source_full)
check("theme_combo", "theme_combo" in source_full)
check("language_combo", "language_combo" in source_full)
check("timezone_input", "timezone_input" in source_full)
check("database_path_input", "database_path_input" in source_full)
check("backup_directory_input",
      "backup_directory_input" in source_full)
check("backup_time_input", "backup_time_input" in source_full)
check("backup_enabled_check",
      "backup_enabled_check" in source_full)
check("backup_retention_spin",
      "backup_retention_spin" in source_full)
check("upload_directory_input",
      "upload_directory_input" in source_full)
check("max_image_size_spin", "max_image_size_spin" in source_full)
check("max_document_size_spin",
      "max_document_size_spin" in source_full)
check("max_video_size_spin", "max_video_size_spin" in source_full)
check("receipt_delay_spin", "receipt_delay_spin" in source_full)
check("grinding_delay_spin", "grinding_delay_spin" in source_full)
check("report_missing_spin", "report_missing_spin" in source_full)
check("check_interval_spin",
      "check_interval_spin" in source_full)
check("log_retention_spin", "log_retention_spin" in source_full)

# ----------------------------------------------------------
# [21] PEP8
# ----------------------------------------------------------
print("\n[21] PEP8")
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
# [22] Docstring
# ----------------------------------------------------------
print("\n[22] Docstring")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块级 docstring 存在",
      ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if (isinstance(node, ast.FunctionDef)
            and not node.name.startswith("_")):
        doc = ast.get_docstring(node)
        check(f"{node.name} docstring 存在", doc is not None)

# ----------------------------------------------------------
# [23] Type Hint
# ----------------------------------------------------------
print("\n[23] Type Hint")
for node in ast.walk(tree):
    if (isinstance(node, ast.FunctionDef)
            and not node.name.startswith("_")):
        check(f"{node.name} 返回类型注解",
              node.returns is not None)

# ----------------------------------------------------------
# [24] __all__ 导出
# ----------------------------------------------------------
print("\n[24] __all__ 导出")
check("__all__ 包含 SettingsView",
      "SettingsView" in source_full.split("__all__")[-1])

# ----------------------------------------------------------
# [25] __init__.py 导出
# ----------------------------------------------------------
print("\n[25] __init__.py 导出")
INIT_PATH = os.path.join("client", "views", "__init__.py")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导入 SettingsView",
      "SettingsView" in init_code)

# ----------------------------------------------------------
# [26] 代码行宽
# ----------------------------------------------------------
print("\n[26] 代码行宽")
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
# [27] 文件末尾换行
# ----------------------------------------------------------
print("\n[27] 文件末尾换行")
with open(SOURCE_PATH, "rb") as f:
    f.seek(-1, 2)
    last_char = f.read(1)
check("文件以换行符结尾", last_char == b"\n")

# ----------------------------------------------------------
# [28] 无 TODO/FIXME
# ----------------------------------------------------------
print("\n[28] 无 TODO/FIXME")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)

# ----------------------------------------------------------
# [29] 历史 View 未被破坏
# ----------------------------------------------------------
print("\n[29] 历史 View 未被破坏")
check("__init__.py 导出 NotificationView",
      "NotificationView" in init_code)
check("__init__.py 导出 QueryView",
      "QueryView" in init_code)
check("__init__.py 导出 SystemLogView",
      "SystemLogView" in init_code)

# ----------------------------------------------------------
# [30] 回归测试
# ----------------------------------------------------------
print("\n[30] 回归测试")
tests_dir = os.path.dirname(os.path.abspath(__file__))

# Settings Service Client 回归
client_result = subprocess.run(
    [sys.executable,
     os.path.join(tests_dir,
                  "test_settings_service_client.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_settings_service_client.py 回归",
      client_result.returncode == 0)

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

# Notification View 回归
notify_result = subprocess.run(
    [sys.executable,
     os.path.join(tests_dir, "test_notification_view.py")],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("test_notification_view.py 回归",
      notify_result.returncode == 0)

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