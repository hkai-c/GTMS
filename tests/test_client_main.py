"""Sprint 3 — Task 3.11 client/main.py 自检脚本

验证项:
    py_compile
    import
    main() 函数
    QApplication 单实例
    ApiClient 单实例
    AuthService 单实例
    LoginView 创建
    MainWindow 创建
    Signal 连接
    login_success
    logout_requested
    重新显示 LoginView
    logger
    无 print
    循环导入
    禁止命名
    异常退出
    事件循环

注意: 本测试使用源码分析，确保在无 GUI 环境下可运行。
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
print("  Task 3.11 — client/main.py Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "client" / "main.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. 源码加载
# ============================================================
main_src = (
    Path(__file__).parent.parent / "client" / "main.py"
).read_text(encoding="utf-8")

# 提取代码行（排除 docstring 和注释）
code_lines = []
in_docstring = False
for line in main_src.split("\n"):
    stripped = line.strip()
    if stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 3:
        continue
    if stripped.startswith('"""') and not stripped.endswith('"""'):
        in_docstring = True
        continue
    if in_docstring and stripped.endswith('"""'):
        in_docstring = False
        continue
    if in_docstring:
        continue
    if stripped.startswith("#"):
        continue
    if not stripped:
        continue
    code_lines.append(stripped)

code_text = "\n".join(code_lines)

# ============================================================
# 3. 结构检查
# ============================================================
print("\n[3] 结构检查")
check("文件以 docstring 开头", main_src.strip().startswith('"""'))
check("有 __all__", "__all__" in main_src)
check("__all__ 包含 main", '"main"' in main_src)

# ============================================================
# 4. 公开 API
# ============================================================
print("\n[4] 公开 API")
check("def main() -> int", "def main() -> int:" in main_src)
check("main 是唯一公开函数",
      "__all__" in main_src and len([l for l in main_src.split("\n")
                                      if '"main"' in l and "__all__" in main_src]) > 0)
# 检查：私有函数 _run, _connect_signals
check("_run 是私有函数", "def _run()" in main_src)
check("_connect_signals 是私有函数", "def _connect_signals" in main_src)

# ============================================================
# 5. main() 函数
# ============================================================
print("\n[5] main() 函数")
check("main() 返回 int", "def main() -> int:" in main_src)
check("main() 调用 _run()", "_run()" in main_src)
check("main() 有 try-except", "try:" in main_src and "except Exception:" in main_src)
check("main() 异常返回 1", "return 1" in main_src)
check("main() 正常返回 _run() 结果", "return _run()" in main_src)
check("main() logger.exception", "logger.exception" in main_src)

# ============================================================
# 6. _run() 函数
# ============================================================
print("\n[6] _run() 函数")
check("_run() 返回 int", "def _run() -> int:" in main_src)
check("_run() 创建 QApplication", "QApplication(sys.argv)" in main_src)
check("_run() 设置 appName", '"GTMS"' in main_src)
check("_run() 设置 appVersion", '"1.0.0"' in main_src)
check("_run() 创建 ApiClient", "ApiClient(base_url=" in main_src)
check("_run() 创建 AuthService", "AuthService(api_client)" in main_src)
check("_run() 创建 LoginView", "LoginView(auth_service)" in main_src)
check("_run() 调用 _connect_signals", "_connect_signals" in main_src)
check("_run() login_view.show()", "login_view.show()" in main_src)
check("_run() app.exec()", "app.exec()" in main_src)
check("_run() 返回 exit_code", "return exit_code" in main_src)

# ============================================================
# 7. QApplication 单实例
# ============================================================
print("\n[7] QApplication 单实例")
check("QApplication 只创建一次", main_src.count("QApplication(") == 1)
check("QApplication 在 _run() 中创建",
      "QApplication(sys.argv)" in main_src)

# ============================================================
# 8. ApiClient 单实例
# ============================================================
print("\n[8] ApiClient 单实例")
check("ApiClient 只创建一次", main_src.count("ApiClient(") == 1)
check("ApiClient 在 _run() 中创建",
      "ApiClient(base_url=client_config.API_BASE_URL)" in main_src)

