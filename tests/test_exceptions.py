"""Sprint 2 — Task 2.1 异常体系自检脚本

验证项：
    1.  py_compile
    2.  导入检查
    3.  BaseAppException 属性
    4.  to_dict()
    5.  __str__()
    6.  __repr__()
    7.  BusinessLogicException
    8.  AuthenticationException
    9.  PermissionDeniedException
    10. NotFoundException
    11. DuplicateException
    12. status_code 默认值
    13. code 默认值
    14. message 默认值
    15. detail 默认值
    16. 继承关系
    17. 可自定义 message
    18. raise / except BaseAppException
    19. 全部异常实例化成功
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.core.exceptions import (
    BaseAppException,
    BusinessLogicException,
    AuthenticationException,
    PermissionDeniedException,
    NotFoundException,
    DuplicateException,
)

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    """检查条件并输出结果。"""
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  -- {detail}")


print("=" * 60)
print("  Task 2.1 — Exceptions Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "core" / "exceptions.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. 导入检查
# ============================================================
print("\n[2] 导入检查")
check("BaseAppException", BaseAppException is not None)
check("BusinessLogicException", BusinessLogicException is not None)
check("AuthenticationException", AuthenticationException is not None)
check("PermissionDeniedException", PermissionDeniedException is not None)
check("NotFoundException", NotFoundException is not None)
check("DuplicateException", DuplicateException is not None)

# ============================================================
# 3. BaseAppException 属性
# ============================================================
print("\n[3] BaseAppException 属性")
base = BaseAppException("test", status_code=500, code="TEST_CODE", detail={"key": "val"})
check("message", base.message == "test")
check("status_code", base.status_code == 500)
check("code", base.code == "TEST_CODE")
check("detail", base.detail == {"key": "val"})

# ============================================================
# 4. to_dict()
# ============================================================
print("\n[4] to_dict()")
d = base.to_dict()
check("to_dict has code", d.get("code") == "TEST_CODE")
check("to_dict has message", d.get("message") == "test")
check("to_dict has detail", d.get("detail") == {"key": "val"})

# to_dict with None detail
base_no_detail = BaseAppException("no detail", status_code=500, code="NO_DETAIL")
d2 = base_no_detail.to_dict()
check("to_dict without detail", "detail" not in d2)

# ============================================================
# 5. __str__()
# ============================================================
print("\n[5] __str__()")
check("__str__", str(base) == "[TEST_CODE] test")

# ============================================================
# 6. __repr__()
# ============================================================
print("\n[6] __repr__()")
r = repr(base)
check("__repr__ has class name", "BaseAppException" in r)
check("__repr__ has code", "TEST_CODE" in r)
check("__repr__ has status_code", "500" in r)

# ============================================================
# 7-11. 各子类默认值
# ============================================================
print("\n[7] BusinessLogicException 默认值")
e = BusinessLogicException()
check("status_code = 400", e.status_code == 400)
check("code = BUSINESS_ERROR", e.code == "BUSINESS_ERROR")
check("message", e.message == "Business logic error")
check("detail is None", e.detail is None)

print("\n[8] AuthenticationException 默认值")
e = AuthenticationException()
check("status_code = 401", e.status_code == 401)
check("code = AUTHENTICATION_FAILED", e.code == "AUTHENTICATION_FAILED")
check("message", e.message == "Authentication failed")

print("\n[9] PermissionDeniedException 默认值")
e = PermissionDeniedException()
check("status_code = 403", e.status_code == 403)
check("code = PERMISSION_DENIED", e.code == "PERMISSION_DENIED")
check("message", e.message == "Permission denied")

print("\n[10] NotFoundException 默认值")
e = NotFoundException()
check("status_code = 404", e.status_code == 404)
check("code = NOT_FOUND", e.code == "NOT_FOUND")
check("message", e.message == "Resource not found")

print("\n[11] DuplicateException 默认值")
e = DuplicateException()
check("status_code = 409", e.status_code == 409)
check("code = DUPLICATE_DATA", e.code == "DUPLICATE_DATA")
check("message", e.message == "Duplicate data")

# ============================================================
# 12. 继承关系
# ============================================================
print("\n[12] 继承关系")
check("BaseAppException → Exception", issubclass(BaseAppException, Exception))
check("BusinessLogicException → BaseAppException", issubclass(BusinessLogicException, BaseAppException))
check("AuthenticationException → BaseAppException", issubclass(AuthenticationException, BaseAppException))
check("PermissionDeniedException → BaseAppException", issubclass(PermissionDeniedException, BaseAppException))
check("NotFoundException → BaseAppException", issubclass(NotFoundException, BaseAppException))
check("DuplicateException → BaseAppException", issubclass(DuplicateException, BaseAppException))

# ============================================================
# 13. 可自定义 message
# ============================================================
print("\n[13] 可自定义 message")
e = NotFoundException("用户 123 不存在")
check("自定义 message", e.message == "用户 123 不存在")
check("code 仍为默认", e.code == "NOT_FOUND")

# ============================================================
# 14. raise / except BaseAppException
# ============================================================
print("\n[14] raise / except BaseAppException")
try:
    raise BusinessLogicException("业务错误")
except BaseAppException as e:
    check("捕获 BaseAppException", e.message == "业务错误")
    check("status_code", e.status_code == 400)

try:
    raise NotFoundException("资源不存在")
except BaseAppException as e:
    check("捕获 NotFoundException", isinstance(e, NotFoundException))

# ============================================================
# 15. 全部异常实例化
# ============================================================
print("\n[15] 全部异常实例化成功")
exceptions = [
    BaseAppException("base", status_code=500, code="BASE"),
    BusinessLogicException("自定义"),
    AuthenticationException("认证失败"),
    PermissionDeniedException("权限不足"),
    NotFoundException("资源不存在"),
    DuplicateException("数据重复"),
]
for ex in exceptions:
    name = ex.__class__.__name__
    check(f"实例化 {name}", isinstance(ex, BaseAppException))

# ============================================================
# 16. 检查禁止的命名
# ============================================================
print("\n[16] 禁止命名检查")
try:
    from server.core.exceptions import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未导出", True)

try:
    from server.core.exceptions import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未导出", True)

try:
    from server.core.exceptions import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未导出", True)

# ============================================================
# 17. 非 FastAPI 依赖
# ============================================================
print("\n[17] 非 FastAPI 依赖")
try:
    from fastapi import HTTPException  # noqa: F401
    check("FastAPI 是否已安装", True, "（非测试项，仅记录）")
except ImportError:
    check("FastAPI 未安装", True, "纯 Python Exception 无依赖")

# 验证异常类本身不依赖 HTTPException
check("BaseAppException 父类是 Exception", BaseAppException.__bases__ == (Exception,))

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

# 退出码
sys.exit(0 if FAILED == 0 else 1)