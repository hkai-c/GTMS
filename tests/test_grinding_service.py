"""Sprint 2 — Task 2.7 GrindingService 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  start_grinding — 基本创建
    4.  start_grinding — process_status GRINDING
    5.  start_grinding — operator_id 自动设置
    6.  start_grinding — start_time 自动设置
    7.  start_grinding — 非 RECEIVED 状态禁止
    8.  start_grinding — 任务不存在抛异常
    9.  start_grinding — 无权限用户抛异常
    10. start_grinding — Administrator 可以开始
    11. start_grinding — 无需收件人与操作人相同
    12. start_grinding — SystemLog 写入
    13. finish_grinding — 基本完成 PASSED
    14. finish_grinding — 写入 machine_type/wheel_type/params
    15. finish_grinding — end_time 自动设置
    16. finish_grinding — result_status PASSED
    17. finish_grinding — process_status 保持 GRINDING
    18. finish_grinding — 失败 FAILED
    19. finish_grinding — 失败时 failure_reason 必填
    20. finish_grinding — 失败未填 failure_reason 抛异常
    21. finish_grinding — 无效 result_status 抛异常
    22. finish_grinding — 非 operator 且非 admin 抛异常
    23. finish_grinding — Administrator 可以完成
    24. finish_grinding — 绑定 attachment
    25. finish_grinding — attachment 不存在抛异常
    26. finish_grinding — attachment 不属于任务抛异常
    27. finish_grinding — SystemLog 写入
    28. get_grinding — 查询成功
    29. get_grinding — 不存在抛 NotFoundException
    30. get_grinding — 已删除记录过滤
    31. update_grinding — 修改字段
    32. update_grinding — 禁止修改 operator_id
    33. update_grinding — 禁止未知字段
    34. update_grinding — 禁止修改 start_time
    35. update_grinding — 非 operator 且非 admin 抛异常
    36. update_grinding — Administrator 可以修改
    37. update_grinding — SystemLog 写入
    38. delete_grinding — 软删除
    39. delete_grinding — 非管理员抛异常
    40. delete_grinding — SystemLog 写入
    41. 事务 rollback
    42. 禁止命名
    43. 循环导入
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.database.session import SessionLocal
from server.models import (
    User, TrialTask, Customer, GrindingRecord, Attachment, SystemLog,
)
from server.services.grinding_service import GrindingService
from server.services.task_service import TaskService, TaskCreate
from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from server.enums import (
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
print("  Task 2.7 — GrindingService Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "services" / "grinding_service.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
check("GrindingService", GrindingService is not None)

# ============================================================
# 准备测试数据
# ============================================================
db = SessionLocal()
grinding_service = GrindingService()
task_service = TaskService()

admin = db.query(User).filter(User.username == "admin").first()
tech = db.query(User).filter(User.username == "tech1").first()
viewer = db.query(User).filter(User.username == "viewer1").first()
manager = db.query(User).filter(User.username == "manager1").first()
customer = db.query(Customer).first()

# 清理测试数据
db.query(Attachment).filter(Attachment.file_path.like("%TEST%")).delete()
db.query(SystemLog).filter(SystemLog.target_type == "GrindingRecord").delete()
db.query(GrindingRecord).filter().delete()
db.query(TrialTask).filter(TrialTask.requirement.like("%TEST%")).delete()
db.commit()

# 创建测试任务（在 CREATED 状态）
task = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 试磨测试任务"),
)
task_id = task.id

# 手动将任务状态改为 RECEIVED（模拟收件完成）
task.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()

# ============================================================
# 3. start_grinding — 基本创建
# ============================================================
print("\n[3] start_grinding — 基本创建")
grinding = grinding_service.start_grinding(db, task_id=task_id, current_user=tech)
check("返回 GrindingRecord", isinstance(grinding, GrindingRecord))
check("grinding.id > 0", grinding.id > 0)
check("task_id 正确", grinding.task_id == task_id)

# ============================================================
# 4. start_grinding — process_status GRINDING
# ============================================================
print("\n[4] start_grinding — process_status 流转")
db.refresh(task)
check("process_status=GRINDING", task.process_status == TrialTaskProcessStatus.GRINDING)

# ============================================================
# 5. start_grinding — operator_id 自动设置
# ============================================================
print("\n[5] start_grinding — operator_id 自动设置")
check("operator_id=tech.id", grinding.operator_id == tech.id)

# ============================================================
# 6. start_grinding — start_time 自动设置
# ============================================================
print("\n[6] start_grinding — start_time 自动设置")
check("start_time 不为空", grinding.start_time is not None)
check("start_time 在合理范围", abs((grinding.start_time - datetime.now()).total_seconds()) < 10)

# ============================================================
# 7. 非 RECEIVED 状态禁止
# ============================================================
print("\n[7] start_grinding — 非 RECEIVED 状态禁止")
# 创建新任务，保持 CREATED
task2 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 状态测试"),
)
try:
    grinding_service.start_grinding(db, task_id=task2.id, current_user=tech)
    check("应抛异常", False)
except BusinessLogicException:
    check("非 RECEIVED→BusinessLogicException", True)
finally:
    db.delete(task2)
    db.commit()

# ============================================================
# 8. 任务不存在抛异常
# ============================================================
print("\n[8] start_grinding — 任务不存在")
try:
    grinding_service.start_grinding(db, task_id=99999, current_user=tech)
    check("应抛异常", False)
except NotFoundException:
    check("任务不存在→NotFoundException", True)

# ============================================================
# 9. 无权限用户抛异常
# ============================================================
print("\n[9] start_grinding — 无权限用户")
# 创建新任务并设为 RECEIVED
task3 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 权限测试"),
)
task3.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()

try:
    grinding_service.start_grinding(db, task_id=task3.id, current_user=viewer)
    check("应抛异常", False)
except PermissionDeniedException:
    check("viewer→PermissionDeniedException", True)

# 清理
db.query(GrindingRecord).filter(GrindingRecord.task_id == task3.id).delete()
db.delete(task3)
db.commit()

# ============================================================
# 10. Administrator 可以开始试磨
# ============================================================
print("\n[10] start_grinding — Administrator")
task4 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST Admin测试"),
)
task4.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()

grinding4 = grinding_service.start_grinding(db, task_id=task4.id, current_user=admin)
check("Admin 可以开始", grinding4.operator_id == admin.id)

# 清理
db.query(GrindingRecord).filter(GrindingRecord.task_id == task4.id).delete()
db.delete(task4)
db.commit()

# ============================================================
# 11. 无需收件人与操作人相同
# ============================================================
print("\n[11] start_grinding — 操作人无需与收件人相同")
# grinding 由 tech 创建，已通过测试 3
check("tech 创建了试磨记录", grinding.operator_id == tech.id)

# ============================================================
# 12. start_grinding SystemLog
# ============================================================
print("\n[12] start_grinding — SystemLog")
log = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "GrindingRecord",
        SystemLog.target_id == grinding.id,
        SystemLog.action == ActionType.STATUS_CHANGE,
    )
    .first()
)
check("STATUS_CHANGE 日志存在", log is not None)
check("日志包含 action=START_GRINDING", log is not None and log.changes.get("action") == "START_GRINDING")

# ============================================================
# 准备 finish_grinding 测试数据 — 创建新的任务和试磨记录
# ============================================================
task5 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST Finish测试"),
)
task5.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
task5_id = task5.id

grinding5 = grinding_service.start_grinding(db, task_id=task5_id, current_user=tech)

# 创建测试 Attachment
att1 = Attachment(
    task_id=task5_id,
    file_type=FileType.IMAGE,
    file_name="TEST_grind_img1.jpg",
    file_path="uploads/images/TEST_grind_img1.jpg",
    file_size=1024,
    uploaded_by=tech.id,
    created_by=tech.id,
)
att2 = Attachment(
    task_id=task5_id,
    file_type=FileType.IMAGE,
    file_name="TEST_grind_img2.jpg",
    file_path="uploads/images/TEST_grind_img2.jpg",
    file_size=2048,
    uploaded_by=tech.id,
    created_by=tech.id,
)
db.add_all([att1, att2])
db.commit()
att1_id = att1.id
att2_id = att2.id

# ============================================================
# 13. finish_grinding — 基本完成 PASSED
# ============================================================
print("\n[13] finish_grinding — 基本完成 PASSED")
finished = grinding_service.finish_grinding(
    db,
    task_id=task5_id,
    machine_model="MGK-300",
    wheel_model="SDC-200",
    process_parameter="转速3000rpm,进给0.05mm",
    result_status=TrialTaskResultStatus.PASSED,
    failure_reason=None,
    attachment_ids=[att1_id, att2_id],
    current_user=tech,
)
check("返回 GrindingRecord", isinstance(finished, GrindingRecord))

# ============================================================
# 14. finish_grinding — 写入字段
# ============================================================
print("\n[14] finish_grinding — 写入字段")
check("machine_type=MGK-300", finished.machine_type == "MGK-300")
check("wheel_type=SDC-200", finished.wheel_type == "SDC-200")
check("params 正确", finished.params == "转速3000rpm,进给0.05mm")

# ============================================================
# 15. finish_grinding — end_time 自动设置
# ============================================================
print("\n[15] finish_grinding — end_time")
check("end_time 不为空", finished.end_time is not None)
check("end_time 在合理范围", abs((finished.end_time - datetime.now()).total_seconds()) < 10)

# ============================================================
# 16. finish_grinding — result_status PASSED
# ============================================================
print("\n[16] finish_grinding — result_status")
db.refresh(task5)
check("result_status=PASSED", task5.result_status == TrialTaskResultStatus.PASSED)

# ============================================================
# 17. finish_grinding — process_status 保持 GRINDING
# ============================================================
print("\n[17] finish_grinding — process_status 保持")
check("process_status=GRINDING", task5.process_status == TrialTaskProcessStatus.GRINDING)

# ============================================================
# 18. finish_grinding — 失败 FAILED
# ============================================================
print("\n[18] finish_grinding — 失败")
# 创建新任务
task6 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 失败测试"),
)
task6.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
task6_id = task6.id

grinding6 = grinding_service.start_grinding(db, task_id=task6_id, current_user=tech)

finished6 = grinding_service.finish_grinding(
    db,
    task_id=task6_id,
    machine_model="MGK-400",
    wheel_model="SDC-300",
    process_parameter="转速2000rpm",
    result_status=TrialTaskResultStatus.FAILED,
    failure_reason="砂轮磨损严重，无法满足精度要求",
    attachment_ids=[],
    current_user=tech,
)
db.refresh(task6)
check("result_status=FAILED", task6.result_status == TrialTaskResultStatus.FAILED)
check("fail_reason 写入 GrindingRecord", finished6.fail_reason == "砂轮磨损严重，无法满足精度要求")
check("failure_reason 写入 TrialTask", task6.failure_reason == "砂轮磨损严重，无法满足精度要求")

# ============================================================
# 19. finish_grinding — 失败时 process_status 保持 GRINDING
# ============================================================
print("\n[19] finish_grinding — 失败时 process_status 保持")
check("process_status 仍为 GRINDING", task6.process_status == TrialTaskProcessStatus.GRINDING)

# ============================================================
# 20. 失败未填 failure_reason 抛异常
# ============================================================
print("\n[20] finish_grinding — 失败未填 failure_reason")
# 创建新任务
task7 = task_service.create_task(
    db, admin,
    TaskCreate(customer_id=customer.id, requirement="TEST 失败无原因"),
)
task7.process_status = TrialTaskProcessStatus.RECEIVED
db.commit()
task7_id = task7.id

grinding_service.start_grinding(db, task_id=task7_id, current_user=tech)

try:
    grinding_service.finish_grinding(
        db,
        task_id=task7_id,
        machine_model="MGK-500",
        wheel_model=None,
        process_parameter=None,
        result_status=TrialTaskResultStatus.FAILED,
        failure_reason=None,
        attachment_ids=[],
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("失败无原因→BusinessLogicException", True)

# ============================================================
# 21. 无效 result_status 抛异常
# ============================================================
print("\n[21] finish_grinding — 无效 result_status")
try:
    grinding_service.finish_grinding(
        db,
        task_id=task7_id,
        machine_model=None,
        wheel_model=None,
        process_parameter=None,
        result_status=TrialTaskResultStatus.PENDING,
        failure_reason=None,
        attachment_ids=[],
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("PENDING→BusinessLogicException", True)

# ============================================================
# 22. 非 operator 且非 admin 抛异常
# ============================================================
print("\n[22] finish_grinding — 非 operator 且非 admin")
try:
    grinding_service.finish_grinding(
        db,
        task_id=task5_id,
        machine_model=None,
        wheel_model=None,
        process_parameter=None,
        result_status=TrialTaskResultStatus.PASSED,
        failure_reason=None,
        attachment_ids=[],
        current_user=manager,
    )
    check("应抛异常", False)
except PermissionDeniedException:
    check("manager→PermissionDeniedException", True)

# ============================================================
# 23. Administrator 可以完成
# ============================================================
print("\n[23] finish_grinding — Administrator")
# 使用 task7（还未完成）
finished7 = grinding_service.finish_grinding(
    db,
    task_id=task7_id,
    machine_model="MGK-500",
    wheel_model="CBN-100",
    process_parameter="转速1500rpm",
    result_status=TrialTaskResultStatus.PASSED,
    failure_reason=None,
    attachment_ids=[],
    current_user=admin,
)
check("Admin 可以完成（operator=tech）", finished7 is not None)

# ============================================================
# 24. finish_grinding — 绑定 attachment
# ============================================================
print("\n[24] finish_grinding — 绑定 attachment")
check("image_paths 不为空", finished.image_paths is not None)
paths = json.loads(finished.image_paths)
check("包含 2 个路径", len(paths) == 2)
check("路径正确", "TEST_grind_img1.jpg" in paths[0] or "TEST_grind_img1.jpg" in paths[1])

# ============================================================
# 25. attachment 不存在抛异常
# ============================================================
print("\n[25] finish_grinding — attachment 不存在")
try:
    grinding_service.finish_grinding(
        db,
        task_id=task5_id,
        machine_model=None,
        wheel_model=None,
        process_parameter=None,
        result_status=TrialTaskResultStatus.PASSED,
        failure_reason=None,
        attachment_ids=[99999],
        current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("不存在附件→BusinessLogicException", True)

# ============================================================
# 26. attachment 不属于任务抛异常
# ============================================================
print("\n[26] finish_grinding — attachment 不属于任务")
# 创建另一个任务的附件
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
    grinding_service.finish_grinding(
        db,
        task_id=task5_id,
        machine_model=None,
        wheel_model=None,
        process_parameter=None,
        result_status=TrialTaskResultStatus.PASSED,
        failure_reason=None,
        attachment_ids=[att_other_id],
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
# 27. finish_grinding SystemLog
# ============================================================
print("\n[27] finish_grinding — SystemLog")
log_finish = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "GrindingRecord",
        SystemLog.target_id == finished.id,
        SystemLog.action == ActionType.STATUS_CHANGE,
    )
    .order_by(SystemLog.id.desc())
    .first()
)
check("FINISH_GRINDING 日志存在", log_finish is not None)
check("action=FINISH_GRINDING", log_finish is not None and log_finish.changes.get("action") == "FINISH_GRINDING")

# ============================================================
# 28. get_grinding — 查询成功
# ============================================================
print("\n[28] get_grinding — 查询成功")
fetched = grinding_service.get_grinding(db, task5_id)
check("get_grinding 返回正确", fetched.id == finished.id)

# ============================================================
# 29. get_grinding — 不存在
# ============================================================
print("\n[29] get_grinding — 不存在")
try:
    grinding_service.get_grinding(db, 99999)
    check("应抛异常", False)
except NotFoundException:
    check("不存在→NotFoundException", True)

# ============================================================
# 30. get_grinding — 已删除记录过滤
# ============================================================
print("\n[30] get_grinding — 已删除记录过滤")
# 软删除 task6 的试磨记录
grinding6.is_deleted = True
db.commit()
try:
    grinding_service.get_grinding(db, task6_id)
    check("应抛异常", False)
except NotFoundException:
    check("已删除→NotFoundException", True)
# 恢复
grinding6.is_deleted = False
db.commit()

# ============================================================
# 31. update_grinding — 修改字段
# ============================================================
print("\n[31] update_grinding — 修改字段")
updated = grinding_service.update_grinding(
    db,
    task_id=task5_id,
    machine_type="MGK-300-V2",
    wheel_type="SDC-200-PRO",
    current_user=tech,
)
check("machine_type 更新", updated.machine_type == "MGK-300-V2")
check("wheel_type 更新", updated.wheel_type == "SDC-200-PRO")

# ============================================================
# 32. update_grinding — 禁止修改 operator_id
# ============================================================
print("\n[32] update_grinding — 禁止修改 operator_id")
try:
    grinding_service.update_grinding(
        db, task_id=task5_id, operator_id=admin.id, current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("operator_id→BusinessLogicException", True)

# ============================================================
# 33. update_grinding — 禁止未知字段
# ============================================================
print("\n[33] update_grinding — 禁止未知字段")
try:
    grinding_service.update_grinding(
        db, task5_id, unknown_field="test", current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("unknown_field→BusinessLogicException", True)

# ============================================================
# 34. update_grinding — 禁止修改 start_time
# ============================================================
print("\n[34] update_grinding — 禁止修改 start_time")
try:
    grinding_service.update_grinding(
        db, task_id=task5_id, start_time=datetime.now(), current_user=tech,
    )
    check("应抛异常", False)
except BusinessLogicException:
    check("start_time→BusinessLogicException", True)

# ============================================================
# 35. update_grinding — 非 operator 且非 admin 抛异常
# ============================================================
print("\n[35] update_grinding — 非 operator 且非 admin")
try:
    grinding_service.update_grinding(
        db, task_id=task5_id, machine_type="XXX", current_user=manager,
    )
    check("应抛异常", False)
except PermissionDeniedException:
    check("manager→PermissionDeniedException", True)

# ============================================================
# 36. update_grinding — Administrator 可以修改
# ============================================================
print("\n[36] update_grinding — Administrator")
updated_admin = grinding_service.update_grinding(
    db, task_id=task5_id, params="Admin修改的参数", current_user=admin,
)
check("Admin 可以修改", updated_admin.params == "Admin修改的参数")

# ============================================================
# 37. update_grinding — SystemLog
# ============================================================
print("\n[37] update_grinding — SystemLog")
log_update = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "GrindingRecord",
        SystemLog.target_id == grinding5.id,
        SystemLog.action == ActionType.UPDATE,
    )
    .order_by(SystemLog.id.desc())
    .first()
)
check("UPDATE 日志存在", log_update is not None)

# ============================================================
# 38. delete_grinding — 软删除
# ============================================================
print("\n[38] delete_grinding — 软删除")
grinding_service.delete_grinding(db, task5_id, admin)
deleted = db.query(GrindingRecord).filter(GrindingRecord.id == finished.id).first()
check("is_deleted=True", deleted.is_deleted)

# 恢复
deleted.is_deleted = False
db.commit()

# ============================================================
# 39. delete_grinding — 非管理员抛异常
# ============================================================
print("\n[39] delete_grinding — 非管理员")
try:
    grinding_service.delete_grinding(db, task5_id, tech)
    check("应抛异常", False)
except PermissionDeniedException:
    check("tech→PermissionDeniedException", True)

# ============================================================
# 40. delete_grinding — SystemLog
# ============================================================
print("\n[40] delete_grinding — SystemLog")
grinding_service.delete_grinding(db, task5_id, admin)
log_delete = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "GrindingRecord",
        SystemLog.target_id == finished.id,
        SystemLog.action == ActionType.DELETE,
    )
    .first()
)
check("DELETE 日志存在", log_delete is not None)

# 恢复
db.query(GrindingRecord).filter(GrindingRecord.task_id == task5_id).update(
    {"is_deleted": False}, synchronize_session=False
)
db.commit()

# ============================================================
# 41. 事务 rollback
# ============================================================
print("\n[41] 事务 rollback")
before = db.query(GrindingRecord).filter(GrindingRecord.is_deleted == False).count()
try:
    grinding_service.start_grinding(db, task_id=99999, current_user=tech)
except Exception:
    pass
after = db.query(GrindingRecord).filter(GrindingRecord.is_deleted == False).count()
check("rollback 后数量不变", before == after)

# ============================================================
# 42. 禁止命名
# ============================================================
print("\n[42] 禁止命名")
try:
    from server.services.grinding_service import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未使用", True)
try:
    from server.services.grinding_service import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未使用", True)
try:
    from server.services.grinding_service import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未使用", True)

# ============================================================
# 43. 循环导入
# ============================================================
print("\n[43] 循环导入")
from server.services import grinding_service as gs
check("无循环导入", True)

# ============================================================
# 清理
# ============================================================
db.query(Attachment).filter(Attachment.task_id.in_([task_id, task5_id, task6_id, task7_id])).delete()
db.query(SystemLog).filter(SystemLog.target_type == "GrindingRecord").delete()
db.query(GrindingRecord).filter(GrindingRecord.task_id.in_([task_id, task5_id, task6_id, task7_id])).delete()
for t in [task, task5, task6, task7]:
    try:
        db.delete(t)
    except Exception:
        pass
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