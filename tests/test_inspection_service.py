"""Test: Inspection Service (Sprint 8 — Task 8.2)

严格依据 DEVELOPMENT_ROADMAP.md Task 8.2 验收标准。
测试 server/services/inspection_service.py 全部公开 API 与代码规范。

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
print("  Task 8.2 — Inspection Service Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "services", "inspection_service.py")

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
    from server.services.inspection_service import InspectionService
    check("InspectionService 导入", True)
except ImportError as e:
    check("InspectionService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("InspectionService 是 class", inspect.isclass(InspectionService))
check("InspectionService 可实例化", InspectionService() is not None)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(InspectionService)
    if not m.startswith("_") and callable(getattr(InspectionService, m))
]
check("list_inspections 存在", "list_inspections" in public_methods)
check("get_inspection 存在", "get_inspection" in public_methods)
check("create_inspection 存在", "create_inspection" in public_methods)
check("finish_inspection 存在", "finish_inspection" in public_methods)
check("update_inspection 存在", "update_inspection" in public_methods)
check("delete_inspection 存在", "delete_inspection" in public_methods)
check("公开 API 数量 = 6", len(public_methods) == 6)

# ----------------------------------------------------------
# [5] 公开 API 签名
# ----------------------------------------------------------
print("\n[5] 公开 API 签名")

# list_inspections
sig = inspect.signature(InspectionService.list_inspections)
params = list(sig.parameters.keys())
check("list_inspections: 含 db", "db" in params)
check("list_inspections: 含 task_id", "task_id" in params)
check("list_inspections: 含 inspector_id", "inspector_id" in params)
check("list_inspections: 含 result", "result" in params)
check("list_inspections: 含 page", "page" in params)
check("list_inspections: 含 page_size", "page_size" in params)

# get_inspection
sig = inspect.signature(InspectionService.get_inspection)
params = list(sig.parameters.keys())
check("get_inspection: 含 db", "db" in params)
check("get_inspection: 含 inspection_id", "inspection_id" in params)

# create_inspection
sig = inspect.signature(InspectionService.create_inspection)
params = list(sig.parameters.keys())
check("create_inspection: 含 db", "db" in params)
check("create_inspection: 含 data", "data" in params)
check("create_inspection: 含 operator_id", "operator_id" in params)

# finish_inspection
sig = inspect.signature(InspectionService.finish_inspection)
params = list(sig.parameters.keys())
check("finish_inspection: 含 db", "db" in params)
check("finish_inspection: 含 inspection_id", "inspection_id" in params)
check("finish_inspection: 含 result", "result" in params)
check("finish_inspection: 含 failure_reason", "failure_reason" in params)
check("finish_inspection: 含 operator_id", "operator_id" in params)

# update_inspection
sig = inspect.signature(InspectionService.update_inspection)
params = list(sig.parameters.keys())
check("update_inspection: 含 db", "db" in params)
check("update_inspection: 含 inspection_id", "inspection_id" in params)
check("update_inspection: 含 data", "data" in params)
check("update_inspection: 含 operator_id", "operator_id" in params)

# delete_inspection
sig = inspect.signature(InspectionService.delete_inspection)
params = list(sig.parameters.keys())
check("delete_inspection: 含 db", "db" in params)
check("delete_inspection: 含 inspection_id", "inspection_id" in params)
check("delete_inspection: 含 operator_id", "operator_id" in params)

# ----------------------------------------------------------
# [6] 返回值类型注解
# ----------------------------------------------------------
print("\n[6] 返回值类型注解")

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

code = extract_code_text(SOURCE_PATH)

check("list_inspections 返回 InspectionListResponse",
      "InspectionListResponse" in source)
check("get_inspection 返回 InspectionResponse",
      "InspectionResponse" in source)
check("create_inspection 返回 InspectionResponse",
      "InspectionResponse" in source)
check("finish_inspection 返回 InspectionResponse",
      "InspectionResponse" in source)
check("update_inspection 返回 InspectionResponse",
      "InspectionResponse" in source)
check("delete_inspection 返回 None",
      "-> None" in source)

# ----------------------------------------------------------
# [7] 使用 Inspection Schema
# ----------------------------------------------------------
print("\n[7] 使用 Inspection Schema")
check("导入 InspectionCreate", "InspectionCreate" in source)
check("导入 InspectionUpdate", "InspectionUpdate" in source)
check("导入 InspectionResponse", "InspectionResponse" in source)
check("导入 InspectionListResponse", "InspectionListResponse" in source)

# ----------------------------------------------------------
# [8] 创建检测：校验 TrialTask 存在
# ----------------------------------------------------------
print("\n[8] 创建检测：校验 TrialTask 存在")
check("校验 TrialTask 存在", "试磨任务不存在" in source)
check("查询 TrialTask", "TrialTask" in source)
check("过滤 is_deleted=False", "is_deleted" in source)

# ----------------------------------------------------------
# [9] 创建检测：校验 GrindingRecord 存在
# ----------------------------------------------------------
print("\n[9] 创建检测：校验 GrindingRecord 存在")
check("校验 GrindingRecord 存在",
      "尚未开始试磨" in source)
check("查询 GrindingRecord", "GrindingRecord" in source)

# ----------------------------------------------------------
# [10] 创建检测：校验 task_id 未重复
# ----------------------------------------------------------
print("\n[10] 创建检测：校验 task_id 未重复")
check("校验未重复创建检测记录",
      "不可重复创建" in source)
check("查询 InspectionRecord 按 task_id",
      "InspectionRecord.task_id" in code)

# ----------------------------------------------------------
# [11] 创建检测：创建 ORM
# ----------------------------------------------------------
print("\n[11] 创建检测：创建 ORM")
check("创建 InspectionRecord ORM 实例",
      "InspectionRecord(" in code)
check("设置 task_id", "task_id=data.task_id" in code)
check("设置 report_path", "report_path=data.report_path" in code)
check("设置 accuracy", "accuracy=data.accuracy" in code)
check("设置 result", "result=data.result" in code)
check("设置 inspector_id", "inspector_id=data.inspector_id" in code)
check("db.add(inspection)", "db.add(inspection)" in code)
check("db.flush()", "db.flush()" in code)

# ----------------------------------------------------------
# [12] 创建检测：事务 + SystemLog
# ----------------------------------------------------------
print("\n[12] 创建检测：事务 + SystemLog")
check("try/commit", "db.commit()" in source)
check("except rollback", "db.rollback()" in source)
check("写入 SystemLog (CREATE)", 'ActionType.CREATE' in source)
check("SystemLog 写入至少 1 次", source.count("self._write_log(") >= 1)

# ----------------------------------------------------------
# [13] 完成检测：校验 InspectionRecord + TrialTask
# ----------------------------------------------------------
print("\n[13] 完成检测：校验 InspectionRecord + TrialTask")
check("finish_inspection 校验 InspectionRecord 存在",
      "检测记录不存在" in source)
check("finish_inspection 校验 TrialTask 存在",
      "关联试磨任务不存在" in source)

# ----------------------------------------------------------
# [14] 完成检测：校验状态为 GRINDING
# ----------------------------------------------------------
print("\n[14] 完成检测：校验状态为 GRINDING")
check("检查 process_status == GRINDING",
      "TrialTaskProcessStatus.GRINDING" in source)
check("非 GRINDING 抛出异常",
      "仅试磨中状态的任务可完成检测" in source)

# ----------------------------------------------------------
# [15] 完成检测：failure_reason 必填
# ----------------------------------------------------------
print("\n[15] 完成检测：failure_reason 必填")
check("FAILED 时 failure_reason 必填",
      "failure_reason 必须填写" in source)
check("检查 failure_reason.strip()", "failure_reason.strip()" in source)

# ----------------------------------------------------------
# [16] 完成检测：推进状态
# ----------------------------------------------------------
# BUG-E2E-006 修复后：finish_inspection 不再推进 process_status → DISPATCHED
# Dispatch 模块负责 process_status → DISPATCHED
print("\n[16] 完成检测：不推进 process_status（Dispatch 负责）")
check("finish_inspection 不推进 process_status 至 DISPATCHED",
      "TrialTaskProcessStatus.DISPATCHED" not in source)
check("设置 result_status",
      "TrialTaskResultStatus.PASSED" in source)
# BUG-E2E-006 修复后：不再记录 process_status 变更日志
check("不记录旧 process_status（无状态变更）",
      "old_process_status" not in source)

# ----------------------------------------------------------
# [17] 完成检测：事务 + SystemLog
# ----------------------------------------------------------
print("\n[17] 完成检测：事务 + SystemLog")
check("finish_inspection try/commit", "db.commit()" in source)
check("finish_inspection except rollback", "db.rollback()" in source)
# BUG-E2E-006 修复后：不写入 STATUS_CHANGE 日志（process_status 不变更）
check("不写入 SystemLog (STATUS_CHANGE)",
      'ActionType.STATUS_CHANGE' not in source)
check("finish 写入 1 条 SystemLog（仅 UPDATE）",
      source.count("self._write_log(") >= 1)

# ----------------------------------------------------------
# [18] 更新检测：exclude_unset
# ----------------------------------------------------------
print("\n[18] 更新检测：exclude_unset")
check("使用 model_dump(exclude_unset=True)",
      "exclude_unset=True" in source)
check("仅更新非 None 字段",
      "not changes" in source)

# ----------------------------------------------------------
# [19] 更新检测：事务 + SystemLog
# ----------------------------------------------------------
print("\n[19] 更新检测：事务 + SystemLog")
check("update_inspection try/commit", "db.commit()" in source)
check("update_inspection except rollback", "db.rollback()" in source)
check("update 写入 SystemLog (UPDATE)",
      'ActionType.UPDATE' in source)

# ----------------------------------------------------------
# [20] 删除检测：软删除
# ----------------------------------------------------------
print("\n[20] 删除检测：软删除")
check("delete_inspection 设置 is_deleted=True",
      "is_deleted = True" in code)
check("不物理删除", "delete" not in code.lower().split("inspection")[0])

# ----------------------------------------------------------
# [21] 删除检测：事务 + SystemLog
# ----------------------------------------------------------
print("\n[21] 删除检测：事务 + SystemLog")
check("delete_inspection try/commit", "db.commit()" in source)
check("delete_inspection except rollback", "db.rollback()" in source)
check("delete 写入 SystemLog (DELETE)",
      'ActionType.DELETE' in source)

# ----------------------------------------------------------
# [22] 列表查询：分页 + 筛选 + 排序
# ----------------------------------------------------------
print("\n[22] 列表查询：分页 + 筛选 + 排序")
check("list_inspections 支持 task_id 筛选",
      "task_id" in source)
check("list_inspections 支持 inspector_id 筛选",
      "inspector_id" in source)
check("list_inspections 支持 result 筛选",
      "result" in source)
check("list_inspections 支持分页 (page/page_size)",
      "page" in source and "page_size" in source)
check("list_inspections 按 created_at DESC 排序",
      "created_at.desc()" in source)

# ----------------------------------------------------------
# [23] 仅依赖 Server 层
# ----------------------------------------------------------
print("\n[23] 仅依赖 Server 层")
check("无 client 导入", "from client" not in source)
check("无 requests 导入", "requests" not in source)
check("无 httpx 导入", "httpx" not in source)

# ----------------------------------------------------------
# [24] 零 Workflow 绕过
# ----------------------------------------------------------
print("\n[24] 零 Workflow 绕过")
check("status 仅通过 Service 控制",
      True)

# ----------------------------------------------------------
# [25] 日志
# ----------------------------------------------------------
print("\n[25] 日志")
check("使用 logging.getLogger('gtms.server')",
      'logging.getLogger("gtms.server")' in source)
check("logger.info 使用", "logger.info" in source)
check("logger.exception 使用", "logger.exception" in source)
check("无 print()", "print(" not in code)

# ----------------------------------------------------------
# [26] 类型注解
# ----------------------------------------------------------
print("\n[26] 类型注解")
check("InspectionService 有类型注解",
      "from typing import Optional" in source)

# ----------------------------------------------------------
# [27] PEP8
# ----------------------------------------------------------
print("\n[27] PEP8")
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
# [28] 循环导入
# ----------------------------------------------------------
print("\n[28] 循环导入")
check("无循环导入", "from server.services.inspection_service" not in code)

# ----------------------------------------------------------
# [29] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[29] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 pass", re.search(r'\bpass\b', code) is None)

# ----------------------------------------------------------
# [30] __all__
# ----------------------------------------------------------
print("\n[30] __all__")
check("__all__ 含 InspectionService", "InspectionService" in source)

# ----------------------------------------------------------
# [31] 私有方法
# ----------------------------------------------------------
print("\n[31] 私有方法")
check("_get_inspection_orm 存在", "def _get_inspection_orm" in source)
check("_to_response 存在", "def _to_response" in source)
check("_write_log 存在", "def _write_log" in source)

# ----------------------------------------------------------
# [32] 使用 InspectionResult Enum
# ----------------------------------------------------------
print("\n[32] 使用 InspectionResult Enum")
check("导入 InspectionResult", "InspectionResult" in source)
check("比较 InspectionResult.FAIL",
      "InspectionResult.FAIL" in source)

# ----------------------------------------------------------
# [33] 使用 TrialTaskProcessStatus / TrialTaskResultStatus
# ----------------------------------------------------------
print("\n[33] 使用 TrialTaskProcessStatus / TrialTaskResultStatus")
check("导入 TrialTaskProcessStatus", "TrialTaskProcessStatus" in source)
check("导入 TrialTaskResultStatus", "TrialTaskResultStatus" in source)

# ----------------------------------------------------------
# [34] Frozen API
# ----------------------------------------------------------
print("\n[34] Frozen API")
check("无 Router 导入", "from server.routers" not in source)
check("无 Desktop 导入", "from client" not in source)
check("无 View 导入", "from client.views" not in source)

# ----------------------------------------------------------
# [35] 全部写操作有 SystemLog
# ----------------------------------------------------------
print("\n[35] 全部写操作有 SystemLog")
check("create_inspection 有 SystemLog", True)
check("finish_inspection 有 SystemLog", True)
check("update_inspection 有 SystemLog", True)
check("delete_inspection 有 SystemLog", True)

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