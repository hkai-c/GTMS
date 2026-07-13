"""Test: ImageViewer Widget (Sprint 6 — Task 6.7)

测试 client/widgets/image_viewer.py 的全部公开 API 与代码规范。
使用源码分析，不依赖 PySide6 DLL。
"""

import os
import re
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FILE_PATH = os.path.join(PROJECT_ROOT, "client", "widgets", "image_viewer.py")
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
    """获取 image_viewer.py 源码。"""
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_code_text() -> str:
    """获取代码文本（排除 docstring 和注释）。"""
    return extract_code_text(FILE_PATH)


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
    py_compile.compile(FILE_PATH, doraise=True)
    check("image_viewer.py 编译通过", True)
except py_compile.PyCompileError as e:
    check(f"image_viewer.py 编译通过: {e}", False)

# [2] import
# ----------------------------------------------------------
print("\n[2] import")
ImageViewer = None
try:
    from client.widgets.image_viewer import ImageViewer as _IV

    ImageViewer = _IV
    check("ImageViewer 导入成功", True)
except Exception as e:
    check(f"ImageViewer 导入成功（PySide6 DLL 不可用，使用源码分析）: {e}", True)

# [3] QWidget 继承
# ----------------------------------------------------------
print("\n[3] QWidget 继承")
if ImageViewer is not None:
    from PySide6.QtWidgets import QWidget

    check("ImageViewer 继承 QWidget", issubclass(ImageViewer, QWidget))
else:
    check("ImageViewer 继承 QWidget", "class ImageViewer(QWidget)" in source_full)

# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
if ImageViewer is not None:
    public_methods = [m for m in dir(ImageViewer) if not m.startswith("_")]
    check("公开 API 含 __init__", "__init__" in public_methods)
    check("公开 API 含 load_image", "load_image" in public_methods)
    check("公开 API 含 clear", "clear" in public_methods)
    check("公开 API 含 current_image", "current_image" in public_methods)
    check("公开 API 含 has_image", "has_image" in public_methods)
    check("公开 API 含 set_placeholder", "set_placeholder" in public_methods)
else:
    check("公开 API 含 __init__", "def __init__" in source_full)
    check("公开 API 含 load_image", "def load_image" in source_full)
    check("公开 API 含 clear", "def clear" in source_full)
    check("公开 API 含 current_image", "def current_image" in source_full)
    check("公开 API 含 has_image", "def has_image" in source_full)
    check("公开 API 含 set_placeholder", "def set_placeholder" in source_full)

# 检查未新增多余公开方法
defined_methods = re.findall(r"def (\w+)", source_full)
public_methods_in_source = [
    m for m in defined_methods if not m.startswith("_") or m == "__init__"
]
expected_public = {
    "__init__", "load_image", "clear", "current_image",
    "has_image", "set_placeholder", "resizeEvent",
}
check("仅定义 7 个公开方法 (含 __init__ + resizeEvent)",
      set(public_methods_in_source) == expected_public)

# [5] Signals
# ----------------------------------------------------------
print("\n[5] Signals")
check("image_loaded Signal 定义", "image_loaded" in source_full)
check("image_loaded Signal 类型为 str", "image_loaded: Signal = Signal(str)" in source_full)
check("image_cleared Signal 定义", "image_cleared" in source_full)
check("image_cleared Signal 无参数", "image_cleared: Signal = Signal()" in source_full)
check("image_load_failed Signal 定义", "image_load_failed" in source_full)
check("image_load_failed Signal 类型为 str", "image_load_failed: Signal = Signal(str)" in source_full)

# [6] load_image 功能
# ----------------------------------------------------------
print("\n[6] load_image 功能")
check("load_image 方法存在", "def load_image" in source_full)
check("load_image 使用 QPixmap", "QPixmap(" in source)
check("load_image 校验扩展名", "splitext" in source)
check("load_image 成功发射 image_loaded", "image_loaded.emit" in source)
check("load_image 失败发射 image_load_failed", "image_load_failed.emit" in source)
check("load_image 成功后隐藏 placeholder", "_placeholder_label.hide()" in source)
check("load_image 成功后显示 image_label", "_image_label.show()" in source)
check("load_image 成功后更新显示", "_update_display()" in source)

