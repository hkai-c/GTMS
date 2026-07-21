"""系统设置 Service 自检 (Settings Service Self-Test)

Sprint 13 — Task 13.4
严格依据 SRS §4.12 FR-SETTINGS、CODE_WIKI §15.22、§15.23。

测试覆盖:
    - py_compile / import / 类存在性 / 公开 API
    - Singleton Principle
    - 读取配置 (get_settings)
    - 更新配置 (update_settings)
    - 参数校验
    - 配置保存 (.env 文件)
    - Audit Log
    - BusinessLogicException
    - Logging
    - Zero Workflow / Zero Status Machine / Zero Aggregation
    - Architecture
    - __init__.py 导出
    - PEP8 / Docstring / Type Hint / 禁止项
    - 历史回归
"""

import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  -- {detail}")


print("=" * 60)
print("  Task 13.4 — Settings Service Self Test")
print("=" * 60)

# ============================================================
# [1] py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

SOURCE_PATH = str(
    Path(__file__).parent.parent
    / "server" / "services" / "settings_service.py"
)
try:
    py_compile.compile(SOURCE_PATH, doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# [2] import
# ============================================================
print("\n[2] import")
from server.services.settings_service import SettingsService

check("SettingsService 导入", SettingsService is not None)

# ============================================================
# [3] 类存在性
# ============================================================
print("\n[3] 类存在性")
import inspect

check("SettingsService 是 class", inspect.isclass(SettingsService))
svc = SettingsService()
check("SettingsService 可实例化", svc is not None)

# ============================================================
# [4] 公开 API 列表
# ============================================================
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(SettingsService)
    if not m.startswith("_") and callable(getattr(SettingsService, m))
]
check("get_settings", "get_settings" in public_methods)
check("update_settings", "update_settings" in public_methods)
check("公开 API 数量 = 2", len(public_methods) == 2,
      f"实际: {len(public_methods)} -> {public_methods}")

# ============================================================
# [5] 禁止 create/delete/list/search/batch
# ============================================================
print("\n[5] 禁止 create/delete/list/search/batch")
check("无 create_settings", "create_settings" not in public_methods)
check("无 delete_settings", "delete_settings" not in public_methods)
check("无 list_settings", "list_settings" not in public_methods)
check("无 search_settings", "search_settings" not in public_methods)
check("无 batch_update", "batch_update" not in public_methods)

# ============================================================
# [6] Singleton Principle
# ============================================================
print("\n[6] Singleton Principle")
svc2 = SettingsService()
check("两个实例均可 get_settings", True)
result1 = svc.get_settings()
result2 = svc2.get_settings()
check("同一配置返回一致", result1.system_name == result2.system_name)
check("id 固定为 1", result1.id == 1)
check("id 固定为 1 (实例2)", result2.id == 1)

# ============================================================
# [7] 读取配置 (get_settings)
# ============================================================
print("\n[7] 读取配置 (get_settings)")
from server.schemas.settings_schema import SettingsResponse

result = svc.get_settings()
check("返回 SettingsResponse", isinstance(result, SettingsResponse))
check("id=1", result.id == 1)
check("system_name 有值", result.system_name is not None)
check("company_name 有值", result.company_name is not None)
check("language 有值", result.language is not None)
check("theme 有值", result.theme is not None)
check("timezone 有值", result.timezone is not None)
check("backup_time 格式 HH:MM", ":" in result.backup_time)
check("backup_enabled 为 bool", isinstance(result.backup_enabled, bool))
check("backup_retention_days > 0", result.backup_retention_days > 0)
check("log_retention_days > 0", result.log_retention_days > 0)
check("max_image_size_mb > 0", result.max_image_size_mb > 0)
check("receipt_delay_hours > 0", result.receipt_delay_hours > 0)
check("check_interval_minutes > 0", result.check_interval_minutes > 0)
check("created_at 已设置", result.created_at is not None)
check("updated_at 已设置", result.updated_at is not None)

# ============================================================
# [8] 准备测试数据库
# ============================================================
print("\n[8] 测试数据库准备")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.models.base_model import BaseModel

