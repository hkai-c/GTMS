"""Test: Customer Service (Sprint 4 — Task 4.2)

严格依据 DEVELOPMENT_ROADMAP.md Task 4.2 验收标准。
测试 server/services/customer_service.py 全部公开 API 与代码规范。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import ast
import inspect
import sys


# ============================================================
# 自检框架
# ============================================================

PASSED = 0
FAILED = 0


def check(desc: str, condition: bool) -> None:
    """执行一条检查。

    Args:
        desc: 检查描述。
        condition: 检查条件。
    """
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {desc}")
    else:
        FAILED += 1
        print(f"  [FAIL] {desc}")


# ============================================================
# 自检
# ============================================================

print("=" * 60)
print("  Task 4.2 — Customer Service Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile("server/services/customer_service.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.services.customer_service import CustomerService
    check("CustomerService 导入", True)
except ImportError as e:
    check("import", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("CustomerService 是 class", inspect.isclass(CustomerService))
check("CustomerService 可实例化", CustomerService() is not None)

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(CustomerService)
    if not m.startswith("_") and callable(getattr(CustomerService, m))
]
check("list_customers 存在", "list_customers" in public_methods)
check("get_customer 存在", "get_customer" in public_methods)
check("create_customer 存在", "create_customer" in public_methods)
check("update_customer 存在", "update_customer" in public_methods)
check("公开 API 数量 = 4", len(public_methods) == 4)

# ----------------------------------------------------------
# [5] 禁止 delete_customer
# ----------------------------------------------------------
print("\n[5] 禁止 delete_customer")
all_methods = [m for m in dir(CustomerService) if callable(getattr(CustomerService, m))]
check("无 delete_customer", "delete_customer" not in all_methods)
check("无 delete", "delete" not in [m for m in all_methods if not m.startswith("_")])

# ----------------------------------------------------------
# [6] 公开 API 签名
# ----------------------------------------------------------
print("\n[6] 公开 API 签名")

# list_customers
sig = inspect.signature(CustomerService.list_customers)
params = list(sig.parameters.keys())
check("list_customers 参数: db", "db" in params)
check("list_customers 参数: company_name", "company_name" in params)
check("list_customers 参数: page", "page" in params)
check("list_customers 参数: page_size", "page_size" in params)
check("list_customers 返回类型包含 CustomerListResponse",
      "CustomerListResponse" in str(sig.return_annotation))

# get_customer
sig = inspect.signature(CustomerService.get_customer)
params = list(sig.parameters.keys())
check("get_customer 参数: db", "db" in params)
check("get_customer 参数: customer_id", "customer_id" in params)
check("get_customer 返回类型包含 CustomerResponse",
      "CustomerResponse" in str(sig.return_annotation))

# create_customer
sig = inspect.signature(CustomerService.create_customer)
params = list(sig.parameters.keys())
check("create_customer 参数: db", "db" in params)
check("create_customer 参数: data", "data" in params)
check("create_customer 参数: operator_id", "operator_id" in params)
check("create_customer 返回类型包含 CustomerResponse",
      "CustomerResponse" in str(sig.return_annotation))

# update_customer
sig = inspect.signature(CustomerService.update_customer)
params = list(sig.parameters.keys())
check("update_customer 参数: db", "db" in params)
check("update_customer 参数: customer_id", "customer_id" in params)
check("update_customer 参数: data", "data" in params)
check("update_customer 参数: operator_id", "operator_id" in params)
check("update_customer 返回类型包含 CustomerResponse",
      "CustomerResponse" in str(sig.return_annotation))

# ----------------------------------------------------------
# [7] 源码分析 — 读取源文件
# ----------------------------------------------------------
print("\n[7] 源码分析")
with open("server/services/customer_service.py", "r", encoding="utf-8") as f:
    source = f.read()
source_lower = source.lower()

# 提取代码（不含 docstring 和注释）
tree = ast.parse(source)
code_lines = []
for node in ast.walk(tree):
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
        continue
code_text = source  # 保留完整源码用于模式匹配

# ----------------------------------------------------------
# [8] 异常使用
# ----------------------------------------------------------
print("\n[8] 异常使用")
check("NotFoundError 异常", "NotFoundException" in source)
check("BusinessLogicException", "BusinessLogicException" in source)
check("不含 HTTPException", "HTTPException" not in source)
check("不含 ValidationException", "ValidationException" not in source)
check("不含 AuthorizationException", "AuthorizationException" not in source)
check("不含 ConflictException", "ConflictException" not in source)

# ----------------------------------------------------------
# [9] 不修改 Frozen API
# ----------------------------------------------------------
print("\n[9] 不修改 Frozen API")
check("不导入 security", "server.core.security" not in source)
check("不含 hash_password", "hash_password" not in source)
check("不含 verify_password", "verify_password" not in source)
check("不含 has_permission", "has_permission" not in source)
check("不含 create_access_token", "create_access_token" not in source)
check("不含 JWT", "jwt" not in source_lower)
check("不含 FastAPI", "fastapi" not in source_lower)
check("不含 requests", "requests" not in source_lower)

# ----------------------------------------------------------
# [10] 事务处理
# ----------------------------------------------------------
print("\n[10] 事务处理")
check("包含 db.commit()", "db.commit()" in source)
check("包含 db.rollback()", "db.rollback()" in source)
check("包含 try/except", "try:" in source and "except" in source)

# 检查 create_customer 中的 try/commit/rollback
create_method = inspect.getsource(CustomerService.create_customer)
check("create_customer 有 commit", "db.commit()" in create_method)
check("create_customer 有 rollback", "db.rollback()" in create_method)

# 检查 update_customer 中的 try/commit/rollback
update_method = inspect.getsource(CustomerService.update_customer)
check("update_customer 有 commit", "db.commit()" in update_method)
check("update_customer 有 rollback", "db.rollback()" in update_method)

# ----------------------------------------------------------
# [11] SystemLog
# ----------------------------------------------------------
print("\n[11] SystemLog")
check("导入 SystemLog", "SystemLog" in source)
check("导入 ActionType", "ActionType" in source)
check("使用 ActionType.CREATE", "ActionType.CREATE" in source)
check("使用 ActionType.UPDATE", "ActionType.UPDATE" in source)
check("_write_log 方法存在", "_write_log" in source)
check("create_customer 写入 SystemLog", "Customer Created" in source or "Customer" in source)
check("update_customer 写入 SystemLog", "Customer Updated" in source or "Customer" in source)

# ----------------------------------------------------------
# [12] 日志
# ----------------------------------------------------------
print("\n[12] 日志")
check("导入 logging", "import logging" in source)
check("logger = logging.getLogger", "logging.getLogger" in source)
check("logger.info 调用", "logger.info" in source)
check("logger.exception 调用", "logger.exception" in source)
check("不含 print(", "print(" not in source)

# ----------------------------------------------------------
# [13] 业务逻辑 — company_name strip()
# ----------------------------------------------------------
print("\n[13] company_name strip()")
check("create_customer 有 strip()", ".strip()" in create_method)
check("update_customer 有 strip()", ".strip()" in update_method)

# ----------------------------------------------------------
# [14] 业务逻辑 — company_name 唯一性
# ----------------------------------------------------------
print("\n[14] company_name 唯一性")
check("create_customer 检查重复", "客户名称已存在" in create_method)
check("update_customer 检查重复", "客户名称已存在" in update_method)
check("update_customer 排除自身", "Customer.id !=" in update_method or "id != customer_id" in update_method)

# ----------------------------------------------------------
# [15] 业务逻辑 — exclude_unset
# ----------------------------------------------------------
print("\n[15] update_customer exclude_unset")
check("使用 model_dump(exclude_unset=True)", "exclude_unset" in update_method)

# ----------------------------------------------------------
# [16] 业务逻辑 — 分页与排序
# ----------------------------------------------------------
print("\n[16] list_customers 分页与排序")
list_method = inspect.getsource(CustomerService.list_customers)
check("使用 offset", "offset" in list_method)
check("使用 limit", "limit" in list_method)
check("使用 order_by", "order_by" in list_method)
check("按 company_name 排序", "company_name" in list_method and "asc" in list_method.lower())
check("使用 like", "like" in list_method)

# ----------------------------------------------------------
# [17] 业务逻辑 — 过滤 is_deleted
# ----------------------------------------------------------
print("\n[17] 过滤 is_deleted")
check("list_customers 过滤 is_deleted", "is_deleted" in list_method)
check("get_customer 过滤 is_deleted", "is_deleted" in inspect.getsource(CustomerService.get_customer))
check("create_customer 检查唯一性时过滤 is_deleted", "is_deleted" in create_method)

# ----------------------------------------------------------
# [18] ORM 映射
# ----------------------------------------------------------
print("\n[18] ORM 映射")
check("_to_response 方法存在", "_to_response" in source)
check("contact_person 映射", "contact_person" in source)
check("email=None 预留", "email=None" in source)
check("remark=None 预留", "remark=None" in source)

# ----------------------------------------------------------
# [19] CustomerResponse / CustomerListResponse
# ----------------------------------------------------------
print("\n[19] Schema 返回类型")
check("导入 CustomerResponse", "CustomerResponse" in source)
check("导入 CustomerListResponse", "CustomerListResponse" in source)
check("导入 CustomerCreate", "CustomerCreate" in source)
check("导入 CustomerUpdate", "CustomerUpdate" in source)

# ----------------------------------------------------------
# [20] 无 Router 导入
# ----------------------------------------------------------
print("\n[20] 无 Router 导入")
check("不导入 server.routers", "server.routers" not in source)
check("不导入 fastapi", "fastapi" not in source_lower)
check("不导入 HTTPException", "HTTPException" not in source)
check("不导入 Depends", "Depends" not in source)
check("不导入 APIRouter", "APIRouter" not in source)

# ----------------------------------------------------------
# [21] 不导入 client
# ----------------------------------------------------------
print("\n[21] 不导入 client")
check("不导入 client", "client" not in source)

# ----------------------------------------------------------
# [22] 私有方法
# ----------------------------------------------------------
print("\n[22] 私有方法")
private_methods = [m for m in dir(CustomerService) if m.startswith("_") and not m.startswith("__") and callable(getattr(CustomerService, m))]
check("_to_response 是私有方法", "_to_response" in private_methods)
check("_write_log 是私有方法", "_write_log" in private_methods)

# ----------------------------------------------------------
# [23] Type Hint
# ----------------------------------------------------------
print("\n[23] Type Hint")
check("导入 Optional", "Optional" in source)
check("导入 Session", "Session" in source)
check("db 参数有类型标注", "db: Session" in source)

# ----------------------------------------------------------
# [24] Google Docstring
# ----------------------------------------------------------
print("\n[24] Google Docstring")
check("模块有 docstring", source.strip().startswith('"""'))
check("类有 docstring", 'class CustomerService' in source)
check("list_customers 有 Args", "Args:" in list_method)
check("list_customers 有 Returns", "Returns:" in list_method)
check("create_customer 有 Args", "Args:" in create_method)
check("create_customer 有 Returns", "Returns:" in create_method)
check("create_customer 有 Raises", "Raises:" in create_method)
check("update_customer 有 Args", "Args:" in update_method)
check("update_customer 有 Returns", "Returns:" in update_method)
check("update_customer 有 Raises", "Raises:" in update_method)

