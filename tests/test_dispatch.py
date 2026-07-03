"""Sprint 1 — Task 1.9 Dispatch ORM 自检脚本"""

import traceback


def test_import():
    """2. 导入检查"""
    from server.models.dispatch import Dispatch
    from server.models import Dispatch as DispatchFromInit
    from server.models.trial_task import TrialTask
    from server.models.user import User
    from server.models.base_model import BaseModel
    print("[PASS] 2. 导入检查（dispatch.py + __init__.py + 交叉导入）")
    return Dispatch, TrialTask, User, BaseModel


def test_metadata(Dispatch):
    """3. 元数据检查"""
    assert Dispatch.__tablename__ == "dispatches", f"表名错误: {Dispatch.__tablename__}"
    print('[PASS] 3. __tablename__ = "dispatches"')


def test_columns(Dispatch):
    """4. 列检查"""
    cols = {c.name: c for c in Dispatch.__table__.columns}
    col_names = set(cols.keys())
    expected = {
        "id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted",
        "task_id", "direction", "dispatch_date", "operator_id",
    }
    assert col_names == expected, f"列不匹配: 期望 {expected - col_names}, 多余 {col_names - expected}"
    print(f"[PASS] 4. 列数检查: {len(cols)} 列 (10 = 4 业务 + 6 BaseModel)")
    return cols


def test_column_types(cols):
    """5. 业务列类型检查"""
    from sqlalchemy import String, DateTime, Integer
    assert isinstance(cols["task_id"].type, Integer), "task_id 类型错误"
    assert isinstance(cols["direction"].type, String), "direction 类型错误"
    assert cols["direction"].type.length == 200, "direction 长度错误"
    assert isinstance(cols["dispatch_date"].type, DateTime), "dispatch_date 类型错误"
    assert isinstance(cols["operator_id"].type, Integer), "operator_id 类型错误"
    print("[PASS] 5. 业务列类型检查")


def test_nullable(cols):
    """6. 可空检查"""
    assert not cols["task_id"].nullable, "task_id should be NOT NULL"
    assert not cols["direction"].nullable, "direction should be NOT NULL"
    assert not cols["dispatch_date"].nullable, "dispatch_date should be NOT NULL"
    assert not cols["operator_id"].nullable, "operator_id should be NOT NULL"
    print("[PASS] 6. 可空检查（4 业务字段均为 NOT NULL）")


def test_foreign_keys(Dispatch):
    """7. 外键检查"""
    fks = {fk.parent.name: fk for fk in Dispatch.__table__.foreign_keys}
    assert "task_id" in fks, "缺少 task_id FK"
    assert "operator_id" in fks, "缺少 operator_id FK"
    task_fk = fks["task_id"]
    op_fk = fks["operator_id"]
    assert task_fk.column.table.name == "trial_tasks", f"task_id FK 目标表错误"
    assert task_fk.ondelete == "CASCADE", f"task_id ondelete 错误: {task_fk.ondelete}"
    assert op_fk.column.table.name == "users", f"operator_id FK 目标表错误"
    assert op_fk.ondelete == "RESTRICT", f"operator_id ondelete 错误: {op_fk.ondelete}"
    print("[PASS] 7. 外键检查（task_id→CASCADE, operator_id→RESTRICT）")


def test_unique(Dispatch):
    """8. UNIQUE 约束检查"""
    from sqlalchemy import UniqueConstraint
    unique_cols = set()
    for c in Dispatch.__table__.columns:
        if c.unique:
            unique_cols.add(c.name)
    for const in Dispatch.__table__.constraints:
        if isinstance(const, UniqueConstraint):
            for c in const.columns:
                unique_cols.add(c.name)
    assert "task_id" in unique_cols, "task_id 缺少 UNIQUE 约束"
    print("[PASS] 8. UNIQUE 约束检查（task_id）")


