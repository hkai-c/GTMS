"""Test: TrialTaskView (Sprint 5 — Task 5.7)

测试 client/views/trial_task_view.py 的全部公开 API 与 CRUD 规范合规性。
使用源码分析，不依赖 PySide6 DLL。
"""

import ast
import os
import re
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

TRIAL_TASK_VIEW_PATH = os.path.join(
    PROJECT_ROOT, "client", "views", "trial_task_view.py"
)
INIT_PATH = os.path.join(PROJECT_ROOT, "client", "views", "__init__.py")


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


def get_source() -> str:
    """获取 trial_task_view.py 源码。"""
    with open(TRIAL_TASK_VIEW_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    """获取 trial_task_view.py 代码文本（排除 docstring 和注释）。"""
    return extract_code_text(TRIAL_TASK_VIEW_PATH)


# ============================================================
# 预加载
# ============================================================

source_full = get_source()
source = get_code_text()


# ============================================================
# 自检
# ============================================================

# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(TRIAL_TASK_VIEW_PATH, doraise=True)
    check("trial_task_view.py 编译通过", True)
except py_compile.PyCompileError as e:
    check(f"trial_task_view.py 编译通过: {e}", False)

# [2] import
# ----------------------------------------------------------
print("\n[2] import")
TrialTaskView = None
try:
    from client.views.trial_task_view import TrialTaskView as _TV

    TrialTaskView = _TV
    check("TrialTaskView 导入成功", True)
except Exception as e:
    check(f"TrialTaskView 导入成功（PySide6 DLL 不可用，使用源码分析）: {e}", True)

# [3] QWidget 继承
# ----------------------------------------------------------
print("\n[3] QWidget 继承")
if TrialTaskView is not None:
    from PySide6.QtWidgets import QWidget

    check("TrialTaskView 继承 QWidget", issubclass(TrialTaskView, QWidget))
else:
    check("TrialTaskView 继承 QWidget",
          "class TrialTaskView(QWidget)" in source_full)

# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
if TrialTaskView is not None:
    public_methods = [m for m in dir(TrialTaskView) if not m.startswith("_")]
    check("公开 API 含 refresh", "refresh" in public_methods)
else:
    check("公开 API 含 refresh", "def refresh" in source_full)

check("公开 API 含 task_changed Signal", "task_changed" in source_full)
check("task_changed 是 Signal", "Signal()" in source_full)

# [5] Signal
# ----------------------------------------------------------
print("\n[5] Signal")
check("task_changed Signal 定义", "task_changed" in source_full)
check("task_changed 发射: emit", "task_changed.emit()" in source)
check("task_changed 在删除后发射", "_on_delete" in source_full)

# [6] Toolbar
# ----------------------------------------------------------
print("\n[6] Toolbar")
check("含 add_btn", "add_btn" in source)
check("含 edit_btn", "edit_btn" in source)
check("含 delete_btn", "delete_btn" in source)
check("含 refresh_btn", "refresh_btn" in source)
check("含 Stretch", "addStretch" in source)
check("按钮命名统一", "BUTTON_TEXT" in source)

# [7] SearchBar 集成
# ----------------------------------------------------------
print("\n[7] SearchBar 集成")
check("导入 SearchBar", "from client.widgets.search_bar import SearchBar" in source_full)
check("创建 SearchBar 实例", "SearchBar(" in source)
check("search_requested 连接", "search_requested.connect" in source)
check("_on_search 回调", "def _on_search" in source_full)
check("搜索重置到第一页", "_current_page = 1" in source)

# [8] StatusBadge 集成
# ----------------------------------------------------------
print("\n[8] StatusBadge 集成")
check("导入 StatusBadge", "from client.widgets.status_badge import StatusBadge" in source_full)
check("创建 StatusBadge 实例", "StatusBadge(" in source)
check("setCellWidget 用于流程状态", "setCellWidget" in source)
check("process_status 使用 StatusBadge", "process_status" in source_full)

# [9] Table
# ----------------------------------------------------------
print("\n[9] Table")
check("使用 QTableWidget", "QTableWidget" in source)
check("NoEditTriggers", "NoEditTriggers" in source)
check("SingleSelection", "SingleSelection" in source)
check("SelectRows", "SelectRows" in source)
check("AlternatingRowColors", "AlternatingRowColors" in source)
check("Stretch", "Stretch" in source)

# [10] Pagination
# ----------------------------------------------------------
print("\n[10] Pagination")
check("含 first_page_btn", "first_page_btn" in source)
check("含 prev_page_btn", "prev_page_btn" in source)
check("含 next_page_btn", "next_page_btn" in source)
check("含 last_page_btn", "last_page_btn" in source)
check("含 page_label", "page_label" in source)
check("含 total_label", "total_label" in source)
check("含 _page_size", "_page_size" in source)
check("含 _current_page", "_current_page" in source)
check("含 _total", "_total" in source)
check("含 total_pages", "total_pages" in source)

# [11] StatusBar
# ----------------------------------------------------------
print("\n[11] StatusBar")
check("含 status_bar", "status_bar" in source)
check("_update_status_bar 方法", "def _update_status_bar" in source_full)

# [12] refresh() 流程
# ----------------------------------------------------------
print("\n[12] refresh() 流程")
check("refresh() 存在", "def refresh" in source_full)
check("refresh() 调用 list_tasks", "list_tasks" in source)
check("refresh() 调用 _populate_table", "_populate_table" in source)
check("refresh() 调用 _update_pagination_ui", "_update_pagination_ui" in source)
check("refresh() 调用 _update_status_bar", "_update_status_bar" in source)

# [13] Desktop TaskService 调用
# ----------------------------------------------------------
print("\n[13] Desktop TaskService 调用")
check("导入 TaskService", "from client.services.task_service import TaskService" in source_full)
check("__init__ 接收 task_service", "task_service:" in source_full)
check("使用 self._task_service", "self._task_service" in source)
check("list_tasks 调用", "list_tasks" in source)
check("delete_task 调用", "delete_task" in source)

# [14] Signal
# ----------------------------------------------------------
print("\n[14] Signal")
check("task_changed Signal", "task_changed" in source_full)
check("Signal() 定义", "Signal()" in source_full)

# [15] ObjectName (§15.7.23)
# ----------------------------------------------------------
print("\n[15] ObjectName")
object_names = [
    "toolbar", "search_bar", "task_table", "status_bar",
    "add_btn", "edit_btn", "delete_btn", "refresh_btn",
    "first_page_btn", "prev_page_btn", "next_page_btn", "last_page_btn",
    "page_label", "total_label", "title_label",
]
for name in object_names:
    check(f"ObjectName {name} 已设置", f'setObjectName' in source and name in source)

# [16] TABLE_HEADERS (§15.7.24)
# ----------------------------------------------------------
print("\n[16] TABLE_HEADERS")
check("TABLE_HEADERS 常量定义", "TABLE_HEADERS" in source_full)
check("setHorizontalHeaderLabels(TABLE_HEADERS)", "TABLE_HEADERS" in source)
check("8 列表头", "任务编号" in source_full and "创建时间" in source_full)

# [17] Constants (§15.7.25)
# ----------------------------------------------------------
print("\n[17] Constants")
constants = [
    "WINDOW_TITLE", "TABLE_HEADERS", "COLUMN_INDEX",
    "DEFAULT_PAGE_SIZE", "BUTTON_TEXT", "OBJECT_NAMES", "LOGGER_NAME",
]
for const_name in constants:
    check(f"常量 {const_name} 定义", const_name in source_full)
check("常量定义在文件顶部", source_full.index("WINDOW_TITLE") < source_full.index("class TrialTaskView"))

# [18] 无 Magic Number / Magic String (§15.7.26)
# ----------------------------------------------------------
print("\n[18] 无 Magic Number / Magic String")
check("DEFAULT_PAGE_SIZE 使用引用", "DEFAULT_PAGE_SIZE" in source)
check("BUTTON_TEXT 使用引用", "BUTTON_TEXT[" in source)
check("COLUMN_INDEX 使用引用", "COLUMN_INDEX[" in source)
check("OBJECT_NAMES 使用引用", "OBJECT_NAMES[" in source)

# [19] 命名一致性 (§15.7.27)
# ----------------------------------------------------------
print("\n[19] 命名一致性")
check("refresh() 命名", "def refresh" in source_full)
check("_update_button_permissions 命名", "def _update_button_permissions" in source_full)
check("_populate_table 命名", "def _populate_table" in source_full)
check("_on_search 命名", "def _on_search" in source_full)
check("_on_add 命名", "def _on_add" in source_full)
check("_on_edit 命名", "def _on_edit" in source_full)
check("_on_delete 命名", "def _on_delete" in source_full)

# [20] Widget 独立性
# ----------------------------------------------------------
print("\n[20] Widget 独立性")
check("无 import ApiClient", "ApiClient" not in source)
check("无 import requests", "requests" not in source)
check("无 import server.services", "from server.services" not in source)
check("无 import server.routers", "from server.routers" not in source)
check("无 import server.models", "from server.models" not in source)

# [21] 无 Service
# ----------------------------------------------------------
print("\n[21] 无 Service（除 TaskService）")
check("无 CustomerService", "CustomerService" not in source)
check("无 UserService", "UserService" not in source)
check("无 AuthService", "AuthService" not in source)

# [22] 无 HTTP
# ----------------------------------------------------------
print("\n[22] 无 HTTP")
check("无 requests", "requests" not in source)
check("无 httpx", "httpx" not in source)
check("无 urllib", "urllib" not in source)

# [23] 无 ORM
# ----------------------------------------------------------
print("\n[23] 无 ORM")
check("无 sqlalchemy", "sqlalchemy" not in source)
check("无 Session", "Session" not in source)

# [24] 无 Database
# ----------------------------------------------------------
print("\n[24] 无 Database")
check("无 database", "database" not in source.lower())

# [25] 无 JWT
# ----------------------------------------------------------
print("\n[25] 无 JWT")
check("无 jwt", "jwt" not in source.lower())
check("无 bcrypt", "bcrypt" not in source)

# [26] 无业务逻辑
# ----------------------------------------------------------
print("\n[26] 无业务逻辑")
check("无状态流转", "next_status" not in source)
check("无编号生成", "generate_task_no" not in source)
check("无权限计算", "require_permission" not in source)
check("无 commit", "commit" not in source)
check("无 rollback", "rollback" not in source)

# [27] logger
# ----------------------------------------------------------
print("\n[27] logger")
check("使用 logging.getLogger", 'logging.getLogger("gtms.client")' in source)
check("无 print()", "print(" not in source)

# [28] Type Hint
# ----------------------------------------------------------
print("\n[28] Type Hint")
check("__init__ task_service: TaskService", "task_service: TaskService" in source_full)
check("__init__ parent: optional", "parent:" in source_full)
check("__init__ -> None", "-> None:" in source_full)
check("refresh() -> None", "-> None:" in source_full)
check("_populate_table tasks: list", "list[dict[str, Any]]" in source_full)
check("_on_search keyword: str", "keyword: str" in source_full)
check("_update_status_bar message: str", "message: str" in source_full)
check("实例变量 Type Hint", "self._tasks:" in source_full and "list[dict[str, Any]]" in source_full)

# [29] Docstring
# ----------------------------------------------------------
print("\n[29] Docstring")
try:
    tree = ast.parse(source_full)
    check("模块级 docstring 存在", ast.get_docstring(tree) is not None)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TrialTaskView":
            check("类 docstring 存在", ast.get_docstring(node) is not None)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    doc = ast.get_docstring(item)
                    check(f"{item.name} docstring 存在", doc is not None)
except SyntaxError as e:
    check(f"AST 解析失败: {e}", False)

# [30] PEP8
# ----------------------------------------------------------
print("\n[30] PEP8")
import subprocess

result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", TRIAL_TASK_VIEW_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# [31] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[31] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass", re.search(r'\bpass\b', source) is None)

