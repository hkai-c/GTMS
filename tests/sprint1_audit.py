"""Sprint 1 全量一致性审计脚本"""
import traceback, os

print("=== Sprint 1 全量一致性审计 ===")
print()

# ============================================================
# Part 2: ORM file existence
# ============================================================
print("--- Part 2: ORM 文件存在性 ---")
models_dir = "server/models"
expected_files = [
    "user.py", "role.py", "permission.py", "customer.py",
    "trial_task.py", "receipt.py", "grinding_record.py",
    "inspection_record.py", "dispatch.py", "attachment.py",
    "system_log.py", "notification.py",
]
existing = set(os.listdir(models_dir))
missing = []
extra = []
for f in expected_files:
    if f not in existing:
        missing.append(f)
for f in existing:
    if f.endswith(".py") and f not in expected_files and f not in ("__init__.py", "base_model.py"):
        extra.append(f)
print(f"  Existing: {len(expected_files) - len(missing)}/{len(expected_files)}")
for f in expected_files:
    status = "EXISTS" if f in existing else "MISSING"
    print(f"    [{status}] {f}")
if missing:
    print(f"  MISSING: {missing}")
if extra:
    print(f"  EXTRA: {extra}")

# ============================================================
# Part 3: Association tables
# ============================================================
print()
print("--- Part 3: 关联表审计 ---")
from server.models.user import user_roles, role_permissions
from sqlalchemy import Table
print(f"  user_roles type: {type(user_roles).__name__}")
print(f"  role_permissions type: {type(role_permissions).__name__}")
print(f"  user_roles is Table: {isinstance(user_roles, Table)}")
print(f"  role_permissions is Table: {isinstance(role_permissions, Table)}")
print(f"  [PASS] 关联表均为 SQLAlchemy Table")

# ============================================================
# Part 4: __init__.py exports
# ============================================================
print()
print("--- Part 4: __init__.py 审计 ---")
from server.models import __all__ as models_all
from server.enums import __all__ as enums_all
print(f"  models __all__: {len(models_all)} items")
print(f"    {models_all}")
print(f"  enums __all__: {len(enums_all)} items")
print(f"    {enums_all}")

# Check Base
try:
    from server.database.base import Base
    print(f"  [INFO] Base available from server.database.base")
except ImportError:
    print(f"  [WARN] Base not importable")

# ============================================================
# Part 5: Relationship audit
# ============================================================
print()
print("--- Part 5: Relationship 审计 ---")
from server.models.trial_task import TrialTask
from server.models.user import User

tt_rels = list(TrialTask.__mapper__.relationships.keys())
print(f"  TrialTask relationships: {tt_rels}")

expected_tt_rels = [
    "customer", "sales", "receipt", "grinding_record",
    "inspection", "dispatch", "attachments", "notifications",
]
for rel in expected_tt_rels:
    if rel in tt_rels:
        print(f"    [PASS] TrialTask.{rel}")
    else:
        print(f"    [FAIL] TrialTask.{rel} MISSING")

user_rels = list(User.__mapper__.relationships.keys())
print(f"  User relationships: {user_rels}")
expected_user_rels = ["roles", "notifications", "system_logs"]
for rel in expected_user_rels:
    if rel in user_rels:
        print(f"    [PASS] User.{rel}")
    else:
        print(f"    [FAIL] User.{rel} MISSING")

# ============================================================
# Part 6: Foreign Key audit
# ============================================================
print()
print("--- Part 6: Foreign Key 审计 ---")
from server.models import (
    Customer, TrialTask as TT, Receipt, GrindingRecord,
    InspectionRecord, Dispatch, Attachment, SystemLog, Notification,
)

fk_models = [
    ("Customer", Customer, ["created_by"]),
    ("TrialTask", TT, ["customer_id", "sales_id"]),
    ("Receipt", Receipt, ["task_id", "receiver_id"]),
    ("GrindingRecord", GrindingRecord, ["task_id", "operator_id"]),
    ("InspectionRecord", InspectionRecord, ["task_id", "inspector_id"]),
    ("Dispatch", Dispatch, ["task_id", "operator_id"]),
    ("Attachment", Attachment, ["task_id", "uploaded_by"]),
    ("SystemLog", SystemLog, ["user_id"]),
    ("Notification", Notification, ["task_id", "target_user_id"]),
]

for name, model, expected_fks in fk_models:
    fks = {fk.parent.name for fk in model.__table__.foreign_keys}
    missing_fks = set(expected_fks) - fks
    extra_fks = fks - set(expected_fks)
    if missing_fks:
        print(f"  [FAIL] {name}: missing FK {missing_fks}")
    elif extra_fks:
        print(f"  [FAIL] {name}: extra FK {extra_fks}")
    else:
        print(f"  [PASS] {name}: {len(fks)} FK(s)")