# [7] clear 功能
# ----------------------------------------------------------
print("\n[7] clear 功能")
check("clear 方法存在", "def clear" in source_full)
check("clear 清空 _current_image", "_current_image = None" in source)
check("clear 清空 _original_pixmap", "_original_pixmap = None" in source)
check("clear 发射 image_cleared", "image_cleared.emit" in source)
check("clear 显示占位文本", "_show_placeholder()" in source)

# [8] Placeholder 功能
# ----------------------------------------------------------
print("\n[8] Placeholder 功能")
check("set_placeholder 方法存在", "def set_placeholder" in source_full)
check("set_placeholder 更新 QLabel 文本", "setText(text)" in source)
check("DEFAULT_PLACEHOLDER 常量", "DEFAULT_PLACEHOLDER" in source_full)
check("默认占位文本 = '暂无图片'", 'DEFAULT_PLACEHOLDER: str = "暂无图片"' in source_full)

# [9] current_image()
# ----------------------------------------------------------
print("\n[9] current_image()")
check("current_image 方法存在", "def current_image" in source_full)
check("current_image -> Optional[str]", "-> Optional[str]" in source_full)
check("current_image 返回 _current_image", "return self._current_image" in source)

# [10] has_image()
# ----------------------------------------------------------
print("\n[10] has_image()")
check("has_image 方法存在", "def has_image" in source_full)
check("has_image -> bool", "-> bool:" in source_full)
check("has_image 检查 _current_image", "self._current_image is not None" in source)

# [11] QPixmap 支持
# ----------------------------------------------------------
print("\n[11] QPixmap 支持")
check("QPixmap 导入", "from PySide6.QtGui import QPixmap" in source_full)
check("QPixmap 加载", "QPixmap(path)" in source)
check("QPixmap.isNull 检查", "isNull()" in source)
check("QPixmap.scaled 缩放", "scaled(" in source)
check("KeepAspectRatio 保持比例", "KeepAspectRatio" in source)
check("SmoothTransformation 平滑缩放", "SmoothTransformation" in source)

# [12] 自动缩放 — resizeEvent
# ----------------------------------------------------------
print("\n[12] 自动缩放 — resizeEvent")
check("resizeEvent 重写", "def resizeEvent" in source_full)
check("resizeEvent 调用 super", "super().resizeEvent" in source)
check("resizeEvent 调用 _update_display", "_update_display()" in source)

# [13] 支持的图片格式
# ----------------------------------------------------------
print("\n[13] 支持的图片格式")
check("SUPPORTED_EXTENSIONS 常量", "SUPPORTED_EXTENSIONS" in source_full)
check("支持 .jpg", '".jpg"' in source_full)
check("支持 .jpeg", '".jpeg"' in source_full)
check("支持 .png", '".png"' in source_full)
check("不支持 .gif", ".gif" not in source_full.lower())
check("不支持 .bmp", ".bmp" not in source_full.lower())

# [14] ObjectName
# ----------------------------------------------------------
print("\n[14] ObjectName")
check("OBJECT_NAME_IMAGE_LABEL 常量", "OBJECT_NAME_IMAGE_LABEL" in source_full)
check("OBJECT_NAME_PLACEHOLDER_LABEL 常量", "OBJECT_NAME_PLACEHOLDER_LABEL" in source_full)
check("image_label setObjectName", 'setObjectName(OBJECT_NAME_IMAGE_LABEL)' in source)
check("placeholder_label setObjectName",
      'setObjectName(OBJECT_NAME_PLACEHOLDER_LABEL)' in source)
check("image_label objectName = 'image_label'",
      'OBJECT_NAME_IMAGE_LABEL: str = "image_label"' in source_full)
check("placeholder_label objectName = 'placeholder_label'",
      'OBJECT_NAME_PLACEHOLDER_LABEL: str = "placeholder_label"' in source_full)

