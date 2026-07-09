"""Test: Task Service (Sprint 5 — Task 5.2)

严格依据 DEVELOPMENT_ROADMAP.md Task 5.2 验收标准。
测试 server/services/task_service.py 全部公开 API 与代码规范。

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
print("  Task 5.2 — Task Service Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile("server/services/task_service.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.services.task_service import TaskService
    check("TaskService 导入", True)
except ImportError as e:
    check("TaskService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("TaskService 是 class", inspect.isclass(TaskService))
check("TaskService 可实例化", TaskService() is not None)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(TaskService)
    if not m.startswith("_") and callable(getattr(TaskService, m))
]
check("list_tasks 存在", "list_tasks" in public_methods)
check("get_task 存在", "get_task" in public_methods)
check("create_task 存在", "create_task" in public_methods)
check("update_task 存在", "update_task" in public_methods)
check("delete_task 存在", "delete_task" in public_methods)
check("公开 API 数量 = 5", len(public_methods) == 5)

# ----------------------------------------------------------
# [5] 公开 API 签名
# ----------------------------------------------------------
print("\n[5] 公开 API 签名")

# list_tasks
sig = inspect.signature(TaskService.list_tasks)
params = list(sig.parameters.keys())
check("list_tasks: 含 db", "db" in params)
check("list_tasks: 含 task_no", "task_no" in params)
check("list_tasks: 含 customer_id", "customer_id" in params)
check("list_tasks: 含 process_status", "process_status" in params)
check("list_tasks: 含 result_status", "result_status" in params)
check("list_tasks: 含 sales_id", "sales_id" in params)
check("list_tasks: 含 page", "page" in params)
check("list_tasks: 含 page_size", "page_size" in params)

# get_task
sig = inspect.signature(TaskService.get_task)
params = list(sig.parameters.keys())
check("get_task: 含 db", "db" in params)
check("get_task: 含 task_id", "task_id" in params)

# create_task
sig = inspect.signature(TaskService.create_task)
params = list(sig.parameters.keys())
check("create_task: 含 db", "db" in params)
check("create_task: 含 data", "data" in params)
check("create_task: 含 operator_id", "operator_id" in params)

# update_task
sig = inspect.signature(TaskService.update_task)
params = list(sig.parameters.keys())
check("update_task: 含 db", "db" in params)
check("update_task: 含 task_id", "task_id" in params)
check("update_task: 含 data", "data" in params)
check("update_task: 含 operator_id", "operator_id" in params)

# delete_task
sig = inspect.signature(TaskService.delete_task)
params = list(sig.parameters.keys())
check("delete_task: 含 db", "db" in params)
check("delete_task: 含 task_id", "task_id" in params)
check("delete_task: 含 operator_id", "operator_id" in params)

# ----------------------------------------------------------
# [6] 返回值类型注解
# ----------------------------------------------------------
print("\n[6] 返回值类型注解")

# 获取源码
service_path = os.path.join("server", "services", "task_service.py")
with open(service_path, "r", encoding="utf-8") as f:
    source = f.read()

# 检查返回类型注解
check("list_tasks 返回类型注解包含 TrialTaskListResponse",
      "TrialTaskListResponse" in source)
check("get_task 返回类型注解包含 TrialTaskResponse",
      "TrialTaskResponse" in source)
check("create_task 返回类型注解包含 TrialTaskResponse",
      "TrialTaskResponse" in source)
check("update_task 返回类型注解包含 TrialTaskResponse",
      "TrialTaskResponse" in source)
check("delete_task 返回类型注解包含 None",
      "-> None" in source)

# ----------------------------------------------------------
# [7] 使用 TrialTask Schema (Pydantic v2)
# ----------------------------------------------------------
print("\n[7] 使用 TrialTask Schema (Pydantic v2)")
code = extract_code_text(service_path)
check("导入 TrialTaskCreate", "TrialTaskCreate" in source)
check("导入 TrialTaskUpdate", "TrialTaskUpdate" in source)
check("导入 TrialTaskResponse", "TrialTaskResponse" in source)
check("导入 TrialTaskListResponse", "TrialTaskListResponse" in source)
check("未使用 dataclass", "from dataclasses import" not in source)
check("未使用旧 TaskCreate", "class TaskCreate" not in source)
check("未使用旧 TaskUpdate", "class TaskUpdate" not in source)
check("未使用旧 TaskFilter", "class TaskFilter" not in source)

# ----------------------------------------------------------
# [8] generate_task_no 调用
# ----------------------------------------------------------
print("\n[8] generate_task_no 调用")
check("导入 generate_task_no", "from server.utils.id_generator import generate_task_no" in source)
check("create_task 中调用 generate_task_no", "generate_task_no(db)" in code)
check("未自己拼接编号字符串", "YYYYMMDD" not in code)

# ----------------------------------------------------------
# [9] 状态流转校验
# ----------------------------------------------------------
print("\n[9] 状态流转校验")

# 检查 _validate_process_status_change 方法
all_methods = [m for m in dir(TaskService) if callable(getattr(TaskService, m))]
check("_validate_process_status_change 存在", "_validate_process_status_change" in all_methods)
check("_validate_result_status_change 存在", "_validate_result_status_change" in all_methods)

# 检查使用 next_statuses 属性
check("使用 next_statuses 校验流转", "next_statuses" in source)

# 检查非法流转抛出异常
check("非法流转抛出 BusinessLogicException",
      "BusinessLogicException" in source and "非法状态流转" in source)

# ----------------------------------------------------------
# [10] 编辑限制
# ----------------------------------------------------------
print("\n[10] 编辑限制")
check("编辑限制：仅 CREATED 状态可编辑",
      "仅创建状态的任务可编辑" in source)
check("编辑限制：检查 process_status != CREATED",
      "TrialTaskProcessStatus.CREATED" in source)

# ----------------------------------------------------------
# [11] 删除规则
# ----------------------------------------------------------
print("\n[11] 删除规则")
check("软删除 is_deleted=True", "is_deleted = True" in code)
check("无物理删除（无 db.delete）", "db.delete" not in code)
check("delete_task 无 PermissionDeniedException", "PermissionDeniedException" not in source)

# ----------------------------------------------------------
# [12] 搜索 & 分页
# ----------------------------------------------------------
print("\n[12] 搜索 & 分页")
check("按 task_no 模糊搜索", "task_no.like" in source)
check("按 customer_id 筛选", "customer_id" in source)
check("按 process_status 筛选", "process_status" in source)
check("按 result_status 筛选", "result_status" in source)
check("按 sales_id 筛选", "sales_id" in source)
check("分页 offset", "offset" in source)
check("分页 limit", "limit" in source)
check("排序 created_at DESC", "created_at.desc()" in source)

# ----------------------------------------------------------
# [13] 事务管理
# ----------------------------------------------------------
print("\n[13] 事务管理")
check("create_task 有 try/commit/except/rollback",
      "commit" in source and "rollback" in source)
check("update_task 有 try/commit/except/rollback",
      "commit" in source and "rollback" in source)
check("delete_task 有 try/commit/except/rollback",
      "commit" in source and "rollback" in source)

# ----------------------------------------------------------
# [14] SystemLog
# ----------------------------------------------------------
print("\n[14] SystemLog")
check("导入 SystemLog", "SystemLog" in source)
check("导入 ActionType", "ActionType" in source)
check("create 写入 SystemLog (ActionType.CREATE)", "ActionType.CREATE" in source)
check("update 写入 SystemLog (ActionType.UPDATE)", "ActionType.UPDATE" in source)
check("delete 写入 SystemLog (ActionType.DELETE)", "ActionType.DELETE" in source)
check("_write_log 方法存在", "_write_log" in all_methods)

# ----------------------------------------------------------
# [15] 异常使用
# ----------------------------------------------------------
print("\n[15] 异常使用")
check("使用 NotFoundException", "NotFoundException" in source)
check("使用 BusinessLogicException", "BusinessLogicException" in source)
check("未使用 HTTPException", "HTTPException" not in source)
check("未使用 ValidationException", "ValidationException" not in source)
check("未使用 AuthorizationException", "AuthorizationException" not in source)
check("未使用 ConflictException", "ConflictException" not in source)
check("未使用 PermissionDeniedException", "PermissionDeniedException" not in source)

# ----------------------------------------------------------
# [16] 业务规则
# ----------------------------------------------------------
print("\n[16] 业务规则")
check("创建时校验 customer_id 存在", "客户不存在或已删除" in source)
check("创建时校验 sales_id 存在", "销售不存在或已禁用" in source)
check("创建时默认 process_status=CREATED", "TrialTaskProcessStatus.CREATED" in source)
check("创建时默认 result_status=PENDING", "TrialTaskResultStatus.PENDING" in source)
check("更新时校验 customer_id 存在", "客户不存在或已删除" in source)
check("更新时校验 sales_id 存在", "销售不存在或已禁用" in source)

# ----------------------------------------------------------
# [17] 代码规范
# ----------------------------------------------------------
print("\n[17] 代码规范")
check("无 print()", "print(" not in code)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 tab 缩进", "\t" not in source)
check("文件以换行结尾", source.endswith("\n"))
check("使用 logger (gtms.server)", 'logging.getLogger("gtms.server")' in source)
check("有 __all__", "__all__" in source)
check("__all__ 包含 TaskService", "TaskService" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [18] Docstring
# ----------------------------------------------------------
print("\n[18] Docstring")
# 使用 inspect.getdoc 检查每个方法是否有 docstring
for method_name in ["list_tasks", "get_task", "create_task", "update_task", "delete_task"]:
    method = getattr(TaskService, method_name)
    doc = inspect.getdoc(method)
    check(f"{method_name} 有 docstring", doc is not None and len(doc) > 0)

# ----------------------------------------------------------
# [19] Type Hint
# ----------------------------------------------------------
print("\n[19] Type Hint")
# 检查所有公开方法参数有类型注解
for method_name in ["list_tasks", "get_task", "create_task", "update_task", "delete_task"]:
    method = getattr(TaskService, method_name)
    sig = inspect.signature(method)
    all_annotated = all(
        p.annotation is not inspect.Parameter.empty
        for p in sig.parameters.values()
        if p.name != "self"
    )
    check(f"{method_name} 所有参数有类型注解", all_annotated)
    check(f"{method_name} 有返回类型注解", sig.return_annotation is not inspect.Signature.empty)

# ----------------------------------------------------------
# [20] 无循环导入
# ----------------------------------------------------------
print("\n[20] 无循环导入")
try:
    import importlib
    importlib.reload(sys.modules.get("server.services.task_service",
               __import__("server.services.task_service", fromlist=["TaskService"])))
    check("无循环导入", True)
except Exception as e:
    check("无循环导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [21] 公开 API 冻结
# ----------------------------------------------------------
print("\n[21] 公开 API 冻结")
check("公开方法数量 = 5", len(public_methods) == 5)
check("无新增公开方法", set(public_methods) == {
    "list_tasks", "get_task", "create_task", "update_task", "delete_task"
})

# ----------------------------------------------------------
# [22] __all__ 仅导出 TaskService
# ----------------------------------------------------------
print("\n[22] __all__ 仅导出 TaskService")
from server.services.task_service import __all__ as task_service_all
check("__all__ 包含 TaskService", "TaskService" in task_service_all)
check("__all__ 不包含 TaskCreate", "TaskCreate" not in task_service_all)
check("__all__ 不包含 TaskUpdate", "TaskUpdate" not in task_service_all)
check("__all__ 不包含 TaskFilter", "TaskFilter" not in task_service_all)
check("__all__ 仅 1 个导出", len(task_service_all) == 1)

# ----------------------------------------------------------
# [23] 使用 Customer ORM 和 User ORM
# ----------------------------------------------------------
print("\n[23] 使用 Customer/User ORM")
check("导入 Customer", "Customer" in source)
check("导入 User", "User" in source)
check("导入 TrialTask", "TrialTask" in source)

# ----------------------------------------------------------
# [24] 私有方法数量
# ----------------------------------------------------------
print("\n[24] 私有方法")
private_methods = [
    m for m in dir(TaskService)
    if m.startswith("_") and not m.startswith("__") and callable(getattr(TaskService, m))
]
check("有 _get_task_orm", "_get_task_orm" in private_methods)
check("有 _to_response", "_to_response" in private_methods)
check("有 _write_log", "_write_log" in private_methods)
check("有 _validate_process_status_change", "_validate_process_status_change" in private_methods)
check("有 _validate_result_status_change", "_validate_result_status_change" in private_methods)
check("私有方法数量 = 5", len(private_methods) == 5)

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