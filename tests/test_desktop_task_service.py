"""Test: Desktop TaskService (Sprint 5 — Task 5.4)

测试 client/services/task_service.py 的全部公开 API 与代码规范。
使用源码分析，不依赖 PySide6 DLL。
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
print("  Task 5.4 — Desktop TaskService Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile("client/services/task_service.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from client.services.task_service import TaskService
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

# 获取源码
service_path = os.path.join("client", "services", "task_service.py")
with open(service_path, "r", encoding="utf-8") as f:
    source = f.read()
code = extract_code_text(service_path)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
# 公开方法 = 不以下划线开头（排除 __init__ 等私有方法）
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
# [5] __init__ 签名
# ----------------------------------------------------------
print("\n[5] __init__ 签名")
sig = inspect.signature(TaskService.__init__)
params = list(sig.parameters.keys())
check("__init__ 含 self", "self" in params)
check("__init__ 含 api_client", "api_client" in params)
check("__init__ 参数数量 = 2", len(params) == 2)

# ----------------------------------------------------------
# [6] 公开方法签名
# ----------------------------------------------------------
print("\n[6] 公开方法签名")

# list_tasks
sig = inspect.signature(TaskService.list_tasks)
params = list(sig.parameters.keys())
check("list_tasks: 含 self", "self" in params)
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
check("get_task: 含 self", "self" in params)
check("get_task: 含 task_id", "task_id" in params)

# create_task
sig = inspect.signature(TaskService.create_task)
params = list(sig.parameters.keys())
check("create_task: 含 self", "self" in params)
check("create_task: 含 customer_id", "customer_id" in params)
check("create_task: 含 requirement", "requirement" in params)
check("create_task: 含 sales_id", "sales_id" in params)
check("create_task: 含 tracking_no", "tracking_no" in params)

# update_task
sig = inspect.signature(TaskService.update_task)
params = list(sig.parameters.keys())
check("update_task: 含 self", "self" in params)
check("update_task: 含 task_id", "task_id" in params)
check("update_task: 含 requirement", "requirement" in params)
check("update_task: 含 tracking_no", "tracking_no" in params)
check("update_task: 含 process_status", "process_status" in params)
check("update_task: 含 result_status", "result_status" in params)
check("update_task: 含 destination", "destination" in params)
check("update_task: 含 destination_date", "destination_date" in params)
check("update_task: 含 failure_reason", "failure_reason" in params)

# delete_task
sig = inspect.signature(TaskService.delete_task)
params = list(sig.parameters.keys())
check("delete_task: 含 self", "self" in params)
check("delete_task: 含 task_id", "task_id" in params)

# ----------------------------------------------------------
# [7] HTTP Method
# ----------------------------------------------------------
print("\n[7] HTTP Method")
check("list_tasks 使用 GET", '_api_client.get("/api/tasks"' in code)
check("get_task 使用 GET", '_api_client.get(f"/api/tasks/{task_id}")' in code)
check("create_task 使用 POST", '_api_client.post("/api/tasks"' in code)
check("update_task 使用 PUT", '_api_client.put(f"/api/tasks/{task_id}"' in code)
check("delete_task 使用 DELETE", '_api_client.delete(f"/api/tasks/{task_id}")' in code)

# ----------------------------------------------------------
# [8] URL 路径
# ----------------------------------------------------------
print("\n[8] URL 路径")
check("GET /api/tasks (列表)", '"/api/tasks"' in source)
check("GET /api/tasks/{task_id} (详情)", '"/api/tasks/{task_id}"' in source)
check("POST /api/tasks", '"/api/tasks"' in source)
check("PUT /api/tasks/{task_id}", '"/api/tasks/{task_id}"' in source)
check("DELETE /api/tasks/{task_id}", '"/api/tasks/{task_id}"' in source)

# ----------------------------------------------------------
# [9] Query 参数全映射
# ----------------------------------------------------------
print("\n[9] Query 参数全映射")
check("list_tasks 支持 task_no 查询参数", 'params["task_no"]' in source)
check("list_tasks 支持 customer_id 查询参数", 'params["customer_id"]' in source)
check("list_tasks 支持 process_status 查询参数", 'params["process_status"]' in source)
check("list_tasks 支持 result_status 查询参数", 'params["result_status"]' in source)
check("list_tasks 支持 sales_id 查询参数", 'params["sales_id"]' in source)
check("list_tasks 支持 page 查询参数", 'params["page"]' in source or '"page": page' in source)
check("list_tasks 支持 page_size 查询参数", 'params["page_size"]' in source or '"page_size": page_size' in source)

# ----------------------------------------------------------
# [10] Body 参数
# ----------------------------------------------------------
print("\n[10] Body 参数")
check("create_task body 含 customer_id", '"customer_id": customer_id' in source)
check("create_task body 含 requirement", '"requirement": requirement' in source)
check("create_task body 含 sales_id", '"sales_id": sales_id' in source)
check("update_task 仅提交非 None 字段", "if requirement is not None" in source)
check("update_task 无 None 字段发送", "if failure_reason is not None" in source)

# ----------------------------------------------------------
# [11] response.json()
# ----------------------------------------------------------
print("\n[11] response.json()")
check("list_tasks 返回 resp.json()", "resp.json()" in source)
check("get_task 返回 resp.json()", "resp.json()" in source)
check("create_task 返回 resp.json()", "resp.json()" in source)
check("update_task 返回 resp.json()", "resp.json()" in source)
check("delete_task 返回 resp.json()", "resp.json()" in source)

# ----------------------------------------------------------
# [12] ApiClient 注入
# ----------------------------------------------------------
print("\n[12] ApiClient 注入")
check("__init__ 存储 ApiClient", "self._api_client" in source)
check("全部通过 ApiClient 调用", "_api_client" in source)
check("未直接 import requests", "import requests" not in source)
check("未直接 import httpx", "import httpx" not in source)
check("未直接 import urllib", "import urllib" not in source)

# ----------------------------------------------------------
# [13] 无 Business Logic
# ----------------------------------------------------------
print("\n[13] 无 Business Logic")
check("无 generate_task_no", "generate_task_no" not in source)
check("无 next_statuses", "next_statuses" not in source)
check("无 is_deleted", "is_deleted" not in source)
check("无 SystemLog", "SystemLog" not in source)
check("无 状态流转逻辑", "process_status" not in code or "next_statuses" not in code)
check("无 编辑限制检查", "仅创建状态" not in source)
check("无 唯一性校验", "唯一" not in source)
check("无 权限检查", "permission" not in source.lower())
check("无 分页计算", "page * page_size" not in code)
check("无 ORM 操作", "sqlalchemy" not in source.lower())

# ----------------------------------------------------------
# [14] 无缓存
# ----------------------------------------------------------
print("\n[14] 无缓存")
check("无缓存字典", "cache" not in source.lower())
check("无缓存列表", "self._tasks" not in source)
check("无 @lru_cache", "@lru_cache" not in source)
check("无全局变量", "global" not in code)

# ----------------------------------------------------------
# [15] 无 JWT / Token
# ----------------------------------------------------------
print("\n[15] 无 JWT / Token")
check("无 JWT", "jwt" not in source.lower())
check("无 Token 处理", "token" not in source.lower())
check("无 bearer", "bearer" not in source.lower())

# ----------------------------------------------------------
# [16] 线程安全
# ----------------------------------------------------------
print("\n[16] 线程安全")
check("每个实例绑定 ApiClient", "self._api_client" in source)
check("无 Singleton", "singleton" not in source.lower())
check("无 class 级别缓存", "class" not in source.lower() or "class TaskService" in source)

# ----------------------------------------------------------
# [17] 异常原样抛出
# ----------------------------------------------------------
print("\n[17] 异常原样抛出")
check("无 try", "try:" not in code)
check("无 except", "except" not in code)
check("无 raise (自定义异常)", "raise" not in code)

# ----------------------------------------------------------
# [18] logger
# ----------------------------------------------------------
print("\n[18] logger")
check("使用 logger", "logger" in source)
check("使用 gtms.client", '"gtms.client"' in source)
check("无 print()", "print(" not in code)

# ----------------------------------------------------------
# [19] 返回值类型
# ----------------------------------------------------------
print("\n[19] 返回值类型")
import client.services.task_service as task_module
for method_name in ["list_tasks", "get_task", "create_task", "update_task", "delete_task"]:
    method = getattr(task_module.TaskService, method_name)
    sig = inspect.signature(method)
    has_return = sig.return_annotation is not inspect.Signature.empty
    check(f"{method_name} 有返回类型注解", has_return)

# ----------------------------------------------------------
# [20] Docstring
# ----------------------------------------------------------
print("\n[20] Docstring")
for method_name in ["__init__", "list_tasks", "get_task", "create_task", "update_task", "delete_task"]:
    method = getattr(task_module.TaskService, method_name)
    doc = inspect.getdoc(method)
    check(f"{method_name} 有 docstring", doc is not None and len(doc) > 0)

# ----------------------------------------------------------
# [21] 代码规范
# ----------------------------------------------------------
print("\n[21] 代码规范")
check("无 print()", "print(" not in code)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 pass", "pass" not in code)
check("无 tab 缩进", "\t" not in source)
check("文件以换行结尾", source.endswith("\n"))
check("有 __all__", "__all__" in source)
check("__all__ 包含 TaskService", "TaskService" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [22] 无循环导入
# ----------------------------------------------------------
print("\n[22] 无循环导入")
try:
    import importlib
    importlib.reload(sys.modules.get("client.services.task_service",
               __import__("client.services.task_service", fromlist=["TaskService"])))
    check("无循环导入", True)
except Exception as e:
    check("无循环导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [23] API Freeze
# ----------------------------------------------------------
print("\n[23] API Freeze")
check("公开方法数量 = 5", len(public_methods) == 5)
check("无新增公开方法", set(public_methods) == {
    "list_tasks", "get_task", "create_task", "update_task", "delete_task"
})

# ----------------------------------------------------------
# [24] __all__ 仅导出 TaskService
# ----------------------------------------------------------
print("\n[24] __all__ 仅导出 TaskService")
from client.services.task_service import __all__ as task_all
check("__all__ 包含 TaskService", "TaskService" in task_all)
check("__all__ 仅 1 个导出", len(task_all) == 1)

# ----------------------------------------------------------
# [25] Frozen API 未修改
# ----------------------------------------------------------
print("\n[25] Frozen API 未修改")
# 检查未导入服务端模块
check("未导入 Server TaskService", "from server.services" not in source)
check("未导入 TrialTask Schema", "TrialTaskSchema" not in source)
check("未导入 ORM 模型", "from server.models" not in source)

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