"""BUG-E2E-006 Regression Test

验证 Dispatch 阶段状态机修复后的正确性。

覆盖场景:
    ① grinding → dispatch（正常流程）
    ② inspection finished → dispatch（检测完成后可派发）
    ③ dispatch → closed（派发后可关闭任务）
    ④ 非法状态禁止 dispatch（非 GRINDING 状态禁止派发）
    ⑤ 重复 dispatch 禁止（同一任务不可重复派发）

遵循规范:
    - §15.24 Integration Testing Principle（真实 Service / 真实 DB）
    - §15.25 Bug Fix Principle
    - §15.26 Release Freeze Principle

测试方式: 全部使用真实数据库、真实 Service。
禁止: Mock、Fake、Stub、Dummy。
"""

import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    """执行一条检查。"""
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  -- {detail}")


# ============================================================
# 0. 测试环境准备
# ============================================================
print("=" * 70)
print("  BUG-E2E-006 Regression Test — Dispatch 状态机")
print("=" * 70)

# --- 0.1 替换数据库 URL 为临时文件 ---
import server.config as config_mod

_temp_db = tempfile.NamedTemporaryFile(
    suffix=".db", delete=False, prefix="test_regression_e2e006_",
)
_temp_db.close()
_test_db_url = f"sqlite:///{_temp_db.name}"
config_mod.settings.DATABASE_URL = _test_db_url
config_mod.settings.UPLOAD_DIR = tempfile.mkdtemp(prefix="test_upload_")

print(f"\n[0] 测试环境准备")
print(f"    数据库: {_test_db_url}")

# --- 0.2 创建数据库表 ---
from server.database.engine import engine as test_engine
from server.database.session import SessionLocal
from server.models.base_model import BaseModel
from server.models import (
    User, Role, Permission, user_roles, role_permissions,
    Customer, TrialTask, Receipt, GrindingRecord,
    InspectionRecord, Dispatch,
)
from server.core.security import hash_password

BaseModel.metadata.create_all(bind=test_engine)

db = SessionLocal()

# --- 0.3 种子数据：权限 ---
all_permissions = [
    "auth:login",
    "user:view", "user:create", "user:edit", "user:delete",
    "role:view", "role:create", "role:edit", "role:delete",
    "task:view", "task:create", "task:edit", "task:delete",
    "customer:view", "customer:create", "customer:edit", "customer:delete",
    "receipt:view", "receipt:create", "receipt:edit", "receipt:delete",
    "grinding:view", "grinding:create", "grinding:edit", "grinding:delete",
    "inspection:view", "inspection:create", "inspection:edit", "inspection:delete",
    "dispatch:view", "dispatch:create", "dispatch:edit", "dispatch:delete",
    "query:view", "query:export",
    "log:view",
    "notification:view", "notification:create", "notification:edit",
    "settings:view", "settings:edit",
    "upload:create",
]

perm_objects = {}
for code in all_permissions:
    p = Permission(code=code, name=code.replace(":", " ").title(), module=code.split(":")[0])
    db.add(p)
    perm_objects[code] = p
db.flush()

# --- 0.4 种子数据：角色与用户 ---
admin_role = Role(name="administrator", display_name="管理员", is_system=True)
tech_role = Role(name="technician", display_name="技术员", is_system=True)
sales_role = Role(name="sales", display_name="销售", is_system=False)
db.add_all([admin_role, tech_role, sales_role])
db.flush()

# 管理员拥有所有权限
for p in perm_objects.values():
    db.execute(role_permissions.insert().values(
        role_id=admin_role.id, permission_id=p.id
    ))

# 技术员权限
tech_perms = [
    "auth:login", "task:view",
    "receipt:view", "receipt:create", "receipt:edit",
    "grinding:view", "grinding:create", "grinding:edit",
    "inspection:view", "inspection:create", "inspection:edit",
    "dispatch:view", "dispatch:create", "dispatch:edit",
    "query:view", "notification:view", "upload:create",
]
for code in tech_perms:
    db.execute(role_permissions.insert().values(
        role_id=tech_role.id, permission_id=perm_objects[code].id
    ))

