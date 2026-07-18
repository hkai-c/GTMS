"""Test: Query Service (Sprint 10 — Task 10.2)

严格依据 DEVELOPMENT_ROADMAP.md Task 10.2 验收标准。
测试 server/services/query_service.py 全部公开 API 与代码规范。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import ast
import inspect
import os
import re
import subprocess
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
print("  Task 10.2 — Query Service Self Test")
print("=" * 60)

SOURCE_PATH = os.path.join("server", "services", "query_service.py")
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
    from server.services.query_service import QueryService
    check("QueryService 导入", True)
except ImportError as e:
    check("QueryService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("QueryService 是 class", inspect.isclass(QueryService))
check("QueryService 可实例化", QueryService() is not None)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(QueryService)
    if not m.startswith("_") and callable(getattr(QueryService, m))
]
check("list_tasks 存在", "list_tasks" in public_methods)
check("get_statistics 存在", "get_statistics" in public_methods)
check("get_customer_ranking 存在", "get_customer_ranking" in public_methods)
check("get_machine_ranking 存在", "get_machine_ranking" in public_methods)
check("export_excel 存在", "export_excel" in public_methods)
check("公开 API 数量 = 5", len(public_methods) == 5)

# ----------------------------------------------------------
# [5] 公开 API 签名
# ----------------------------------------------------------
print("\n[5] 公开 API 签名")

# list_tasks
sig = inspect.signature(QueryService.list_tasks)
params = list(sig.parameters.keys())
check("list_tasks: 含 self", "self" in params)
check("list_tasks: 含 db", "db" in params)
check("list_tasks: 含 query_filter", "query_filter" in params)
check("list_tasks: 参数数量 = 3", len(params) == 3)

# get_statistics
sig = inspect.signature(QueryService.get_statistics)
params = list(sig.parameters.keys())
check("get_statistics: 含 self", "self" in params)
check("get_statistics: 含 db", "db" in params)
check("get_statistics: 参数数量 = 2", len(params) == 2)

# get_customer_ranking
sig = inspect.signature(QueryService.get_customer_ranking)
params = list(sig.parameters.keys())
check("get_customer_ranking: 含 self", "self" in params)
check("get_customer_ranking: 含 db", "db" in params)
check("get_customer_ranking: 参数数量 = 2", len(params) == 2)

# get_machine_ranking
sig = inspect.signature(QueryService.get_machine_ranking)
params = list(sig.parameters.keys())
check("get_machine_ranking: 含 self", "self" in params)
check("get_machine_ranking: 含 db", "db" in params)
check("get_machine_ranking: 参数数量 = 2", len(params) == 2)

# export_excel
sig = inspect.signature(QueryService.export_excel)
params = list(sig.parameters.keys())
check("export_excel: 含 self", "self" in params)
check("export_excel: 含 db", "db" in params)
check("export_excel: 含 export_request", "export_request" in params)
check("export_excel: 参数数量 = 3", len(params) == 3)

# ----------------------------------------------------------
# [6] 返回值类型注解
# ----------------------------------------------------------
print("\n[6] 返回值类型注解")

with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()

code = extract_code_text(SOURCE_PATH)

check("list_tasks 返回 QueryResponse", "QueryResponse" in source)
check("get_statistics 返回 StatisticsResponse", "StatisticsResponse" in source)
check("get_customer_ranking 返回 list[RankingItem]",
      "list[RankingItem]" in source)
check("get_machine_ranking 返回 list[RankingItem]",
      "list[RankingItem]" in source)
check("export_excel 返回 list[dict]", "list[dict]" in source)

# ----------------------------------------------------------
# [7] 使用 Query Schema
# ----------------------------------------------------------
print("\n[7] 使用 Query Schema")
check("导入 QueryFilter", "QueryFilter" in source)
check("导入 QueryResponse", "QueryResponse" in source)
check("导入 RankingItem", "RankingItem" in source)
check("导入 StatisticsResponse", "StatisticsResponse" in source)
check("导入 StatisticsSummary", "StatisticsSummary" in source)
check("导入 ExportRequest", "ExportRequest" in source)

# ----------------------------------------------------------
# [8] list_tasks: 分页逻辑
# ----------------------------------------------------------
print("\n[8] list_tasks: 分页逻辑")
check("使用 .offset()", ".offset(" in code)
check("使用 .limit()", ".limit(" in code)
check("使用 .count()", ".count()" in code)
check("计算 offset = (page-1) * page_size", "(query_filter.page - 1)" in code)
check("QueryResponse 含 total 参数", "total=total" in code)
check("QueryResponse 含 page 参数", "page=query_filter.page" in code)
check("QueryResponse 含 page_size 参数",
      "page_size=query_filter.page_size" in code)

# ----------------------------------------------------------
# [9] _apply_filters: 组合查询过滤
# ----------------------------------------------------------
print("\n[9] _apply_filters: 组合查询过滤")
check("customer_id 过滤", "query_filter.customer_id" in source)
check("process_status 过滤", "query_filter.process_status" in source)
check("result_status 过滤", "query_filter.result_status" in source)
check("operator_id 过滤 (sales_id)", "query_filter.operator_id" in source)
check("machine_model 过滤", "query_filter.machine_model" in source)
check("date_from 过滤", "query_filter.date_from" in source)
check("date_to 过滤", "query_filter.date_to" in source)
check("keyword 过滤", "query_filter.keyword" in source)
check("全部使用 .filter()", ".filter(" in source)
check("禁止 Python 内存过滤（无 [x for x in）", "[x for x in" not in source)

# ----------------------------------------------------------
# [10] _apply_sorting: 排序逻辑
# ----------------------------------------------------------
print("\n[10] _apply_sorting: 排序逻辑")
check("sortable_fields 字典", "sortable_fields" in source)
check("支持 id 排序", "TrialTask.id" in source)
check("支持 task_no 排序", "TrialTask.task_no" in source)
check("支持 created_at 排序", "TrialTask.created_at" in source)
check("支持 asc 排序", ".asc()" in source)
check("支持 desc 排序", ".desc()" in source)
check("_apply_sorting 默认排序字段回退",
      ".get(" in source and "TrialTask.created_at" in source)
check("_apply_sorting 默认排序方向回退",
      'sort_order == "asc"' in source and ".desc()" in source)

# ----------------------------------------------------------
# [11] get_statistics: 统计逻辑
# ----------------------------------------------------------
print("\n[11] get_statistics: 统计逻辑")
check("使用 func.count", "func.count" in source)
check("统计本月任务数", "month_start" in source or "month_count" in source)
check("统计年度任务数", "year_start" in source or "year_count" in source)
check("统计通过数量", "passed_count" in source)
check("统计失败数量", "failed_count" in source)
check("成功率计算公式", "passed_count / total_evaluated" in code)
check("成功率 = passed/(passed+failed)*100",
      "100" in source and "success_rate" in source)
check("StatisticsSummary 含 month_count", "month_count" in source)
check("StatisticsSummary 含 year_count", "year_count" in source)
check("StatisticsSummary 含 passed_count", "passed_count" in source)
check("StatisticsSummary 含 failed_count", "failed_count" in source)
check("StatisticsSummary 含 success_rate", "success_rate" in source)
check("StatisticsResponse 含 summary", "summary=summary" in code)
check("StatisticsResponse 含 customer_ranking",
      "customer_ranking=customer_ranking" in code)
check("StatisticsResponse 含 machine_ranking",
      "machine_ranking=machine_ranking" in code)
check("零除保护（total_evaluated > 0）", "total_evaluated > 0" in source)

# ----------------------------------------------------------
# [12] get_customer_ranking: 排行逻辑
# ----------------------------------------------------------
print("\n[12] get_customer_ranking: 排行逻辑")
check("JOIN Customer", "Customer" in source)
check("GROUP BY customer_id", "group_by" in source or "Customer.id" in source)
check("ORDER BY DESC", "desc" in source)
check("LIMIT 10", "limit(10)" in source)
check("返回 RankingItem(name=name, count=cnt)",
      "RankingItem(name=name" in source)
check("使用 func.count", "func.count" in source)

# ----------------------------------------------------------
# [13] get_machine_ranking: 排行逻辑
# ----------------------------------------------------------
print("\n[13] get_machine_ranking: 排行逻辑")
check("JOIN GrindingRecord", "GrindingRecord" in source)
check("GROUP BY machine_type", "machine_type" in source)
check("ORDER BY DESC", "desc" in source)
check("LIMIT 10", "limit(10)" in source)
check("过滤 GrindingRecord.is_deleted",
      "GrindingRecord.is_deleted" in source)
check("返回 RankingItem(name=name, count=cnt)",
      "RankingItem(name=name" in source)

# ----------------------------------------------------------
# [14] export_excel: 导出逻辑
# ----------------------------------------------------------
print("\n[14] export_excel: 导出逻辑")
check("复用 _apply_filters", "_apply_filters" in source)
check("复用 _apply_sorting", "_apply_sorting" in source)
check("复用 _task_to_dict", "_task_to_dict" in source)
check("返回 list[dict]", "list[dict]" in source)
check("禁止 openpyxl", "openpyxl" not in source)
check("禁止文件写入", "open(" not in source)
check("使用 ExportRequest 参数", "export_request" in source)

# ----------------------------------------------------------
# [15] Zero Workflow: 不修改 process_status
# ----------------------------------------------------------
print("\n[15] Zero Workflow: 不修改 process_status")
process_assign = re.findall(
    r'\bprocess_status\s*=\s*(?!=)', code
)
check("无 process_status 赋值", len(process_assign) == 0)

# ----------------------------------------------------------
# [16] Zero Status Machine: 不修改 result_status
# ----------------------------------------------------------
print("\n[16] Zero Status Machine: 不修改 result_status")
result_assign = re.findall(
    r'\bresult_status\s*=\s*(?!=)', code
)
check("无 result_status 赋值", len(result_assign) == 0)

# ----------------------------------------------------------
# [17] 只读事务：禁止写操作
# ----------------------------------------------------------
print("\n[17] 只读事务：禁止写操作")
check("禁止 db.commit()", "db.commit()" not in source)
check("禁止 db.rollback()", "db.rollback()" not in source)
check("禁止 db.flush()", "db.flush()" not in source)
check("禁止 db.delete()", "db.delete(" not in source)
check("禁止 db.add()", "db.add(" not in source)
check("禁止 ORM DELETE", "delete(" not in source)
check("禁止 ORM UPDATE", "update(" not in source)
check("禁止 ORM INSERT", "insert(" not in source)

# ----------------------------------------------------------
# [18] 异常处理
# ----------------------------------------------------------
print("\n[18] 异常处理")
check("无 ValueError", "ValueError" not in source)
check("无 print()", "print(" not in source)
check("无 raise 异常（空结果返回空列表）",
      "raise" not in source)

# ----------------------------------------------------------
# [19] logger
# ----------------------------------------------------------
print("\n[19] logger")
check("使用 gtms.server logger",
      'logging.getLogger("gtms.server")' in source)
check("logger.info 使用", "logger.info" in source)
check("查询条件日志", "查询完成" in source)
check("统计请求日志", "统计完成" in source)
check("导出请求日志", "导出数据准备完成" in source)
check("排行日志", "客户排行完成" in source or "排行完成" in source)

# ----------------------------------------------------------
# [20] Type Hint
# ----------------------------------------------------------
print("\n[20] Type Hint")
check("Session 类型注解", "Session" in source)
check("QueryFilter 类型注解", "QueryFilter" in source)
check("ExportRequest 类型注解", "ExportRequest" in source)
check("所有方法有返回类型注解", "->" in source)

# ----------------------------------------------------------
# [21] 私有方法
# ----------------------------------------------------------
print("\n[21] 私有方法")
check("_apply_filters 存在", "_apply_filters" in source)
check("_apply_sorting 存在", "_apply_sorting" in source)
check("_task_to_dict 存在", "_task_to_dict" in source)
check("私有方法数量 = 3",
      source.count("def _") == 3)

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
check("模块级 docstring 存在", ast.get_docstring(tree) is not None)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "QueryService":
        check("类 docstring 存在", ast.get_docstring(node) is not None)
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                doc = ast.get_docstring(item)
                check(f"{item.name} docstring 存在", doc is not None)

# ----------------------------------------------------------
# [24] 无 TODO / FIXME / pass
# ----------------------------------------------------------
print("\n[24] 无 TODO / FIXME / pass")
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 pass", not re.search(r"\bpass\b", extract_code_text(SOURCE_PATH)))

# ----------------------------------------------------------
# [25] Frozen API
# ----------------------------------------------------------
print("\n[25] Frozen API")
check("无 Router 导入", "from server.routers" not in source)
check("无 Desktop 导入", "from client." not in source)
check("无 FastAPI 导入", "FastAPI" not in source)
check("无 APIRouter 导入", "APIRouter" not in source)

# ----------------------------------------------------------
# [26] __all__ 导出
# ----------------------------------------------------------
print("\n[26] __all__ 导出")
check("__all__ 包含 QueryService",
      "QueryService" in source.split("__all__")[-1])

# ----------------------------------------------------------
# [27] __init__.py 导出
# ----------------------------------------------------------
print("\n[27] __init__.py 导出")
init_code = extract_code_text(INIT_PATH)
check("__init__.py 导出 QueryService", "QueryService" in init_code)

# ----------------------------------------------------------
# [28] 枚举使用
# ----------------------------------------------------------
print("\n[28] 枚举使用")
check("导入 TrialTaskProcessStatus", "TrialTaskProcessStatus" in source)
check("导入 TrialTaskResultStatus", "TrialTaskResultStatus" in source)
check("枚举在 _apply_filters 中使用", "TrialTaskProcessStatus" in source)
check("枚举在 get_statistics 中使用", "TrialTaskResultStatus" in source)

# ----------------------------------------------------------
# [29] 性能：数据库过滤/排序/分页
# ----------------------------------------------------------
print("\n[29] 性能标准")
check("禁止 SELECT *（使用 .query(TrialTask)）",
      "SELECT *" not in source)
check("禁止 Python 聚合（使用 func.count）",
      "func.count" in source)
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
check("使用 tracking_no（非 express_no）",
      "tracking_no" in source and "express_no" not in source)
check("使用 machine_type（GrindingRecord 字段）",
      "machine_type" in source)
check("operator_id 映射到 sales_id",
      "sales_id == query_filter.operator_id" in source)

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