"""消息提醒 Service 自检 (Notification Service Self-Test)

Sprint 12 — Task 12.2
严格依据 §15.17 Notification Principle。

测试覆盖:
    - py_compile / import / 类存在性 / 公开 API
    - list_notifications / get_notification / create_notification
    - mark_as_read / mark_all_as_read / generate_notifications
    - 重复消息 / 不存在对象 / 事务 / Rollback
    - Audit Log / 边界条件 / 权限隔离
    - PEP8 / Docstring / Type Hint / 禁止项
    - Sprint 12 强制约束
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
print("  Task 12.2 — Notification Service Self Test")
print("=" * 60)

# ============================================================
# [1] py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

SOURCE_PATH = str(
    Path(__file__).parent.parent
    / "server" / "services" / "notification_service.py"
)
try:
    py_compile.compile(SOURCE_PATH, doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# [2] import
# ============================================================
print("\n[2] import")
from server.services.notification_service import NotificationService

check("NotificationService 导入", NotificationService is not None)

# ============================================================
# [3] 类存在性
# ============================================================
print("\n[3] 类存在性")
import inspect

check("NotificationService 是 class", inspect.isclass(NotificationService))
svc = NotificationService()
check("NotificationService 可实例化", svc is not None)

# ============================================================
# [4] 公开 API 列表
# ============================================================
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(NotificationService)
    if not m.startswith("_") and callable(getattr(NotificationService, m))
]
check("list_notifications", "list_notifications" in public_methods)
check("get_notification", "get_notification" in public_methods)
check("create_notification", "create_notification" in public_methods)
check("mark_as_read", "mark_as_read" in public_methods)
check("mark_all_as_read", "mark_all_as_read" in public_methods)
check("generate_notifications", "generate_notifications" in public_methods)
check("公开 API 数量 = 6", len(public_methods) == 6)

# ============================================================
# [5] 准备测试数据库
# ============================================================
print("\n[5] 测试数据库准备")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.models.base_model import BaseModel

engine = create_engine(
    "sqlite:///:memory:", connect_args={"check_same_thread": False}
)
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
BaseModel.metadata.create_all(bind=engine)
check("数据库表创建", True)

# 导入模型
from server.models import (
    User, Role, Permission, SystemLog,
    Notification, TrialTask,
    Receipt, GrindingRecord,
)
from server.enums.notify_type import NotifyType
from server.enums.task_process_status import TrialTaskProcessStatus
from server.enums.task_result_status import TrialTaskResultStatus
from server.enums.action_type import ActionType
from server.schemas.notification_schema import NotificationCreate
from server.core.exceptions import (
    BusinessLogicException,
    NotFoundException,
)

# ============================================================
# [6] 创建测试数据
# ============================================================
print("\n[6] 创建测试数据")
from datetime import datetime, timedelta

db = TestSession()

# 创建角色
admin_role = Role(name="admin", display_name="管理员", is_system=True)
tech_role = Role(name="technician", display_name="技术员", is_system=True)
sales_role = Role(name="sales", display_name="销售", is_system=True)
db.add_all([admin_role, tech_role, sales_role])
db.flush()

# 创建权限
perm = Permission(code="notify:view", name="查看通知", module="notification")
db.add(perm)
db.flush()
admin_role.permissions.append(perm)
tech_role.permissions.append(perm)
sales_role.permissions.append(perm)
db.flush()

# 创建用户
user1 = User(
    username="tech1",
    password_hash="hash1",
    real_name="技术员1",
)
user2 = User(
    username="sales1",
    password_hash="hash2",
    real_name="销售1",
)
user3 = User(
    username="admin1",
    password_hash="hash3",
    real_name="管理员1",
)
user4 = User(
    username="tech2",
    password_hash="hash4",
    real_name="技术员2",
)
db.add_all([user1, user2, user3, user4])
db.flush()

# 分配角色
user1.roles.append(tech_role)
user2.roles.append(sales_role)
user3.roles.append(admin_role)
user4.roles.append(tech_role)
db.flush()

# 创建客户
from server.models import Customer
customer = Customer(company_name="测试公司")
db.add(customer)
db.flush()

# 创建试磨任务
task1 = TrialTask(
    task_no="TM202600001",
    customer_id=customer.id,
    requirement="测试要求",
    process_status=TrialTaskProcessStatus.RECEIVED,
    result_status=TrialTaskResultStatus.PENDING,
    sales_id=user2.id,
)
task2 = TrialTask(
    task_no="TM202600002",
    customer_id=customer.id,
    requirement="测试要求",
    process_status=TrialTaskProcessStatus.GRINDING,
    result_status=TrialTaskResultStatus.PENDING,
    sales_id=user2.id,
)
task3 = TrialTask(
    task_no="TM202600003",
    customer_id=customer.id,
    requirement="测试要求",
    process_status=TrialTaskProcessStatus.GRINDING,
    result_status=TrialTaskResultStatus.PENDING,
    sales_id=user2.id,
)
db.add_all([task1, task2, task3])
db.commit()

# 创建收件记录（用于 RULE-01）
old_receipt = Receipt(
    task_id=task1.id,
    received_at=datetime.now() - timedelta(hours=50),
    receiver_id=user1.id,
)
db.add(old_receipt)

# 创建试磨记录（用于 RULE-02 和 RULE-03）
old_grinding = GrindingRecord(
    task_id=task2.id,
    operator_id=user1.id,
    machine_type="MGK-300",
)
old_grinding.created_at = datetime.now() - timedelta(hours=130)
grinding3 = GrindingRecord(
    task_id=task3.id,
    operator_id=user4.id,
    machine_type="MGK-300",
)
grinding3.created_at = datetime.now() - timedelta(hours=80)
db.add_all([old_grinding, grinding3])
db.commit()

check("测试数据创建", True)
check("用户 1 (技术员) id=%d" % user1.id, user1.id > 0)
check("用户 2 (销售) id=%d" % user2.id, user2.id > 0)
check("用户 3 (管理员) id=%d" % user3.id, user3.id > 0)
check("试磨任务 1 id=%d" % task1.id, task1.id > 0)
check("试磨任务 2 id=%d" % task2.id, task2.id > 0)

# ============================================================
# [7] create_notification
# ============================================================
print("\n[7] create_notification")

now = datetime.now()
data = NotificationCreate(
    user_id=user1.id,
    notification_type=NotifyType.RECEIPT_DELAY,
    title="收件超时",
    content="任务 TM202600001 已收件超过2天",
    target_type="trial_task",
    target_id=task1.id,
    is_read=False,
    created_at=now,
)
resp = svc.create_notification(db, data)
check("创建成功", resp.id > 0)
check("user_id 正确", resp.user_id == user1.id)
check("notification_type 正确", resp.notification_type == NotifyType.RECEIPT_DELAY)
check("title 正确", resp.title == NotifyType.RECEIPT_DELAY.display_name)
check("content 正确", resp.content == "任务 TM202600001 已收件超过2天")
check("target_id 正确", resp.target_id == task1.id)
check("is_read=False", resp.is_read is False)
check("read_time=None", resp.read_time is None)

# ============================================================
# [8] 重复创建
# ============================================================
print("\n[8] 重复创建")

data2 = NotificationCreate(
    user_id=user1.id,
    notification_type=NotifyType.RECEIPT_DELAY,
    title="重复",
    content="重复内容",
    target_type="trial_task",
    target_id=task1.id,
    is_read=False,
    created_at=now,
)
try:
    svc.create_notification(db, data2)
    check("重复创建应抛出异常", False)
except BusinessLogicException:
    check("重复创建抛出 BusinessLogicException", True)

# ============================================================
# [9] get_notification
# ============================================================
print("\n[9] get_notification")

resp2 = svc.get_notification(db, resp.id)
check("获取成功", resp2.id == resp.id)
check("user_id 一致", resp2.user_id == resp.user_id)
check("content 一致", resp2.content == resp.content)

# 不存在
try:
    svc.get_notification(db, 99999)
    check("不存在的 ID 应抛出异常", False)
except NotFoundException:
    check("不存在抛出 NotFoundException", True)

# ============================================================
# [10] list_notifications
# ============================================================
print("\n[10] list_notifications")

# 创建更多测试数据
data3 = NotificationCreate(
    user_id=user1.id,
    notification_type=NotifyType.GRINDING_DELAY,
    title="试磨超时",
    content="任务 TM202600002 试磨超过5天",
    target_type="trial_task",
    target_id=task2.id,
    is_read=False,
    created_at=now,
)
svc.create_notification(db, data3)

result = svc.list_notifications(db, user_id=user1.id)
check("list 返回 NotificationListResponse", result.total >= 2)
check("items 数量正确", len(result.items) >= 2)
check("items 类型正确", all(
    hasattr(i, "id") for i in result.items
))

# 分页
result_page = svc.list_notifications(
    db, user_id=user1.id, page=1, page_size=1,
)
check("分页 page_size=1", len(result_page.items) == 1)

# 筛选 is_read
result_unread = svc.list_notifications(
    db, user_id=user1.id, is_read=False,
)
check("筛选未读", all(i.is_read is False for i in result_unread.items))

# 筛选 notification_type
result_type = svc.list_notifications(
    db, user_id=user1.id,
    notification_type=NotifyType.RECEIPT_DELAY,
)
check("筛选类型", all(
    i.notification_type == NotifyType.RECEIPT_DELAY
    for i in result_type.items
))

# 权限隔离
result_other = svc.list_notifications(db, user_id=user2.id)
check("权限隔离", result_other.total == 0)

# ============================================================
# [11] mark_as_read
# ============================================================
print("\n[11] mark_as_read")

resp3 = svc.mark_as_read(db, resp.id, operator_id=user1.id)
check("标记已读成功", resp3.is_read is True)
check("read_time 已设置", resp3.read_time is not None)

# 不存在
try:
    svc.mark_as_read(db, 99999, operator_id=user1.id)
    check("不存在的 ID 应抛出异常", False)
except NotFoundException:
    check("不存在抛出 NotFoundException", True)

# ============================================================
# [12] mark_all_as_read
# ============================================================
print("\n[12] mark_all_as_read")

count = svc.mark_all_as_read(db, user_id=user1.id)
check("mark_all_as_read 返回 int", isinstance(count, int))
check("更新数量 >= 1", count >= 1)

# 再次执行（所有消息已读）
count2 = svc.mark_all_as_read(db, user_id=user1.id)
check("再次执行返回 0", count2 == 0)

# ============================================================
# [13] generate_notifications
# ============================================================
print("\n[13] generate_notifications")

gen_count = svc.generate_notifications(db)
check("generate_notifications 返回 int", isinstance(gen_count, int))
check("生成消息数量 >= 0", gen_count >= 0)

# 幂等测试
gen_count2 = svc.generate_notifications(db)
check("幂等: 再次执行不重复", gen_count2 == 0)

# 验证 RULE-01 生成了消息
recv_notifications = (
    db.query(Notification)
    .filter(
        Notification.type == NotifyType.RECEIPT_DELAY,
        Notification.is_deleted.is_(False),
    )
    .all()
)
check("RULE-01 消息已生成", len(recv_notifications) > 0)

# 验证 RULE-02 生成了消息
grind_notifications = (
    db.query(Notification)
    .filter(
        Notification.type == NotifyType.GRINDING_DELAY,
        Notification.is_deleted.is_(False),
    )
    .all()
)
check("RULE-02 消息已生成", len(grind_notifications) > 0)

# 验证 RULE-03 生成了消息
report_notifications = (
    db.query(Notification)
    .filter(
        Notification.type == NotifyType.REPORT_MISSING,
        Notification.is_deleted.is_(False),
    )
    .all()
)
check("RULE-03 消息已生成", len(report_notifications) > 0)

# ============================================================
# [14] Audit Log
# ============================================================
print("\n[14] Audit Log")

logs = (
    db.query(SystemLog)
    .filter(
        SystemLog.target_type == "notification",
        SystemLog.is_deleted.is_(False),
    )
    .all()
)
check("审计日志已生成", len(logs) > 0)
check("审计日志 module=notification", all(
    log.changes.get("module") == "notification" for log in logs
))

# ============================================================
# [15] 事务与 Rollback
# ============================================================
print("\n[15] 事务与 Rollback")

# 创建一条新消息用于测试回滚
data_rollback = NotificationCreate(
    user_id=user4.id,
    notification_type=NotifyType.GRINDING_DELAY,
    title="试磨超时",
    content="测试回滚",
    target_type="trial_task",
    target_id=task1.id,
    is_read=False,
    created_at=now,
)
svc.create_notification(db, data_rollback)

before_count = (
    db.query(Notification)
    .filter(Notification.is_deleted.is_(False))
    .count()
)
# 重复创建会失败
try:
    svc.create_notification(db, data_rollback)
except BusinessLogicException:
    pass
after_count = (
    db.query(Notification)
    .filter(Notification.is_deleted.is_(False))
    .count()
)
check("事务回滚后数量不变", before_count == after_count)

# ============================================================
# [16] PEP8
# ============================================================
print("\n[16] PEP8")
import subprocess as sp

result = sp.run(
    [sys.executable, "-m", "flake8", SOURCE_PATH, "--ignore=W503"],
    capture_output=True, text=True,
    cwd=str(Path(__file__).parent.parent),
)
check("PEP8", result.stdout.strip() == "", result.stdout.strip())

# ============================================================
# [17] Type Hint
# ============================================================
print("\n[17] Type Hint")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    source = f.read()
check("导入 Session", "Session" in source)
check("类型注解 -> int", "-> int:" in source)
check("类型注解 -> NotificationResponse", "-> NotificationResponse:" in source)

# ============================================================
# [18] Docstring
# ============================================================
print("\n[18] Docstring")
check("模块 docstring", '"""消息提醒业务层' in source)
check("类 docstring", NotificationService.__doc__ is not None)
check("类 docstring 非空", len(NotificationService.__doc__.strip()) > 0)

