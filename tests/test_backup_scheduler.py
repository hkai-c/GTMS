"""Test: Backup Scheduler (Sprint 13 — Task 13.2)

依据 DEVELOPMENT_ROADMAP.md Task 13.2 验收标准。
测试 Backup Scheduler 的 Job 注册、调度器集成与代码规范。

测试覆盖：
    - Scheduler 创建、单例
    - Job 注册（正确 ID）
    - CronTrigger 验证
    - generate_backup_job() 功能
    - 调用 BackupManager.create_backup()
    - 日志输出
    - 异常传播
    - 架构检查（零业务逻辑、零禁止依赖）
    - 常量检查（无 Magic String / Magic Number）
    - 重复启动 / 停止
"""

import ast
import os
import re
import sys
import time
from pathlib import Path
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
print("  Task 13.2 — Backup Scheduler Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [0] 文件存在性检查
# ----------------------------------------------------------
print("\n[0] 文件存在性检查")

JOBS_FILE = os.path.join(PROJECT_ROOT, "server", "scheduler", "jobs.py")
SCHEDULER_FILE = os.path.join(PROJECT_ROOT, "server", "scheduler", "scheduler.py")
INIT_FILE = os.path.join(PROJECT_ROOT, "server", "scheduler", "__init__.py")
CONSTANTS_FILE = os.path.join(PROJECT_ROOT, "server", "scheduler", "constants.py")
MAIN_FILE = os.path.join(PROJECT_ROOT, "server", "main.py")

check("jobs.py 文件存在", os.path.exists(JOBS_FILE))
check("scheduler.py 文件存在", os.path.exists(SCHEDULER_FILE))
check("__init__.py 文件存在", os.path.exists(INIT_FILE))
check("constants.py 文件存在", os.path.exists(CONSTANTS_FILE))
check("main.py 文件存在", os.path.exists(MAIN_FILE))

# ----------------------------------------------------------
# [1] 架构检查 — 禁止依赖
# ----------------------------------------------------------
print("\n[1] 架构检查 — 禁止依赖")

jobs_code = extract_code_text(JOBS_FILE)
scheduler_code = extract_code_text(SCHEDULER_FILE)

with open(JOBS_FILE, "r", encoding="utf-8") as f:
    raw_jobs_file = f.read()

forbidden_modules = [
    ("router", "Router"),
    ("desktop", "Desktop"),
    ("client", "Desktop/View"),
    ("views", "View"),
    ("sqlalchemy", "ORM"),
    ("Session", "ORM Session"),
    ("workflow", "Workflow"),
    ("status_machine", "Status Machine"),
    ("notification_service", "Notification"),
    ("notification_router", "Notification"),
    ("NotificationService", "Notification"),
]
# generate_backup_job 函数代码文本（专用于检查）
# 提取 generate_backup_job 函数体内的代码
backup_job_func_match = re.search(
    r"def generate_backup_job.*?(?=\n(?:def |\Z|\n__all__))",
    raw_jobs_file,
    re.DOTALL,
)
backup_job_func_text = backup_job_func_match.group(0) if backup_job_func_match else ""

for keyword, label in forbidden_modules:
    pattern = re.compile(rf"\b{keyword}\b", re.IGNORECASE)
    found_in_jobs = pattern.search(backup_job_func_text)
    found_in_scheduler = pattern.search(scheduler_code)
    check(f"禁止依赖 {label} (jobs.py)", not found_in_jobs)
    check(f"禁止依赖 {label} (scheduler.py)", not found_in_scheduler)

# ----------------------------------------------------------
# [2] 常量检查 — constants.py
# ----------------------------------------------------------
print("\n[2] 常量检查 — constants.py")

with open(CONSTANTS_FILE, "r", encoding="utf-8") as f:
    constants_raw = f.read()
with open(JOBS_FILE, "r", encoding="utf-8") as f:
    jobs_raw = f.read()
with open(SCHEDULER_FILE, "r", encoding="utf-8") as f:
    scheduler_raw = f.read()

# 2.1 constants.py 存在性
check("constants.py 包含 JobIds", "class JobIds" in constants_raw)
check("constants.py 包含 SchedulerConfig", "class SchedulerConfig" in constants_raw)

# 2.2 JobIds 完整性
check("JobIds.BACKUP", "BACKUP:" in constants_raw)
check("JobIds.NOTIFICATION", "NOTIFICATION:" in constants_raw)
check("JobIds.REPORT (预留)", "REPORT:" in constants_raw)
check("JobIds.AUTO_CLEANUP (预留)", "AUTO_CLEANUP:" in constants_raw)
check("JobIds.MAIL (预留)", "MAIL:" in constants_raw)
check("JobIds.HEALTH_CHECK (预留)", "HEALTH_CHECK:" in constants_raw)

# 2.3 SchedulerConfig 完整性
check("SchedulerConfig.TIMEZONE", "TIMEZONE:" in constants_raw)
check("SchedulerConfig.BACKUP_CRON", "BACKUP_CRON:" in constants_raw)
check("SchedulerConfig.NOTIFICATION_CRON", "NOTIFICATION_CRON:" in constants_raw)
check("SchedulerConfig.REPORT_CRON (预留)", "REPORT_CRON:" in constants_raw)
check("SchedulerConfig.MAIL_CRON (预留)", "MAIL_CRON:" in constants_raw)
check("SchedulerConfig.AUTO_CLEANUP_CRON (预留)", "AUTO_CLEANUP_CRON:" in constants_raw)

# 2.4 所有 Job 引用统一使用 JobIds
check("scheduler.py 使用 JobIds.BACKUP", "JobIds.BACKUP" in scheduler_raw)
check("scheduler.py 使用 JobIds.NOTIFICATION", "JobIds.NOTIFICATION" in scheduler_raw)

# 2.5 所有 Trigger 引用统一使用 SchedulerConfig
check("scheduler.py 使用 SchedulerConfig.TIMEZONE", "SchedulerConfig.TIMEZONE" in scheduler_raw)
check("scheduler.py 使用 SchedulerConfig.BACKUP_CRON", "SchedulerConfig.BACKUP_CRON" in scheduler_raw)
check("scheduler.py 使用 SchedulerConfig.NOTIFICATION_CRON", "SchedulerConfig.NOTIFICATION_CRON" in scheduler_raw)

# 2.6 禁止硬编码 Job ID 字符串
check("scheduler.py 禁止硬编码 id=\"generate_backup\"", 'id="generate_backup"' not in scheduler_raw)
check("scheduler.py 禁止硬编码 id=\"generate_notifications\"", 'id="generate_notifications"' not in scheduler_raw)
check("scheduler.py 禁止硬编码 timezone=\"Asia/Shanghai\"", 'timezone="Asia/Shanghai"' not in scheduler_raw)

# 2.7 __init__.py 导出 constants
with open(INIT_FILE, "r", encoding="utf-8") as f:
    init_raw = f.read()
check("__init__.py 导出 JobIds", "JobIds" in init_raw.split("__all__")[1] if "__all__" in init_raw else False)
check("__init__.py 导出 SchedulerConfig", "SchedulerConfig" in init_raw.split("__all__")[1] if "__all__" in init_raw else False)

# 2.8 无 Magic String / Magic Number
check("scheduler.py 无直接写死的 Cron 数字", "hour=2" not in scheduler_raw and "minute=0" not in scheduler_raw)

# ----------------------------------------------------------
# [3] Job 注册检查
# ----------------------------------------------------------
print("\n[3] Job 注册检查")

check("scheduler.py 注册 generate_backup_job", "generate_backup_job" in scheduler_raw)
check("使用 JobIds.BACKUP 作为 id", "JobIds.BACKUP" in scheduler_raw)
check("使用 JobIds.NOTIFICATION 作为 id", "JobIds.NOTIFICATION" in scheduler_raw)
check("使用 SchedulerConfig.BACKUP_CRON", "SchedulerConfig.BACKUP_CRON" in scheduler_raw)
check("使用 SchedulerConfig.NOTIFICATION_CRON", "SchedulerConfig.NOTIFICATION_CRON" in scheduler_raw)
check("使用 SchedulerConfig.TIMEZONE", "SchedulerConfig.TIMEZONE" in scheduler_raw)
check("max_instances=1", "max_instances=1" in scheduler_raw)
check("replace_existing=True", "replace_existing=True" in scheduler_raw)

# ----------------------------------------------------------
# [4] generate_backup_job() 功能检查
# ----------------------------------------------------------
print("\n[4] generate_backup_job() 功能检查")

check("调用 BackupManager", "BackupManager" in jobs_raw)
check("调用 create_backup()", "create_backup()" in jobs_raw)
check("记录开始日志", "开始执行数据库备份" in jobs_raw)
check("记录完成日志", "数据库备份完成" in jobs_raw)
check("记录失败日志", "数据库备份失败" in jobs_raw)
check("记录耗时", "耗时" in jobs_raw)
check("使用 gtms.server logger", 'getLogger("gtms.server")' in jobs_raw)

# ----------------------------------------------------------
# [5] 零业务逻辑检查
# ----------------------------------------------------------
print("\n[5] 零业务逻辑检查")

# generate_backup_job 仅调用 BackupManager，不包含任何业务判断
check("不包含 TrialTask", "TrialTask" not in jobs_code)
check("不包含 Customer", "Customer" not in jobs_code)
check("不包含 Inspection", "Inspection" not in jobs_code)
check("不包含 GrindingRecord", "GrindingRecord" not in jobs_code)
check("不包含 process_status", "process_status" not in jobs_code)
check("不包含 result_status", "result_status" not in jobs_code)

# ----------------------------------------------------------
# [6] __init__.py 导出检查
# ----------------------------------------------------------
print("\n[6] __init__.py 导出检查")

with open(INIT_FILE, "r", encoding="utf-8") as f:
    init_raw = f.read()

check("__init__.py 导出 generate_backup_job", "generate_backup_job" in init_raw.split("__all__")[1] if "__all__" in init_raw else False)
check("import generate_backup_job", "from .jobs import generate_backup_job" in init_raw)

# ----------------------------------------------------------
# [7] main.py 启动检查
# ----------------------------------------------------------
print("\n[7] main.py 启动检查")

with open(MAIN_FILE, "r", encoding="utf-8") as f:
    main_raw = f.read()

check("main.py 导入 start_scheduler", "from server.scheduler import start_scheduler" in main_raw)
check("main.py 调用 start_scheduler()", "start_scheduler()" in main_raw)

# ----------------------------------------------------------
# [8] generate_backup_job() 单元测试
# ----------------------------------------------------------
print("\n[8] generate_backup_job() 单元测试")

# 模拟 BackupManager.create_backup() 返回成功
with patch("server.scheduler.jobs.BackupManager") as MockBackupManager:
    mock_instance = MagicMock()
    mock_instance.create_backup.return_value = "/backup/test.db"
    MockBackupManager.return_value = mock_instance

    from server.scheduler.jobs import generate_backup_job

    # [8.1] 正常执行
    generate_backup_job()
    mock_instance.create_backup.assert_called_once()
    check("generate_backup_job() 调用 BackupManager.create_backup()", True)

    # [8.2] 执行异常时正确传播
    mock_instance2 = MagicMock()
    mock_instance2.create_backup.side_effect = RuntimeError("备份失败")
    with patch("server.scheduler.jobs.BackupManager", return_value=mock_instance2):
        # 应该不抛出异常（内部捕获并记录日志）
        try:
            generate_backup_job()
            check("generate_backup_job() 异常不传播", True)
        except Exception:
            check("generate_backup_job() 异常不传播", False)

# ----------------------------------------------------------
# [9] 调度器集成测试
# ----------------------------------------------------------
print("\n[9] 调度器集成测试")

# 停止任何已运行的调度器
from server.scheduler import stop_scheduler

stop_scheduler()

# [9.1] 创建调度器
from server.scheduler import get_scheduler, start_scheduler

scheduler1 = get_scheduler()
check("get_scheduler() 返回调度器", scheduler1 is not None)

# [9.2] 调度器单例
scheduler2 = get_scheduler()
check("调度器单例模式", scheduler1 is scheduler2)

# [9.3] 检查注册的 Job
jobs = scheduler1.get_jobs()
job_ids = [job.id for job in jobs]
check("注册了 generate_notifications Job", "generate_notifications" in job_ids)
check("注册了 generate_backup Job", "generate_backup" in job_ids)

# [9.4] 检查 Backup Job 配置
backup_job = None
for job in jobs:
    if job.id == "generate_backup":
        backup_job = job
        break
check("Backup Job 存在", backup_job is not None)

if backup_job:
    check("Backup Job name 正确", backup_job.name == "数据库备份")
    check("Backup Job max_instances=1", backup_job.max_instances == 1)

# [9.5] 重复启动
start_scheduler()
check("重复启动不报错", True)

# [9.6] 重复停止
stop_scheduler()
stop_scheduler()
check("重复停止不报错", True)

# 重新启动调度器以恢复状态
stop_scheduler()

# ----------------------------------------------------------
# [10] 文件头注释检查
# ----------------------------------------------------------
print("\n[10] 文件头注释检查")

check("jobs.py 包含 Sprint 13", "Sprint 13" in jobs_raw)
check("jobs.py 包含 Task 13.2", "Task 13.2" in jobs_raw)
check("scheduler.py 包含 Sprint 13", "Sprint 13" in scheduler_raw)
check("__init__.py 包含 Sprint 13", "Sprint 13" in init_raw)
check("main.py 包含 Sprint 13", "Sprint 13" in main_raw)

# ----------------------------------------------------------
# [11] 异常处理检查
# ----------------------------------------------------------
print("\n[11] 异常处理检查")

# 检查 generate_backup_job 中没有空 except
try_blocks = re.findall(r"try:.*?except.*?:", jobs_code, re.DOTALL)
check("generate_backup_job 存在 try-except", len(try_blocks) >= 1)

# 检查是否有空 except 块
empty_except = re.search(r"except\s*:\s*\n\s*(pass|#)", jobs_raw)
check("无空 except 块", not empty_except)

# 检查是否有 except Exception: pass 模式
check("异常捕获后有日志记录", "logger.exception" in jobs_raw)

# ----------------------------------------------------------
# [12] 禁止 print() 检查
# ----------------------------------------------------------
print("\n[12] 禁止 print() 检查")

check("jobs.py 禁止 print()", "print(" not in jobs_code)
check("scheduler.py 禁止 print()", "print(" not in scheduler_code)

# ----------------------------------------------------------
# [13] 类型注解检查
# ----------------------------------------------------------
print("\n[13] 类型注解检查")

with open(JOBS_FILE, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())

# 找到 generate_backup_job 函数
backup_job_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "generate_backup_job":
        backup_job_func = node
        break

check("generate_backup_job 函数存在", backup_job_func is not None)
if backup_job_func:
    check("generate_backup_job 有返回类型注解", backup_job_func.returns is not None)

# 检查 constants.py 中 JobIds 有类型注解
with open(CONSTANTS_FILE, "r", encoding="utf-8") as f:
    constants_raw = f.read()
check("JobIds.BACKUP 有类型注解", "BACKUP: str" in constants_raw)

# ============================================================
# 结果汇总
# ============================================================

print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  测试结果: {PASSED}/{total} 通过")
if FAILED > 0:
    print(f"  [FAIL] {FAILED} 条检查未通过")
else:
    print(f"  [PASS] 全部通过！")
print("=" * 60)