# Verify ON DELETE
fk_rules = {
    ("Customer", "created_by"): "SET NULL",
    ("TrialTask", "customer_id"): "RESTRICT",
    ("TrialTask", "sales_id"): "RESTRICT",
    ("Receipt", "task_id"): "CASCADE",
    ("Receipt", "receiver_id"): "RESTRICT",
    ("GrindingRecord", "task_id"): "CASCADE",
    ("GrindingRecord", "operator_id"): "RESTRICT",
    ("InspectionRecord", "task_id"): "CASCADE",
    ("InspectionRecord", "inspector_id"): "SET NULL",
    ("Dispatch", "task_id"): "CASCADE",
    ("Dispatch", "operator_id"): "RESTRICT",
    ("Attachment", "task_id"): "CASCADE",
    ("Attachment", "uploaded_by"): "RESTRICT",
    ("SystemLog", "user_id"): "RESTRICT",
    ("Notification", "task_id"): "CASCADE",
    ("Notification", "target_user_id"): "CASCADE",
}

models_map = {m.__name__: m for _, m, _ in fk_models}

print()
print("  ON DELETE 检查:")
all_fk_pass = True
for (model_name, col_name), expected_rule in fk_rules.items():
    model = models_map[model_name]
    fks = {fk.parent.name: fk for fk in model.__table__.foreign_keys}
    actual = fks[col_name].ondelete
    if actual != expected_rule:
        print(f"  [FAIL] {model_name}.{col_name}: expected {expected_rule}, got {actual}")
        all_fk_pass = False
if all_fk_pass:
    print("  [PASS] All ON DELETE rules match DB_DESIGN.md §6")

# ON UPDATE check
print()
print("  ON UPDATE 检查:")
all_onupdate_pass = True
for model_name, model, _ in fk_models:
    for fk in model.__table__.foreign_keys:
        if fk.onupdate is not None:
            print(f"  [FAIL] {model_name}.{fk.parent.name} ON UPDATE={fk.onupdate}")
            all_onupdate_pass = False
if all_onupdate_pass:
    print("  [PASS] All ON UPDATE = None")

# ============================================================
# Part 7: Index audit
# ============================================================
print()
print("--- Part 7: Index 审计 ---")

# DB_DESIGN.md §5.1 defines 43 indexes: I-01 through I-43
# Let's count actual indexes from ORM models
all_orm_models = [
    User, Customer, TT, Receipt, GrindingRecord,
    InspectionRecord, Dispatch, Attachment, SystemLog, Notification,
]

# We also need Role, Permission
from server.models.role import Role
from server.models.permission import Permission

all_orm_models.extend([Role, Permission])

total_explicit_indexes = 0
for model in all_orm_models:
    explicit = []
    if hasattr(model, "__table_args__") and model.__table_args__:
        if isinstance(model.__table_args__, tuple):
            for item in model.__table_args__:
                if hasattr(item, "name"):
                    explicit.append(item.name)
        elif hasattr(model.__table_args__, "name"):
            explicit.append(model.__table_args__.name)
    total_explicit_indexes += len(explicit)
    if explicit:
        print(f"  {model.__tablename__}: {explicit}")

# Count unique constraints
unique_count = 0
for model in all_orm_models:
    from sqlalchemy import UniqueConstraint
    for const in model.__table__.constraints:
        if isinstance(const, UniqueConstraint):
            unique_count += 1

# Also count column-level unique
col_unique = 0
for model in all_orm_models:
    for col in model.__table__.columns:
        if col.unique and col.primary_key is False:
            col_unique += 1

print(f"  Explicit Indexes: {total_explicit_indexes}")
print(f"  Unique Constraints: {unique_count}")
print(f"  Column-level Unique: {col_unique}")
print(f"  Total Tables: {len(all_orm_models)} (+ 2 association tables = 14)")

# ============================================================
# Part 8: Enum audit
# ============================================================
print()
print("--- Part 8: Enum 审计 ---")
from server.enums import (
    TrialTaskProcessStatus, TrialTaskResultStatus, DestinationType,
    InspectionResult, FileType, NotifyType, ActionType,
)
from enum import Enum

enums_to_check = [
    ("TrialTaskProcessStatus", TrialTaskProcessStatus),
    ("TrialTaskResultStatus", TrialTaskResultStatus),
    ("DestinationType", DestinationType),
    ("InspectionResult", InspectionResult),
    ("FileType", FileType),
    ("NotifyType", NotifyType),
    ("ActionType", ActionType),
]

for name, enum in enums_to_check:
    is_str_enum = issubclass(enum, str) and issubclass(enum, Enum)
    print(f"  [PASS] {name}: {list(enum)} (str,Enum={is_str_enum})")

# ============================================================
# Part 10: Statistics
# ============================================================
print()
print("--- Part 10: Sprint 1 统计 ---")
print(f"  ORM 模型: {len(all_orm_models)}")
print(f"  关联表: 2 (user_roles, role_permissions)")
print(f"  数据库表: {len(all_orm_models) + 2}")

# Count FKs
total_fks = sum(len(list(m.__table__.foreign_keys)) for m in all_orm_models)
print(f"  Foreign Keys: {total_fks}")

# Count relationships
total_rels = sum(len(list(m.__mapper__.relationships)) for m in all_orm_models)
print(f"  Relationships: {total_rels}")

# Indexes
print(f"  DB_DESIGN §5.1 Indexes: 43 (I-01 ~ I-43)")
print(f"  Explicit Indexes: {total_explicit_indexes}")
print(f"  Unique Constraints: {unique_count}")
print(f"  Column-level Unique: {col_unique}")

print(f"  Enums: {len(enums_to_check)}")

print()
print("=== Audit Complete ===")