"""Sprint 1 — Task 1.10 Attachment ORM 自检脚本"""

import traceback


def test_import():
    """2. 导入检查"""
    from server.models.attachment import Attachment
    from server.models import Attachment as AttachmentFromInit
    from server.models.trial_task import TrialTask
    from server.models.user import User
    from server.models.base_model import BaseModel
    from server.enums.file_type import FileType
    from server.enums import FileType as FileTypeFromInit
    print("[PASS] 2. 导入检查（attachment.py + __init__.py + 枚举 + 交叉导入）")
    return Attachment, TrialTask, User, BaseModel, FileType


def test_metadata(Attachment):
    """3. 元数据检查"""
    assert Attachment.__tablename__ == "attachments", f"表名错误: {Attachment.__tablename__}"
    print('[PASS] 3. __tablename__ = "attachments"')


def test_columns(Attachment):
    """4. 列检查"""
    cols = {c.name: c for c in Attachment.__table__.columns}
    col_names = set(cols.keys())
    expected = {
        "id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted",
        "task_id", "file_type", "file_name", "file_path", "file_size", "uploaded_by",
    }
    assert col_names == expected, f"列不匹配: 期望 {expected - col_names}, 多余 {col_names - expected}"
    print(f"[PASS] 4. 列数检查: {len(cols)} 列 (12 = 6 业务 + 6 BaseModel)")
    return cols


def test_column_types(cols):
    """5. 业务列类型检查"""
    from sqlalchemy import String, Integer, Enum as SAEnum
    assert isinstance(cols["task_id"].type, Integer), "task_id 类型错误"
    assert isinstance(cols["file_type"].type, SAEnum), "file_type 类型错误"
    assert isinstance(cols["file_name"].type, String), "file_name 类型错误"
    assert cols["file_name"].type.length == 255, "file_name 长度错误"
    assert isinstance(cols["file_path"].type, String), "file_path 类型错误"
    assert cols["file_path"].type.length == 500, "file_path 长度错误"
    assert isinstance(cols["file_size"].type, Integer), "file_size 类型错误"
    assert isinstance(cols["uploaded_by"].type, Integer), "uploaded_by 类型错误"
    print("[PASS] 5. 业务列类型检查")


def test_nullable(cols):
    """6. 可空检查"""
    assert not cols["task_id"].nullable, "task_id should be NOT NULL"
    assert not cols["file_type"].nullable, "file_type should be NOT NULL"
    assert not cols["file_name"].nullable, "file_name should be NOT NULL"
    assert not cols["file_path"].nullable, "file_path should be NOT NULL"
    assert cols["file_size"].nullable, "file_size should be NULLABLE"
    assert not cols["uploaded_by"].nullable, "uploaded_by should be NOT NULL"
    print("[PASS] 6. 可空检查（5 NOT NULL + 1 NULLABLE）")


def test_foreign_keys(Attachment):
    """7. 外键检查"""
    fks = {fk.parent.name: fk for fk in Attachment.__table__.foreign_keys}
    assert "task_id" in fks, "缺少 task_id FK"
    assert "uploaded_by" in fks, "缺少 uploaded_by FK"
    task_fk = fks["task_id"]
    up_fk = fks["uploaded_by"]
    assert task_fk.column.table.name == "trial_tasks", f"task_id FK 目标表错误"
    assert task_fk.ondelete == "CASCADE", f"task_id ondelete 错误: {task_fk.ondelete}"
    assert up_fk.column.table.name == "users", f"uploaded_by FK 目标表错误"
    assert up_fk.ondelete == "RESTRICT", f"uploaded_by ondelete 错误: {up_fk.ondelete}"
    print("[PASS] 7. 外键检查（task_id→CASCADE, uploaded_by→RESTRICT）")