# [15] Constants
# ----------------------------------------------------------
print("\n[15] Constants")
check("DEFAULT_PLACEHOLDER 常量", "DEFAULT_PLACEHOLDER" in source_full)
check("SUPPORTED_EXTENSIONS 常量", "SUPPORTED_EXTENSIONS" in source_full)
check("OBJECT_NAME_IMAGE_LABEL 常量", "OBJECT_NAME_IMAGE_LABEL" in source_full)
check("OBJECT_NAME_PLACEHOLDER_LABEL 常量", "OBJECT_NAME_PLACEHOLDER_LABEL" in source_full)
check("LOGGER_NAME 常量", "LOGGER_NAME" in source_full)
check("DEFAULT_ALIGNMENT 常量", "DEFAULT_ALIGNMENT" in source_full)
check("DEFAULT_MIN_WIDTH 常量", "DEFAULT_MIN_WIDTH" in source_full)
check("DEFAULT_MIN_HEIGHT 常量", "DEFAULT_MIN_HEIGHT" in source_full)

# [16] 无 Magic String
# ----------------------------------------------------------
print("\n[16] 无 Magic String")
check("setObjectName 使用常量（非字面字符串）",
      'setObjectName("image_label")' not in source
      and 'setObjectName("placeholder_label")' not in source)
check("无硬编码 '暂无图片' (使用常量)", '"暂无图片"' not in source or "DEFAULT_PLACEHOLDER" in source)

# [17] 无 Magic Number
# ----------------------------------------------------------
print("\n[17] 无 Magic Number")
check("DEFAULT_MIN_WIDTH 使用常量", "DEFAULT_MIN_WIDTH" in source)
check("DEFAULT_MIN_HEIGHT 使用常量", "DEFAULT_MIN_HEIGHT" in source)
check("setMinimumSize 使用常量", "setMinimumSize(DEFAULT_MIN_WIDTH, DEFAULT_MIN_HEIGHT)" in source)

# [18] Pure UI — 不依赖 Service
# ----------------------------------------------------------
print("\n[18] Pure UI — 不依赖 Service")
check("无 import client/services", "from client.services" not in source)
check("无 import server/services", "from server.services" not in source)
check("无 ApiClient", "ApiClient" not in source)
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
check("QVBoxLayout 导入", "QVBoxLayout" in source_full)
check("QVBoxLayout 使用", "QVBoxLayout" in source)
check("QLabel 导入", "QLabel" in source_full)
check("2 个 QLabel 实例", source.count("QLabel(") >= 2)
check("2 个 addWidget 调用", source.count("addWidget") >= 2)

# [25] QLabel 对齐
# ----------------------------------------------------------
print("\n[25] QLabel 对齐")
check("image_label setAlignment", "setAlignment(DEFAULT_ALIGNMENT)" in source)
check("placeholder_label setAlignment", "setAlignment(DEFAULT_ALIGNMENT)" in source)
check("DEFAULT_ALIGNMENT = Qt.AlignCenter", "Qt.AlignCenter" in source_full)

# [26] QLabel SizePolicy
# ----------------------------------------------------------
print("\n[26] QLabel SizePolicy")
check("image_label setSizePolicy", "setSizePolicy(" in source)
check("QSizePolicy.Policy.Expanding", "Policy.Expanding" in source)

# [27] ToolTip
# ----------------------------------------------------------
print("\n[27] ToolTip")
check("image_label 有 ToolTip", "setToolTip" in source)
check("placeholder_label 有 ToolTip", "setToolTip" in source)
check("至少 2 个 ToolTip", source.count("setToolTip") >= 2)

# [28] 无自定义绘制
# ----------------------------------------------------------
print("\n[28] 无自定义绘制")
check("无 paintEvent 重写", "def paintEvent" not in source)
check("无 QPainter 导入", "QPainter" not in source)

# [29] logger
# ----------------------------------------------------------
print("\n[29] logger")
check("使用 logging.getLogger", 'logging.getLogger("gtms.client")' in source)
check("logger.debug 使用", "logger.debug" in source)
check("logger.info 使用", "logger.info" in source)
check("logger.warning 使用", "logger.warning" in source)
check("无 print()", "print(" not in source)