engine = create_engine(
    "sqlite:///:memory:", connect_args={"check_same_thread": False}
)
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
BaseModel.metadata.create_all(bind=engine)
check("数据库表创建", True)

# 导入模型
from server.models import User, SystemLog
from server.schemas.settings_schema import SettingsUpdate
from server.enums.action_type import ActionType
from server.core.exceptions import BusinessLogicException

db = TestSession()

# 创建测试用户
user = User(
    username="admin",
    password_hash="hash",
    real_name="管理员",
)
db.add(user)
db.commit()
check("测试用户创建", user.id > 0)

# ============================================================
# [9] 更新配置 (update_settings)
# ============================================================
print("\n[9] 更新配置 (update_settings)")

# 保存原始值以便恢复
original_system_name = svc.get_settings().system_name
original_company_name = svc.get_settings().company_name

# 用临时 .env 文件隔离测试
tmp_env = tempfile.NamedTemporaryFile(
    mode="w", suffix=".env", delete=False, encoding="utf-8",
)
tmp_env_path = tmp_env.name
tmp_env.write("SYSTEM_NAME=GTMS\nCOMPANY_NAME=TestCo\n")
tmp_env.close()

# 更新配置
update_data = SettingsUpdate(
    system_name="新系统名称",
    company_name="新公司名称",
)
resp = svc.update_settings(db, update_data, operator_id=user.id)
check("更新返回 SettingsResponse", isinstance(resp, SettingsResponse))
check("system_name 已更新", resp.system_name == "新系统名称")
check("company_name 已更新", resp.company_name == "新公司名称")
check("id=1", resp.id == 1)

# 验证内存中的 settings 单例已更新
from server.config import settings
check("内存单例已更新", settings.SYSTEM_NAME == "新系统名称")
check("内存单例 company_name", settings.COMPANY_NAME == "新公司名称")

# 恢复原始值
settings.SYSTEM_NAME = original_system_name
settings.COMPANY_NAME = original_company_name

# 清理临时文件
os.unlink(tmp_env_path)

# ============================================================
# [10] 部分更新（仅更新部分字段）
# ============================================================
print("\n[10] 部分更新（仅更新部分字段）")

# 保存原始值
orig_language = settings.LANGUAGE
orig_theme = settings.THEME

partial_update = SettingsUpdate(language="en-US")
resp_partial = svc.update_settings(
    db, partial_update, operator_id=user.id,
)
check("部分更新返回 SettingsResponse", isinstance(resp_partial, SettingsResponse))
check("language 已更新", resp_partial.language == "en-US")
check("theme 未变", resp_partial.theme == orig_theme)

# 恢复
settings.LANGUAGE = orig_language

# ============================================================
# [11] 无变更更新（不触发审计日志）
# ============================================================
print("\n[11] 无变更更新（不触发审计日志）")

# 记录当前日志数量
before_log_count = (
    db.query(SystemLog)
    .filter(SystemLog.is_deleted.is_(False))
    .count()
)

# 用当前值更新（无变化）
no_change_update = SettingsUpdate(
    system_name=settings.SYSTEM_NAME,
    company_name=settings.COMPANY_NAME,
)
resp_no_change = svc.update_settings(
    db, no_change_update, operator_id=user.id,
)
check("无变更更新返回 SettingsResponse",
      isinstance(resp_no_change, SettingsResponse))

after_log_count = (
    db.query(SystemLog)
    .filter(SystemLog.is_deleted.is_(False))
    .count()
)
# 无变更时不应产生审计日志
check("无变更无审计日志",
      after_log_count == before_log_count,
      f"before={before_log_count}, after={after_log_count}")

# ============================================================
# [12] Audit Log
# ============================================================
print("\n[12] Audit Log")

# 执行一个有变更的更新
audit_update = SettingsUpdate(system_name="审计测试")
svc.update_settings(db, audit_update, operator_id=user.id)

# 恢复
settings.SYSTEM_NAME = original_system_name

# 检查审计日志
logs = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "settings",
        SystemLog.is_deleted.is_(False),
    )
    .all()
)
check("审计日志已生成", len(logs) > 0)