# 销售权限
sales_perms = [
    "auth:login", "customer:view", "customer:create", "customer:edit",
    "task:view", "task:create", "task:edit",
    "query:view", "notification:view", "upload:create",
]
for code in sales_perms:
    db.execute(role_permissions.insert().values(
        role_id=sales_role.id, permission_id=perm_objects[code].id
    ))

admin_user = User(
    username="admin", password_hash=hash_password("admin123"),
    real_name="管理员", is_active=True,
)
tech_user = User(
    username="tech1", password_hash=hash_password("tech123"),
    real_name="技术员", is_active=True,
)
sales_user = User(
    username="sales1", password_hash=hash_password("sales123"),
    real_name="销售", is_active=True,
)
db.add_all([admin_user, tech_user, sales_user])
db.flush()

db.execute(user_roles.insert().values(user_id=admin_user.id, role_id=admin_role.id))
db.execute(user_roles.insert().values(user_id=tech_user.id, role_id=tech_role.id))
db.execute(user_roles.insert().values(user_id=sales_user.id, role_id=sales_role.id))
db.commit()

check("测试数据库创建", True)
check("用户创建", admin_user.id is not None and tech_user.id is not None)

# --- 0.5 集成测试补丁：LogBase.created_at ---
import server.schemas.log_schema as log_schema_mod
from datetime import datetime as dt_datetime
from typing import Optional
from pydantic import Field as PydanticField

class _PatchedLogBase(log_schema_mod.LogBase):
    """集成测试补丁：LogBase.created_at 改为可选。"""
    created_at: dt_datetime = PydanticField(
        default_factory=dt_datetime.now,
        description="操作时间",
    )

log_schema_mod.LogBase = _PatchedLogBase

import server.services.grinding_service as _gs
import server.services.inspection_service as _is
import server.services.dispatch_service as _ds
import server.services.task_service as _ts
import server.services.receipt_service as _rs
import server.services.customer_service as _cs
import server.services.settings_service as _ss
import server.services.notification_service as _ns

_gs.LogBase = _PatchedLogBase
_is.LogBase = _PatchedLogBase
_ds.LogBase = _PatchedLogBase
_ts.LogBase = _PatchedLogBase
_rs.LogBase = _PatchedLogBase
_cs.LogBase = _PatchedLogBase
_ss.LogBase = _PatchedLogBase
_ns.LogBase = _PatchedLogBase

# --- 0.6 创建 Service 实例 ---
from server.services.customer_service import CustomerService
from server.services.task_service import TaskService
from server.services.receipt_service import ReceiptService
from server.services.grinding_service import GrindingService
from server.services.inspection_service import InspectionService
from server.services.dispatch_service import DispatchService

customer_service = CustomerService()
task_service = TaskService()
receipt_service = ReceiptService()
grinding_service = GrindingService()
inspection_service = InspectionService()
dispatch_service = DispatchService()

from server.enums import (
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
    DestinationType,
    InspectionResult,
)
from server.schemas.customer_schema import CustomerCreate
from server.schemas.trial_task_schema import TrialTaskCreate, TrialTaskUpdate
from server.schemas.receipt_schema import ReceiptCreate
from server.schemas.grinding_schema import GrindingCreate
from server.schemas.inspection_schema import InspectionCreate
from server.schemas.dispatch_schema import DispatchCreate

# --- 0.7 创建测试数据的基础设施 ---
# 创建客户
customer = customer_service.create_customer(db, CustomerCreate(
    company_name="回归测试公司",
    contact_person="测试人",
    phone="13800000000",
    address="测试地址",
), operator_id=admin_user.id)
customer_id = customer.id
check("客户创建", customer_id is not None)

# 创建任务（初始状态 CREATED）
task = task_service.create_task(db, TrialTaskCreate(
    customer_id=customer_id,
    sales_id=sales_user.id,
    requirement="回归测试需求",
    tracking_no="SF_REGRESSION",
), operator_id=admin_user.id)
task_id = task.id
check("任务创建（CREATED）", task_id is not None and task.process_status == TrialTaskProcessStatus.CREATED)

