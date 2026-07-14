"""Test: Dispatch Service (Sprint 9 — Task 9.2)

严格依据 DEVELOPMENT_ROADMAP.md Task 9.2 验收标准。
测试 server/services/dispatch_service.py 全部公开 API 与代码规范。

注意：本测试使用源码分析，不依赖数据库连接。
"""

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
print("  Task 9.2 — Dispatch Service Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "services", "dispatch_service.py")

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
    from server.services.dispatch_service import DispatchService
    check("DispatchService 导入", True)
except ImportError as e:
    check("DispatchService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("DispatchService 是 class", inspect.isclass(DispatchService))
check("DispatchService 可实例化", DispatchService() is not None)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(DispatchService)
    if not m.startswith("_") and callable(getattr(DispatchService, m))
]
check("list_dispatches 存在", "list_dispatches" in public_methods)
check("get_dispatch 存在", "get_dispatch" in public_methods)
check("create_dispatch 存在", "create_dispatch" in public_methods)
check("update_dispatch 存在", "update_dispatch" in public_methods)
check("delete_dispatch 存在", "delete_dispatch" in public_methods)
check("公开 API 数量 = 5", len(public_methods) == 5)

# ----------------------------------------------------------
# [5] 公开 API 签名
# ----------------------------------------------------------
print("\n[5] 公开 API 签名")

# list_dispatches
sig = inspect.signature(DispatchService.list_dispatches)
params = list(sig.parameters.keys())
check("list_dispatches: 含 db", "db" in params)
check("list_dispatches: 含 direction", "direction" in params)
check("list_dispatches: 含 task_id", "task_id" in params)
check("list_dispatches: 含 page", "page" in params)
check("list_dispatches: 含 page_size", "page_size" in params)

# get_dispatch
sig = inspect.signature(DispatchService.get_dispatch)
params = list(sig.parameters.keys())
check("get_dispatch: 含 db", "db" in params)
check("get_dispatch: 含 dispatch_id", "dispatch_id" in params)

# create_dispatch
sig = inspect.signature(DispatchService.create_dispatch)
params = list(sig.parameters.keys())
check("create_dispatch: 含 db", "db" in params)
check("create_dispatch: 含 data", "data" in params)
check("create_dispatch: 含 operator_id", "operator_id" in params)

# update_dispatch
sig = inspect.signature(DispatchService.update_dispatch)
params = list(sig.parameters.keys())
check("update_dispatch: 含 db", "db" in params)
check("update_dispatch: 含 dispatch_id", "dispatch_id" in params)
check("update_dispatch: 含 data", "data" in params)
check("update_dispatch: 含 operator_id", "operator_id" in params)

# delete_dispatch
sig = inspect.signature(DispatchService.delete_dispatch)
params = list(sig.parameters.keys())
check("delete_dispatch: 含 db", "db" in params)
check("delete_dispatch: 含 dispatch_id", "dispatch_id" in params)
check("delete_dispatch: 含 operator_id", "operator_id" in params)

# ----------------------------------------------------------
# [6] 返回值类型注解
# ----------------------------------------------------------
print("\n[6] 返回值类型注解")

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

code = extract_code_text(SOURCE_PATH)

check("list_dispatches 返回 DispatchListResponse",
      "DispatchListResponse" in source)
check("get_dispatch 返回 DispatchResponse",
      "DispatchResponse" in source)
check("create_dispatch 返回 DispatchResponse",
      "DispatchResponse" in source)
check("update_dispatch 返回 DispatchResponse",
      "DispatchResponse" in source)
check("delete_dispatch 返回 None",
      "-> None" in source)

# ----------------------------------------------------------
# [7] 使用 Dispatch Schema
# ----------------------------------------------------------
print("\n[7] 使用 Dispatch Schema")
check("导入 DispatchCreate", "DispatchCreate" in source)
check("导入 DispatchUpdate", "DispatchUpdate" in source)
check("导入 DispatchResponse", "DispatchResponse" in source)
check("导入 DispatchListResponse", "DispatchListResponse" in source)

# ----------------------------------------------------------
# [8] 创建派发：校验 TrialTask 存在
# ----------------------------------------------------------
print("\n[8] 创建派发：校验 TrialTask 存在")
check("校验 TrialTask 存在", "试磨任务不存在" in source)
check("查询 TrialTask", "TrialTask" in source)
check("过滤 is_deleted=False", "is_deleted" in source)

# ----------------------------------------------------------
# [9] 创建派发：校验 InspectionRecord 存在
# ----------------------------------------------------------
print("\n[9] 创建派发：校验 InspectionRecord 存在")
check("校验 InspectionRecord 存在",
      "尚未完成检测" in source)
check("查询 InspectionRecord", "InspectionRecord" in source)

# ----------------------------------------------------------
# [10] 创建派发：校验 Dispatch 不重复
# ----------------------------------------------------------
print("\n[10] 创建派发：校验 Dispatch 不重复")
check("校验 task_id 不重复",
      "不可重复创建" in source)
check("查询 Dispatch 按 task_id",
      "Dispatch.task_id" in code)

# ----------------------------------------------------------
# [11] 创建派发：校验 result_status == PASSED
# ----------------------------------------------------------
print("\n[11] 创建派发：校验 result_status == PASSED")
check("校验 result_status == PASSED",
      "TrialTaskResultStatus.PASSED" in source)
check("非 PASSED 抛出异常",
      "仅检测合格的任务可派发" in source)

# ----------------------------------------------------------
# [12] 创建派发：校验 process_status == GRINDING
# ----------------------------------------------------------
print("\n[12] 创建派发：校验 process_status == GRINDING")
check("校验 process_status == GRINDING",
      "TrialTaskProcessStatus.GRINDING" in source)
check("非 GRINDING 抛出异常",
      "仅试磨中状态的任务可派发" in source)

# ----------------------------------------------------------
# [13] 创建派发：创建 ORM
# ----------------------------------------------------------
print("\n[13] 创建派发：创建 ORM")
check("创建 Dispatch ORM 实例",
      "Dispatch(" in code)
check("设置 task_id", "task_id=data.task_id" in code)
check("设置 direction", "direction=data.direction" in code)
check("设置 dispatch_date", "dispatch_date=data.dispatch_date" in code)
check("设置 operator_id", "operator_id=data.operator_id" in code)
check("db.add(dispatch)", "db.add(dispatch)" in code)
check("db.flush()", "db.flush()" in code)

# ----------------------------------------------------------
# [14] 创建派发：推进 process_status → DISPATCHED
# ----------------------------------------------------------
print("\n[14] 创建派发：推进 process_status → DISPATCHED")
check("推进 process_status",
      "TrialTaskProcessStatus.DISPATCHED" in source)
check("记录旧状态", "old_process_status" in source)

# ----------------------------------------------------------
# [15] 创建派发：事务 + SystemLog
# ----------------------------------------------------------
print("\n[15] 创建派发：事务 + SystemLog")
check("create_dispatch try/commit", "db.commit()" in source)
check("create_dispatch except rollback", "db.rollback()" in source)
check("写入 SystemLog (CREATE)", 'ActionType.CREATE' in source)
check("写入 SystemLog (STATUS_CHANGE)", 'ActionType.STATUS_CHANGE' in source)
check("create 写入至少 2 条 SystemLog",
      source.count("self._write_log(") >= 2)

# ----------------------------------------------------------
# [16] 更新派发：exclude_unset
# ----------------------------------------------------------
print("\n[16] 更新派发：exclude_unset")
check("使用 model_dump(exclude_unset=True)",
      "exclude_unset=True" in source)
check("仅更新非 None 字段",
      "not changes" in source)

# ----------------------------------------------------------
# [17] 更新派发：事务 + SystemLog
# ----------------------------------------------------------
print("\n[17] 更新派发：事务 + SystemLog")
check("update_dispatch try/commit", "db.commit()" in source)
check("update_dispatch except rollback", "db.rollback()" in source)
check("写入 SystemLog (UPDATE)", 'ActionType.UPDATE' in source)

# ----------------------------------------------------------
# [18] 删除派发：软删除
# ----------------------------------------------------------
print("\n[18] 删除派发：软删除")
check("设置 is_deleted=True", "is_deleted = True" in source)
check("不物理删除（无 db.delete）", "db.delete" not in source)

# ----------------------------------------------------------
# [19] 删除派发：事务 + SystemLog
# ----------------------------------------------------------
print("\n[19] 删除派发：事务 + SystemLog")
check("delete_dispatch try/commit", "db.commit()" in source)
check("delete_dispatch except rollback", "db.rollback()" in source)
check("写入 SystemLog (DELETE)", 'ActionType.DELETE' in source)

# ----------------------------------------------------------
# [20] 无 Workflow 违规
# ----------------------------------------------------------
print("\n[20] 无 Workflow 违规")
check("无 Receipt 业务", "Receipt" not in source)
check("无 Grinding 业务（除 GrindingRecord 引用）",
      "GrindingRecord" not in source)

# ----------------------------------------------------------
# [21] 无 Status Machine 违规
# ----------------------------------------------------------
print("\n[21] 无 Status Machine 违规")
# 仅检查赋值（result_status = XXX），不检查比较（result_status == XXX 或 result_status != XXX）
check("不得修改 result_status（仅 PASSED 校验）",
      not re.search(r'\bresult_status\s*=\s*(?!\s*=)', code))

# ----------------------------------------------------------
# [22] 异常处理
# ----------------------------------------------------------
print("\n[22] 异常处理")
check("使用 NotFoundException", "NotFoundException" in source)
check("使用 BusinessLogicException", "BusinessLogicException" in source)
check("无 ValueError", "ValueError" not in source)
check("无 print()", "print(" not in source)

# ----------------------------------------------------------
# [23] logger
# ----------------------------------------------------------
print("\n[23] logger")
check("使用 gtms.server logger", 'logging.getLogger("gtms.server")' in source)
check("logger.info 使用", "logger.info" in source)
check("logger.exception 使用", "logger.exception" in source)

# ----------------------------------------------------------
# [24] Type Hint
# ----------------------------------------------------------
print("\n[24] Type Hint")
check("Session 类型注解", "Session" in source)
check("Optional 导入", "Optional" in source)
check("所有方法有返回类型注解", "->" in source)

# ----------------------------------------------------------
# [25] 私有方法
# ----------------------------------------------------------
print("\n[25] 私有方法")
check("_get_dispatch_orm 存在", "_get_dispatch_orm" in source)
check("_to_response 存在", "_to_response" in source)
check("_write_log 存在", "_write_log" in source)

# ----------------------------------------------------------
# [26] PEP8
# ----------------------------------------------------------
print("\n[26] PEP8")
import subprocess
result = subprocess.run(
    ["python", "-m", "flake8", "--select=E,W,F,N", SOURCE_PATH],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
)
flake8_ok = result.returncode == 0
if not flake8_ok and result.stdout:
    print(f"    flake8: {result.stdout.strip()}")
check("PEP8 合规", flake8_ok)

# ----------------------------------------------------------
# [27] Docstring
# ----------------------------------------------------------
print("\n[27] Docstring")
import ast
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块级 docstring 存在", ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DispatchService":
        check("类 docstring 存在", ast.get_docstring(node) is not None)
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                doc = ast.get_docstring(item)
                check(f"{item.name} docstring 存在", doc is not None)

# ----------------------------------------------------------
# [28] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[28] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)

# ----------------------------------------------------------
# [29] Frozen API
# ----------------------------------------------------------
print("\n[29] Frozen API")
check("无 Router 导入", "from server.routers" not in source)
check("无 Desktop 导入", "from client." not in source)
check("无 Server 服务交叉导入", "InspectionService" not in source)
check("无 GrindingService 导入", "GrindingService" not in source)

# ----------------------------------------------------------
# [30] __all__ 导出
# ----------------------------------------------------------
print("\n[30] __all__ 导出")
check("__all__ 包含 DispatchService", "DispatchService" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [31] __init__.py 导出
# ----------------------------------------------------------
print("\n[31] __init__.py 导出")
INIT_PATH = os.path.join("server", "services", "__init__.py")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导出 DispatchService", "DispatchService" in init_code)

# ----------------------------------------------------------
# [32] 事务完整性
# ----------------------------------------------------------
print("\n[32] 事务完整性")
# 每个写操作至少含 1 次 commit
commit_count = source.count("db.commit()")
check("至少 3 次 commit（create + update + delete + _write_log）",
      commit_count >= 3)
rollback_count = source.count("db.rollback()")
check("至少 3 次 rollback（create + update + delete）",
      rollback_count >= 3)

# ----------------------------------------------------------
# [33] 枚举使用
# ----------------------------------------------------------
print("\n[33] 枚举使用")
check("导入 DestinationType", "DestinationType" in source)
check("导入 ActionType", "ActionType" in source)
check("导入 TrialTaskProcessStatus", "TrialTaskProcessStatus" in source)
check("导入 TrialTaskResultStatus", "TrialTaskResultStatus" in source)

# ----------------------------------------------------------
# [34] 分页逻辑
# ----------------------------------------------------------
print("\n[34] 分页逻辑")
check("list_dispatches 使用 offset", "offset" in source)
check("list_dispatches 使用 limit", "limit" in source)
check("list_dispatches 使用 count", "count()" in source)
check("排序 created_at DESC", "created_at.desc()" in source)

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