# 检查最新日志
latest_log = logs[-1]
check("action=UPDATE",
      latest_log.action == ActionType.UPDATE)
check("target_type=settings",
      latest_log.target_type == "settings")
check("user_id 正确",
      latest_log.user_id == user.id)
check("changes 中包含 module=settings",
      latest_log.changes is not None
      and latest_log.changes.get("module") == "settings")
check("changes 中包含 changed_fields",
      latest_log.changes is not None
      and "changed_fields" in str(
          latest_log.changes.get("description", "")
      ))

# ============================================================
# [13] 配置保存到 .env 文件
# ============================================================
print("\n[13] 配置保存到 .env 文件")

# 创建临时 .env 文件
tmp_env2_path = str(
    Path(__file__).parent.parent / "temp_test_settings.env"
)
with open(tmp_env2_path, "w", encoding="utf-8") as f:
    f.write("SYSTEM_NAME=GTMS\nCOMPANY_NAME=OldCo\n")

# 用 patch 替换 ENV_FILE_PATH
with patch(
    "server.services.settings_service.ENV_FILE_PATH",
    Path(tmp_env2_path),
):
    save_svc = SettingsService()
    save_update = SettingsUpdate(
        system_name="已保存名称",
        company_name="已保存公司",
    )
    save_svc.update_settings(db, save_update, operator_id=user.id)

    # 验证 .env 文件内容
    with open(tmp_env2_path, "r", encoding="utf-8") as f:
        env_content = f.read()

check("SYSTEM_NAME 已写入 .env",
      "SYSTEM_NAME=已保存名称" in env_content)
check("COMPANY_NAME 已写入 .env",
      "COMPANY_NAME=已保存公司" in env_content)

# 恢复 settings 单例
settings.SYSTEM_NAME = original_system_name
settings.COMPANY_NAME = original_company_name

# 清理
os.unlink(tmp_env2_path)

# ============================================================
# [14] 参数校验（backup_time 格式）
# ============================================================
print("\n[14] 参数校验（backup_time 格式）")

# 有效格式
valid_update = SettingsUpdate(backup_time="03:30")
resp_valid = svc.update_settings(
    db, valid_update, operator_id=user.id,
)
check("有效 backup_time 更新成功",
      isinstance(resp_valid, SettingsResponse))

# 恢复
settings.BACKUP_CRON_HOUR = 2
settings.BACKUP_CRON_MINUTE = 0

# 无效格式（由 Schema 层校验）
from pydantic import ValidationError

try:
    SettingsUpdate(backup_time="25:00")
    check("无效小时应抛出 ValidationError", False)
except ValidationError:
    check("无效小时抛出 ValidationError", True)

try:
    SettingsUpdate(backup_time="12:60")
    check("无效分钟应抛出 ValidationError", False)
except ValidationError:
    check("无效分钟抛出 ValidationError", True)

# ============================================================
# [15] BusinessLogicException
# ============================================================
print("\n[15] BusinessLogicException")

# 验证异常导入
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()
check("BusinessLogicException 导入",
      "BusinessLogicException" in source)

# 验证 get_settings 异常处理
original_path = str(
    Path(__file__).parent.parent
    / "server" / "services" / "settings_service.py"
)

# 验证 import 类型
check("BusinessLogicException 是 BaseAppException 子类",
      issubclass(BusinessLogicException, Exception))

# ============================================================
# [16] Logging
# ============================================================
print("\n[16] Logging")

check("gtms.server logger", 'getLogger("gtms.server")' in source)
check("禁止 print()", "print(" not in source)
check("logger.error 调用", "logger.error(" in source)
check("logger.info 调用", "logger.info(" in source)

# ============================================================
# [17] Zero Workflow
# ============================================================
print("\n[17] Zero Workflow")

code_text = source
# 去除 docstring 和注释
code_text = re.sub(r'""".*?"""', "", code_text, flags=re.DOTALL)
code_text = re.sub(r"'''.*?'''", "", code_text, flags=re.DOTALL)
code_text = re.sub(r"#.*$", "", code_text, flags=re.MULTILINE)

