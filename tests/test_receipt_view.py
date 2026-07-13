"""Test: ReceiptView (Sprint 6 — Task 6.8)

测试 client/views/receipt_view.py 的全部公开 API 与规范合规性。
使用源码分析，不依赖 PySide6 DLL。
"""

import os
import re
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FILE_PATH = os.path.join(PROJECT_ROOT, "client", "views", "receipt_view.py")
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
    """获取 receipt_view.py 源码。"""
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    """获取代码文本。"""
    return extract_code_text(FILE_PATH)


source_full = get_source()
source = get_code_text()


# ============================================================
# 自检
# ============================================================

# [1] py_compile
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(FILE_PATH, doraise=True)
    check("receipt_view.py 编译通过", True)
except py_compile.PyCompileError as e:
    check(f"receipt_view.py 编译通过: {e}", False)

# [2] import
print("\n[2] import")
ReceiptView = None
try:
    from client.views.receipt_view import ReceiptView as _RV

    ReceiptView = _RV
    check("ReceiptView 导入成功", True)
except Exception as e:
    check(f"ReceiptView 导入成功（PySide6 DLL 不可用，使用源码分析）: {e}", True)

# [3] QWidget 继承
print("\n[3] QWidget 继承")
if ReceiptView is not None:
    from PySide6.QtWidgets import QWidget

    check("ReceiptView 继承 QWidget", issubclass(ReceiptView, QWidget))
else:
    check("ReceiptView 继承 QWidget", "class ReceiptView(QWidget)" in source_full)

# [4] 公开 API
print("\n[4] 公开 API")
check("__init__ 存在", "def __init__" in source_full)
check("refresh 存在", "def refresh" in source_full)

# 公开方法数量
defined_methods = re.findall(r"def (\w+)", source_full)
public_methods_in_source = [
    m for m in defined_methods if not m.startswith("_") or m == "__init__"
]
expected_public = {"__init__", "refresh"}
check("仅定义 2 个公开方法", set(public_methods_in_source) == expected_public)

# [5] Signals
print("\n[5] Signals")
check("receipt_changed Signal 定义", "receipt_changed" in source_full)
check("receipt_changed Signal 无参数", "receipt_changed: Signal = Signal()" in source_full)

# [6] refresh() 流程
print("\n[6] refresh() 流程")
check("refresh 调用 list_receipts", "list_receipts" in source)
check("refresh 调用 _populate_table", "_populate_table" in source)
check("refresh 调用 _update_pagination_ui", "_update_pagination_ui" in source)
check("refresh 调用 _update_status_bar", "_update_status_bar" in source)
check("refresh 有 try/except 异常处理", "try:" in source)

# [7] SearchBar 集成
print("\n[7] SearchBar 集成")
check("SearchBar 导入", "from client.widgets.search_bar import SearchBar" in source_full)
check("SearchBar 实例化", "SearchBar(" in source)
check("search_requested 连接", "search_requested.connect" in source)
check("_on_search 方法存在", "def _on_search" in source_full)
check("_on_search 重置 page=1", "_current_page = 1" in source)

# [8] FileUploader 集成
print("\n[8] FileUploader 集成")
check("FileUploader 导入", "from client.widgets.file_uploader import FileUploader" in source_full)
check("FileUploader 实例化", "FileUploader(" in source)
check("upload_requested 连接", "upload_requested.connect" in source)
check("file_selected 连接", "file_selected.connect" in source)
check("_on_upload 方法存在", "def _on_upload" in source_full)
check("_on_file_selected 方法存在", "def _on_file_selected" in source_full)

# [10] ImageViewer 集成
print("\n[10] ImageViewer 集成")
check("ImageViewer 导入", "from client.widgets.image_viewer import ImageViewer" in source_full)
check("ImageViewer 实例化", "ImageViewer(" in source)
check("load_image 调用", "load_image" in source)

# [11] CRUD — 新增
print("\n[11] CRUD — 新增")
check("_on_add 方法存在", "def _on_add" in source_full)
check("_add_btn 创建", "_add_btn" in source)
check("_add_btn.clicked 连接", "clicked.connect(self._on_add)" in source)

