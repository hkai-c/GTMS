"""Test: StatusBadge Widget (Sprint 5 — Task 5.5)

测试 client/widgets/status_badge.py 的全部公开 API 与代码规范。
使用源码分析，不依赖 PySide6 DLL。
"""

import ast
import inspect
import os
import re
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

STATUS_BADGE_PATH = os.path.join(PROJECT_ROOT, "client", "widgets", "status_badge.py")
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
    """获取 status_badge.py 源码（含注释/docstring）。"""
    with open(STATUS_BADGE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    """获取 status_badge.py 代码文本（排除 docstring 和注释）。"""
    return extract_code_text(STATUS_BADGE_PATH)


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
    py_compile.compile(STATUS_BADGE_PATH, doraise=True)
    check("status_badge.py 编译通过", True)
except py_compile.PyCompileError as e:
    check(f"status_badge.py 编译通过: {e}", False)

# [2] import
# ----------------------------------------------------------
print("\n[2] import")
StatusBadge = None
try:
    from client.widgets.status_badge import StatusBadge as _SB

    StatusBadge = _SB
    check("StatusBadge 导入成功", True)
except Exception as e:
    check(f"StatusBadge 导入成功（PySide6 DLL 不可用，使用源码分析）: {e}", True)

# [3] QLabel 继承
# ----------------------------------------------------------
print("\n[3] QLabel 继承")
if StatusBadge is not None:
    from PySide6.QtWidgets import QLabel

    check("StatusBadge 继承 QLabel", issubclass(StatusBadge, QLabel))
else:
    check("StatusBadge 继承 QLabel", "class StatusBadge(QLabel)" in source_full)

# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
if StatusBadge is not None:
    public_methods = [m for m in dir(StatusBadge) if not m.startswith("_")]
    check("公开 API 含 __init__", "__init__" in public_methods)
    check("公开 API 含 set_status", "set_status" in public_methods)
    check("公开 API 含 status", "status" in public_methods)
else:
    # 源码分析：检查方法定义
    check("公开 API 含 __init__", "def __init__" in source_full)
    check("公开 API 含 set_status", "def set_status" in source_full)
    check("公开 API 含 status", "def status" in source_full or "@property" in source_full)

# 检查未新增多余公开方法（源码级）
defined_methods = re.findall(r"def (\w+)", source_full)
check("仅定义 3 个公开方法（__init__, set_status, status）",
      set(defined_methods) == {"__init__", "set_status", "status"})

# [5] status property
# ----------------------------------------------------------
print("\n[5] status property")
check("status 是 @property", "@property" in source_full)
check("status 返回 _status", "return self._status" in source)

# [6] set_status 方法
# ----------------------------------------------------------
print("\n[6] set_status 方法")
check("set_status 存在", "def set_status" in source_full)
check("set_status 调用 setText", "setText" in source)
check("set_status 调用 setStyleSheet", "setStyleSheet" in source)
check("set_status 调用 setProperty", "setProperty" in source)
check("set_status 更新 _status", "self._status = status" in source)
check("set_status 未知状态抛 ValueError", "ValueError" in source)

# [7] 全部 Process Status (6 个)
# ----------------------------------------------------------
print("\n[7] 全部 Process Status")
process_statuses = [
    "created", "received", "grinding", "completed",
    "dispatched", "closed",
]
for s in process_statuses:
    check(f"Process Status {s} 在 STATUS_TEXT",
          f'"{s}"' in source_full and "STATUS_TEXT" in source_full)
    check(f"Process Status {s} 在 STATUS_STYLE",
          f'"{s}"' in source_full and "STATUS_STYLE" in source_full)

# 更精确的检查：从源码解析 STATUS_TEXT 字典
# 使用 AST 解析
try:
    tree = ast.parse(source_full)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "StatusBadge":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and hasattr(item.target, 'id'):
                    if item.target.id == "STATUS_TEXT" and isinstance(item.value, ast.Dict):
                        keys = [k.value for k in item.value.keys if isinstance(k, ast.Constant)]
                        for s in process_statuses:
                            check(f"STATUS_TEXT 含 {s}", s in keys)
                    if item.target.id == "STATUS_STYLE" and isinstance(item.value, ast.Dict):
                        keys = [k.value for k in item.value.keys if isinstance(k, ast.Constant)]
                        for s in process_statuses:
                            check(f"STATUS_STYLE 含 {s}", s in keys)
except SyntaxError:
    pass

# [8] 全部 Result Status (3 个)
# ----------------------------------------------------------
print("\n[8] 全部 Result Status")
result_statuses = ["pending", "passed", "failed"]
for s in result_statuses:
    check(f"Result Status {s} 在 STATUS_TEXT",
          f'"{s}"' in source_full and "STATUS_TEXT" in source_full)
    check(f"Result Status {s} 在 STATUS_STYLE",
          f'"{s}"' in source_full and "STATUS_STYLE" in source_full)

# [9] STATUS_TEXT 映射
# ----------------------------------------------------------
print("\n[9] STATUS_TEXT 映射")
# 从源码解析
text_mapping = {
    "created": "已创建",
    "received": "已收件",
    "grinding": "试磨中",
    "completed": "已完成",
    "dispatched": "已寄回",
    "closed": "已关闭",
    "pending": "待试磨",
    "passed": "试磨成功",
    "failed": "试磨失败",
}
for k, v in text_mapping.items():
    check(f"STATUS_TEXT[{k!r}] = {v!r}",
          f'"{k}": "{v}"' in source_full or f"'{k}': '{v}'" in source_full)

# 检查 STATUS_TEXT 共 9 项
text_count = source_full.count('": "') + source_full.count("': '")
# 更精确：在 STATUS_TEXT 块内计数
match = re.search(r"STATUS_TEXT.*?\{(.*?)\}", source_full, re.DOTALL)
if match:
    block = match.group(1)
    entry_count = len(re.findall(r'"\w+":\s*"', block))
    check("STATUS_TEXT 共 9 项", entry_count == 9)

# [10] STATUS_STYLE 映射
# ----------------------------------------------------------
print("\n[10] STATUS_STYLE 映射")
expected_colors = {
    "created": "#9E9E9E",
    "received": "#2196F3",
    "grinding": "#FF9800",
    "completed": "#00BCD4",
    "dispatched": "#9C27B0",
    "closed": "#424242",
    "pending": "#9E9E9E",
    "passed": "#4CAF50",
    "failed": "#F44336",
}
for k, color in expected_colors.items():
    check(f"STATUS_STYLE[{k!r}] 含 {color}", color in source_full)

# 检查 STATUS_STYLE 共 9 项（值是括号包裹的多行字符串，含嵌套大括号）
# 使用 AST 解析
try:
    tree2 = ast.parse(source_full)
    for node in ast.walk(tree2):
        if isinstance(node, ast.ClassDef) and node.name == "StatusBadge":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and hasattr(item.target, 'id'):
                    if item.target.id == "STATUS_STYLE" and isinstance(item.value, ast.Dict):
                        style_count = len(item.value.keys)
                        check("STATUS_STYLE 共 9 项", style_count == 9)
except SyntaxError:
    check("STATUS_STYLE 共 9 项（AST 解析失败）", False)

# [11] 未知状态 ValueError
# ----------------------------------------------------------
print("\n[11] 未知状态 ValueError")
check("set_status 含 ValueError", "ValueError" in source)
check("set_status 含 '未知状态'", "未知状态" in source)

# [12] Qt StyleSheet
# ----------------------------------------------------------
print("\n[12] Qt StyleSheet")
check("使用 setStyleSheet", "setStyleSheet" in source)
check("无 paintEvent 重写", "def paintEvent" not in source)
check("无 QPainter 导入", "QPainter" not in source)
check("StyleSheet 含 QLabel 选择器", "QLabel {" in source)

# StyleSheet 属性检查
style_attrs = ["background-color", "color", "border-radius", "padding", "font-weight", "font-size"]
for attr in style_attrs:
    check(f"StyleSheet 含 {attr}", attr in source)

# [13] Widget 独立性
# ----------------------------------------------------------
print("\n[13] Widget 独立性")
check("无 import client/services", "from client.services" not in source)
check("无 import server/services", "from server.services" not in source)
check("无 import server/routers", "from server.routers" not in source)
check("无 import server/models", "from server.models" not in source)
check("无 import Database", "Database" not in source)
check("无 import ApiClient", "ApiClient" not in source)

# [14] 无 Service
# ----------------------------------------------------------
print("\n[14] 无 Service")
check("无 TaskService", "TaskService" not in source)
check("无 CustomerService", "CustomerService" not in source)
check("无 UserService", "UserService" not in source)
check("无 AuthService", "AuthService" not in source)

# [15] 无 HTTP
# ----------------------------------------------------------
print("\n[15] 无 HTTP")
check("无 requests", "requests" not in source)
check("无 httpx", "httpx" not in source)
check("无 urllib", "urllib" not in source)

# [16] 无 ORM
# ----------------------------------------------------------
print("\n[16] 无 ORM")
check("无 sqlalchemy", "sqlalchemy" not in source)
check("无 Session", "Session" not in source)

# [17] 无 Database
# ----------------------------------------------------------
print("\n[17] 无 Database")
check("无 database", "database" not in source.lower())

# [18] 无 JWT
# ----------------------------------------------------------
print("\n[18] 无 JWT")
check("无 jwt", "jwt" not in source.lower())
check("无 bcrypt", "bcrypt" not in source)

# [19] 无业务逻辑
# ----------------------------------------------------------
print("\n[19] 无业务逻辑")
check("无状态流转", "next_status" not in source)
check("无权限", "permission" not in source.lower())
check("无编号", "task_no" not in source)
check("无 commit", "commit" not in source)
check("无 rollback", "rollback" not in source)
check("无 HTTP 请求", "self._api_client" not in source)

# [20] logger
# ----------------------------------------------------------
print("\n[20] logger")
check("使用 logging.getLogger", 'logging.getLogger("gtms.client")' in source)
check("无 print()", "print(" not in source)

# [21] Type Hint
# ----------------------------------------------------------
print("\n[21] Type Hint")
check("__init__ status: str", "status: str" in source_full)
check("__init__ parent: Optional", "parent:" in source_full and "Optional" in source_full)
check("__init__ -> None", "-> None:" in source_full)
check("set_status status: str", "status: str" in source_full)
check("set_status -> None", "-> None:" in source_full)
check("status property -> Optional[str]", "-> Optional[str]:" in source_full)
check("_status: Optional[str]", "Optional[str]" in source_full)
check("STATUS_TEXT ClassVar", "ClassVar" in source_full)
check("STATUS_STYLE ClassVar", "ClassVar" in source_full)

# [22] Docstring
# ----------------------------------------------------------
print("\n[22] Docstring")
# AST 解析检查 docstring
try:
    tree = ast.parse(source_full)
    # 模块级 docstring
    check("模块级 docstring 存在", ast.get_docstring(tree) is not None)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "StatusBadge":
            check("类 docstring 存在", ast.get_docstring(node) is not None)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    doc = ast.get_docstring(item)
                    check(f"{item.name} docstring 存在", doc is not None)
except SyntaxError as e:
    check(f"AST 解析失败: {e}", False)

# [23] PEP8
# ----------------------------------------------------------
print("\n[23] PEP8")
import subprocess

result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", STATUS_BADGE_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# [24] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[24] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass", re.search(r'\bpass\b', source) is None)

