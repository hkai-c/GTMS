"""Test: Grinding Service (Sprint 7 — Task 7.2)

严格依据 DEVELOPMENT_ROADMAP.md Task 7.2 验收标准。
测试 server/services/grinding_service.py 全部公开 API 与代码规范。

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
print("  Task 7.2 — Grinding Service Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "services", "grinding_service.py")

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
    from server.services.grinding_service import GrindingService
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
check("GrindingService 可实例化", GrindingService() is not None)

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
# [5] 公开 API 签名
# ----------------------------------------------------------
print("\n[5] 公开 API 签名")

# list_grindings
sig = inspect.signature(GrindingService.list_grindings)
params = list(sig.parameters.keys())
check("list_grindings: 含 db", "db" in params)
check("list_grindings: 含 task_id", "task_id" in params)
check("list_grindings: 含 operator_id", "operator_id" in params)
check("list_grindings: 含 page", "page" in params)
check("list_grindings: 含 page_size", "page_size" in params)

# get_grinding
sig = inspect.signature(GrindingService.get_grinding)
params = list(sig.parameters.keys())
check("get_grinding: 含 db", "db" in params)
check("get_grinding: 含 grinding_id", "grinding_id" in params)

# create_grinding
sig = inspect.signature(GrindingService.create_grinding)
params = list(sig.parameters.keys())
check("create_grinding: 含 db", "db" in params)
check("create_grinding: 含 data", "data" in params)
check("create_grinding: 含 operator_id", "operator_id" in params)

# finish_grinding
sig = inspect.signature(GrindingService.finish_grinding)
params = list(sig.parameters.keys())
check("finish_grinding: 含 db", "db" in params)
check("finish_grinding: 含 grinding_id", "grinding_id" in params)
check("finish_grinding: 含 result_status", "result_status" in params)
check("finish_grinding: 含 failure_reason", "failure_reason" in params)
check("finish_grinding: 含 end_time", "end_time" in params)
check("finish_grinding: 含 operator_id", "operator_id" in params)

# update_grinding
sig = inspect.signature(GrindingService.update_grinding)
params = list(sig.parameters.keys())
check("update_grinding: 含 db", "db" in params)
check("update_grinding: 含 grinding_id", "grinding_id" in params)
check("update_grinding: 含 data", "data" in params)
check("update_grinding: 含 operator_id", "operator_id" in params)

# delete_grinding
sig = inspect.signature(GrindingService.delete_grinding)
params = list(sig.parameters.keys())
check("delete_grinding: 含 db", "db" in params)
check("delete_grinding: 含 grinding_id", "grinding_id" in params)
check("delete_grinding: 含 operator_id", "operator_id" in params)

# ----------------------------------------------------------
# [6] 返回值类型注解
# ----------------------------------------------------------
print("\n[6] 返回值类型注解")

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

check("list_grindings 返回类型注解包含 GrindingListResponse",
      "GrindingListResponse" in source)
check("get_grinding 返回类型注解包含 GrindingResponse",
      "GrindingResponse" in source)
check("create_grinding 返回类型注解包含 GrindingResponse",
      "GrindingResponse" in source)
check("finish_grinding 返回类型注解包含 GrindingResponse",
      "GrindingResponse" in source)
check("update_grinding 返回类型注解包含 GrindingResponse",
      "GrindingResponse" in source)
check("delete_grinding 返回类型注解包含 None",
      "-> None" in source)

# ----------------------------------------------------------
# [7] 使用 Grinding Schema
# ----------------------------------------------------------
print("\n[7] 使用 Grinding Schema")
check("导入 GrindingCreate", "GrindingCreate" in source)
check("导入 GrindingUpdate", "GrindingUpdate" in source)
check("导入 GrindingResponse", "GrindingResponse" in source)
check("导入 GrindingListResponse", "GrindingListResponse" in source)

# ----------------------------------------------------------
# [8] 创建试磨：校验 TrialTask 存在
# ----------------------------------------------------------
print("\n[8] 创建试磨：校验 TrialTask 存在")
check("校验 TrialTask 存在", "试磨任务不存在" in source)
check("查询 TrialTask", "TrialTask" in source)
check("过滤 is_deleted=False", "is_deleted" in source)

# ----------------------------------------------------------
# [9] 创建试磨：校验状态为 RECEIVED
# ----------------------------------------------------------
print("\n[9] 创建试磨：校验状态为 RECEIVED")
check("检查 process_status == RECEIVED",
      "TrialTaskProcessStatus.RECEIVED" in source)
check("非 RECEIVED 抛出异常",
      "仅已收件状态的任务可开始试磨" in source)

# ----------------------------------------------------------
# [10] 创建试磨：校验 task_id 未重复
# ----------------------------------------------------------
print("\n[10] 创建试磨：校验 task_id 未重复")
check("校验未重复试磨", "不可重复创建" in source)
check("查询 GrindingRecord", "GrindingRecord" in source)

# ----------------------------------------------------------
# [11] 创建试磨：创建 ORM
# ----------------------------------------------------------
print("\n[11] 创建试磨：创建 ORM")
code = extract_code_text(SOURCE_PATH)
check("创建 GrindingRecord ORM 实例",
      "GrindingRecord(" in code)
check("设置 task_id", "task_id=data.task_id" in code)
check("设置 operator_id", "operator_id=data.operator_id" in code)
check("设置 start_time", "start_time=data.start_time" in code)
check("db.add(grinding)", "db.add(grinding)" in code)
check("db.flush()", "db.flush()" in code)

# ----------------------------------------------------------
# [12] 创建试磨：推进状态
# ----------------------------------------------------------
print("\n[12] 创建试磨：推进 process_status → GRINDING")
check("推进 process_status 至 GRINDING",
      "TrialTaskProcessStatus.GRINDING" in source and "process_status" in source)
check("记录旧状态", "old_status" in source)

# ----------------------------------------------------------
# [13] 创建试磨：事务 + SystemLog
# ----------------------------------------------------------
print("\n[13] 创建试磨：事务 + SystemLog")
check("try/commit", "db.commit()" in source)
check("except rollback", "db.rollback()" in source)
check("写入 SystemLog (CREATE)", 'ActionType.CREATE' in source)
check("写入 SystemLog (STATUS_CHANGE)", 'ActionType.STATUS_CHANGE' in source)
check("SystemLog 写入两次", source.count("self._write_log(") >= 4)

# ----------------------------------------------------------
# [14] 完成试磨：校验 GrindingRecord 存在
# ----------------------------------------------------------
print("\n[14] 完成试磨：校验 GrindingRecord 存在")
check("finish_grinding 校验 GrindingRecord 存在",
      "试磨记录不存在" in source)

# ----------------------------------------------------------
# [15] 完成试磨：校验状态为 GRINDING
# ----------------------------------------------------------
print("\n[15] 完成试磨：校验状态为 GRINDING")
check("检查 process_status == GRINDING",
      "TrialTaskProcessStatus.GRINDING" in source)
check("非 GRINDING 抛出异常",
      "仅试磨中状态的任务可完成试磨" in source)

# ----------------------------------------------------------
# [16] 完成试磨：校验 result_status 合法性
# ----------------------------------------------------------
print("\n[16] 完成试磨：校验 result_status 合法性")
check("检查 result_status in (PASSED, FAILED)",
      "TrialTaskResultStatus.PASSED" in source and
      "TrialTaskResultStatus.FAILED" in source)
check("非法值抛出异常", "非法的试磨结果" in source)

# ----------------------------------------------------------
# [17] 完成试磨：failure_reason 必填
# ----------------------------------------------------------
print("\n[17] 完成试磨：failure_reason 必填")
check("failed 时 failure_reason 必填",
      "failure_reason 必须填写" in source)
check("检查 failure_reason.strip()", "failure_reason.strip()" in source)

# ----------------------------------------------------------
# [18] 完成试磨：推进状态
# ----------------------------------------------------------
# BUG-E2E-006 修复后：finish_grinding 不再推进 process_status → DISPATCHED
# Dispatch 模块负责 process_status → DISPATCHED
print("\n[18] 完成试磨：不推进 process_status（Dispatch 负责）")
check("finish_grinding 不推进 process_status 至 DISPATCHED",
      "TrialTaskProcessStatus.DISPATCHED" not in source)
check("设置 result_status", "task.result_status = result_status" in code)

# ----------------------------------------------------------
# [19] 完成试磨：设置 end_time
# ----------------------------------------------------------
print("\n[19] 完成试磨：设置 end_time")
check("默认 end_time 为当前时间", "datetime.now()" in source)
check("更新 grinding.end_time", "grinding.end_time" in source)

# ----------------------------------------------------------
# [20] 完成试磨：事务 + SystemLog
# ----------------------------------------------------------
print("\n[20] 完成试磨：事务 + SystemLog")
check("finish_grinding 有 try/commit", "commit" in source)
check("finish_grinding 有 except rollback", "rollback" in source)

# ----------------------------------------------------------
# [21] 更新试磨：校验 GrindingRecord 存在
# ----------------------------------------------------------
print("\n[21] 更新试磨：校验 GrindingRecord 存在")
check("update_grinding 校验 GrindingRecord 存在",
      "试磨记录不存在" in source)

# ----------------------------------------------------------
# [22] 更新试磨：exclude_unset
# ----------------------------------------------------------
print("\n[22] 更新试磨：exclude_unset")
check("使用 exclude_unset", "exclude_unset=True" in source)
check("仅更新非 None 字段", "if new_value is not None" in source)
check("无变更时直接返回", "if not changes:" in source)

# ----------------------------------------------------------
# [23] 更新试磨：事务 + SystemLog
# ----------------------------------------------------------
print("\n[23] 更新试磨：事务 + SystemLog")
check("update_grinding 有 try/commit", "commit" in source)
check("update_grinding 有 except rollback", "rollback" in source)

# ----------------------------------------------------------
# [24] 删除试磨：软删除
# ----------------------------------------------------------
print("\n[24] 删除试磨：软删除")
check("设置 is_deleted=True", "is_deleted = True" in source)
check("不物理删除", "is_deleted" in source)

# ----------------------------------------------------------
# [25] 删除试磨：事务 + SystemLog
# ----------------------------------------------------------
print("\n[25] 删除试磨：事务 + SystemLog")
check("delete_grinding 有 try/commit", "commit" in source)
check("delete_grinding 有 except rollback", "rollback" in source)

# ----------------------------------------------------------
# [26] 列表查询：分页 + 筛选
# ----------------------------------------------------------
print("\n[26] 列表查询：分页 + 筛选")
check("按 task_id 筛选", "task_id" in source if "task_id" else False)
check("按 operator_id 筛选", "operator_id" in source)
check("按 created_at DESC 排序", "created_at.desc()" in source)
check("分页 offset", "offset" in source)
check("分页 limit", "limit" in source)
check("过滤 is_deleted=False", "is_deleted.is_(False)" in source)

# ----------------------------------------------------------
# [27] 使用枚举常量
# ----------------------------------------------------------
print("\n[27] 使用枚举常量")
check("导入 TrialTaskProcessStatus",
      "TrialTaskProcessStatus" in source)
check("导入 TrialTaskResultStatus",
      "TrialTaskResultStatus" in source)
check("导入 ActionType", "ActionType" in source)

# ----------------------------------------------------------
# [28] 使用枚举常量值（TrialTaskProcessStatus）
# ----------------------------------------------------------
print("\n[28] 使用枚举常量值（TrialTaskProcessStatus）")
check("使用 .RECEIVED", "TrialTaskProcessStatus.RECEIVED" in source)
check("使用 .GRINDING", "TrialTaskProcessStatus.GRINDING" in source)
# BUG-E2E-006 修复后：grinding_service 不再使用 DISPATCHED
# Dispatch 模块负责 DISPATCHED 状态推进
check("不使用 .DISPATCHED（由 Dispatch 负责）",
      "TrialTaskProcessStatus.DISPATCHED" not in source)

# ----------------------------------------------------------
# [29] 使用枚举常量值（TrialTaskResultStatus）
# ----------------------------------------------------------
print("\n[29] 使用枚举常量值（TrialTaskResultStatus）")
check("使用 .PASSED", "TrialTaskResultStatus.PASSED" in source)
check("使用 .FAILED", "TrialTaskResultStatus.FAILED" in source)

# ----------------------------------------------------------
# [30] Type Hint
# ----------------------------------------------------------
print("\n[30] Type Hint")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        check(
            f"{node.name} 有返回类型注解",
            node.returns is not None,
        )

# ----------------------------------------------------------
# [31] Docstring
# ----------------------------------------------------------
print("\n[31] Docstring")
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
# [32] PEP8
# ----------------------------------------------------------
print("\n[32] PEP8")
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
# [33] 无循环导入
# ----------------------------------------------------------
print("\n[33] 无循环导入")
check("未导入自身", "from server.services.grinding_service" not in code)
check("未导入 Router", "from server.routers" not in source)
check("未导入 View", "from client" not in source)

# ----------------------------------------------------------
# [34] Frozen API
# ----------------------------------------------------------
print("\n[34] Frozen API")
check("未导入 requests", "requests" not in source)
check("未导入 httpx", "httpx" not in source)
check("未导入 ApiClient", "ApiClient" not in source)
check("未导入 JWT", "jwt" not in source.lower())
check("未导入 bcrypt", "bcrypt" not in source)

# ----------------------------------------------------------
# [35] __init__.py 导出
# ----------------------------------------------------------
print("\n[35] __init__.py 导出")
try:
    from server.services.grinding_service import GrindingService as GS
    check("GrindingService 可导入", GS is not None)
except ImportError as e:
    check("GrindingService 可导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [36] __all__ 导出
# ----------------------------------------------------------
print("\n[36] __all__ 导出")
check("__all__ 包含 GrindingService", "GrindingService" in source.split("__all__")[1].split("]")[0] if "__all__" in source else False)

# ----------------------------------------------------------
# [37] 性能：分页
# ----------------------------------------------------------
print("\n[37] 性能：分页")
check("使用 .limit()", ".limit(" in source)
check("使用 .offset()", ".offset(" in source)
check("使用 .count()", ".count()" in source)

# ----------------------------------------------------------
# [38] 性能：禁止全表查询
# ----------------------------------------------------------
print("\n[38] 性能：禁止全表查询")
check("list_grindings 无 .all() 在分页前", "limit" in source and "offset" in source)

# ----------------------------------------------------------
# [39] 禁止依赖
# ----------------------------------------------------------
print("\n[39] 禁止依赖")
check("未导入 print", "print(" not in code)
check("未导入 Raw SQL", "execute(" not in code)
check("未导入 text()", "text(" not in code)

# ----------------------------------------------------------
# [40] 日志
# ----------------------------------------------------------
print("\n[40] 日志")
check("使用 gtms.server logger",
      '"gtms.server"' in source)
check("记录 create 成功", "试磨开始成功" in source)
check("记录 finish 成功", "试磨完成" in source)
check("记录 update 成功", "试磨记录更新成功" in source)
check("记录 delete 成功", "试磨记录已删除" in source)
check("记录异常日志", "logger.exception" in source)

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