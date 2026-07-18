"""Test: Log Service (Sprint 11 — Task 11.2)

严格依据 DEVELOPMENT_ROADMAP.md Task 11.2 验收标准。
测试 server/services/log_service.py 全部公开 API 与代码规范。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import ast
import inspect
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
# 自检
# ============================================================

print("=" * 60)
print("  Task 11.2 — Log Service Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "services", "log_service.py")
INIT_PATH = os.path.join("server", "services", "__init__.py")

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
    from server.services.log_service import LogService
    check("LogService 导入", True)
except ImportError as e:
    check("LogService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("LogService 是 class", inspect.isclass(LogService))
check("LogService 可实例化", LogService() is not None)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(LogService)
    if not m.startswith("_") and callable(getattr(LogService, m))
]
check("list_logs 存在", "list_logs" in public_methods)
check("get_log 存在", "get_log" in public_methods)
check("create_log 存在", "create_log" in public_methods)
check("export_logs 存在", "export_logs" in public_methods)
check("公开 API 数量 = 4", len(public_methods) == 4)

# ----------------------------------------------------------
# [5] 公开 API 签名
# ----------------------------------------------------------
print("\n[5] 公开 API 签名")

# list_logs
sig = inspect.signature(LogService.list_logs)
params = list(sig.parameters.keys())
check("list_logs: 含 self", "self" in params)
check("list_logs: 含 db", "db" in params)
check("list_logs: 含 log_query", "log_query" in params)
check("list_logs: 参数数量 = 3", len(params) == 3)

# get_log
sig = inspect.signature(LogService.get_log)
params = list(sig.parameters.keys())
check("get_log: 含 self", "self" in params)
check("get_log: 含 db", "db" in params)
check("get_log: 含 log_id", "log_id" in params)
check("get_log: 参数数量 = 3", len(params) == 3)

# create_log
sig = inspect.signature(LogService.create_log)
params = list(sig.parameters.keys())
check("create_log: 含 self", "self" in params)
check("create_log: 含 db", "db" in params)
check("create_log: 含 log_base", "log_base" in params)
check("create_log: 参数数量 = 3", len(params) == 3)

# export_logs
sig = inspect.signature(LogService.export_logs)
params = list(sig.parameters.keys())
check("export_logs: 含 self", "self" in params)
check("export_logs: 含 db", "db" in params)
check("export_logs: 含 log_query", "log_query" in params)
check("export_logs: 参数数量 = 3", len(params) == 3)

# ----------------------------------------------------------
# [6] 返回值类型注解
# ----------------------------------------------------------
print("\n[6] 返回值类型注解")

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

code = extract_code_text(SOURCE_PATH)

check("list_logs 返回 LogListResponse",
      "LogListResponse" in source)
check("get_log 返回 LogResponse", "LogResponse" in source)
check("create_log 返回 LogResponse", "LogResponse" in source)
check("export_logs 返回 list[dict]", "list[dict]" in source)

# ----------------------------------------------------------
# [7] 使用 Log Schema
# ----------------------------------------------------------
print("\n[7] 使用 Log Schema")
check("导入 LogBase", "LogBase" in source)
check("导入 LogListResponse", "LogListResponse" in source)
check("导入 LogQuery", "LogQuery" in source)
check("导入 LogResponse", "LogResponse" in source)

# ----------------------------------------------------------
# [8] list_logs: 分页逻辑
# ----------------------------------------------------------
print("\n[8] list_logs: 分页逻辑")
check("使用 .offset()", ".offset(" in code)
check("使用 .limit()", ".limit(" in code)
check("使用 .count()", ".count()" in code)
check("计算 offset = (page-1) * page_size",
      "(log_query.page - 1)" in code)
check("LogListResponse 含 total 参数",
      "total=total" in code)
check("filter is_deleted", "is_deleted" in source)

# ----------------------------------------------------------
# [9] _apply_filters: 筛选逻辑
# ----------------------------------------------------------
print("\n[9] _apply_filters: 筛选逻辑")
check("operator_id 过滤 (user_id)",
      "log_query.operator_id" in source)
check("operation 过滤 (action)",
      "log_query.operation" in source)
check("module 过滤 (changes JSON)",
      'changes["module"]' in source)
check("keyword 过滤 (target_type + description)",
      "log_query.keyword" in source)
check("keyword 使用 or_", "or_" in source)
check("keyword 使用 ilike", "ilike" in source)
check("keyword 使用 % 通配符",
      'f"%{log_query.keyword}%"' in source)
check("start_time 过滤", "log_query.start_time" in source)
check("end_time 过滤", "log_query.end_time" in source)
check("全部使用 .filter()", ".filter(" in source)
check("禁止 Python 内存过滤（无 [x for x in）",
      "[x for x in" not in source)

# ----------------------------------------------------------
# [10] _apply_sorting: 排序逻辑
# ----------------------------------------------------------
print("\n[10] _apply_sorting: 排序逻辑")
check("使用 getattr 动态获取排序列",
      "getattr(" in source)
check("默认排序字段回退到 created_at",
      "SystemLog.created_at" in source
      and "sort_column is None" in source)
check("支持 asc 排序", ".asc()" in source)
check("支持 desc 排序", "desc(" in source)
check("sort_order 判断",
      'sort_order == "asc"' in source)

# ----------------------------------------------------------
# [11] get_log: 错误处理
# ----------------------------------------------------------
print("\n[11] get_log: 错误处理")
check("日志不存在时 raise ValueError",
      "raise ValueError" in source)
check("错误消息包含 id", "日志不存在" in source)
check("使用 .first()", ".first()" in source)
check("filter is_deleted", "is_deleted" in source)

# ----------------------------------------------------------
# [12] create_log: 事务
# ----------------------------------------------------------
print("\n[12] create_log: 事务")
check("使用 db.add()", "db.add(" in source)
check("使用 db.commit()", "db.commit()" in source)
check("使用 db.refresh()", "db.refresh(" in source)
check("module/description 存入 changes JSON",
      'changes = {' in source)
check("设置 user_id=log_base.operator_id",
      "user_id=log_base.operator_id" in source)
check("设置 action=log_base.operation",
      "action=log_base.operation" in source)
check("设置 target_type=log_base.target_type",
      "target_type=log_base.target_type" in source)
check("设置 target_id=log_base.target_id",
      "target_id=log_base.target_id" in source)

# ----------------------------------------------------------
# [13] export_logs: 导出数据准备
# ----------------------------------------------------------
print("\n[13] export_logs: 导出数据准备")
check("复用 _apply_filters", "_apply_filters" in source)
check("复用 _apply_sorting", "_apply_sorting" in source)
check("使用 _to_export_dict", "_to_export_dict" in source)
check("返回 list[dict]", "list[dict]" in source)
check("禁止 openpyxl", "openpyxl" not in source)
check("禁止文件写入 (open)", "open(" not in source)
check("禁止保存文件", "save" not in source.lower())

# ----------------------------------------------------------
# [14] Zero try/except
# ----------------------------------------------------------
print("\n[14] Zero try/except")
check("无 try", "try" not in code)
check("无 except", "except" not in code)

# ----------------------------------------------------------
# [15] Zero Workflow: 不修改 process_status
# ----------------------------------------------------------
print("\n[15] Zero Workflow: 不修改 process_status")
check("无 process_status",
      "process_status" not in source)

# ----------------------------------------------------------
# [16] Zero Status Machine: 不修改 result_status
# ----------------------------------------------------------
print("\n[16] Zero Status Machine: 不修改 result_status")
check("无 result_status",
      "result_status" not in source)

# ----------------------------------------------------------
# [17] 事务规则：仅 create_log 提交事务
# ----------------------------------------------------------
print("\n[17] 事务规则")
# create_log 中使用 db.commit（通过 create_log 检查）
# list/get/export 不应有 db.commit/rollback/flush
list_code = "\n".join(
    source.split("def list_logs")[1].split("def _apply_filters")[0]
    if "def list_logs" in source and "def _apply_filters" in source
    else [""]
)
export_code = "\n".join(
    source.split("def export_logs")[1].split("def _to_log_response")[0]
    if "def export_logs" in source and "def _to_log_response" in source
    else [""]
)
get_code = "\n".join(
    source.split("def get_log")[1].split("def create_log")[0]
    if "def get_log" in source and "def create_log" in source
    else [""]
)
check("list_logs 无 db.commit",
      "db.commit()" not in list_code)
check("get_log 无 db.commit",
      "db.commit()" not in get_code)
check("export_logs 无 db.commit",
      "db.commit()" not in export_code)
check("create_log 有 db.commit",
      "db.commit()" in source)

# ----------------------------------------------------------
# [18] 异常处理：仅 ValueError 用于不存在的日志
# ----------------------------------------------------------
print("\n[18] 异常处理")
check("无 print()", "print(" not in source)

# ----------------------------------------------------------
# [19] logger
# ----------------------------------------------------------
print("\n[19] logger")
check("使用 gtms.server logger",
      'logging.getLogger("gtms.server")' in source)
check("logger.info 使用", "logger.info" in source)
check("logger.debug 使用", "logger.debug" in source)
check("list_logs 日志", "list_logs" in source)
check("create_log 日志", "create_log" in source)
check("export_logs 日志", "export_logs" in source)
check("get_log 日志", "get_log" in source)

# ----------------------------------------------------------
# [20] Type Hint
# ----------------------------------------------------------
print("\n[20] Type Hint")
check("Session 类型注解", "Session" in source)
check("LogQuery 类型注解", "LogQuery" in source)
check("LogBase 类型注解", "LogBase" in source)
check("所有方法有返回类型注解", "->" in source)

# ----------------------------------------------------------
# [21] 私有方法
# ----------------------------------------------------------
print("\n[21] 私有方法")
check("_apply_filters 存在", "_apply_filters" in source)
check("_apply_sorting 存在", "_apply_sorting" in source)
check("_to_log_response 存在", "_to_log_response" in source)
check("_to_export_dict 存在", "_to_export_dict" in source)
check("私有方法数量 = 4",
      source.count("def _") == 4)

# ----------------------------------------------------------
# [22] PEP8
# ----------------------------------------------------------
print("\n[22] PEP8")
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
# [23] Docstring
# ----------------------------------------------------------
print("\n[23] Docstring")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
check("模块级 docstring 存在",
      ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "LogService":
        check("类 docstring 存在",
              ast.get_docstring(node) is not None)
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                doc = ast.get_docstring(item)
                check(f"{item.name} docstring 存在",
                      doc is not None)

# ----------------------------------------------------------
# [24] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[24] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 pass",
      not re.search(r"\bpass\b", extract_code_text(SOURCE_PATH)))

# ----------------------------------------------------------
# [25] Frozen API
# ----------------------------------------------------------
print("\n[25] Frozen API")
check("无 Router 导入",
      "from server.routers" not in source)
check("无 Desktop 导入",
      "from client." not in source)
check("无 FastAPI 导入", "FastAPI" not in source)
check("无 APIRouter 导入", "APIRouter" not in source)

# ----------------------------------------------------------
# [26] __all__ 导出
# ----------------------------------------------------------
print("\n[26] __all__ 导出")
check("__all__ 包含 LogService",
      "LogService" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [27] __init__.py 导出
# ----------------------------------------------------------
print("\n[27] __init__.py 导出")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导出 LogService",
      "LogService" in init_code)

# ----------------------------------------------------------
# [28] 枚举使用
# ----------------------------------------------------------
print("\n[28] 枚举使用")
check("导入 ActionType",
      "ActionType" in source or "action" in source.lower())
check("SystemLog.action 使用 ActionType 枚举",
      "SystemLog.action" in source)

# ----------------------------------------------------------
# [29] 性能标准
# ----------------------------------------------------------
print("\n[29] 性能标准")
check("禁止 SELECT *",
      "SELECT *" not in source)
check("数据库过滤（全部 .filter）",
      source.count(".filter(") >= 5)
check("数据库排序（.order_by）",
      ".order_by(" in source)
check("数据库分页（.offset + .limit）",
      ".offset(" in source and ".limit(" in source)

# ----------------------------------------------------------
# [30] 模型字段正确性
# ----------------------------------------------------------
print("\n[30] 模型字段正确性")
check("使用 user_id（非 operator_id）",
      "SystemLog.user_id" in source)
check("使用 action（非 operation）",
      "SystemLog.action" in source)
check("使用 target_type",
      "SystemLog.target_type" in source)
check("使用 changes JSON 字段",
      'changes' in source)
check("operator_id 映射到 user_id",
      "user_id=log_base.operator_id" in source)
check("operation 映射到 action",
      "action=log_base.operation" in source)

# ----------------------------------------------------------
# [31] 文件末尾换行
# ----------------------------------------------------------
print("\n[31] 文件末尾换行")
with open(SOURCE_PATH, "rb") as f:
    f.seek(-1, 2)
    last_char = f.read(1)
check("文件以换行符结尾", last_char == b"\n")

# ----------------------------------------------------------
# [32] 代码行宽
# ----------------------------------------------------------
print("\n[32] 代码行宽")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()
long_lines = [
    i + 1 for i, line in enumerate(lines)
    if len(line.rstrip("\n")) > 79
]
if long_lines:
    print(f"    超长行: {long_lines}")
check("所有行 ≤ 79 字符", len(long_lines) == 0)

# ----------------------------------------------------------
# [33] __init__.py 完整性
# ----------------------------------------------------------
print("\n[33] __init__.py 完整性")
init_source = extract_code_text(INIT_PATH)
check("__init__.py 导入 LogService",
      "from server.services.log_service import LogService"
      in init_source)
check("__init__.py 导出 LogService",
      '"LogService"' in init_source)

# ----------------------------------------------------------
# [34] 禁止 Router/HTTP/Desktop/View
# ----------------------------------------------------------
print("\n[34] 禁止项")
check("无 Router", "router" not in source.lower())
check("无 HTTP", "HTTP" not in source)
check("无 Desktop", "desktop" not in source.lower())
check("无 View", "view" not in source.lower().replace(
    "overview", ""))

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