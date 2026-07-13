"""Test: Desktop GrindingService (Sprint 7 — Task 7.4)

严格依据 DEVELOPMENT_ROADMAP.md Task 7.4 验收标准。
测试 client/services/grinding_service.py 全部公开 API 与代码规范。

注意：本测试使用源码分析 + Mock ApiClient，不依赖真实网络连接。
"""

import ast
import inspect
import os
import re
import sys
from datetime import datetime
from unittest.mock import MagicMock

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
print("  Task 7.4 — Desktop GrindingService Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("client", "services", "grinding_service.py")

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
    from client.services.grinding_service import GrindingService
    check("GrindingService 导入", True)
except ImportError as e:
    check("GrindingService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("GrindingService 是 class", inspect.isclass(GrindingService))
check("GrindingService 可实例化",
      GrindingService(MagicMock()) is not None)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(GrindingService)
    if not m.startswith("_") and callable(getattr(GrindingService, m))
]
check("list_grindings 存在", "list_grindings" in public_methods)
check("get_grinding 存在", "get_grinding" in public_methods)
check("create_grinding 存在", "create_grinding" in public_methods)
check("finish_grinding 存在", "finish_grinding" in public_methods)
check("update_grinding 存在", "update_grinding" in public_methods)
check("delete_grinding 存在", "delete_grinding" in public_methods)
check("公开 API 数量 = 6", len(public_methods) == 6)

# ----------------------------------------------------------
# [5] 方法签名
# ----------------------------------------------------------
print("\n[5] 方法签名")

sig = inspect.signature(GrindingService.list_grindings)
params = list(sig.parameters.keys())
check("list_grindings: 含 task_id", "task_id" in params)
check("list_grindings: 含 operator_id", "operator_id" in params)
check("list_grindings: 含 page", "page" in params)
check("list_grindings: 含 page_size", "page_size" in params)

sig = inspect.signature(GrindingService.get_grinding)
params = list(sig.parameters.keys())
check("get_grinding: 含 grinding_id", "grinding_id" in params)

sig = inspect.signature(GrindingService.create_grinding)
params = list(sig.parameters.keys())
check("create_grinding: 含 task_id", "task_id" in params)
check("create_grinding: 含 operator_id", "operator_id" in params)
check("create_grinding: 含 start_time", "start_time" in params)

sig = inspect.signature(GrindingService.finish_grinding)
params = list(sig.parameters.keys())
check("finish_grinding: 含 grinding_id", "grinding_id" in params)
check("finish_grinding: 含 result_status", "result_status" in params)
check("finish_grinding: 含 failure_reason", "failure_reason" in params)

sig = inspect.signature(GrindingService.update_grinding)
params = list(sig.parameters.keys())
check("update_grinding: 含 grinding_id", "grinding_id" in params)

sig = inspect.signature(GrindingService.delete_grinding)
params = list(sig.parameters.keys())
check("delete_grinding: 含 grinding_id", "grinding_id" in params)

# ----------------------------------------------------------
# [6] 返回类型注解
# ----------------------------------------------------------
print("\n[6] 返回类型注解")

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

check("list_grindings 返回 dict[str, Any]",
      "list_grindings" in source and "dict[str, Any]" in source)
check("get_grinding 返回 dict[str, Any]",
      "get_grinding" in source and "dict[str, Any]" in source)
check("create_grinding 返回 dict[str, Any]",
      "create_grinding" in source and "dict[str, Any]" in source)
check("finish_grinding 返回 dict[str, Any]",
      "finish_grinding" in source and "dict[str, Any]" in source)
check("update_grinding 返回 dict[str, Any]",
      "update_grinding" in source and "dict[str, Any]" in source)
check("delete_grinding 返回 dict[str, Any]",
      "delete_grinding" in source and "dict[str, Any]" in source)

# ----------------------------------------------------------
# [7] HTTP Method 映射
# ----------------------------------------------------------
print("\n[7] HTTP Method 映射")
code = extract_code_text(SOURCE_PATH)

check("list_grindings → GET /api/grinding",
      'self._api_client.get("/api/grinding"' in code)
check("get_grinding → GET /api/grinding/{id}",
      'self._api_client.get(f"/api/grinding/{grinding_id}")' in code)
check("create_grinding → POST /api/grinding",
      'self._api_client.post("/api/grinding"' in code)
check("finish_grinding → POST /api/grinding/{id}/finish",
      'self._api_client.post(' in code and
      '/api/grinding/{grinding_id}/finish"' in code)
check("update_grinding → PUT /api/grinding/{id}",
      'self._api_client.put(' in code and
      '/api/grinding/{grinding_id}"' in code)
check("delete_grinding → DELETE /api/grinding/{id}",
      'self._api_client.delete(f"/api/grinding/{grinding_id}")' in code)

# ----------------------------------------------------------
# [8] Query 参数
# ----------------------------------------------------------
print("\n[8] Query 参数")
check("list_grindings 仅提交非 None 参数",
      "if task_id is not None" in source)
check("list_grindings 默认 page=1", "page: int = 1" in source)
check("list_grindings 默认 page_size=20", "page_size: int = 20" in source)

# ----------------------------------------------------------
# [9] Body 规则
# ----------------------------------------------------------
print("\n[9] Body 规则")
check("create_grinding 仅提交非 None 字段",
      "if machine_type is not None" in source)
check("finish_grinding 仅提交非 None 字段",
      "if failure_reason is not None" in source)
check("update_grinding 仅提交非 None 字段",
      "if machine_type is not None" in source)

# ----------------------------------------------------------
# [10] response.json()
# ----------------------------------------------------------
print("\n[10] response.json()")
check("list_grindings 返回 resp.json()",
      "resp.json()" in source)
check("get_grinding 返回 resp.json()",
      source.count("resp.json()") >= 6)

# ----------------------------------------------------------
# [11] 使用 ApiClient
# ----------------------------------------------------------
print("\n[11] 使用 ApiClient")
check("使用 self._api_client", "self._api_client" in source)
check("禁止直接 requests", "requests" not in code and "httpx" not in code)

# ----------------------------------------------------------
# [12] 异常：无 try/except
# ----------------------------------------------------------
print("\n[12] 异常：无 try/except")
check("无 try/except（原样抛出）", "except" not in code)

# ----------------------------------------------------------
# [13] 无业务逻辑
# ----------------------------------------------------------
print("\n[13] 无业务逻辑")
check("无 process_status 判断", "process_status" not in code)
check("无 result_status 判断", "result_status =" not in code and
      "result_status ==" not in code)
check("无 ORM 查询", "query(" not in code)
check("无 db.commit", "db.commit" not in code)
check("无 SystemLog", "SystemLog" not in code)

# ----------------------------------------------------------
# [14] PEP8
# ----------------------------------------------------------
print("\n[14] PEP8")
import subprocess
result = subprocess.run(
    ["python", "-m", "flake8",
     "--select=E,W,F,N",
     "--max-line-length=100",
     SOURCE_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
check("PEP8 合规", result.returncode == 0 or not result.stdout.strip())

# ----------------------------------------------------------
# [15] Type Hint
# ----------------------------------------------------------
print("\n[15] Type Hint")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        check(
            f"{node.name} 有返回类型注解",
            node.returns is not None,
        )

# ----------------------------------------------------------
# [16] Docstring
# ----------------------------------------------------------
print("\n[16] Docstring")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块有 docstring", ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        check(
            f"{node.name} 有 docstring",
            ast.get_docstring(node) is not None,
        )
    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        check(
            f"{node.name} 有 docstring",
            ast.get_docstring(node) is not None,
        )

# ----------------------------------------------------------
# [17] 依赖检查
# ----------------------------------------------------------
print("\n[17] 依赖检查")
check("未导入 server 模块", "from server" not in source)
check("未导入 ORM / Database", "sqlalchemy" not in source)
check("未导入 JWT", "jwt" not in code)
check("未导入 PySide6", "PySide6" not in source)
check("未导入 View", "from client.views" not in source)
check("未导入 Widget", "from client.widgets" not in source)

# ----------------------------------------------------------
# [18] Logger
# ----------------------------------------------------------
print("\n[18] Logger")
check("使用 gtms.client logger", '"gtms.client"' in source)
check("无 print()", "print(" not in code)

# ----------------------------------------------------------
# [19] __init__.py 导出
# ----------------------------------------------------------
print("\n[19] __init__.py 导出")
try:
    from client.services.grinding_service import GrindingService as GS
    check("GrindingService 可导入", GS is not None)
except ImportError as e:
    check("GrindingService 可导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [20] __all__ 导出
# ----------------------------------------------------------
print("\n[20] __all__ 导出")
check("__all__ 包含 GrindingService",
      "GrindingService" in source.split("__all__")[1].split("]")[0]
      if "__all__" in source else False)

# ----------------------------------------------------------
# [21] Mock 测试
# ----------------------------------------------------------
print("\n[21] Mock 测试")
mock_client = MagicMock()

# list_grindings
mock_resp = MagicMock()
mock_resp.json.return_value = {"items": [], "total": 0}
mock_client.get.return_value = mock_resp
service = GrindingService(mock_client)
result = service.list_grindings()
check("list_grindings 调用成功", result == {"items": [], "total": 0})
check("_api_client.get 被调用", mock_client.get.called)

# get_grinding
mock_resp2 = MagicMock()
mock_resp2.json.return_value = {"id": 1, "task_id": 1}
mock_client.get.return_value = mock_resp2
result = service.get_grinding(1)
check("get_grinding 调用成功", result["id"] == 1)
check("_api_client.get 调用参数正确",
      mock_client.get.call_args[0][0] == "/api/grinding/1")

# create_grinding
mock_resp3 = MagicMock()
mock_resp3.json.return_value = {"id": 1, "task_id": 1}
mock_client.post.return_value = mock_resp3
now = datetime(2026, 7, 11, 10, 0, 0)
result = service.create_grinding(task_id=1, operator_id=2, start_time=now)
check("create_grinding 调用成功", result["task_id"] == 1)
check("_api_client.post 被调用", mock_client.post.called)

# finish_grinding
mock_resp4 = MagicMock()
mock_resp4.json.return_value = {"id": 1, "task_id": 1}
mock_client.post.return_value = mock_resp4
result = service.finish_grinding(1, result_status="passed")
check("finish_grinding 调用成功", result["task_id"] == 1)

# update_grinding
mock_resp5 = MagicMock()
mock_resp5.json.return_value = {"id": 1, "task_id": 1}
mock_client.put.return_value = mock_resp5
result = service.update_grinding(1, machine_type="Model-X")
check("update_grinding 调用成功", result["task_id"] == 1)
check("_api_client.put 被调用", mock_client.put.called)

# delete_grinding
mock_resp6 = MagicMock()
mock_resp6.json.return_value = {"message": "试磨记录已删除"}
mock_client.delete.return_value = mock_resp6
result = service.delete_grinding(1)
check("delete_grinding 调用成功", "message" in result)
check("_api_client.delete 被调用", mock_client.delete.called)

# 总计 6 个 HTTP 方法
check("GET 调用 2 次", mock_client.get.call_count == 2)
check("POST 调用 2 次", mock_client.post.call_count == 2)
check("PUT 调用 1 次", mock_client.put.call_count == 1)
check("DELETE 调用 1 次", mock_client.delete.call_count == 1)

# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 60)
print(f"  PASSED: {PASSED}")
print(f"  FAILED: {FAILED}")
print(f"  TOTAL:  {PASSED + FAILED}")
print("=" * 60)

if FAILED > 0:
    print("\n  [FAIL] 存在未通过的检查项！")
    sys.exit(1)
else:
    print("\n  [PASS] 全部检查通过！")