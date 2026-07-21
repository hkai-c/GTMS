"""Test: Settings Schema (Sprint 13 — Task 13.3)

依据 DEVELOPMENT_ROADMAP.md Task 13.3 验收标准。
测试 server/schemas/settings_schema.py 全部 Schema 与代码规范。

测试覆盖：
    - Schema 存在性
    - 字段检查
    - Validation
    - 类型检查
    - extra="forbid"
    - 继承关系
    - Response 字段
    - __init__.py 导出
    - Zero Workflow
    - Zero Status Machine
    - Zero ORM
    - 架构检查
"""

import ast
import os
import re
import sys
from datetime import datetime

from pydantic import BaseModel, ValidationError

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
print("  Task 13.3 — Settings Schema Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [0] 文件存在性检查
# ----------------------------------------------------------
print("\n[0] 文件存在性检查")

SCHEMA_FILE = os.path.join(PROJECT_ROOT, "server", "schemas", "settings_schema.py")
INIT_FILE = os.path.join(PROJECT_ROOT, "server", "schemas", "__init__.py")

check("settings_schema.py 文件存在", os.path.exists(SCHEMA_FILE))
check("__init__.py 文件存在", os.path.exists(INIT_FILE))

# ----------------------------------------------------------
# [1] Schema 导入检查
# ----------------------------------------------------------
print("\n[1] Schema 导入检查")

from server.schemas.settings_schema import (
    SettingsBase,
    SettingsResponse,
    SettingsUpdate,
)
from server.schemas import SettingsBase as SB, SettingsResponse as SR, SettingsUpdate as SU

check("SettingsBase 导入成功", True)
check("SettingsUpdate 导入成功", True)
check("SettingsResponse 导入成功", True)
check("通过 __init__.py 导入 SettingsBase", SB is SettingsBase)
check("通过 __init__.py 导入 SettingsUpdate", SU is SettingsUpdate)
check("通过 __init__.py 导入 SettingsResponse", SR is SettingsResponse)

# ----------------------------------------------------------
# [2] Schema 数量检查
# ----------------------------------------------------------
print("\n[2] Schema 数量检查")

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())

schema_classes = []
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
        for base in node.bases:
            base_name = base.id if isinstance(base, ast.Name) else ""
            if base_name in ("BaseModel", "SettingsBase"):
                schema_classes.append(node.name)
                break

check(f"Schema 类数量 (3~4): {len(schema_classes)}", 3 <= len(schema_classes) <= 4)
check("SettingsBase 存在", "SettingsBase" in schema_classes)
check("SettingsUpdate 存在", "SettingsUpdate" in schema_classes)
check("SettingsResponse 存在", "SettingsResponse" in schema_classes)

# ----------------------------------------------------------
# [3] 继承关系检查
# ----------------------------------------------------------
print("\n[3] 继承关系检查")

check("SettingsBase 继承 BaseModel", issubclass(SettingsBase, BaseModel))
check("SettingsResponse 继承 SettingsBase", issubclass(SettingsResponse, SettingsBase))
check("SettingsUpdate 继承 BaseModel", issubclass(SettingsUpdate, BaseModel))

# ----------------------------------------------------------
# [4] SettingsBase 字段检查
# ----------------------------------------------------------
print("\n[4] SettingsBase 字段检查")

base_fields = SettingsBase.model_fields
check("SettingsBase 字段数量 >= 18", len(base_fields) >= 18)

# 数据库与备份
check("database_path 字段", "database_path" in base_fields)
check("backup_directory 字段", "backup_directory" in base_fields)
check("backup_enabled 字段", "backup_enabled" in base_fields)
check("backup_time 字段", "backup_time" in base_fields)
check("backup_retention_days 字段", "backup_retention_days" in base_fields)

# 上传
check("upload_directory 字段", "upload_directory" in base_fields)
check("max_image_size_mb 字段", "max_image_size_mb" in base_fields)
check("max_document_size_mb 字段", "max_document_size_mb" in base_fields)
check("max_video_size_mb 字段", "max_video_size_mb" in base_fields)

# 通知
check("receipt_delay_hours 字段", "receipt_delay_hours" in base_fields)
check("grinding_delay_hours 字段", "grinding_delay_hours" in base_fields)
check("report_missing_hours 字段", "report_missing_hours" in base_fields)
check("check_interval_minutes 字段", "check_interval_minutes" in base_fields)

