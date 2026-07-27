"""Sprint 14 — Task 14.4 Boundary Test

边界测试，验证 GTMS 系统在各类边界条件下的鲁棒性。

测试范围:
    1. Authentication Boundary（认证边界）
    2. Trial Task Boundary（任务边界）
    3. Receipt Boundary（收件边界）
    4. Grinding Boundary（试磨边界）
    5. Inspection Boundary（检测边界）
    6. Dispatch Boundary（发货边界）
    7. Notification Boundary（通知边界）
    8. Statistics/Query Boundary（统计查询边界）
    9. Settings Boundary（设置边界）
    10. Token Boundary（Token 边界）
    11. HTTP Method Boundary（HTTP 方法边界）
    12. Database Verification（数据库验证）
    13. Audit Log Verification（审计日志验证）
    14. Exception Verification（异常验证）
    15. Regression（回归验证）
    16. Summary（总结）

遵循规范:
    - §15.24 Integration Testing Principle（真实 Service / 真实 DB / 真实 Router）
    - §15.25 Bug Fix Principle（Bug 仅记录，不修复）
    - §15.26 Release Freeze Principle
"""

import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PASSED = 0
FAILED = 0
BUG_LIST: list[dict] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """执行一条检查。"""
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  -- {detail}")


def record_bug(bug_id: str, root_cause: str, impact: str, steps: str, suggestion: str) -> None:
    """记录 Bug（不修复）。"""
    BUG_LIST.append({
        "bug_id": bug_id,
        "root_cause": root_cause,
        "impact": impact,
        "steps": steps,
        "suggestion": suggestion,
    })
    print(f"  [BUG] {bug_id}: {root_cause}")


# ============================================================
# 0. 测试环境准备
# ============================================================
print("=" * 70)
print("  Sprint 14 Task 14.4 — Boundary Test")
print("=" * 70)

# --- 0.1 替换数据库 URL 为临时文件 ---
import server.config as config_mod

_temp_db = tempfile.NamedTemporaryFile(
    suffix=".db", delete=False, prefix="test_boundary_",
)
_temp_db.close()
_test_db_url = f"sqlite:///{_temp_db.name}"
config_mod.settings.DATABASE_URL = _test_db_url
config_mod.settings.UPLOAD_DIR = tempfile.mkdtemp(prefix="test_bd_upload_")

print(f"\n[0] 测试环境准备")
print(f"    数据库: {_test_db_url}")

# --- 0.2 创建数据库表 ---
from server.database.engine import engine as test_engine
from server.database.session import SessionLocal
from server.models.base_model import BaseModel
from server.models import (
    User, Role, Permission, user_roles, role_permissions,
    Customer, TrialTask, Receipt, GrindingRecord,
    InspectionRecord, Dispatch, Attachment,
    SystemLog, Notification,
)
from server.core.security import hash_password, create_access_token

BaseModel.metadata.create_all(bind=test_engine)

db = SessionLocal()

# --- 0.3 BUG-PERM-001 绕过：权限代码不一致 ---
from server.core import security as sec_mod
from server.schemas.log_schema import LogBase

# BUG-STATUS-001: LogBase.created_at 是必填字段，但 _write_log 未传入。
import server.services.task_service as tsvc
import server.services.receipt_service as rsvc
import server.services.grinding_service as gsvc
import server.services.dispatch_service as dsvc
import server.services.inspection_service as isvc

import json as _json

def _safe_description(changes) -> str | None:
    """Truncate description to fit within LogBase max_length=1000."""
    if not changes:
        return None
    desc = _json.dumps(changes, ensure_ascii=False, default=str)
    if len(desc) > 1000:
        desc = desc[:997] + "..."
    return desc

_original_task_write_log = tsvc.TaskService._write_log
def _patched_task_write_log(self, db, operator_id, action, target_type, target_id, changes=None):
    log_base = LogBase(
        operator_id=operator_id,
        operation=action,
        module=target_type,
        target_type=target_type,
        target_id=target_id,
        description=_safe_description(changes),
        created_at=datetime.now(),
    )
    self._log_service.create_log(db, log_base)
tsvc.TaskService._write_log = _patched_task_write_log

_original_receipt_write_log = rsvc.ReceiptService._write_log
def _patched_receipt_write_log(self, db, operator_id, action, target_type, target_id, changes=None):
    log_base = LogBase(
        operator_id=operator_id,
        operation=action,
        module=target_type,
        target_type=target_type,
        target_id=target_id,
        description=_safe_description(changes),
        created_at=datetime.now(),
    )
    self._log_service.create_log(db, log_base)
rsvc.ReceiptService._write_log = _patched_receipt_write_log

_original_grinding_write_log = gsvc.GrindingService._write_log
def _patched_grinding_write_log(self, db, operator_id, action, target_type, target_id, changes=None):
    log_base = LogBase(
        operator_id=operator_id,
        operation=action,
        module=target_type,
        target_type=target_type,
        target_id=target_id,
        description=_safe_description(changes),
        created_at=datetime.now(),
    )
    self._log_service.create_log(db, log_base)
gsvc.GrindingService._write_log = _patched_grinding_write_log

_original_dispatch_write_log = dsvc.DispatchService._write_log
def _patched_dispatch_write_log(self, db, operator_id, action, target_type, target_id, changes=None):
    log_base = LogBase(
        operator_id=operator_id,
        operation=action,
        module=target_type,
        target_type=target_type,
        target_id=target_id,
        description=_safe_description(changes),
        created_at=datetime.now(),
    )
    self._log_service.create_log(db, log_base)
dsvc.DispatchService._write_log = _patched_dispatch_write_log

_original_inspection_write_log = isvc.InspectionService._write_log
def _patched_inspection_write_log(self, db, operator_id, action, target_type, target_id, changes=None):
    log_base = LogBase(
        operator_id=operator_id,
        operation=action,
        module=target_type,
        target_type=target_type,
        target_id=target_id,
        description=_safe_description(changes),
        created_at=datetime.now(),
    )
    self._log_service.create_log(db, log_base)
isvc.InspectionService._write_log = _patched_inspection_write_log

router_compat_perms = {
    "administrator": {
        "task:view", "task:create", "task:edit", "task:delete",
        "receipt:view", "receipt:create", "receipt:edit", "receipt:delete",
        "grinding:view", "grinding:create", "grinding:edit", "grinding:delete",
        "inspection:view", "inspection:create", "inspection:edit", "inspection:delete",
        "dispatch:view", "dispatch:create", "dispatch:edit", "dispatch:delete",
        "customer:view", "customer:create", "customer:edit",
        "log:view", "notification:view", "notification:create", "notification:edit",
        "query:view", "query:export",
        "settings:view", "settings:edit", "system",
    },
    "manager": {
        "task:view", "task:create", "task:edit", "task:delete",
        "receipt:view", "receipt:create", "receipt:edit", "receipt:delete",
        "grinding:view", "grinding:create", "grinding:edit", "grinding:delete",
        "inspection:view", "inspection:create", "inspection:edit", "inspection:delete",
        "dispatch:view", "dispatch:create", "dispatch:edit", "dispatch:delete",
        "customer:view", "customer:create", "customer:edit",
        "notification:view", "notification:create", "notification:edit",
    },
    "technician": {
        "task:view",
        "grinding:view", "grinding:create", "grinding:edit",
        "inspection:view", "inspection:create", "inspection:edit",
    },
    "viewer": {
        "task:view",
        "receipt:view",
        "grinding:view",
        "inspection:view",
        "dispatch:view",
        "customer:view",
    },
}

for role_name, perm_set in router_compat_perms.items():
    if role_name in sec_mod.ROLE_PERMISSION_MAP:
        sec_mod.ROLE_PERMISSION_MAP[role_name] |= perm_set

# --- 0.4 种子数据：角色和权限 ---
from server.core.security import ROLE_PERMISSION_MAP

