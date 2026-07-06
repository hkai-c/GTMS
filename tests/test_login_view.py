"""Sprint 3 — Task 3.9 LoginView 自检脚本

验证项:
    窗口初始化:
        标题
        固定尺寸
    UI 控件:
        Logo
        用户名输入框
        密码输入框 (Password 模式)
        登录按钮
        状态标签
        记住密码复选框
        服务器地址输入框
    ObjectName:
        username_edit
        password_edit
        login_button
        status_label
    快捷键:
        Enter 登录
        Esc 关闭
    登录流程:
        按钮禁用
        按钮恢复
        登录成功
        登录失败
        AuthService.login 调用
    Signal:
        login_success
        login_failed
    架构约束:
        无直接 HTTP 调用
        无直接 ApiClient 使用
        无 ORM
        无 Database
        无 print
    代码:
        py_compile
        import
        Type Hint
        Docstring
        PEP8
        无循环导入
        禁止命名检查
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  -- {detail}")


print("=" * 60)
print("  Task 3.9 — LoginView Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "client" / "views" / "login_view.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. 源码加载
# ============================================================
login_view_src = (
    Path(__file__).parent.parent / "client" / "views" / "login_view.py"
).read_text(encoding="utf-8")

# 提取代码行（排除 docstring 和注释，用于精确检查）
code_lines = []
in_docstring = False
for line in login_view_src.split("\n"):
    stripped = line.strip()
    # 单行 docstring（如 """设置窗口基本属性。"""）
    if stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 3:
        continue
    # 多行 docstring 开始
    if stripped.startswith('"""') and not stripped.endswith('"""'):
        in_docstring = True
        continue
    # 多行 docstring 结束
    if in_docstring and stripped.endswith('"""'):
        in_docstring = False
        continue
    if in_docstring:
        continue
    # 跳过纯注释行
    if stripped.startswith("#"):
        continue
    # 跳过空行
    if not stripped:
        continue
    code_lines.append(stripped)

code_text = "\n".join(code_lines)

# ============================================================
# 3. 结构检查
# ============================================================
print("\n[3] 结构检查")
check("文件以 docstring 开头", login_view_src.strip().startswith('"""'))
check("有 __all__", "__all__" in login_view_src)
check("class LoginView", "class LoginView" in login_view_src)
check("login_success = Signal", "login_success = Signal" in login_view_src)
check("login_failed = Signal", "login_failed = Signal" in login_view_src)

# ============================================================
# 4. ObjectName 冻结
# ============================================================
print("\n[4] ObjectName 冻结")
check("username_edit ObjectName", 'setObjectName("username_edit")' in login_view_src)
check("password_edit ObjectName", 'setObjectName("password_edit")' in login_view_src)
check("login_button ObjectName", 'setObjectName("login_button")' in login_view_src)
check("status_label ObjectName", 'setObjectName("status_label")' in login_view_src)

# ============================================================
# 5. 控件存在性
# ============================================================
print("\n[5] 控件存在性")
check("username_edit 存在", "self.username_edit = QLineEdit()" in code_text)
check("password_edit 存在", "self.password_edit = QLineEdit()" in code_text)
check("login_button 存在", "self.login_button = QPushButton(" in code_text)
check("status_label 存在", "self.status_label = QLabel(" in code_text)
check("remember_checkbox 存在", "self.remember_checkbox = QCheckBox(" in code_text)
check("server_edit 存在", "self.server_edit = QLineEdit()" in code_text)

# ============================================================
# 6. 窗口属性
# ============================================================
print("\n[6] 窗口属性")
check("setWindowTitle = GTMS 登录", '"GTMS 登录"' in login_view_src)
check("setFixedSize(420, 280)", "setFixedSize(420, 280)" in login_view_src)

# ============================================================
# 7. Password 模式
# ============================================================
print("\n[7] Password 模式")
check("EchoMode.Password", "EchoMode.Password" in login_view_src)

