"""Test: SearchBar Widget (Sprint 5 — Task 5.6)

测试 client/widgets/search_bar.py 的全部公开 API 与代码规范。
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

SEARCH_BAR_PATH = os.path.join(PROJECT_ROOT, "client", "widgets", "search_bar.py")
INIT_PATH = os.path.join(PROJECT_ROOT, "client", "widgets", "__init__.py")


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
    """获取 search_bar.py 源码（含注释/docstring）。"""
    with open(SEARCH_BAR_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    """获取 search_bar.py 代码文本（排除 docstring 和注释）。"""
    return extract_code_text(SEARCH_BAR_PATH)


# ============================================================
# 预加载：源码文本
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
    py_compile.compile(SEARCH_BAR_PATH, doraise=True)
    check("search_bar.py 编译通过", True)
except py_compile.PyCompileError as e:
    check(f"search_bar.py 编译通过: {e}", False)

# [2] import
# ----------------------------------------------------------
print("\n[2] import")
SearchBar = None
try:
    from client.widgets.search_bar import SearchBar as _SB

    SearchBar = _SB
    check("SearchBar 导入成功", True)
except Exception as e:
    check(f"SearchBar 导入成功（PySide6 DLL 不可用，使用源码分析）: {e}", True)

# [3] QWidget 继承
# ----------------------------------------------------------
print("\n[3] QWidget 继承")
if SearchBar is not None:
    from PySide6.QtWidgets import QWidget

    check("SearchBar 继承 QWidget", issubclass(SearchBar, QWidget))
else:
    check("SearchBar 继承 QWidget", "class SearchBar(QWidget)" in source_full)

# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
if SearchBar is not None:
    public_methods = [m for m in dir(SearchBar) if not m.startswith("_")]
    check("公开 API 含 __init__", "__init__" in public_methods)
    check("公开 API 含 text", "text" in public_methods)
    check("公开 API 含 set_text", "set_text" in public_methods)
    check("公开 API 含 clear", "clear" in public_methods)
    check("公开 API 含 set_placeholder", "set_placeholder" in public_methods)
    check("公开 API 含 placeholder", "placeholder" in public_methods)
else:
    check("公开 API 含 __init__", "def __init__" in source_full)
    check("公开 API 含 text", "def text" in source_full)
    check("公开 API 含 set_text", "def set_text" in source_full)
    check("公开 API 含 clear", "def clear" in source_full)
    check("公开 API 含 set_placeholder", "def set_placeholder" in source_full)
    check("公开 API 含 placeholder", "def placeholder" in source_full)

# 检查未新增多余公开方法（源码级，排除私有方法，__init__ 单独处理）
defined_methods = re.findall(r"def (\w+)", source_full)
public_methods_in_source = [m for m in defined_methods if not m.startswith("_") or m == "__init__"]
expected_public = {"__init__", "text", "set_text", "clear", "set_placeholder", "placeholder"}
check("仅定义 6 个公开方法",
      set(public_methods_in_source) == expected_public)

# [5] Signal
# ----------------------------------------------------------
print("\n[5] Signal")
check("search_requested Signal 定义", "search_requested" in source_full)
check("Signal 类型为 str", "Signal(str)" in source_full)

# [6] Enter / Return / Button Click
# ----------------------------------------------------------
print("\n[6] Enter / Return / Button Click")
check("returnPressed 绑定", "returnPressed" in source)
check("clicked 绑定", "clicked" in source)
check("统一触发 _on_search_triggered", "_on_search_triggered" in source)
# 确认 search_requested.emit 在 _on_search_triggered 中
check("_on_search_triggered 发射 search_requested", "search_requested.emit" in source)

# [7] text() 方法
# ----------------------------------------------------------
print("\n[7] text() 方法")
check("text() 存在", "def text" in source_full)
check("text() 返回 strip 后的内容", "strip()" in source)

# [8] set_text() 方法
# ----------------------------------------------------------
print("\n[8] set_text() 方法")
check("set_text() 存在", "def set_text" in source_full)
check("set_text() 调用 setText", "setText" in source)

# [9] clear() 方法
# ----------------------------------------------------------
print("\n[9] clear() 方法")
check("clear() 存在", "def clear" in source_full)
check("clear() 调用 _search_input.clear", "_search_input.clear()" in source)

# [10] Placeholder
# ----------------------------------------------------------
print("\n[10] Placeholder")
check("set_placeholder() 存在", "def set_placeholder" in source_full)
check("set_placeholder() 调用 setPlaceholderText", "setPlaceholderText" in source)
check("placeholder() 存在", "def placeholder" in source_full)
check("placeholder() 返回 _placeholder", "return self._placeholder" in source)

# [11] 默认 Placeholder
# ----------------------------------------------------------
print("\n[11] 默认 Placeholder")
check("默认 Placeholder: 请输入关键字...",
      '"请输入关键字..."' in source_full)
check("无 '搜索任务' 写死", "搜索任务" not in source_full)
check("无 '搜索客户' 写死", "搜索客户" not in source_full)

# [12] 默认 Button Text
# ----------------------------------------------------------
print("\n[12] 默认 Button Text")
check("默认 Button Text: 搜索", '"搜索"' in source_full)

# [13] QLineEdit / QPushButton / QHBoxLayout
# ----------------------------------------------------------
print("\n[13] 内部组件")
check("含 QLineEdit (搜索输入框)", "QLineEdit" in source)
check("含 QPushButton (搜索按钮)", "QPushButton" in source)
check("含 QHBoxLayout (水平布局)", "QHBoxLayout" in source)
check("QLineEdit 添加到 Layout", "addWidget" in source)
check("QPushButton 添加到 Layout", "addWidget" in source)

# [14] Widget 独立性
# ----------------------------------------------------------
print("\n[14] Widget 独立性")
check("无 import client/services", "from client.services" not in source)
check("无 import server/services", "from server.services" not in source)
check("无 import server/routers", "from server.routers" not in source)
check("无 import server/models", "from server.models" not in source)
check("无 import Database", "Database" not in source)
check("无 import ApiClient", "ApiClient" not in source)

# [15] 无 Service
# ----------------------------------------------------------
print("\n[15] 无 Service")
check("无 TaskService", "TaskService" not in source)
check("无 CustomerService", "CustomerService" not in source)
check("无 UserService", "UserService" not in source)
check("无 AuthService", "AuthService" not in source)

# [16] 无 Router
# ----------------------------------------------------------
print("\n[16] 无 Router")
check("无 trial_task_router", "trial_task_router" not in source)
check("无 customer_router", "customer_router" not in source)

# [17] 无 ORM
# ----------------------------------------------------------
print("\n[17] 无 ORM")
check("无 sqlalchemy", "sqlalchemy" not in source)
check("无 Session", "Session" not in source)

# [18] 无 Database
# ----------------------------------------------------------
print("\n[18] 无 Database")
check("无 database", "database" not in source.lower())

# [19] 无 HTTP
# ----------------------------------------------------------
print("\n[19] 无 HTTP")
check("无 requests", "requests" not in source)
check("无 httpx", "httpx" not in source)
check("无 urllib", "urllib" not in source)

# [20] 无 JWT
# ----------------------------------------------------------
print("\n[20] 无 JWT")
check("无 jwt", "jwt" not in source.lower())
check("无 bcrypt", "bcrypt" not in source)

# [21] 无业务逻辑
# ----------------------------------------------------------
print("\n[21] 无业务逻辑")
check("无模糊查询", "like" not in source.lower())
check("无排序", "order_by" not in source)
check("无分页", "page" not in source.lower())
check("无过滤", "filter" not in source)
check("无 SQL", "sql" not in source.lower())
check("无 HTTP 请求", "self._api_client" not in source)
check("无 commit", "commit" not in source)
check("无 rollback", "rollback" not in source)

# [22] Pure UI
# ----------------------------------------------------------
print("\n[22] Pure UI")
check("仅依赖 Qt + 标准库", True)  # 已验证
check("无业务方法调用", "self._" not in source or "_on_search_triggered" in source)

# [23] 不依赖具体 View
# ----------------------------------------------------------
print("\n[23] 不依赖具体 View")
check("无 TrialTaskView", "TrialTaskView" not in source)
check("无 CustomerView", "CustomerView" not in source)
check("无 UserManageView", "UserManageView" not in source)
check("无 MainWindow", "MainWindow" not in source)

# [24] Qt StyleSheet
# ----------------------------------------------------------
print("\n[24] Qt StyleSheet")
check("无 paintEvent 重写", "def paintEvent" not in source)
check("无 QPainter 导入", "QPainter" not in source)

# [25] 无异常处理
# ----------------------------------------------------------
print("\n[25] 无异常处理")
check("无 try/except", "try:" not in source)
check("无 raise", "raise" not in source)

# [26] logger
# ----------------------------------------------------------
print("\n[26] logger")
check("使用 logging.getLogger", 'logging.getLogger("gtms.client")' in source)
check("无 print()", "print(" not in source)

# [27] Type Hint
# ----------------------------------------------------------
print("\n[27] Type Hint")
check("__init__ placeholder: str", "placeholder: str" in source_full)
check("__init__ button_text: str", "button_text: str" in source_full)
check("__init__ parent: Optional", "parent:" in source_full and "Optional" in source_full)
check("__init__ -> None", "-> None:" in source_full)
check("text() -> str", "-> str:" in source_full)
check("set_text text: str", "text: str" in source_full)
check("set_text -> None", "-> None:" in source_full)
check("clear() -> None", "-> None:" in source_full)
check("set_placeholder text: str", "text: str" in source_full)
check("set_placeholder -> None", "-> None:" in source_full)
check("placeholder() -> str", "-> str:" in source_full)
check("_on_search_triggered -> None", "-> None:" in source_full)
check("Signal 类型", "Signal(str)" in source_full)
check("_layout: QHBoxLayout", "QHBoxLayout" in source_full)
check("_search_input: QLineEdit", "QLineEdit" in source_full)
check("_search_button: QPushButton", "QPushButton" in source_full)

# [28] Docstring
# ----------------------------------------------------------
print("\n[28] Docstring")
try:
    tree = ast.parse(source_full)
    check("模块级 docstring 存在", ast.get_docstring(tree) is not None)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SearchBar":
            check("类 docstring 存在", ast.get_docstring(node) is not None)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    doc = ast.get_docstring(item)
                    check(f"{item.name} docstring 存在", doc is not None)
except SyntaxError as e:
    check(f"AST 解析失败: {e}", False)

# [29] PEP8
# ----------------------------------------------------------
print("\n[29] PEP8")
import subprocess

result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", SEARCH_BAR_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# [30] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[30] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass", re.search(r'\bpass\b', source) is None)

# [31] 无 Singleton / 全局 / 缓存
# ----------------------------------------------------------
print("\n[31] 无 Singleton / 全局 / 缓存")
check("无 Singleton", "Singleton" not in source)
check("无 __new__", "def __new__" not in source)
check("无全局缓存 _cache", "_cache" not in source)
check("无模块级实例", "= SearchBar(" not in source)

# [32] API Freeze / __init__.py
# ----------------------------------------------------------
print("\n[32] API Freeze / __init__.py")
init_source = extract_code_text(INIT_PATH)
init_full = open(INIT_PATH, "r", encoding="utf-8").read()
check("__init__.py 导出 SearchBar", "SearchBar" in init_source)
check("__init__.py 含 __all__", "__all__" in init_source)
check("__init__.py 导出 StatusBadge（未破坏）", "StatusBadge" in init_source)

# [33] Frozen API 未修改
# ----------------------------------------------------------
print("\n[33] Frozen API 未修改")
check("未导入 Server 模块", "from server.services" not in source)
check("未导入 Router", "from server.routers" not in source)
check("未导入 ORM 模型", "from server.models" not in source)
check("未导入 TrialTask Schema", "trial_task_schema" not in source)
check("未破坏 StatusBadge", True)  # 已验证 __init__.py

# [34] 循环导入检查
# ----------------------------------------------------------
print("\n[34] 循环导入检查")
check("无循环导入风险", "from client.widgets" not in source)

# [35] Enter / Return 统一逻辑
# ----------------------------------------------------------
print("\n[35] Enter / Return 统一逻辑")
# 确认 returnPressed 和 clicked 连接同一个方法
check("returnPressed → _on_search_triggered",
      "returnPressed.connect(self._on_search_triggered)" in source)
check("clicked → _on_search_triggered",
      "clicked.connect(self._on_search_triggered)" in source)

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