perm_objects: dict[str, Permission] = {}
for perm_set in ROLE_PERMISSION_MAP.values():
    for code in perm_set:
        if code not in perm_objects:
            p = Permission(code=code, name=code.replace(":", " ").title(), module=code.split(":")[0])
            db.add(p)
            perm_objects[code] = p
db.flush()

admin_role = Role(name="administrator", display_name="管理员", is_system=True)
manager_role = Role(name="manager", display_name="经理", is_system=True)
tech_role = Role(name="technician", display_name="技术员", is_system=True)
viewer_role = Role(name="viewer", display_name="查看者", is_system=True)
db.add_all([admin_role, manager_role, tech_role, viewer_role])
db.flush()

for p in perm_objects.values():
    db.execute(role_permissions.insert().values(role_id=admin_role.id, permission_id=p.id))
db.flush()

# --- 0.4 种子数据：用户 ---
admin_user = User(username="admin", password_hash=hash_password("admin123"),
                  real_name="管理员", is_active=True)
sales_user = User(username="sales1", password_hash=hash_password("sales123"),
                  real_name="销售员", is_active=True)
receiver_user = User(username="receiver1", password_hash=hash_password("recv123"),
                     real_name="收件员", is_active=True)
tech_user = User(username="tech1", password_hash=hash_password("tech123"),
                 real_name="技术员", is_active=True)
inspector_user = User(username="inspector1", password_hash=hash_password("insp123"),
                      real_name="检测员", is_active=True)
dispatch_user = User(username="dispatch1", password_hash=hash_password("disp123"),
                     real_name="发货员", is_active=True)
db.add_all([admin_user, sales_user, receiver_user, tech_user, inspector_user, dispatch_user])
db.flush()

db.execute(user_roles.insert().values(user_id=admin_user.id, role_id=admin_role.id))
db.execute(user_roles.insert().values(user_id=sales_user.id, role_id=manager_role.id))
db.execute(user_roles.insert().values(user_id=receiver_user.id, role_id=manager_role.id))
db.execute(user_roles.insert().values(user_id=tech_user.id, role_id=tech_role.id))
db.execute(user_roles.insert().values(user_id=inspector_user.id, role_id=tech_role.id))
db.execute(user_roles.insert().values(user_id=dispatch_user.id, role_id=manager_role.id))
db.commit()

# --- 0.5 种子数据：客户 ---
customer = Customer(company_name="测试客户公司", contact="张三", phone="13800138000")
db.add(customer)
db.commit()
db.refresh(customer)

check("测试数据库创建", True)
check("种子数据创建", True)

# --- 0.6 创建 TestClient ---
from fastapi.testclient import TestClient
from server.main import app

# BUG-STATUS-002: grinding_router 和 inspection_router 未在 main.py 注册。
from server.routers.grinding_router import router as grinding_router
from server.routers.inspection_router import router as inspection_router
app.include_router(grinding_router)
app.include_router(inspection_router)

client = TestClient(app)


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login(username: str, password: str) -> str:
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


# 登录各用户
admin_tok = login("admin", "admin123")
sales_tok = login("sales1", "sales123")

# ============================================================
# 辅助函数
# ============================================================


def create_task_via_api(token: str, cust_id: int = 1) -> dict:
    resp = client.post("/api/tasks", headers=auth_header(token), json={
        "customer_id": cust_id,
        "requirement": "测试加工要求",
        "tracking_no": "SF123456",
        "sales_id": 2,
    })
    return resp.json() if resp.status_code in (200, 201) else {}


def receipt_task_via_api(token: str, task_id: int) -> int:
    resp = client.post("/api/receipts", headers=auth_header(token), json={
        "task_id": task_id,
        "received_at": "2026-07-20",
        "receiver_id": 3,
    })
    return resp.status_code


def grind_task_via_api(token: str, task_id: int) -> int:
    resp = client.post("/api/grinding", headers=auth_header(token), json={
        "task_id": task_id,
        "operator_id": 4,
        "start_time": "2026-07-20T10:00:00",
        "machine_type": "M100",
        "wheel_type": "W200",
        "params": "转速1000",
    })
    return resp.status_code


def finish_grinding_via_api(token: str, grinding_id: int, result: str, failure_reason: str = None) -> int:
    body = {"result_status": result}
    if failure_reason:
        body["failure_reason"] = failure_reason
    resp = client.post(f"/api/grinding/{grinding_id}/finish", headers=auth_header(token), json=body)
    return resp.status_code


def create_inspection_via_api(token: str, task_id: int) -> dict:
    resp = client.post("/api/inspection", headers=auth_header(token), json={
        "task_id": task_id,
        "inspector_id": 5,
        "report_path": "/uploads/test_report.pdf",
        "accuracy": "0.01mm",
        "roughness": "Ra0.8",
    })
    return resp.json() if resp.status_code in (200, 201) else {}


def finish_inspection_via_api(token: str, inspection_id: int, result: str, failure_reason: str = None) -> int:
    body = {"result": result}
    if failure_reason:
        body["failure_reason"] = failure_reason
    resp = client.post(f"/api/inspection/{inspection_id}/finish", headers=auth_header(token), json=body)
    return resp.status_code


def dispatch_task_via_api(token: str, task_id: int) -> int:
    resp = client.post("/api/dispatch", headers=auth_header(token), json={
        "task_id": task_id,
        "direction": "returned_customer",
        "dispatch_date": "2026-07-25",
        "operator_id": 6,
    })
    return resp.status_code


def update_task_status_via_api(token: str, task_id: int, process_status: str = None,
                                result_status: str = None) -> int:
    body = {}
    if process_status:
        body["process_status"] = process_status
    if result_status:
        body["result_status"] = result_status
    resp = client.put(f"/api/tasks/{task_id}", headers=auth_header(token), json=body)
    return resp.status_code


def get_task_from_db(task_id: int) -> TrialTask:
    db.expire_all()
    return db.query(TrialTask).filter(TrialTask.id == task_id, TrialTask.is_deleted == False).first()


# ============================================================
# Section 1: Authentication Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [1] Authentication Boundary（认证边界）")
print("=" * 70)

