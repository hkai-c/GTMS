"""Receipt ORM 自测脚本"""

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
    "server/models/receipt.py",
    "server/models/trial_task.py",
    "server/models/user.py",
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
from server.models import Receipt
print(f"  [OK] Receipt imported: {Receipt.__tablename__}")

# ============================================================
# 3. metadata registration
# ============================================================
print("\n" + "=" * 60)
print("3. metadata")
print("=" * 60)
from server.database.base import Base

assert "receipts" in Base.metadata.tables, "receipts not registered in metadata"
table_names = list(Base.metadata.tables.keys())
receipt_in = "receipts" in table_names
print(f"  [OK] receipts in metadata: {receipt_in}")
print(f"  [OK] Total tables: {len(table_names)}")

# ============================================================
# 4. columns count
# ============================================================
print("\n" + "=" * 60)
print("4. columns")
print("=" * 60)

columns = Receipt.__table__.columns
print(f"  [OK] Total columns: {len(columns)}")

# 验证：4 业务 + 6 BaseModel = 10
assert len(columns) == 10, f"Expected 10 columns, got {len(columns)}"
print("  [OK] 10 columns (4 business + 6 BaseModel) ✓")

# 验证必须字段存在
required_fields = [
    "task_id", "received_at", "receiver_id", "image_paths",
    "id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted",
]
for col in columns:
    if col.name in required_fields:
        print(f"  [OK] {col.name} exists")

# 确认所有必须字段都找到
found_names = [c.name for c in columns]
for rf in required_fields:
    assert rf in found_names, f"Missing required field: {rf}"

# ============================================================
# 5. foreign keys
# ============================================================
print("\n" + "=" * 60)
print("5. foreign_keys")
print("=" * 60)

table = Receipt.__table__
fks = list(table.foreign_keys)
print(f"  [OK] {len(fks)} foreign keys found")

for fk in fks:
    target = fk.column
    print(f"  [OK] {fk.parent.name} → {target.table.name}.{target.name}")

# 验证必须外键
expected_targets = {
    ("task_id", "trial_tasks", "id"),
    ("receiver_id", "users", "id"),
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

mapper = Receipt.__mapper__
rels = list(mapper.relationships)
print(f"  [OK] {len(rels)} relationships found")

for rel in rels:
    print(f"  [OK] {rel.key} → {rel.mapper.class_.__name__}")

# 验证：必须 2 个 relationship (task, receiver)
assert len(rels) == 2, f"Expected 2 relationships, got {len(rels)}"
rel_keys = [r.key for r in rels]
assert "task" in rel_keys, "Missing 'task' relationship"
assert "receiver" in rel_keys, "Missing 'receiver' relationship"
print("  [OK] All relationships correct ✓")

# ============================================================
# 7. indexes / unique
# ============================================================
print("\n" + "=" * 60)
print("7. indexes")
print("=" * 60)
indexes = table.indexes
print(f"  [OK] {len(indexes)} explicit indexes (per DB_DESIGN.md §5.1)")

for idx in indexes:
    print(f"  [OK] {idx.name} on {[c.name for c in idx.columns]}")

# unique constraint comes from mapped_column(unique=True), not in table.indexes
has_task_id_unique = False
for col in table.columns:
    if col.name == "task_id" and col.unique:
        has_task_id_unique = True
        break

assert has_task_id_unique, "task_id must have unique constraint"
print("  [OK] task_id has unique constraint via mapped_column(unique=True) ✓")

# ============================================================
# 8. no hardcoded strings
# ============================================================
print("\n" + "=" * 60)
print("8. no hardcoded status strings")
print("=" * 60)
import tokenize
import io

with open("server/models/receipt.py", "r") as f:
    tokens = list(tokenize.generate_tokens(f.readline))

hardcoded = []
for tok in tokens:
    if tok.type == tokenize.STRING:
        s = tok.string.strip('"\'')
        if s in ["created", "received", "grinding", "dispatched", "closed", "pending", "passed", "failed"]:
            hardcoded.append((tok.start[0], s))

if hardcoded:
    print(f"  [FAIL] Hardcoded status strings found: {hardcoded}")
    sys.exit(1)
else:
    print("  [OK] No hardcoded status strings ✓")

# ============================================================
# 9. no circular import
# ============================================================
print("\n" + "=" * 60)
print("9. no circular import")
print("=" * 60)
# 我们已经成功导入，所以 circular import 不存在
print("  [OK] Import successful, no circular import ✓")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Total tables in metadata: {len(Base.metadata.tables)}")
print(f"  Receipt columns: {len(columns)}")
print(f"  Foreign keys: {len(fks)}")
print(f"  Relationships: {len(rels)}")
print(f"  Indexes: {len(indexes)}")

print("\n=== ALL TESTS PASSED ===")