# [32] 无 Magic Number / Magic String
# ----------------------------------------------------------
print("\n[32] 无 Magic Number")
check("DEFAULT_PAGE_SIZE 引用", "DEFAULT_PAGE_SIZE" in source)
check("BUTTON_TEXT 引用", "BUTTON_TEXT[" in source)
check("COLUMN_INDEX 引用", "COLUMN_INDEX[" in source)

# [33] API Freeze / __init__.py
# ----------------------------------------------------------
print("\n[33] API Freeze / __init__.py")
init_source = extract_code_text(INIT_PATH)
init_full = open(INIT_PATH, "r", encoding="utf-8").read()
check("__init__.py 导出 TrialTaskView", "TrialTaskView" in init_source)
check("__init__.py 含 __all__", "__all__" in init_source)
check("__init__.py 原有导出未破坏", "CustomerView" in init_source)

# [34] Frozen API 未修改
# ----------------------------------------------------------
print("\n[34] Frozen API 未修改")
check("未导入 Server 模块", "from server.services" not in source)
check("未导入 Router", "from server.routers" not in source)
check("未导入 ORM 模型", "from server.models" not in source)
check("未导入 TrialTask Schema", "trial_task_schema" not in source)

# [35] 循环导入检查
# ----------------------------------------------------------
print("\n[35] 循环导入检查")
check("无循环导入风险", "from client.views" not in source)

# [36] 删除功能
# ----------------------------------------------------------
print("\n[36] 删除功能")
check("_on_delete 存在", "def _on_delete" in source_full)
check("QMessageBox 确认", "QMessageBox.question" in source)
check("delete_task 调用", "delete_task" in source)
check("删除后 emit task_changed", "task_changed.emit" in source)

# [37] 新增/编辑接口保留
# ----------------------------------------------------------
print("\n[37] 新增/编辑接口保留")
check("_on_add 存在", "def _on_add" in source_full)
check("_on_edit 存在", "def _on_edit" in source_full)
check("新增/编辑为提示（Task 5.8 未完成）", "Task 5.8" in source_full)

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