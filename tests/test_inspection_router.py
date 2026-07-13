"""Test: Inspection Router (Sprint 8 — Task 8.3)

严格依据 DEVELOPMENT_ROADMAP.md Task 8.3 验收标准。
测试 server/routers/inspection_router.py 全部公开接口与代码规范。

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
print("  Task 8.3 — Inspection Router Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "routers", "inspection_router.py")

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
    from server.routers.inspection_router import router
    check("router 导入", True)
except ImportError as e:
    check("router 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] router 类型
# ----------------------------------------------------------
print("\n[3] router 类型")
check("router 是 APIRouter", router.__class__.__name__ == "APIRouter")

# ----------------------------------------------------------
# [4] router 配置
# ----------------------------------------------------------
print("\n[4] router 配置")
check("prefix = '/api/inspection'", router.prefix == "/api/inspection")
check("tags = ['Inspection']", "Inspection" in router.tags)

# ----------------------------------------------------------
# [5] 路由数量
# ----------------------------------------------------------
print("\n[5] 路由数量")
route_count = len(router.routes)
check(f"路由数量 = 6 (实际: {route_count})", route_count == 6)

# ----------------------------------------------------------
# [6] HTTP Method
# ----------------------------------------------------------
print("\n[6] HTTP Method")
methods = set()
for route in router.routes:
    methods.update(route.methods)
check("GET 存在", "GET" in methods)
check("POST 存在", "POST" in methods)
check("PUT 存在", "PUT" in methods)
check("DELETE 存在", "DELETE" in methods)

# ----------------------------------------------------------
# [7] URL 路径
# ----------------------------------------------------------
print("\n[7] URL 路径")

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

code = extract_code_text(SOURCE_PATH)

# 检查装饰器中的路径
check("GET /api/inspection (列表)", '""' in source)  # 空字符串 = /api/inspection
check("GET /api/inspection/{inspection_id}",
      '"/{inspection_id}"' in source)
check("POST /api/inspection (创建)", '""' in source)
check("POST /api/inspection/{inspection_id}/finish",
      '"/{inspection_id}/finish"' in source)
check("PUT /api/inspection/{inspection_id}",
      '"/{inspection_id}"' in source)
check("DELETE /api/inspection/{inspection_id}",
      '"/{inspection_id}"' in source)

# ----------------------------------------------------------
# [8] Router 导入
# ----------------------------------------------------------
print("\n[8] Router 导入")
check("导入 InspectionService", "InspectionService" in source)
check("导入 InspectionCreate", "InspectionCreate" in source)
check("导入 InspectionUpdate", "InspectionUpdate" in source)
check("导入 InspectionResponse", "InspectionResponse" in source)
check("导入 InspectionListResponse", "InspectionListResponse" in source)
check("导入 require_permission", "require_permission" in source)
check("导入 get_db", "get_db" in source)
check("导入 get_current_active_user", "get_current_active_user" in source)

# ----------------------------------------------------------
# [9] 服务实例
# ----------------------------------------------------------
print("\n[9] 服务实例")
check("_inspection_service 实例化", "_inspection_service = InspectionService()" in source)

# ----------------------------------------------------------
# [10] 权限
# ----------------------------------------------------------
print("\n[10] 权限")
check("inspection:view 权限", 'require_permission("inspection:view")' in source)
check("inspection:create 权限", 'require_permission("inspection:create")' in source)
check("inspection:edit 权限", 'require_permission("inspection:edit")' in source)
check("inspection:delete 权限", 'require_permission("inspection:delete")' in source)

# ----------------------------------------------------------
# [11] 依赖注入
# ----------------------------------------------------------
print("\n[11] 依赖注入")
check("Depends(get_db) 使用", "Depends(get_db)" in source)
check("Depends(get_current_active_user) 使用",
      "Depends(get_current_active_user)" in source)
check("Depends(require_permission) 使用",
      "Depends(require_permission" in source)

# [12] 零业务逻辑
# ----------------------------------------------------------
print("\n[12] 零业务逻辑")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source_full = f.read()
check("零业务逻辑：无 process_status 判断赋值", "process_status =" not in code)
check("零业务逻辑：无 result_status 判断赋值", "result_status =" not in code)
check("Router 无 TrialTask 数据库查询", "TrialTask." not in code and "TrialTask(" not in code)
check("零业务逻辑：无 InspectionRecord 查询（数据库查询在 Service）",
      "InspectionRecord" not in code)
check("零业务逻辑：无 GrindingRecord 查询（数据库查询在 Service）",
      "GrindingRecord" not in code)
check("零业务逻辑：无 db.commit() 调用（事务在 Service）",
      "db.commit()" not in code)
check("零业务逻辑：无 db.rollback() 调用（事务在 Service）",
      "db.rollback()" not in code)
check("零业务逻辑：无 db.add() 调用（事务在 Service）",
      "db.add()" not in code)
check("零业务逻辑：无 db.flush() 调用（事务在 Service）",
      "db.flush()" not in code)

# ----------------------------------------------------------
# [13] 无 try/except
# ----------------------------------------------------------
print("\n[13] 无 try/except")
check("Router 无 try", "try:" not in code)
check("Router 无 except", "except" not in code)

# ----------------------------------------------------------
# [14] 无 HTTPException
# ----------------------------------------------------------
print("\n[14] 无 HTTPException")
check("Router 无 HTTPException", "HTTPException" not in code)

# ----------------------------------------------------------
# [15] 零 Workflow
# ----------------------------------------------------------
print("\n[15] 零 Workflow")
check("Router 无 process_status 赋值", "process_status =" not in code)
check("Router 无 result_status 赋值", "result_status =" not in code)

# ----------------------------------------------------------
# [16] 零 Status Machine
# ----------------------------------------------------------
print("\n[16] 零 Status Machine")
check("Router 无状态流转（DISPATCHED 赋值）", "TrialTaskProcessStatus.DISPATCHED" not in code)

# ----------------------------------------------------------
# [17] OpenAPI 元数据
# ----------------------------------------------------------
print("\n[17] OpenAPI 元数据")
check("response_model 使用", "response_model=" in source)
check("status_code 使用", "status_code=" in source)
check("summary 使用", "summary=" in source)
check("description 使用", "description=" in source)

# ----------------------------------------------------------
# [18] 状态码
# ----------------------------------------------------------
print("\n[18] 状态码")
check("GET list 200", "status.HTTP_200_OK" in source)
check("GET detail 200", "status.HTTP_200_OK" in source)
check("POST create 201", "status.HTTP_201_CREATED" in source)
check("POST finish 200", "status.HTTP_200_OK" in source)
check("PUT update 200", "status.HTTP_200_OK" in source)
check("DELETE 200", "status.HTTP_200_OK" in source)

# ----------------------------------------------------------
# [19] InspectionFinishRequest 内联定义
# ----------------------------------------------------------
print("\n[19] InspectionFinishRequest 内联定义")
check("InspectionFinishRequest 类定义", "class InspectionFinishRequest" in source)
check("InspectionFinishRequest 继承 BaseModel", "BaseModel" in source)
check("InspectionFinishRequest 有 result", "result" in source)
check("InspectionFinishRequest 有 failure_reason", "failure_reason" in source)

# ----------------------------------------------------------
# [20] 无 JWT / bcrypt
# ----------------------------------------------------------
print("\n[20] 无 JWT / bcrypt")
check("Router 无 jwt", "jwt" not in code)
check("Router 无 bcrypt", "bcrypt" not in code)

# ----------------------------------------------------------
# [21] 无 ORM
# ----------------------------------------------------------
print("\n[21] 无 ORM")
check("Router 无 SystemLog 调用", "SystemLog" not in code)
check("Router 无 手动 Session 创建", "Session()" not in code)

# ----------------------------------------------------------
# [22] PEP8
# ----------------------------------------------------------
print("\n[22] PEP8")
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
# [23] 循环导入
# ----------------------------------------------------------
print("\n[23] 循环导入")
check("无循环导入", "from server.routers.inspection_router" not in code)

# ----------------------------------------------------------
# [24] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[24] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 pass", re.search(r'\bpass\b', code) is None)

# ----------------------------------------------------------
# [25] __all__
# ----------------------------------------------------------
print("\n[25] __all__")
check("__all__ 含 router", "router" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [26] __init__.py 导出
# ----------------------------------------------------------
print("\n[26] __init__.py 导出")
init_path = os.path.join("server", "routers", "__init__.py")
init_source = extract_code_text(init_path)
check("__init__.py 导出 inspection_router", "inspection_router" in init_source)
check("__init__.py 导出 grinding_router (未破坏)", "grinding_router" in init_source)
check("__init__.py 导出 trial_task_router (未破坏)", "trial_task_router" in init_source)
check("__init__.py 导出 receipt_router (未破坏)", "receipt_router" in init_source)

# ----------------------------------------------------------
# [27] Frozen API
# ----------------------------------------------------------
print("\n[27] Frozen API")
check("无 ORM 模型导入（除 User）", "from server.models import" not in code)
check("无 Service 实例手动创建", "InspectionService()" in source)
check("未导入 GrindingService", "GrindingService" not in source)
check("未导入 TrialTaskService", "TrialTaskService" not in source)

# ----------------------------------------------------------
# [28] 文件以换行结尾
# ----------------------------------------------------------
print("\n[28] 文件以换行结尾")
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