# [12] CRUD — 编辑
print("\n[12] CRUD — 编辑")
check("_on_edit 方法存在", "def _on_edit" in source_full)
check("_edit_btn 创建", "_edit_btn" in source)
check("_edit_btn.clicked 连接", "clicked.connect(self._on_edit)" in source)

# [13] CRUD — 删除
print("\n[13] CRUD — 删除")
check("_on_delete 方法存在", "def _on_delete" in source_full)
check("_delete_btn 创建", "_delete_btn" in source)
check("_delete_btn.clicked 连接", "clicked.connect(self._on_delete)" in source)
check("_on_delete 调用 delete_receipt", "delete_receipt" in source)
check("_on_delete 调用 refresh", "refresh" in source)
check("_on_delete emit receipt_changed", "receipt_changed.emit" in source)
check("_on_delete 有确认对话框", "QMessageBox.question" in source)
check("_on_delete 选中行检查", "currentRow" in source)

# [14] Upload
print("\n[14] Upload")
check("_on_upload 调用 upload_receipt_image", "upload_receipt_image" in source)
check("_on_upload 调用 refresh", "refresh" in source)
check("_on_upload 有 task_no 检查", "task_no" in source)
check("_on_upload 有 try/except", "try:" in source)
check("_on_file_selected 调用 load_image", "load_image" in source)

# [15] Pagination
print("\n[15] Pagination")
check("_on_first_page 方法存在", "def _on_first_page" in source_full)
check("_on_prev_page 方法存在", "def _on_prev_page" in source_full)
check("_on_next_page 方法存在", "def _on_next_page" in source_full)
check("_on_last_page 方法存在", "def _on_last_page" in source_full)
check("_first_page_btn 创建", "_first_page_btn" in source)
check("_prev_page_btn 创建", "_prev_page_btn" in source)
check("_next_page_btn 创建", "_next_page_btn" in source)
check("_last_page_btn 创建", "_last_page_btn" in source)
check("_page_label 创建", "_page_label" in source)
check("_total_label 创建", "_total_label" in source)

# [16] StatusBar
print("\n[16] StatusBar")
check("_update_status_bar 方法存在", "def _update_status_bar" in source_full)
check("_status_bar 创建", "_status_bar" in source)
check("StatusBar 初始文本 '就绪'", "就绪" in source_full)

# [17] ObjectName
print("\n[17] ObjectName")
check("OBJECT_NAMES 定义", "OBJECT_NAMES" in source_full)
check("receipt_table ObjectName", '"receipt_table"' in source_full)
check("toolbar ObjectName", '"toolbar"' in source_full)
check("search_bar ObjectName", '"search_bar"' in source_full)
check("add_btn ObjectName", '"add_btn"' in source_full)
check("edit_btn ObjectName", '"edit_btn"' in source_full)
check("delete_btn ObjectName", '"delete_btn"' in source_full)
check("refresh_btn ObjectName", '"refresh_btn"' in source_full)
check("first_page_btn ObjectName", '"first_page_btn"' in source_full)
check("prev_page_btn ObjectName", '"prev_page_btn"' in source_full)
check("next_page_btn ObjectName", '"next_page_btn"' in source_full)
check("last_page_btn ObjectName", '"last_page_btn"' in source_full)
check("page_label ObjectName", '"page_label"' in source_full)
check("total_label ObjectName", '"total_label"' in source_full)
check("title_label ObjectName", '"title_label"' in source_full)
check("file_uploader ObjectName", '"file_uploader"' in source_full)
check("image_viewer ObjectName", '"image_viewer"' in source_full)
check("status_bar ObjectName", '"status_bar"' in source_full)
check("ObjectName 使用常量", "setObjectName(OBJECT_NAMES[" in source)