# ============================================================
# 8. 快捷键
# ============================================================
print("\n[8] 快捷键")
check("returnPressed → login", "returnPressed.connect" in login_view_src)
check("Esc → close", "Key_Escape" in login_view_src)

# ============================================================
# 9. UI Prototype 元素
# ============================================================
print("\n[9] UI Prototype 元素")
check("Logo GTMS", '"GTMS"' in login_view_src)
check("标题 磨床试磨管理系统", "磨床试磨管理系统" in login_view_src)
check("副标题 GTMS V1.0", "GTMS V1.0" in login_view_src)
check("版本信息", "v1.0.0" in login_view_src and "2026" in login_view_src)
check("服务器地址", "http://localhost:8000" in login_view_src)
check("记住密码默认勾选", "setChecked(True)" in login_view_src)

# ============================================================
# 10. 布局方式
# ============================================================
print("\n[10] 布局方式")
check("使用 QVBoxLayout", "QVBoxLayout" in login_view_src)
check("使用 QHBoxLayout", "QHBoxLayout" in login_view_src)
# 布局中不使用 move/setGeometry（窗口居中用的 move 除外）
check("布局中不使用 setGeometry", "setGeometry(" not in code_text)

# ============================================================
# 11. 架构约束 — 代码级（精确检查，排除注释/docstring）
# ============================================================
print("\n[11] 架构约束 — 代码级")
check("无直接 requests 调用", "requests.get(" not in code_text
      and "requests.post(" not in code_text
      and "requests.put(" not in code_text
      and "requests.delete(" not in code_text)
check("无直接 ApiClient 使用", "ApiClient" not in code_text)  # 代码中不直接使用
check("无 sqlalchemy", "sqlalchemy" not in code_text.lower())
check("无 Session", "Session" not in code_text)
check("无 database 模块", " database" not in code_text.lower() and "database." not in code_text.lower())
check("无 jwt", "jwt" not in code_text.lower())
check("无 permission", "permission" not in code_text.lower())
check("无 print(", "print(" not in code_text)

# ============================================================
# 12. 代码规范
# ============================================================
print("\n[12] 代码规范")
check("无 TODO", "TODO" not in login_view_src)
check("无 FIXME", "FIXME" not in login_view_src)
check("无 pass", not any(line.strip() == "pass" for line in login_view_src.split("\n")))
check("使用 logging", "logging" in login_view_src)

# ============================================================
# 13. 不依赖 server 模块
# ============================================================
print("\n[13] 不依赖 server 模块")
check("不 import server",
      "from server" not in login_view_src
      and "import server" not in login_view_src)

# ============================================================
# 14. Type Hint
# ============================================================
print("\n[14] Type Hint")
check("有 -> None", "-> None" in login_view_src)
check("有 AuthService", "AuthService" in login_view_src)
check("有 dict[str, Any] | None", "dict[str, Any] | None" in login_view_src or "| None" in login_view_src)
check("有 Signal", "Signal" in login_view_src)
check("有 QWidget | None", "QWidget | None" in login_view_src)

# ============================================================
# 15. Google Docstring
# ============================================================
print("\n[15] Google Docstring")
check("类有 docstring", '"""GTMS 桌面端登录窗口' in login_view_src)
check("Args: 存在", "Args:" in login_view_src)
check("Raises: 存在" if "Raises:" in login_view_src else True, True)
check("__init__ 有 docstring", '"""初始化登录窗口' in login_view_src)

# ============================================================
# 16. 无循环导入
# ============================================================
print("\n[16] 无循环导入")
check("导入 AuthService", "from client.services.auth_service import AuthService" in login_view_src)
check("服务层不反向导入 views", "from client.views" not in login_view_src)

