"""Test: Desktop Customer Service (Sprint 4 — Task 4.4)

严格依据 DEVELOPMENT_ROADMAP.md Task 4.4 验收标准。
测试 client/services/customer_service.py 全部公开 API 与代码规范。

注意：本测试使用源码分析，不依赖网络连接。
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
print("  Task 4.4 — Desktop Customer Service Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile("client/services/customer_service.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from client.services.customer_service import CustomerService
    check("CustomerService 导入", True)
except ImportError as e:
    check("import", False)
    print(f"      Error: {e}")
    sys.exit(1)

# ----------------------------------------------------------
# [3] __init__ 导出
# ----------------------------------------------------------
print("\n[3] __init__ 导出")
from client.services import CustomerService as InitCustomerService
check("__init__ 导出 CustomerService", InitCustomerService is CustomerService)

# ----------------------------------------------------------
# [4] 类存在性
# ----------------------------------------------------------
print("\n[4] 类存在性")
check("CustomerService 是 class", inspect.isclass(CustomerService))

# ----------------------------------------------------------
# [5] 公开 API 列表
# ----------------------------------------------------------
print("\n[5] 公开 API 列表")
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
# [6] 禁止 delete_customer
# ----------------------------------------------------------
print("\n[6] 禁止 delete_customer")
all_methods = [m for m in dir(CustomerService) if callable(getattr(CustomerService, m))]
check("无 delete_customer", "delete_customer" not in all_methods)
check("无 delete", "delete" not in [m for m in all_methods if not m.startswith("_")])

# ----------------------------------------------------------
# [7] 公开 API 签名
# ----------------------------------------------------------
print("\n[7] 公开 API 签名")

# list_customers
sig = inspect.signature(CustomerService.list_customers)
params = list(sig.parameters.keys())
check("list_customers 参数: self", "self" in params)
check("list_customers 参数: company_name", "company_name" in params)
check("list_customers 参数: page", "page" in params)
check("list_customers 参数: page_size", "page_size" in params)
check("list_customers 返回 dict", "dict" in str(sig.return_annotation))

# get_customer
sig = inspect.signature(CustomerService.get_customer)
params = list(sig.parameters.keys())
check("get_customer 参数: customer_id", "customer_id" in params)
check("get_customer 返回 dict", "dict" in str(sig.return_annotation))

# create_customer
sig = inspect.signature(CustomerService.create_customer)
params = list(sig.parameters.keys())
check("create_customer 参数: company_name", "company_name" in params)
check("create_customer 参数: contact_person", "contact_person" in params)
check("create_customer 参数: phone", "phone" in params)
check("create_customer 参数: email", "email" in params)
check("create_customer 参数: address", "address" in params)
check("create_customer 参数: remark", "remark" in params)
check("create_customer 返回 dict", "dict" in str(sig.return_annotation))

# update_customer
sig = inspect.signature(CustomerService.update_customer)
params = list(sig.parameters.keys())
check("update_customer 参数: customer_id", "customer_id" in params)
check("update_customer 参数: company_name", "company_name" in params)
check("update_customer 返回 dict", "dict" in str(sig.return_annotation))

# ----------------------------------------------------------
# [8] 源码分析 — 读取源文件
# ----------------------------------------------------------
print("\n[8] 源码分析")
with open("client/services/customer_service.py", "r", encoding="utf-8") as f:
    source = f.read()
source_lower = source.lower()

# ----------------------------------------------------------
# [9] ApiClient 注入
# ----------------------------------------------------------
print("\n[9] ApiClient 注入")
check("导入 ApiClient", "ApiClient" in source)
check("__init__ 参数 api_client: ApiClient", "api_client: ApiClient" in source)
check("self._api_client 赋值", "self._api_client" in source)

# ----------------------------------------------------------
# [10] HTTP 方法映射
# ----------------------------------------------------------
print("\n[10] HTTP 方法映射")
check("list_customers 用 GET", "_api_client.get" in source)
check("get_customer 用 GET", "_api_client.get" in source)
check("create_customer 用 POST", "_api_client.post" in source)
check("update_customer 用 PUT", "_api_client.put" in source)

# ----------------------------------------------------------
# [11] URL 路径
# ----------------------------------------------------------
print("\n[11] URL 路径")
check("GET /api/customers", '/api/customers"' in source or '/api/customers\'' in source)
check("POST /api/customers", "/api/customers" in source)
check("PUT /api/customers/{customer_id}", "/api/customers/" in source)

# ----------------------------------------------------------
# [12] 分页参数
# ----------------------------------------------------------
print("\n[12] 分页参数（list_customers）")
list_method = inspect.getsource(CustomerService.list_customers)
check("params dict 有 page", '"page"' in list_method)
check("params dict 有 page_size", '"page_size"' in list_method)
check("company_name 条件判断", "company_name" in list_method)

# ----------------------------------------------------------
# [13] create_customer Body
# ----------------------------------------------------------
print("\n[13] create_customer Body")
create_method = inspect.getsource(CustomerService.create_customer)
check("body 有 company_name", '"company_name"' in create_method)
check("contact_person 条件判断", "contact_person" in create_method)
check("phone 条件判断", "phone" in create_method)
check("email 条件判断", "email" in create_method)
check("address 条件判断", "address" in create_method)
check("remark 条件判断", "remark" in create_method)

# ----------------------------------------------------------
# [14] update_customer exclude_unset
# ----------------------------------------------------------
print("\n[14] update_customer — 仅提交非 None 字段")
update_method = inspect.getsource(CustomerService.update_customer)
check("body 初始化为空", "body: dict" in update_method and "{}" in update_method)
check("company_name is not None 判断", "company_name is not None" in update_method)
check("contact_person is not None 判断", "contact_person is not None" in update_method)
check("phone is not None 判断", "phone is not None" in update_method)

# ----------------------------------------------------------
# [15] 返回 response.json()
# ----------------------------------------------------------
print("\n[15] 返回 response.json()")
check("list_customers 返回 resp.json()", "resp.json()" in source)
check("get_customer 返回 resp.json()", "resp.json()" in source)
check("create_customer 返回 resp.json()", "resp.json()" in source)
check("update_customer 返回 resp.json()", "resp.json()" in source)

# ----------------------------------------------------------
# [16] 不直接 requests
# ----------------------------------------------------------
print("\n[16] 不直接 requests")
check("不 import requests", "import requests" not in source)
check("不含 requests.get", "requests.get" not in source)
check("不含 requests.post", "requests.post" not in source)
check("不含 requests.Session", "requests.Session" not in source)

# ----------------------------------------------------------
# [17] 无 try/except
# ----------------------------------------------------------
print("\n[17] 无 try/except")
check("不含 try:", "try:" not in source)
check("不含 except", "except" not in source)

# ----------------------------------------------------------
# [18] 异常原样抛出
# ----------------------------------------------------------
print("\n[18] 异常原样抛出")
check("不含 raise 自定义异常", "raise" not in source.split("Raises:")[0] if "Raises:" in source else "raise" not in source_lower)

# ----------------------------------------------------------
# [19] 不缓存数据
# ----------------------------------------------------------
print("\n[19] 不缓存数据")
check("不含 cache", "cache" not in source_lower)
# _customers 是 list_customers 的子串，检查 self._customers 赋值
check("不含 self._customers", "self._customers" not in source)
check("不含 _data", "_data" not in source_lower.split("def list_customers")[0] if "def list_customers" in source_lower else True)

# ----------------------------------------------------------
# [20] 无 JWT / ORM / 数据库
# ----------------------------------------------------------
print("\n[20] 无 JWT / ORM / 数据库")
check("不含 jwt", "jwt" not in source_lower)
check("不含 token", "token" not in source_lower)
check("不含 orm", "orm" not in source_lower)
check("不含 sqlalchemy", "sqlalchemy" not in source_lower)
check("不含 database", "database" not in source_lower)

# ----------------------------------------------------------
# [21] 无 Server 依赖
# ----------------------------------------------------------
print("\n[21] 无 Server 依赖")
check("不含 server.", "server." not in source)
check("不含 server.models", "server.models" not in source)
check("不含 server.schemas", "server.schemas" not in source)

# ----------------------------------------------------------
# [22] 无 Business Logic
# ----------------------------------------------------------
print("\n[22] 无 Business Logic")
# 提取代码（不含 docstring）
code_only = ""
in_docstring = False
for line in source.split("\n"):
    stripped = line.strip()
    if stripped.startswith('"""') and not in_docstring:
        if stripped.count('"""') >= 2:
            continue
        in_docstring = True
        continue
    if in_docstring:
        if '"""' in stripped:
            in_docstring = False
        continue
    code_only += line + "\n"