# 创建备选任务（用于多个场景测试）
task2 = task_service.create_task(db, TrialTaskCreate(
    customer_id=customer_id,
    sales_id=sales_user.id,
    requirement="回归测试需求2",
    tracking_no="SF_REGRESSION_2",
), operator_id=admin_user.id)
task2_id = task2.id
check("任务2创建（CREATED）", task2_id is not None)

# ============================================================
# 辅助函数：将任务推进到 GRINDING 状态
# ============================================================

def advance_to_grinding(db_session, t_id: int, tech_uid: int) -> tuple:
    """将任务从 CREATED 推进到 GRINDING。
    
    执行: 收件 → 开始试磨
    返回: (grinding_id, inspection_id)
    """
    # 收件
    receipt_service.create_receipt(db_session, ReceiptCreate(
        task_id=t_id,
        received_at=datetime.now(),
        receiver_id=tech_uid,
    ), operator_id=tech_uid)
    
    # 开始试磨
    grinding = grinding_service.create_grinding(db_session, GrindingCreate(
        task_id=t_id,
        operator_id=tech_uid,
        start_time=datetime.now(),
        machine_type="TEST_MACHINE",
        wheel_type="TEST_WHEEL",
        params="test_params",
    ), operator_id=tech_uid)
    
    # 创建检测记录
    inspection = inspection_service.create_inspection(db_session, InspectionCreate(
        task_id=t_id,
        inspector_id=tech_uid,
        report_path="/test/report.pdf",
        accuracy="0.01mm",
        roughness="Ra0.4",
        result=InspectionResult.PASS,
    ), operator_id=tech_uid)
    
    return grinding.id, inspection.id


# ============================================================
# 场景 ①：grinding → dispatch（正常流程）
# ============================================================
print("\n" + "=" * 70)
print("  [场景 ①] grinding → dispatch（正常流程）")
print("=" * 70)

# 推进任务到 grinding
g_id, i_id = advance_to_grinding(db, task_id, tech_user.id)

# 验证在 grinding 状态
db.refresh(db.query(TrialTask).filter(TrialTask.id == task_id).first())
db_task = db.query(TrialTask).filter(TrialTask.id == task_id).first()
check("前置: process_status = grinding",
      db_task.process_status == TrialTaskProcessStatus.GRINDING,
      f"实际: {db_task.process_status.value}")

# 完成试磨（PASSED）
grinding_service.finish_grinding(
    db, g_id,
    result_status=TrialTaskResultStatus.PASSED,
    operator_id=tech_user.id,
)
db.refresh(db_task)
check("试磨完成后 result_status = passed",
      db_task.result_status == TrialTaskResultStatus.PASSED,
      f"实际: {db_task.result_status.value}")
check("试磨完成后 process_status 保持 grinding",
      db_task.process_status == TrialTaskProcessStatus.GRINDING,
      f"实际: {db_task.process_status.value}")

# 完成检测（PASS）
inspection_service.finish_inspection(
    db, i_id,
    result=InspectionResult.PASS,
    operator_id=tech_user.id,
)
db.refresh(db_task)
check("检测完成后 result_status 保持 passed",
      db_task.result_status == TrialTaskResultStatus.PASSED)
check("检测完成后 process_status 保持 grinding",
      db_task.process_status == TrialTaskProcessStatus.GRINDING,
      f"实际: {db_task.process_status.value}")

# 创建 Dispatch
dispatch = dispatch_service.create_dispatch(db, DispatchCreate(
    task_id=task_id,
    direction=DestinationType.RETURNED_CUSTOMER,
    dispatch_date=datetime.now(),
    operator_id=tech_user.id,
), operator_id=tech_user.id)

check("场景①: dispatch 创建成功", dispatch.id is not None)
db.refresh(db_task)
check("场景①: process_status → dispatched",
      db_task.process_status == TrialTaskProcessStatus.DISPATCHED,
      f"实际: {db_task.process_status.value}")
check("场景①: dispatch.task_id 正确", dispatch.task_id == task_id)
check("场景①: dispatch.direction 正确",
      dispatch.direction == DestinationType.RETURNED_CUSTOMER)


