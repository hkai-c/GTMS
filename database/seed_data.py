"""数据库初始化种子数据 (Seed Data)

Sprint 1 — Task 1.14
参考：DB_DESIGN.md §8, CODE_WIKI.md

功能：
    - 创建默认角色（4 个）
    - 创建权限（20 个）
    - 创建管理员账号 + 3 个测试用户
    - 建立角色-权限关联
    - 建立用户-角色关联
    - 创建示例客户数据（3 个）
    - 支持幂等重复执行

使用方式:
    python database/seed_data.py
"""

import time
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, select, insert

from server.database.base import Base
from server.database.engine import engine
from server.database.session import SessionLocal
from server.models import (
    User, Role, Permission, Customer,
    user_roles, role_permissions,
)
from passlib.hash import bcrypt


# ============================================================
# 种子数据定义
# ============================================================

# 角色（DB_DESIGN.md §8.1）
# name: 唯一标识, display_name: 显示名
ROLES = [
    {"name": "administrator", "display_name": "管理员", "description": "系统管理员，拥有全部权限"},
    {"name": "manager", "display_name": "经理", "description": "部门经理，管理任务与报告"},
    {"name": "technician", "display_name": "技术员", "description": "技术员，负责试磨与检测"},
    {"name": "viewer", "display_name": "查看者", "description": "查看者，只读权限"},
]

# 权限（DB_DESIGN.md §8.2）
PERMISSIONS = [
    # 用户管理
    {"code": "user:read", "name": "查看用户", "module": "user"},
    {"code": "user:write", "name": "编辑用户", "module": "user"},
    {"code": "user:delete", "name": "删除用户", "module": "user"},
    # 角色管理
    {"code": "role:read", "name": "查看角色", "module": "role"},
    {"code": "role:write", "name": "编辑角色", "module": "role"},
    # 任务管理
    {"code": "task:read", "name": "查看任务", "module": "task"},
    {"code": "task:write", "name": "编辑任务", "module": "task"},
    {"code": "task:status_change", "name": "状态变更", "module": "task"},
    {"code": "task:delete", "name": "删除任务", "module": "task"},
    # 收件管理
    {"code": "receipt:read", "name": "查看收件", "module": "receipt"},
    {"code": "receipt:write", "name": "编辑收件", "module": "receipt"},
    # 试磨管理
    {"code": "grinding:read", "name": "查看试磨", "module": "grinding"},
    {"code": "grinding:write", "name": "编辑试磨", "module": "grinding"},
    # 检测管理
    {"code": "inspection:read", "name": "查看检测", "module": "inspection"},
    {"code": "inspection:write", "name": "编辑检测", "module": "inspection"},
    # 发货管理
    {"code": "dispatch:read", "name": "查看发货", "module": "dispatch"},
    {"code": "dispatch:write", "name": "编辑发货", "module": "dispatch"},
    # 报告
    {"code": "report:read", "name": "查看报告", "module": "report"},
    {"code": "report:export", "name": "导出报告", "module": "report"},
    # 系统管理
    {"code": "system:admin", "name": "系统管理", "module": "system"},
]

# 用户（DB_DESIGN.md §8.3）
USERS = [
    {"username": "admin", "password": "admin123", "real_name": "管理员", "role_name": "administrator"},
    {"username": "manager1", "password": "pass123", "real_name": "经理", "role_name": "manager"},
    {"username": "tech1", "password": "pass123", "real_name": "技术员", "role_name": "technician"},
    {"username": "viewer1", "password": "pass123", "real_name": "查看者", "role_name": "viewer"},
]

# 角色-权限映射（DB_DESIGN.md §8.1 角色权限分配）
ROLE_PERMISSION_MAP = {
    "administrator": "all",
    "manager": [
        "task:read", "task:write", "task:status_change", "task:delete",
        "receipt:read", "receipt:write",
        "grinding:read", "grinding:write",
        "inspection:read", "inspection:write",
        "dispatch:read", "dispatch:write",
        "report:read", "report:export",
    ],
    "technician": [
        "task:read",
        "grinding:read", "grinding:write",
        "inspection:read", "inspection:write",
        "report:read",
    ],
    "viewer": [
        "task:read",
        "receipt:read",
        "report:read",
    ],
}

# 客户（DB_DESIGN.md §8.5）
CUSTOMERS = [
    {"company_name": "三一重工", "contact": "张先生", "phone": "13800001001", "address": "湖南省长沙市"},
    {"company_name": "中联重科", "contact": "李女士", "phone": "13800001002", "address": "湖南省长沙市"},
    {"company_name": "徐工集团", "contact": "王先生", "phone": "13800001003", "address": "江苏省徐州市"},
]


# ============================================================
# 工具函数
# ============================================================

def hash_password(password: str) -> str:
    """使用 bcrypt 加密密码"""
    return bcrypt.hash(password)


# ============================================================
# 主函数
# ============================================================