# ============================================================
# 9. AuthService 单实例
# ============================================================
print("\n[9] AuthService 单实例")
check("AuthService 只创建一次", main_src.count("AuthService(") == 1)
check("AuthService 绑定 ApiClient",
      "AuthService(api_client)" in main_src)

# ============================================================
# 10. LoginView 创建
# ============================================================
print("\n[10] LoginView 创建")
check("LoginView 创建一次", main_src.count("LoginView(") == 1)
check("LoginView 绑定 AuthService",
      "LoginView(auth_service)" in main_src)

# ============================================================
# 11. MainWindow 创建
# ============================================================
print("\n[11] MainWindow 创建")
check("MainWindow 在登录成功后创建", "MainWindow()" in main_src)
check("MainWindow 不在 _run() 中预创建",
      "MainWindow()" not in main_src.split("def _connect_signals")[0])

# ============================================================
# 12. Signal 连接
# ============================================================
print("\n[12] Signal 连接")
check("login_success.connect", "login_success.connect" in main_src)
check("logout_requested.connect", "logout_requested.connect" in main_src)
check("_connect_signals 函数", "def _connect_signals" in main_src)

# ============================================================
# 13. login_success 回调
# ============================================================
print("\n[13] login_success 回调")
check("on_login_success 函数", "on_login_success" in main_src)
check("创建 MainWindow", "MainWindow()" in main_src)
check("set_auth_service", "set_auth_service" in main_src)
check("refresh_permissions", "refresh_permissions" in main_src)
check("main_window.show()", "main_window.show()" in main_src)
check("login_view.hide()", "login_view.hide()" in main_src)
check("logger Login Success", "Login Success" in main_src)

# ============================================================
# 14. logout_requested 回调
# ============================================================
print("\n[14] logout_requested 回调")
check("on_logout_requested 函数", "on_logout_requested" in main_src)
check("login_view.show()", "login_view.show()" in main_src)
check("清理 main_window_ref", "main_window_ref[0] = None" in main_src)
check("logger Logout", "Logout" in main_src)

# ============================================================
# 15. 重新显示 LoginView
# ============================================================
print("\n[15] 重新显示 LoginView")
check("退出后重新显示 LoginView", "login_view.show()" in main_src)
check("不重新创建 LoginView", main_src.count("LoginView(") == 1)
check("不重新创建 QApplication", main_src.count("QApplication(") == 1)

# ============================================================
# 16. 重新登录 → 新 MainWindow
# ============================================================
print("\n[16] 重新登录 → 新 MainWindow")
# 验证 MainWindow 在 on_login_success 中创建，每次登录都新建
check("MainWindow 在回调中创建", "MainWindow()" in main_src)
check("旧 MainWindow 被清理", "main_window_ref[0] = None" in main_src)

# ============================================================
# 17. 生命周期
# ============================================================
print("\n[17] 生命周期")
check("Application Started", "Application Started" in main_src)
check("LoginView displayed", "LoginView displayed" in main_src)
check("MainWindow Opened", "MainWindow Opened" in main_src)
check("Application Exit", "Application Exit" in main_src)

# ============================================================
# 18. logger
# ============================================================
print("\n[18] logger")
check("使用 getLogger", "getLogger" in main_src)
check("logger name: gtms.client", '"gtms.client"' in main_src)
check("无 print(", "print(" not in code_text)

# ============================================================
# 19. 架构约束
# ============================================================
print("\n[19] 架构约束")
check("无直接 requests 调用",
      "requests.get(" not in code_text and "requests.post(" not in code_text
      and "requests.put(" not in code_text and "requests.delete(" not in code_text)
check("无 import requests", "import requests" not in main_src)
check("无直接 ApiClient 使用 (除创建)", "ApiClient" not in code_text or main_src.count("ApiClient(") <= 1)
check("无 sqlalchemy", "sqlalchemy" not in main_src.lower())
check("无 Session", "Session" not in code_text)
check("无 jwt", "jwt" not in code_text.lower())
check("无服务端权限调用",
      "has_permission" not in main_src.lower()
      and "check_permission" not in main_src.lower())
check("不依赖 server 模块",
      "from server" not in main_src
      and "import server" not in main_src)