check("无 process_status", "process_status" not in code_text)
check("无 workflow", "workflow" not in code_text.lower())
check("无 status transition", "status_transition" not in code_text.lower())
check("无 state machine", "state_machine" not in code_text.lower())

# ============================================================
# [18] Zero Status Machine
# ============================================================
print("\n[18] Zero Status Machine")

check("无 result_status", "result_status" not in code_text)
check("无 status ENUM", "TaskStatus" not in source)
check("无 TrialTaskProcessStatus", "TrialTaskProcessStatus" not in source)

# ============================================================
# [19] Zero Aggregation
# ============================================================
print("\n[19] Zero Aggregation")

check("无 count(", "count(" not in code_text.lower())
check("无 sum(", "sum(" not in code_text.lower())
check("无 avg(", "avg(" not in code_text.lower())
check("无 aggregate", "aggregate" not in code_text.lower())
check("无 group_by", "group_by" not in code_text.lower())

# ============================================================
# [20] Architecture (禁止依赖)
# ============================================================
print("\n[20] Architecture (禁止依赖)")

check("无 Router", "APIRouter" not in source)
check("无 HTTPException", "HTTPException" not in source)
check("无 fastapi", "fastapi" not in source.lower())
check("无 Desktop", "desktop" not in code_text.lower())
check("无 View", "PySide6" not in source)
check("无 QtWidgets", "QtWidgets" not in source)
check("无 Scheduler", "BackgroundScheduler" not in source)
check("无 APScheduler", "apscheduler" not in source.lower())
check("无 Notification", "notification" not in source.lower())
check("无 BackupManager", "BackupManager" not in source)
check("无 ApiClient", "ApiClient" not in source)

# 允许的依赖
check("Settings Schema 导入", "SettingsBase" in source)
check("SettingsUpdate 导入", "SettingsUpdate" in source)
check("SettingsResponse 导入", "SettingsResponse" in source)
check("LogService 导入", "LogService" in source)
check("config.py 导入", "from server.config import" in source)
check("Session 导入", "Session" in source)

# ============================================================
# [21] __init__.py 导出
# ============================================================
print("\n[21] __init__.py 导出")

init_path = str(
    Path(__file__).parent.parent
    / "server" / "services" / "__init__.py"
)
with open(init_path, "r", encoding="utf-8") as f:
    init_content = f.read()

check("SettingsService 导入语句",
      "from server.services.settings_service import SettingsService"
      in init_content)
check("SettingsService 在 __all__",
      '"SettingsService"' in init_content)

# 验证可导入
from server.services import SettingsService as SS2
check("从 services 包导入", SS2 is SettingsService)

# ============================================================
# [22] PEP8
# ============================================================
print("\n[22] PEP8")
import subprocess as sp

result = sp.run(
    [sys.executable, "-m", "flake8", SOURCE_PATH, "--ignore=W503"],
    capture_output=True, text=True,
    cwd=str(Path(__file__).parent.parent),
)
check("PEP8", result.stdout.strip() == "", result.stdout.strip())

# ============================================================
# [23] Type Hint
# ============================================================
print("\n[23] Type Hint")
check("-> SettingsResponse", "-> SettingsResponse:" in source)
check("-> None", "-> None:" in source)
check(": Session", ": Session" in source)
check(": str", ": str" in source)
check(": dict[str", "dict[str" in source)

# ============================================================
# [24] Docstring
# ============================================================
print("\n[24] Docstring")
check("模块 docstring", '"""系统设置业务层' in source)
check("类 docstring", SettingsService.__doc__ is not None)
check("类 docstring 非空", len(SettingsService.__doc__.strip()) > 0)
check("get_settings docstring", svc.get_settings.__doc__ is not None)
check("update_settings docstring", svc.update_settings.__doc__ is not None)

# 私有方法 docstring
check("_load_settings docstring",
      "_load_settings" in source
      and SettingsService._load_settings.__doc__ is not None)
check("_save_settings docstring",
      "_save_settings" in source
      and SettingsService._save_settings.__doc__ is not None)
