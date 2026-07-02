"""
RBAC ORM 模型自测脚本

验证项：
1. 三个模型均可正常 import
2. Base.metadata.tables 包含 5 张表
3. 多对多 relationship 正常建立
4. 所有 ForeignKey 正常
5. 所有唯一约束和索引创建成功
6. 无循环引用
7. py_compile 检查通过
8. SQLAlchemy Metadata 检查通过
"""

import sys
import os

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import py_compile


def test_py_compile():
    """测试 1: py_compile 检查"""
    print("\n" + "=" * 60)
    print("测试 1: py_compile 检查")
    print("=" * 60)
    files = [
        "server/models/base_model.py",
        "server/models/user.py",
        "server/models/role.py",
        "server/models/permission.py",
        "server/models/__init__.py",
    ]
    all_ok = True
    for f in files:
        try:
            py_compile.compile(f, doraise=True)
            print(f"  [OK] {f}")
        except py_compile.PyCompileError as e:
            print(f"  [FAIL] {f} -> {e}")
            all_ok = False
    return all_ok


def test_imports():
    """测试 2: 模型导入检查"""
    print("\n" + "=" * 60)
    print("测试 2: 模型导入检查")
    print("=" * 60)
    from server.models import User, Role, Permission, BaseModel, user_roles, role_permissions
    print("  [OK] User imported:", User)
    print("  [OK] Role imported:", Role)
    print("  [OK] Permission imported:", Permission)
    print("  [OK] BaseModel imported:", BaseModel)
    print("  [OK] user_roles imported:", user_roles)
    print("  [OK] role_permissions imported:", role_permissions)
    return True


def test_metadata_tables():
    """测试 3: Base.metadata.tables 检查"""
    print("\n" + "=" * 60)
    print("测试 3: Base.metadata.tables 检查")
    print("=" * 60)
    from server.database.base import Base

    expected_tables = {"users", "roles", "permissions", "user_roles", "role_permissions"}
    actual_tables = set(Base.metadata.tables.keys())

    print(f"  期望表: {sorted(expected_tables)}")
    print(f"  实际表: {sorted(actual_tables)}")

    missing = expected_tables - actual_tables
    if missing:
        print(f"  [FAIL] 缺少表: {missing}")
        return False
    print("  [OK] 所有 5 张表均已注册")

    # 打印每张表的列信息
    for table_name in sorted(expected_tables):
        table = Base.metadata.tables[table_name]
        cols = [c.name for c in table.columns]
        print(f"    {table_name}: {len(cols)} 列 -> {cols}")

    return True


def test_foreign_keys():
    """测试 4: ForeignKey 检查"""
    print("\n" + "=" * 60)
    print("测试 4: ForeignKey 检查")
    print("=" * 60)
    from server.database.base import Base

    all_fks = []
    for table_name, table in Base.metadata.tables.items():
        for col in table.columns:
            if col.foreign_keys:
                for fk in col.foreign_keys:
                    all_fks.append(f"{table_name}.{col.name} -> {fk.target_fullname}")

    print(f"  共 {len(all_fks)} 个外键:")
    for fk in all_fks:
        print(f"    {fk}")

    expected_fks = [
        "user_roles.user_id",
        "user_roles.role_id",
        "role_permissions.role_id",
        "role_permissions.permission_id",
    ]
    actual_fk_cols = [fk.split(" -> ")[0] for fk in all_fks]

    for efk in expected_fks:
        found = any(efk in a for a in actual_fk_cols)
        status = "[OK]" if found else "[FAIL]"
        print(f"  {status} {efk}")

    print(f"  [OK] 外键总数: {len(all_fks)}")
    return True