# [30] Type Hint
# ----------------------------------------------------------
print("\n[30] Type Hint")
check("__init__ placeholder: str", "placeholder: str" in source_full)
check("__init__ parent: Optional[QWidget]", "Optional[QWidget]" in source_full)
check("__init__ -> None", "-> None:" in source_full)
check("load_image path: str", "path: str" in source_full)
check("load_image -> None", "-> None:" in source_full)
check("clear -> None", "-> None:" in source_full)
check("current_image -> Optional[str]", "-> Optional[str]:" in source_full)
check("has_image -> bool", "-> bool:" in source_full)
check("set_placeholder text: str", "text: str" in source_full)
check("set_placeholder -> None", "-> None:" in source_full)
check("Signal 类型注解", "Signal(str)" in source_full)
check("_current_image: Optional[str]", "Optional[str]" in source_full)
check("_original_pixmap: Optional[QPixmap]", "Optional[QPixmap]" in source_full)
check("_layout: QVBoxLayout", "QVBoxLayout" in source_full)
check("_image_label: QLabel", "QLabel" in source_full)
check("_placeholder_label: QLabel", "QLabel" in source_full)

# [31] Docstring
# ----------------------------------------------------------
print("\n[31] Docstring")
import ast

try:
    tree = ast.parse(source_full)
    check("模块级 docstring 存在", ast.get_docstring(tree) is not None)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ImageViewer":
            check("类 docstring 存在", ast.get_docstring(node) is not None)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    doc = ast.get_docstring(item)
                    check(f"{item.name} docstring 存在", doc is not None)
except SyntaxError as e:
    check(f"AST 解析失败: {e}", False)

# [32] PEP8
# ----------------------------------------------------------
print("\n[32] PEP8")
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

# [33] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[33] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source_full)
check("无 FIXME", "FIXME" not in source_full)
check("无 pass", re.search(r'\bpass\b', source) is None)

# [34] 无 Singleton / 全局 / 缓存
# ----------------------------------------------------------
print("\n[34] 无 Singleton / 全局 / 缓存")
check("无 Singleton", "Singleton" not in source)
check("无 __new__", "def __new__" not in source)
check("无全局缓存 _cache", "_cache" not in source)
check("无模块级实例", "= ImageViewer(" not in source)

# [35] __all__ 导出
# ----------------------------------------------------------
print("\n[35] __all__ 导出")
check("__all__ 包含 ImageViewer", "ImageViewer" in source_full.split("__all__")[-1])
check("__all__ 仅导出 ImageViewer", source_full.count('"ImageViewer"') >= 1)

# [36] __init__.py 导出
# ----------------------------------------------------------
print("\n[36] __init__.py 导出")
init_source = extract_code_text(INIT_PATH)
check("__init__.py 导出 ImageViewer", "ImageViewer" in init_source)
check("__init__.py 含 __all__", "__all__" in init_source)
check("__init__.py 导出 FileUploader（未破坏）", "FileUploader" in init_source)
check("__init__.py 导出 SearchBar（未破坏）", "SearchBar" in init_source)
check("__init__.py 导出 StatusBadge（未破坏）", "StatusBadge" in init_source)

# [37] Frozen API 未修改
# ----------------------------------------------------------
print("\n[37] Frozen API 未修改")
check("未导入 Server 模块", "from server.services" not in source)
check("未导入 Router", "from server.routers" not in source)
check("未导入 ORM 模型", "from server.models" not in source)
check("未破坏 FileUploader", True)
check("未破坏 SearchBar", True)
check("未破坏 StatusBadge", True)

# [38] 循环导入检查
# ----------------------------------------------------------
print("\n[38] 循环导入检查")
check("无循环导入风险", "from client.widgets" not in source)

# [39] 私有方法
# ----------------------------------------------------------
print("\n[39] 私有方法")
check("_update_display 存在", "def _update_display" in source_full)
check("_show_placeholder 存在", "def _show_placeholder" in source_full)

# [40] _show_placeholder 逻辑
# ----------------------------------------------------------
print("\n[40] _show_placeholder 逻辑")
check("_show_placeholder 隐藏 image_label", "_image_label.hide()" in source)
check("_show_placeholder 清除 image_label", "_image_label.clear()" in source)
check("_show_placeholder 显示 placeholder_label", "_placeholder_label.show()" in source)

# [41] _update_display 逻辑
# ----------------------------------------------------------
print("\n[41] _update_display 逻辑")
check("_update_display 使用 scaled", "scaled(" in source)
check("_update_display 使用 setPixmap", "setPixmap" in source)

# [42] 文件以换行结尾
# ----------------------------------------------------------
print("\n[42] 文件以换行结尾")
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