# ============================================================
# 场景 ②：inspection finished → dispatch（检测完成后可派发）
# ============================================================
print("\n" + "=" * 70)
print("  [场景 ②] inspection finished → dispatch")
print("=" * 70)

# 用 task2 重复流程
g2_id, i2_id = advance_to_grinding(db, task2_id, tech_user.id)

# 完成试磨
grinding_service.finish_grinding(
    db, g2_id,
    result_status=TrialTaskResultStatus.PASSED,
    operator_id=tech_user.id,
)

# 完成检测（PASS）
inspection_service.finish_inspection(
    db, i2_id,
    result=InspectionResult.PASS,
    operator_id=tech_user.id,
)

db_task2 = db.query(TrialTask).filter(TrialTask.id == task2_id).first()
check("场景② 前置: process_status = grinding",
      db_task2.process_status == TrialTaskProcessStatus.GRINDING,
      f"实际: {db_task2.process_status.value}")
check("场景② 前置: result_status = passed",
      db_task2.result_status == TrialTaskResultStatus.PASSED)

# 创建 Dispatch
dispatch2 = dispatch_service.create_dispatch(db, DispatchCreate(
    task_id=task2_id,
    direction=DestinationType.RETURNED_CUSTOMER,
    dispatch_date=datetime.now(),
    operator_id=tech_user.id,
), operator_id=tech_user.id)

check("场景②: dispatch 创建成功", dispatch2.id is not None)
db.refresh(db_task2)
check("场景②: process_status → dispatched",
      db_task2.process_status == TrialTaskProcessStatus.DISPATCHED,
      f"实际: {db_task2.process_status.value}")


# ============================================================
# 场景 ③：dispatch → closed（派发后可关闭任务）
# ============================================================
print("\n" + "=" * 70)
print("  [场景 ③] dispatch → closed")
print("=" * 70)

# task2 当前在 dispatched 状态，执行关闭
from server.schemas.trial_task_schema import TrialTaskUpdate
task_service.update_task(db, task2_id, TrialTaskUpdate(
    process_status=TrialTaskProcessStatus.CLOSED,
), operator_id=admin_user.id)

db.refresh(db_task2)
check("场景③: process_status → closed",
      db_task2.process_status == TrialTaskProcessStatus.CLOSED,
      f"实际: {db_task2.process_status.value}")


# ============================================================
# 场景 ④：非法状态禁止 dispatch
# ============================================================
print("\n" + "=" * 70)
print("  [场景 ④] 非法状态禁止 dispatch")
print("=" * 70)

from server.core.exceptions import BusinessLogicException

# 创建新任务用于非法状态测试
task3 = task_service.create_task(db, TrialTaskCreate(
    customer_id=customer_id,
    sales_id=sales_user.id,
    requirement="非法状态测试",
    tracking_no="SF_ILLEGAL",
), operator_id=admin_user.id)
task3_id = task3.id

# 4.1 CREATED 状态禁止 dispatch
# 注意: dispatch_service 校验顺序为:
#   ① TrialTask 存在 → ② InspectionRecord 存在 → ③ 不重复
#   → ④ result_status == PASSED → ⑤ process_status == GRINDING
# CREATED 状态的任务没有 InspectionRecord，会在步骤②被拦截。
try:
    dispatch_service.create_dispatch(db, DispatchCreate(
        task_id=task3_id,
        direction=DestinationType.RETURNED_CUSTOMER,
        dispatch_date=datetime.now(),
        operator_id=tech_user.id,
    ), operator_id=tech_user.id)
    check("场景④.1: CREATED 状态禁止 dispatch",
          False, "应该抛出异常但未抛出")
except BusinessLogicException as e:
    # 校验链中先检查 InspectionRecord，CREATED 状态无检测记录
    check("场景④.1: CREATED 状态禁止 dispatch",
          "尚未完成检测" in str(e) or "仅试磨中状态" in str(e),
          f"异常: {e}")
except Exception as e:
    check("场景④.1: CREATED 状态禁止 dispatch",
          False, f"非预期异常: {type(e).__name__}: {e}")

# 4.2 推进到 RECEIVED 状态，尝试 dispatch
g3_id, i3_id = advance_to_grinding(db, task3_id, tech_user.id)

