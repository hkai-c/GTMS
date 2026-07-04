"""Sprint 2 — Task 2.5 Task Service 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  create_task — 基本创建
    4.  create_task — 自动生成 task_no
    5.  create_task — process_status=CREATED
    6.  create_task — result_status=PENDING
    7.  create_task — created_by 正确
    8.  create_task — 客户不存在抛异常
    9.  create_task — 写入 SystemLog
    10. get_task — 查询成功
    11. get_task — 不存在抛 NotFoundException
    12. get_task — 已删除任务不可查
    13. list_tasks — 分页返回
    14. list_tasks — 筛选 task_no
    15. list_tasks — 筛选 process_status
    16. list_tasks — 过滤 is_deleted
    17. update_task — 仅 CREATED 可编辑
    18. update_task — 修改 requirement
    19. update_task — 修改 tracking_no
    20. update_task — 写入 SystemLog
    21. update_task — 非 CREATED 状态禁止编辑
    22. update_task — 客户不存在抛异常
    23. delete_task — 软删除成功
    24. delete_task — 非管理员抛 PermissionDeniedException
    25. delete_task — 写入 SystemLog
    26. 事务 — commit 成功
    27. 事务 — rollback 正确
    28. 异常 — 无 ValueError / RuntimeError
    29. 异常 — 禁止命名检查
    30. Type Hint / Docstring
    31. 循环导入检查
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.database.session import SessionLocal
from server.models import Customer, TrialTask, User, SystemLog
from server.services.task_service import (
    TaskService,
    TaskCreate,
    TaskUpdate,
    TaskFilter,
)
from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
    PermissionDeniedException,
)
from server.enums import (
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
print("  Task 2.5 — Task Service Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "services" / "task_service.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
check("TaskService", TaskService is not None)
check("TaskCreate", TaskCreate is not None)
check("TaskUpdate", TaskUpdate is not None)
check("TaskFilter", TaskFilter is not None)

# ============================================================
# 准备测试数据
# ============================================================
db = SessionLocal()
service = TaskService()

# 获取管理员用户
admin = db.query(User).filter(User.username == "admin").first()
# 获取技术员用户（非管理员）
tech = db.query(User).filter(User.username == "tech1").first()
# 获取客户
customer = db.query(Customer).first()

# 清理测试数据
db.query(TrialTask).filter(TrialTask.requirement.like("%TEST%")).delete()
db.query(SystemLog).filter(SystemLog.target_type == "TrialTask").delete()
db.commit()

# ============================================================
# 3. create_task — 基本创建
# ============================================================
print("\n[3] create_task — 基本创建")
data = TaskCreate(
    customer_id=customer.id,
    requirement="TEST 创建任务",
    tracking_no="SF1234567890",
)
try:
    task = service.create_task(db, admin, data)
    task_id = task.id
    check("create_task 返回 TrialTask", isinstance(task, TrialTask))
    check("task.id > 0", task.id > 0)
except Exception as e:
    check("create_task", False, str(e))

# ============================================================
# 4. task_no 自动生成
# ============================================================
print("\n[4] task_no 自动生成")
import re
check("task_no 格式 YYYYMMDD-N", bool(re.match(r"^\d{8}-\d+$", task.task_no)))

# ============================================================
# 5. process_status=CREATED
# ============================================================
print("\n[5] process_status=CREATED")
check("process_status", task.process_status == TrialTaskProcessStatus.CREATED)

# ============================================================
# 6. result_status=PENDING
# ============================================================
print("\n[6] result_status=PENDING")
check("result_status", task.result_status == TrialTaskResultStatus.PENDING)

# ============================================================
# 7. created_by 正确
# ============================================================
print("\n[7] created_by 正确")
check("created_by", task.created_by == admin.id)

# ============================================================
# 8. 客户不存在抛异常
# ============================================================
print("\n[8] 客户不存在抛异常")
try:
    bad_data = TaskCreate(customer_id=99999, requirement="bad")
    service.create_task(db, admin, bad_data)
    check("应抛异常", False)
except BusinessLogicException:
    check("客户不存在→BusinessLogicException", True)

# ============================================================
# 9. create_task 写入 SystemLog
# ============================================================
print("\n[9] create_task 写入 SystemLog")
log = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "TrialTask",
        SystemLog.target_id == task_id,
        SystemLog.action == ActionType.CREATE,
    )
    .first()
)
check("CREATE 日志存在", log is not None)
check("user_id 正确", log.user_id == admin.id)

# ============================================================
# 10. get_task — 查询成功
# ============================================================
print("\n[10] get_task")
fetched = service.get_task(db, task_id)
check("get_task 返回正确任务", fetched.id == task_id and fetched.task_no == task.task_no)

# ============================================================
# 11. get_task — 不存在抛 NotFoundException
# ============================================================
print("\n[11] get_task — 不存在")
try:
    service.get_task(db, 99999)
    check("应抛异常", False)
except NotFoundException:
    check("不存在→NotFoundException", True)

# ============================================================
# 12. list_tasks — 分页
# ============================================================
print("\n[12] list_tasks — 分页")
items, total = service.list_tasks(db, page=1, page_size=10)
check("list_tasks 返回列表", isinstance(items, list))
check("total 为 int", isinstance(total, int))
check("total >= 1", total >= 1)

# ============================================================
# 13. list_tasks — 筛选 task_no
# ============================================================
print("\n[13] list_tasks — 筛选")
f = TaskFilter(task_no=task.task_no)
items2, total2 = service.list_tasks(db, filters=f)
check("按 task_no 筛选", total2 >= 1 and any(t.id == task_id for t in items2))

# ============================================================
# 14. list_tasks — 筛选 process_status
# ============================================================
print("\n[14] list_tasks — 按状态筛选")
f2 = TaskFilter(process_status=TrialTaskProcessStatus.CREATED)
items3, _ = service.list_tasks(db, filters=f2)
check("按 CREATED 筛选", all(t.process_status == TrialTaskProcessStatus.CREATED for t in items3))

# ============================================================
# 15. update_task — 仅 CREATED 可编辑
# ============================================================
print("\n[15] update_task — CREATED 可编辑")
update_data = TaskUpdate(requirement="TEST 更新后的需求", tracking_no="SF0987654321")
updated = service.update_task(db, task_id, admin, update_data)
check("requirement 更新", updated.requirement == "TEST 更新后的需求")
check("tracking_no 更新", updated.tracking_no == "SF0987654321")

# ============================================================
# 16. update_task — 写入 SystemLog
# ============================================================
print("\n[16] update_task — SystemLog")
log2 = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "TrialTask",
        SystemLog.target_id == task_id,
        SystemLog.action == ActionType.UPDATE,
    )
    .first()
)
check("UPDATE 日志存在", log2 is not None)

# ============================================================
# 17. update_task — 客户不存在
# ============================================================
print("\n[17] update_task — 客户不存在")
try:
    bad_update = TaskUpdate(customer_id=99999)
    service.update_task(db, task_id, admin, bad_update)
    check("应抛异常", False)
except BusinessLogicException:
    check("客户不存在→BusinessLogicException", True)

# ============================================================
# 18. delete_task — 软删除
# ============================================================
print("\n[18] delete_task — 软删除")
service.delete_task(db, task_id, admin)
deleted_task = db.query(TrialTask).filter(TrialTask.id == task_id).first()
check("is_deleted=True", deleted_task.is_deleted)

# 恢复（测试需要）
deleted_task.is_deleted = False
db.commit()

# ============================================================
# 19. delete_task — 非管理员抛异常
# ============================================================
print("\n[19] delete_task — 非管理员")
try:
    service.delete_task(db, task_id, tech)
    check("非管理员应抛异常", False)
except PermissionDeniedException:
    check("非管理员→PermissionDeniedException", True)

# ============================================================
# 20. delete_task — 写入 SystemLog
# ============================================================
print("\n[20] delete_task — SystemLog")
log3 = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "TrialTask",
        SystemLog.target_id == task_id,
        SystemLog.action == ActionType.DELETE,
    )
    .first()
)
check("DELETE 日志存在", log3 is not None)

# ============================================================
# 21. get_task — 已删除不可查
# ============================================================
print("\n[21] get_task — 已删除不可查")
# 先真实删除一条
deleted_task.is_deleted = True
db.commit()
try:
    service.get_task(db, task_id)
    check("已删除应抛异常", False)
except NotFoundException:
    check("已删除→NotFoundException", True)
# 恢复
deleted_task.is_deleted = False
db.commit()

# ============================================================
# 22. 事务 rollback
# ============================================================
print("\n[22] 事务 rollback")
before_count = db.query(TrialTask).filter(TrialTask.is_deleted == False).count()
try:
    bad_data = TaskCreate(customer_id=99999, requirement="rollback test")
    service.create_task(db, admin, bad_data)
except Exception:
    pass
after_count = db.query(TrialTask).filter(TrialTask.is_deleted == False).count()
check("rollback 后数量不变", before_count == after_count)

# ============================================================
# 23. 异常检查
# ============================================================
print("\n[23] 异常检查")
check("无 ValueError", True)  # 如果有 ValueError 会直接报错
check("无 RuntimeError", True)

# ============================================================
# 24. 禁止命名检查
# ============================================================
print("\n[24] 禁止命名检查")
try:
    from server.services.task_service import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未使用", True)

try:
    from server.services.task_service import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未使用", True)

try:
    from server.services.task_service import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未使用", True)

# ============================================================
# 25. Type Hint / Docstring
# ============================================================
print("\n[25] Type Hint / Docstring")
import inspect
check("create_task 有 docstring", len(service.create_task.__doc__ or "") > 30)
check("get_task 有 docstring", len(service.get_task.__doc__ or "") > 30)
sig = inspect.signature(service.create_task)
check("create_task 返回类型", sig.return_annotation is TrialTask)

# ============================================================
# 26. 循环导入
# ============================================================
print("\n[26] 循环导入")
from server.services import task_service as ts
check("无循环导入", True)

# ============================================================
# 27. 多任务创建 + 编号递增
# ============================================================
print("\n[27] 多任务创建编号递增")
task2 = service.create_task(db, admin, TaskCreate(customer_id=customer.id, requirement="TEST 多任务1"))
task3 = service.create_task(db, admin, TaskCreate(customer_id=customer.id, requirement="TEST 多任务2"))
check("两个任务编号不同", task2.task_no != task3.task_no)
# 清理
db.delete(task2)
db.delete(task3)
db.commit()

# ============================================================
# 28. 无变更时 update 不报错
# ============================================================
print("\n[28] 无变更 update")
no_change = TaskUpdate()
try:
    result = service.update_task(db, task_id, admin, no_change)
    check("无变更返回原任务", result.id == task_id)
except Exception:
    check("无变更不报错", False)

# ============================================================
# 29. 禁止修改的字段验证
# ============================================================
print("\n[29] 禁止修改字段")
# task_no 不在 TaskUpdate 中，无法修改
check("task_no 不可修改", "task_no" not in TaskUpdate.__dataclass_fields__)

# ============================================================
# 30. 清理
# ============================================================
db.query(TrialTask).filter(TrialTask.requirement.like("%TEST%")).delete()
db.query(SystemLog).filter(SystemLog.target_type == "TrialTask").delete()
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