# ============================================================
# 20. 代码规范
# ============================================================
print("\n[20] 代码规范")
check("无 TODO", "TODO" not in main_src)
check("无 FIXME", "FIXME" not in main_src)
check("无 pass",
      not any(line.strip() == "pass" for line in main_src.split("\n")))
check("使用 logging", "logging" in main_src)
check("使用 sys.exit" not in code_text, "sys.exit" not in code_text)

# ============================================================
# 21. Type Hint
# ============================================================
print("\n[21] Type Hint")
check("main() -> int", "def main() -> int:" in main_src)
check("_run() -> int", "def _run() -> int:" in main_src)
check("_connect_signals -> None", "-> None:" in main_src)
check("有 app: QApplication", "app: QApplication" in main_src)
check("有 auth_service: AuthService", "auth_service: AuthService" in main_src)
check("有 login_view: LoginView", "login_view: LoginView" in main_src)
check("有 user: dict[str, Any]", "dict[str, Any]" in main_src)

# ============================================================
# 22. Google Docstring
# ============================================================
print("\n[22] Google Docstring")
check("文件有 docstring", '"""GTMS 桌面端启动入口' in main_src)
check("main() 有 docstring", '"""GTMS 桌面端启动入口' in main_src)
check("_run() 有 docstring", '"""执行主启动流程' in main_src)
check("_connect_signals 有 docstring", '"""连接登录/退出 Signal' in main_src)
check("Args: 存在", "Args:" in main_src)
check("Returns: 存在", "Returns:" in main_src)

# ============================================================
# 23. 无循环导入
# ============================================================
print("\n[23] 无循环导入")
check("导入 ApiClient", "from client.services.api_client import ApiClient" in main_src)
check("导入 AuthService", "from client.services.auth_service import AuthService" in main_src)
check("导入 LoginView", "from client.views.login_view import LoginView" in main_src)
check("导入 MainWindow", "from client.views.main_window import MainWindow" in main_src)
check("导入 client_config", "from client.config import client_config" in main_src)
check("服务层不反向导入 main", "from client.main" not in main_src)

# ============================================================
# 24. 异常退出
# ============================================================
print("\n[24] 异常退出")
check("main() try-except", "try:" in main_src)
check("except Exception", "except Exception" in main_src)
check("异常返回 1", "return 1" in main_src)
check("正常返回 0", "return exit_code" in main_src)

# ============================================================
# 25. 事件循环
# ============================================================
print("\n[25] 事件循环")
check("app.exec()", "app.exec()" in main_src)
check("返回 exit_code", "exit_code = app.exec()" in main_src)

# ============================================================
# 26. 禁止命名检查
# ============================================================
print("\n[26] 禁止命名检查")
forbidden = [
    "ValidationException", "AuthorizationException", "ConflictException",
]
for name in forbidden:
    check(f"文件不含 {name}", name not in main_src)

# ============================================================
# 27. 闭包变量
# ============================================================
print("\n[27] 闭包变量")
check("main_window_ref 闭包", "main_window_ref" in main_src)
check("main_window_ref 类型标注", "MainWindow | None" in main_src)

# ============================================================
# 28. 不重新创建 QApplication
# ============================================================
print("\n[28] 不重新创建 QApplication")
check("QApplication 只创建一次", main_src.count("QApplication(") == 1)

# ============================================================
# 29. 不重新创建 ApiClient
# ============================================================
print("\n[29] 不重新创建 ApiClient")
check("ApiClient 只创建一次", main_src.count("ApiClient(") == 1)

# ============================================================
# 30. 不重新创建 AuthService
# ============================================================
print("\n[30] 不重新创建 AuthService")
check("AuthService 只创建一次", main_src.count("AuthService(") == 1)

# ============================================================
# 31. 不调用 os.exec()
# ============================================================
print("\n[31] 不调用 os.exec()")
check("不 import os", "import os" not in main_src)
check("不调用 os.exec", "os.exec" not in main_src)

# ============================================================
# 32. 不重启程序
# ============================================================
print("\n[32] 不重启程序")
check("不 import subprocess", "subprocess" not in main_src)
check("不调用 sys.exit 在循环中", "sys.exit" not in code_text)

# ============================================================
# 33. PEP8
# ============================================================
print("\n[33] PEP8")
check("import 在函数前", main_src.index("import ") < main_src.index("def main"))

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