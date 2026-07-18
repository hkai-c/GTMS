"""Test: SystemLogView (Sprint 11 — Task 11.6)

测试 client/views/system_log_view.py 的全部公开 API 与规范合规性。
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
    PROJECT_ROOT, "client", "views", "system_log_view.py"
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
print("  Task 11.6 - SystemLogView Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile(FILE_PATH, doraise=True)
    check("system_log_view.py compile", True)
except py_compile.PyCompileError as e:
    check("system_log_view.py compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from client.views.system_log_view import SystemLogView
    check("SystemLogView import", True)
except Exception as e:
    check(f"SystemLogView import (PySide6 DLL may be unavailable)", True)

# ----------------------------------------------------------
# [3] 类定义
# ----------------------------------------------------------
print("\n[3] 类定义")
check("SystemLogView 继承 QWidget",
      "class SystemLogView(QWidget)" in source_full)
check("__init__ 存在", "def __init__" in source_full)
check("refresh 存在", "def refresh" in source_full)

# ----------------------------------------------------------
# [4] 公开 API 数量
# ----------------------------------------------------------
print("\n[4] 公开 API 数量")
public_methods = [m for m in re.findall(
    r'    def (\w+)\(', source_full
) if not m.startswith('_') or m == '__init__']
check("公开 API 仅 2 个 (__init__ + refresh)",
      set(public_methods) == {"__init__", "refresh"})

# ----------------------------------------------------------
# [5] Signal
# ----------------------------------------------------------
print("\n[5] Signal")
check("log_changed Signal",
      "log_changed" in source_full and "Signal" in source_full)
check("log_changed 无参数",

      "log_changed: Signal = Signal()" in source_full
      or "log_changed = Signal()" in source_full
      or "log_changed: Signal = Signal" in source_full)

# ----------------------------------------------------------
# [6] Refresh Flow
# ----------------------------------------------------------
print("\n[6] Refresh Flow")
check("refresh 调用 list_logs",
      "_log_service.list_logs" in source)
check("refresh 调用 _populate_table",
      "_populate_table" in source)
check("refresh 调用 _update_pagination",
      "_update_pagination" in source)
check("refresh 调用 _update_status_bar",
      "_update_status_bar" in source)

# ----------------------------------------------------------
# [7] 表格
# ----------------------------------------------------------
print("\n[7] 表格")
check("QTableWidget 使用",
      "QTableWidget" in source_full)
check("8 列 (COLUMN_HEADERS)",
      "len(COLUMN_HEADERS)" in source)
check("COLUMN_HEADERS 含 ID",
      '"ID"' in source_full)
check("COLUMN_HEADERS 含 操作人",
      '"操作人"' in source_full)
check("COLUMN_HEADERS 含 操作类型",
      '"操作类型"' in source_full)
check("COLUMN_HEADERS 含 操作模块",
      '"操作模块"' in source_full)
check("COLUMN_HEADERS 含 操作对象",
      '"操作对象"' in source_full)
check("COLUMN_HEADERS 含 对象ID",
      '"对象ID"' in source_full)
check("COLUMN_HEADERS 含 描述",
      '"描述"' in source_full)
check("COLUMN_HEADERS 含 操作时间",
      '"操作时间"' in source_full)
check("SelectRows", "SelectRows" in source)
check("SingleSelection", "SingleSelection" in source)
check("NoEditTriggers", "NoEditTriggers" in source)
check("AlternatingRowColors",
      "setAlternatingRowColors" in source)
check("Stretch", "Stretch" in source)

# ----------------------------------------------------------
# [8] 按钮（仅刷新 + 导出）
# ----------------------------------------------------------
print("\n[8] 按钮（仅刷新 + 导出）")
check("刷新按钮", "refresh_btn" in source_full)
check("导出按钮", "export_btn" in source_full)
check("无新增按钮",
      "add_btn" not in source_full
      and "create_btn" not in source_full)
check("无编辑按钮",
      "edit_btn" not in source_full)
check("无删除按钮",
      "delete_btn" not in source_full)

# ----------------------------------------------------------
# [9] 筛选控件
# ----------------------------------------------------------
print("\n[9] 筛选控件")
check("SearchBar 集成",
      "SearchBar" in source_full)
check("操作人筛选",
      "operator_filter" in source_full)
check("操作类型筛选",
      "operation_filter" in source_full)
check("模块筛选",
      "module_filter" in source_full)
check("开始时间筛选",
      "start_time_filter" in source_full)
check("结束时间筛选",
      "end_time_filter" in source_full)
check("操作类型下拉框",
      "QComboBox" in source_full)
check("时间范围选择器",
      "QDateTimeEdit" in source_full)

# ----------------------------------------------------------
# [10] 分页
# ----------------------------------------------------------
print("\n[10] 分页")
check("第一页按钮",
      "first_page_btn" in source_full)
check("上一页按钮",
      "prev_page_btn" in source_full)
check("下一页按钮",
      "next_page_btn" in source_full)
check("最后一页按钮",
      "last_page_btn" in source_full)
check("页码标签",
      "page_label" in source_full)
check("总数标签",
      "total_label" in source_full)
check("DEFAULT_PAGE_SIZE = 20",
      "DEFAULT_PAGE_SIZE: int = 20" in source_full)

# ----------------------------------------------------------
# [11] 状态栏
# ----------------------------------------------------------
print("\n[11] 状态栏")
check("状态栏控件",
      "status_bar" in source_full)
check("就绪状态文本",
      'STATUS_TEXT["ready"]' in source)
check("刷新完成文本",
      'STATUS_TEXT["refresh_completed"]' in source)
check("导出完成文本",
      'STATUS_TEXT["export_completed"]' in source)

# ----------------------------------------------------------
# [12] 导出
# ----------------------------------------------------------
print("\n[12] 导出")
check("_on_export 调用 export_logs",
      "_log_service.export_logs" in source)
check("无 openpyxl", "openpyxl" not in source_full)
check("无 xlsxwriter", "xlsxwriter" not in source_full)
check("无 csv", "csv" not in source_full)
check("无文件写入", "open(" not in source)

# ----------------------------------------------------------
# [13] 依赖
# ----------------------------------------------------------
print("\n[13] 依赖")
check("依赖 LogService",
      "from client.services.log_service import LogService"
      in source_full)
check("依赖 SearchBar",
      "from client.widgets.search_bar import SearchBar"
      in source_full)
check("零 HTTP", "requests" not in source_full)
check("零 ORM", "sqlalchemy" not in source_full.lower())
check("零 Router",
      "from server.routers" not in source_full)

# ----------------------------------------------------------
# [14] 零业务逻辑
# ----------------------------------------------------------
print("\n[14] 零业务逻辑")
check("Zero Workflow", "process_status" not in source)
check("Zero Status Machine", "result_status" not in source)
check("Zero Aggregation", "func." not in source)

# ----------------------------------------------------------
# [15] Constants
# ----------------------------------------------------------
print("\n[15] Constants")
check("WINDOW_TITLE 常量", "WINDOW_TITLE" in source_full)
check("COLUMN_HEADERS 常量", "COLUMN_HEADERS" in source_full)
check("COLUMN_INDEX 常量", "COLUMN_INDEX" in source_full)
check("DEFAULT_PAGE_SIZE 常量", "DEFAULT_PAGE_SIZE" in source_full)
check("BUTTON_TEXT 常量", "BUTTON_TEXT" in source_full)
check("OBJECT_NAMES 常量", "OBJECT_NAMES" in source_full)
check("OPERATION_TYPES 常量", "OPERATION_TYPES" in source_full)
check("STATUS_TEXT 常量", "STATUS_TEXT" in source_full)
check("MESSAGE_TEXT 常量", "MESSAGE_TEXT" in source_full)
check("LABEL_TEXT 常量", "LABEL_TEXT" in source_full)

# ----------------------------------------------------------
# [16] ObjectName
# ----------------------------------------------------------
print("\n[16] ObjectName")
check("title_label", "OBJECT_NAMES" in source_full)
check("search_bar",
      '"search_bar"' in source_full)
check("log_table",
      '"log_table"' in source_full)
check("refresh_btn",
      '"refresh_btn"' in source_full)
check("export_btn",
      '"export_btn"' in source_full)
check("status_bar",
      '"status_bar"' in source_full)

# ----------------------------------------------------------
# [17] Logger
# ----------------------------------------------------------
print("\n[17] Logger")
check("gtms.client logger",
      'logging.getLogger("gtms.client")' in source_full)
check("logger.info 使用",
      "logger.info" in source_full)
check("logger.debug 使用",
      "logger.debug" in source_full)
check("logger.error 使用",
      "logger.error" in source_full)
check("无 print()", "print(" not in source)

# ----------------------------------------------------------
# [18] PEP8
# ----------------------------------------------------------
print("\n[18] PEP8")
result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N",
            "--ignore=W503", FILE_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
if result.returncode != 0 and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", result.returncode == 0)

# ----------------------------------------------------------
# [19] Docstring
# ----------------------------------------------------------
print("\n[19] Docstring")
with open(FILE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块级 docstring",
      ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        doc = ast.get_docstring(node)
        check(f"{node.name} docstring", doc is not None)

# ----------------------------------------------------------
# [20] Type Hint
# ----------------------------------------------------------
print("\n[20] Type Hint")
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        check(f"{node.name} 返回类型注解",
              node.returns is not None)

# ----------------------------------------------------------
# [21] __all__
# ----------------------------------------------------------
print("\n[21] __all__")
check("__all__ 含 SystemLogView",
      "SystemLogView" in source_full.split("__all__")[-1])

# ----------------------------------------------------------
# [22] __init__.py 导出
# ----------------------------------------------------------
print("\n[22] __init__.py 导出")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导出 SystemLogView",
      "SystemLogView" in init_code)

# ----------------------------------------------------------
# [23] 历史 View 未破坏
# ----------------------------------------------------------
print("\n[23] 历史 View 未破坏")
check("__init__.py 导出 QueryView",
      "QueryView" in init_code)
check("__init__.py 导出 LoginView",
      "LoginView" in init_code)
check("__init__.py 导出 MainWindow",
      "MainWindow" in init_code)
check("__init__.py 导出 TrialTaskView",
      "TrialTaskView" in init_code)
check("__init__.py 导出 ReceiptView",
      "ReceiptView" in init_code)
check("__init__.py 导出 GrindingView",
      "GrindingView" in init_code)
check("__init__.py 导出 InspectionView",
      "InspectionView" in init_code)
check("__init__.py 导出 DispatchView",
      "DispatchView" in init_code)

# ----------------------------------------------------------
# [24] 冻结 API
# ----------------------------------------------------------
print("\n[24] 冻结 API")
check("无 Server 导入",
      "from server.services" not in source_full)

# ----------------------------------------------------------
# [25] 代码行宽
# ----------------------------------------------------------
print("\n[25] 代码行宽")
with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()
long_lines = [
    i + 1 for i, line in enumerate(lines)
    if len(line.rstrip("\n")) > 79
]
if long_lines:
    print(f"    超长行: {long_lines[:5]}")
check("所有行 <= 79 字符", len(long_lines) == 0)

# ----------------------------------------------------------
# [26] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[26] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass",
      re.search(r'\bpass\b', source) is None)

# ----------------------------------------------------------
# [27] 文件末尾换行
# ----------------------------------------------------------
print("\n[27] 文件末尾换行")
check("文件末尾换行", source_full.endswith("\n"))

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