def test_indexes(Attachment):
    """8. 索引检查（§5.1: I-24 PRIMARY, I-25 task_id, I-26 file_type）"""
    explicit = []
    if hasattr(Attachment, "__table_args__") and Attachment.__table_args__:
        if isinstance(Attachment.__table_args__, tuple):
            for item in Attachment.__table_args__:
                if hasattr(item, "name"):
                    explicit.append(item.name)
        elif hasattr(Attachment.__table_args__, "name"):
            explicit.append(Attachment.__table_args__.name)
    expected_names = {"ix_attachments_task_id", "ix_attachments_file_type"}
    assert set(explicit) == expected_names, f"索引不匹配: 期望 {expected_names}, 实际 {set(explicit)}"
    print(f"[PASS] 8. 索引检查（{len(explicit)} 显式索引，符合 §5.1 I-25, I-26）")


def test_relationships(Attachment):
    """9. 关系检查"""
    from sqlalchemy.orm import RelationshipProperty
    mapper = Attachment.__mapper__
    assert "task" in mapper.relationships, "缺少 task relationship"
    assert "uploader" in mapper.relationships, "缺少 uploader relationship"
    assert isinstance(mapper.relationships["task"], RelationshipProperty)
    assert isinstance(mapper.relationships["uploader"], RelationshipProperty)
    print("[PASS] 9. 关系检查（task 多对一, uploader 多对一）")


def test_back_populates(Attachment, TrialTask):
    """10. back_populates 双向检查"""
    assert "attachments" in TrialTask.__mapper__.relationships, "TrialTask 缺少 attachments 关系"
    print("[PASS] 10. back_populates 双向检查（TrialTask.attachments ↔ Attachment.task）")


def test_repr(Attachment):
    """11. __repr__ 检查"""
    a = Attachment(task_id=1, file_type="image", file_name="test.jpg", file_path="/uploads/test.jpg", uploaded_by=2)
    r = repr(a)
    assert "Attachment" in r, f"repr 缺少类名: {r}"
    assert "task_id=1" in r, f"repr 缺少 task_id: {r}"
    print(f"[PASS] 11. __repr__ 检查: {r}")


def test_on_update(Attachment):
    """12. ON UPDATE 检查（不应指定）"""
    fks = {fk.parent.name: fk for fk in Attachment.__table__.foreign_keys}
    for name, fk in fks.items():
        assert fk.onupdate is None, f"{name} onupdate 不应指定: {fk.onupdate}"
    print("[PASS] 12. ON UPDATE 检查（未指定，使用 SQLAlchemy 默认）")


def test_enum(FileType):
    """13. 枚举检查"""
    assert FileType.IMAGE == "image"
    assert FileType.DOCUMENT == "document"
    assert FileType.CAD == "cad"
    assert FileType.VIDEO == "video"
    assert FileType.IMAGE.display_name == "图片"
    print("[PASS] 13. 枚举检查（FileType: image/document/cad/video）")


def test_circular_import():
    """14. 循环导入检查"""
    import server.models
    import importlib
    importlib.reload(server.models)
    print("[PASS] 14. 循环导入检查（无异常）")


def test_enum_inheritance():
    """15. 枚举继承检查（str, Enum）"""
    from server.enums.file_type import FileType
    from enum import Enum
    assert issubclass(FileType, str), "FileType 必须继承 str"
    assert issubclass(FileType, Enum), "FileType 必须继承 Enum"
    print("[PASS] 15. 枚举继承检查（FileType(str, Enum)）")


def main():
    print("=== Attachment ORM 自检 ===")
    print()

    # 1. py_compile
    import py_compile
    try:
        py_compile.compile("server/models/attachment.py", doraise=True)
        py_compile.compile("server/enums/file_type.py", doraise=True)
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
    ]

    passed = 0
    failed = 0

    # Step 2: 导入（返回依赖对象）
    try:
        Attachment, TrialTask, User, BaseModel, FileType = test_import()
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. 导入检查: {e}")
        traceback.print_exc()
        failed += 1
        return

    # Step 3-15
    for name, fn in tests[2:]:
        try:
            if name in ("back_populates 检查",):
                fn(Attachment, TrialTask)
            elif name in ("列类型检查", "可空检查"):
                cols = {c.name: c for c in Attachment.__table__.columns}
                fn(cols)
            elif name == "枚举检查":
                fn(FileType)
            elif name in ("循环导入检查", "枚举继承检查"):
                fn()
            else:
                fn(Attachment)
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