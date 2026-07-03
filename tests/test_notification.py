"""Sprint 1 — Task 1.12 Notification ORM 自检脚本"""

import traceback


def test_import():
    """2. 导入检查"""
    from server.models.notification import Notification
    from server.models import Notification as NotifFromInit
    from server.models.trial_task import TrialTask
    from server.models.user import User
    from server.models.base_model import BaseModel
    from server.enums.notify_type import NotifyType
    from server.enums import NotifyType as NTFromInit
    print("[PASS] 2. 导入检查（notification.py + __init__.py + 枚举 + 交叉导入）")
    return Notification, TrialTask, User, BaseModel, NotifyType


def test_metadata(Notification):
    """3. 元数据检查"""
    assert Notification.__tablename__ == "notifications", f"表名错误: {Notification.__tablename__}"
    print('[PASS] 3. __tablename__ = "notifications"')


def test_columns(Notification):
    """4. 列检查"""
    cols = {c.name: c for c in Notification.__table__.columns}
    col_names = set(cols.keys())
    expected = {
        "id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted",
        "task_id", "type", "message", "is_read", "target_user_id",
    }
    assert col_names == expected, f"列不匹配: 期望 {expected - col_names}, 多余 {col_names - expected}"
    print(f"[PASS] 4. 列数检查: {len(cols)} 列 (11 = 5 业务 + 6 BaseModel)")
    return cols


def test_column_types(cols):
    """5. 业务列类型检查"""
    from sqlalchemy import Integer, Text, Boolean, Enum as SAEnum
    assert isinstance(cols["task_id"].type, Integer), "task_id 类型错误"
    assert isinstance(cols["type"].type, SAEnum), "type 类型错误"
    assert isinstance(cols["message"].type, Text), "message 类型错误"
    assert isinstance(cols["is_read"].type, Boolean), "is_read 类型错误"
    assert isinstance(cols["target_user_id"].type, Integer), "target_user_id 类型错误"
    print("[PASS] 5. 业务列类型检查")


def test_nullable(cols):
    """6. 可空检查"""
    assert not cols["task_id"].nullable, "task_id should be NOT NULL"
    assert not cols["type"].nullable, "type should be NOT NULL"
    assert not cols["message"].nullable, "message should be NOT NULL"
    assert not cols["is_read"].nullable, "is_read should be NOT NULL"
    assert not cols["target_user_id"].nullable, "target_user_id should be NOT NULL"
    print("[PASS] 6. 可空检查（5 业务字段均为 NOT NULL）")


def test_defaults(cols):
    """7. 默认值检查"""
    assert cols["is_read"].default.arg == False, "is_read 默认值应为 False"
    print("[PASS] 7. 默认值检查（is_read=False）")


def test_foreign_keys(Notification):
    """8. 外键检查"""
    fks = {fk.parent.name: fk for fk in Notification.__table__.foreign_keys}
    assert "task_id" in fks, "缺少 task_id FK"
    assert "target_user_id" in fks, "缺少 target_user_id FK"
    task_fk = fks["task_id"]
    tu_fk = fks["target_user_id"]
    assert task_fk.column.table.name == "trial_tasks", f"task_id FK 目标表错误"
    assert task_fk.ondelete == "CASCADE", f"task_id ondelete 错误: {task_fk.ondelete}"
    assert tu_fk.column.table.name == "users", f"target_user_id FK 目标表错误"
    assert tu_fk.ondelete == "CASCADE", f"target_user_id ondelete 错误: {tu_fk.ondelete}"
    print("[PASS] 8. 外键检查（task_id→CASCADE, target_user_id→CASCADE）")


def test_indexes(Notification):
    """9. 索引检查（§5.1: I-32, I-33, I-34）"""
    explicit = []
    if hasattr(Notification, "__table_args__") and Notification.__table_args__:
        if isinstance(Notification.__table_args__, tuple):
            for item in Notification.__table_args__:
                if hasattr(item, "name"):
                    explicit.append(item.name)
        elif hasattr(Notification.__table_args__, "name"):
            explicit.append(Notification.__table_args__.name)
    expected_names = {
        "ix_notifications_target_user",
        "ix_notifications_is_read",
        "ix_notifications_type",
    }
    assert set(explicit) == expected_names, f"索引不匹配: 期望 {expected_names}, 实际 {set(explicit)}"
    print(f"[PASS] 9. 索引检查（{len(explicit)} 显式索引，符合 §5.1 I-32, I-33, I-34）")


