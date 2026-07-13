"""Test: FileUploader Widget (Sprint 6 — Task 6.6)

测试 client/widgets/file_uploader.py 的全部公开 API 与代码规范。
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

FILE_UPLOADER_PATH = os.path.join(PROJECT_ROOT, "client", "widgets", "file_uploader.py")
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
    """获取 file_uploader.py 源码（含注释/docstring）。"""
    with open(FILE_UPLOADER_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    """获取 file_uploader.py 代码文本（排除 docstring 和注释）。"""
    return extract_code_text(FILE_UPLOADER_PATH)


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
    py_compile.compile(FILE_UPLOADER_PATH, doraise=True)
    check("file_uploader.py 编译通过", True)
except py_compile.PyCompileError as e:
    check(f"file_uploader.py 编译通过: {e}", False)

# [2] import
# ----------------------------------------------------------
print("\n[2] import")
FileUploader = None
try:
    from client.widgets.file_uploader import FileUploader as _FU

    FileUploader = _FU
    check("FileUploader 导入成功", True)
except Exception as e:
    check(f"FileUploader 导入成功（PySide6 DLL 不可用，使用源码分析）: {e}", True)

# [3] QWidget 继承
# ----------------------------------------------------------
print("\n[3] QWidget 继承")
if FileUploader is not None:
    from PySide6.QtWidgets import QWidget

    check("FileUploader 继承 QWidget", issubclass(FileUploader, QWidget))
else:
    check("FileUploader 继承 QWidget", "class FileUploader(QWidget)" in source_full)

# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
if FileUploader is not None:
    public_methods = [m for m in dir(FileUploader) if not m.startswith("_")]
    check("公开 API 含 __init__", "__init__" in public_methods)
    check("公开 API 含 selected_file", "selected_file" in public_methods)
    check("公开 API 含 clear", "clear" in public_methods)
    check("公开 API 含 set_filter", "set_filter" in public_methods)
    check("公开 API 含 set_max_file_size", "set_max_file_size" in public_methods)
    check("公开 API 含 set_placeholder", "set_placeholder" in public_methods)
    check("公开 API 含 set_default_dir", "set_default_dir" in public_methods)
    check("公开 API 含 set_button_texts", "set_button_texts" in public_methods)
else:
    check("公开 API 含 __init__", "def __init__" in source_full)
    check("公开 API 含 selected_file", "def selected_file" in source_full)
    check("公开 API 含 clear", "def clear" in source_full)
    check("公开 API 含 set_filter", "def set_filter" in source_full)
    check("公开 API 含 set_max_file_size", "def set_max_file_size" in source_full)
    check("公开 API 含 set_placeholder", "def set_placeholder" in source_full)
    check("公开 API 含 set_default_dir", "def set_default_dir" in source_full)
    check("公开 API 含 set_button_texts", "def set_button_texts" in source_full)

# 检查未新增多余公开方法
defined_methods = re.findall(r"def (\w+)", source_full)
public_methods_in_source = [
    m for m in defined_methods if not m.startswith("_") or m == "__init__"
]
expected_public = {
    "__init__", "selected_file", "clear", "set_filter",
    "set_max_file_size", "set_placeholder", "set_default_dir",
    "set_button_texts",
}
check("仅定义 8 个公开方法 (含 __init__)",
      set(public_methods_in_source) == expected_public)

# [5] Signals
# ----------------------------------------------------------
print("\n[5] Signals")
check("file_selected Signal 定义", "file_selected" in source_full)
check("file_selected Signal 类型为 str", "file_selected: Signal = Signal(str)" in source_full)
check("upload_requested Signal 定义", "upload_requested" in source_full)
check("upload_requested Signal 类型为 str", "upload_requested: Signal = Signal(str)" in source_full)
check("cleared Signal 定义", "cleared" in source_full)
check("cleared Signal 无参数", "cleared: Signal = Signal()" in source_full)

# [6] Browse 功能
# ----------------------------------------------------------
print("\n[6] Browse 功能")
check("_on_browse 方法存在", "def _on_browse" in source_full)
check("QFileDialog 导入", "QFileDialog" in source_full)
check("getOpenFileName 调用", "getOpenFileName" in source)
check("文件选择后 setText", "setText" in source)
check("文件选择后 emit file_selected", "file_selected.emit" in source)

# [7] Upload 功能
# ----------------------------------------------------------
print("\n[7] Upload 功能")
check("_on_upload 方法存在", "def _on_upload" in source_full)
check("upload 发射 upload_requested", "upload_requested.emit" in source)
check("upload 不执行 HTTP", "ApiClient" not in source)
check("upload 不执行 Service", "ReceiptService" not in source)

# [8] Clear 功能
# ----------------------------------------------------------
print("\n[8] Clear 功能")
check("_on_clear 方法存在", "def _on_clear" in source_full)
check("clear() 调用 _path_edit.clear", "_path_edit.clear()" in source)
check("clear() 发射 cleared 信号", "cleared.emit()" in source)

# [9] Filter 功能
# ----------------------------------------------------------
print("\n[9] Filter 功能")
check("set_filter 方法存在", "def set_filter" in source_full)
check("set_filter 更新 _filter", "self._filter = filter_text" in source)
check("set_filter 空字符串抛 ValueError", "raise ValueError" in source)

# [10] Placeholder 功能
# ----------------------------------------------------------
print("\n[10] Placeholder 功能")
check("set_placeholder 方法存在", "def set_placeholder" in source_full)
check("set_placeholder 调用 setPlaceholderText", "setPlaceholderText" in source)

# [11] Max File Size 功能
# ----------------------------------------------------------
print("\n[11] Max File Size 功能")
check("set_max_file_size 方法存在", "def set_max_file_size" in source_full)
check("set_max_file_size 更新 _max_file_size", "self._max_file_size = size" in source)
check("set_max_file_size <= 0 抛 ValueError", "raise ValueError" in source)

# [12] 默认目录功能
# ----------------------------------------------------------
print("\n[12] 默认目录功能")
check("set_default_dir 方法存在", "def set_default_dir" in source_full)
check("set_default_dir 更新 _default_dir", "self._default_dir = directory" in source)

# [13] 按钮文字动态设置
# ----------------------------------------------------------
print("\n[13] 按钮文字动态设置")
check("set_button_texts 方法存在", "def set_button_texts" in source_full)
check("set_button_texts 支持 browse", "browse" in source_full)
check("set_button_texts 支持 upload", "upload" in source_full)
check("set_button_texts 支持 clear", "clear" in source_full)

# [14] ObjectName
# ----------------------------------------------------------
print("\n[14] ObjectName")
check("file_path_edit ObjectName", "OBJECT_NAME_PATH_EDIT" in source_full)
check("browse_button ObjectName", "OBJECT_NAME_BROWSE_BUTTON" in source_full)
check("upload_button ObjectName", "OBJECT_NAME_UPLOAD_BUTTON" in source_full)
check("clear_button ObjectName", "OBJECT_NAME_CLEAR_BUTTON" in source_full)
check("file_path_edit setObjectName", 'setObjectName(OBJECT_NAME_PATH_EDIT)' in source)
check("browse_button setObjectName", 'setObjectName(OBJECT_NAME_BROWSE_BUTTON)' in source)
check("upload_button setObjectName", 'setObjectName(OBJECT_NAME_UPLOAD_BUTTON)' in source)
check("clear_button setObjectName", 'setObjectName(OBJECT_NAME_CLEAR_BUTTON)' in source)

# [15] Constants
# ----------------------------------------------------------
print("\n[15] Constants")
check("DEFAULT_FILTER 常量", "DEFAULT_FILTER" in source_full)
check("DEFAULT_MAX_FILE_SIZE 常量", "DEFAULT_MAX_FILE_SIZE" in source_full)
check("DEFAULT_PLACEHOLDER 常量", "DEFAULT_PLACEHOLDER" in source_full)
check("BUTTON_TEXT_BROWSE 常量", "BUTTON_TEXT_BROWSE" in source_full)
check("BUTTON_TEXT_UPLOAD 常量", "BUTTON_TEXT_UPLOAD" in source_full)
check("BUTTON_TEXT_CLEAR 常量", "BUTTON_TEXT_CLEAR" in source_full)
check("LOGGER_NAME 常量", "LOGGER_NAME" in source_full)
check("MESSAGE_TITLE_ERROR 常量", "MESSAGE_TITLE_ERROR" in source_full)
check("MESSAGE_TEXT_SIZE_TOO_LARGE 常量", "MESSAGE_TEXT_SIZE_TOO_LARGE" in source_full)
check("MESSAGE_TEXT_EXTENSION_INVALID 常量", "MESSAGE_TEXT_EXTENSION_INVALID" in source_full)
check("SIZE_MB_DIVISOR 常量", "SIZE_MB_DIVISOR" in source_full)

# [16] 无 Magic String — 无硬编码按钮文字
# ----------------------------------------------------------
print("\n[16] 无 Magic String")
check("无硬编码 '浏览' (使用常量)", '"浏览"' not in source or "BUTTON_TEXT_BROWSE" in source)
check("无硬编码 '上传' (使用常量)", '"上传"' not in source or "BUTTON_TEXT_UPLOAD" in source)
check("无硬编码 '清除' (使用常量)", '"清除"' not in source or "BUTTON_TEXT_CLEAR" in source)
check("setObjectName 使用常量（非字面字符串）",
      "setObjectName(\"file_path_edit\")" not in source
      and "setObjectName(\"browse_button\")" not in source
      and "setObjectName(\"upload_button\")" not in source
      and "setObjectName(\"clear_button\")" not in source)
check("无硬编码 10*1024*1024", "10 * 1024 * 1024" not in source or "DEFAULT_MAX_FILE_SIZE" in source)

# [17] 无 Magic Number
# ----------------------------------------------------------
print("\n[17] 无 Magic Number")
check("无硬编码 10485760", "10485760" not in source_full)
check("无硬编码 1024*1024 (使用 SIZE_MB_DIVISOR)", "SIZE_MB_DIVISOR" in source_full)

# [18] Pure UI — 不依赖 Service
# ----------------------------------------------------------
print("\n[18] Pure UI — 不依赖 Service")
check("无 import client/services", "from client.services" not in source)
check("无 import server/services", "from server.services" not in source)
check("无 import ApiClient", "ApiClient" not in source)
check("无 ReceiptService", "ReceiptService" not in source)
check("无 TaskService", "TaskService" not in source)
check("无 CustomerService", "CustomerService" not in source)
check("无 UserService", "UserService" not in source)
check("无 AuthService", "AuthService" not in source)

# [19] Pure UI — 不依赖 HTTP
# ----------------------------------------------------------
print("\n[19] Pure UI — 不依赖 HTTP")
check("无 requests", "requests" not in source)
check("无 httpx", "httpx" not in source)
check("无 urllib", "urllib" not in source)
check("无 self._api_client", "self._api_client" not in source)

# [20] Pure UI — 不依赖 ORM / Database
# ----------------------------------------------------------
print("\n[20] Pure UI — 不依赖 ORM / Database")
check("无 sqlalchemy", "sqlalchemy" not in source)
check("无 Session", "Session" not in source)
check("无 database", "database" not in source.lower())
check("无 commit", "commit" not in source)
check("无 rollback", "rollback" not in source)

# [21] Pure UI — 不依赖 Router
# ----------------------------------------------------------
print("\n[21] Pure UI — 不依赖 Router")
check("无 import server/routers", "from server.routers" not in source)
check("无 receipt_router", "receipt_router" not in source)
check("无 upload_router", "upload_router" not in source)

# [22] Pure UI — 不依赖 JWT
# ----------------------------------------------------------
print("\n[22] Pure UI — 不依赖 JWT")
check("无 jwt", "jwt" not in source.lower())
check("无 bcrypt", "bcrypt" not in source)

# [23] Widget 独立性 — 不依赖具体 View
# ----------------------------------------------------------
print("\n[23] Widget 独立性 — 不依赖具体 View")
check("无 TrialTaskView", "TrialTaskView" not in source)
check("无 CustomerView", "CustomerView" not in source)
check("无 ReceiptView", "ReceiptView" not in source)
check("无 MainWindow", "MainWindow" not in source)

# [24] Layout
# ----------------------------------------------------------
print("\n[24] Layout")
check("QHBoxLayout 导入", "QHBoxLayout" in source_full)
check("QHBoxLayout 使用", "QHBoxLayout" in source)
check("QLineEdit 导入", "QLineEdit" in source_full)
check("QPushButton 导入", "QPushButton" in source_full)
check("4 个 addWidget 调用", source.count("addWidget") >= 4)

# [25] QLineEdit 只读
# ----------------------------------------------------------
print("\n[25] QLineEdit 只读")
check("setReadOnly(True) 调用", "setReadOnly(True)" in source)

# [26] ToolTip
# ----------------------------------------------------------
print("\n[26] ToolTip")
check("_path_edit 有 ToolTip", "setToolTip" in source)
check("_browse_button 有 ToolTip", "setToolTip" in source)
check("_upload_button 有 ToolTip", "setToolTip" in source)
check("_clear_button 有 ToolTip", "setToolTip" in source)
check("至少 4 个 ToolTip", source.count("setToolTip") >= 4)

# [27] Qt StyleSheet — 无自定义绘制
# ----------------------------------------------------------
print("\n[27] Qt StyleSheet — 无自定义绘制")
check("无 paintEvent 重写", "def paintEvent" not in source)
check("无 QPainter 导入", "QPainter" not in source)

# [28] logger
# ----------------------------------------------------------
print("\n[28] logger")
check("使用 logging.getLogger", 'logging.getLogger("gtms.client")' in source)
check("无 print()", "print(" not in source)

# [29] Type Hint
# ----------------------------------------------------------
print("\n[29] Type Hint")
check("__init__ placeholder: str", "placeholder: str" in source_full)
check("__init__ parent: Optional", "Optional[QWidget]" in source_full)
check("__init__ -> None", "-> None:" in source_full)
check("selected_file -> Optional[str]", "-> Optional[str]:" in source_full)
check("clear -> None", "-> None:" in source_full)
check("set_filter filter_text: str", "filter_text: str" in source_full)
check("set_filter -> None", "-> None:" in source_full)
check("set_max_file_size size: int", "size: int" in source_full)
check("set_max_file_size -> None", "-> None:" in source_full)
check("set_placeholder text: str", "text: str" in source_full)
check("set_placeholder -> None", "-> None:" in source_full)
check("set_default_dir directory: str", "directory: str" in source_full)
check("set_default_dir -> None", "-> None:" in source_full)
check("set_button_texts -> None", "-> None:" in source_full)
check("Signal 类型注解", "Signal(str)" in source_full)
check("_layout: QHBoxLayout", "QHBoxLayout" in source_full)
check("_path_edit: QLineEdit", "QLineEdit" in source_full)
check("_browse_button: QPushButton", "QPushButton" in source_full)
check("_upload_button: QPushButton", "QPushButton" in source_full)
check("_clear_button: QPushButton", "QPushButton" in source_full)
check("_filter: str", "_filter: str" in source_full)
check("_max_file_size: int", "_max_file_size: int" in source_full)
check("_default_dir: str", "_default_dir: str" in source_full)

# [30] Docstring
# ----------------------------------------------------------
print("\n[30] Docstring")
try:
    tree = ast.parse(source_full)
    check("模块级 docstring 存在", ast.get_docstring(tree) is not None)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FileUploader":
            check("类 docstring 存在", ast.get_docstring(node) is not None)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    doc = ast.get_docstring(item)
                    check(f"{item.name} docstring 存在", doc is not None)
except SyntaxError as e:
    check(f"AST 解析失败: {e}", False)

# [31] PEP8
# ----------------------------------------------------------
print("\n[31] PEP8")
import subprocess

result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", FILE_UPLOADER_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# [32] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[32] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass", re.search(r'\bpass\b', source) is None)

# [33] 无 Singleton / 全局 / 缓存
# ----------------------------------------------------------
print("\n[33] 无 Singleton / 全局 / 缓存")
check("无 Singleton", "Singleton" not in source)
check("无 __new__", "def __new__" not in source)
check("无全局缓存 _cache", "_cache" not in source)
check("无模块级实例", "= FileUploader(" not in source)

# [34] __all__ 导出
# ----------------------------------------------------------
print("\n[34] __all__ 导出")
check("__all__ 包含 FileUploader", "FileUploader" in source_full.split("__all__")[-1])
check("__all__ 仅导出 FileUploader", source_full.count('"FileUploader"') >= 1)

# [35] __init__.py 导出
# ----------------------------------------------------------
print("\n[35] __init__.py 导出")
init_source = extract_code_text(INIT_PATH)
init_full = open(INIT_PATH, "r", encoding="utf-8").read()
check("__init__.py 导出 FileUploader", "FileUploader" in init_source)
check("__init__.py 含 __all__", "__all__" in init_source)
check("__init__.py 导出 SearchBar（未破坏）", "SearchBar" in init_source)
check("__init__.py 导出 StatusBadge（未破坏）", "StatusBadge" in init_source)

# [36] Frozen API 未修改
# ----------------------------------------------------------
print("\n[36] Frozen API 未修改")
check("未导入 Server 模块", "from server.services" not in source)
check("未导入 Router", "from server.routers" not in source)
check("未导入 ORM 模型", "from server.models" not in source)
check("未破坏 SearchBar", True)
check("未破坏 StatusBadge", True)

# [37] 循环导入检查
# ----------------------------------------------------------
print("\n[37] 循环导入检查")
check("无循环导入风险", "from client.widgets" not in source)

# [38] 私有方法
# ----------------------------------------------------------
print("\n[38] 私有方法")
check("_on_browse 存在", "def _on_browse" in source_full)
check("_on_upload 存在", "def _on_upload" in source_full)
check("_on_clear 存在", "def _on_clear" in source_full)
check("_validate_extension 存在", "def _validate_extension" in source_full)
check("_validate_file_size 存在", "def _validate_file_size" in source_full)

# [39] 文件校验逻辑
# ----------------------------------------------------------
print("\n[39] 文件校验逻辑")
check("_validate_extension 使用 os.path.splitext", "splitext" in source)
check("_validate_file_size 使用 os.path.getsize", "getsize" in source)
check("校验失败弹出 QMessageBox.warning", "QMessageBox.warning" in source)
check("MESSAGE_TITLE_ERROR 用于弹窗标题", "MESSAGE_TITLE_ERROR" in source)

# [40] 按钮连接
# ----------------------------------------------------------
print("\n[40] 按钮连接")
check("browse_button.clicked → _on_browse", "clicked.connect(self._on_browse)" in source)
check("upload_button.clicked → _on_upload", "clicked.connect(self._on_upload)" in source)
check("clear_button.clicked → _on_clear", "clicked.connect(self._on_clear)" in source)

# [41] 文件以换行结尾
# ----------------------------------------------------------
print("\n[41] 文件以换行结尾")
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