# 系统
check("system_name 字段", "system_name" in base_fields)
check("company_name 字段", "company_name" in base_fields)
check("theme 字段", "theme" in base_fields)
check("language 字段", "language" in base_fields)
check("timezone 字段", "timezone" in base_fields)
check("log_retention_days 字段", "log_retention_days" in base_fields)

# ----------------------------------------------------------
# [5] SettingsBase 默认值检查
# ----------------------------------------------------------
print("\n[5] SettingsBase 默认值检查")

base = SettingsBase()
check("backup_enabled 默认 True", base.backup_enabled is True)
check("backup_retention_days 默认 30", base.backup_retention_days == 30)
check("receipt_delay_hours 默认 48", base.receipt_delay_hours == 48)
check("grinding_delay_hours 默认 120", base.grinding_delay_hours == 120)
check("report_missing_hours 默认 72", base.report_missing_hours == 72)
check("check_interval_minutes 默认 60", base.check_interval_minutes == 60)
check("system_name 默认 GTMS", base.system_name == "GTMS")
check("theme 默认 light", base.theme == "light")
check("language 默认 zh-CN", base.language == "zh-CN")
check("timezone 默认 Asia/Shanghai", base.timezone == "Asia/Shanghai")
check("log_retention_days 默认 90", base.log_retention_days == 90)

# ----------------------------------------------------------
# [6] SettingsBase Validation
# ----------------------------------------------------------
print("\n[6] SettingsBase Validation")

# 6.1 backup_retention_days > 0
try:
    SettingsBase(backup_retention_days=0)
    check("backup_retention_days=0 抛出 ValidationError", False)
except ValidationError:
    check("backup_retention_days=0 抛出 ValidationError", True)

try:
    SettingsBase(backup_retention_days=-1)
    check("backup_retention_days=-1 抛出 ValidationError", False)
except ValidationError:
    check("backup_retention_days=-1 抛出 ValidationError", True)

# 6.2 backup_time 格式校验
try:
    SettingsBase(backup_time="25:00")
    check("backup_time=25:00 抛出 ValidationError", False)
except ValidationError:
    check("backup_time=25:00 抛出 ValidationError", True)

try:
    SettingsBase(backup_time="abc")
    check("backup_time=abc 抛出 ValidationError", False)
except ValidationError:
    check("backup_time=abc 抛出 ValidationError", True)

# 6.3 正常值
s = SettingsBase(backup_time="03:30")
check("backup_time=03:30 正常", s.backup_time == "03:30")

# 6.4 max_image_size_mb > 0
try:
    SettingsBase(max_image_size_mb=0)
    check("max_image_size_mb=0 抛出 ValidationError", False)
except ValidationError:
    check("max_image_size_mb=0 抛出 ValidationError", True)

# 6.5 system_name min_length=1
try:
    SettingsBase(system_name="")
    check("system_name='' 抛出 ValidationError", False)
except ValidationError:
    check("system_name='' 抛出 ValidationError", True)

# 6.6 timezone min_length=1
try:
    SettingsBase(timezone="")
    check("timezone='' 抛出 ValidationError", False)
except ValidationError:
    check("timezone='' 抛出 ValidationError", True)

# ----------------------------------------------------------
# [7] SettingsUpdate 字段检查
# ----------------------------------------------------------
print("\n[7] SettingsUpdate 字段检查")

update_fields = SettingsUpdate.model_fields
check("SettingsUpdate 字段数量 >= 18", len(update_fields) >= 18)

# 所有字段应为 Optional
for field_name, field_info in update_fields.items():
    check(f"SettingsUpdate.{field_name} 为 Optional", field_info.default is None)

# 禁止系统字段
check("SettingsUpdate 无 id 字段", "id" not in update_fields)
check("SettingsUpdate 无 created_at 字段", "created_at" not in update_fields)
check("SettingsUpdate 无 updated_at 字段", "updated_at" not in update_fields)

# ----------------------------------------------------------
# [8] SettingsUpdate extra="forbid"
# ----------------------------------------------------------
print("\n[8] SettingsUpdate extra=\"forbid\"")

try:
    SettingsUpdate(invalid_field="test")
    check("extra=forbid 拒绝额外字段", False)
