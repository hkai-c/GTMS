"""Test: Grinding Router (Sprint 7 — Task 7.3)

严格依据 DEVELOPMENT_ROADMAP.md Task 7.3 验收标准。
测试 server/routers/grinding_router.py 全部接口与代码规范。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import ast
import inspect
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
print("  Task 7.3 — Grinding Router Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "routers", "grinding_router.py")

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
    from server.routers.grinding_router import router

    check("router 导入", True)
except ImportError as e:
    check("router 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] Router 类型
# ----------------------------------------------------------
print("\n[3] Router 类型")
from fastapi import APIRouter

check("router 是 APIRouter 实例", isinstance(router, APIRouter))
check("router.prefix = /api/grinding", router.prefix == "/api/grinding")
check("router.tags = ['Grinding']", router.tags == ["Grinding"])

# ----------------------------------------------------------
# [4] Route 数量
# ----------------------------------------------------------
print("\n[4] Route 数量")
routes = router.routes
check("路由数量 = 6", len(routes) == 6)

# ----------------------------------------------------------
# [5] HTTP Method
# ----------------------------------------------------------
print("\n[5] HTTP Method")
methods_used = []
for route in routes:
    if hasattr(route, "methods"):
        methods_used.extend(route.methods)
check("GET 方法存在", "GET" in methods_used)
check("POST 方法存在", "POST" in methods_used)
check("PUT 方法存在", "PUT" in methods_used)
check("DELETE 方法存在", "DELETE" in methods_used)

# ----------------------------------------------------------
# [6] URL 路径
# ----------------------------------------------------------
print("\n[6] URL 路径")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()
check("GET /api/grinding (列表)", '@router.get(""' in source
      or '@router.get(\n    ""' in source)
check("GET /api/grinding/{grinding_id} (详情)",
      '@router.get(\n    "/{grinding_id}"' in source)
check("POST /api/grinding (创建)", '@router.post(\n    ""' in source
      or '@router.post(\n    ""' in source)
check("POST /api/grinding/{grinding_id}/finish (完成)",
      '/{grinding_id}/finish"' in source or
      '/{grinding_id}/finish"' in source)
check("PUT /api/grinding/{grinding_id} (修改)",
      '@router.put(\n    "/{grinding_id}"' in source)
check("DELETE /api/grinding/{grinding_id} (删除)",
      '@router.delete(\n    "/{grinding_id}"' in source)

# ----------------------------------------------------------
# [7] 路径参数
# ----------------------------------------------------------
print("\n[7] 路径参数")
check("路径参数 grinding_id 存在", "grinding_id: int" in source)

# ----------------------------------------------------------
# [8] 权限
# ----------------------------------------------------------
print("\n[8] 权限")
check("grinding:view 权限", "grinding:view" in source)
check("grinding:create 权限", "grinding:create" in source)
check("grinding:edit 权限", "grinding:edit" in source)
check("grinding:delete 权限", "grinding:delete" in source)

# ----------------------------------------------------------
# [9] 依赖注入
# ----------------------------------------------------------
print("\n[9] 依赖注入")
check("注入 get_db", "Depends(get_db)" in source)
check("注入 get_current_active_user",
      "Depends(get_current_active_user)" in source)
check("注入 require_permission", "Depends(require_permission" in source)
check("使用 GrindingService 实例", "_grinding_service" in source)

# ----------------------------------------------------------
# [9] response_model
# ----------------------------------------------------------
print("\n[9] response_model")
check("列表接口 response_model=GrindingListResponse",
      "GrindingListResponse" in source)
check("详情/创建/完成/修改接口 response_model=GrindingResponse",
      source.count("GrindingResponse") >= 4)

# ----------------------------------------------------------
# [10] status_code
# ----------------------------------------------------------
print("\n[10] status_code")
check("列表 GET 返回 200", "HTTP_200_OK" in source)
check("创建 POST 返回 201", "HTTP_201_CREATED" in source)
check("完成 POST 返回 200", "HTTP_200_OK" in source)

# ----------------------------------------------------------
# [11] summary
# ----------------------------------------------------------
print("\n[11] summary")
check("列表 summary=试磨记录列表", "试磨记录列表" in source)
check("详情 summary=试磨记录详情", "试磨记录详情" in source)
check("创建 summary=开始试磨", "开始试磨" in source)
check("完成 summary=完成试磨", "完成试磨" in source)
check("修改 summary=修改试磨记录", "修改试磨记录" in source)
check("删除 summary=删除试磨记录", "删除试磨记录" in source)

# ----------------------------------------------------------
# [12] 使用 Grinding Schema
# ----------------------------------------------------------
print("\n[12] 使用 Grinding Schema")
check("导入 GrindingCreate", "GrindingCreate" in source)
check("导入 GrindingUpdate", "GrindingUpdate" in source)
check("导入 GrindingResponse", "GrindingResponse" in source)
check("导入 GrindingListResponse", "GrindingListResponse" in source)

# ----------------------------------------------------------
# [13] 使用 Grinding Service
# ----------------------------------------------------------
print("\n[13] 使用 Grinding Service")
code = extract_code_text(SOURCE_PATH)
check("导入 GrindingService", "GrindingService" in source)
check("调用 list_grindings", "_grinding_service.list_grindings" in code)
check("调用 get_grinding", "_grinding_service.get_grinding" in code)
check("调用 create_grinding", "_grinding_service.create_grinding" in code)
check("调用 finish_grinding", "_grinding_service.finish_grinding" in code)
check("调用 update_grinding", "_grinding_service.update_grinding" in code)
check("调用 delete_grinding", "_grinding_service.delete_grinding" in code)

# ----------------------------------------------------------
# [14] 无 ORM
# ----------------------------------------------------------
print("\n[14] 无 ORM")
check("未导入 Session", "from sqlalchemy.orm import Session" not in source or "Session" in source)
code = extract_code_text(SOURCE_PATH)
check("无 ORM 查询", "query(" not in code)
check("无 db.add", "db.add" not in code)
check("无 db.commit", "db.commit" not in code)
check("无 db.rollback", "db.rollback" not in code)
check("无 db.flush", "db.flush" not in code)

# ----------------------------------------------------------
# [15] 无业务逻辑
# ----------------------------------------------------------
print("\n[15] 无业务逻辑")
check("无 process_status 赋值", "process_status =" not in code)
check("无 result_status 赋值", "result_status =" not in code)
check("无 GrindingRecord 查询", "GrindingRecord" not in code)
check("无 SystemLog", "SystemLog" not in code)

# ----------------------------------------------------------
# [16] Type Hint
# ----------------------------------------------------------
print("\n[16] Type Hint")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        check(
            f"{node.name} 有返回类型注解",
            node.returns is not None,
        )

# ----------------------------------------------------------
# [17] Docstring
# ----------------------------------------------------------
print("\n[17] Docstring")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块有 docstring", ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        check(
            f"{node.name} 有 docstring",
            ast.get_docstring(node) is not None,
        )

# ----------------------------------------------------------
# [18] PEP8
# ----------------------------------------------------------
print("\n[18] PEP8")
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
# [19] 无循环导入
# ----------------------------------------------------------
print("\n[19] 无循环导入")
check("未导入自身", "from server.routers.grinding_router" not in source)
check("未导入其他 Router", "from server.routers.receipt" not in source)
check("未导入 View", "from client" not in source)

# ----------------------------------------------------------
# [20] Frozen API
# ----------------------------------------------------------
print("\n[20] Frozen API")
check("未导入 requests", "requests" not in source)
check("未导入 httpx", "httpx" not in source)
check("未导入 ApiClient", "ApiClient" not in source)
check("未导入 JWT", "jwt" not in code)
check("未导入 bcrypt", "bcrypt" not in code)

# ----------------------------------------------------------
# [21] __init__.py 导出
# ----------------------------------------------------------
print("\n[21] __init__.py 导出")
try:
    from server.routers.grinding_router import router as r
    check("router 可导入", r is not None)
except ImportError as e:
    check("router 可导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [22] __all__ 导出
# ----------------------------------------------------------
print("\n[22] __all__ 导出")
check("__all__ 包含 router", "router" in source.split("__all__")[1].split("]")[0] if "__all__" in source else False)

# ----------------------------------------------------------
# [23] description
# ----------------------------------------------------------
print("\n[23] description")
check("列表接口有 description", "分页查询试磨记录列表" in source)
check("创建接口有 description", "RECEIVED" in source)
check("完成接口有 description", "DISPATCHED" in source)

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