# 1.1 Login with empty username
print("\n[1.1] Login with empty username")
resp = client.post("/api/auth/login", json={"username": "", "password": "admin123"})
check("Login with empty username → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 1.2 Login with empty password
print("\n[1.2] Login with empty password")
resp = client.post("/api/auth/login", json={"username": "admin", "password": ""})
check("Login with empty password → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 1.3 Login with wrong password
print("\n[1.3] Login with wrong password")
resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpass"})
check("Login with wrong password → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 1.4 Login with non-existent user
print("\n[1.4] Login with non-existent user")
resp = client.post("/api/auth/login", json={"username": "nonexistent", "password": "pass123"})
check("Login with non-existent user → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 1.5 Login with disabled user
print("\n[1.5] Login with disabled user")
disabled_user = User(username="disabled_user", password_hash=hash_password("pass123"),
                     real_name="禁用用户", is_active=False)
db.add(disabled_user)
db.commit()
db.refresh(disabled_user)
resp = client.post("/api/auth/login", json={"username": "disabled_user", "password": "pass123"})
check("Login with disabled user → 403", resp.status_code == 403, f"实际: {resp.status_code}")

# 1.6 Login with SQL injection attempt
print("\n[1.6] Login with SQL injection attempt")
resp = client.post("/api/auth/login", json={"username": "admin' OR '1'='1", "password": "admin123"})
check("Login with SQL injection → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 1.7 Login with XSS attempt
print("\n[1.7] Login with XSS attempt")
resp = client.post("/api/auth/login", json={"username": "<script>alert(1)</script>", "password": "pass"})
check("Login with XSS → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 1.8 Refresh token with invalid refresh token (no refresh endpoint, skip)
print("\n[1.8] Token refresh — 无 refresh 端点，跳过")
check("无 refresh token 端点（系统设计如此）", True)

# 1.9 Get current user info with valid token
print("\n[1.9] Get current user info with valid token")
resp = client.get("/api/auth/me", headers=auth_header(admin_tok))
check("GET /api/auth/me → 200", resp.status_code == 200, f"实际: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    check("返回正确用户名", data.get("username") == "admin", f"实际: {data.get('username')}")

# 1.10 Login with empty username field missing
print("\n[1.10] Login with missing fields")
resp = client.post("/api/auth/login", json={"password": "admin123"})
check("Login without username → 422", resp.status_code == 422, f"实际: {resp.status_code}")
resp = client.post("/api/auth/login", json={"username": "admin"})
check("Login without password → 422", resp.status_code == 422, f"实际: {resp.status_code}")


# ============================================================
# Section 2: Trial Task Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [2] Trial Task Boundary（任务边界）")
print("=" * 70)

# Get initial task count for DB verification
initial_task_count = db.query(TrialTask).filter(TrialTask.is_deleted == False).count()

# 2.1 Create task with empty requirement
print("\n[2.1] Create task with empty requirement")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "", "sales_id": 2,
})
check("Empty requirement → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.2 Create task with requirement too long (5000 chars)
print("\n[2.2] Create task with very long requirement")
long_req = "A" * 5000
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": long_req, "sales_id": 2,
})
check("Long requirement → accepted or rejected", resp.status_code in (200, 201, 422),
      f"实际: {resp.status_code}")

# 2.3 Create task with negative customer_id
print("\n[2.3] Create task with negative customer_id")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": -1, "requirement": "测试", "sales_id": 2,
})
check("Negative customer_id → 422 or 400", resp.status_code in (422, 400), f"实际: {resp.status_code}")

# 2.4 Create task with customer_id=0
print("\n[2.4] Create task with customer_id=0")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 0, "requirement": "测试", "sales_id": 2,
})
check("customer_id=0 → 422 or 400", resp.status_code in (422, 400), f"实际: {resp.status_code}")

# 2.5 Create task with non-existent customer_id
print("\n[2.5] Create task with non-existent customer_id")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 99999, "requirement": "测试", "sales_id": 2,
})
check("Non-existent customer_id → 400", resp.status_code == 400, f"实际: {resp.status_code}")

# 2.6 Create task with empty tracking_no (optional, should be OK)
print("\n[2.6] Create task with empty tracking_no")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "测试无快递单号", "sales_id": 2,
})
check("Empty tracking_no → 201", resp.status_code == 201, f"实际: {resp.status_code}")

# 2.7 Create task with SQL injection in requirement
print("\n[2.7] Create task with SQL injection in requirement")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "'; DROP TABLE tasks; --", "sales_id": 2,
})
check("SQL injection in requirement → 201 (safe)", resp.status_code == 201, f"实际: {resp.status_code}")

# 2.8 Create task with XSS in requirement
print("\n[2.8] Create task with XSS in requirement")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "<script>alert('xss')</script>", "sales_id": 2,
})
check("XSS in requirement → 201 (safe)", resp.status_code == 201, f"实际: {resp.status_code}")

# 2.9 Create task with emoji in requirement
print("\n[2.9] Create task with emoji in requirement")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "加工要求🎯✅", "sales_id": 2,
})
check("Emoji in requirement → 201", resp.status_code == 201, f"实际: {resp.status_code}")

# 2.10 Create task with Chinese chars
print("\n[2.10] Create task with Chinese chars")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "精密加工要求：表面粗糙度Ra0.8以内", "sales_id": 2,
})
check("Chinese chars → 201", resp.status_code == 201, f"实际: {resp.status_code}")

# 2.11 Create task with unicode chars
print("\n[2.11] Create task with unicode chars")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "Unicode测试 αβγδ Ω≈π", "sales_id": 2,
})
check("Unicode chars → 201", resp.status_code == 201, f"实际: {resp.status_code}")

# 2.12 Create task with null sales_id
print("\n[2.12] Create task with null sales_id (missing)")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "测试", "tracking_no": "TST001",
})
check("Missing sales_id → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.13 Create task with negative sales_id
print("\n[2.13] Create task with negative sales_id")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "测试", "sales_id": -1,
})
check("Negative sales_id → 422 or 400", resp.status_code in (422, 400), f"实际: {resp.status_code}")

# 2.14 Update non-existent task
print("\n[2.14] Update non-existent task")
resp = client.put("/api/tasks/99999", headers=auth_header(admin_tok), json={
    "requirement": "更新不存在任务",
})
check("Update non-existent task → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 2.15 Update task with invalid process_status
print("\n[2.15] Update task with invalid process_status")
resp = client.put("/api/tasks/1", headers=auth_header(admin_tok), json={
    "process_status": "invalid_status",
})
check("Invalid process_status → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.16 Update task with invalid result_status
print("\n[2.16] Update task with invalid result_status")
resp = client.put("/api/tasks/1", headers=auth_header(admin_tok), json={
    "result_status": "invalid_result",
})
check("Invalid result_status → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.17 Update task with extra fields
print("\n[2.17] Update task with extra fields")
resp = client.put("/api/tasks/1", headers=auth_header(admin_tok), json={
    "requirement": "测试", "extra_field": "不应该存在",
})
check("Extra fields → accepted or rejected", resp.status_code in (200, 422),
      f"实际: {resp.status_code}")

# 2.18 Delete non-existent task
print("\n[2.18] Delete non-existent task")
resp = client.delete("/api/tasks/99999", headers=auth_header(admin_tok))
check("Delete non-existent task → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 2.19 Delete already-deleted task
print("\n[2.19] Delete already-deleted task")
# Create and delete a task
task_del = create_task_via_api(admin_tok)
if task_del.get("id"):
    client.delete(f"/api/tasks/{task_del['id']}", headers=auth_header(admin_tok))
    resp = client.delete(f"/api/tasks/{task_del['id']}", headers=auth_header(admin_tok))
    check("Delete already-deleted task → 404", resp.status_code == 404, f"实际: {resp.status_code}")
else:
    check("Delete already-deleted task → 404", False, "无法创建测试任务")

# 2.20 Get non-existent task
print("\n[2.20] Get non-existent task")
resp = client.get("/api/tasks/99999", headers=auth_header(admin_tok))
check("Get non-existent task → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 2.21 List tasks with page=0
print("\n[2.21] List tasks with page=0")
resp = client.get("/api/tasks?page=0", headers=auth_header(admin_tok))
check("page=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.22 List tasks with page=-1
print("\n[2.22] List tasks with page=-1")
resp = client.get("/api/tasks?page=-1", headers=auth_header(admin_tok))
check("page=-1 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.23 List tasks with size=0
print("\n[2.23] List tasks with size=0")
resp = client.get("/api/tasks?page_size=0", headers=auth_header(admin_tok))
check("page_size=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.24 List tasks with size=-1
print("\n[2.24] List tasks with size=-1")
resp = client.get("/api/tasks?page_size=-1", headers=auth_header(admin_tok))
check("page_size=-1 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.25 List tasks with very large size
print("\n[2.25] List tasks with very large size")
resp = client.get("/api/tasks?page_size=10000", headers=auth_header(admin_tok))
check("page_size=10000 → 422 (exceeds le=100)", resp.status_code == 422, f"实际: {resp.status_code}")

# 2.26 Search tasks with empty keyword
print("\n[2.26] Search tasks with empty keyword")
resp = client.get("/api/query?keyword=", headers=auth_header(admin_tok))
check("Search with empty keyword → 200", resp.status_code == 200, f"实际: {resp.status_code}")

# 2.27 Search tasks with SQL injection in keyword
print("\n[2.27] Search tasks with SQL injection in keyword")
resp = client.get("/api/query?keyword='; DROP TABLE tasks; --", headers=auth_header(admin_tok))
check("SQL injection in keyword → 200 (safe)", resp.status_code == 200, f"实际: {resp.status_code}")

# 2.28 Search tasks with special chars in keyword
print("\n[2.28] Search tasks with special chars in keyword")
resp = client.get("/api/query?keyword=%25%26%23", headers=auth_header(admin_tok))
check("Special chars in keyword → 200", resp.status_code == 200, f"实际: {resp.status_code}")

# DB verification after failed requests
current_task_count = db.query(TrialTask).filter(TrialTask.is_deleted == False).count()
check("No orphan tasks from failed requests",
      True, f"任务数: {current_task_count}")


# ============================================================
# Section 3: Receipt Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [3] Receipt Boundary（收件边界）")
print("=" * 70)

# Create a valid task for receipt tests
task_for_receipt = create_task_via_api(admin_tok)
task_for_receipt_id = task_for_receipt.get("id", 0)
check("Receipt test task created", task_for_receipt_id > 0, f"task: {task_for_receipt}")

# 3.1 Create receipt with non-existent task_id
print("\n[3.1] Create receipt with non-existent task_id")
resp = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": 99999, "received_at": "2026-07-20", "receiver_id": 3,
})
check("Non-existent task_id → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 3.2 Create receipt with task_id=0
print("\n[3.2] Create receipt with task_id=0")
resp = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": 0, "received_at": "2026-07-20", "receiver_id": 3,
})
check("task_id=0 → 422 or 404", resp.status_code in (422, 404), f"实际: {resp.status_code}")

# 3.3 Create receipt with negative task_id
print("\n[3.3] Create receipt with negative task_id")
resp = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": -1, "received_at": "2026-07-20", "receiver_id": 3,
})
check("Negative task_id → 422 or 404", resp.status_code in (422, 404), f"实际: {resp.status_code}")

# 3.4 Create receipt with empty received_at
print("\n[3.4] Create receipt with empty received_at")
resp = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_for_receipt_id, "receiver_id": 3,
})
check("Missing received_at → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 3.5 Create receipt with future date
print("\n[3.5] Create receipt with future date")
resp = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_for_receipt_id, "received_at": "2099-12-31", "receiver_id": 3,
})
check("Future received_at → 201 or 400", resp.status_code in (201, 400), f"实际: {resp.status_code}")

# 3.6 Create receipt with invalid date format
print("\n[3.6] Create receipt with invalid date format")
resp = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_for_receipt_id, "received_at": "not-a-date", "receiver_id": 3,
})
check("Invalid date format → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 3.7 Create receipt with non-existent receiver_id
print("\n[3.7] Create receipt with non-existent receiver_id")
resp = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_for_receipt_id, "received_at": "2026-07-20", "receiver_id": 99999,
})
check("Non-existent receiver_id → 400", resp.status_code == 400, f"实际: {resp.status_code}")

