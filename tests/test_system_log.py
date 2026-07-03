"""Sprint 1 — Task 1.11 SystemLog ORM 自检脚本"""

import traceback


def test_import():
    """2. 导入检查"""
    from server.models.system_log import SystemLog
    from server.models import SystemLog as SLFromInit
    from server.models.user import User
    from server.models.base_model import BaseModel
    from server.enums.action_type import ActionType
    from server.enums import ActionType as ATFromInit
    print("[PASS] 2. 导入检查（system_log.py + __init__.py + 枚举 + 交叉导入）")
    return SystemLog, User, BaseModel, ActionType


def test_metadata(SystemLog):
    """3. 元数据检查"""
    assert SystemLog.__tablename__ == "system_logs", f"表名错误: {SystemLog.__tablename__}"
    print('[PASS] 3. __tablename__ = "system_logs"')


def test_columns(SystemLog):
    """4. 列检查"""
    cols = {c.name: c for c in SystemLog.__table__.columns}
    col_names = set(cols.keys())
    expected = {
        "id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted",
        "user_id", "action", "target_type", "target_id", "changes", "ip_address",
    }
    assert col_names == expected, f"列不匹配: 期望 {expected - col_names}, 多余 {col_names - expected}"
    print(f"[PASS] 4. 列数检查: {len(cols)} 列 (12 = 6 业务 + 6 BaseModel)")
    return cols


def test_column_types(cols):
    """5. 业务列类型检查"""
    from sqlalchemy import Integer, String, JSON, Enum as SAEnum
    assert isinstance(cols["user_id"].type, Integer), "user_id 类型错误"
    assert isinstance(cols["action"].type, SAEnum), "action 类型错误"
    assert isinstance(cols["target_type"].type, String), "target_type 类型错误"
    assert cols["target_type"].type.length == 50, "target_type 长度错误"
    assert isinstance(cols["target_id"].type, Integer), "target_id 类型错误"
    assert isinstance(cols["changes"].type, JSON), "changes 类型错误"
    assert isinstance(cols["ip_address"].type, String), "ip_address 类型错误"
    assert cols["ip_address"].type.length == 50, "ip_address 长度错误"
    print("[PASS] 5. 业务列类型检查")


def test_nullable(cols):
    """6. 可空检查"""
    assert not cols["user_id"].nullable, "user_id should be NOT NULL"
    assert not cols["action"].nullable, "action should be NOT NULL"
    assert not cols["target_type"].nullable, "target_type should be NOT NULL"
    assert cols["target_id"].nullable, "target_id should be NULLABLE"
    assert cols["changes"].nullable, "changes should be NULLABLE"
    assert cols["ip_address"].nullable, "ip_address should be NULLABLE"
    print("[PASS] 6. 可空检查（3 NOT NULL + 3 NULLABLE）")


def test_foreign_keys(SystemLog):
    """7. 外键检查"""
    fks = {fk.parent.name: fk for fk in SystemLog.__table__.foreign_keys}
    assert "user_id" in fks, "缺少 user_id FK"
    user_fk = fks["user_id"]
    assert user_fk.column.table.name == "users", f"user_id FK 目标表错误"
    assert user_fk.ondelete == "RESTRICT", f"user_id ondelete 错误: {user_fk.ondelete}"
    print("[PASS] 7. 外键检查（user_id→RESTRICT）")


def test_indexes(SystemLog):
    """8. 索引检查（§5.1: I-28, I-29, I-30）"""
    explicit = []
    if hasattr(SystemLog, "__table_args__") and SystemLog.__table_args__:
        if isinstance(SystemLog.__table_args__, tuple):
            for item in SystemLog.__table_args__:
                if hasattr(item, "name"):
                    explicit.append(item.name)
        elif hasattr(SystemLog.__table_args__, "name"):
            explicit.append(SystemLog.__table_args__.name)
    expected_names = {
        "ix_logs_user_id",
        "ix_logs_action",
        "ix_logs_created_at",
    }
    assert set(explicit) == expected_names, f"索引不匹配: 期望 {expected_names}, 实际 {set(explicit)}"
    print(f"[PASS] 8. 索引检查（{len(explicit)} 显式索引，符合 §5.1 I-28, I-29, I-30）")


def test_relationships(SystemLog):
    """9. 关系检查"""
    from sqlalchemy.orm import RelationshipProperty
    mapper = SystemLog.__mapper__
    assert "user" in mapper.relationships, "缺少 user relationship"
    assert isinstance(mapper.relationships["user"], RelationshipProperty)
    print("[PASS] 9. 关系检查（user 多对一）")


