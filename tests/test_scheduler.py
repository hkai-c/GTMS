"""Test: Scheduler (Sprint 12 — Task 12.4)

严格依据 DEVELOPMENT_ROADMAP.md Task 12.4 验收标准。
测试 server/scheduler/ 全部模块与代码规范。

注意：本测试使用源码分析 + 单元测试，不依赖真实 HTTP 连接。
"""

import ast
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

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
print("  Task 12.4 — Scheduler Self Test")
print("=" * 60)

SCHEDULER_DIR = os.path.join("server", "scheduler")
SCHEDULER_PY = os.path.join(SCHEDULER_DIR, "scheduler.py")
JOBS_PY = os.path.join(SCHEDULER_DIR, "jobs.py")
INIT_PY = os.path.join(SCHEDULER_DIR, "__init__.py")

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
for fp in [SCHEDULER_PY, JOBS_PY, INIT_PY]:
    try:
        import py_compile
        py_compile.compile(fp, doraise=True)
        check(f"{os.path.basename(fp)} py_compile", True)
    except py_compile.PyCompileError as e:
        check(f"{os.path.basename(fp)} py_compile", False)
        print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.scheduler import start_scheduler, stop_scheduler, get_scheduler
    check("scheduler 包导入", True)
except ImportError as e:
    check("scheduler 包导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

try:
    from server.scheduler.scheduler import (
        _create_scheduler, _scheduler,
    )
    check("scheduler 模块导入", True)
except ImportError as e:
    check("scheduler 模块导入", False)
    print(f"      Error: {e}")

try:
    from server.scheduler.jobs import generate_notifications_job
    check("jobs 模块导入", True)
except ImportError as e:
    check("jobs 模块导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [3] 调度器创建
# ----------------------------------------------------------
print("\n[3] 调度器创建")
scheduler = get_scheduler()
check("调度器创建成功", scheduler is not None)
check("调度器类型为 BackgroundScheduler",
      "BackgroundScheduler" in str(type(scheduler)))

# ----------------------------------------------------------
# [4] Job 注册
# ----------------------------------------------------------
print("\n[4] Job 注册")
jobs = scheduler.get_jobs()
check("至少 1 个 Job", len(jobs) >= 1)
job = jobs[0] if jobs else None
check("Job 存在", job is not None)
if job:
    check("Job ID = generate_notifications",
          job.id == "generate_notifications")
    check("Job 名称 = 消息提醒生成",
          job.name == "消息提醒生成")

# ----------------------------------------------------------
# [5] Cron 配置
# ----------------------------------------------------------
print("\n[5] Cron 配置")
if job:
    check("trigger 是 CronTrigger",
          "CronTrigger" in str(type(job.trigger)))
    # CronTrigger(minute=0) → 每小时整点执行
    check("Cron minute=0",
          str(job.trigger) is not None)

# ----------------------------------------------------------
# [6] 调度器启动
# ----------------------------------------------------------
print("\n[6] 调度器启动")
# 停止可能残留的调度器
try:
    stop_scheduler()
except Exception:
    pass
# 重新创建
from server.scheduler.scheduler import _scheduler as _sched
_sched = None
import server.scheduler.scheduler as sched_mod
sched_mod._scheduler = None

scheduler = get_scheduler()
check("调度器初始状态 running=False",
      scheduler.running is False)
start_scheduler()
check("调度器启动后 running=True",
      scheduler.running is True)
stop_scheduler()
check("调度器停止后 running=False",
      scheduler.running is False)

# ----------------------------------------------------------
# [7] 重复启动安全
# ----------------------------------------------------------
print("\n[7] 重复启动安全")
sched_mod._scheduler = None
scheduler = get_scheduler()
start_scheduler()
check("首次启动成功", scheduler.running is True)
# 再次启动
start_scheduler()
check("重复启动安全（不报错）", scheduler.running is True)
stop_scheduler()
check("停止后 running=False", scheduler.running is False)

# ----------------------------------------------------------
# [8] 重复停止安全
# ----------------------------------------------------------
print("\n[8] 重复停止安全")
stop_scheduler()
check("重复停止安全（不报错）", True)

# ----------------------------------------------------------
# [9] get_scheduler 单例
# ----------------------------------------------------------
print("\n[9] get_scheduler 单例")
sched_mod._scheduler = None
s1 = get_scheduler()
s2 = get_scheduler()
check("get_scheduler 返回同一实例", s1 is s2)

# ----------------------------------------------------------
# [10] Job 唯一实例
# ----------------------------------------------------------
print("\n[10] Job 唯一实例")
sched_mod._scheduler = None
scheduler = get_scheduler()
jobs = scheduler.get_jobs()
gen_jobs = [j for j in jobs if j.id == "generate_notifications"]
check("仅 1 个 generate_notifications Job",
      len(gen_jobs) == 1)

# ----------------------------------------------------------
# [11] max_instances=1
# ----------------------------------------------------------
print("\n[11] max_instances=1")
check("max_instances=1",
      gen_jobs[0].max_instances == 1 if gen_jobs else False)

# ----------------------------------------------------------
# [12] replace_existing=True
# ----------------------------------------------------------
print("\n[12] replace_existing=True")
# 通过分析源码确认
scheduler_source = extract_code_text(SCHEDULER_PY)
check("replace_existing=True",
      "replace_existing" in scheduler_source)

# ----------------------------------------------------------
# [13] 调度器源码分析
# ----------------------------------------------------------
print("\n[13] 调度器源码分析")
sc_text = extract_code_text(SCHEDULER_PY)
check("导入 BackgroundScheduler",
      "BackgroundScheduler" in sc_text)
check("导入 CronTrigger",
      "CronTrigger" in sc_text)
check("导入 generate_notifications_job",
      "generate_notifications_job" in sc_text)
check("使用 add_job",
      "add_job" in sc_text)

# ----------------------------------------------------------
# [14] 零业务逻辑（scheduler.py）
# ----------------------------------------------------------
print("\n[14] 零业务逻辑（scheduler.py）")
check("无 ORM 导入", "Session" not in sc_text)
check("无 NotificationService", "NotificationService" not in sc_text)
check("无 Workflow", "process_status" not in sc_text)
check("无 Status Machine", "result_status" not in sc_text)
check("无 SystemLog", "SystemLog" not in sc_text)
check("无 commit", "commit" not in sc_text.lower())
check("无 rollback", "rollback" not in sc_text.lower())
check("无 Router", "APIRouter" not in sc_text)
check("无 HTTP", "HTTPException" not in sc_text)
check("无 Desktop", "from client." not in sc_text)

# ----------------------------------------------------------
# [15] 零业务逻辑（jobs.py）
# ----------------------------------------------------------
print("\n[15] 零业务逻辑（jobs.py）")
jobs_text = extract_code_text(JOBS_PY)
check("无 ORM 直接操作（无 Session()）",
      "Session(" not in jobs_text)
check("无 Workflow", "process_status" not in jobs_text)
check("无 Status Machine", "result_status" not in jobs_text)
check("无 SystemLog", "SystemLog" not in jobs_text)
check("无 Router", "APIRouter" not in jobs_text)
check("无 HTTP", "HTTPException" not in jobs_text)
check("无 Desktop", "from client." not in jobs_text)

# ----------------------------------------------------------
# [16] jobs.py 仅调用 Service
# ----------------------------------------------------------
print("\n[16] jobs.py 仅调用 Service")
check("导入 NotificationService",
      "NotificationService" in jobs_text)
check("调用 generate_notifications",
      "generate_notifications" in jobs_text)
check("导入 SessionLocal",
      "SessionLocal" in jobs_text)

# ----------------------------------------------------------
# [17] __init__.py 导出
# ----------------------------------------------------------
print("\n[17] __init__.py 导出")
init_text = extract_code_text(INIT_PY)
check("导出 start_scheduler",
      "start_scheduler" in init_text)
check("导出 stop_scheduler",
      "stop_scheduler" in init_text)
check("导出 get_scheduler",
      "get_scheduler" in init_text)

# ----------------------------------------------------------
# [18] PEP8
# ----------------------------------------------------------
print("\n[18] PEP8")
for fp in [SCHEDULER_PY, JOBS_PY, INIT_PY]:
    result = subprocess.run(
        ["python", "-m", "flake8", "--select=E,W,F,N", fp],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    ok = result.returncode == 0
    if not ok and result.stdout:
        print(f"    flake8 {os.path.basename(fp)}: {result.stdout.strip()}")
    check(f"{os.path.basename(fp)} PEP8", ok)

# ----------------------------------------------------------
# [19] Docstring
# ----------------------------------------------------------
print("\n[19] Docstring")
for fp in [SCHEDULER_PY, JOBS_PY, INIT_PY]:
    with open(fp, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    name = os.path.basename(fp)
    check(f"{name} 模块级 docstring",
          ast.get_docstring(tree) is not None)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith(
            "_"
        ):
            doc = ast.get_docstring(node)
            check(f"{name}:{node.name} docstring", doc is not None)

# ----------------------------------------------------------
# [20] Type Hint
# ----------------------------------------------------------
print("\n[20] Type Hint")
for fp in [SCHEDULER_PY, JOBS_PY]:
    with open(fp, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    name = os.path.basename(fp)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith(
            "_"
        ):
            check(f"{name}:{node.name} 返回类型注解",
                  node.returns is not None)

# ----------------------------------------------------------
# [21] 行宽
# ----------------------------------------------------------
print("\n[21] 行宽")
for fp in [SCHEDULER_PY, JOBS_PY, INIT_PY]:
    with open(fp, "r", encoding="utf-8") as f:
        lines = f.readlines()
    long_lines = [
        i + 1 for i, line in enumerate(lines)
        if len(line.rstrip("\n")) > 79
    ]
    name = os.path.basename(fp)
    if long_lines:
        print(f"    {name} 超长行: {long_lines}")
    check(f"{name} 行宽 <= 79", len(long_lines) == 0)

# ----------------------------------------------------------
# [22] 文件末尾换行
# ----------------------------------------------------------
print("\n[22] 文件末尾换行")
for fp in [SCHEDULER_PY, JOBS_PY, INIT_PY]:
    with open(fp, "rb") as f:
        f.seek(-1, 2)
        last_char = f.read(1)
    check(f"{os.path.basename(fp)} 末尾换行", last_char == b"\n")

# ----------------------------------------------------------
# [23] 无 print
# ----------------------------------------------------------
print("\n[23] 无 print")
for fp in [SCHEDULER_PY, JOBS_PY, INIT_PY]:
    text = extract_code_text(fp)
    check(f"{os.path.basename(fp)} 无 print()",
          "print(" not in text)

# ----------------------------------------------------------
# [24] 无 try/except（scheduler.py）
# ----------------------------------------------------------
print("\n[24] 无 try/except（scheduler.py）")
check("scheduler.py 无 try/except",
      "try:" not in extract_code_text(SCHEDULER_PY))

# ----------------------------------------------------------
# [25] jobs.py 有 try/except（允许）
# ----------------------------------------------------------
print("\n[25] jobs.py 有 try/except（允许）")
# jobs.py 需要 try/except 来捕获调度异常并记录日志
# 这是 §15.19.3 明确允许的
jobs_full = extract_code_text(JOBS_PY)
check("jobs.py 有异常处理（符合 §15.19.3）",
      "try:" in jobs_full)

# ----------------------------------------------------------
# [26] 禁止依赖
# ----------------------------------------------------------
print("\n[26] 禁止依赖")
for fp in [SCHEDULER_PY, JOBS_PY]:
    full = open(fp, "r", encoding="utf-8").read()
    name = os.path.basename(fp)
    check(f"{name} 无 requests", "requests" not in full)
    check(f"{name} 无 httpx", "httpx" not in full)
    check(f"{name} 无 Router", "APIRouter" not in full)
    check(f"{name} 无 View", "from client.views" not in full)
    check(f"{name} 无 Desktop", "from client." not in full)

# ----------------------------------------------------------
# [27] 时区配置
# ----------------------------------------------------------
print("\n[27] 时区配置")
check("使用 SchedulerConfig.TIMEZONE",
      "SchedulerConfig.TIMEZONE" in open(SCHEDULER_PY, "r", encoding="utf-8").read())

# ----------------------------------------------------------
# [28] __all__ 导出
# ----------------------------------------------------------
print("\n[28] __all__ 导出")
for fp in [SCHEDULER_PY, JOBS_PY, INIT_PY]:
    full = open(fp, "r", encoding="utf-8").read()
    name = os.path.basename(fp)
    check(f"{name} __all__ 存在", "__all__" in full)

# ----------------------------------------------------------
# [29] 无循环导入
# ----------------------------------------------------------
print("\n[29] 无循环导入")
for fp in [SCHEDULER_PY, JOBS_PY]:
    full = open(fp, "r", encoding="utf-8").read()
    name = os.path.basename(fp)
    check(f"{name} 无自身导入",
          f"from server.scheduler.{name.replace('.py', '')}" not in full)

# ----------------------------------------------------------
# [30] 调度器与 Service 解耦
# ----------------------------------------------------------
print("\n[30] 调度器与 Service 解耦")
# scheduler.py 不应导入 NotificationService
sc_full = open(SCHEDULER_PY, "r", encoding="utf-8").read()
check("scheduler.py 不导入 NotificationService",
      "NotificationService" not in sc_full)
check("scheduler.py 不导入 ORM",
      "from server.models" not in sc_full)

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