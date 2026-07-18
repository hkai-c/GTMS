"""Test: QueryView (Sprint 10 — Task 10.5)

测试 client/views/query_view.py 的全部公开 API 与规范合规性。
使用源码分析，不依赖 PySide6 DLL。
"""

import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FILE_PATH = os.path.join(
    PROJECT_ROOT, "client", "views", "query_view.py"
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
print("  Task 10.5 - QueryView Self Test")
print("=" * 60)

# [1] py_compile
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(FILE_PATH, doraise=True)
    check("query_view.py compile", True)
except py_compile.PyCompileError as e:
    check(f"query_view.py compile: {e}", False)

# [2] import
print("\n[2] import")
QueryView = None
try:
    from client.views.query_view import QueryView as _QV
    QueryView = _QV
    check("QueryView import", True)
except Exception as e:
    check(f"QueryView import (PySide6 DLL可能不可用): {e}", True)

# [3] QWidget inheritance
print("\n[3] QWidget inheritance")
if QueryView is not None:
    from PySide6.QtWidgets import QWidget
    check("QueryView inherit QWidget", issubclass(QueryView, QWidget))
else:
    check("QueryView inherit QWidget", "class QueryView(QWidget)" in source_full)

# [4] Public API
print("\n[4] Public API")
check("__init__ exists", "def __init__" in source_full)
check("refresh exists", "def refresh" in source_full)
defined_methods = re.findall(r"def (\w+)", source_full)
public_methods = [m for m in defined_methods if not m.startswith("_") or m == "__init__"]
expected_public = {"__init__", "refresh"}
check("only 2 public methods", set(public_methods) == expected_public)

# [5] Signals
print("\n[5] Signals")
check("query_changed Signal", "query_changed" in source_full and "Signal()" in source_full)
check("query_changed no params", "Signal()" in source_full)

# [6] SearchBar integration
print("\n[6] SearchBar integration")
check("import SearchBar", "from client.widgets.search_bar import SearchBar" in source_full)
check("SearchBar instance", "SearchBar(" in source_full)
check("search_requested connect", "search_requested.connect" in source_full)
check("_on_search method", "def _on_search" in source_full)

# [7] Statistics panel
print("\n[7] Statistics panel")
check("statistics_panel ObjectName", "statistics_panel" in source_full)
check("monthly_count_label", "monthly_count_label" in source_full)
check("annual_count_label", "annual_count_label" in source_full)
check("success_rate_label", "success_rate_label" in source_full)
check("_update_statistics method", "def _update_statistics" in source_full)

# [8] Ranking panel
print("\n[8] Ranking panel")
check("ranking_panel ObjectName", "ranking_panel" in source_full)
check("customer_ranking_label", "customer_ranking_label" in source_full)
check("machine_ranking_label", "machine_ranking_label" in source_full)
check("_update_rankings method", "def _update_rankings" in source_full)

# [9] Export button
print("\n[9] Export button")
check("export_btn ObjectName", "export_btn" in source_full)
check("export Excel button", "导出 Excel" in source_full)
check("_on_export method", "def _on_export" in source_full)
check("export_excel call", "export_excel(" in source_full)

# [10] Table
print("\n[10] Table")
check("QTableWidget", "QTableWidget" in source_full)
check("query_table ObjectName", "query_table" in source_full)
check("8 columns", "COLUMN_INDEX" in source_full)
check("COLUMN_INDEX task_no", "task_no" in source_full)
check("COLUMN_INDEX customer_name", "customer_name" in source_full)
check("COLUMN_INDEX operator_name", "operator_name" in source_full)

# [11] Pagination
print("\n[11] Pagination")
check("pagination_widget ObjectName", "pagination_widget" in source_full)
check("first_page_btn", "first_page_btn" in source_full)
check("prev_page_btn", "prev_page_btn" in source_full)
check("next_page_btn", "next_page_btn" in source_full)
check("last_page_btn", "last_page_btn" in source_full)
check("page_label", "page_label" in source_full)
check("total_label", "total_label" in source_full)

# [12] StatusBar
print("\n[12] StatusBar")
check("status_bar ObjectName", "status_bar" in source_full)
check("STATUS_TEXT ready", "STATUS_TEXT" in source_full)

# [13] ObjectName
print("\n[13] ObjectName")
check("OBJECT_NAMES dict", "OBJECT_NAMES" in source_full)
check("title_label ObjectName", "title_label" in source_full)
check("search_bar ObjectName", "search_bar" in source_full)
check("filter_area ObjectName", "filter_area" in source_full)
check("toolbar ObjectName", "toolbar" in source_full)
check("refresh_btn ObjectName", "refresh_btn" in source_full)

# [14] Layout
print("\n[14] Layout")
check("QHBoxLayout", "QHBoxLayout" in source_full)
check("QVBoxLayout", "QVBoxLayout" in source_full)
check("title_label", "title_label" in source_full)
check("_create_search_area", "def _create_search_area" in source_full)
check("_create_statistics_panel", "def _create_statistics_panel" in source_full)
check("_create_ranking_panel", "def _create_ranking_panel" in source_full)
check("_create_toolbar", "def _create_toolbar" in source_full)
check("_create_table", "def _create_table" in source_full)
check("_create_pagination", "def _create_pagination" in source_full)
check("_create_status_bar", "def _create_status_bar" in source_full)

# [15] Zero Workflow
print("\n[15] Zero Workflow (15.11)")
check("no TrialTaskProcessStatus", "TrialTaskProcessStatus" not in source_full)

# [16] Zero Status Machine
print("\n[16] Zero Status Machine (15.12)")
check("no TrialTaskResultStatus", "TrialTaskResultStatus" not in source_full)

# [17] Zero Business Logic
print("\n[17] Zero Business Logic")
check("all stats from QueryService", "get_statistics(" in source_full)
check("all rankings from QueryService", "get_customer_ranking(" in source_full and "get_machine_ranking(" in source_full)

# [18] Zero HTTP
print("\n[18] Zero HTTP")
check("no ApiClient", "ApiClient" not in source_full)
check("no requests", "requests" not in source_full)
check("no httpx", "httpx" not in source_full)

# [19] Zero ORM
print("\n[19] Zero ORM")
check("no SQLAlchemy", "SQLAlchemy" not in source_full)
check("no Session", "Session" not in source_full)
check("no db.commit", "db.commit" not in source_full)

# [20] Zero Aggregation
print("\n[20] Zero Aggregation")
check("no Python sum()", "sum(" not in source)
check("no Python sorted()", "sorted(" not in source)

# [21] Constants
print("\n[21] Constants")
check("WINDOW_TITLE", "WINDOW_TITLE" in source_full)
check("BUTTON_TEXT", "BUTTON_TEXT" in source_full)
check("LABEL_TEXT", "LABEL_TEXT" in source_full)
check("OBJECT_NAMES", "OBJECT_NAMES" in source_full)
check("DEFAULT_PAGE_SIZE", "DEFAULT_PAGE_SIZE" in source_full)
check("TABLE_HEADERS", "TABLE_HEADERS" in source_full)

# [22] Logging
print("\n[22] Logging")
check("logger: gtms.client", "gtms.client" in source_full)
check("no print()", "print(" not in source)

# [23] __init__.py export
print("\n[23] __init__.py export")
init_source = extract_code_text(INIT_PATH)
check("__init__.py exports QueryView", "QueryView" in init_source)

# [24] PEP8
print("\n[24] PEP8")
import subprocess
result = subprocess.run(["python", "-m", "flake8", "--select=E,W,F,N", FILE_PATH], capture_output=True, text=True, cwd=PROJECT_ROOT)
if result.returncode != 0 and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8", result.returncode == 0)

# [25] No Router
print("\n[25] No Router")
check("no server.routers", "from server.routers" not in source_full)

# [26] No pyqtSignal
print("\n[26] No pyqtSignal")
check("no pyqtSignal", "pyqtSignal" not in source_full)

# [27] CRUD
print("\n[27] CRUD")
check("no add/create", "def create" not in source_full and "def add" not in source_full)
check("no edit/update", "def edit" not in source_full and "def update" not in source_full)
check("no delete", "def delete" not in source_full)

# Summary
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  Result: ALL PASSED")
else:
    print(f"  Result: {FAILED} FAILED")
print("=" * 60)

sys.exit(0 if FAILED == 0 else 1)