def test_back_populates(SystemLog, User):
    """10. back_populates 双向检查"""
    assert "system_logs" in User.__mapper__.relationships, "User 缺少 system_logs 关系"
    print("[PASS] 10. back_populates 双向检查（User.system_logs ↔ SystemLog.user）")


def test_repr(SystemLog):
    """11. __repr__ 检查"""
    s = SystemLog(user_id=1, action="create", target_type="trial_tasks")
    r = repr(s)
    assert "SystemLog" in r, f"repr 缺少类名: {r}"
    assert "user_id=1" in r, f"repr 缺少 user_id: {r}"
    print(f"[PASS] 11. __repr__ 检查: {r}")


def test_on_update(SystemLog):
    """12. ON UPDATE 检查（不应指定）"""
    fks = {fk.parent.name: fk for fk in SystemLog.__table__.foreign_keys}
    for name, fk in fks.items():
        assert fk.onupdate is None, f"{name} onupdate 不应指定: {fk.onupdate}"
    print("[PASS] 12. ON UPDATE 检查（未指定，使用 SQLAlchemy 默认）")


def test_enum(ActionType):
    """13. 枚举检查"""
    assert ActionType.CREATE == "create"
    assert ActionType.UPDATE == "update"
    assert ActionType.DELETE == "delete"
    assert ActionType.STATUS_CHANGE == "status_change"
    assert ActionType.CREATE.display_name == "创建"
    assert ActionType.STATUS_CHANGE.display_name == "状态变更"
    print("[PASS] 13. 枚举检查（ActionType: create/update/delete/status_change）")


def test_circular_import():
    """14. 循环导入检查"""
    import server.models
    import importlib
    importlib.reload(server.models)
    print("[PASS] 14. 循环导入检查（无异常）")


def test_enum_inheritance():
    """15. 枚举继承检查（str, Enum）"""
    from server.enums.action_type import ActionType
    from enum import Enum
    assert issubclass(ActionType, str), "ActionType 必须继承 str"
    assert issubclass(ActionType, Enum), "ActionType 必须继承 Enum"
    print("[PASS] 15. 枚举继承检查（ActionType(str, Enum)）")


def test_unique_constraints(SystemLog):
    """16. 唯一约束检查（无）"""
    from sqlalchemy import UniqueConstraint
    unique_count = 0
    for const in SystemLog.__table__.constraints:
        if isinstance(const, UniqueConstraint):
            unique_count += 1
    assert unique_count == 0, f"不应有 UniqueConstraint, 发现 {unique_count} 个"
    print("[PASS] 16. 唯一约束检查（0 个 UniqueConstraint）")


def main():
    print("=== SystemLog ORM 自检 ===")
    print()

    # 1. py_compile
    import py_compile
    try:
        py_compile.compile("server/models/system_log.py", doraise=True)
        py_compile.compile("server/enums/action_type.py", doraise=True)
        py_compile.compile("server/models/user.py", doraise=True)
        print("[PASS] 1. py_compile 语法检查")
    except py_compile.PyCompileError as e:
        print(f"[FAIL] 1. py_compile 语法检查: {e}")
        return

    tests = [
        ("导入检查", test_import),
        ("元数据检查", test_metadata),
        ("列检查", test_columns),
        ("列类型检查", test_column_types),
        ("可空检查", test_nullable),
        ("外键检查", test_foreign_keys),
        ("索引检查", test_indexes),
        ("关系检查", test_relationships),
        ("back_populates 检查", test_back_populates),
        ("__repr__ 检查", test_repr),
        ("ON UPDATE 检查", test_on_update),
        ("枚举检查", test_enum),
        ("循环导入检查", test_circular_import),
        ("枚举继承检查", test_enum_inheritance),
        ("唯一约束检查", test_unique_constraints),
    ]

    passed = 0
    failed = 0

    # Step 2: 导入
    try:
        SystemLog, User, BaseModel, ActionType = test_import()
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. 导入检查: {e}")
        traceback.print_exc()
        failed += 1
        return

    # Step 3-16
    for name, fn in tests[1:]:
        try:
            if name in ("back_populates 检查",):
                fn(SystemLog, User)
            elif name in ("列类型检查", "可空检查"):
                cols = {c.name: c for c in SystemLog.__table__.columns}
                fn(cols)
            elif name == "枚举检查":
                fn(ActionType)
            elif name in ("循环导入检查", "枚举继承检查"):
                fn()
            else:
                fn(SystemLog)
            passed += 1
        except Exception as e:
            idx = tests.index((name, fn)) + 2
            print(f"[FAIL] {idx}. {name}: {e}")
            traceback.print_exc()
            failed += 1

    print()
    print(f"=== 自检完成: {passed}/{passed + failed} 通过 ===")


if __name__ == "__main__":
    main()