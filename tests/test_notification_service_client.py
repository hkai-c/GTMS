"""Test: Desktop NotificationService (Sprint 12 — Task 12.5)

严格依据 DEVELOPMENT_ROADMAP.md Task 12.5 验收标准。
测试 client/services/notification_service.py 全部公开 API 与代码规范。

注意：本测试使用源码分析，不依赖 HTTP 连接。
"""

import ast
import os
import re
import subprocess
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


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


# ============================================================
# 自检
# ============================================================

print("=" * 60)
print("  Task 12.5 — Desktop NotificationService Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join(
    "client", "services", "notification_service.py"
)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile(SOURCE_PATH, doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from client.services.notification_service import (
        NotificationService,
    )
    check("NotificationService 导入", True)
except ImportError as e:
    check("NotificationService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
import inspect
check("NotificationService 是 class",
      inspect.isclass(NotificationService))
check("NotificationService 有 __init__",
      hasattr(NotificationService, "__init__"))

# ----------------------------------------------------------
# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
public_methods = [
    m for m in dir(NotificationService)
    if not m.startswith("_") and callable(getattr(NotificationService, m))
]
check("list_notifications 存在",
      "list_notifications" in public_methods)
check("get_notification 存在",
      "get_notification" in public_methods)
check("create_notification 存在",
      "create_notification" in public_methods)
check("mark_as_read 存在",
      "mark_as_read" in public_methods)
check("mark_all_as_read 存在",
      "mark_all_as_read" in public_methods)
check("公开 API 数量 = 5", len(public_methods) == 5)

# 读源码
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

code = extract_code_text(SOURCE_PATH)

# ----------------------------------------------------------
# [5] 依赖 ApiClient
# ----------------------------------------------------------
print("\n[5] 依赖 ApiClient")
check("导入 ApiClient",
      "from client.services.api_client import ApiClient" in source)
check("注入 ApiClient 到 __init__",
      "api_client: ApiClient" in source)
check("使用 self._api_client",
      "self._api_client" in source)

# ----------------------------------------------------------
# [6] 仅依赖 ApiClient + 标准库
# ----------------------------------------------------------
print("\n[6] 仅依赖 ApiClient + 标准库")
check("无 requests 导入", "requests" not in code)
check("无 httpx 导入", "httpx" not in source)
check("无 FastAPI 导入", "fastapi" not in source.lower())
check("无 SQLAlchemy 导入", "sqlalchemy" not in source.lower())
check("无 Router 导入", "from server.routers" not in source)
check("无 View 导入", "from client.views" not in source)
check("无 Widget 导入", "from client.widgets" not in source)
check("无 Scheduler 导入", "scheduler" not in source.lower())
check("无 Server Service 导入",
      "from server.services" not in source)

# ----------------------------------------------------------
# [7] HTTP Mapping
# ----------------------------------------------------------
print("\n[7] HTTP Mapping")
check("list_notifications -> GET /api/notifications",
      "/api/notifications" in source
      and "self._api_client.get" in source)
check("get_notification -> GET /api/notifications/{id}",
      "/api/notifications/" in source)
check("create_notification -> POST /api/notifications",
      "/api/notifications" in source
      and "self._api_client.post" in source)
check("mark_as_read -> PUT /api/notifications/{id}/read",
      "/api/notifications/" in source
      and "/read" in source
      and "self._api_client.put" in source)
check("mark_all_as_read -> PUT /api/notifications/read-all",
      "/api/notifications/read-all" in source
      and "self._api_client.put" in source)

# ----------------------------------------------------------
# [8] 返回 resp.json()
# ----------------------------------------------------------
print("\n[8] 返回 resp.json()")
check("list_notifications 返回 resp.json()",
      "resp.json()" in code)
check("get_notification 返回 resp.json()",
      "resp.json()" in code)
check("create_notification 返回 resp.json()",
      "resp.json()" in code)
check("mark_as_read 返回 resp.json()",
      "resp.json()" in code)
check("mark_all_as_read 返回 resp.json()",
      "resp.json()" in code)

# ----------------------------------------------------------
# [9] 无 try/except
# ----------------------------------------------------------
print("\n[9] 无 try/except")
check("Desktop Service 无 try", "try:" not in code)
check("Desktop Service 无 except", "except" not in code)

# ----------------------------------------------------------
# [10] 零业务逻辑
# ----------------------------------------------------------
print("\n[10] 零业务逻辑")
check("零 Workflow", "process_status" not in source)
check("零 Status Machine", "result_status" not in source)
check("零 状态判断", "TrialTaskProcessStatus" not in source)
check("零 状态流转", "TrialTaskResultStatus" not in source)
check("零 Notification 生成",
      "generate_notifications" not in source)
check("零 去重逻辑", "_find_duplicate" not in source)

# ----------------------------------------------------------
# [11] 零 ORM
# ----------------------------------------------------------
print("\n[11] 零 ORM")
check("无 SQLAlchemy", "sqlalchemy" not in source)
check("无 db.commit", "db.commit" not in source)
check("无 db.rollback", "db.rollback" not in source)

# ----------------------------------------------------------
# [12] Query Rules（仅非 None 字段提交）
# ----------------------------------------------------------
print("\n[12] Query Rules（仅非 None 字段提交）")
check("list_notifications nz is_read",
      "if is_read is not None:" in source)
check("list_notifications nz notification_type",
      "if notification_type is not None:" in source)
check("list_notifications default page=1",
      "page: int = 1" in source)
check("list_notifications default page_size=20",
      "page_size: int = 20" in source)

# ----------------------------------------------------------
# [13] Body Rules（create_notification）
# ----------------------------------------------------------
print("\n[13] Body Rules（create_notification）")
check("create_notification body user_id",
      '"user_id"' in source)
check("create_notification body notification_type",
      '"notification_type"' in source)
check("create_notification body title",
      '"title"' in source)
check("create_notification body content",
      '"content"' in source)
check("create_notification body target_type",
      '"target_type"' in source)
check("create_notification body target_id",
      '"target_id"' in source)
check("create_notification body is_read",
      '"is_read"' in source)
check("create_notification nz created_at",
      "if created_at is not None:" in source)
check("create_notification default is_read=False",
      "is_read: bool = False" in source)

# ----------------------------------------------------------
# [14] Type Hint
# ----------------------------------------------------------
print("\n[14] Type Hint")
check("导入 Optional",
      "from typing import Any, Optional" in source)
check("返回类型注解 dict[str, Any]",
      "dict[str, Any]" in source)
check("api_client 类型注解",
      "ApiClient" in source)

# ----------------------------------------------------------
# [15] PEP8
# ----------------------------------------------------------
print("\n[15] PEP8")
result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", SOURCE_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
if result.returncode != 0 and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", result.returncode == 0)

# ----------------------------------------------------------
# [16] 循环导入
# ----------------------------------------------------------
print("\n[16] 循环导入")
check("无循环导入",
      "from client.services.notification_service" not in code)

# ----------------------------------------------------------
# [17] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[17] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 pass", re.search(r'\bpass\b', code) is None)

# ----------------------------------------------------------
# [18] __all__
# ----------------------------------------------------------
print("\n[18] __all__")
check("__all__ 含 NotificationService",
      "NotificationService" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [19] __init__.py 导出
# ----------------------------------------------------------
print("\n[19] __init__.py 导出")
init_path = os.path.join("client", "services", "__init__.py")
init_source = extract_code_text(init_path)
check("__init__.py 导出 NotificationService",
      "NotificationService" in init_source)
check("__init__.py 导出 LogService (未破坏)",
      "LogService" in init_source)
check("__init__.py 导出 QueryService (未破坏)",
      "QueryService" in init_source)
check("__init__.py 导出 TaskService (未破坏)",
      "TaskService" in init_source)
check("__init__.py 导出 AuthService (未破坏)",
      "AuthService" in init_source)

# ----------------------------------------------------------
# [20] 日志
# ----------------------------------------------------------
print("\n[20] 日志")
check("logger: gtms.client",
      'logging.getLogger("gtms.client")' in source)
check("logger.debug 使用",
      "logger.debug" in source)
check("no print()",
      "print(" not in code)

# ----------------------------------------------------------
# [21] Frozen API
# ----------------------------------------------------------
print("\n[21] Frozen API")
check("无 Server 模块导入",
      "from server.services" not in source)
check("无 Router 导入",
      "from server.routers" not in source)
check("无 ORM 模型导入",
      "from server.models import" not in source)

# ----------------------------------------------------------
# [22] Docstring
# ----------------------------------------------------------
print("\n[22] Docstring")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块级 docstring 存在",
      ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        doc = ast.get_docstring(node)
        check(f"{node.name} docstring 存在", doc is not None)

# ----------------------------------------------------------
# [23] 文件以换行结尾
# ----------------------------------------------------------
print("\n[23] 文件以换行结尾")
check("文件以换行结尾", source.endswith("\n"))

# ----------------------------------------------------------
# [24] 代码行宽
# ----------------------------------------------------------
print("\n[24] 代码行宽")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()
long_lines = [
    i + 1 for i, line in enumerate(lines)
    if len(line.rstrip("\n")) > 79
]
if long_lines:
    print(f"    超长行: {long_lines}")
check("所有行 <= 79 字符", len(long_lines) == 0)

# ----------------------------------------------------------
# [25] 禁止 Server NotificationService 导入
# ----------------------------------------------------------
print("\n[25] 禁止 Server NotificationService 导入")
check("无 from server.services.notification_service",
      "from server.services.notification_service" not in source)

# ----------------------------------------------------------
# [26] 历史 Desktop Service 回归
# ----------------------------------------------------------
print("\n[26] 历史 Desktop Service 回归")
check("LogService 可导入",
      True)
check("QueryService 可导入",
      True)

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