def seed_data():
    """执行种子数据初始化"""
    start_time = time.time()
    stats = {
        "roles": {"created": 0, "skipped": 0},
        "permissions": {"created": 0, "skipped": 0},
        "users": {"created": 0, "skipped": 0},
        "customers": {"created": 0, "skipped": 0},
        "role_permissions": {"created": 0, "skipped": 0},
        "user_roles": {"created": 0, "skipped": 0},
    }

    print("=" * 60)
    print("  GTMS Seed Data 初始化")
    print("=" * 60)
    print()

    # 确保表已创建
    print("[1/7] 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"      已存在 {len(tables)} 张表")
    print()

    # 开始事务
    session = SessionLocal()
    try:
        # ---- 角色 ----
        print("[2/7] 初始化角色...")
        role_map = {}
        for role_data in ROLES:
            name = role_data["name"]
            existing = session.query(Role).filter_by(name=name).first()
            if existing:
                role_map[name] = existing
                stats["roles"]["skipped"] += 1
                print(f"      - 跳过角色: {existing.display_name} ({name})")
            else:
                role = Role(
                    name=name,
                    display_name=role_data["display_name"],
                    description=role_data["description"],
                    is_system=True,
                )
                session.add(role)
                session.flush()
                role_map[name] = role
                stats["roles"]["created"] += 1
                print(f"      + 创建角色: {role.display_name} ({name})")
        print()

        # ---- 权限 ----
        print("[3/7] 初始化权限...")
        perm_map = {}
        for perm_data in PERMISSIONS:
            code = perm_data["code"]
            existing = session.query(Permission).filter_by(code=code).first()
            if existing:
                perm_map[code] = existing
                stats["permissions"]["skipped"] += 1
            else:
                perm = Permission(
                    code=code,
                    name=perm_data["name"],
                    module=perm_data["module"],
                )
                session.add(perm)
                session.flush()
                perm_map[code] = perm
                stats["permissions"]["created"] += 1
                print(f"      + 创建权限: {perm.name} ({code})")
        print(f"      新增 {stats['permissions']['created']} 条, 跳过 {stats['permissions']['skipped']} 条")
        print()

        # ---- 角色-权限关联 ----
        print("[4/7] 建立角色-权限关联...")
        for role_name, perm_codes in ROLE_PERMISSION_MAP.items():
            role = role_map[role_name]
            if perm_codes == "all":
                perms = list(perm_map.values())
            else:
                perms = [perm_map[pc] for pc in perm_codes]

            # 获取已有关联
            existing_rows = session.execute(
                select(role_permissions.c.permission_id).where(
                    role_permissions.c.role_id == role.id
                )
            ).fetchall()
            existing_perm_ids = {row[0] for row in existing_rows}

            for perm in perms:
                if perm.id in existing_perm_ids:
                    stats["role_permissions"]["skipped"] += 1
                else:
                    session.execute(
                        insert(role_permissions).values(
                            role_id=role.id, permission_id=perm.id
                        )
                    )
                    stats["role_permissions"]["created"] += 1
        print(f"      新增 {stats['role_permissions']['created']} 条关联")
        print(f"      跳过 {stats['role_permissions']['skipped']} 条关联")
        print()

        # ---- 用户 ----
        print("[5/7] 初始化用户...")
        user_map = {}
        for user_data in USERS:
            username = user_data["username"]
            existing = session.query(User).filter_by(username=username).first()
            if existing:
                user_map[username] = existing
                stats["users"]["skipped"] += 1
                print(f"      - 跳过用户: {username}")
            else:
                user = User(
                    username=username,
                    password_hash=hash_password(user_data["password"]),
                    real_name=user_data["real_name"],
                    is_active=True,
                )
                session.add(user)
                session.flush()
                user_map[username] = user
                stats["users"]["created"] += 1
                print(f"      + 创建用户: {username} ({user.real_name})")
        print()

        # ---- 用户-角色关联 ----
        print("[6/7] 建立用户-角色关联...")
        for user_data in USERS:
            username = user_data["username"]
            role_name = user_data["role_name"]
            user = user_map[username]
            role = role_map[role_name]

            existing = session.execute(
                select(user_roles).where(
                    user_roles.c.user_id == user.id,
                    user_roles.c.role_id == role.id,
                )
            ).first()

            if existing:
                stats["user_roles"]["skipped"] += 1
                print(f"      - 跳过: {username} → {role.display_name}")
            else:
                session.execute(
                    insert(user_roles).values(
                        user_id=user.id, role_id=role.id
                    )
                )
                stats["user_roles"]["created"] += 1
                print(f"      + 绑定: {username} → {role.display_name}")
        print()

        # ---- 客户 ----
        print("[7/7] 初始化示例客户...")
        for cust_data in CUSTOMERS:
            company_name = cust_data["company_name"]
            existing = session.query(Customer).filter_by(company_name=company_name).first()
            if existing:
                stats["customers"]["skipped"] += 1
                print(f"      - 跳过客户: {company_name}")
            else:
                cust = Customer(
                    company_name=company_name,
                    contact=cust_data["contact"],
                    phone=cust_data["phone"],
                    address=cust_data["address"],
                )
                session.add(cust)
                stats["customers"]["created"] += 1
                print(f"      + 创建客户: {company_name}")
        print()

        session.commit()
        elapsed = time.time() - start_time

        # ============================================================
        # 结果输出
        # ============================================================
        print("=" * 60)
        print("  种子数据初始化完成")
        print("=" * 60)
        print(f"  角色:     +{stats['roles']['created']} / -{stats['roles']['skipped']}")
        print(f"  权限:     +{stats['permissions']['created']} / -{stats['permissions']['skipped']}")
        print(f"  用户:     +{stats['users']['created']} / -{stats['users']['skipped']}")
        print(f"  客户:     +{stats['customers']['created']} / -{stats['customers']['skipped']}")
        print(f"  角色-权限: +{stats['role_permissions']['created']} / -{stats['role_permissions']['skipped']}")
        print(f"  用户-角色: +{stats['user_roles']['created']} / -{stats['user_roles']['skipped']}")
        print(f"  总耗时:   {elapsed:.2f}s")
        print("=" * 60)

    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] 种子数据初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    seed_data()