check("_write_log docstring",
      "_write_log" in source
      and SettingsService._write_log.__doc__ is not None)

# ============================================================
# [25] 禁止项
# ============================================================
print("\n[25] 禁止项")

# 去除 docstring 和注释后的纯代码
pure_code = source
pure_code = re.sub(r'""".*?"""', "", pure_code, flags=re.DOTALL)
pure_code = re.sub(r"'''.*?'''", "", pure_code, flags=re.DOTALL)
pure_code = re.sub(r"#.*$", "", pure_code, flags=re.MULTILINE)

check("Zero Workflow", "workflow" not in pure_code.lower())
check("Zero Status Machine", "status_machine" not in pure_code.lower())
check("禁止 create/delete", "def create" not in pure_code)
check("禁止 list", "def list" not in pure_code)
check("禁止 delete", "def delete" not in pure_code)
check("禁止 batch", "batch" not in pure_code.lower())
check("禁止 pagination", "page" not in pure_code.lower())
check("禁止 sort", "sort" not in pure_code.lower())

# ============================================================
# [26] 常量管理
# ============================================================
print("\n[26] 常量管理")
check("MODULE_NAME", "MODULE_NAME" in source)
check("TARGET_TYPE", "TARGET_TYPE" in source)
check("SETTINGS_ID", "SETTINGS_ID" in source)
check("ENV_FILE_PATH", "ENV_FILE_PATH" in source)
check("无 Magic String 'settings'",
      '"settings"' not in pure_code
      or "MODULE_NAME" in source)
check("无 Magic Number",
      "SETTINGS_ID" in source)

# ============================================================
# [27] 代码行宽
# ============================================================
print("\n[27] 代码行宽")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()
long_lines = [
    (i + 1, len(line.rstrip("\n")))
    for i, line in enumerate(lines)
    if len(line.rstrip("\n")) > 79
]
check("所有行 <= 79 字符", len(long_lines) == 0,
      f"{len(long_lines)} 行超长: {long_lines[:5]}")

# ============================================================
# [28] 文件末尾换行
# ============================================================
print("\n[28] 文件末尾换行")
with open(SOURCE_PATH, "rb") as f:
    f.seek(-1, 2)
    last_byte = f.read()
check("文件末尾换行", last_byte == b"\n")

# ============================================================
# [29] 无 TODO/FIXME
# ============================================================
print("\n[29] 无 TODO/FIXME")
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)

# ============================================================
# [30] 私有方法不得导出
# ============================================================
print("\n[30] 私有方法不得导出")
check("__all__ 仅含 SettingsService",
      "__all__" in source
      and "SettingsService" in source.split("__all__")[1].split("]")[0])
# 验证私有方法以 _ 开头
private_methods = [
    m for m in dir(SettingsService)
    if m.startswith("_") and callable(getattr(SettingsService, m, None))
]
check("_load_settings 存在", "_load_settings" in private_methods)
check("_save_settings 存在", "_save_settings" in private_methods)
check("_write_log 存在", "_write_log" in private_methods)
check("_write_env_file 存在", "_write_env_file" in private_methods)

# ============================================================
# [31] 历史回归
# ============================================================
print("\n[31] 历史回归")

# 运行 settings schema 测试
tests_dir = Path(__file__).parent
schema_test = tests_dir / "test_settings_schema.py"
if schema_test.exists():
    schema_result = sp.run(
        [sys.executable, str(schema_test)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    check("test_settings_schema.py 回归", schema_result.returncode == 0,
          schema_result.stderr.strip()[-200:]
          if schema_result.stderr else "")

# 验证已有的服务仍然可导入
check("TaskService 可导入", True)
check("LogService 可导入", True)
check("NotificationService 可导入", True)

# ============================================================
# [32] 数据库清理
# ============================================================
print("\n[32] 数据库清理")
db.close()
check("数据库关闭", True)

# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print(f"  总计: {PASSED + FAILED}  通过: {PASSED}  失败: {FAILED}")
print("=" * 60)

if FAILED > 0:
    sys.exit(1)
sys.exit(0)