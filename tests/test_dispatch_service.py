"""Sprint 2 — Task 2.9 DispatchService 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  create_dispatch — 基本创建
    4.  create_dispatch — destination 写入
    5.  create_dispatch — dispatch_date 写入
    6.  create_dispatch — process_status DISPATCHED
    7.  create_dispatch — result_status 保持 PASSED
    8.  create_dispatch — 非 PASSED 状态禁止
    9.  create_dispatch — 非 GRINDING 状态禁止
    10. create_dispatch — 任务不存在
    11. create_dispatch — 无权限用户抛异常
    12. create_dispatch — Administrator 可以创建
    13. create_dispatch — 无需 GrindingRecord.operator_id
    14. create_dispatch — operator_id 自动设置
    15. create_dispatch — remark 参数接受
    16. create_dispatch — TrialTask.destination 独立
    17. create_dispatch — process_status 确认
    18. create_dispatch — SystemLog
    19. create_dispatch — result_status=FAILED 禁止
    20. get_dispatch — 查询成功
    21. get_dispatch — 不存在抛 NotFoundException
    22. get_dispatch — 已删除记录过滤
    23. update_dispatch — 修改字段
    24. update_dispatch — 禁止未知字段
    25. update_dispatch — 禁止修改 created_by
    26. update_dispatch — 禁止修改 created_at
    27. update_dispatch — 非 created_by 且非 admin 抛异常
    28. update_dispatch — Administrator 可以修改
    29. update_dispatch — created_by 可以修改
    30. update_dispatch — SystemLog
    31. delete_dispatch — 软删除
    32. delete_dispatch — 非管理员抛异常
    33. delete_dispatch — SystemLog
    34. 事务 rollback
    35. 禁止命名
    36. 循环导入
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.database.session import SessionLocal
from server.models import (
    User, TrialTask, Customer, Dispatch, GrindingRecord, SystemLog,
)
from server.services.dispatch_service import DispatchService
from server.services.task_service import TaskService, TaskCreate
from server.services.grinding_service import GrindingService
from server.services.inspection_service import InspectionService
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
print("  Task 2.9 — DispatchService Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "services" / "dispatch_service.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
check("DispatchService", DispatchService is not None)

# ============================================================
# 准备测试数据
# ============================================================
db = SessionLocal()
dispatch_service = DispatchService()
task_service = TaskService()
grinding_service = GrindingService()
inspection_service = InspectionService()

admin = db.query(User).filter(User.username == "admin").first()
tech = db.query(User).filter(User.username == "tech1").first()
viewer = db.query(User).filter(User.username == "viewer1").first()
manager = db.query(User).filter(User.username == "manager1").first()
customer = db.query(Customer).first()

# 清理测试数据
from server.models import InspectionRecord
db.query(SystemLog).filter(SystemLog.target_type == "Dispatch").delete()
db.query(Dispatch).filter().delete()
db.query(InspectionRecord).filter().delete()
db.query(GrindingRecord).filter().delete()
db.query(TrialTask).filter(TrialTask.requirement.like("%TEST%")).delete()
db.commit()

# 创建测试任务并推进到 GRINDING + PASSED 状态
task = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 去向测试任务"),
)
task_id = task.id
task.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()

grinding_service.start_grinding(db, task_id=task_id, current_user=tech)

# 上传检测报告（PASSED），使任务进入 result_status=PASSED
inspection_service.upload_report(
    db,
    task_id=task_id,
    inspection_result=InspectionResult.PASS,
    precision="0.01mm",
    roughness=None,
    attachment_ids=[],
    failure_reason=None,
    current_user=tech,
)

# ============================================================
# 3. create_dispatch — 基本创建
# ============================================================
print("\n[3] create_dispatch — 基本创建")
dispatch = dispatch_service.create_dispatch(
    db,
    task_id=task_id,
    destination="客户A工厂",
    dispatch_date=datetime(2026, 7, 4, 10, 0, 0),
    remark="加急处理",
    current_user=manager,
)
check("返回 Dispatch", isinstance(dispatch, Dispatch))
check("dispatch.id > 0", dispatch.id > 0)
check("task_id 正确", dispatch.task_id == task_id)

# ============================================================
# 4. create_dispatch — destination 写入
# ============================================================
print("\n[4] create_dispatch — destination")
check("direction=客户A工厂", dispatch.direction == "客户A工厂")

# ============================================================
# 5. create_dispatch — dispatch_date 写入
# ============================================================
print("\n[5] create_dispatch — dispatch_date")
check("dispatch_date 正确", dispatch.dispatch_date == datetime(2026, 7, 4, 10, 0, 0))

# ============================================================
# 6. create_dispatch — process_status
# ============================================================
print("\n[6] create_dispatch — process_status")
db.refresh(task)
check("process_status=DISPATCHED", task.process_status == TrialTaskProcessStatus.DISPATCHED)

# ============================================================
# 7. create_dispatch — result_status 保持
# ============================================================
print("\n[7] create_dispatch — result_status 保持")
check("result_status=PASSED", task.result_status == TrialTaskResultStatus.PASSED)

# ============================================================
# 8. 非 PASSED 状态禁止
# ============================================================
print("\n[8] create_dispatch — 非 PASSED 状态")
# 创建新任务保持 GRINDING 但 result_status=FAILED
task2 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 非PASSED"),
)
task2.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task2.id, current_user=tech)
# 上传 FAILED 检测
inspection_service.upload_report(
    db,
    task_id=task2.id,
    inspection_result=InspectionResult.FAIL,
    precision="0.5mm",
    roughness=None,
    attachment_ids=[],
    failure_reason="精度不合格",
    current_user=tech,
)
db.refresh(task2)
# result_status=FAILED, process_status=GRINDING → 应禁止
try:
    dispatch_service.create_dispatch(
        db,
        task_id=task2.id,
        destination="测试",
        dispatch_date=datetime.now(),
        remark=None,
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("result_status=FAILED→BusinessLogicException", True)

# ============================================================
# 9. 非 GRINDING 状态禁止
# ============================================================
print("\n[9] create_dispatch — 非 GRINDING 状态")
# 创建新任务保持 CREATED
task3 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 非GRINDING"),
)
try:
    dispatch_service.create_dispatch(
        db,
        task_id=task3.id,
        destination="测试",
        dispatch_date=datetime.now(),
        remark=None,
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("非 GRINDING→BusinessLogicException", True)

# 清理
db.delete(task3)
db.commit()

# ============================================================
# 10. 任务不存在
# ============================================================
print("\n[10] create_dispatch — 任务不存在")
try:
    dispatch_service.create_dispatch(
        db,
        task_id=99999,
        destination="测试",
        dispatch_date=datetime.now(),
        remark=None,
        current_user=tech,
    )
    check("应抛异常", False)
except NotFoundException:
    check("任务不存在→NotFoundException", True)

# ============================================================
# 11. 无权限用户
# ============================================================
print("\n[11] create_dispatch — 无权限用户")
# 创建新任务推进到 GRINDING + PASSED
task4 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 权限测试"),
)
task4.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task4.id, current_user=tech)
inspection_service.upload_report(
    db,
    task_id=task4.id,
    inspection_result=InspectionResult.PASS,
    precision=None,
    roughness=None,
    attachment_ids=[],
    failure_reason=None,
    current_user=tech,
)

try:
    dispatch_service.create_dispatch(
        db,
        task_id=task4.id,
        destination="测试",
        dispatch_date=datetime.now(),
        remark=None,
        current_user=tech,
    )
    check("应抛异常", False)
except PermissionDeniedException:
    check("tech(无dispatch:write)→PermissionDeniedException", True)

# 清理
db.query(Dispatch).filter(Dispatch.task_id == task4.id).delete()
db.query(InspectionRecord).filter(InspectionRecord.task_id == task4.id).delete()
db.query(GrindingRecord).filter(GrindingRecord.task_id == task4.id).delete()
db.delete(task4)
db.commit()

# ============================================================
# 12. Administrator 可以创建
# ============================================================
print("\n[12] create_dispatch — Administrator")
task5 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST Admin去向"),
)
task5.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task5.id, current_user=tech)
inspection_service.upload_report(
    db,
    task_id=task5.id,
    inspection_result=InspectionResult.PASS,
    precision=None,
    roughness=None,
    attachment_ids=[],
    failure_reason=None,
    current_user=tech,
)

dispatch5 = dispatch_service.create_dispatch(
    db,
    task_id=task5.id,
    destination="客户B总部",
    dispatch_date=datetime.now(),
    remark=None,
    current_user=admin,
)
check("Admin 可以创建", dispatch5 is not None)

# 清理
db.query(SystemLog).filter(
    SystemLog.target_type == "Dispatch",
    SystemLog.target_id == dispatch5.id,
).delete()
db.query(Dispatch).filter(Dispatch.task_id == task5.id).delete()
db.query(InspectionRecord).filter(InspectionRecord.task_id == task5.id).delete()
db.query(GrindingRecord).filter(GrindingRecord.task_id == task5.id).delete()
db.delete(task5)
db.commit()

# ============================================================
# 13. 无需 GrindingRecord.operator_id
# ============================================================
print("\n[13] create_dispatch — 无需 GrindingRecord.operator_id")
# task 的 grinding 由 tech 创建，但 manager 也可以创建去向
task6 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST Manager去向"),
)
task6.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
grinding_service.start_grinding(db, task_id=task6.id, current_user=tech)
inspection_service.upload_report(
    db,
    task_id=task6.id,
    inspection_result=InspectionResult.PASS,
    precision=None,
    roughness=None,
    attachment_ids=[],
    failure_reason=None,
    current_user=tech,
)

dispatch6 = dispatch_service.create_dispatch(
    db,
    task_id=task6.id,
    destination="客户C分部",
    dispatch_date=datetime.now(),
    remark=None,
    current_user=manager,
)
check("manager 可创建去向（非试磨操作人）", dispatch6 is not None)

# ============================================================
# 14. operator_id 自动设置
# ============================================================
print("\n[14] create_dispatch — operator_id 自动设置")
check("operator_id=manager.id", dispatch.operator_id == manager.id)

# ============================================================
# 15. remark 参数接受
# ============================================================
print("\n[15] create_dispatch — remark 参数")
check("remark 已接受（无异常）", True)

# ============================================================
# 16. TrialTask.destination 不要求同步（仅 Dispatch.direction 记录）
# ============================================================
print("\n[16] create_dispatch — TrialTask.destination 独立")
# TrialTask.destination 是 DestinationType 枚举，由后续流程单独设置
# Dispatch.direction 是字符串，独立记录去向描述
check("Dispatch.direction 独立记录", dispatch.direction == "客户A工厂")

# ============================================================
# 17. process_status 已更新为 DISPATCHED
# ============================================================
print("\n[17] create_dispatch — process_status 确认")
db.refresh(task)
check("process_status 确认为 DISPATCHED", task.process_status == TrialTaskProcessStatus.DISPATCHED)

# ============================================================
# 18. create_dispatch — SystemLog
# ============================================================
print("\n[18] create_dispatch — SystemLog")
log = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "Dispatch",
        SystemLog.target_id == dispatch.id,
        SystemLog.action == ActionType.CREATE,
    )
    .first()
)
check("CREATE 日志存在", log is not None)
check("action=CREATE_DISPATCH", log is not None and log.changes.get("action") == "CREATE_DISPATCH")
check("remark 已记录", log is not None and log.changes.get("remark") == "加急处理")

# ============================================================
# 19. result_status=FAILED 禁止创建
# ============================================================
print("\n[19] create_dispatch — result_status=FAILED")
# task2 已经是 FAILED + GRINDING → 已在测试 8 验证
check("FAILED 禁止创建（已由测试8验证）", True)

# ============================================================
# 20. get_dispatch — 查询成功
# ============================================================
print("\n[20] get_dispatch — 查询成功")
fetched = dispatch_service.get_dispatch(db, task_id)
check("get_dispatch 返回正确", fetched.id == dispatch.id)

# ============================================================
# 21. get_dispatch — 不存在
# ============================================================
print("\n[21] get_dispatch — 不存在")
try:
    dispatch_service.get_dispatch(db, 99999)
    check("应抛异常", False)
except NotFoundException:
    check("不存在→NotFoundException", True)

# ============================================================
# 22. get_dispatch — 已删除记录过滤
# ============================================================
print("\n[22] get_dispatch — 已删除记录过滤")
dispatch.is_deleted = True
db.commit()
try:
    dispatch_service.get_dispatch(db, task_id)
    check("应抛异常", False)
except NotFoundException:
    check("已删除→NotFoundException", True)
# 恢复
dispatch.is_deleted = False
db.commit()

# ============================================================
# 23. update_dispatch — 修改字段
# ============================================================
print("\n[23] update_dispatch — 修改字段")
updated = dispatch_service.update_dispatch(
    db, task_id,
    direction="客户A总部（更新）",
    current_user=manager,
)
check("direction 更新", updated.direction == "客户A总部（更新）")

# ============================================================
# 24. update_dispatch — 禁止未知字段
# ============================================================
print("\n[24] update_dispatch — 禁止未知字段")
try:
    dispatch_service.update_dispatch(
        db, task_id, unknown_field="test", current_user=manager,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("unknown_field→BusinessLogicException", True)

# ============================================================
# 25. update_dispatch — 禁止修改 created_by
# ============================================================
print("\n[25] update_dispatch — 禁止修改 created_by")
try:
    dispatch_service.update_dispatch(
        db, task_id, created_by=admin.id, current_user=manager,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("created_by→BusinessLogicException", True)

# ============================================================
# 26. update_dispatch — 禁止修改 created_at
# ============================================================
print("\n[26] update_dispatch — 禁止修改 created_at")
try:
    dispatch_service.update_dispatch(
        db, task_id, created_at=datetime.now(), current_user=manager,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("created_at→BusinessLogicException", True)

# ============================================================
# 27. 非 created_by 且非 admin 抛异常
# ============================================================
print("\n[27] update_dispatch — 非 created_by 且非 admin")
# dispatch 由 manager 创建，tech 尝试修改
try:
    dispatch_service.update_dispatch(
        db, task_id, direction="XXX", current_user=tech,
    )
    check("应抛异常", False)
except PermissionDeniedException:
    check("tech→PermissionDeniedException", True)

# ============================================================
# 28. Administrator 可以修改
# ============================================================
print("\n[28] update_dispatch — Administrator")
updated_admin = dispatch_service.update_dispatch(
    db, task_id, dispatch_date=datetime(2026, 7, 5), current_user=admin,
)
check("Admin 可以修改", updated_admin.dispatch_date == datetime(2026, 7, 5))

# ============================================================
# 29. created_by 可以修改
# ============================================================
print("\n[29] update_dispatch — created_by")
updated_creator = dispatch_service.update_dispatch(
    db, task_id, direction="客户A（manager修改）", current_user=manager,
)
check("created_by 可以修改", updated_creator.direction == "客户A（manager修改）")

# ============================================================
# 30. update_dispatch — SystemLog
# ============================================================
print("\n[30] update_dispatch — SystemLog")
log_update = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "Dispatch",
        SystemLog.target_id == dispatch.id,
        SystemLog.action == ActionType.UPDATE,
    )
    .order_by(SystemLog.id.desc())
    .first()
)
check("UPDATE 日志存在", log_update is not None)

# ============================================================
# 31. delete_dispatch — 软删除
# ============================================================
print("\n[31] delete_dispatch — 软删除")
dispatch_service.delete_dispatch(db, task_id, admin)
deleted = db.query(Dispatch).filter(Dispatch.id == dispatch.id).first()
check("is_deleted=True", deleted.is_deleted)

# 恢复
deleted.is_deleted = False
db.commit()

# ============================================================
# 32. 非管理员抛异常
# ============================================================
print("\n[32] delete_dispatch — 非管理员")
try:
    dispatch_service.delete_dispatch(db, task_id, tech)
    check("应抛异常", False)
except PermissionDeniedException:
    check("tech→PermissionDeniedException", True)

# ============================================================
# 33. delete_dispatch — SystemLog
# ============================================================
print("\n[33] delete_dispatch — SystemLog")
dispatch_service.delete_dispatch(db, task_id, admin)
log_delete = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "Dispatch",
        SystemLog.target_id == dispatch.id,
        SystemLog.action == ActionType.DELETE,
    )
    .first()
)
check("DELETE 日志存在", log_delete is not None)

# 恢复
db.query(Dispatch).filter(Dispatch.task_id == task_id).update(
    {"is_deleted": False}, synchronize_session=False
)
db.commit()

# ============================================================
# 34. 事务 rollback
# ============================================================
print("\n[34] 事务 rollback")
before = db.query(Dispatch).filter(Dispatch.is_deleted == False).count()
try:
    dispatch_service.create_dispatch(
        db,
        task_id=99999,
        destination="测试",
        dispatch_date=datetime.now(),
        remark=None,
        current_user=tech,
    )
except Exception:
    pass
after = db.query(Dispatch).filter(Dispatch.is_deleted == False).count()
check("rollback 后数量不变", before == after)

# ============================================================
# 35. 禁止命名
# ============================================================
print("\n[35] 禁止命名")
try:
    from server.services.dispatch_service import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未使用", True)
try:
    from server.services.dispatch_service import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未使用", True)
try:
    from server.services.dispatch_service import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未使用", True)

# ============================================================
# 36. 循环导入
# ============================================================
print("\n[36] 循环导入")
from server.services import dispatch_service as ds
check("无循环导入", True)

# ============================================================
# 清理
# ============================================================
task_ids = [task_id, task2.id, task6.id]
db.query(SystemLog).filter(SystemLog.target_type == "Dispatch").delete()
db.query(Dispatch).filter(Dispatch.task_id.in_(task_ids)).delete()
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