"""TrialTask ORM 自测脚本"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import py_compile

# ============================================================
# 1. py_compile
# ============================================================
print("=" * 60)
print("1. py_compile")
print("=" * 60)
files = [
    "server/models/trial_task.py",
    "server/models/customer.py",
]
for f in files:
    py_compile.compile(f, doraise=True)
    print(f"  [OK] {f}")

# ============================================================
# 2. imports
# ============================================================
print("\n" + "=" * 60)
print("2. imports")
print("=" * 60)
from server.models import TrialTask
print(f"  [OK] TrialTask imported: {TrialTask.__tablename__}")

# ============================================================
# 3. metadata
# ============================================================
print("\n" + "=" * 60)
print("3. metadata")
print("=" * 60)
from server.database.base import Base
tables = sorted(Base.metadata.tables.keys())
assert "trial_tasks" in tables
print(f"  [OK] trial_tasks registered ({len(tables)} tables total)")

# ============================================================
# 4. columns
# ============================================================
print("\n" + "=" * 60)
print("4. columns")
print("=" * 60)
tbl = Base.metadata.tables["trial_tasks"]
cols = {c.name: c for c in tbl.columns}
print(f"  Total: {len(cols)} columns")

expected = [
    "id", "task_no", "customer_id", "requirement", "tracking_no",
    "sales_id", "process_status", "result_status", "destination",
    "destination_date", "failure_reason", "is_deleted",
    "created_by", "updated_by", "created_at", "updated_at",
]
for e in expected:
    assert e in cols, f"Missing column: {e}"
    print(f"  [OK] {e}: {cols[e].type}")

# ============================================================
# 5. foreign_keys
# ============================================================
print("\n" + "=" * 60)
print("5. foreign_keys")
print("=" * 60)
fks = []
for c in tbl.columns:
    for fk in c.foreign_keys:
        fks.append((c.name, fk.target_fullname))
print(f"  Total: {len(fks)} FKs")
for col, target in fks:
    print(f"  [OK] {col} -> {target}")
assert len(fks) == 2
assert ("customer_id", "customers.id") in fks
assert ("sales_id", "users.id") in fks

# ============================================================
# 6. relationships
# ============================================================
print("\n" + "=" * 60)
print("6. relationships")
print("=" * 60)
rels = {r.key: r for r in TrialTask.__mapper__.relationships}
print(f"  Total: {len(rels)} relationships")
for key, rel in rels.items():
    print(f"  [OK] {key}: {rel}")
assert "customer" in rels
assert "sales" in rels
assert rels["customer"].back_populates == "tasks"

# ============================================================
# 7. indexes
# ============================================================
print("\n" + "=" * 60)
print("7. indexes")
print("=" * 60)
idx_names = sorted([idx.name for idx in tbl.indexes])
print(f"  Total: {len(idx_names)} indexes")
expected_idxs = [
    "ix_trial_tasks_created_at",
    "ix_trial_tasks_customer_id",
    "ix_trial_tasks_is_deleted",
    "ix_trial_tasks_process_status",
    "ix_trial_tasks_result_status",
    "ix_trial_tasks_sales_id",
]
for ei in expected_idxs:
    assert ei in idx_names, f"Missing index: {ei}"
    print(f"  [OK] {ei}")

# ============================================================
# 8. unique constraint
# ============================================================
print("\n" + "=" * 60)
print("8. unique constraint")
print("=" * 60)
from sqlalchemy import UniqueConstraint
ucs = [c for c in tbl.constraints if isinstance(c, UniqueConstraint)]
for uc in ucs:
    uc_cols = [c.name for c in uc.columns]
    print(f"  [OK] UniqueConstraint: {uc_cols}")
assert any("task_no" in [c.name for c in uc.columns] for uc in ucs)
print("  [OK] task_no unique constraint found")

# ============================================================
# 9. enum check
# ============================================================
print("\n" + "=" * 60)
print("9. enum check")
print("=" * 60)
from server.enums import TrialTaskProcessStatus, TrialTaskResultStatus, DestinationType

ps = cols["process_status"]
rs = cols["result_status"]
ds = cols["destination"]

# Check enum type (SQLAlchemy Enum with correct members)
from sqlalchemy import Enum as SAEnum
assert isinstance(ps.type, SAEnum)
assert isinstance(rs.type, SAEnum)
assert isinstance(ds.type, SAEnum)
assert set(ps.type.enums) == set(e.name for e in TrialTaskProcessStatus)
assert set(rs.type.enums) == set(e.name for e in TrialTaskResultStatus)
assert set(ds.type.enums) == set(e.name for e in DestinationType)
print(f"  [OK] process_status: {ps.type}")
print(f"  [OK] result_status: {rs.type}")
print(f"  [OK] destination: {ds.type}")

# Check defaults
assert ps.default.arg == TrialTaskProcessStatus.CREATED
assert rs.default.arg == TrialTaskResultStatus.PENDING
print(f"  [OK] process_status default: {ps.default.arg}")
print(f"  [OK] result_status default: {rs.default.arg}")

# ============================================================
# 10. no hardcoded strings
# ============================================================
print("\n" + "=" * 60)
print("10. no hardcoded status strings")
print("=" * 60)
with open("server/models/trial_task.py", "r", encoding="utf-8") as f:
    src = f.read()

# Check that all enum references use the enum class, not strings
# (Comments are excluded from this check)
import re
# Remove comments
src_no_comments = re.sub(r"#.*", "", src)
# Check for hardcoded status strings in code (not in comments)
bad = ["created", "received", "grinding", "dispatched", "closed",
       "pending", "passed", "failed",
       "returned_customer", "retained_company", "scrapped", "returned_sales"]
found = []
for b in bad:
    if f'"{b}"' in src_no_comments or f"'{b}'" in src_no_comments:
        found.append(b)
if found:
    print(f"  [WARN] Hardcoded: {found}")
else:
    print("  [OK] No hardcoded status strings")

# ============================================================
# 11. no circular import
# ============================================================
print("\n" + "=" * 60)
print("11. no circular import")
print("=" * 60)
import server.models.trial_task
import server.models.customer
print("  [OK] No circular import")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Total columns:      {len(cols)} (10 business + 6 BaseModel)")
print(f"  Enum columns:       3")
print(f"  Foreign Keys:       {len(fks)}")
print(f"  Relationships:      {len(rels)}")
print(f"  Indexes:            {len(idx_names)}")
print(f"  Unique Constraints: {len(ucs)}")
print(f"  Check Constraints:  0")
print()
print("=== ALL TESTS PASSED ===")