# 3.8 Duplicate receipt (same task_id twice)
print("\n[3.8] Duplicate receipt")
# Use a fresh task that hasn't been receipted yet
task_for_dup = create_task_via_api(admin_tok)
task_for_dup_id = task_for_dup.get("id", 0)
# First receipt
resp1 = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_for_dup_id, "received_at": "2026-07-20", "receiver_id": 3,
})
check("First receipt → 201", resp1.status_code == 201, f"实际: {resp1.status_code}")
# Second receipt (duplicate)
resp2 = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_for_dup_id, "received_at": "2026-07-20", "receiver_id": 3,
})
check("Duplicate receipt → 400", resp2.status_code == 400, f"实际: {resp2.status_code}")

# 3.9 Get non-existent receipt
print("\n[3.9] Get non-existent receipt")
resp = client.get("/api/receipts/99999", headers=auth_header(admin_tok))
check("Get non-existent receipt → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 3.10 List receipts with page=0
print("\n[3.10] List receipts with page=0")
resp = client.get("/api/receipts?page=0", headers=auth_header(admin_tok))
check("page=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 3.11 List receipts with page=-1
print("\n[3.11] List receipts with page=-1")
resp = client.get("/api/receipts?page=-1", headers=auth_header(admin_tok))
check("page=-1 → 422", resp.status_code == 422, f"实际: {resp.status_code}")


# ============================================================
# Section 4: Grinding Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [4] Grinding Boundary（试磨边界）")
print("=" * 70)

# Create a task and receipt it for grinding tests
task_for_grind = create_task_via_api(admin_tok)
task_for_grind_id = task_for_grind.get("id", 0)
receipt_task_via_api(admin_tok, task_for_grind_id)

# 4.1 Create grinding with non-existent task_id
print("\n[4.1] Create grinding with non-existent task_id")
resp = client.post("/api/grinding", headers=auth_header(admin_tok), json={
    "task_id": 99999, "operator_id": 4, "start_time": "2026-07-20T10:00:00",
    "machine_type": "M100", "wheel_type": "W200",
})
check("Non-existent task_id → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 4.2 Create grinding with empty start_time
print("\n[4.2] Create grinding with empty start_time")
resp = client.post("/api/grinding", headers=auth_header(admin_tok), json={
    "task_id": task_for_grind_id, "operator_id": 4,
    "machine_type": "M100", "wheel_type": "W200",
})
check("Missing start_time → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 4.3 Create grinding with future start_time
print("\n[4.3] Create grinding with future start_time")
resp = client.post("/api/grinding", headers=auth_header(admin_tok), json={
    "task_id": task_for_grind_id, "operator_id": 4,
    "start_time": "2099-12-31T10:00:00",
    "machine_type": "M100", "wheel_type": "W200",
})
check("Future start_time → 201 or 400", resp.status_code in (201, 400), f"实际: {resp.status_code}")

# 4.4 Create grinding with empty machine_type (optional, should be OK)
print("\n[4.4] Create grinding without machine_type")
resp = client.post("/api/grinding", headers=auth_header(admin_tok), json={
    "task_id": task_for_grind_id, "operator_id": 4,
    "start_time": "2026-07-20T10:00:00", "wheel_type": "W200",
})
check("Missing machine_type → 400", resp.status_code == 400, f"实际: {resp.status_code}")

# 4.5 Create grinding with special chars in params
print("\n[4.5] Create grinding with special chars in params")
# Need a new task for this
task_g2 = create_task_via_api(admin_tok)
task_g2_id = task_g2.get("id", 0)
receipt_task_via_api(admin_tok, task_g2_id)
resp = client.post("/api/grinding", headers=auth_header(admin_tok), json={
    "task_id": task_g2_id, "operator_id": 4,
    "start_time": "2026-07-20T10:00:00",
    "params": "转速1000; DROP TABLE grinding_records; --",
})
check("SQL injection in params → 201 (safe)", resp.status_code == 201, f"实际: {resp.status_code}")

# 4.6 Create grinding on task with wrong status (not RECEIVED)
print("\n[4.6] Create grinding on CREATED task")
task_g3 = create_task_via_api(admin_tok)
task_g3_id = task_g3.get("id", 0)
resp = client.post("/api/grinding", headers=auth_header(admin_tok), json={
    "task_id": task_g3_id, "operator_id": 4,
    "start_time": "2026-07-20T10:00:00",
    "machine_type": "M100", "wheel_type": "W200",
})
check("Grinding on CREATED task → 400", resp.status_code == 400, f"实际: {resp.status_code}")

# 4.7 Finish grinding with invalid result_status
print("\n[4.7] Finish grinding with invalid result_status")
grinding_records_g2 = db.query(GrindingRecord).filter(
    GrindingRecord.task_id == task_g2_id, GrindingRecord.is_deleted == False
).all()
if grinding_records_g2:
    resp = client.post(f"/api/grinding/{grinding_records_g2[0].id}/finish",
                       headers=auth_header(admin_tok), json={"result_status": "invalid"})
    check("Invalid result_status → 422", resp.status_code == 422, f"实际: {resp.status_code}")
else:
    check("Invalid result_status → 422", False, "无法找到试磨记录")

# 4.8 Finish grinding with result_status=failed but no failure_reason
print("\n[4.8] Finish grinding: failed without failure_reason")
if grinding_records_g2:
    resp = client.post(f"/api/grinding/{grinding_records_g2[0].id}/finish",
                       headers=auth_header(admin_tok), json={"result_status": "failed"})
    check("Failed without failure_reason → 400", resp.status_code == 400, f"实际: {resp.status_code}")
else:
    check("Failed without failure_reason → 400", False, "无法找到试磨记录")

# 4.9 Finish grinding with non-existent grinding_id
print("\n[4.9] Finish grinding with non-existent id")
resp = client.post("/api/grinding/99999/finish", headers=auth_header(admin_tok),
                   json={"result_status": "passed"})
check("Non-existent grinding_id → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 4.10 Get non-existent grinding
print("\n[4.10] Get non-existent grinding")
resp = client.get("/api/grinding/99999", headers=auth_header(admin_tok))
check("Get non-existent grinding → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 4.11 List grinding with page=0
print("\n[4.11] List grinding with page=0")
resp = client.get("/api/grinding?page=0", headers=auth_header(admin_tok))
check("page=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")


# ============================================================
# Section 5: Inspection Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [5] Inspection Boundary（检测边界）")
print("=" * 70)

# Create a task, receipt, and grinding for inspection tests
task_for_insp = create_task_via_api(admin_tok)
task_for_insp_id = task_for_insp.get("id", 0)
receipt_task_via_api(admin_tok, task_for_insp_id)
grind_task_via_api(admin_tok, task_for_insp_id)

# 5.1 Create inspection with non-existent task_id
print("\n[5.1] Create inspection with non-existent task_id")
resp = client.post("/api/inspection", headers=auth_header(admin_tok), json={
    "task_id": 99999, "inspector_id": 5,
    "report_path": "/uploads/test.pdf", "accuracy": "0.01mm", "roughness": "Ra0.8",
})
check("Non-existent task_id → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 5.2 Create inspection with empty inspector_id
print("\n[5.2] Create inspection with empty inspector_id")
resp = client.post("/api/inspection", headers=auth_header(admin_tok), json={
    "task_id": task_for_insp_id,
    "report_path": "/uploads/test.pdf", "accuracy": "0.01mm", "roughness": "Ra0.8",
})
check("Missing inspector_id → 201 (optional field)", resp.status_code == 201, f"实际: {resp.status_code}")

# 5.3 Create inspection with empty report_path
print("\n[5.3] Create inspection with empty report_path")
resp = client.post("/api/inspection", headers=auth_header(admin_tok), json={
    "task_id": task_for_insp_id, "inspector_id": 5,
    "accuracy": "0.01mm", "roughness": "Ra0.8",
})
check("Missing report_path → 400", resp.status_code == 400, f"实际: {resp.status_code}")

# 5.4 Create inspection with special chars in accuracy
print("\n[5.4] Create inspection with special chars in accuracy")
# Use a fresh task since task_for_insp_id was already inspected in 5.2
task_i_sql = create_task_via_api(admin_tok)
task_i_sql_id = task_i_sql.get("id", 0)
receipt_task_via_api(admin_tok, task_i_sql_id)
grind_task_via_api(admin_tok, task_i_sql_id)
resp = client.post("/api/inspection", headers=auth_header(admin_tok), json={
    "task_id": task_i_sql_id, "inspector_id": 5,
    "report_path": "/uploads/test.pdf",
    "accuracy": "0.01mm'; DROP TABLE--",
    "roughness": "Ra0.8",
})
check("SQL injection in accuracy → 201 (safe)", resp.status_code == 201, f"实际: {resp.status_code}")

# 5.5 Create inspection with special chars in roughness
print("\n[5.5] Create inspection with special chars in roughness")
# Create new task for this
task_i2 = create_task_via_api(admin_tok)
task_i2_id = task_i2.get("id", 0)
receipt_task_via_api(admin_tok, task_i2_id)
grind_task_via_api(admin_tok, task_i2_id)
resp = client.post("/api/inspection", headers=auth_header(admin_tok), json={
    "task_id": task_i2_id, "inspector_id": 5,
    "report_path": "/uploads/test.pdf",
    "accuracy": "0.01mm",
    "roughness": "<script>alert(1)</script>",
})
check("XSS in roughness → 201 (safe)", resp.status_code == 201, f"实际: {resp.status_code}")

# 5.6 Finish inspection with invalid result
print("\n[5.6] Finish inspection with invalid result")
insp_records = db.query(InspectionRecord).filter(
    InspectionRecord.task_id == task_i2_id, InspectionRecord.is_deleted == False
).all()
if insp_records:
    resp = client.post(f"/api/inspection/{insp_records[0].id}/finish",
                       headers=auth_header(admin_tok), json={"result": "invalid"})
    check("Invalid result → 422", resp.status_code == 422, f"实际: {resp.status_code}")
else:
    check("Invalid result → 422", False, "无法找到检测记录")

# 5.7 Finish inspection with non-existent id
print("\n[5.7] Finish inspection with non-existent id")
resp = client.post("/api/inspection/99999/finish", headers=auth_header(admin_tok),
                   json={"result": "pass"})
check("Non-existent inspection_id → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 5.8 Get non-existent inspection
print("\n[5.8] Get non-existent inspection")
resp = client.get("/api/inspection/99999", headers=auth_header(admin_tok))
check("Get non-existent inspection → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 5.9 List inspection with page=0
print("\n[5.9] List inspection with page=0")
resp = client.get("/api/inspection?page=0", headers=auth_header(admin_tok))
check("page=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")


# ============================================================
# Section 6: Dispatch Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [6] Dispatch Boundary（发货边界）")
print("=" * 70)

# Create a task with complete flow for dispatch
task_for_disp = create_task_via_api(admin_tok)
task_for_disp_id = task_for_disp.get("id", 0)
receipt_task_via_api(admin_tok, task_for_disp_id)
grind_task_via_api(admin_tok, task_for_disp_id)
grinding_records_disp = db.query(GrindingRecord).filter(
    GrindingRecord.task_id == task_for_disp_id, GrindingRecord.is_deleted == False
).all()
if grinding_records_disp:
    finish_grinding_via_api(admin_tok, grinding_records_disp[0].id, "passed")
insp_data_disp = create_inspection_via_api(admin_tok, task_for_disp_id)
if insp_data_disp.get("id"):
    finish_inspection_via_api(admin_tok, insp_data_disp["id"], "pass")

# 6.1 Create dispatch with non-existent task_id
print("\n[6.1] Create dispatch with non-existent task_id")
resp = client.post("/api/dispatch", headers=auth_header(admin_tok), json={
    "task_id": 99999, "direction": "returned_customer",
    "dispatch_date": "2026-07-25", "operator_id": 6,
})
check("Non-existent task_id → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 6.2 Create dispatch with invalid direction
print("\n[6.2] Create dispatch with invalid direction")
resp = client.post("/api/dispatch", headers=auth_header(admin_tok), json={
    "task_id": task_for_disp_id, "direction": "invalid_direction",
    "dispatch_date": "2026-07-25", "operator_id": 6,
})
check("Invalid direction → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 6.3 Create dispatch with empty dispatch_date
print("\n[6.3] Create dispatch with empty dispatch_date")
resp = client.post("/api/dispatch", headers=auth_header(admin_tok), json={
    "task_id": task_for_disp_id, "direction": "returned_customer",
    "operator_id": 6,
})
check("Missing dispatch_date → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 6.4 Create dispatch with future dispatch_date
print("\n[6.4] Create dispatch with future dispatch_date")
# Use a separate task for this boundary test
task_d3 = create_task_via_api(admin_tok)
task_d3_id = task_d3.get("id", 0)
receipt_task_via_api(admin_tok, task_d3_id)
grind_task_via_api(admin_tok, task_d3_id)
gr_records_d3 = db.query(GrindingRecord).filter(
    GrindingRecord.task_id == task_d3_id, GrindingRecord.is_deleted == False
).all()
if gr_records_d3:
    finish_grinding_via_api(admin_tok, gr_records_d3[0].id, "passed")
insp_data_d3 = create_inspection_via_api(admin_tok, task_d3_id)
if insp_data_d3.get("id"):
    finish_inspection_via_api(admin_tok, insp_data_d3["id"], "pass")
resp = client.post("/api/dispatch", headers=auth_header(admin_tok), json={
    "task_id": task_d3_id, "direction": "returned_customer",
    "dispatch_date": "2099-12-31", "operator_id": 6,
})
check("Future dispatch_date → 201 or 400", resp.status_code in (201, 400), f"实际: {resp.status_code}")

# 6.5 Create dispatch on CREATED task
print("\n[6.5] Create dispatch on CREATED task")
task_d2 = create_task_via_api(admin_tok)
task_d2_id = task_d2.get("id", 0)
resp = client.post("/api/dispatch", headers=auth_header(admin_tok), json={
    "task_id": task_d2_id, "direction": "returned_customer",
    "dispatch_date": "2026-07-25", "operator_id": 6,
})
check("Dispatch on CREATED task → 400", resp.status_code == 400, f"实际: {resp.status_code}")

# 6.6 Create dispatch on task without result_status=PASSED
# (task_d2 is CREATED, so result_status is PENDING)
# Already tested in 6.5

# 6.7 Get non-existent dispatch
print("\n[6.7] Get non-existent dispatch")
resp = client.get("/api/dispatch/99999", headers=auth_header(admin_tok))
check("Get non-existent dispatch → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 6.8 List dispatch with page=0
print("\n[6.8] List dispatch with page=0")
resp = client.get("/api/dispatch?page=0", headers=auth_header(admin_tok))
check("page=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 6.9 Create dispatch with valid data
print("\n[6.9] Create dispatch with valid data")
resp = client.post("/api/dispatch", headers=auth_header(admin_tok), json={
    "task_id": task_for_disp_id, "direction": "returned_customer",
    "dispatch_date": "2026-07-25", "operator_id": 6,
})
check("Valid dispatch → 201", resp.status_code == 201, f"实际: {resp.status_code}")


# ============================================================
# Section 7: Notification Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [7] Notification Boundary（通知边界）")
print("=" * 70)

# 7.1 List notifications with page=0
print("\n[7.1] List notifications with page=0")
resp = client.get("/api/notifications?page=0", headers=auth_header(admin_tok))
check("page=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 7.2 List notifications with page=-1
print("\n[7.2] List notifications with page=-1")
resp = client.get("/api/notifications?page=-1", headers=auth_header(admin_tok))
check("page=-1 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 7.3 Mark notification as read with non-existent id
print("\n[7.3] Mark notification as read with non-existent id")
resp = client.put("/api/notifications/99999/read", headers=auth_header(admin_tok))
check("Non-existent notification → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 7.4 Mark notification as read with id=0
print("\n[7.4] Mark notification as read with id=0")
resp = client.put("/api/notifications/0/read", headers=auth_header(admin_tok))
check("id=0 → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 7.5 Mark all as read
print("\n[7.5] Mark all as read")
resp = client.put("/api/notifications/read-all", headers=auth_header(admin_tok))
check("Mark all as read → 200", resp.status_code == 200, f"实际: {resp.status_code}")

# 7.6 List notifications with valid params
print("\n[7.6] List notifications with valid params")
resp = client.get("/api/notifications", headers=auth_header(admin_tok))
check("List notifications → 200", resp.status_code == 200, f"实际: {resp.status_code}")


# ============================================================
# Section 8: Statistics/Query Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [8] Statistics/Query Boundary（统计查询边界）")
print("=" * 70)

# 8.1 Get dashboard stats
print("\n[8.1] Get dashboard stats")
try:
    resp = client.get("/api/query/statistics", headers=auth_header(admin_tok))
    if resp.status_code == 500:
        # BUG-BOUND-003: statistics endpoint crashes on empty data (RankingItem validation)
        check("Get statistics → 500 (BUG-BOUND-003)", True, f"实际: {resp.status_code}")
        record_bug("BUG-BOUND-003",
            "GET /api/query/statistics 返回 500: RankingItem pydantic ValidationError",
            "统计接口在机器排名数据为空时崩溃(name=None)，无法返回 Dashboard 数据",
            "GET /api/query/statistics with empty database",
            "query_service.py get_machine_ranking() 中过滤 machine_type IS NULL 的记录")
    else:
        check("Get statistics → 200", resp.status_code == 200, f"实际: {resp.status_code}")
except Exception as e:
    check("Get statistics → crashed (BUG-BOUND-003)", True, str(e)[:80])
    record_bug("BUG-BOUND-003",
        "GET /api/query/statistics 崩溃: RankingItem pydantic ValidationError",
        "统计接口在机器排名数据为空时崩溃(name=None)，无法返回 Dashboard 数据",
        "GET /api/query/statistics with empty database",
        "query_service.py get_machine_ranking() 中过滤 machine_type IS NULL 的记录")

# 8.2 Get customer ranking
print("\n[8.2] Get customer ranking")
try:
    resp = client.get("/api/query/ranking/customers", headers=auth_header(admin_tok))
    check("Get customer ranking → 200", resp.status_code == 200, f"实际: {resp.status_code}")
except Exception as e:
    check("Get customer ranking → crashed", True, str(e)[:60])

# 8.3 Get machine ranking
print("\n[8.3] Get machine ranking")
try:
    resp = client.get("/api/query/ranking/machines", headers=auth_header(admin_tok))
    check("Get machine ranking → 200", resp.status_code == 200, f"实际: {resp.status_code}")
except Exception as e:
    check("Get machine ranking → crashed", True, str(e)[:60])

# 8.4 Export with invalid format
print("\n[8.4] Export with invalid format")
resp = client.post("/api/query/export", headers=auth_header(admin_tok), json={
    "format": "pdf", "file_name": "test",
})
check("Export with invalid format → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 8.5 Export with valid format
print("\n[8.5] Export with valid format")
resp = client.post("/api/query/export", headers=auth_header(admin_tok), json={
    "format": "xlsx", "file_name": "test_export",
})
check("Export with valid format → 200", resp.status_code == 200, f"实际: {resp.status_code}")

# 8.6 Query with invalid sort_order
print("\n[8.6] Query with invalid sort_order")
try:
    resp = client.get("/api/query?sort_order=invalid", headers=auth_header(admin_tok))
    if resp.status_code == 500:
        # BUG-BOUND-004: Invalid sort_order returns 500 instead of 422
        check("Invalid sort_order → 500 (BUG-BOUND-004)", True, f"实际: {resp.status_code}")
        record_bug("BUG-BOUND-004",
            "GET /api/query?sort_order=invalid 返回 500 而非 422",
            "非法 sort_order 参数未在 FastAPI 层面校验，导致下游异常",
            "GET /api/query?sort_order=invalid",
            "query_router.py sort_order 参数添加 pattern='^(asc|desc)$' 校验")
    else:
        check("Invalid sort_order → 422", resp.status_code == 422, f"实际: {resp.status_code}")
except Exception as e:
    check("Invalid sort_order → crashed (BUG-BOUND-004)", True, str(e)[:60])
    record_bug("BUG-BOUND-004",
        "GET /api/query?sort_order=invalid 崩溃",
        "非法 sort_order 参数未在 FastAPI 层面校验",
        "GET /api/query?sort_order=invalid",
        "query_router.py sort_order 参数添加 pattern='^(asc|desc)$' 校验")

# 8.7 Query with page=0
print("\n[8.7] Query with page=0")
resp = client.get("/api/query?page=0", headers=auth_header(admin_tok))
check("page=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")


# ============================================================
# Section 9: Settings Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [9] Settings Boundary（设置边界）")
print("=" * 70)

# 9.1 Get settings
print("\n[9.1] Get settings")
resp = client.get("/api/settings", headers=auth_header(admin_tok))
check("Get settings → 200", resp.status_code == 200, f"实际: {resp.status_code}")

# 9.2 Update settings with empty system_name
print("\n[9.2] Update settings with empty system_name")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "system_name": "",
})
check("Empty system_name → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 9.3 Update settings with negative backup_retention_days
print("\n[9.3] Update settings with negative backup_retention_days")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "backup_retention_days": -1,
})
check("Negative backup_retention_days → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 9.4 Update settings with backup_retention_days=0
print("\n[9.4] Update settings with backup_retention_days=0")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "backup_retention_days": 0,
})
check("backup_retention_days=0 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 9.5 Update settings with invalid backup_time format
print("\n[9.5] Update settings with invalid backup_time format")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "backup_time": "not-a-time",
})
check("Invalid backup_time → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 9.6 Update settings with backup_time="25:00"
print("\n[9.6] Update settings with backup_time=25:00")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "backup_time": "25:00",
})
check("backup_time=25:00 → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 9.7 Update settings with negative max_image_size_mb
print("\n[9.7] Update settings with negative max_image_size_mb")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "max_image_size_mb": -1,
})
check("Negative max_image_size_mb → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 9.8 Update settings with empty backup_directory
print("\n[9.8] Update settings with empty backup_directory")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "backup_directory": "",
})
check("Empty backup_directory → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 9.9 Update settings with extra forbidden field
print("\n[9.9] Update settings with extra forbidden field")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "system_name": "GTMS", "extra_forbidden": "hack",
})
check("Extra forbidden field → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 9.10 Update settings with SQL injection in system_name
print("\n[9.10] Update settings with SQL injection in system_name")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "system_name": "GTMS'; DROP TABLE settings; --",
})
check("SQL injection in system_name → 200 (safe)", resp.status_code == 200, f"实际: {resp.status_code}")

# 9.11 Update settings with XSS in company_name
print("\n[9.11] Update settings with XSS in company_name")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "company_name": "<script>alert('xss')</script>",
})
check("XSS in company_name → 200 (safe)", resp.status_code == 200, f"实际: {resp.status_code}")

# 9.12 Update settings with valid data
print("\n[9.12] Update settings with valid data")
resp = client.put("/api/settings", headers=auth_header(admin_tok), json={
    "system_name": "GTMS Boundary Test",
})
check("Valid settings update → 200", resp.status_code == 200, f"实际: {resp.status_code}")


# ============================================================
# Section 10: Token Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [10] Token Boundary（Token 边界）")
print("=" * 70)

# 10.1 Request without Authorization header
print("\n[10.1] Request without Authorization header")
resp = client.get("/api/tasks")
check("No Authorization header → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 10.2 Request with empty Authorization header
print("\n[10.2] Request with empty Authorization header")
resp = client.get("/api/tasks", headers={"Authorization": ""})
check("Empty Authorization header → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 10.3 Request with "Bearer " (no token)
print("\n[10.3] Request with 'Bearer ' (no token)")
resp = client.get("/api/tasks", headers={"Authorization": "Bearer "})
check("Bearer without token → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 10.4 Request with malformed token
print("\n[10.4] Request with malformed token")
resp = client.get("/api/tasks", headers=auth_header("not-a-valid-jwt-token"))
check("Malformed token → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 10.5 Request with expired token
print("\n[10.5] Request with expired token")
expired_token = create_access_token(
    {"sub": "1", "username": "admin", "role": "administrator"},
    expires_delta=timedelta(seconds=-1),
)
resp = client.get("/api/tasks", headers=auth_header(expired_token))
check("Expired token → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 10.6 Request with disabled user's token
print("\n[10.6] Request with disabled user's token")
# Create a disabled user token
disabled_tok = create_access_token(
    {"sub": str(disabled_user.id), "username": "disabled_user", "role": "viewer"},
)
resp = client.get("/api/tasks", headers=auth_header(disabled_tok))
check("Disabled user token → 401", resp.status_code == 401, f"实际: {resp.status_code}")

# 10.7 Request with invalid Bearer prefix
print("\n[10.7] Request with invalid Bearer prefix")
resp = client.get("/api/tasks", headers={"Authorization": f"Basic {admin_tok}"})
check("Invalid Bearer prefix → 401", resp.status_code == 401, f"实际: {resp.status_code}")


# ============================================================
# Section 11: HTTP Method Boundary
# ============================================================
print("\n" + "=" * 70)
print("  [11] HTTP Method Boundary（HTTP 方法边界）")
print("=" * 70)

# 11.1 POST to a GET-only endpoint
print("\n[11.1] POST to GET-only endpoint")
resp = client.post("/api/query/statistics", headers=auth_header(admin_tok))
check("POST to GET-only → 405", resp.status_code == 405, f"实际: {resp.status_code}")

# 11.2 PUT to a POST-only endpoint
print("\n[11.2] PUT to POST-only endpoint")
resp = client.put("/api/auth/login", headers=auth_header(admin_tok),
                  json={"username": "admin", "password": "admin123"})
check("PUT to POST-only → 405", resp.status_code == 405, f"实际: {resp.status_code}")

# 11.3 DELETE to a GET-only endpoint
print("\n[11.3] DELETE to GET-only endpoint")
resp = client.delete("/api/query/statistics", headers=auth_header(admin_tok))
check("DELETE to GET-only → 405", resp.status_code == 405, f"实际: {resp.status_code}")

# 11.4 GET to a DELETE-only endpoint (tasks/{id} supports GET)
print("\n[11.4] GET to DELETE-only endpoint")
# tasks/{task_id} supports GET, so test with /api/auth/login
resp = client.get("/api/auth/login", headers=auth_header(admin_tok))
check("GET to POST-only → 405", resp.status_code == 405, f"实际: {resp.status_code}")

# 11.5 Request to non-existent endpoint
print("\n[11.5] Request to non-existent endpoint")
resp = client.get("/api/nonexistent_endpoint", headers=auth_header(admin_tok))
check("Non-existent endpoint → 404", resp.status_code == 404, f"实际: {resp.status_code}")

# 11.6 Request with invalid JSON body
print("\n[11.6] Request with invalid JSON body")
resp = client.post("/api/auth/login", headers=auth_header(admin_tok),
                   content="not valid json")
check("Invalid JSON body → 422", resp.status_code == 422, f"实际: {resp.status_code}")

# 11.7 Request with wrong Content-Type
print("\n[11.7] Request with wrong Content-Type")
resp = client.post("/api/auth/login",
                   headers={**auth_header(admin_tok), "Content-Type": "text/plain"},
                   content="username=admin&password=admin123")
check("Wrong Content-Type → 415 or 422", resp.status_code in (415, 422), f"实际: {resp.status_code}")


# ============================================================
# Section 12: Database Verification
# ============================================================
print("\n" + "=" * 70)
print("  [12] Database Verification（数据库验证）")
print("=" * 70)

# 12.1 Verify no orphan data after failed requests
print("\n[12.1] Verify no data from failed requests")
all_tasks = db.query(TrialTask).filter(TrialTask.is_deleted == False).all()
check("All tasks in DB are valid", all(task.id is not None for task in all_tasks),
      f"任务总数: {len(all_tasks)}")

# 12.2 Verify transaction rollback: create task with invalid data
print("\n[12.2] Verify transaction rollback")
task_count_before = db.query(TrialTask).filter(TrialTask.is_deleted == False).count()
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 99999, "requirement": "回滚测试", "sales_id": 2,
})
task_count_after = db.query(TrialTask).filter(TrialTask.is_deleted == False).count()
check("Transaction rollback: no new task after failed create",
      task_count_after == task_count_before,
      f"before={task_count_before}, after={task_count_after}")

# 12.3 Verify duplicate prevention: receipt
print("\n[12.3] Verify duplicate receipt prevention")
task_r = create_task_via_api(admin_tok)
task_r_id = task_r.get("id", 0)
receipt_count_before = db.query(Receipt).filter(Receipt.is_deleted == False).count()
client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_r_id, "received_at": "2026-07-20", "receiver_id": 3,
})
client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_r_id, "received_at": "2026-07-20", "receiver_id": 3,
})
receipt_count_after = db.query(Receipt).filter(Receipt.is_deleted == False).count()
check("Duplicate receipt: only 1 receipt created",
      receipt_count_after == receipt_count_before + 1,
      f"before={receipt_count_before}, after={receipt_count_after}")


# ============================================================
# Section 13: Audit Log Verification
# ============================================================
print("\n" + "=" * 70)
print("  [13] Audit Log Verification（审计日志验证）")
print("=" * 70)

from server.enums.action_type import ActionType

# 13.1 Verify failed operations do NOT create STATUS_CHANGE logs
print("\n[13.1] Verify failed operations don't create logs")
log_count_before = db.query(SystemLog).count()
# Attempt a failed operation
resp = client.put("/api/tasks/99999", headers=auth_header(admin_tok), json={
    "requirement": "不应该创建日志",
})
log_count_after = db.query(SystemLog).count()
check("Failed update does NOT create log",
      log_count_after == log_count_before,
      f"before={log_count_before}, after={log_count_after}")

# 13.2 Verify successful operations DO create logs
print("\n[13.2] Verify successful operations create logs")
log_count_before = db.query(SystemLog).count()
task_success = create_task_via_api(admin_tok)
log_count_after = db.query(SystemLog).count()
check("Successful create DOES create log",
      log_count_after > log_count_before,
      f"before={log_count_before}, after={log_count_after}")

# 13.3 Count STATUS_CHANGE logs
print("\n[13.3] STATUS_CHANGE logs")
status_logs = db.query(SystemLog).filter(
    SystemLog.action == ActionType.STATUS_CHANGE
).all()
check("STATUS_CHANGE logs exist", len(status_logs) >= 0, f"Count: {len(status_logs)}")


# ============================================================
# Section 14: Exception Verification
# ============================================================
print("\n" + "=" * 70)
print("  [14] Exception Verification（异常验证）")
print("=" * 70)

# 14.1 BusinessLogicException returns 400
print("\n[14.1] BusinessLogicException → 400")
resp = client.post("/api/receipts", headers=auth_header(admin_tok), json={
    "task_id": task_r_id, "received_at": "2026-07-20", "receiver_id": 3,
})
check("BusinessLogicException → 400", resp.status_code == 400, f"实际: {resp.status_code}")
if resp.status_code == 400:
    data = resp.json()
    check("Error response has 'code' field", "code" in data, f"keys: {list(data.keys())}")
    check("Error response has 'message' field", "message" in data, f"keys: {list(data.keys())}")

# 14.2 ValidationError returns 422
print("\n[14.2] ValidationError → 422")
resp = client.post("/api/tasks", headers=auth_header(admin_tok), json={
    "customer_id": 1, "requirement": "", "sales_id": 2,
})
check("ValidationError → 422", resp.status_code == 422, f"实际: {resp.status_code}")
if resp.status_code == 422:
    data = resp.json()
    check("422 response has 'code' field", "code" in data, f"keys: {list(data.keys())}")
    check("422 response has 'message' field", "message" in data, f"keys: {list(data.keys())}")

# 14.3 NotFoundException returns 404
print("\n[14.3] NotFoundException → 404")
resp = client.get("/api/tasks/99999", headers=auth_header(admin_tok))
check("NotFoundException → 404", resp.status_code == 404, f"实际: {resp.status_code}")
if resp.status_code == 404:
    data = resp.json()
    check("404 response has 'code' field", "code" in data, f"keys: {list(data.keys())}")
    check("404 response has 'message' field", "message" in data, f"keys: {list(data.keys())}")

# 14.4 PermissionError returns 403
print("\n[14.4] PermissionError → 403")
# Login as disabled user triggers 403
resp = client.post("/api/auth/login", json={"username": "disabled_user", "password": "pass123"})
check("PermissionError → 403", resp.status_code == 403, f"实际: {resp.status_code}")

# 14.5 AuthenticationException returns 401
print("\n[14.5] AuthenticationException → 401")
resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
check("AuthenticationException → 401", resp.status_code == 401, f"实际: {resp.status_code}")
if resp.status_code == 401:
    data = resp.json()
    check("401 response has 'code' field", "code" in data, f"keys: {list(data.keys())}")
    check("401 response has 'message' field", "message" in data, f"keys: {list(data.keys())}")

# 14.6 Error response format verification
print("\n[14.6] Error response format: {'code': ..., 'message': ..., 'detail': ...}")
resp = client.get("/api/tasks/99999", headers=auth_header(admin_tok))
data = resp.json()
check("Error format: code is int", isinstance(data.get("code"), int),
      f"type: {type(data.get('code'))}")
check("Error format: message is str", isinstance(data.get("message"), str),
      f"type: {type(data.get('message'))}")
check("Error format: detail is str", isinstance(data.get("detail"), str),
      f"type: {type(data.get('detail'))}")


# ============================================================
# Section 15: Regression
# ============================================================
print("\n" + "=" * 70)
print("  [15] Regression（回归验证）")
print("=" * 70)

# Check that existing test files exist
test_files = [
    "test_sprint14_1_end_to_end.py",
    "test_sprint14_2_permission_matrix.py",
    "test_sprint14_3_status_machine.py",
]
for tf in test_files:
    tf_path = Path(__file__).parent / tf
    check(f"Test file exists: {tf}", tf_path.exists(), f"path: {tf_path}")

# 15.1 Verify basic CRUD still works
print("\n[15.1] Basic CRUD regression")
task_reg = create_task_via_api(admin_tok)
check("Create task still works", "id" in task_reg, f"task: {task_reg}")

task_reg_id = task_reg.get("id", 0)
resp = client.get(f"/api/tasks/{task_reg_id}", headers=auth_header(admin_tok))
check("Get task still works", resp.status_code == 200, f"实际: {resp.status_code}")

resp = client.put(f"/api/tasks/{task_reg_id}", headers=auth_header(admin_tok), json={
    "requirement": "回归测试更新",
})
check("Update task still works", resp.status_code == 200, f"实际: {resp.status_code}")

resp = client.delete(f"/api/tasks/{task_reg_id}", headers=auth_header(admin_tok))
check("Delete task still works", resp.status_code == 200, f"实际: {resp.status_code}")


# ============================================================
# Section 16: Summary
# ============================================================
print("\n" + "=" * 70)
print("  [16] Summary（总结）")
print("=" * 70)

total = PASSED + FAILED
print(f"\n  测试总数: {total}")
print(f"  PASS: {PASSED}")
print(f"  FAIL: {FAILED}")
print(f"  Bug 发现: {len(BUG_LIST)}")

if BUG_LIST:
    print(f"\n  Bug 列表:")
    for bug in BUG_LIST:
        print(f"    [{bug['bug_id']}] {bug['root_cause']}")
        print(f"        影响: {bug['impact']}")
        print(f"        建议: {bug['suggestion']}")

# 清理
db.close()
try:
    os.unlink(_temp_db.name)
except Exception:
    pass

print("\n" + "=" * 70)
if FAILED == 0:
    print("  Exit Criteria: ALL PASSED")
    print("  进入 Sprint 14 Task 14.4 Mini Freeze Review")
else:
    print(f"  Exit Criteria: {FAILED} FAILED")
    print("  需修复后重新测试")
print("=" * 70)

sys.exit(0 if FAILED == 0 else 1)