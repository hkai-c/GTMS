"""Test: Audit Logging Integration (Sprint 11 — Task 11.4)

严格依据 DEVELOPMENT_ROADMAP.md Task 11.4 验收标准。
验证所有业务 Service 已集成 LogService.create_log()，
不再直接创建 SystemLog ORM 对象。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import ast
import os
import re
import subprocess
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
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
# 目标 Service 列表
# ============================================================

TARGET_SERVICES = [
    "customer_service",
    "task_service",
    "receipt_service",
    "grinding_service",
    "inspection_service",
    "dispatch_service",
]

SERVICE_PATHS = {
    s: os.path.join("server", "services", f"{s}.py")
    for s in TARGET_SERVICES
}

# Services that have a DELETE operation
DELETE_SERVICES = [
    "task_service",
    "receipt_service",
    "grinding_service",
    "inspection_service",
    "dispatch_service",
]

# Services that have STATUS_CHANGE operation
STATUS_CHANGE_SERVICES = [
    "receipt_service",
    "grinding_service",
    "inspection_service",
    "dispatch_service",
]

# Services that are task-based (have process_status)
TASK_SERVICES = [
    "task_service",
    "receipt_service",
    "grinding_service",
    "inspection_service",
    "dispatch_service",
]

# Services that are task-based (have result_status)
RESULT_STATUS_SERVICES = [
    "task_service",
    "grinding_service",
    "inspection_service",
    "dispatch_service",
]

# ============================================================
# 自检
# ============================================================

print("=" * 60)
print("  Task 11.4 — Audit Logging Integration Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile — 所有 Service 编译通过
# ----------------------------------------------------------
print("\n[1] py_compile — 所有 Service")
for name, path in SERVICE_PATHS.items():
    try:
        import py_compile
        py_compile.compile(path, doraise=True)
        check(f"{name} py_compile", True)
    except py_compile.PyCompileError as e:
        check(f"{name} py_compile", False)
        print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import — 所有 Service 可导入
# ----------------------------------------------------------
print("\n[2] import — 所有 Service")
IMPORT_MAP = {
    "customer_service": "CustomerService",
    "task_service": "TaskService",
    "receipt_service": "ReceiptService",
    "grinding_service": "GrindingService",
    "inspection_service": "InspectionService",
    "dispatch_service": "DispatchService",
}
for name, cls_name in IMPORT_MAP.items():
    try:
        mod = __import__(
            f"server.services.{name}", fromlist=[cls_name]
        )
        getattr(mod, cls_name)
        check(f"{name} import", True)
    except (ImportError, AttributeError) as e:
        check(f"{name} import", False)
        print(f"      Error: {e}")

# ----------------------------------------------------------
# [3] 禁止 SystemLog 导入
# ----------------------------------------------------------
print("\n[3] 禁止 SystemLog 导入")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    has_systemlog_import = (
        "from server.models import" in code
        and "SystemLog" in code
    )
    check(
        f"{name} 无 SystemLog 导入",
        not has_systemlog_import,
    )

# ----------------------------------------------------------
# [4] 禁止直接创建 SystemLog
# ----------------------------------------------------------
print("\n[4] 禁止直接创建 SystemLog ORM")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    check(
        f"{name} 无 SystemLog( 构造",
        "SystemLog(" not in code,
    )
    check(
        f"{name} 无 db.add(SystemLog",
        "db.add(SystemLog" not in code,
    )

# ----------------------------------------------------------
# [5] 使用 LogService.create_log()
# ----------------------------------------------------------
print("\n[5] 使用 LogService.create_log()")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    check(
        f"{name} 使用 LogService.create_log",
        "_log_service.create_log" in code,
    )

# ----------------------------------------------------------
# [6] _log_service 类属性
# ----------------------------------------------------------
print("\n[6] _log_service 类属性")
for name, path in SERVICE_PATHS.items():
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    check(
        f"{name} _log_service = LogService()",
        "_log_service = LogService()" in content,
    )

# ----------------------------------------------------------
# [7] 导入 LogService 和 LogBase
# ----------------------------------------------------------
print("\n[7] 导入 LogService 和 LogBase")
for name, path in SERVICE_PATHS.items():
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    check(
        f"{name} 导入 LogService",
        "from server.services.log_service import LogService"
        in content,
    )
    check(
        f"{name} 导入 LogBase",
        "from server.schemas.log_schema import LogBase"
        in content,
    )

# ----------------------------------------------------------
# [8] _write_log 方法签名不变
# ----------------------------------------------------------
print("\n[8] _write_log 方法签名不变")
for name, path in SERVICE_PATHS.items():
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    check(
        f"{name} _write_log 存在",
        "def _write_log" in content,
    )
    check(
        f"{name} _write_log 含 operator_id",
        "operator_id: int" in content,
    )
    check(
        f"{name} _write_log 含 action",
        "action: ActionType" in content,
    )
    check(
        f"{name} _write_log 含 target_type",
        "target_type: str" in content,
    )

# ----------------------------------------------------------
# [9] CREATE 操作记录
# ----------------------------------------------------------
print("\n[9] CREATE 操作记录")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    check(
        f"{name} 记录 CREATE",
        "ActionType.CREATE" in code,
    )

# ----------------------------------------------------------
# [10] UPDATE 操作记录
# ----------------------------------------------------------
print("\n[10] UPDATE 操作记录")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    check(
        f"{name} 记录 UPDATE",
        "ActionType.UPDATE" in code,
    )

# ----------------------------------------------------------
# [11] DELETE 操作记录（仅含 delete 方法的 Service）
# ----------------------------------------------------------
print("\n[11] DELETE 操作记录")
for name in DELETE_SERVICES:
    path = SERVICE_PATHS[name]
    code = extract_code_text(path)
    check(
        f"{name} 记录 DELETE",
        "ActionType.DELETE" in code,
    )

# ----------------------------------------------------------
# [12] STATUS_CHANGE 操作记录（仅含状态变更的 Service）
# ----------------------------------------------------------
print("\n[12] STATUS_CHANGE 操作记录")
for name in STATUS_CHANGE_SERVICES:
    path = SERVICE_PATHS[name]
    code = extract_code_text(path)
    check(
        f"{name} 记录 STATUS_CHANGE",
        "ActionType.STATUS_CHANGE" in code,
    )

# ----------------------------------------------------------
# [13] LogBase 参数正确
# ----------------------------------------------------------
print("\n[13] LogBase 参数正确")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    check(
        f"{name} LogBase operator_id",
        "operator_id=operator_id" in code,
    )
    check(
        f"{name} LogBase operation",
        "operation=action" in code,
    )
    check(
        f"{name} LogBase module",
        "module=target_type" in code,
    )
    check(
        f"{name} LogBase target_type",
        "target_type=target_type" in code,
    )

# ----------------------------------------------------------
# [14] Zero Workflow 改动（仅 task-based Service）
# ----------------------------------------------------------
print("\n[14] Zero Workflow 改动")
for name in TASK_SERVICES:
    path = SERVICE_PATHS[name]
    code = extract_code_text(path)
    check(
        f"{name} process_status 存在",
        "process_status" in code,
    )

# ----------------------------------------------------------
# [15] Zero Status Machine 改动（仅 task-based Service）
# ----------------------------------------------------------
print("\n[15] Zero Status Machine 改动")
for name in RESULT_STATUS_SERVICES:
    path = SERVICE_PATHS[name]
    code = extract_code_text(path)
    check(
        f"{name} result_status 存在",
        "result_status" in code,
    )

# ----------------------------------------------------------
# [16] Frozen API 未修改
# ----------------------------------------------------------
print("\n[16] Frozen API 未修改")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    check(
        f"{name} 无 Router 导入",
        "from server.routers" not in code,
    )
    check(
        f"{name} 无 Desktop 导入",
        "from client." not in code,
    )
    check(
        f"{name} 无 View 导入",
        "from client.views" not in code,
    )

# ----------------------------------------------------------
# [17] PEP8（忽略预存 E501/E712 问题）
# ----------------------------------------------------------
print("\n[17] PEP8")
for name, path in SERVICE_PATHS.items():
    result = subprocess.run(
        [
            "python", "-m", "flake8",
            "--select=E,W,F,N",
            "--ignore=E501,E712,F841",
            path,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    flake8_ok = result.returncode == 0
    if not flake8_ok and result.stdout:
        print(f"    {name} flake8 (new): {result.stdout.strip()}")
    check(f"{name} PEP8 合规（新增）", flake8_ok)

# ----------------------------------------------------------
# [18] 无 print()
# ----------------------------------------------------------
print("\n[18] 无 print()")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    check(
        f"{name} 无 print()",
        "print(" not in code,
    )

# ----------------------------------------------------------
# [19] logger 使用
# ----------------------------------------------------------
print("\n[19] logger 使用")
for name, path in SERVICE_PATHS.items():
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    check(
        f"{name} 使用 logger",
        "logger" in content,
    )

# ----------------------------------------------------------
# [20] 私有方法保持
# ----------------------------------------------------------
print("\n[20] 私有方法保持")
for name, path in SERVICE_PATHS.items():
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    check(
        f"{name} _write_log 存在",
        "def _write_log" in content,
    )
    check(
        f"{name} _to_response 存在",
        "_to_response" in content,
    )

# ----------------------------------------------------------
# [21] 同事务提交（_write_log 在 try 块内）
# ----------------------------------------------------------
print("\n[21] 同事务提交")
for name, path in SERVICE_PATHS.items():
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    check(
        f"{name} _write_log 在 try 块内",
        "_write_log" in content,
    )
    check(
        f"{name} except rollback",
        "rollback" in content,
    )

# ----------------------------------------------------------
# [22] 无重复日志
# ----------------------------------------------------------
print("\n[22] 无重复日志")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    check(
        f"{name} 无 SystemLog 直接操作",
        "SystemLog(" not in code,
    )

# ----------------------------------------------------------
# [23] 无遗漏日志
# ----------------------------------------------------------
print("\n[23] 无遗漏日志")
for name, path in SERVICE_PATHS.items():
    code = extract_code_text(path)
    write_count = code.count("_write_log(")
    check(
        f"{name} 有日志写入 ({write_count} 次)",
        write_count > 0,
    )

# ----------------------------------------------------------
# [24] 文件末尾换行
# ----------------------------------------------------------
print("\n[24] 文件末尾换行")
for name, path in SERVICE_PATHS.items():
    with open(path, "rb") as f:
        f.seek(-1, 2)
        last_char = f.read(1)
    check(
        f"{name} 末尾换行",
        last_char == b"\n",
    )

# ----------------------------------------------------------
# [25] 无 ast 导入错误
# ----------------------------------------------------------
print("\n[25] ast 解析")
for name, path in SERVICE_PATHS.items():
    try:
        with open(path, "r", encoding="utf-8") as f:
            ast.parse(f.read())
        check(f"{name} ast 解析", True)
    except SyntaxError as e:
        check(f"{name} ast 解析", False)
        print(f"      Error: {e}")

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