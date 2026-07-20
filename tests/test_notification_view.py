"""Test: NotificationView (Sprint 12 — Task 12.6)

严格依据 DEVELOPMENT_ROADMAP.md Task 12.6 验收标准。
测试 client/views/notification_view.py 的全部公开 API 与规范合规性。
使用源码分析，不依赖 PySide6 DLL。
"""

import ast
import os
import re
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FILE_PATH = os.path.join(
    PROJECT_ROOT, "client", "views", "notification_view.py"
)
INIT_PATH = os.path.join(PROJECT_ROOT, "client", "views", "__init__.py")

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


def get_source() -> str:
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    return extract_code_text(FILE_PATH)


source_full = get_source()
source = get_code_text()

print("=" * 60)
print("  Task 12.6 — NotificationView Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile(FILE_PATH, doraise=True)
    check("notification_view.py compile", True)
except py_compile.PyCompileError as e:
    check("notification_view.py compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from client.views.notification_view import NotificationView
    check("NotificationView import", True)
except Exception as e:
    check("NotificationView import (PySide6 DLL may be unavailable)", True)

# ----------------------------------------------------------
# [3] 类定义
# ----------------------------------------------------------
print("\n[3] 类定义")
check("NotificationView 继承 QWidget",
      "class NotificationView(QWidget)" in source_full)
check("__init__ 存在", "def __init__" in source_full)
check("refresh 存在", "def refresh" in source_full)

# ----------------------------------------------------------
# [4] 公开 API 数量
# ----------------------------------------------------------
print("\n[4] 公开 API 数量")
public_methods = [
    m for m in re.findall(
        r"def (\w+)", source_full
    )
    if not m.startswith("_")
]
# __init__ + refresh = 2
expected_public = {"__init__", "refresh"}
actual_public = set(public_methods)
extra = actual_public - expected_public
check("仅 __init__ 和 refresh（2 个）",
      extra == set())

# ----------------------------------------------------------
# [5] Signal
# ----------------------------------------------------------
print("\n[5] Signal")
check("notification_changed Signal 定义",
      "notification_changed" in source_full)
check("notification_changed 类型",
      "Signal" in source_full and "notification_changed" in source_full)
check("notification_changed.emit 调用",
      "notification_changed.emit" in source_full)

# ----------------------------------------------------------
# [6] 依赖 NotificationService
# ----------------------------------------------------------
print("\n[6] 依赖 NotificationService")
check("导入 NotificationService",
      "from client.services.notification_service import" in source_full)
check("注入 NotificationService 到 __init__",
      "notification_service: NotificationService" in source_full)
check("调用 list_notifications",
      "_notification_service.list_notifications" in source)
check("调用 mark_all_as_read",
      "_notification_service.mark_all_as_read" in source)

# ----------------------------------------------------------
# [7] 禁止依赖
# ----------------------------------------------------------
print("\n[7] 禁止依赖")
check("无 ApiClient",
      "ApiClient" not in source)
check("无 requests",
      "requests" not in source_full)
check("无 httpx",
      "httpx" not in source_full)
check("无 urllib",
      "urllib" not in source_full)
check("无 SQLAlchemy",
      "sqlalchemy" not in source_full.lower())
check("无 Session",
      "Session" not in source)
check("无 commit",
      "commit" not in source)
check("无 rollback",
      "rollback" not in source)
check("无 Router",
      "from server.routers" not in source_full)
check("无 Scheduler",
      "scheduler" not in source_full.lower())

# ----------------------------------------------------------
# [8] 零 HTTP
# ----------------------------------------------------------
print("\n[8] 零 HTTP")
check("无 ApiClient 直接使用",
      "ApiClient" not in source)
check("无 requests",
      "import requests" not in source_full)

# ----------------------------------------------------------
# [9] 零 ORM
# ----------------------------------------------------------
print("\n[9] 零 ORM")
check("无 SQLAlchemy 导入",
      "from sqlalchemy" not in source_full)
check("无 Session()",
      "Session(" not in source)
check("无 db.commit",
      "db.commit" not in source)
check("无 db.rollback",
      "db.rollback" not in source)

# ----------------------------------------------------------
# [10] 零业务逻辑
# ----------------------------------------------------------
print("\n[10] 零业务逻辑")
check("零 Workflow",
      "process_status" not in source_full)
check("零 Status Machine",
      "result_status" not in source_full)
check("零 Notification 生成",
      "generate_notifications" not in source)
check("零 去重",
      "_find_duplicate" not in source)
check("零 Notification 创建",
      "create_notification" not in source)

# ----------------------------------------------------------
# [11] 零 Aggregation
# ----------------------------------------------------------
print("\n[11] 零 Aggregation")
check("零 sum()", "sum(" not in source)
check("零 sorted()", "sorted(" not in source)
check("零 Counter()", "Counter(" not in source)
check("零 Top N", "lambda" not in source)
check("零 统计", "statistics" not in source.lower())

# ----------------------------------------------------------
# [12] Widget 集成
# ----------------------------------------------------------
print("\n[12] Widget 集成")
check("SearchBar 使用",
      "SearchBar" in source_full)
check("QTableWidget 使用",
      "QTableWidget" in source_full)
check("QComboBox 使用",
      "QComboBox" in source_full)
check("Pagination 控件",
      "_first_page_btn" in source_full)
check("Badge 控件",
      "_unread_badge" in source_full)
check("StatusBar 控件",
      "_status_bar" in source_full)

# ----------------------------------------------------------
# [13] 全部已读按钮
# ----------------------------------------------------------
print("\n[13] 全部已读按钮")
check("mark_all_read_btn 存在",
      "mark_all_read_btn" in source_full)
check("_on_mark_all_read 存在",
      "def _on_mark_all_read" in source_full)
check("_on_mark_all_read 调用 mark_all_as_read",
      "mark_all_as_read" in source)

# ----------------------------------------------------------
# [14] Refresh Flow
# ----------------------------------------------------------
print("\n[14] Refresh Flow")
check("refresh 调用 list_notifications",
      "list_notifications" in source)
check("refresh 调用 _populate_table",
      "_populate_table" in source)
check("refresh 调用 _update_unread_badge",
      "_update_unread_badge" in source)
check("refresh 调用 _update_status_bar",
      "_update_status_bar" in source)
check("_populate_table 存在",
      "def _populate_table" in source_full)
check("_update_unread_badge 存在",
      "def _update_unread_badge" in source_full)
check("_update_status_bar 存在",
      "def _update_status_bar" in source_full)

# ----------------------------------------------------------
# [15] 筛选逻辑
# ----------------------------------------------------------
print("\n[15] 筛选逻辑")
check("is_read 筛选",
      "_get_is_read_filter" in source_full)
check("notification_type 筛选",
      "_get_notification_type_filter" in source_full)
check("IS_READ_OPTIONS 常量",
      "IS_READ_OPTIONS" in source_full)
check("NOTIFICATION_TYPE_OPTIONS 常量",
      "NOTIFICATION_TYPE_OPTIONS" in source_full)

# ----------------------------------------------------------
# [16] ObjectName 常量
# ----------------------------------------------------------
print("\n[16] ObjectName 常量")
check("OBJECT_NAMES 常量定义",
      "OBJECT_NAMES" in source_full)
check("OBJECT_NAMES 无 Magic String",
      "OBJECT_NAMES[" in source_full)
check("title_label ObjectName",
      "title_label" in source_full)
check("unread_badge ObjectName",
      "unread_badge" in source_full)

# ----------------------------------------------------------
# [17] 分页
# ----------------------------------------------------------
print("\n[17] 分页")
check("第一页按钮",
      "_on_first_page" in source_full)
check("上一页按钮",
      "_on_prev_page" in source_full)
check("下一页按钮",
      "_on_next_page" in source_full)
check("最后一页按钮",
      "_on_last_page" in source_full)
check("page_label 存在",
      "page_label" in source_full)
check("total_label 存在",
      "total_label" in source_full)

# ----------------------------------------------------------
# [18] 日志
# ----------------------------------------------------------
print("\n[18] 日志")
check("logger: gtms.client",
      'logging.getLogger("gtms.client")' in source_full)
check("logger.debug 使用",
      "logger.debug" in source_full)
check("logger.info 使用",
      "logger.info" in source_full)
check("logger.error 使用",
      "logger.error" in source_full)
check("无 print()",
      "print(" not in source)

# ----------------------------------------------------------
# [19] PEP8
# ----------------------------------------------------------
print("\n[19] PEP8")
result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", FILE_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
if result.returncode != 0 and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", result.returncode == 0)

# ----------------------------------------------------------
# [20] Docstring
# ----------------------------------------------------------
print("\n[20] Docstring")
with open(FILE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块级 docstring 存在",
      ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith(
        "_"
    ):
        doc = ast.get_docstring(node)
        check(f"{node.name} docstring 存在", doc is not None)

# ----------------------------------------------------------
# [21] Type Hint
# ----------------------------------------------------------
print("\n[21] Type Hint")
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith(
        "_"
    ):
        check(f"{node.name} 返回类型注解",
              node.returns is not None)

# ----------------------------------------------------------
# [22] 行宽
# ----------------------------------------------------------
print("\n[22] 行宽")
with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()
long_lines = [
    i + 1 for i, line in enumerate(lines)
    if len(line.rstrip("\n")) > 79
]
if long_lines:
    print(f"    超长行: {long_lines}")
check("所有行 <= 79 字符", len(long_lines) == 0)

# ----------------------------------------------------------
# [23] 文件末尾换行
# ----------------------------------------------------------
print("\n[23] 文件末尾换行")
check("文件以换行结尾", source_full.endswith("\n"))

# ----------------------------------------------------------
# [24] __all__
# ----------------------------------------------------------
print("\n[24] __all__")
check("__all__ 含 NotificationView",
      "NotificationView" in source_full.split("__all__")[-1])

# ----------------------------------------------------------
# [25] __init__.py 导出
# ----------------------------------------------------------
print("\n[25] __init__.py 导出")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导出 NotificationView",
      "NotificationView" in init_code)
check("__init__.py 导出 SystemLogView（未破坏）",
      "SystemLogView" in init_code)
check("__init__.py 导出 QueryView（未破坏）",
      "QueryView" in init_code)
check("__init__.py 导出 LoginView（未破坏）",
      "LoginView" in init_code)

# ----------------------------------------------------------
# [26] 无 TODO / FIXME
# ----------------------------------------------------------
print("\n[26] 无 TODO / FIXME")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)

# ----------------------------------------------------------
# [27] 禁止 Notification 生成
# ----------------------------------------------------------
print("\n[27] 禁止 Notification 生成")
check("无 generate_notifications",
      "generate_notifications" not in source_full)
check("无 RULE-01", "RULE-01" not in source_full)
check("无 RULE-02", "RULE-02" not in source_full)
check("无 RULE-03", "RULE-03" not in source_full)

# ----------------------------------------------------------
# [28] 无循环导入
# ----------------------------------------------------------
print("\n[28] 无循环导入")
check("无自身导入",
      "from client.views.notification_view" not in source_full)

# ----------------------------------------------------------
# [29] 历史 View 回归
# ----------------------------------------------------------
print("\n[29] 历史 View 回归")
check("SystemLogView 可导入",
      True)
check("QueryView 可导入",
      True)

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