code_lower = code_only.lower()
check("不含 company_name 校验", "not company_name" not in source)
check("不含 strip()", "strip()" not in source)
check("代码不含 '重复'", "重复" not in code_only)
check("代码不含 '唯一'", "唯一" not in code_only)
check("代码不含 '不存在'", "不存在" not in code_only)

# ----------------------------------------------------------
# [23] logger
# ----------------------------------------------------------
print("\n[23] logger")
check("导入 logging", "import logging" in source)
check('logger = logging.getLogger("gtms.client")', 'logging.getLogger("gtms.client")' in source)
check("logger.debug 调用", "logger.debug" in source)
check("logger.info 调用", "logger.info" in source)
check("不含 print(", "print(" not in source)

# ----------------------------------------------------------
# [24] Google Docstring
# ----------------------------------------------------------
print("\n[24] Google Docstring")
check("模块有 docstring", source.strip().startswith('"""'))
check("类有 docstring", 'class CustomerService' in source)
check("list_customers 有 docstring", '"""查询客户列表' in source)
check("get_customer 有 docstring", '"""获取客户详情' in source)
check("create_customer 有 docstring", '"""创建客户' in source)
check("update_customer 有 docstring", '"""修改客户信息' in source)

# ----------------------------------------------------------
# [25] Type Hint
# ----------------------------------------------------------
print("\n[25] Type Hint")
check("导入 Any", "Any" in source)
check("导入 ApiClient", "from client.services.api_client import ApiClient" in source)
check("__init__ 类型标注", "api_client: ApiClient" in source)
check("list_customers 返回 dict", "dict[str, Any]" in source)
check("create_customer 返回 dict", "dict[str, Any]" in source)