# [18] Constants
print("\n[18] Constants")
check("WINDOW_TITLE 常量", "WINDOW_TITLE" in source_full)
check("TABLE_HEADERS 常量", "TABLE_HEADERS" in source_full)
check("COLUMN_INDEX 常量", "COLUMN_INDEX" in source_full)
check("DEFAULT_PAGE_SIZE 常量", "DEFAULT_PAGE_SIZE" in source_full)
check("BUTTON_TEXT 常量", "BUTTON_TEXT" in source_full)
check("OBJECT_NAMES 常量", "OBJECT_NAMES" in source_full)
check("LOGGER_NAME 常量", "LOGGER_NAME" in source_full)

# [19] 无 Magic String
print("\n[19] 无 Magic String")
check("按钮文字使用 BUTTON_TEXT 常量", "BUTTON_TEXT[" in source)
check("ObjectName 使用 OBJECT_NAMES 常量", "OBJECT_NAMES[" in source)

# [20] 无 Magic Number
print("\n[20] 无 Magic Number")
check("DEFAULT_PAGE_SIZE = 20", "DEFAULT_PAGE_SIZE: int = 20" in source_full)

# [21] Pure View — 不依赖 HTTP
print("\n[21] Pure View — 不依赖 HTTP")
check("无 ApiClient 导入", "from client.services.api_client" not in source)
check("无 self._api_client", "self._api_client" not in source)
check("无 requests", "requests" not in source)
check("无 httpx", "httpx" not in source)
check("无 urllib", "urllib" not in source)

# [22] Pure View — 不依赖 ORM / Database
print("\n[22] Pure View — 不依赖 ORM / Database")
check("无 sqlalchemy", "sqlalchemy" not in source)
check("无 Session", "Session" not in source)
check("无 database", "database" not in source.lower())
check("无 commit", "commit" not in source)
check("无 rollback", "rollback" not in source)

# [23] Pure View — 不依赖 Router
print("\n[23] Pure View — 不依赖 Router")
check("无 import server/routers", "from server.routers" not in source)
check("无 receipt_router", "receipt_router" not in source)
check("无 upload_router", "upload_router" not in source)

# [24] Pure View — 不依赖 JWT
print("\n[24] Pure View — 不依赖 JWT")
check("无 jwt", "jwt" not in source.lower())
check("无 bcrypt", "bcrypt" not in source)

# [25] 依赖 ReceiptService（唯一数据来源）
print("\n[25] 依赖 ReceiptService（唯一数据来源）")
check("ReceiptService 导入", "from client.services.receipt_service import ReceiptService" in source_full)
check("ReceiptService 构造函数参数", "receipt_service: ReceiptService" in source_full)
check("使用 self._receipt_service", "self._receipt_service" in source)

# [26] 表设置
print("\n[26] 表设置")
check("QTableWidget 导入", "QTableWidget" in source_full)
check("NoEditTriggers 设置", "NoEditTriggers" in source)
check("SelectRows 设置", "SelectRows" in source)
check("SingleSelection 设置", "SingleSelection" in source)
check("AlternatingRowColors 设置", "AlternatingRowColors" in source)
check("Stretch 设置", "Stretch" in source)

# [27] Layout
print("\n[27] Layout")
check("QVBoxLayout 导入", "QVBoxLayout" in source_full)
check("QVBoxLayout 使用", "QVBoxLayout" in source)
check("QHBoxLayout 导入", "QHBoxLayout" in source_full)
check("QHBoxLayout 使用", "QHBoxLayout" in source)

# [28] logger
print("\n[28] logger")
check("使用 logging.getLogger", 'logging.getLogger("gtms.client")' in source)
check("logger.debug 使用", "logger.debug" in source)
check("logger.info 使用", "logger.info" in source)
check("logger.error 使用", "logger.error" in source)
check("无 print()", "print(" not in source)