except ValidationError:
    check("extra=forbid 拒绝额外字段", True)

# 空更新应允许
su = SettingsUpdate()
check("空 SettingsUpdate 允许", True)

# 部分更新
su = SettingsUpdate(system_name="New Name")
check("部分更新 system_name", su.system_name == "New Name")

# ----------------------------------------------------------
# [9] SettingsResponse 字段检查
# ----------------------------------------------------------
print("\n[9] SettingsResponse 字段检查")

response_fields = SettingsResponse.model_fields
check("SettingsResponse 有 id 字段", "id" in response_fields)
check("SettingsResponse 有 created_at 字段", "created_at" in response_fields)
check("SettingsResponse 有 updated_at 字段", "updated_at" in response_fields)

# 继承所有 SettingsBase 字段
for field_name in base_fields:
    check(f"SettingsResponse 继承 {field_name}", field_name in response_fields)

# ----------------------------------------------------------
# [10] 类型注解检查
# ----------------------------------------------------------
print("\n[10] 类型注解检查")

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    schema_raw = f.read()

check("所有字段有类型注解 (str)", "str = Field(" in schema_raw)
check("所有字段有类型注解 (int)", "int = Field(" in schema_raw)
check("所有字段有类型注解 (bool)", "bool = Field(" in schema_raw)
check("所有字段有 Field 描述", "description=" in schema_raw)

# 禁止 Any
check("禁止 Any 类型", "Any" not in schema_raw)

# ----------------------------------------------------------
# [11] 架构检查 — 禁止依赖
# ----------------------------------------------------------
print("\n[11] 架构检查 — 禁止依赖")

code_text = extract_code_text(SCHEMA_FILE)

forbidden_modules = [
    ("orm", "ORM"),
    ("sqlalchemy", "ORM"),
    ("Session", "ORM Session"),
    ("router", "Router"),
    ("desktop", "Desktop"),
    ("client", "Desktop/View"),
    ("views", "View"),
    ("scheduler", "Scheduler"),
    ("notification_service", "Notification Service"),
    ("BackupManager", "Backup"),
    ("workflow", "Workflow"),
    ("status_machine", "Status Machine"),
]
for keyword, label in forbidden_modules:
    pattern = re.compile(rf"\b{keyword}\b", re.IGNORECASE)
    found = pattern.search(code_text)
    check(f"禁止依赖 {label}", not found)

# 禁止直接读取配置文件
check("禁止直接读取 config", "config" not in code_text.split("import")[0] if "import" in code_text else True)

# ----------------------------------------------------------
# [12] Zero Workflow / Status Machine
# ----------------------------------------------------------
print("\n[12] Zero Workflow / Status Machine")

check("Zero Workflow", "process_status" not in code_text)
check("Zero Status Machine", "status_machine" not in code_text)

# ----------------------------------------------------------
# [13] 文件头注释检查
# ----------------------------------------------------------
print("\n[13] 文件头注释检查")

check("文件头包含 Sprint 13", "Sprint 13" in schema_raw)
check("文件头包含 Task 13.3", "Task 13.3" in schema_raw)
check("文件头包含 SRS", "SRS" in schema_raw)
check("文件头包含 CODE_WIKI", "CODE_WIKI" in schema_raw)

# ----------------------------------------------------------
# [14] __init__.py 导出检查
# ----------------------------------------------------------
print("\n[14] __init__.py 导出检查")

with open(INIT_FILE, "r", encoding="utf-8") as f:
    init_raw = f.read()

check("导入 settings_schema", "from .settings_schema import" in init_raw)
check("__all__ 包含 SettingsBase", "SettingsBase" in init_raw.split("__all__")[1] if "__all__" in init_raw else False)
check("__all__ 包含 SettingsUpdate", "SettingsUpdate" in init_raw.split("__all__")[1] if "__all__" in init_raw else False)
check("__all__ 包含 SettingsResponse", "SettingsResponse" in init_raw.split("__all__")[1] if "__all__" in init_raw else False)

# ----------------------------------------------------------
# [15] Pydantic v2 特性
# ----------------------------------------------------------
print("\n[15] Pydantic v2 特性")

check("使用 ConfigDict", "ConfigDict" in schema_raw)
check("使用 field_validator", "field_validator" in schema_raw)
check("使用 from_attributes=True", "from_attributes=True" in schema_raw)

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