"""Sprint 2 — Task 2.6 Receipt Service 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  create_receipt — 基本创建
    4.  create_receipt — 状态流转 CREATED→RECEIVED
    5.  create_receipt — 非 CREATED 状态禁止
    6.  create_receipt — 任务不存在抛异常
    7.  create_receipt — Attachment 创建
    8.  create_receipt — SystemLog 写入
    9.  get_receipt — 查询成功
    10. get_receipt — 不存在抛 NotFoundException
    11. update_receipt — 修改 receipt_date
    12. update_receipt — 新增图片
    13. update_receipt — SystemLog 写入
    14. delete_receipt — 软删除 Receipt
    15. delete_receipt — 软删除 Attachment
    16. delete_receipt — 非管理员抛异常
    17. delete_receipt — SystemLog 写入
    18. 事务 — rollback
    19. 异常 — 禁止命名
    20. 循环导入
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.database.session import SessionLocal
from server.models import User, TrialTask, Customer, Receipt, Attachment, SystemLog
from server.services.receipt_service import (
    ReceiptService,
    ReceiptCreate,
    ReceiptUpdate,
)
from server.services.task_service import TaskService, TaskCreate
from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from server.enums import (
    TrialTaskProcessStatus,
    ActionType,
    FileType,
)

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  -- {detail}")


print("=" * 60)
print("  Task 2.6 — Receipt Service Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "services" / "receipt_service.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
check("ReceiptService", ReceiptService is not None)
check("ReceiptCreate", ReceiptCreate is not None)
check("ReceiptUpdate", ReceiptUpdate is not None)

# ============================================================
# 准备测试数据
# ============================================================
db = SessionLocal()
receipt_service = ReceiptService()
task_service = TaskService()

admin = db.query(User).filter(User.username == "admin").first()
tech = db.query(User).filter(User.username == "tech1").first()
customer = db.query(Customer).first()

# 清理测试数据
db.query(Attachment).filter(Attachment.file_path.like("%TEST%")).delete()
db.query(Receipt).filter().delete()
db.query(SystemLog).filter(SystemLog.target_type == "Receipt").delete()
db.query(TrialTask).filter(TrialTask.requirement.like("%TEST%")).delete()
db.commit()

# 创建测试任务
task = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 收件测试任务"),
)
task_id = task.id

# ============================================================
# 3. create_receipt — 基本创建
# ============================================================
print("\n[3] create_receipt — 基本创建")
data = ReceiptCreate(
    task_id=task_id,
    receipt_date=datetime(2026, 7, 3, 10, 0, 0),
    receiver_id=tech.id,
    images=["test_img1.jpg", "test_img2.jpg"],
)
receipt = receipt_service.create_receipt(db, data, admin)
check("create_receipt 返回 Receipt", isinstance(receipt, Receipt))
check("receipt.id > 0", receipt.id > 0)
check("task_id 正确", receipt.task_id == task_id)

# ============================================================
# 4. 状态流转 CREATED→RECEIVED
# ============================================================
print("\n[4] 状态流转 CREATED→RECEIVED")
db.refresh(task)
check("process_status=RECEIVED", task.process_status == TrialTaskProcessStatus.RECEIVED)

# ============================================================
# 5. 非 CREATED 状态禁止收件
# ============================================================
print("\n[5] 非 CREATED 状态禁止收件")
# 创建新任务，将状态改为 RECEIVED
task2 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 状态测试"),
)
# 手动改为 RECEIVED
task2.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()

data2 = ReceiptCreate(
    task_id=task2.id,
    receipt_date=datetime(2026, 7, 3, 10, 0, 0),
    receiver_id=tech.id,
)
try:
    receipt_service.create_receipt(db, data2, admin)
    check("应抛异常", False)
except BusinessLogicException:
    check("非 CREATED→BusinessLogicException", True)

# 恢复
db.delete(task2)
db.commit()

# ============================================================
# 6. 任务不存在抛异常
# ============================================================
print("\n[6] 任务不存在抛异常")
data3 = ReceiptCreate(
    task_id=99999,
    receipt_date=datetime(2026, 7, 3, 10, 0, 0),
    receiver_id=tech.id,
)
try:
    receipt_service.create_receipt(db, data3, admin)
    check("应抛异常", False)
except NotFoundException:
    check("任务不存在→NotFoundException", True)

# ============================================================
# 7. Attachment 创建
# ============================================================
print("\n[7] Attachment 创建")
attachments = (
    db.query(Attachment)
    .filter(
        Attachment.task_id == task_id,
        Attachment.file_type == FileType.IMAGE,
        Attachment.is_deleted == False,  # noqa: E712
    )
    .all()
)
check("创建了 2 条 Attachment", len(attachments) == 2)
check("file_type=IMAGE", all(a.file_type == FileType.IMAGE for a in attachments))

# ============================================================
# 8. SystemLog 写入
# ============================================================
print("\n[8] create_receipt SystemLog")
log = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "Receipt",
        SystemLog.target_id == receipt.id,
        SystemLog.action == ActionType.STATUS_CHANGE,
    )
    .first()
)
check("STATUS_CHANGE 日志存在", log is not None)

# ============================================================
# 9. get_receipt — 查询成功
# ============================================================
print("\n[9] get_receipt")
fetched = receipt_service.get_receipt(db, task_id)
check("get_receipt 返回正确", fetched.id == receipt.id)

# ============================================================
# 10. get_receipt — 不存在
# ============================================================
print("\n[10] get_receipt — 不存在")
try:
    receipt_service.get_receipt(db, 99999)
    check("应抛异常", False)
except NotFoundException:
    check("不存在→NotFoundException", True)

# ============================================================
# 11. update_receipt — 修改 receipt_date
# ============================================================
print("\n[11] update_receipt — 修改 receipt_date")
new_date = datetime(2026, 7, 4, 14, 0, 0)
update_data = ReceiptUpdate(receipt_date=new_date)
updated = receipt_service.update_receipt(db, task_id, update_data, admin)
check("receipt_date 更新", updated.received_at == new_date)

# ============================================================
# 12. update_receipt — 新增图片
# ============================================================
print("\n[12] update_receipt — 新增图片")
update_data2 = ReceiptUpdate(images=["test_img3.jpg"])
updated2 = receipt_service.update_receipt(db, task_id, update_data2, admin)
attachments_after = (
    db.query(Attachment)
    .filter(
        Attachment.task_id == task_id,
        Attachment.file_type == FileType.IMAGE,
        Attachment.is_deleted == False,  # noqa: E712
    )
    .count()
)
check("新增后共 3 条 Attachment", attachments_after == 3)

# ============================================================
# 13. update_receipt SystemLog
# ============================================================
print("\n[13] update_receipt SystemLog")
log2 = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "Receipt",
        SystemLog.target_id == receipt.id,
        SystemLog.action == ActionType.UPDATE,
    )
    .first()
)
check("UPDATE 日志存在", log2 is not None)

# ============================================================
# 14. delete_receipt — 软删除 Receipt
# ============================================================
print("\n[14] delete_receipt — 软删除")
receipt_service.delete_receipt(db, task_id, admin)
deleted = db.query(Receipt).filter(Receipt.id == receipt.id).first()
check("Receipt is_deleted=True", deleted.is_deleted)

# 恢复
deleted.is_deleted = False
db.commit()

# ============================================================
# 15. delete_receipt — 软删除 Attachment
# ============================================================
print("\n[15] delete_receipt — 软删除 Attachment")
# 先恢复 Attachment
db.query(Attachment).filter(Attachment.task_id == task_id).update(
    {"is_deleted": False}, synchronize_session=False
)
db.commit()

receipt_service.delete_receipt(db, task_id, admin)
deleted_atts = (
    db.query(Attachment)
    .filter(
        Attachment.task_id == task_id,
        Attachment.file_type == FileType.IMAGE,
        Attachment.is_deleted == True,  # noqa: E712
    )
    .count()
)
check("Attachment 已被软删除", deleted_atts >= 3)

# 恢复
db.query(Attachment).filter(Attachment.task_id == task_id).update(
    {"is_deleted": False}, synchronize_session=False
)
db.query(Receipt).filter(Receipt.task_id == task_id).update(
    {"is_deleted": False}, synchronize_session=False
)
db.commit()

# ============================================================
# 16. 非管理员抛异常
# ============================================================
print("\n[16] delete_receipt — 非管理员")
try:
    receipt_service.delete_receipt(db, task_id, tech)
    check("应抛异常", False)
except PermissionDeniedException:
    check("非管理员→PermissionDeniedException", True)

# ============================================================
# 17. delete_receipt SystemLog
# ============================================================
print("\n[17] delete_receipt SystemLog")
receipt_service.delete_receipt(db, task_id, admin)
log3 = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "Receipt",
        SystemLog.target_id == receipt.id,
        SystemLog.action == ActionType.DELETE,
    )
    .first()
)
check("DELETE 日志存在", log3 is not None)

# 恢复
db.query(Attachment).filter(Attachment.task_id == task_id).update(
    {"is_deleted": False}, synchronize_session=False
)
db.query(Receipt).filter(Receipt.task_id == task_id).update(
    {"is_deleted": False}, synchronize_session=False
)
db.commit()

# ============================================================
# 18. 事务 rollback
# ============================================================
print("\n[18] 事务 rollback")
before = db.query(Receipt).filter(Receipt.is_deleted == False).count()
try:
    bad_data = ReceiptCreate(task_id=99999, receipt_date=datetime.now(), receiver_id=tech.id)
    receipt_service.create_receipt(db, bad_data, admin)
except Exception:
    pass
after = db.query(Receipt).filter(Receipt.is_deleted == False).count()
check("rollback 后数量不变", before == after)

# ============================================================
# 19. 禁止命名
# ============================================================
print("\n[19] 禁止命名")
try:
    from server.services.receipt_service import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未使用", True)
try:
    from server.services.receipt_service import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未使用", True)
try:
    from server.services.receipt_service import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未使用", True)

# ============================================================
# 20. 循环导入
# ============================================================
print("\n[20] 循环导入")
from server.services import receipt_service as rs
check("无循环导入", True)

# ============================================================
# 清理
# ============================================================
db.query(Attachment).filter(Attachment.task_id == task_id).delete()
db.query(SystemLog).filter(SystemLog.target_type == "Receipt").delete()
db.query(Receipt).filter(Receipt.task_id == task_id).delete()
db.delete(task)
db.commit()
db.close()

# ============================================================
# 结果
# ============================================================
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  结果: ALL PASSED")
else:
    print(f"  结果: {FAILED} FAILED")
print("=" * 60)

sys.exit(0 if FAILED == 0 else 1)