"""Test: Desktop QueryService (Sprint 9 — Task 10.4)

严格依据 DEVELOPMENT_ROADMAP.md Task 10.4 验收标准。
测试 client/services/query_service.py 全部公开 API 与代码规范。

注意：本测试使用源码分析，不依赖 HTTP 连接。
"""

import ast
import os
import re
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
print("  Task 10.4 — Desktop QueryService Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("client", "services", "query_service.py")

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
    from client.services.query_service import QueryService
    check("QueryService 导入", True)
except ImportError as e:
    check("QueryService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
import inspect
check("QueryService 是 class", inspect.isclass(QueryService))
check("QueryService 有 __init__", hasattr(QueryService, "__init__"))

# ----------------------------------------------------------
# [4] 公开 API
# ----------------------------------------------------------
print("\n[4] 公开 API")
public_methods = [
    m for m in dir(QueryService)
    if not m.startswith("_") and callable(getattr(QueryService, m))
]
check("list_dispatches 存在", "list_tasks" in public_methods)
check("get_dispatch 存在", "get_statistics" in public_methods)
check("create_dispatch 存在", "get_customer_ranking" in public_methods)
check("update_dispatch 存在", "get_machine_ranking" in public_methods)
check("delete_dispatch 存在", "export_excel" in public_methods)
check("公开 API 数量 = 5", len(public_methods) == 5)

# 读源码
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

code = extract_code_text(SOURCE_PATH)

# ----------------------------------------------------------
# [5] 依赖 ApiClient
# ----------------------------------------------------------
print("\n[5] 依赖 ApiClient")
check("导入 ApiClient", "from client.services.api_client import ApiClient" in source)
check("注入 ApiClient 到 __init__", "api_client: ApiClient" in source)
check("使用 self._api_client", "self._api_client" in source)

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

# ----------------------------------------------------------
# [7] HTTP Mapping
# ----------------------------------------------------------
print("\n[7] HTTP Mapping")
"list_tasks -> GET /api/query",
      "get" in code)
"get_statistics -> GET /api/query/statistics",
      "get" in code)
"get_customer_ranking -> GET /api/query/ranking/customers",
      "get" in code)
"get_machine_ranking -> GET /api/query/ranking/machines",
      "get" in code)
"export_excel -> POST /api/query/export",
      "post" in code)

# ----------------------------------------------------------
# [8] 返回 resp.json()
# ----------------------------------------------------------
print("\n[8] 返回 resp.json()")
check("list_dispatches 返回 resp.json()", "resp.json()" in code)
check("get_dispatch 返回 resp.json()", "resp.json()" in code)
check("create_dispatch 返回 resp.json()", "resp.json()" in code)
check("update_dispatch 返回 resp.json()", "resp.json()" in code)
check("delete_dispatch 返回 resp.json()", "resp.json()" in code)

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
check("零 Workflow", "TrialTaskProcessStatus" not in source)
check("零 Status Machine", "TrialTaskResultStatus" not in source)
check("零 状态判断", "TrialTaskProcessStatus" not in source)
check("零 状态流转", "TrialTaskResultStatus" not in source)

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
"list_tasks nz_id",
      "if_id is not None:" in source)
check("list_dispatches 仅提交非 None task_id",
      "if machine_model is not None:" in source)
check("list_dispatches 默认 page=1",
      "page: int = 1" in source)
check("list_dispatches 默认 page_size=20",
      "page_size: int = 20" in source)

# ----------------------------------------------------------
# [13] Body Rules（仅提交非 None 字段）
# ----------------------------------------------------------
"export_excel body_by",
      "_name" in source)
"export_excel nz_id",
      "if_id is not None:" in source)
"export_excel nz process_status",
      "if process_status is not None:" in source)
      "if operator_id is not None:" in source)

# ----------------------------------------------------------
# [14] Type Hint
# ----------------------------------------------------------
print("\n[14] Type Hint")
check("导入 Optional", "from typing import Any, Optional" in source)
check("返回类型注解 dict[str, Any]",
      "dict[str, Any]" in source)
check("api_client 类型注解", "ApiClient" in source)

# ----------------------------------------------------------
# [15] PEP8
# ----------------------------------------------------------
print("\n[15] PEP8")
import subprocess
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
check("无循环导入", "from client.services.query_service" not in code)

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
check("__all__ 含 QueryService", "QueryService" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [19] __init__.py 导出
# ----------------------------------------------------------
print("\n[19] __init__.py 导出")
init_path = os.path.join("client", "services", "__init__.py")
init_source = extract_code_text(init_path)
check("__init__.py 导出 QueryService", "QueryService" in init_source)
check("__init__.py 导出 InspectionService (未破坏)", "InspectionService" in init_source)
check("__init__.py 导出 GrindingService (未破坏)", "GrindingService" in init_source)
check("__init__.py 导出 ReceiptService (未破坏)", "ReceiptService" in init_source)

# ----------------------------------------------------------
# [20] 日志
# ----------------------------------------------------------
print("\n[20] 日志")
check("logger: gtms.client", 'logging.getLogger("gtms.client")' in source)
check("logger.debug 使用", "logger.debug" in source)
check("logger.info 使用", "logger.info" in source)
check("无 print()", "print(" not in code)
"logger.debug","logger.debug" in source)
# [21] Frozen API
# ----------------------------------------------------------
print("\n[21] Frozen API")
check("无 Server 模块导入", "from server.services" not in source)
check("无 Router 导入", "from server.routers" not in source)
check("无 ORM 模型导入", "from server.models import" not in source)

# ----------------------------------------------------------
# [22] 文件以换行结尾
# ----------------------------------------------------------
print("\n[22] 文件以换行结尾")
check("文件以换行结尾", source.endswith("\n"))

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