def test_relationships(Notification):
    """10. 关系检查"""
    from sqlalchemy.orm import RelationshipProperty
    mapper = Notification.__mapper__
    assert "task" in mapper.relationships, "缺少 task relationship"
    assert "target_user" in mapper.relationships, "缺少 target_user relationship"
    assert isinstance(mapper.relationships["task"], RelationshipProperty)
    assert isinstance(mapper.relationships["target_user"], RelationshipProperty)
    print("[PASS] 10. 关系检查（task 多对一, target_user 多对一）")


def test_back_populates(Notification, TrialTask, User):
    """11. back_populates 双向检查（TrialTask + User）"""
    assert "notifications" in TrialTask.__mapper__.relationships, "TrialTask 缺少 notifications 关系"
    assert "notifications" in User.__mapper__.relationships, "User 缺少 notifications 关系"
    print("[PASS] 11. back_populates 双向检查（TrialTask.notifications ↔ Notification.task, User.notifications ↔ Notification.target_user）")


def test_repr(Notification):
    """12. __repr__ 检查"""
    n = Notification(task_id=1, type="receipt_delay", message="收件超时提醒", target_user_id=2)
    r = repr(n)
    assert "Notification" in r, f"repr 缺少类名: {r}"
    assert "task_id=1" in r, f"repr 缺少 task_id: {r}"
    print(f"[PASS] 12. __repr__ 检查: {r}")


def test_on_update(Notification):
    """13. ON UPDATE 检查（不应指定）"""
    fks = {fk.parent.name: fk for fk in Notification.__table__.foreign_keys}
    for name, fk in fks.items():
        assert fk.onupdate is None, f"{name} onupdate 不应指定: {fk.onupdate}"
    print("[PASS] 13. ON UPDATE 检查（未指定，使用 SQLAlchemy 默认）")


def test_enum(NotifyType):
    """14. 枚举检查"""
    assert NotifyType.RECEIPT_DELAY == "receipt_delay"
    assert NotifyType.GRINDING_DELAY == "grinding_delay"
    assert NotifyType.REPORT_MISSING == "report_missing"
    assert NotifyType.RECEIPT_DELAY.display_name == "收件超时"
    assert NotifyType.GRINDING_DELAY.display_name == "试磨超时"
    assert NotifyType.REPORT_MISSING.display_name == "报告缺失"
    print("[PASS] 14. 枚举检查（NotifyType: receipt_delay/grinding_delay/report_missing）")


def test_circular_import():
    """15. 循环导入检查"""
    import server.models
    import importlib
    importlib.reload(server.models)
    print("[PASS] 15. 循环导入检查（无异常）")


def test_enum_inheritance():
    """16. 枚举继承检查（str, Enum）"""
    from server.enums.notify_type import NotifyType
    from enum import Enum
    assert issubclass(NotifyType, str), "NotifyType 必须继承 str"
    assert issubclass(NotifyType, Enum), "NotifyType 必须继承 Enum"
    print("[PASS] 16. 枚举继承检查（NotifyType(str, Enum)）")


def test_unique_constraints(Notification):
    """17. 唯一约束检查（无）"""
    from sqlalchemy import UniqueConstraint
    unique_count = 0
    for const in Notification.__table__.constraints:
        if isinstance(const, UniqueConstraint):
            unique_count += 1
    assert unique_count == 0, f"不应有 UniqueConstraint, 发现 {unique_count} 个"
    print("[PASS] 17. 唯一约束检查（0 个 UniqueConstraint）")


def main():
    print("=== Notification ORM 自检 ===")
    print()

    # 1. py_compile
    import py_compile
    try:
        py_compile.compile("server/models/notification.py", doraise=True)
        py_compile.compile("server/enums/notify_type.py", doraise=True)
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
        ("默认值检查", test_defaults),
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
        Notification, TrialTask, User, BaseModel, NotifyType = test_import()
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. 导入检查: {e}")
        traceback.print_exc()
        failed += 1
        return

    # Step 3-17
    for name, fn in tests[2:]:
        try:
            if name in ("back_populates 检查",):
                fn(Notification, TrialTask, User)
            elif name in ("列类型检查", "可空检查", "默认值检查"):
                cols = {c.name: c for c in Notification.__table__.columns}
                fn(cols)
            elif name == "枚举检查":
                fn(NotifyType)
            elif name in ("循环导入检查", "枚举继承检查"):
                fn()
            else:
                fn(Notification)
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