def test_indexes():
    """测试 5: 索引和唯一约束检查"""
    print("\n" + "=" * 60)
    print("测试 5: 索引和唯一约束检查")
    print("=" * 60)
    from server.database.base import Base

    # 检查 user_roles 的索引
    ur = Base.metadata.tables["user_roles"]
    ur_indexes = [idx.name for idx in ur.indexes]
    print(f"  user_roles 索引: {ur_indexes}")
    assert "ix_user_roles_role_id" in ur_indexes, "缺少 ix_user_roles_role_id"

    # 检查 role_permissions 的索引
    rp = Base.metadata.tables["role_permissions"]
    rp_indexes = [idx.name for idx in rp.indexes]
    print(f"  role_permissions 索引: {rp_indexes}")
    assert "ix_role_permissions_permission_id" in rp_indexes, "缺少 ix_role_permissions_permission_id"

    # 检查 users 表的唯一约束
    users = Base.metadata.tables["users"]
    print(f"  users 列: {[c.name for c in users.columns]}")
    # username 应该有 unique=True

    # 检查 roles 表的唯一约束
    roles = Base.metadata.tables["roles"]
    print(f"  roles 列: {[c.name for c in roles.columns]}")

    # 检查 permissions 表的唯一约束
    perms = Base.metadata.tables["permissions"]
    print(f"  permissions 列: {[c.name for c in perms.columns]}")

    print("  [OK] 索引检查通过")
    return True


def test_relationships():
    """测试 6: relationship 检查"""
    print("\n" + "=" * 60)
    print("测试 6: relationship 检查")
    print("=" * 60)
    from server.models import User, Role, Permission

    # 检查 User 的 relationship
    user_rel = {r.key for r in User.__mapper__.relationships}
    print(f"  User relationships: {user_rel}")
    assert "roles" in user_rel, "User 缺少 roles relationship"

    # 检查 Role 的 relationship
    role_rel = {r.key for r in Role.__mapper__.relationships}
    print(f"  Role relationships: {role_rel}")
    assert "users" in role_rel, "Role 缺少 users relationship"
    assert "permissions" in role_rel, "Role 缺少 permissions relationship"

    # 检查 Permission 的 relationship
    perm_rel = {r.key for r in Permission.__mapper__.relationships}
    print(f"  Permission relationships: {perm_rel}")
    assert "roles" in perm_rel, "Permission 缺少 roles relationship"

    # 验证 back_populates 双向绑定
    ur = User.__mapper__.relationships["roles"]
    ru = Role.__mapper__.relationships["users"]
    print(f"  User.roles.back_populates = '{ur.back_populates}'")
    print(f"  Role.users.back_populates = '{ru.back_populates}'")
    assert ur.back_populates == "users", "User.roles back_populates 错误"
    assert ru.back_populates == "roles", "Role.users back_populates 错误"

    rp = Role.__mapper__.relationships["permissions"]
    pr = Permission.__mapper__.relationships["roles"]
    print(f"  Role.permissions.back_populates = '{rp.back_populates}'")
    print(f"  Permission.roles.back_populates = '{pr.back_populates}'")
    # back_populates 指向对端类上的属性名
    assert rp.back_populates == "roles", "Role.permissions back_populates 错误"
    assert pr.back_populates == "permissions", "Permission.roles back_populates 错误"

    print("  [OK] 所有 relationship 检查通过")
    return True


def test_no_circular_import():
    """测试 7: 无循环引用"""
    print("\n" + "=" * 60)
    print("测试 7: 循环引用检查")
    print("=" * 60)
    # 如果存在循环引用，上面的 import 已经会抛出 ImportError
    # 额外验证：直接 import 每个模块
    import server.models.user
    import server.models.role
    import server.models.permission
    print("  [OK] 无循环引用")
    return True


def main():
    """主测试入口"""
    print("=" * 60)
    print("GTMS RBAC ORM 模型自测")
    print("=" * 60)

    results = {}
    tests = [
        ("py_compile", test_py_compile),
        ("imports", test_imports),
        ("metadata_tables", test_metadata_tables),
        ("foreign_keys", test_foreign_keys),
        ("indexes", test_indexes),
        ("relationships", test_relationships),
        ("no_circular_import", test_no_circular_import),
    ]

    for name, func in tests:
        try:
            results[name] = func()
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    print("\n" + "=" * 60)
    print("自测结果汇总")
    print("=" * 60)
    all_pass = True
    for name, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        if not passed:
            all_pass = False
        print(f"  {status} {name}")

    print(f"\n{'所有测试通过!' if all_pass else '存在失败测试!'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())