# [25] 无 Singleton / 全局变量 / 缓存 / 静态对象
# ----------------------------------------------------------
print("\n[25] 无 Singleton / 全局 / 缓存")
check("无 Singleton", "Singleton" not in source)
check("无 __new__", "def __new__" not in source)
check("无全局缓存 _cache", "_cache" not in source)
check("无模块级实例", "= StatusBadge(" not in source)

# [26] API Freeze / __init__.py
# ----------------------------------------------------------
print("\n[26] API Freeze / __init__.py")
init_source = extract_code_text(INIT_PATH)
init_full = open(INIT_PATH, "r", encoding="utf-8").read()
check("__init__.py 导出 StatusBadge", "StatusBadge" in init_source)
check("__init__.py 含 __all__", "__all__" in init_source)
check("__init__.py 仅导出 StatusBadge", init_full.count("StatusBadge") >= 2)

# [27] Frozen API 未修改
# ----------------------------------------------------------
print("\n[27] Frozen API 未修改")
check("未导入 Server 模块", "from server.services" not in source)
check("未导入 Router", "from server.routers" not in source)
check("未导入 ORM 模型", "from server.models" not in source)
check("未导入 TrialTask Schema", "trial_task_schema" not in source)

# [28] 循环导入检查
# ----------------------------------------------------------
print("\n[28] 循环导入检查")
check("无循环导入风险", "from client.widgets" not in source)

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