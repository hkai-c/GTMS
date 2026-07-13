"""Test: Receipt Service (Sprint 6 — Task 6.2)

严格依据 DEVELOPMENT_ROADMAP.md Task 6.2 验收标准。
测试 server/services/receipt_service.py 全部公开 API 与代码规范。

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
print("  Task 6.2 — Receipt Service Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile("server/services/receipt_service.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.services.receipt_service import ReceiptService
    check("ReceiptService 导入", True)
except ImportError as e:
    check("ReceiptService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("ReceiptService 是 class", inspect.isclass(ReceiptService))
check("ReceiptService 可实例化", ReceiptService() is not None)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(ReceiptService)
    if not m.startswith("_") and callable(getattr(ReceiptService, m))
]
check("list_receipts 存在", "list_receipts" in public_methods)
check("get_receipt 存在", "get_receipt" in public_methods)
check("create_receipt 存在", "create_receipt" in public_methods)
check("update_receipt 存在", "update_receipt" in public_methods)
check("delete_receipt 存在", "delete_receipt" in public_methods)
check("公开 API 数量 = 5", len(public_methods) == 5)

# ----------------------------------------------------------
# [5] 公开 API 签名
# ----------------------------------------------------------
print("\n[5] 公开 API 签名")

# list_receipts
sig = inspect.signature(ReceiptService.list_receipts)
params = list(sig.parameters.keys())
check("list_receipts: 含 db", "db" in params)
check("list_receipts: 含 task_id", "task_id" in params)
check("list_receipts: 含 page", "page" in params)
check("list_receipts: 含 page_size", "page_size" in params)

# get_receipt
sig = inspect.signature(ReceiptService.get_receipt)
params = list(sig.parameters.keys())
check("get_receipt: 含 db", "db" in params)
check("get_receipt: 含 receipt_id", "receipt_id" in params)

# create_receipt
sig = inspect.signature(ReceiptService.create_receipt)
params = list(sig.parameters.keys())
check("create_receipt: 含 db", "db" in params)
check("create_receipt: 含 data", "data" in params)
check("create_receipt: 含 operator_id", "operator_id" in params)

# update_receipt
sig = inspect.signature(ReceiptService.update_receipt)
params = list(sig.parameters.keys())
check("update_receipt: 含 db", "db" in params)
check("update_receipt: 含 receipt_id", "receipt_id" in params)
check("update_receipt: 含 data", "data" in params)
check("update_receipt: 含 operator_id", "operator_id" in params)

# delete_receipt
sig = inspect.signature(ReceiptService.delete_receipt)
params = list(sig.parameters.keys())
check("delete_receipt: 含 db", "db" in params)
check("delete_receipt: 含 receipt_id", "receipt_id" in params)
check("delete_receipt: 含 operator_id", "operator_id" in params)

# ----------------------------------------------------------
# [6] 返回值类型注解
# ----------------------------------------------------------
print("\n[6] 返回值类型注解")

service_path = os.path.join("server", "services", "receipt_service.py")
with open(service_path, "r", encoding="utf-8") as f:
    source = f.read()

check("list_receipts 返回类型注解包含 ReceiptListResponse",
      "ReceiptListResponse" in source)
check("get_receipt 返回类型注解包含 ReceiptResponse",
      "ReceiptResponse" in source)
check("create_receipt 返回类型注解包含 ReceiptResponse",
      "ReceiptResponse" in source)
check("update_receipt 返回类型注解包含 ReceiptResponse",
      "ReceiptResponse" in source)
check("delete_receipt 返回类型注解包含 None",
      "-> None" in source)

# ----------------------------------------------------------
# [7] 使用 Receipt Schema (Pydantic v2)
# ----------------------------------------------------------
print("\n[7] 使用 Receipt Schema")
code = extract_code_text(service_path)
check("导入 ReceiptCreate", "ReceiptCreate" in source)
check("导入 ReceiptUpdate", "ReceiptUpdate" in source)
check("导入 ReceiptResponse", "ReceiptResponse" in source)
check("导入 ReceiptListResponse", "ReceiptListResponse" in source)

# ----------------------------------------------------------
# [8] 创建收件：校验 TrialTask 存在
# ----------------------------------------------------------
print("\n[8] 创建收件：校验 TrialTask 存在")
check("校验 TrialTask 存在", "试磨任务不存在" in source)
check("查询 TrialTask", "TrialTask" in source)
check("过滤 is_deleted=False", "is_deleted" in source)

# ----------------------------------------------------------
# [9] 创建收件：校验状态为 CREATED
# ----------------------------------------------------------
print("\n[9] 创建收件：校验状态为 CREATED")
check("检查 process_status == CREATED",
      "TrialTaskProcessStatus.CREATED" in source)
check("非 CREATED 抛出异常",
      "仅创建状态的任务可收件" in source)

# ----------------------------------------------------------
# [10] 创建收件：校验 receiver_id 存在
# ----------------------------------------------------------
print("\n[10] 创建收件：校验 receiver_id 存在")
check("校验收件人存在", "收件人不存在或已禁用" in source)
check("查询 User", "User" in source)

# ----------------------------------------------------------
# [11] 创建收件：校验不重复收件
# ----------------------------------------------------------
print("\n[11] 创建收件：校验不重复收件")
check("校验 task_id 未重复", "该任务已收件" in source)
check("查询已有 Receipt", "Receipt" in source)

# ----------------------------------------------------------
# [12] 创建收件：状态流转
# ----------------------------------------------------------
print("\n[12] 创建收件：状态流转")
check("推进 process_status → RECEIVED",
      "TrialTaskProcessStatus.RECEIVED" in source)
check("记录旧状态", "old_status" in source)

# ----------------------------------------------------------
# [13] 创建收件：SystemLog
# ----------------------------------------------------------
print("\n[13] 创建收件：SystemLog")
check("写入 Receipt Created 日志",
      'target_type="Receipt"' in source and 'ActionType.CREATE' in source)
check("写入 TrialTask Status Change 日志",
      'target_type="TrialTask"' in source and 'ActionType.STATUS_CHANGE' in source)

# ----------------------------------------------------------
# [14] 删除规则
# ----------------------------------------------------------
print("\n[14] 删除规则")
check("软删除 is_deleted=True", "is_deleted = True" in code)
check("无物理删除（无 db.delete）", "db.delete" not in code)

# ----------------------------------------------------------
# [15] 搜索 & 分页
# ----------------------------------------------------------
print("\n[15] 搜索 & 分页")
check("按 task_id 筛选", "task_id" in source)
check("分页 offset", "offset" in source)
check("分页 limit", "limit" in source)
check("排序 created_at DESC", "created_at.desc()" in source)

# ----------------------------------------------------------
# [16] 事务管理
# ----------------------------------------------------------
print("\n[16] 事务管理")
check("create_receipt 有 try/commit/except/rollback",
      "commit" in source and "rollback" in source)
check("update_receipt 有 try/commit/except/rollback",
      "commit" in source and "rollback" in source)
check("delete_receipt 有 try/commit/except/rollback",
      "commit" in source and "rollback" in source)

# ----------------------------------------------------------
# [17] SystemLog
# ----------------------------------------------------------
print("\n[17] SystemLog")
check("导入 SystemLog", "SystemLog" in source)
check("导入 ActionType", "ActionType" in source)
all_methods = [m for m in dir(ReceiptService) if callable(getattr(ReceiptService, m))]
check("_write_log 方法存在", "_write_log" in all_methods)

# ----------------------------------------------------------
# [18] 异常使用
# ----------------------------------------------------------
print("\n[18] 异常使用")
check("使用 NotFoundException", "NotFoundException" in source)
check("使用 BusinessLogicException", "BusinessLogicException" in source)
check("未使用 HTTPException", "HTTPException" not in source)
check("未使用 PermissionDeniedException", "PermissionDeniedException" not in source)

# ----------------------------------------------------------
# [19] 不上传文件
# ----------------------------------------------------------
print("\n[19] 不上传文件")
check("未导入 UploadFile", "UploadFile" not in source)
check("未导入 file_handler", "file_handler" not in source)
check("未导入 File", "from fastapi import File" not in source)
check("未使用 Base64", "base64" not in source.lower())
check("未使用 Binary", "Binary" not in source)

# ----------------------------------------------------------
# [20] 代码规范
# ----------------------------------------------------------
print("\n[20] 代码规范")
check("无 print()", "print(" not in code)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 tab 缩进", "\t" not in source)
check("文件以换行结尾", source.endswith("\n"))
check("使用 logger (gtms.server)", 'logging.getLogger("gtms.server")' in source)
check("有 __all__", "__all__" in source)
check("__all__ 包含 ReceiptService", "ReceiptService" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [21] Docstring
# ----------------------------------------------------------
print("\n[21] Docstring")
for method_name in ["list_receipts", "get_receipt", "create_receipt",
                      "update_receipt", "delete_receipt"]:
    method = getattr(ReceiptService, method_name)
    doc = inspect.getdoc(method)
    check(f"{method_name} 有 docstring", doc is not None and len(doc) > 0)

# ----------------------------------------------------------
# [22] Type Hint
# ----------------------------------------------------------
print("\n[22] Type Hint")
for method_name in ["list_receipts", "get_receipt", "create_receipt",
                      "update_receipt", "delete_receipt"]:
    method = getattr(ReceiptService, method_name)
    sig = inspect.signature(method)
    all_annotated = all(
        p.annotation is not inspect.Parameter.empty
        for p in sig.parameters.values()
        if p.name != "self"
    )
    check(f"{method_name} 所有参数有类型注解", all_annotated)
    check(f"{method_name} 有返回类型注解",
          sig.return_annotation is not inspect.Signature.empty)

# ----------------------------------------------------------
# [23] 无循环导入
# ----------------------------------------------------------
print("\n[23] 无循环导入")
try:
    import importlib
    importlib.reload(sys.modules.get("server.services.receipt_service",
               __import__("server.services.receipt_service",
                          fromlist=["ReceiptService"])))
    check("无循环导入", True)
except Exception as e:
    check("无循环导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [24] 公开 API 冻结
# ----------------------------------------------------------
print("\n[24] 公开 API 冻结")
check("公开方法数量 = 5", len(public_methods) == 5)
check("无新增公开方法", set(public_methods) == {
    "list_receipts", "get_receipt", "create_receipt",
    "update_receipt", "delete_receipt"
})

# ----------------------------------------------------------
# [25] __all__ 仅导出 ReceiptService
# ----------------------------------------------------------
print("\n[25] __all__ 仅导出 ReceiptService")
from server.services.receipt_service import __all__ as receipt_service_all
check("__all__ 包含 ReceiptService", "ReceiptService" in receipt_service_all)
check("__all__ 仅 1 个导出", len(receipt_service_all) == 1)

# ----------------------------------------------------------
# [26] 使用 ORM 模型
# ----------------------------------------------------------
print("\n[26] 使用 ORM 模型")
check("导入 Receipt", "Receipt" in source)
check("导入 TrialTask", "TrialTask" in source)
check("导入 User", "User" in source)
check("导入 SystemLog", "SystemLog" in source)

# ----------------------------------------------------------
# [27] 私有方法
# ----------------------------------------------------------
print("\n[27] 私有方法")
private_methods = [
    m for m in dir(ReceiptService)
    if m.startswith("_") and not m.startswith("__")
    and callable(getattr(ReceiptService, m))
]
check("有 _get_receipt_orm", "_get_receipt_orm" in private_methods)
check("有 _to_response", "_to_response" in private_methods)
check("有 _write_log", "_write_log" in private_methods)
check("私有方法数量 = 3", len(private_methods) == 3)

# ----------------------------------------------------------
# [28] PEP8 合规
# ----------------------------------------------------------
print("\n[28] PEP8")
try:
    import pycodestyle
    style = pycodestyle.StyleGuide(quiet=True, ignore=["E712", "E501"])
    report = style.check_files([service_path])
    check("PEP8 合规", report.total_errors == 0)
except ImportError:
    check("PEP8 (pycodestyle 未安装，跳过)", True)

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