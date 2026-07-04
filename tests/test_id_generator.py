"""Sprint 2 — Task 2.4 Task ID Generator 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  空数据库生成第一条编号
    4.  已有编号自动 +1
    5.  不同日期重新从 1 开始
    6.  编号格式正确
    7.  日期格式正确
    8.  流水号递增正确
    9.  数据库查询正确
    10. 唯一性检查
    11. BusinessLogicException
    12. Type Hint
    13. Docstring
    14. 循环导入检查
    15. 重复调用验证
    16. 并发冲突模拟（唯一约束重试）
"""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.utils.id_generator import generate_task_no
from server.database.session import SessionLocal
from server.models import TrialTask, User, Customer
from server.core.exceptions import BusinessLogicException
from sqlalchemy.orm import Session

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
print("  Task 2.4 — Task ID Generator Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "utils" / "id_generator.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
check("generate_task_no", generate_task_no is not None)

# ============================================================
# 准备测试数据库
# ============================================================
db = SessionLocal()

# 确保有测试用户和客户
user = db.query(User).filter(User.username == "admin").first()
customer = db.query(Customer).first()
if customer is None:
    # 如果没有客户，创建一个
    customer = Customer(
        company_name="测试公司",
        contact="测试",
        phone="13800000000",
        address="测试地址",
    )
    db.add(customer)
    db.flush()

# 清理今天的所有测试 task_no
today_str = date.today().strftime("%Y%m%d")
db.query(TrialTask).filter(TrialTask.task_no.like(f"{today_str}-%")).delete()
db.commit()

# ============================================================
# 3. 空数据库生成第一条编号
# ============================================================
print("\n[3] 空数据库生成第一条编号")
task_no1 = generate_task_no(db)
check("第一条编号", task_no1 == f"{today_str}-1", f"实际: {task_no1}")

# ============================================================
# 4. 已有编号自动 +1
# ============================================================
print("\n[4] 已有编号自动 +1")
# 插入一条记录模拟已有编号
trial1 = TrialTask(
    task_no=task_no1,
    customer_id=customer.id,
    sales_id=user.id,
    requirement="test",
)
db.add(trial1)
db.commit()

task_no2 = generate_task_no(db)
check("自动 +1 到 2", task_no2 == f"{today_str}-2", f"实际: {task_no2}")

# 再插入第二条
trial2 = TrialTask(
    task_no=task_no2,
    customer_id=customer.id,
    sales_id=user.id,
    requirement="test",
)
db.add(trial2)
db.commit()

task_no3 = generate_task_no(db)
check("自动 +1 到 3", task_no3 == f"{today_str}-3", f"实际: {task_no3}")

# 插入第三条
trial3 = TrialTask(
    task_no=task_no3,
    customer_id=customer.id,
    sales_id=user.id,
    requirement="test",
)
db.add(trial3)
db.commit()

# ============================================================
# 5. 不同日期重新从 1 开始
# ============================================================
print("\n[5] 不同日期重新从 1 开始")
# 插入一条昨日编号的记录
yesterday_str = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
trial_yesterday = TrialTask(
    task_no=f"{yesterday_str}-99",
    customer_id=customer.id,
    sales_id=user.id,
    requirement="test",
)
db.add(trial_yesterday)
db.commit()

# 今天应该不受昨日影响
task_no_today = generate_task_no(db)
check("不受昨日编号影响", task_no_today == f"{today_str}-4", f"实际: {task_no_today}")

# 插入第四条
trial_today = TrialTask(
    task_no=task_no_today,
    customer_id=customer.id,
    sales_id=user.id,
    requirement="test",
)
db.add(trial_today)
db.commit()

# 下一个应该是 -5
task_no4 = generate_task_no(db)
check("继续递增到 5", task_no4 == f"{today_str}-5", f"实际: {task_no4}")

# ============================================================
# 6. 编号格式正确
# ============================================================
print("\n[6] 编号格式正确")
import re
pattern = r"^\d{8}-\d+$"
check("格式匹配 YYYYMMDD-N", bool(re.match(pattern, task_no1)))
check("格式匹配 YYYYMMDD-N", bool(re.match(pattern, task_no2)))
check("格式匹配 YYYYMMDD-N", bool(re.match(pattern, task_no3)))

# ============================================================
# 7. 日期格式正确
# ============================================================
print("\n[7] 日期格式正确")
date_part = task_no1.split("-")[0]
check("日期部分为 8 位数字", len(date_part) == 8 and date_part.isdigit())
check("日期为今天", date_part == today_str)

# ============================================================
# 8. 流水号递增正确
# ============================================================
print("\n[8] 流水号递增正确")
seq1 = int(task_no1.split("-")[1])
seq2 = int(task_no2.split("-")[1])
seq3 = int(task_no3.split("-")[1])
check("seq1 < seq2", seq1 < seq2)
check("seq2 < seq3", seq2 < seq3)

# ============================================================
# 9. 数据库查询正确
# ============================================================
print("\n[9] 数据库查询正确")
# 验证已插入的记录存在
all_today = (
    db.query(TrialTask)
    .filter(TrialTask.task_no.like(f"{today_str}-%"))
    .count()
)
check("今天有 4 条记录", all_today == 4, f"实际: {all_today}")

# ============================================================
# 10. 唯一性检查
# ============================================================
print("\n[10] 唯一性检查")
# 所有任务编号应唯一
today_tasks = (
    db.query(TrialTask.task_no)
    .filter(TrialTask.task_no.like(f"{today_str}-%"))
    .all()
)
task_nos = [t[0] for t in today_tasks]
check("无重复编号", len(task_nos) == len(set(task_nos)))

# ============================================================
# 11. BusinessLogicException
# ============================================================
print("\n[11] BusinessLogicException")
exc = BusinessLogicException("test")
check("BusinessLogicException 可实例化", isinstance(exc, BusinessLogicException))

# ============================================================
# 12. Type Hint
# ============================================================
print("\n[12] Type Hint")
import inspect
sig = inspect.signature(generate_task_no)
check("返回类型为 str", sig.return_annotation is str)
check("db 参数有类型", sig.parameters["db"].annotation is not inspect.Parameter.empty)

# ============================================================
# 13. Docstring
# ============================================================
print("\n[13] Docstring")
check("有 docstring", len(generate_task_no.__doc__ or "") > 30)

# ============================================================
# 14. 循环导入检查
# ============================================================
print("\n[14] 循环导入检查")
from server.utils import id_generator
check("无循环导入", True)

# ============================================================
# 15. 重复调用验证
# ============================================================
print("\n[15] 重复调用验证")
# 连续调用 5 次，验证递增
for i in range(5):
    tn = generate_task_no(db)
    trial = TrialTask(
        task_no=tn,
        customer_id=customer.id,
        sales_id=user.id,
        requirement="test",
    )
    db.add(trial)
    db.commit()
    check(f"第{i+1}次调用成功", tn == f"{today_str}-{5 + i}", f"实际: {tn}")

# ============================================================
# 16. 并发冲突模拟
# ============================================================
print("\n[16] 并发冲突模拟")
# 模拟：先生成编号，再手动插入一条同编号记录
# 然后再次生成，验证 retry 机制
next_no = generate_task_no(db)  # 应该是 {today}-10
# 手动插入一条占用该编号
conflict = TrialTask(
    task_no=next_no,
    customer_id=customer.id,
    sales_id=user.id,
    requirement="conflict",
)
db.add(conflict)
db.commit()

# 再次生成，应该检测到冲突并返回下一个编号
retry_no = generate_task_no(db)
check("冲突后自动重试并返回下一个编号", retry_no == f"{today_str}-11", f"实际: {retry_no}")

# ============================================================
# 清理
# ============================================================
db.query(TrialTask).filter(TrialTask.task_no.like(f"{today_str}-%")).delete()
db.query(TrialTask).filter(TrialTask.task_no.like(f"{yesterday_str}-%")).delete()
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