"""Sprint 2 — Task 2.2 Security Module 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  hash_password — 非明文
    4.  verify_password(True)
    5.  verify_password(False)
    6.  hash 唯一性（相同密码不同 hash）
    7.  JWT 创建
    8.  JWT 解析
    9.  JWT Payload 字段完整性
    10. JWT 过期检测
    11. 非法 Token 检测
    12. 错误签名检测
    13. has_permission() 权限检查
    14. Role Mapping 角色映射
    15. is_admin()
    16. is_manager()
    17. is_technician()
    18. is_viewer()
    19. check_permission 抛出异常
    20. AuthenticationException 正确抛出
"""

import sys
import time
from pathlib import Path
from datetime import timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    ROLE_PERMISSION_MAP,
    has_permission,
    check_permission,
    is_admin,
    is_manager,
    is_technician,
    is_viewer,
)
from server.core.exceptions import (
    AuthenticationException,
    PermissionDeniedException,
    BusinessLogicException,
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
print("  Task 2.2 — Security Module Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "core" / "security.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] 导入检查")
check("hash_password", hash_password is not None)
check("verify_password", verify_password is not None)
check("create_access_token", create_access_token is not None)
check("decode_access_token", decode_access_token is not None)
check("ROLE_PERMISSION_MAP", ROLE_PERMISSION_MAP is not None)
check("has_permission", has_permission is not None)
check("check_permission", check_permission is not None)
check("is_admin", is_admin is not None)
check("is_manager", is_manager is not None)
check("is_technician", is_technician is not None)
check("is_viewer", is_viewer is not None)

# ============================================================
# 3. hash_password — 非明文
# ============================================================
print("\n[3] hash_password — 非明文检查")
hashed = hash_password("admin123")
check("返回非空字符串", isinstance(hashed, str) and len(hashed) > 0)
check("结果非明文", "admin123" not in hashed)
check("bcrypt 前缀 ($2b$)", hashed.startswith("$2"))

# ============================================================
# 4. verify_password(True)
# ============================================================
print("\n[4] verify_password(True)")
check("正确密码验证通过", verify_password("admin123", hashed))

# ============================================================
# 5. verify_password(False)
# ============================================================
print("\n[5] verify_password(False)")
check("错误密码验证失败", not verify_password("wrongpassword", hashed))
check("空密码验证失败", not verify_password("", hashed))
check("空 hash 验证失败", not verify_password("admin123", ""))

# ============================================================
# 6. hash 唯一性
# ============================================================
print("\n[6] hash 唯一性（相同密码不同 salt）")
hashed2 = hash_password("admin123")
check("两次 hash 不同", hashed != hashed2)
check("两个 hash 都能验证原密码", verify_password("admin123", hashed) and verify_password("admin123", hashed2))

# ============================================================
# 7. JWT 创建
# ============================================================
print("\n[7] JWT 创建")
payload_data = {"sub": "1", "username": "admin", "role": "administrator"}
token = create_access_token(payload_data)
check("Token 非空字符串", isinstance(token, str) and len(token) > 0)
check("Token 为三段式 (header.payload.signature)", len(token.split(".")) == 3)

# ============================================================
# 8. JWT 解析
# ============================================================
print("\n[8] JWT 解析")
payload = decode_access_token(token)
check("解析成功", payload is not None)

# ============================================================
# 9. JWT Payload 字段完整性
# ============================================================
print("\n[9] JWT Payload 字段完整性")
check("sub", payload.get("sub") == "1")
check("username", payload.get("username") == "admin")
check("role", payload.get("role") == "administrator")
check("iat 存在", "iat" in payload)
check("exp 存在", "exp" in payload)
check("exp > iat", payload["exp"] > payload["iat"])

# ============================================================
# 10. JWT 过期检测
# ============================================================
print("\n[10] JWT 过期检测")
expired_token = create_access_token(payload_data, expires_delta=timedelta(seconds=-1))
try:
    decode_access_token(expired_token)
    check("过期 Token 应被拒绝", False)
except AuthenticationException as e:
    check("过期 Token 抛出 AuthenticationException", "过期" in e.message or "expired" in e.message.lower())

# ============================================================
# 11. 非法 Token 检测
# ============================================================
print("\n[11] 非法 Token 检测")
try:
    decode_access_token("not.a.valid.jwt.token.string")
    check("非法 Token 应被拒绝", False)
except AuthenticationException:
    check("非法 Token 抛出 AuthenticationException", True)

try:
    decode_access_token("")
    check("空 Token 应被拒绝", False)
except AuthenticationException:
    check("空 Token 抛出 AuthenticationException", True)

# ============================================================
# 12. 错误签名检测
# ============================================================
print("\n[12] 错误签名检测")
# 篡改 token 中间部分
parts = token.split(".")
tampered_token = parts[0] + "." + "tampered" + "." + parts[2]
try:
    decode_access_token(tampered_token)
    check("错误签名 Token 应被拒绝", False)
except AuthenticationException:
    check("错误签名 Token 抛出 AuthenticationException", True)

# ============================================================
# 13. has_permission() 权限检查
# ============================================================
print("\n[13] has_permission() 权限检查")
check("管理员有 task:read", has_permission("administrator", "task:read"))
check("管理员有 system:admin", has_permission("administrator", "system:admin"))
check("经理有 task:write", has_permission("manager", "task:write"))
check("经理没有 system:admin", not has_permission("manager", "system:admin"))
check("技术员有 grinding:write", has_permission("technician", "grinding:write"))
check("技术员没有 user:delete", not has_permission("technician", "user:delete"))
check("查看者有 report:read", has_permission("viewer", "report:read"))
check("查看者没有 task:write", not has_permission("viewer", "task:write"))
check("不存在的角色", not has_permission("nonexistent", "task:read"))
check("不存在的权限", not has_permission("administrator", "nonexistent:perm"))

# ============================================================
# 14. Role Mapping 角色映射
# ============================================================
print("\n[14] Role Mapping 角色映射")
check("ROLE_PERMISSION_MAP 有 4 个角色", len(ROLE_PERMISSION_MAP) == 4)
check("管理员有全部权限", len(ROLE_PERMISSION_MAP["administrator"]) == 20)
check("经理有 14 个权限", len(ROLE_PERMISSION_MAP["manager"]) == 14)
check("技术员有 6 个权限", len(ROLE_PERMISSION_MAP["technician"]) == 6)
check("查看者有 3 个权限", len(ROLE_PERMISSION_MAP["viewer"]) == 3)

# ============================================================
# 15-18. Role Check
# ============================================================
print("\n[15] is_admin()")
check("admin 是管理员", is_admin("administrator"))
check("manager 不是管理员", not is_admin("manager"))

print("\n[16] is_manager()")
check("manager 是经理", is_manager("manager"))
check("admin 不是经理", not is_manager("administrator"))

print("\n[17] is_technician()")
check("technician 是技术员", is_technician("technician"))
check("viewer 不是技术员", not is_technician("viewer"))

print("\n[18] is_viewer()")
check("viewer 是查看者", is_viewer("viewer"))
check("technician 不是查看者", not is_viewer("technician"))

# ============================================================
# 19. check_permission 抛出异常
# ============================================================
print("\n[19] check_permission 抛出异常")
# 有权限不应抛异常
try:
    check_permission("administrator", "task:read")
    check("有权限时不抛异常", True)
except Exception:
    check("有权限时不抛异常", False)

# 无权限应抛异常
try:
    check_permission("viewer", "task:write")
    check("无权限时应抛异常", False)
except PermissionDeniedException:
    check("无权限时抛出 PermissionDeniedException", True)

# ============================================================
# 20. 缺少 payload 字段抛出异常
# ============================================================
print("\n[20] 缺少 payload 字段抛出异常")
try:
    create_access_token({"sub": "1"})  # 缺少 username, role
    check("缺少字段应抛异常", False)
except BusinessLogicException:
    check("缺少字段抛出 BusinessLogicException", True)

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