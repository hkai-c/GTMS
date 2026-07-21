"""Test: Backup Manager (Sprint 13 — Task 13.1)

依据 DEVELOPMENT_ROADMAP.md Task 13.1 验收标准。
测试 server/utils/backup.py BackupManager 全部 Public API 与代码规范。

测试覆盖：
    - create_backup() 成功 / 数据库不存在
    - restore() 成功 / 备份文件不存在 / 路径无效
    - cleanup_old_backups() 正常清理 / 自定义保留天数 / 无效参数
    - 重复备份（每次生成独立文件）
    - 保留策略（仅清理过期文件）
    - 非法路径
    - 异常处理（无空 except、无吞异常）
    - 架构检查（无禁止依赖）
    - 常量检查（无 Magic String / Magic Number）
    - 日志检查（使用 gtms.server logger）
"""

import ast
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

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
print("  Task 13.1 — Backup Manager Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [0] 文件存在性检查
# ----------------------------------------------------------
print("\n[0] 文件存在性检查")

BACKUP_FILE = os.path.join(PROJECT_ROOT, "server", "utils", "backup.py")
check("backup.py 文件存在", os.path.exists(BACKUP_FILE))

INIT_FILE = os.path.join(PROJECT_ROOT, "server", "utils", "__init__.py")
check("__init__.py 文件存在", os.path.exists(INIT_FILE))

# ----------------------------------------------------------
# [1] 架构检查 — 禁止依赖
# ----------------------------------------------------------
print("\n[1] 架构检查 — 禁止依赖")

code_text = extract_code_text(BACKUP_FILE)

forbidden_modules = [
    ("scheduler", "Scheduler"),
    ("notification", "Notification"),
    ("router", "Router"),
    ("desktop", "Desktop"),
    ("client", "Desktop/View"),
    ("views", "View"),
    ("sqlalchemy", "ORM"),
    ("Session", "ORM Session"),
    ("workflow", "Workflow"),
    ("status_machine", "Status Machine"),
]
for keyword, label in forbidden_modules:
    pattern = re.compile(rf"\b{keyword}\b", re.IGNORECASE)
    found = pattern.search(code_text)
    check(f"禁止依赖 {label}", not found)

# ----------------------------------------------------------
# [2] 常量检查 — 无 Magic String / Magic Number
# ----------------------------------------------------------
print("\n[2] 常量检查")

check("BACKUP_FILE_PREFIX 常量存在", "BACKUP_FILE_PREFIX" in code_text)
check("BACKUP_FILE_SUFFIX 常量存在", "BACKUP_FILE_SUFFIX" in code_text)
check("DEFAULT_RETENTION_DAYS 常量存在", "DEFAULT_RETENTION_DAYS" in code_text)
check("TIMESTAMP_FORMAT 常量存在", "TIMESTAMP_FORMAT" in code_text)

# 检查常量是否在代码中使用
with open(BACKUP_FILE, "r", encoding="utf-8") as f:
    raw_code = f.read()

check("BACKUP_FILE_PREFIX 在代码中引用", raw_code.count("BACKUP_FILE_PREFIX") >= 2)
check("BACKUP_FILE_SUFFIX 在代码中引用", raw_code.count("BACKUP_FILE_SUFFIX") >= 2)
check("DEFAULT_RETENTION_DAYS 在代码中引用", raw_code.count("DEFAULT_RETENTION_DAYS") >= 2)
check("TIMESTAMP_FORMAT 在代码中引用", raw_code.count("TIMESTAMP_FORMAT") >= 2)

# ----------------------------------------------------------
# [3] 日志检查 — 使用 gtms.server logger
# ----------------------------------------------------------
print("\n[3] 日志检查")

check("使用 gtms.server logger", 'getLogger("gtms.server")' in raw_code)
check("使用 logger.info()", "logger.info(" in raw_code)
check("使用 logger.error()", "logger.error(" in raw_code)
check("禁止 print()", "print(" not in code_text)

# ----------------------------------------------------------
# [4] 异常处理检查
# ----------------------------------------------------------
print("\n[4] 异常处理检查")

check("使用 BusinessLogicException", "BusinessLogicException" in raw_code)
check("禁止空 except", "except:" not in raw_code)
check("禁止 except Exception: pass", "except Exception:" not in raw_code or "pass" not in raw_code.split("except Exception:")[-1].split("\n")[0] if "except Exception:" in raw_code else True)

# ----------------------------------------------------------
# [5] Public API 检查
# ----------------------------------------------------------
print("\n[5] Public API 检查")

# 解析 AST 获取类方法
with open(BACKUP_FILE, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())

# 找到 BackupManager 类
backup_manager_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "BackupManager":
        backup_manager_class = node
        break

check("BackupManager 类存在", backup_manager_class is not None)

public_methods = []
for node in backup_manager_class.body:
    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        public_methods.append(node.name)

check(f"Public API 数量 = 3 (实际: {len(public_methods)})", len(public_methods) == 3)
check("create_backup 存在", "create_backup" in public_methods)
check("restore 存在", "restore" in public_methods)
check("cleanup_old_backups 存在", "cleanup_old_backups" in public_methods)

# ----------------------------------------------------------
# [6] __init__.py 导出检查
# ----------------------------------------------------------
print("\n[6] __init__.py 导出检查")

with open(INIT_FILE, "r", encoding="utf-8") as f:
    init_content = f.read()

check("__init__.py 导出 BackupManager", "BackupManager" in init_content)
check("__all__ 包含 BackupManager", "BackupManager" in init_content.split("__all__")[1] if "__all__" in init_content else False)

# ----------------------------------------------------------
# [7] create_backup() 功能测试
# ----------------------------------------------------------
print("\n[7] create_backup() 功能测试")

# 创建临时目录
tmp_dir = tempfile.mkdtemp(prefix="gtms_test_backup_")
tmp_db_dir = Path(tmp_dir) / "database"
tmp_db_dir.mkdir(parents=True)
tmp_backup_dir = Path(tmp_dir) / "backup"
tmp_backup_dir.mkdir(parents=True)

# 创建临时数据库文件
tmp_db_path = tmp_db_dir / "gtms.db"
tmp_db_path.write_text("test database content")

from server.utils.backup import (
    BACKUP_FILE_PREFIX,
    BACKUP_FILE_SUFFIX,
    BackupManager,
    TIMESTAMP_FORMAT,
)

# [7.1] 正常备份 — 使用 mock 替换内部方法
manager = BackupManager()
with patch.object(manager, "_backup_dir", tmp_backup_dir):
    with patch.object(manager, "_db_path", tmp_db_path):
        backup_path = manager.create_backup()
        check("create_backup() 返回路径", isinstance(backup_path, str) and len(backup_path) > 0)
        check("备份文件存在", Path(backup_path).exists())
        check("备份文件内容匹配", Path(backup_path).read_text() == "test database content")

        # [7.2] 重复备份 — 每次生成独立文件
        import time as time_mod
        time_mod.sleep(1.1)  # 确保时间戳不同
        backup_path2 = manager.create_backup()
        check("重复备份不覆盖", backup_path != backup_path2)
        check("重复备份文件存在", Path(backup_path2).exists())

        # [7.3] 数据库文件不存在
        non_existent_path = tmp_db_dir / "nonexistent.db"
        with patch.object(manager, "_db_path", non_existent_path):
            try:
                manager.create_backup()
                check("数据库不存在时抛出异常", False)
            except Exception as e:
                check("数据库不存在时抛出异常", True)
                check("异常消息包含'数据库文件不存在'", "数据库文件不存在" in str(e))

# ----------------------------------------------------------
# [8] restore() 功能测试
# ----------------------------------------------------------
print("\n[8] restore() 功能测试")

# 重新创建测试环境
tmp_dir2 = tempfile.mkdtemp(prefix="gtms_test_restore_")
tmp_db_dir2 = Path(tmp_dir2) / "database"
tmp_db_dir2.mkdir(parents=True)
tmp_backup_dir2 = Path(tmp_dir2) / "backup"
tmp_backup_dir2.mkdir(parents=True)

tmp_db_path2 = tmp_db_dir2 / "gtms.db"
tmp_db_path2.write_text("original db content")

# [8.1] 正常恢复
manager2 = BackupManager()
with patch.object(manager2, "_backup_dir", tmp_backup_dir2):
    with patch.object(manager2, "_db_path", tmp_db_path2):
        # 先创建备份，再修改原文件，最后恢复
        backup_path3 = manager2.create_backup()
        tmp_db_path2.write_text("modified content")
        manager2.restore(backup_path3)
        check("restore() 恢复成功", tmp_db_path2.read_text() == "original db content")

        # [8.2] 备份文件不存在
        try:
            manager2.restore(str(tmp_backup_dir2 / "nonexistent.db"))
            check("备份文件不存在时抛出异常", False)
        except Exception as e:
            check("备份文件不存在时抛出异常", True)
            check("异常消息包含'备份文件不存在'", "备份文件不存在" in str(e))

        # [8.3] 备份路径是目录而非文件
        try:
            manager2.restore(str(tmp_backup_dir2))
            check("备份路径是目录时抛出异常", False)
        except Exception as e:
            check("备份路径是目录时抛出异常", True)
            check("异常消息包含'不是有效的文件'", "不是有效的文件" in str(e))

# ----------------------------------------------------------
# [9] cleanup_old_backups() 功能测试
# ----------------------------------------------------------
print("\n[9] cleanup_old_backups() 功能测试")

tmp_dir3 = tempfile.mkdtemp(prefix="gtms_test_cleanup_")
tmp_db_dir3 = Path(tmp_dir3) / "database"
tmp_db_dir3.mkdir(parents=True)
tmp_backup_dir3 = Path(tmp_dir3) / "backup"
tmp_backup_dir3.mkdir(parents=True)

tmp_db_path3 = tmp_db_dir3 / "gtms.db"
tmp_db_path3.write_text("test content")

# 创建不同日期的备份文件
old_time = datetime.now() - timedelta(days=60)
recent_time = datetime.now() - timedelta(days=10)

old_backup = tmp_backup_dir3 / f"{BACKUP_FILE_PREFIX}{old_time.strftime(TIMESTAMP_FORMAT)}{BACKUP_FILE_SUFFIX}"
recent_backup = tmp_backup_dir3 / f"{BACKUP_FILE_PREFIX}{recent_time.strftime(TIMESTAMP_FORMAT)}{BACKUP_FILE_SUFFIX}"
non_backup_file = tmp_backup_dir3 / "other_file.txt"

old_backup.write_text("old backup")
recent_backup.write_text("recent backup")
non_backup_file.write_text("not a backup")

# 设置文件修改时间
os.utime(str(old_backup), (old_time.timestamp(), old_time.timestamp()))
os.utime(str(recent_backup), (recent_time.timestamp(), recent_time.timestamp()))

manager3 = BackupManager()
with patch.object(manager3, "_backup_dir", tmp_backup_dir3):
    with patch.object(manager3, "_db_path", tmp_db_path3):

        # [9.1] 正常清理 — 保留 30 天
        cleaned = manager3.cleanup_old_backups(30)
        check("清理旧备份成功", cleaned >= 0)
        check("旧备份已删除", not old_backup.exists())
        check("近期备份保留", recent_backup.exists())
        check("非备份文件保留", non_backup_file.exists())

        # [9.2] 无过期文件时清理
        cleaned2 = manager3.cleanup_old_backups(30)
        check("无过期文件清理返回 0", cleaned2 == 0)

        # [9.3] 自定义保留天数
        cleaned3 = manager3.cleanup_old_backups(5)
        check("自定义保留天数清理", cleaned3 >= 0)

        # [9.4] retention_days = 0 抛出异常
        try:
            manager3.cleanup_old_backups(0)
            check("retention_days=0 时抛出异常", False)
        except Exception as e:
            check("retention_days=0 时抛出异常", True)
            check("异常消息包含'保留天数必须大于 0'", "保留天数必须大于 0" in str(e))

        # [9.5] retention_days 负数抛出异常
        try:
            manager3.cleanup_old_backups(-1)
            check("retention_days=-1 时抛出异常", False)
        except Exception as e:
            check("retention_days=-1 时抛出异常", True)

# ----------------------------------------------------------
# [10] 异常处理 — 无吞异常
# ----------------------------------------------------------
print("\n[10] 异常处理 — 无吞异常")

# 检查每个 try-except 块中是否都有 raise 或日志
try_blocks = re.findall(r"try:.*?except.*?:", code_text, re.DOTALL)
check("存在 try-except 块", len(try_blocks) > 0)

# 检查空 except 块
empty_except_pattern = re.compile(r"except\s*:\s*\n\s*(pass|#)")
empty_except_found = empty_except_pattern.search(raw_code)
check("无空 except 块", not empty_except_found)

# ----------------------------------------------------------
# [11] 类型注解检查
# ----------------------------------------------------------
print("\n[11] 类型注解检查")

check("create_backup 有返回类型注解", "-> str:" in code_text)
check("restore 有返回类型注解", "-> None:" in code_text)
check("cleanup_old_backups 有返回类型注解", "-> int:" in code_text)

# ----------------------------------------------------------
# [12] 文件头注释检查
# ----------------------------------------------------------
print("\n[12] 文件头注释检查")

check("文件头包含 Sprint 13", "Sprint 13" in raw_code)
check("文件头包含 Task 13.1", "Task 13.1" in raw_code)
check("文件头包含 CODE_WIKI", "CODE_WIKI" in raw_code)

# ----------------------------------------------------------
# 清理临时目录
# ----------------------------------------------------------
shutil.rmtree(tmp_dir, ignore_errors=True)
shutil.rmtree(tmp_dir2, ignore_errors=True)
shutil.rmtree(tmp_dir3, ignore_errors=True)

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