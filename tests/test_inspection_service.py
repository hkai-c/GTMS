"""Sprint 2 — Task 2.8 InspectionService 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  upload_report — 基本创建 PASS
    4.  upload_report — precision/roughness 写入
    5.  upload_report — result_status PASSED
    6.  upload_report — 非 GRINDING 状态禁止
    7.  upload_report — 任务不存在
    8.  upload_report — 无权限用户抛异常
    9.  upload_report — Administrator 可以上传
    10. upload_report — 失败 FAILED
    11. upload_report — 失败时 failure_reason 必填
    12. upload_report — 失败未填 failure_reason 抛异常
    13. upload_report — 失败时 process_status 保持 GRINDING
    14. upload_report — 绑定 attachment
    15. upload_report — attachment 不存在抛异常
    16. upload_report — attachment 不属于任务抛异常
    17. upload_report — SystemLog
    18. upload_report — 无需 GrindingRecord.operator_id
    19. upload_report — inspector_id 自动设置
    20. get_inspection — 查询成功
    21. get_inspection — 不存在抛 NotFoundException
    22. get_inspection — 已删除记录过滤
    23. update_inspection — 修改字段
    24. update_inspection — 禁止未知字段
    25. update_inspection — 禁止修改 created_by
    26. update_inspection — 禁止修改 created_at
    27. update_inspection — 非 created_by 且非 admin 抛异常
    28. update_inspection — Administrator 可以修改
    29. update_inspection — created_by 可以修改
    30. update_inspection — SystemLog
    31. delete_inspection — 软删除
    32. delete_inspection — 非管理员抛异常
    33. delete_inspection — SystemLog
    34. 事务 rollback
    35. 禁止命名
    36. 循环导入
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.database.session import SessionLocal
from server.models import (
    User, TrialTask, Customer, InspectionRecord, Attachment, SystemLog,
)
from server.services.inspection_service import InspectionService
from server.services.task_service import TaskService, TaskCreate
from server.services.grinding_service import GrindingService
from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from server.enums import (
    InspectionResult,
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
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
print("  Task 2.8 — InspectionService Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "services" / "inspection_service.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
check("InspectionService", InspectionService is not None)

# ============================================================
# 准备测试数据
# ============================================================
db = SessionLocal()
inspection_service = InspectionService()
task_service = TaskService()
grinding_service = GrindingService()

admin = db.query(User).filter(User.username == "admin").first()
tech = db.query(User).filter(User.username == "tech1").first()
viewer = db.query(User).filter(User.username == "viewer1").first()
manager = db.query(User).filter(User.username == "manager1").first()
customer = db.query(Customer).first()

# 清理测试数据
from server.models import GrindingRecord
db.query(Attachment).filter(Attachment.file_path.like("%TEST%")).delete()
db.query(SystemLog).filter(SystemLog.target_type == "InspectionRecord").delete()
db.query(InspectionRecord).filter().delete()
db.query(GrindingRecord).filter().delete()
db.query(TrialTask).filter(TrialTask.requirement.like("%TEST%")).delete()
db.commit()

# 创建测试任务并推进到 GRINDING 状态
task = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 检测测试任务"),
)
task_id = task.id
task.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()

# 开始试磨
grinding_service.start_grinding(db, task_id=task_id, current_user=tech)

# 创建测试 Attachment
att1 = Attachment(
    task_id=task_id,
    file_type=FileType.IMAGE,
    file_name="TEST_inspect_img1.jpg",
    file_path="uploads/images/TEST_inspect_img1.jpg",
    file_size=1024,
    uploaded_by=tech.id,
    created_by=tech.id,
)
att2 = Attachment(
    task_id=task_id,
    file_type=FileType.IMAGE,
    file_name="TEST_inspect_img2.jpg",
    file_path="uploads/images/TEST_inspect_img2.jpg",
    file_size=2048,
    uploaded_by=tech.id,
    created_by=tech.id,
)
db.add_all([att1, att2])
db.commit()
att1_id = att1.id
att2_id = att2.id

# ============================================================
# 3. upload_report — 基本创建 PASS
# ============================================================
print("\n[3] upload_report — 基本创建 PASS")
inspection = inspection_service.upload_report(
    db,
    task_id=task_id,
    inspection_result=InspectionResult.PASS,
    precision="0.01mm",
    roughness="Ra0.8",
    attachment_ids=[att1_id, att2_id],
    failure_reason=None,
    current_user=tech,
)
check("返回 InspectionRecord", isinstance(inspection, InspectionRecord))
check("inspection.id > 0", inspection.id > 0)
check("task_id 正确", inspection.task_id == task_id)

# ============================================================
# 4. upload_report — precision/roughness 写入
# ============================================================
print("\n[4] upload_report — precision/roughness")
check("accuracy=0.01mm", inspection.accuracy == "0.01mm")
check("roughness=Ra0.8", inspection.roughness == "Ra0.8")
check("result=PASS", inspection.result == InspectionResult.PASS)

# ============================================================
# 5. upload_report — result_status
# ============================================================
print("\n[5] upload_report — result_status")
db.refresh(task)
check("result_status=PASSED", task.result_status == TrialTaskResultStatus.PASSED)

# ============================================================
# 6. 非 GRINDING 状态禁止
# ============================================================
print("\n[6] upload_report — 非 GRINDING 状态")
# 创建新任务保持 CREATED
task2 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 状态测试"),
)
try:
    inspection_service.upload_report(
        db,
        task_id=task2.id,
        inspection_result=InspectionResult.PASS,
        precision=None,
        roughness=None,
        attachment_ids=[],
        failure_reason=None,
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("非 GRINDING→BusinessLogicException", True)
finally:
    db.delete(task2)
    db.commit()

# ============================================================
# 7. 任务不存在
# ============================================================
print("\n[7] upload_report — 任务不存在")
try:
    inspection_service.upload_report(
        db,
        task_id=99999,
        inspection_result=InspectionResult.PASS,
        precision=None,
        roughness=None,
        attachment_ids=[],
        failure_reason=None,
        current_user=tech,
    )
    check("应抛异常", False)
except NotFoundException:
    check("任务不存在→NotFoundException", True)

# ============================================================
# 8. 无权限用户
# ============================================================
print("\n[8] upload_report — 无权限用户")
# 创建新任务并推进到 GRINDING
task3 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 权限测试"),
)
task3.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task3.id, current_user=tech)

try:
    inspection_service.upload_report(
        db,
        task_id=task3.id,
        inspection_result=InspectionResult.PASS,
        precision=None,
        roughness=None,
        attachment_ids=[],
        failure_reason=None,
        current_user=viewer,
    )
    check("应抛异常", False)
except PermissionDeniedException:
    check("viewer→PermissionDeniedException", True)

# 清理
db.query(InspectionRecord).filter(InspectionRecord.task_id == task3.id).delete()
db.query(GrindingRecord).filter(GrindingRecord.task_id == task3.id).delete()
db.query(SystemLog).filter(
    SystemLog.target_type == "InspectionRecord",
    SystemLog.target_id == task3.id,
).delete()
db.delete(task3)
db.commit()

# ============================================================
# 9. Administrator 可以上传
# ============================================================
print("\n[9] upload_report — Administrator")
task4 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST Admin检测"),
)
task4.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task4.id, current_user=tech)

inspection4 = inspection_service.upload_report(
    db,
    task_id=task4.id,
    inspection_result=InspectionResult.PASS,
    precision="0.005mm",
    roughness=None,
    attachment_ids=[],
    failure_reason=None,
    current_user=admin,
)
check("Admin 可以上传", inspection4 is not None)

# 清理
db.query(InspectionRecord).filter(InspectionRecord.task_id == task4.id).delete()
db.query(GrindingRecord).filter(GrindingRecord.task_id == task4.id).delete()
db.query(SystemLog).filter(
    SystemLog.target_type == "InspectionRecord",
    SystemLog.target_id == inspection4.id,
).delete()
db.delete(task4)
db.commit()

# ============================================================
# 10. upload_report — 失败 FAILED
# ============================================================
print("\n[10] upload_report — 失败")
task5 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 失败检测"),
)
task5.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task5.id, current_user=tech)

inspection5 = inspection_service.upload_report(
    db,
    task_id=task5.id,
    inspection_result=InspectionResult.FAIL,
    precision="0.1mm",
    roughness="Ra3.2",
    attachment_ids=[],
    failure_reason="精度不达标，超出公差范围",
    current_user=tech,
)
db.refresh(task5)
check("result_status=FAILED", task5.result_status == TrialTaskResultStatus.FAILED)
check("failure_reason 写入", task5.failure_reason == "精度不达标，超出公差范围")

# ============================================================
# 11. 失败时 failure_reason 必填
# ============================================================
print("\n[11] upload_report — 失败时 failure_reason 必填")
check("task5 failure_reason 已填", task5.failure_reason is not None)

# ============================================================
# 12. 失败未填 failure_reason 抛异常
# ============================================================
print("\n[12] upload_report — 失败未填 failure_reason")
task6 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 失败无原因"),
)
task6.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task6.id, current_user=tech)

try:
    inspection_service.upload_report(
        db,
        task_id=task6.id,
        inspection_result=InspectionResult.FAIL,
        precision=None,
        roughness=None,
        attachment_ids=[],
        failure_reason=None,
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("失败无原因→BusinessLogicException", True)

# ============================================================
# 13. 失败时 process_status 保持 GRINDING
# ============================================================
print("\n[13] upload_report — 失败时 process_status 保持")
db.refresh(task5)
check("process_status=GRINDING", task5.process_status == TrialTaskProcessStatus.GRINDING)

# ============================================================
# 14. upload_report — 绑定 attachment
# ============================================================
print("\n[14] upload_report — 绑定 attachment")
check("report_path 不为空", inspection.report_path is not None)
paths = json.loads(inspection.report_path)
check("包含 2 个路径", len(paths) == 2)

# ============================================================
# 15. attachment 不存在抛异常
# ============================================================
print("\n[15] upload_report — attachment 不存在")
task7 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 附件不存在"),
)
task7.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task7.id, current_user=tech)

try:
    inspection_service.upload_report(
        db,
        task_id=task7.id,
        inspection_result=InspectionResult.PASS,
        precision=None,
        roughness=None,
        attachment_ids=[99999],
        failure_reason=None,
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("不存在附件→BusinessLogicException", True)

# ============================================================
# 16. attachment 不属于任务抛异常
# ============================================================
print("\n[16] upload_report — attachment 不属于任务")
task_other = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 其他任务"),
)
att_other = Attachment(
    task_id=task_other.id,
    file_type=FileType.IMAGE,
    file_name="TEST_other.jpg",
    file_path="uploads/images/TEST_other.jpg",
    file_size=512,
    uploaded_by=tech.id,
    created_by=tech.id,
)
db.add(att_other)
db.commit()
att_other_id = att_other.id

try:
    inspection_service.upload_report(
        db,
        task_id=task7.id,
        inspection_result=InspectionResult.PASS,
        precision=None,
        roughness=None,
        attachment_ids=[att_other_id],
        failure_reason=None,
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("不属于任务→BusinessLogicException", True)

# 清理
db.delete(att_other)
db.delete(task_other)
db.commit()

# ============================================================
# 17. upload_report — SystemLog
# ============================================================
print("\n[17] upload_report — SystemLog")
log = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "InspectionRecord",
        SystemLog.target_id == inspection.id,
        SystemLog.action == ActionType.CREATE,
    )
    .first()
)
check("CREATE 日志存在", log is not None)
check("action=UPLOAD_INSPECTION", log is not None and log.changes.get("action") == "UPLOAD_INSPECTION")

# ============================================================
# 18. 无需 GrindingRecord.operator_id
# ============================================================
print("\n[18] upload_report — 无需 GrindingRecord.operator_id")
# tech 开始试磨，但 manager 也有 inspection:write 权限
# manager 可以上传检测（无需是试磨操作人）
task8 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST Manager检测"),
)
task8.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
# tech 开始试磨
grinding_service.start_grinding(db, task_id=task8.id, current_user=tech)

# manager 上传检测（manager 有 inspection:write）
inspection8 = inspection_service.upload_report(
    db,
    task_id=task8.id,
    inspection_result=InspectionResult.PASS,
    precision="0.02mm",
    roughness=None,
    attachment_ids=[],
    failure_reason=None,
    current_user=manager,
)
check("manager 可上传检测（非试磨操作人）", inspection8 is not None)

# ============================================================
# 19. inspector_id 自动设置
# ============================================================
print("\n[19] upload_report — inspector_id 自动设置")
check("inspector_id=tech.id", inspection.inspector_id == tech.id)
check("created_by=tech.id", inspection.created_by == tech.id)

# ============================================================
# 20. get_inspection — 查询成功
# ============================================================
print("\n[20] get_inspection — 查询成功")
fetched = inspection_service.get_inspection(db, task_id)
check("get_inspection 返回正确", fetched.id == inspection.id)

# ============================================================
# 21. get_inspection — 不存在
# ============================================================
print("\n[21] get_inspection — 不存在")
try:
    inspection_service.get_inspection(db, 99999)
    check("应抛异常", False)
except NotFoundException:
    check("不存在→NotFoundException", True)

# ============================================================
# 22. get_inspection — 已删除记录过滤
# ============================================================
print("\n[22] get_inspection — 已删除记录过滤")
# 软删除 task5 的检测记录
inspection5.is_deleted = True
db.commit()
try:
    inspection_service.get_inspection(db, task5.id)
    check("应抛异常", False)
except NotFoundException:
    check("已删除→NotFoundException", True)
# 恢复
inspection5.is_deleted = False
db.commit()

# ============================================================
# 23. update_inspection — 修改字段
# ============================================================
print("\n[23] update_inspection — 修改字段")
updated = inspection_service.update_inspection(
    db, task_id,
    accuracy="0.005mm",
    roughness="Ra0.4",
    current_user=tech,
)
check("accuracy 更新", updated.accuracy == "0.005mm")
check("roughness 更新", updated.roughness == "Ra0.4")

# ============================================================
# 24. update_inspection — 禁止未知字段
# ============================================================
print("\n[24] update_inspection — 禁止未知字段")
try:
    inspection_service.update_inspection(
        db, task_id, unknown_field="test", current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("unknown_field→BusinessLogicException", True)

# ============================================================
# 25. update_inspection — 禁止修改 created_by
# ============================================================
print("\n[25] update_inspection — 禁止修改 created_by")
try:
    inspection_service.update_inspection(
        db, task_id, created_by=admin.id, current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("created_by→BusinessLogicException", True)

# ============================================================
# 26. update_inspection — 禁止修改 created_at
# ============================================================
print("\n[26] update_inspection — 禁止修改 created_at")
try:
    inspection_service.update_inspection(
        db, task_id, created_at=datetime.now(), current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("created_at→BusinessLogicException", True)

# ============================================================
# 27. 非 created_by 且非 admin 抛异常
# ============================================================
print("\n[27] update_inspection — 非 created_by 且非 admin")
# inspection 由 tech 创建，manager 尝试修改
try:
    inspection_service.update_inspection(
        db, task_id, accuracy="XXX", current_user=manager,
    )
    check("应抛异常", False)
except PermissionDeniedException:
    check("manager→PermissionDeniedException", True)

# ============================================================
# 28. Administrator 可以修改
# ============================================================
print("\n[28] update_inspection — Administrator")
updated_admin = inspection_service.update_inspection(
    db, task_id, result=InspectionResult.PASS, current_user=admin,
)
check("Admin 可以修改", updated_admin.result == InspectionResult.PASS)

# ============================================================
# 29. created_by 可以修改
# ============================================================
print("\n[29] update_inspection — created_by")
updated_creator = inspection_service.update_inspection(
    db, task_id, roughness="Ra0.2", current_user=tech,
)
check("created_by 可以修改", updated_creator.roughness == "Ra0.2")

# ============================================================
# 30. update_inspection — SystemLog
# ============================================================
print("\n[30] update_inspection — SystemLog")
log_update = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "InspectionRecord",
        SystemLog.target_id == inspection.id,
        SystemLog.action == ActionType.UPDATE,
    )
    .order_by(SystemLog.id.desc())
    .first()
)
check("UPDATE 日志存在", log_update is not None)

# ============================================================
# 31. delete_inspection — 软删除
# ============================================================
print("\n[31] delete_inspection — 软删除")
inspection_service.delete_inspection(db, task_id, admin)
deleted = db.query(InspectionRecord).filter(InspectionRecord.id == inspection.id).first()
check("is_deleted=True", deleted.is_deleted)

# 恢复
deleted.is_deleted = False
db.commit()

# ============================================================
# 32. 非管理员抛异常
# ============================================================
print("\n[32] delete_inspection — 非管理员")
try:
    inspection_service.delete_inspection(db, task_id, tech)
    check("应抛异常", False)
except PermissionDeniedException:
    check("tech→PermissionDeniedException", True)

# ============================================================
# 33. delete_inspection — SystemLog
# ============================================================
print("\n[33] delete_inspection — SystemLog")
inspection_service.delete_inspection(db, task_id, admin)
log_delete = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "InspectionRecord",
        SystemLog.target_id == inspection.id,
        SystemLog.action == ActionType.DELETE,
    )
    .first()
)
check("DELETE 日志存在", log_delete is not None)

# 恢复
db.query(InspectionRecord).filter(InspectionRecord.task_id == task_id).update(
    {"is_deleted": False}, synchronize_session=False
)
db.commit()

# ============================================================
# 34. 事务 rollback
# ============================================================
print("\n[34] 事务 rollback")
before = db.query(InspectionRecord).filter(InspectionRecord.is_deleted == False).count()
try:
    inspection_service.upload_report(
        db,
        task_id=99999,
        inspection_result=InspectionResult.PASS,
        precision=None,
        roughness=None,
        attachment_ids=[],
        failure_reason=None,
        current_user=tech,
    )
except Exception:
    pass
after = db.query(InspectionRecord).filter(InspectionRecord.is_deleted == False).count()
check("rollback 后数量不变", before == after)

# ============================================================
# 35. 禁止命名
# ============================================================
print("\n[35] 禁止命名")
try:
    from server.services.inspection_service import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未使用", True)
try:
    from server.services.inspection_service import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未使用", True)
try:
    from server.services.inspection_service import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未使用", True)

# ============================================================
# 36. 循环导入
# ============================================================
print("\n[36] 循环导入")
from server.services import inspection_service as ins
check("无循环导入", True)

# ============================================================
# 清理
# ============================================================
task_ids = [task_id, task5.id, task6.id, task7.id, task8.id]
db.query(Attachment).filter(Attachment.task_id.in_(task_ids)).delete()
db.query(SystemLog).filter(SystemLog.target_type == "InspectionRecord").delete()
db.query(InspectionRecord).filter(InspectionRecord.task_id.in_(task_ids)).delete()
db.query(GrindingRecord).filter(GrindingRecord.task_id.in_(task_ids)).delete()
for t_id in task_ids:
    t = db.query(TrialTask).filter(TrialTask.id == t_id).first()
    if t:
        db.delete(t)
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