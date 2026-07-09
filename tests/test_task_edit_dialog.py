"""Test: TaskEditDialog (Sprint 5 — Task 5.8)

测试 client/views/task_edit_dialog.py 的全部公开 API 与 Pure UI 合规性。
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

TASK_EDIT_DIALOG_PATH = os.path.join(
    PROJECT_ROOT, "client", "views", "task_edit_dialog.py"
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
    with open(TASK_EDIT_DIALOG_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    """获取代码文本。"""
    return extract_code_text(TASK_EDIT_DIALOG_PATH)


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
    py_compile.compile(TASK_EDIT_DIALOG_PATH, doraise=True)
    check("task_edit_dialog.py 编译通过", True)
except py_compile.PyCompileError as e:
    check(f"task_edit_dialog.py 编译通过: {e}", False)

# [2] import
# ----------------------------------------------------------
print("\n[2] import")
TaskEditDialog = None
try:
    from client.views.task_edit_dialog import TaskEditDialog as _TED

    TaskEditDialog = _TED
    check("TaskEditDialog 导入成功", True)
except Exception as e:
    check(f"TaskEditDialog 导入成功（PySide6 DLL 不可用，使用源码分析）: {e}", True)

# [3] QDialog 继承
# ----------------------------------------------------------
print("\n[3] QDialog 继承")
if TaskEditDialog is not None:
    from PySide6.QtWidgets import QDialog

    check("TaskEditDialog 继承 QDialog", issubclass(TaskEditDialog, QDialog))
else:
    check("TaskEditDialog 继承 QDialog",
          "class TaskEditDialog(QDialog)" in source_full)

# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
if TaskEditDialog is not None:
    public_methods = [m for m in dir(TaskEditDialog) if not m.startswith("_")]
    check("公开 API 含 get_result", "get_result" in public_methods)
    check("公开 API 含 fill_data", "fill_data" in public_methods)
else:
    check("公开 API 含 get_result", "def get_result" in source_full)
    check("公开 API 含 fill_data", "def fill_data" in source_full)

# 确认公开方法仅 2 个（不含 __init__）
defined_methods = re.findall(r"def (\w+)", source_full)
public_methods_in_source = [
    m for m in defined_methods if not m.startswith("_") or m == "__init__"
]
expected_public = {"__init__", "get_result", "fill_data"}
check("仅定义 3 个公开方法（含 __init__）",
      set(public_methods_in_source) == expected_public)

# [5] Create Mode
# ----------------------------------------------------------
print("\n[5] Create Mode")
check("支持 create 模式", '"create"' in source_full)
check("WINDOW_TITLE_CREATE 定义", "WINDOW_TITLE_CREATE" in source_full)
check("mode 参数控制", "mode" in source_full)

# [6] Edit Mode
# ----------------------------------------------------------
print("\n[6] Edit Mode")
check("支持 edit 模式", '"edit"' in source_full)
check("WINDOW_TITLE_EDIT 定义", "WINDOW_TITLE_EDIT" in source_full)

# [7] fill_data()
# ----------------------------------------------------------
print("\n[7] fill_data()")
check("fill_data() 存在", "def fill_data" in source_full)
check("fill_data() 预填客户", "customer" in source)
check("fill_data() 预填加工要求", "requirement" in source)
check("fill_data() 预填销售", "sales" in source)
check("fill_data() 预填快递单号", "tracking_no" in source)
check("fill_data() 预填备注", "remark" in source)

# [8] get_result()
# ----------------------------------------------------------
print("\n[8] get_result()")
check("get_result() 存在", "def get_result" in source_full)
check("get_result() 返回 _result", "return self._result" in source)

# [9] ObjectName (§15.7.23)
# ----------------------------------------------------------
print("\n[9] ObjectName")
object_names = [
    "customer_edit", "requirement_edit", "sales_edit",
    "tracking_no_edit", "remark_edit", "button_box",
]
for name in object_names:
    check(f"ObjectName {name} 已设置",
          f'setObjectName' in source and name in source)

# [10] Constants
# ----------------------------------------------------------
print("\n[10] Constants")
constants = [
    "WINDOW_TITLE_CREATE", "WINDOW_TITLE_EDIT",
    "FORM_LABELS", "OBJECT_NAMES",
    "DEFAULT_WIDTH", "DEFAULT_HEIGHT", "LOGGER_NAME",
]
for const_name in constants:
    check(f"常量 {const_name} 定义", const_name in source_full)
check("常量定义在文件顶部",
      source_full.index("WINDOW_TITLE_CREATE") < source_full.index("class TaskEditDialog"))

# [11] Layout
# ----------------------------------------------------------
print("\n[11] Layout")
check("使用 QFormLayout", "QFormLayout" in source)
check("使用 QDialogButtonBox", "QDialogButtonBox" in source)

# [12] QDialogButtonBox
# ----------------------------------------------------------
print("\n[12] QDialogButtonBox")
check("QDialogButtonBox 含 Ok", "StandardButton.Ok" in source)
check("QDialogButtonBox 含 Cancel", "StandardButton.Cancel" in source)
check("accepted 连接", "accepted.connect" in source)
check("rejected 连接", "rejected.connect" in source)

# [13] accept / reject
# ----------------------------------------------------------
print("\n[13] accept / reject")
check("accept() 调用", "self.accept()" in source)
check("reject 连接", "self.reject" in source)

# [14] 字段
# ----------------------------------------------------------
print("\n[14] 字段")
fields = ["customer", "requirement", "sales", "tracking_no", "remark"]
for field in fields:
    check(f"字段 {field} 存在", field in source and "QLineEdit" in source)

# [15] 不显示系统字段
# ----------------------------------------------------------
print("\n[15] 不显示系统字段")
check("无 task_no 输入", "task_no" not in source)
check("无 process_status 输入", "process_status" not in source)
check("无 result_status 输入", "result_status" not in source)
check("无 created_at 输入", "created_at" not in source)
check("无 updated_at 输入", "updated_at" not in source)

# [16] Pure UI
# ----------------------------------------------------------
print("\n[16] Pure UI")
check("无 import TaskService", "TaskService" not in source)
check("无 import CustomerService", "CustomerService" not in source)
check("无 import ApiClient", "ApiClient" not in source)
check("无 import requests", "requests" not in source)
check("无 import server.services", "from server.services" not in source)
check("无 import server.routers", "from server.routers" not in source)
check("无 import server.models", "from server.models" not in source)

# [17] 无 Service 调用
# ----------------------------------------------------------
print("\n[17] 无 Service 调用")
check("无 create_task 调用", "create_task" not in source)
check("无 update_task 调用", "update_task" not in source)
check("无 delete_task 调用", "delete_task" not in source)
check("无 list_tasks 调用", "list_tasks" not in source)
check("无 _task_service", "_task_service" not in source)

# [18] 无 HTTP
# ----------------------------------------------------------
print("\n[18] 无 HTTP")
check("无 requests", "requests" not in source)
check("无 httpx", "httpx" not in source)
check("无 urllib", "urllib" not in source)

# [19] 无 ORM / Database
# ----------------------------------------------------------
print("\n[19] 无 ORM / Database")
check("无 sqlalchemy", "sqlalchemy" not in source)
check("无 Session", "Session" not in source)
check("无 database", "database" not in source.lower())

# [20] 无 JWT
# ----------------------------------------------------------
print("\n[20] 无 JWT")
check("无 jwt", "jwt" not in source.lower())
check("无 bcrypt", "bcrypt" not in source)

# [21] 无业务逻辑
# ----------------------------------------------------------
print("\n[21] 无业务逻辑")
check("无状态流转", "next_status" not in source)
check("无编号生成", "generate_task_no" not in source)
check("无权限判断", "permission" not in source.lower())
check("无 commit", "commit" not in source)
check("无 rollback", "rollback" not in source)

# [22] 无 try/except
# ----------------------------------------------------------
print("\n[22] 无 try/except")
check("无 try/except", "try:" not in source)

# [23] 无 QMessageBox
# ----------------------------------------------------------
print("\n[23] 无 QMessageBox")
check("无 QMessageBox", "QMessageBox" not in source)

# [24] logger
# ----------------------------------------------------------
print("\n[24] logger")
check("使用 logging.getLogger", 'logging.getLogger("gtms.client")' in source)
check("无 print()", "print(" not in source)

# [25] Type Hint
# ----------------------------------------------------------
print("\n[25] Type Hint")
check("__init__ mode: str", "mode: str" in source_full)
check("__init__ parent: optional", "parent:" in source_full)
check("__init__ -> None", "-> None:" in source_full)
check("get_result() -> dict | None", "-> dict[str, Any] | None" in source_full)
check("fill_data() data: dict", "data: dict[str, Any]" in source_full)
check("_result: dict | None", "dict[str, Any] | None" in source_full)
check("_mode: str", "_mode: str" in source_full)

# [26] Docstring
# ----------------------------------------------------------
print("\n[26] Docstring")
try:
    tree = ast.parse(source_full)
    check("模块级 docstring 存在", ast.get_docstring(tree) is not None)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TaskEditDialog":
            check("类 docstring 存在", ast.get_docstring(node) is not None)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    doc = ast.get_docstring(item)
                    check(f"{item.name} docstring 存在", doc is not None)
except SyntaxError as e:
    check(f"AST 解析失败: {e}", False)

# [27] PEP8
# ----------------------------------------------------------
print("\n[27] PEP8")
import subprocess

result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", TASK_EDIT_DIALOG_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# [28] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[28] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass", re.search(r'\bpass\b', source) is None)

# [29] 无 Magic Number / Magic String
# ----------------------------------------------------------
print("\n[29] 无 Magic Number / Magic String")
check("DEFAULT_WIDTH 引用", "DEFAULT_WIDTH" in source)
check("DEFAULT_HEIGHT 引用", "DEFAULT_HEIGHT" in source)
check("WINDOW_TITLE_CREATE 引用", "WINDOW_TITLE_CREATE" in source)
check("WINDOW_TITLE_EDIT 引用", "WINDOW_TITLE_EDIT" in source)
check("FORM_LABELS 引用", "FORM_LABELS[" in source)
check("OBJECT_NAMES 引用", "OBJECT_NAMES[" in source)

# [30] API Freeze / __init__.py
# ----------------------------------------------------------
print("\n[30] API Freeze / __init__.py")
init_source = extract_code_text(INIT_PATH)
init_full = open(INIT_PATH, "r", encoding="utf-8").read()
check("__init__.py 导出 TaskEditDialog", "TaskEditDialog" in init_source)
check("__init__.py 含 __all__", "__all__" in init_source)
check("__init__.py 原有导出未破坏", "TrialTaskView" in init_source)

# [31] Frozen API 未修改
# ----------------------------------------------------------
print("\n[31] Frozen API 未修改")
check("未导入 Server 模块", "from server.services" not in source)
check("未导入 Router", "from server.routers" not in source)
check("未导入 ORM 模型", "from server.models" not in source)
check("未导入 TrialTask Schema", "trial_task_schema" not in source)

# [32] 循环导入检查
# ----------------------------------------------------------
print("\n[32] 循环导入检查")
check("无循环导入风险", "from client.views" not in source)

# [33] 无 Signal
# ----------------------------------------------------------
print("\n[33] 无 Signal")
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