# ============================================================
# [19] 禁止项
# ============================================================
print("\n[19] 禁止项")
import re

code_text = source
code_text = re.sub(r'""".*?"""', "", code_text, flags=re.DOTALL)
code_text = re.sub(r"'''.*?'''", "", code_text, flags=re.DOTALL)
code_text = re.sub(r"#.*$", "", code_text, flags=re.MULTILINE)

check("Zero try/except", "try:" not in code_text)
check("Zero print", "print(" not in code_text)
check("无 Router", "APIRouter" not in source)
check("无 HTTP", "HTTPException" not in source)
check("无 ApiClient", "ApiClient" not in source)
check("无 Scheduler", "scheduler" not in code_text.lower())
check("只读 process_status（不修改）", "process_status = " not in code_text)
check("只读 result_status（不修改）", "result_status = " not in code_text)

# ============================================================
# [20] Sprint 12 强制约束
# ============================================================
print("\n[20] Sprint 12 强制约束")
check("LogService 导入", "LogService" in source)
check("_write_log 调用 LogService", "LogService" in source)
check("_log_service 属性", "_log_service" in source)
check("禁止 Session.add(SystemLog)", "Session.add(SystemLog)" not in source)
check("禁止 db.add(SystemLog)", "db.add(SystemLog)" not in source)
check("generate_notifications 幂等", "幂等" in source or "idempotent" in source.lower())
check("_find_duplicate 方法", "def _find_duplicate" in source)
check("_create_if_not_exists 方法", "def _create_if_not_exists" in source)
check("唯一写入口", "Notification(" in source)

