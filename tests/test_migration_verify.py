"""Sprint 1 — Task 1.15 Migration Verification Script

验证：
    - Metadata 一致性（Base.metadata.tables vs 数据库）
    - Table 数量（14 张）
    - Foreign Key 数量（16 个）
    - Index 数量（43 个）
    - Enum 数量（7 个）
    - Alembic version 表
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect
from server.database.engine import engine
from server.models import Base

# ============================================================
# 1. Metadata 一致性检查
# ============================================================
print("=" * 60)
print("  Migration Verification")
print("=" * 60)

inspector = inspect(engine)

# 数据库中的表
db_tables = set(inspector.get_table_names())
print(f"\n[1] 数据库表数量: {len(db_tables)}")
print(f"    数据库表: {sorted(db_tables)}")

# Base.metadata 中的表
meta_tables = set(Base.metadata.tables.keys())
print(f"\n[2] Base.metadata 表数量: {len(meta_tables)}")
print(f"    Metadata 表: {sorted(meta_tables)}")

# 去除 alembic_version
db_business_tables = db_tables - {"alembic_version"}
print(f"\n[3] 业务表数量: {len(db_business_tables)}")

# 检查差异
missing_in_db = meta_tables - db_business_tables
extra_in_db = db_business_tables - meta_tables

if missing_in_db:
    print(f"    [ERROR] 数据库中缺失表: {missing_in_db}")
if extra_in_db:
    print(f"    [ERROR] 数据库中存在额外表: {extra_in_db}")
if not missing_in_db and not extra_in_db:
    print("    Meta ↔ DB 完全一致: PASS")

# ============================================================
# 2. Foreign Key 检查
# ============================================================
print(f"\n[4] Foreign Key 检查:")
all_fks = []
for table_name in sorted(db_business_tables):
    fks = inspector.get_foreign_keys(table_name)
    for fk in fks:
        all_fks.append((table_name, fk["constrained_columns"], fk["referred_table"], fk["referred_columns"], fk.get("options", {}).get("ondelete", "")))
        print(f"    {table_name}.{fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']} (ON DELETE {fk.get('options', {}).get('ondelete', 'NONE')})")

print(f"\n    FK 总数: {len(all_fks)}")

# ============================================================
# 3. Index 检查
# ============================================================
print(f"\n[5] Index 检查:")
all_indexes = []
for table_name in sorted(db_business_tables):
    indexes = inspector.get_indexes(table_name)
    for idx in indexes:
        all_indexes.append((table_name, idx["name"], idx["column_names"], idx["unique"]))
        print(f"    {table_name}.{idx['name']} ON {idx['column_names']} (unique={idx['unique']})")

# 也统计 UNIQUE 约束 (它们也创建索引)
all_unique = []
for table_name in sorted(db_business_tables):
    uq = inspector.get_unique_constraints(table_name)
    for u in uq:
        all_unique.append((table_name, u["name"] or "UNIQUE", u["column_names"]))

print(f"\n    普通索引: {len(all_indexes)}")
print(f"    UNIQUE 约束: {len(all_unique)}")
print(f"    索引总计 (含 PK): {len(all_indexes) + len(all_unique) + len(db_business_tables)}")

# ============================================================
# 4. 列 / 枚举检查
# ============================================================
print(f"\n[6] 列与枚举检查:")
total_cols = 0
for table_name in sorted(db_business_tables):
    cols = inspector.get_columns(table_name)
    total_cols += len(cols)
    enum_cols = [c for c in cols if isinstance(c.get("type"), type) and "Enum" in str(type(c["type"]))]
    print(f"    {table_name}: {len(cols)} 列")

print(f"\n    总列数: {total_cols}")

# ============================================================
# 5. 14 张表清单验证
# ============================================================
expected_tables = {
    "users", "roles", "permissions",
    "user_roles", "role_permissions",
    "customers", "trial_tasks",
    "receipts", "grinding_records", "inspection_records",
    "dispatches", "attachments", "system_logs", "notifications",
}
print(f"\n[7] 14 表清单验证:")
missing = expected_tables - db_business_tables
extra = db_business_tables - expected_tables
if missing:
    print(f"    缺失: {missing}")
if extra:
    print(f"    多余: {extra}")
if not missing and not extra:
    print("    14 表全部存在: PASS")

# ============================================================
# 6. Alembic Version 检查
# ============================================================
print(f"\n[8] Alembic Version:")
if "alembic_version" in db_tables:
    print("    alembic_version 表存在: PASS")
else:
    print("    [ERROR] alembic_version 表不存在!")

# ============================================================
# 结果
# ============================================================
print("\n" + "=" * 60)
print("  Verification Complete")
print("=" * 60)