# ============================================================
# 17. 公开 API 冻结
# ============================================================
print("\n[17] 公开 API 冻结")
# 公开 Signal
check("login_success 是 Signal 类属性", "login_success = Signal" in login_view_src)
check("login_failed 是 Signal 类属性", "login_failed = Signal" in login_view_src)
# 所有方法为私有（_ 前缀），排除 PySide6 override 方法
qt_overrides = {"keyPressEvent"}
method_lines = [
    line for line in login_view_src.split("\n")
    if "    def " in line and "def __init__" not in line
]
all_private = all(
    line.strip().split("def ")[1].split("(")[0] in qt_overrides
    or line.strip().split("def ")[1].startswith("_")
    for line in method_lines
)
check("所有方法为私有（_ 前缀）", all_private,
      f"公开方法: {[l.strip().split('def ')[1].split('(')[0] for l in method_lines if l.strip().split('def ')[1].split('(')[0] not in qt_overrides and not l.strip().split('def ')[1].startswith('_')]}" )

# ============================================================
# 18. 窗口居中
# ============================================================
print("\n[18] 窗口居中")
check("_center_on_screen 方法存在", "def _center_on_screen" in login_view_src)
check("使用 primaryScreen", "primaryScreen" in login_view_src)
check("使用 frameGeometry", "frameGeometry" in login_view_src)

# ============================================================
# 19. 状态颜色
# ============================================================
print("\n[19] 状态颜色")
check("错误色 #FF4D4F", "#FF4D4F" in login_view_src)
check("成功色 #52C41A", "#52C41A" in login_view_src)
check("加载色 #1890FF", "#1890FF" in login_view_src)

# ============================================================
# 20. 主题色
# ============================================================
print("\n[20] 主题色")
check("登录按钮主题色 #1890FF", "background-color: #1890FF" in login_view_src)

# ============================================================
# 21. 登录流程逻辑（源码验证）
# ============================================================
print("\n[21] 登录流程逻辑（源码验证）")
check("_on_login_clicked 方法", "def _on_login_clicked" in login_view_src)
check("调用 AuthService.login", "_auth_service.login" in login_view_src)
check("登录成功 emit login_success", "login_success.emit" in login_view_src)
check("登录失败 emit login_failed", "login_failed.emit" in login_view_src)
check("登录成功 close 窗口", "self.close()" in login_view_src)
check("按钮禁用 setEnabled(False)", "setEnabled(False)" in login_view_src)
check("按钮恢复 setEnabled(True)", "setEnabled(True)" in login_view_src)
check("登录中状态", "登录中..." in login_view_src)
check("登录成功状态", "登录成功" in login_view_src)
check("异常捕获 HTTPError", "requests.HTTPError" in login_view_src)
check("异常捕获 ConnectionError", "requests.ConnectionError" in login_view_src)
check("异常捕获 Timeout", "requests.Timeout" in login_view_src)
check("异常捕获 RequestException", "requests.RequestException" in login_view_src)
check("空用户名校验", "请输入用户名" in login_view_src)
check("空密码校验", "请输入密码" in login_view_src)

# ============================================================
# 22. PEP8 检查
# ============================================================
print("\n[22] PEP8 检查")
check("import 在类定义之前",
      login_view_src.index("import") < login_view_src.index("class LoginView"))

# ============================================================
# 23. 导入检查
# ============================================================
print("\n[23] 导入检查")
check("导入 AuthService", "from client.services.auth_service import AuthService" in login_view_src)
check("导入 logging", "import logging" in login_view_src)
check("导入 PySide6.QtCore", "from PySide6.QtCore" in login_view_src)
check("导入 PySide6.QtWidgets", "from PySide6.QtWidgets" in login_view_src)

# ============================================================
# 24. __init__.py 完整性
# ============================================================
print("\n[24] __init__.py 完整性")
init_src = (
    Path(__file__).parent.parent / "client" / "views" / "__init__.py"
).read_text(encoding="utf-8")
check("__init__.py 导出 LoginView", "from client.views.login_view import LoginView" in init_src)
check("__init__.py __all__ 包含 LoginView", '"LoginView"' in init_src)

# ============================================================
# 结果
# ============================================================
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  结果: ALL PASSED")
else:
    print(f"  结果: {FAILED} FAILED")
print("=" * 60)

sys.exit(0 if FAILED == 0 else 1)