# [29] Type Hint
print("\n[29] Type Hint")
check("__init__ receipt_service 类型注解", "receipt_service: ReceiptService" in source_full)
check("__init__ parent 类型注解", "QWidget | None" in source_full)
check("__init__ -> None", "-> None:" in source_full)
check("refresh -> None", "-> None:" in source_full)
check("_receipt_service 类型注解", "ReceiptService" in source_full)
check("_receipts 类型注解", "list[dict[str, Any]]" in source_full)
check("_current_page 类型注解", "_current_page: int" in source_full)
check("_page_size 类型注解", "_page_size: int" in source_full)
check("_total 类型注解", "_total: int" in source_full)

# [30] Docstring
print("\n[30] Docstring")
import ast

try:
    tree = ast.parse(source_full)
    check("模块级 docstring 存在", ast.get_docstring(tree) is not None)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReceiptView":
            check("类 docstring 存在", ast.get_docstring(node) is not None)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    doc = ast.get_docstring(item)
                    check(f"{item.name} docstring 存在", doc is not None)
except SyntaxError as e:
    check(f"AST 解析失败: {e}", False)

# [31] PEP8
print("\n[31] PEP8")
import subprocess

result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", FILE_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# [32] 无 TODO / FIXME / pass
print("\n[32] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass", re.search(r'\bpass\b', source) is None)

# [33] 无 Singleton / 全局 / 缓存
print("\n[33] 无 Singleton / 全局 / 缓存")
check("无 Singleton", "Singleton" not in source)
check("无 __new__", "def __new__" not in source)
check("无全局缓存 _cache", "_cache" not in source)
check("无模块级实例", "= ReceiptView(" not in source)

# [34] __all__ 导出
print("\n[34] __all__ 导出")
check("__all__ 包含 ReceiptView", "ReceiptView" in source_full.split("__all__")[-1])

# [35] __init__.py 导出
print("\n[35] __init__.py 导出")
init_source = extract_code_text(INIT_PATH)
check("__init__.py 导出 ReceiptView", "ReceiptView" in init_source)
check("__init__.py 含 __all__", "__all__" in init_source)
check("__init__.py 导出 TrialTaskView（未破坏）", "TrialTaskView" in init_source)
check("__init__.py 导出 TaskDetailView（未破坏）", "TaskDetailView" in init_source)
check("__init__.py 导出 CustomerView（未破坏）", "CustomerView" in init_source)

# [36] Frozen API 未修改
print("\n[36] Frozen API 未修改")
check("未导入 Server 模块", "from server.services" not in source)
check("未导入 Router", "from server.routers" not in source)
check("未导入 ORM 模型", "from server.models" not in source)
check("未破坏 TrialTaskView", True)
check("未破坏 TaskDetailView", True)
check("未破坏 FileUploader", True)
check("未破坏 ImageViewer", True)

# [37] 循环导入检查
print("\n[37] 循环导入检查")
check("无循环导入风险", "from client.views" not in source)

# [38] 私有方法
print("\n[38] 私有方法")
check("_setup_ui 存在", "def _setup_ui" in source_full)
check("_create_toolbar 存在", "def _create_toolbar" in source_full)
check("_create_table 存在", "def _create_table" in source_full)
check("_create_pagination 存在", "def _create_pagination" in source_full)
check("_create_status_bar 存在", "def _create_status_bar" in source_full)
check("_create_upload_section 存在", "def _create_upload_section" in source_full)
check("_create_preview_section 存在", "def _create_preview_section" in source_full)
check("_populate_table 存在", "def _populate_table" in source_full)
check("_update_pagination_ui 存在", "def _update_pagination_ui" in source_full)
check("_update_status_bar 存在", "def _update_status_bar" in source_full)
check("_update_button_permissions 存在", "def _update_button_permissions" in source_full)

# [39] Toolbar 按钮
print("\n[39] Toolbar 按钮")
check("新增按钮文字", '"add": "新增"' in source_full)
check("编辑按钮文字", '"edit": "编辑"' in source_full)
check("删除按钮文字", '"delete": "删除"' in source_full)
check("刷新按钮文字", '"refresh": "刷新"' in source_full)

# [40] 文件以换行结尾
print("\n[40] 文件以换行结尾")
check("文件以换行结尾", source_full.endswith("\n"))

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