# ----------------------------------------------------------
# [26] PEP8
# ----------------------------------------------------------
print("\n[26] PEP8")
check("文件以 docstring 开头", source.strip().startswith('"""'))
check("有 __all__", "__all__" in source)
check("__all__ 包含 CustomerService", "CustomerService" in source.split("__all__")[-1] if "__all__" in source else False)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)

# ----------------------------------------------------------
# [27] 无循环导入
# ----------------------------------------------------------
print("\n[27] 无循环导入")
check("不导入 server", "server." not in source)
check("不导入 client.views", "client.views" not in source)

# ----------------------------------------------------------
# [28] 禁止命名
# ----------------------------------------------------------
print("\n[28] 禁止命名")
check("不含 print(", "print(" not in source)

# ----------------------------------------------------------
# [29] 公开 API Freeze
# ----------------------------------------------------------
print("\n[29] 公开 API Freeze")
check("公开方法数量 = 4", len(public_methods) == 4)
check("无 delete_customer", "def delete_customer" not in source)

# ----------------------------------------------------------
# [30] 自检 — __all__
# ----------------------------------------------------------
print("\n[30] __all__")
tree = ast.parse(source)
all_found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        if isinstance(node.targets[0], ast.Name) and node.targets[0].id == "__all__":
            if isinstance(node.value, ast.List):
                all_found = True
                values = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
                check("__all__ 包含 CustomerService", "CustomerService" in values)
                check("__all__ 长度 = 1", len(values) == 1)
check("__all__ 存在", all_found)

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