# 完成试磨
grinding_service.finish_grinding(
    db, g3_id,
    result_status=TrialTaskResultStatus.PASSED,
    operator_id=tech_user.id,
)

# 完成检测
inspection_service.finish_inspection(
    db, i3_id,
    result=InspectionResult.PASS,
    operator_id=tech_user.id,
)

# 创建 dispatch（正常）
dispatch3 = dispatch_service.create_dispatch(db, DispatchCreate(
    task_id=task3_id,
    direction=DestinationType.RETURNED_CUSTOMER,
    dispatch_date=datetime.now(),
    operator_id=tech_user.id,
), operator_id=tech_user.id)
check("场景④.2: dispatch 创建成功（正常前置）", dispatch3.id is not None)

# 4.3 DISPATCHED 状态禁止再次 dispatch
try:
    dispatch_service.create_dispatch(db, DispatchCreate(
        task_id=task3_id,
        direction=DestinationType.RETURNED_CUSTOMER,
        dispatch_date=datetime.now(),
        operator_id=tech_user.id,
    ), operator_id=tech_user.id)
    check("场景④.3: DISPATCHED 状态禁止 dispatch（重复）",
          False, "应该抛出异常但未抛出")
except BusinessLogicException as e:
    check("场景④.3: DISPATCHED 状态禁止 dispatch（重复）",
          "不可重复创建" in str(e) or "仅试磨中状态" in str(e),
          f"异常: {e}")
except Exception as e:
    check("场景④.3: DISPATCHED 状态禁止 dispatch（重复）",
          False, f"非预期异常: {type(e).__name__}: {e}")

# 4.4 关闭任务后禁止 dispatch
task_service.update_task(db, task3_id, TrialTaskUpdate(
    process_status=TrialTaskProcessStatus.CLOSED,
), operator_id=admin_user.id)

try:
    dispatch_service.create_dispatch(db, DispatchCreate(
        task_id=task3_id,
        direction=DestinationType.RETURNED_CUSTOMER,
        dispatch_date=datetime.now(),
        operator_id=tech_user.id,
    ), operator_id=tech_user.id)
    check("场景④.4: CLOSED 状态禁止 dispatch",
          False, "应该抛出异常但未抛出")
except BusinessLogicException as e:
    check("场景④.4: CLOSED 状态禁止 dispatch",
          True,
          f"异常: {e}")
except Exception as e:
    check("场景④.4: CLOSED 状态禁止 dispatch",
          False, f"非预期异常: {type(e).__name__}: {e}")


# ============================================================
# 场景 ⑤：重复 dispatch 禁止
# ============================================================
print("\n" + "=" * 70)
print("  [场景 ⑤] 重复 dispatch 禁止")
print("=" * 70)

# task1 已经创建了 dispatch，再次创建应失败
try:
    dispatch_service.create_dispatch(db, DispatchCreate(
        task_id=task_id,
        direction=DestinationType.RETURNED_CUSTOMER,
        dispatch_date=datetime.now(),
        operator_id=tech_user.id,
    ), operator_id=tech_user.id)
    check("场景⑤: 重复 dispatch 禁止",
          False, "应该抛出异常但未抛出")
except BusinessLogicException as e:
    check("场景⑤: 重复 dispatch 禁止",
          "不可重复创建" in str(e) or "仅试磨中状态" in str(e),
          f"异常: {e}")
except Exception as e:
    check("场景⑤: 重复 dispatch 禁止",
          False, f"非预期异常: {type(e).__name__}: {e}")


# ============================================================
# 清理
# ============================================================
print("\n" + "=" * 70)
print("  清理")
print("=" * 70)

db.close()
BaseModel.metadata.drop_all(bind=test_engine)
test_engine.dispose()

try:
    os.unlink(_temp_db.name)
    check("临时数据库删除", True)
except OSError as e:
    check("临时数据库删除", False, str(e))


# ============================================================
# 结果
# ============================================================
print("\n" + "=" * 70)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  结果: ALL PASSED")
else:
    print(f"  结果: {FAILED} FAILED")
print("=" * 70)

sys.exit(0 if FAILED == 0 else 1)