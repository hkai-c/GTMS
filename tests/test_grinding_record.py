"""GrindingRecord ORM 自测脚本"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import py_compile

# ============================================================
# 1. py_compile
# ============================================================
print("=" * 60)
print("1. py_compile")
print("=" * 60)
files = [
    "server/models/grinding_record.py",
    "server/models/trial_task.py",
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
from server.models import GrindingRecord
print(f"  [OK] GrindingRecord imported: {GrindingRecord.__tablename__}")

# ============================================================
# 3. metadata registration
# ============================================================
print("\n" + "=" * 60)
print("3. metadata")
print("=" * 60)
from server.database.base import Base

assert "grinding_records" in Base.metadata.tables, "grinding_records not in metadata"
table_names = list(Base.metadata.tables.keys())
print(f"  [OK] grinding_records in metadata: True")
print(f"  [OK] Total tables: {len(table_names)}")

# ============================================================
# 4. columns
# ============================================================
print("\n" + "=" * 60)
print("4. columns")
print("=" * 60)

columns = GrindingRecord.__table__.columns
print(f"  [OK] Total columns: {len(columns)}")

# 验证：9 业务 + 6 BaseModel = 15
assert len(columns) == 15, f"Expected 15 columns, got {len(columns)}"
print("  [OK] 15 columns (9 business + 6 BaseModel) ✓")

required_fields = [
    "task_id", "operator_id", "machine_type", "wheel_type", "params",
    "start_time", "end_time", "image_paths", "fail_reason",
    "id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted",
]
found_names = [c.name for c in columns]
for rf in required_fields:
    assert rf in found_names, f"Missing required field: {rf}"
    print(f"  [OK] {rf}")

# ============================================================
# 5. foreign keys
# ============================================================
print("\n" + "=" * 60)
print("5. foreign_keys")
print("=" * 60)

table = GrindingRecord.__table__
fks = list(table.foreign_keys)
print(f"  [OK] {len(fks)} foreign keys found")

for fk in fks:
    target = fk.column
    print(f"  [OK] {fk.parent.name} → {target.table.name}.{target.name}")

expected_targets = {
    ("task_id", "trial_tasks", "id"),
    ("operator_id", "users", "id"),
}
found = set()
for fk in fks:
    found.add((fk.parent.name, fk.column.table.name, fk.column.name))
assert found == expected_targets, f"Expected {expected_targets}, got {found}"
print("  [OK] All foreign keys correct ✓")

# ============================================================
# 6. relationships
# ============================================================
print("\n" + "=" * 60)
print("6. relationships")
print("=" * 60)

mapper = GrindingRecord.__mapper__
rels = list(mapper.relationships)
print(f"  [OK] {len(rels)} relationships found")

for rel in rels:
    print(f"  [OK] {rel.key} → {rel.mapper.class_.__name__}")

assert len(rels) == 2, f"Expected 2 relationships, got {len(rels)}"
rel_keys = [r.key for r in rels]
assert "task" in rel_keys, "Missing 'task' relationship"
assert "operator" in rel_keys, "Missing 'operator' relationship"
print("  [OK] All relationships correct ✓")

# ============================================================
# 7. indexes
# ============================================================
print("\n" + "=" * 60)
print("7. indexes")
print("=" * 60)

indexes = table.indexes
print(f"  [OK] {len(indexes)} explicit indexes")

expected_index_names = {
    "ix_grinding_operator_id",
    "ix_grinding_machine_type",
    "ix_grinding_start_time",
}
found_index_names = {idx.name for idx in indexes}
print(f"  [OK] Found: {found_index_names}")

for idx in indexes:
    print(f"  [OK] {idx.name} on {[c.name for c in idx.columns]}")

assert found_index_names == expected_index_names, \
    f"Expected {expected_index_names}, got {found_index_names}"
print("  [OK] All indexes correct ✓")

# unique constraint on task_id
has_task_id_unique = False
for col in table.columns:
    if col.name == "task_id" and col.unique:
        has_task_id_unique = True
        break
assert has_task_id_unique, "task_id must have unique constraint"
print("  [OK] task_id has unique constraint ✓")

# ============================================================
# 8. repr
# ============================================================
print("\n" + "=" * 60)
print("8. repr")
print("=" * 60)

rec = GrindingRecord(task_id=1, operator_id=2)
r = repr(rec)
assert "GrindingRecord" in r, f"repr missing class name: {r}"
assert "task_id=1" in r, f"repr missing task_id: {r}"
assert "operator_id=2" in r, f"repr missing operator_id: {r}"
print(f"  [OK] repr: {r}")

# ============================================================
# 9. no circular import
# ============================================================
print("\n" + "=" * 60)
print("9. no circular import")
print("=" * 60)
print("  [OK] Import successful, no circular import ✓")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Total tables in metadata: {len(Base.metadata.tables)}")
print(f"  GrindingRecord columns: {len(columns)}")
print(f"  Foreign keys: {len(fks)}")
print(f"  Relationships: {len(rels)}")
print(f"  Indexes: {len(indexes)}")

print("\n=== ALL TESTS PASSED ===")