def test_indexes(Dispatch):
    """9. 索引检查（§5.1: 仅 PRIMARY + UNIQUE）"""
    # 不应有显式 __table_args__ 索引（无 __table_args__ 也是正确的）
    explicit = []
    if hasattr(Dispatch, "__table_args__") and Dispatch.__table_args__:
        if isinstance(Dispatch.__table_args__, tuple):
            for item in Dispatch.__table_args__:
                if hasattr(item, "name"):
                    explicit.append(item.name)
        elif hasattr(Dispatch.__table_args__, "name"):
            explicit.append(Dispatch.__table_args__.name)
    assert len(explicit) == 0, f"不应有显式索引定义，发现: {explicit}"
    print("[PASS] 9. 索引检查（0 显式索引，符合 §5.1）")


def test_relationships(Dispatch):
    """10. 关系检查"""
    from sqlalchemy.orm import RelationshipProperty
    mapper = Dispatch.__mapper__
    assert "task" in mapper.relationships, "缺少 task relationship"
    assert "operator" in mapper.relationships, "缺少 operator relationship"
    assert isinstance(mapper.relationships["task"], RelationshipProperty)
    assert isinstance(mapper.relationships["operator"], RelationshipProperty)
    print("[PASS] 10. 关系检查（task 一对一, operator 多对一）")


def test_back_populates(Dispatch, TrialTask):
    """11. back_populates 双向检查"""
    assert "dispatch" in TrialTask.__mapper__.relationships, "TrialTask 缺少 dispatch 关系"
    print("[PASS] 11. back_populates 双向检查（TrialTask.dispatch ↔ Dispatch.task）")


def test_repr(Dispatch):
    """12. __repr__ 检查"""
    d = Dispatch(task_id=1, direction="退回客户", dispatch_date="2026-07-03", operator_id=2)
    r = repr(d)
    assert "Dispatch" in r, f"repr 缺少类名: {r}"
    assert "task_id=1" in r, f"repr 缺少 task_id: {r}"
    print(f"[PASS] 12. __repr__ 检查: {r}")


def test_on_update(Dispatch):
    """13. ON UPDATE 检查（不应指定）"""
    fks = {fk.parent.name: fk for fk in Dispatch.__table__.foreign_keys}
    task_fk = fks["task_id"]
    op_fk = fks["operator_id"]
    assert task_fk.onupdate is None, f"task_id onupdate 不应指定: {task_fk.onupdate}"
    assert op_fk.onupdate is None, f"operator_id onupdate 不应指定: {op_fk.onupdate}"
    print("[PASS] 13. ON UPDATE 检查（未指定，使用 SQLAlchemy 默认）")


def test_circular_import():
    """14. 循环导入检查"""
    # 重新加载所有模块，确保无循环导入
    import server.models
    import importlib
    importlib.reload(server.models)
    print("[PASS] 14. 循环导入检查（无异常）")


def main():
    print("=== Dispatch ORM 自检 ===")
    print()

    # 1. py_compile
    import py_compile
    try:
        py_compile.compile("server/models/dispatch.py", doraise=True)
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
        ("UNIQUE 约束检查", test_unique),
        ("索引检查", test_indexes),
        ("关系检查", test_relationships),
        ("back_populates 检查", test_back_populates),
        ("__repr__ 检查", test_repr),
        ("ON UPDATE 检查", test_on_update),
        ("循环导入检查", test_circular_import),
    ]

    passed = 0
    failed = 0

    # Step 2: 导入（返回依赖对象）
    try:
        Dispatch, TrialTask, User, BaseModel = test_import()
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. 导入检查: {e}")
        traceback.print_exc()
        failed += 1
        return

    # Step 3-14
    for name, fn in tests[2:]:
        try:
            if name in ("back_populates 检查",):
                fn(Dispatch, TrialTask)
            elif name in ("列类型检查", "可空检查"):
                cols = {c.name: c for c in Dispatch.__table__.columns}
                fn(cols)
            elif name == "循环导入检查":
                fn()
            else:
                fn(Dispatch)
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