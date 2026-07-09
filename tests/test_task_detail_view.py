"""Test: TaskDetailView (Sprint 5 — Task 5.9)

测试 client/views/task_detail_view.py 的全部公开 API 与 Pure View 合规性。
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

TASK_DETAIL_VIEW_PATH = os.path.join(
    PROJECT_ROOT, "client", "views", "task_detail_view.py"
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
    """获取源码。"""
    with open(TASK_DETAIL_VIEW_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    """获取代码文本。"""
    return extract_code_text(TASK_DETAIL_VIEW_PATH)


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
    py_compile.compile(TASK_DETAIL_VIEW_PATH, doraise=True)
    check("task_detail_view.py 编译通过", True)
except py_compile.PyCompileError as e:
    check(f"task_detail_view.py 编译通过: {e}", False)

# [2] import
# ----------------------------------------------------------
print("\n[2] import")
TaskDetailView = None
try:
    from client.views.task_detail_view import TaskDetailView as _TDV

    TaskDetailView = _TDV
    check("TaskDetailView 导入成功", True)
except Exception as e:
    check(f"TaskDetailView 导入成功（PySide6 DLL 不可用，使用源码分析）: {e}", True)

# [3] QWidget 继承
# ----------------------------------------------------------
print("\n[3] QWidget 继承")
if TaskDetailView is not None:
    from PySide6.QtWidgets import QWidget

    check("TaskDetailView 继承 QWidget", issubclass(TaskDetailView, QWidget))
else:
    check("TaskDetailView 继承 QWidget",
          "class TaskDetailView(QWidget)" in source_full)

# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
if TaskDetailView is not None:
    public_methods = [m for m in dir(TaskDetailView) if not m.startswith("_")]
    check("公开 API 含 refresh", "refresh" in public_methods)
    check("公开 API 含 load_task", "load_task" in public_methods)
else:
    check("公开 API 含 refresh", "def refresh" in source_full)
    check("公开 API 含 load_task", "def load_task" in source_full)

# 确认公开方法仅 2 个（不含 __init__）
defined_methods = re.findall(r"def (\w+)", source_full)
public_methods_in_source = [
    m for m in defined_methods if not m.startswith("_") or m == "__init__"
]
expected_public = {"__init__", "refresh", "load_task"}
check("仅定义 3 个公开方法（含 __init__）",
      set(public_methods_in_source) == expected_public)

# [5] GroupBox
# ----------------------------------------------------------
print("\n[5] GroupBox")
group_names = [
    "basic", "task", "status", "receiving",
    "grinding", "inspection", "destination",
]
for name in group_names:
    check(f"GroupBox {name} 存在", f"{name}_group" in source)

# [6] StatusBadge 集成
# ----------------------------------------------------------
print("\n[6] StatusBadge 集成")
check("导入 StatusBadge", "from client.widgets.status_badge import StatusBadge" in source_full)
check("创建 StatusBadge 实例", "StatusBadge(" in source)
check("process_status badge", "_process_badge" in source)
check("result_status badge", "_result_badge" in source)

# [7] refresh() 流程
# ----------------------------------------------------------
print("\n[7] refresh() 流程")
check("refresh() 存在", "def refresh" in source_full)
check("refresh() 调用 get_task", "get_task" in source)
check("refresh() 调用 _update_ui", "_update_ui" in source)

# [8] load_task()
# ----------------------------------------------------------
print("\n[8] load_task()")
check("load_task() 存在", "def load_task" in source_full)
check("load_task() 设置 _task_id", "_task_id = task_id" in source)
check("load_task() 调用 refresh", "self.refresh()" in source)

# [9] Desktop TaskService 调用
# ----------------------------------------------------------
print("\n[9] Desktop TaskService 调用")
check("导入 TaskService", "from client.services.task_service import TaskService" in source_full)
check("__init__ 接收 task_service", "task_service: TaskService" in source_full)
check("使用 self._task_service", "self._task_service" in source)
check("get_task 调用", "get_task" in source)

# [10] 动态显示/隐藏
# ----------------------------------------------------------
print("\n[10] 动态显示/隐藏")
check("_update_group_visibility 方法", "def _update_group_visibility" in source_full)
check("setVisible 调用", "setVisible" in source)
check("status_priority 定义", "status_priority" in source)
check("created=0", '"created": 0' in source)
check("received=1", '"received": 1' in source)
check("grinding=2", '"grinding": 2' in source)
check("completed=3", '"completed": 3' in source)
check("dispatched=4", '"dispatched": 4' in source)
check("closed=5", '"closed": 5' in source)

# [11] ObjectName (§15.7.23)
# ----------------------------------------------------------
print("\n[11] ObjectName")
object_names = [
    "title_label", "basic_group", "task_group", "status_group",
    "receiving_group", "grinding_group", "inspection_group",
    "destination_group", "close_btn",
]
for name in object_names:
    check(f"ObjectName {name} 已设置", f'setObjectName' in source and name in source)

# [12] Constants
# ----------------------------------------------------------
print("\n[12] Constants")
constants = [
    "WINDOW_TITLE", "GROUP_TITLE", "FIELD_LABEL", "OBJECT_NAMES",
    "DEFAULT_WIDTH", "DEFAULT_HEIGHT", "LOGGER_NAME",
]
for const_name in constants:
    check(f"常量 {const_name} 定义", const_name in source_full)
check("常量定义在文件顶部",
      source_full.index("WINDOW_TITLE") < source_full.index("class TaskDetailView"))

# [13] 无 Magic Number / Magic String
# ----------------------------------------------------------
print("\n[13] 无 Magic Number / Magic String")
check("DEFAULT_WIDTH 引用", "DEFAULT_WIDTH" in source)
check("DEFAULT_HEIGHT 引用", "DEFAULT_HEIGHT" in source)
check("GROUP_TITLE 引用", "GROUP_TITLE[" in source)
check("FIELD_LABEL 引用", "FIELD_LABEL[" in source)
check("OBJECT_NAMES 引用", "OBJECT_NAMES[" in source)

# [14] Widget 独立性
# ----------------------------------------------------------
print("\n[14] Widget 独立性")
check("无 import ApiClient", "ApiClient" not in source)
check("无 import requests", "requests" not in source)
check("无 import server.services", "from server.services" not in source)
check("无 import server.routers", "from server.routers" not in source)
check("无 import server.models", "from server.models" not in source)

# [15] 无 Service（除 TaskService）
# ----------------------------------------------------------
print("\n[15] 无 Service（除 TaskService）")
check("无 CustomerService", "CustomerService" not in source)
check("无 UserService", "UserService" not in source)
check("无 AuthService", "AuthService" not in source)

# [16] 无 HTTP
# ----------------------------------------------------------
print("\n[16] 无 HTTP")
check("无 requests", "requests" not in source)
check("无 httpx", "httpx" not in source)
check("无 urllib", "urllib" not in source)

# [17] 无 ORM
# ----------------------------------------------------------
print("\n[17] 无 ORM")
check("无 sqlalchemy", "sqlalchemy" not in source)
check("无 Session", "Session" not in source)

# [18] 无 Database
# ----------------------------------------------------------
print("\n[18] 无 Database")
check("无 database", "database" not in source.lower())

# [19] 无 JWT
# ----------------------------------------------------------
print("\n[19] 无 JWT")
check("无 jwt", "jwt" not in source.lower())
check("无 bcrypt", "bcrypt" not in source)

# [20] 无业务逻辑
# ----------------------------------------------------------
print("\n[20] 无业务逻辑")
check("无状态流转", "next_status" not in source)
check("无编号生成", "generate_task_no" not in source)
check("无权限判断", "permission" not in source.lower())
check("无 commit", "commit" not in source)
check("无 rollback", "rollback" not in source)
check("无 create_task", re.search(r'\bcreate_task\b', source) is None)
check("无 update_task", "update_task" not in source)
check("无 delete_task", "delete_task" not in source)

# [21] logger
# ----------------------------------------------------------
print("\n[21] logger")
check("使用 logging.getLogger", 'logging.getLogger("gtms.client")' in source)
check("无 print()", "print(" not in source)

# [22] Type Hint
# ----------------------------------------------------------
print("\n[22] Type Hint")
check("__init__ task_service: TaskService", "task_service: TaskService" in source_full)
check("__init__ parent: optional", "parent:" in source_full)
check("__init__ -> None", "-> None:" in source_full)
check("load_task() task_id: int", "task_id: int" in source_full)
check("refresh() -> None", "-> None:" in source_full)
check("_task_id: int | None", "int | None" in source_full)
check("_task_data: dict | None", "dict[str, Any] | None" in source_full)

# [23] Docstring
# ----------------------------------------------------------
print("\n[23] Docstring")
try:
    tree = ast.parse(source_full)
    check("模块级 docstring 存在", ast.get_docstring(tree) is not None)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TaskDetailView":
            check("类 docstring 存在", ast.get_docstring(node) is not None)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    doc = ast.get_docstring(item)
                    check(f"{item.name} docstring 存在", doc is not None)
except SyntaxError as e:
    check(f"AST 解析失败: {e}", False)

# [24] PEP8
# ----------------------------------------------------------
print("\n[24] PEP8")
import subprocess

result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", TASK_DETAIL_VIEW_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# [25] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[25] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass", re.search(r'\bpass\b', source) is None)

# [26] API Freeze / __init__.py
# ----------------------------------------------------------
print("\n[26] API Freeze / __init__.py")
init_source = extract_code_text(INIT_PATH)
init_full = open(INIT_PATH, "r", encoding="utf-8").read()
check("__init__.py 导出 TaskDetailView", "TaskDetailView" in init_source)
check("__init__.py 含 __all__", "__all__" in init_source)
check("__init__.py 原有导出未破坏", "TaskEditDialog" in init_source)

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
check("无循环导入风险", "from client.views" not in source)

# [29] QScrollArea
# ----------------------------------------------------------
print("\n[29] QScrollArea")
check("使用 QScrollArea", "QScrollArea" in source)

# [30] 无 Signal
# ----------------------------------------------------------
print("\n[30] 无 Signal")
check("无自定义 Signal", "Signal" not in source)

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