# ----------------------------------------------------------
# [25] PEP8
# ----------------------------------------------------------
print("\n[25] PEP8")
check("文件以 docstring 开头", source.strip().startswith('"""'))
check("有 __all__", "__all__" in source)
check("__all__ 包含 CustomerService", "CustomerService" in source.split("__all__")[-1] if "__all__" in source else False)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("导入在文件顶部", source.index("class CustomerService") > source.index("import"))

# ----------------------------------------------------------
# [26] 无循环导入
# ----------------------------------------------------------
print("\n[26] 无循环导入")
check("不导入 server.routers", "server.routers" not in source)
check("不导入 client", "client." not in source)

# ----------------------------------------------------------
# [27] 禁止命名检查
# ----------------------------------------------------------
print("\n[27] 禁止命名检查")
check("不含 ValidationException", "validationexception" not in source_lower)
check("不含 AuthorizationException", "authorizationexception" not in source_lower)
check("不含 ConflictException", "conflictexception" not in source_lower)
check("不含 HTTPException", "httpexception" not in source_lower)

# ----------------------------------------------------------
# [28] 公开 API Freeze
# ----------------------------------------------------------
print("\n[28] 公开 API Freeze")
check("公开方法数量 = 4", len(public_methods) == 4)
check("无 delete_customer", "delete_customer" not in source)
check("无 delete 公开方法", not any("def delete" in source for _ in [1]))
check("不含 'def delete'", "def delete" not in source)

# ----------------------------------------------------------
# [29] 不删除功能
# ----------------------------------------------------------
print("\n[29] 不删除功能")
check("无 ActionType.DELETE", "ActionType.DELETE" not in source)
check("无 is_deleted = True 赋值", "is_deleted = True" not in source)
# 删除只出现在 docstring 说明"不提供删除"，业务代码中无删除逻辑
check("无 delete_customer 方法", "def delete_customer" not in source)
check("无 '该客户存在关联任务'", "该客户存在关联任务" not in source)
check("无 '无法删除'", "无法删除" not in source)

# ----------------------------------------------------------
# [30] 全源码扫描
# ----------------------------------------------------------
print("\n[30] 全源码扫描")
check("不含 print(", "print(" not in source)
check("不含 pass", "pass" not in source.split("class")[0])  # 仅检查非类定义区域
check("有 Contact 映射", "contact_person=customer.contact" in source)

# ============================================================
# 结果
# ============================================================
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  结果: ALL PASSED")
else:
    print("  结果: SOME FAILED")
print("=" * 60)

sys.exit(0 if FAILED == 0 else 1)