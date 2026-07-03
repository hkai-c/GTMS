"""InspectionRecord ORM 自测脚本"""

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
    "server/enums/inspection_result.py",
    "server/models/inspection_record.py",
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
from server.enums import InspectionResult
from server.models import InspectionRecord
print(f"  [OK] InspectionResult: {[e.value for e in InspectionResult]}")
print(f"  [OK] InspectionRecord imported: {InspectionRecord.__tablename__}")

# ============================================================
# 3. metadata
# ============================================================
print("\n" + "=" * 60)
print("3. metadata")
print("=" * 60)
from server.database.base import Base

assert "inspection_records" in Base.metadata.tables, "inspection_records not in metadata"
table_names = list(Base.metadata.tables.keys())
print(f"  [OK] inspection_records in metadata: True")
print(f"  [OK] Total tables: {len(table_names)}")

# ============================================================
# 4. columns
# ============================================================
print("\n" + "=" * 60)
print("4. columns")
print("=" * 60)

columns = InspectionRecord.__table__.columns
print(f"  [OK] Total columns: {len(columns)}")

# 验证：6 业务 + 6 BaseModel = 12
assert len(columns) == 12, f"Expected 12 columns, got {len(columns)}"
print("  [OK] 12 columns (6 business + 6 BaseModel) ✓")

required_fields = [
    "task_id", "report_path", "accuracy", "roughness",
    "result", "inspector_id",
    "id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted",
]
found_names = [c.name for c in columns]
for rf in required_fields:
    assert rf in found_names, f"Missing required field: {rf}"
    print(f"  [OK] {rf}")

# 验证 result 是 SAEnum
result_col = columns.get("result")
assert result_col is not None
assert hasattr(result_col.type, "enums"), "result must be SAEnum"
print(f"  [OK] result is SAEnum(InspectionResult): {list(result_col.type.enums)}")

# ============================================================
# 5. foreign keys
# ============================================================
print("\n" + "=" * 60)
print("5. foreign_keys")
print("=" * 60)

table = InspectionRecord.__table__
fks = list(table.foreign_keys)
print(f"  [OK] {len(fks)} foreign keys found")

for fk in fks:
    target = fk.column
    print(f"  [OK] {fk.parent.name} → {target.table.name}.{target.name} "
          f"(ondelete={fk.ondelete})")

expected_targets = {
    ("task_id", "trial_tasks", "id"),
    ("inspector_id", "users", "id"),
}
found = set()
for fk in fks:
    found.add((fk.parent.name, fk.column.table.name, fk.column.name))
assert found == expected_targets, f"Expected {expected_targets}, got {found}"
print("  [OK] All foreign keys correct ✓")

# 验证 inspector_id FK 为 SET NULL
inspector_fk = [fk for fk in fks if fk.parent.name == "inspector_id"][0]
assert inspector_fk.ondelete == "SET NULL", \
    f"inspector_id ondelete should be SET NULL, got {inspector_fk.ondelete}"
print("  [OK] inspector_id ondelete=SET NULL ✓")

# ============================================================
# 6. relationships
# ============================================================
print("\n" + "=" * 60)
print("6. relationships")
print("=" * 60)

mapper = InspectionRecord.__mapper__
rels = list(mapper.relationships)
print(f"  [OK] {len(rels)} relationships found")

for rel in rels:
    print(f"  [OK] {rel.key} → {rel.mapper.class_.__name__}")

assert len(rels) == 2, f"Expected 2 relationships, got {len(rels)}"
rel_keys = [r.key for r in rels]
assert "task" in rel_keys, "Missing 'task' relationship"
assert "inspector" in rel_keys, "Missing 'inspector' relationship"
print("  [OK] All relationships correct ✓")

# ============================================================
# 7. indexes
# ============================================================
print("\n" + "=" * 60)
print("7. indexes")
print("=" * 60)

indexes = table.indexes
print(f"  [OK] {len(indexes)} explicit indexes (per §5.1)")

for idx in indexes:
    print(f"  [OK] {idx.name} on {[c.name for c in idx.columns]}")

# 验证：无额外索引（仅 PRIMARY + UNIQUE）
assert len(indexes) == 0, f"Expected 0 explicit indexes, got {len(indexes)}"
print("  [OK] No extra indexes (per §5.1) ✓")

# 验证 task_id unique
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

rec = InspectionRecord(task_id=1, report_path="/reports/r1.pdf")
r = repr(rec)
assert "InspectionRecord" in r, f"repr missing class name: {r}"
assert "task_id=1" in r, f"repr missing task_id: {r}"
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
print(f"  InspectionRecord columns: {len(columns)}")
print(f"  Foreign keys: {len(fks)}")
print(f"  Relationships: {len(rels)}")
print(f"  Indexes: {len(indexes)}")

print("\n=== ALL TESTS PASSED ===")