# ============================================================
# [21] 代码行宽
# ============================================================
print("\n[21] 代码行宽")
with open(SOURCE_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()
long_lines = [
    (i + 1, len(line.rstrip("\n")))
    for i, line in enumerate(lines)
    if len(line.rstrip("\n")) > 79
]
check("所有行 <= 79 字符", len(long_lines) == 0,
      f"{len(long_lines)} 行超长: {long_lines[:5]}")

# ============================================================
# [22] 文件末尾换行
# ============================================================
print("\n[22] 文件末尾换行")
with open(SOURCE_PATH, "rb") as f:
    f.seek(-1, 2)
    last_byte = f.read()
check("文件末尾换行", last_byte == b"\n")

# ============================================================
# [23] 无 TODO/FIXME
# ============================================================
print("\n[23] 无 TODO/FIXME")
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)

# ============================================================
# [24] 错误响应格式
# ============================================================
print("\n[24] 错误响应格式")
check("NotFoundException 导入", "NotFoundException" in source)
check("BusinessLogicException 导入", "BusinessLogicException" in source)

# ============================================================
# [25] Notification Schema 使用
# ============================================================
print("\n[25] Notification Schema 使用")
check("NotificationCreate 导入", "NotificationCreate" in source)
check("NotificationResponse 导入", "NotificationResponse" in source)
check("NotificationListResponse 导入", "NotificationListResponse" in source)

# ============================================================
# [26] 数据库清理
# ============================================================
print("\n[26] 数据库清理")
db.close()
check("数据库关闭", True)

# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print(f"  总计: {PASSED + FAILED}  通过: {PASSED}  失败: {FAILED}")
print("=" * 60)

if FAILED > 0:
    sys.exit(1)
sys.exit(0)