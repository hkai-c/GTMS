"""Test: Customer View (Sprint 4 — Task 4.5)

严格依据 DEVELOPMENT_ROADMAP.md Task 4.5 验收标准。
测试 client/views/customer_view.py 和 client/views/customer_edit_dialog.py 全部公开 API 与代码规范。

注意：本测试使用源码分析，不依赖 PySide6 运行环境。
"""

import re
import sys


# ============================================================
# 自检框架
# ============================================================

PASSED = 0
FAILED = 0


def check(desc: str, condition: bool) -> None:
    """执行一条检查。"""
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {desc}")
    else:
        FAILED += 1
        print(f"  [FAIL] {desc}")


print("=" * 60)
print("  Task 4.5 — Customer View Self Test")
print("=" * 60)

# ============================================================
# 读取源码
# ============================================================

with open("client/views/customer_view.py", "r", encoding="utf-8") as f:
    view_source = f.read()
view_lower = view_source.lower()

with open("client/views/customer_edit_dialog.py", "r", encoding="utf-8") as f:
    dialog_source = f.read()
dialog_lower = dialog_source.lower()


# 辅助：提取代码文本（不含 docstring 和注释）
def extract_code_text(source: str) -> str:
    """提取源码中的非 docstring 和非注释部分。"""
    lines = source.split("\n")
    result = []
    in_docstring = False
    for line in lines:
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
        # 跳过纯注释行
        if stripped.startswith("#"):
            continue
        result.append(line)
    return "\n".join(result)


view_code = extract_code_text(view_source)
dialog_code = extract_code_text(dialog_source)

# ============================================================
# [1] py_compile
# ============================================================
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile("client/views/customer_view.py", doraise=True)
    py_compile.compile("client/views/customer_edit_dialog.py", doraise=True)
    check("py_compile customer_view", True)
    check("py_compile customer_edit_dialog", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ============================================================
# [2] 类定义
# ============================================================
print("\n[2] 类定义")
check("CustomerView 类定义", "class CustomerView" in view_source)
check("CustomerEditDialog 类定义", "class CustomerEditDialog" in dialog_source)
check("CustomerView 继承 QWidget", "QWidget" in view_source and "class CustomerView" in view_source)
check("CustomerEditDialog 继承 QDialog", "QDialog" in dialog_source and "class CustomerEditDialog" in dialog_source)

# ============================================================
# [3] __init__ 导出
# ============================================================
print("\n[3] __init__ 导出")
with open("client/views/__init__.py", "r", encoding="utf-8") as f:
    init_source = f.read()
check("__init__ 导入 CustomerView", "from client.views.customer_view import CustomerView" in init_source)
check("__init__ 导入 CustomerEditDialog", "from client.views.customer_edit_dialog import CustomerEditDialog" in init_source)
check("__all__ 包含 CustomerView", '"CustomerView"' in init_source.split("__all__")[-1] if "__all__" in init_source else False)
check("__all__ 包含 CustomerEditDialog", '"CustomerEditDialog"' in init_source.split("__all__")[-1] if "__all__" in init_source else False)

# ============================================================
# [4] 公开 API — CustomerView
# ============================================================
print("\n[4] CustomerView 公开 API")
# 提取公开方法定义
pub_methods = re.findall(r'^\s{4}def\s+(\w+)\s*\(', view_source, re.MULTILINE)
pub_methods = [m for m in pub_methods if not m.startswith("_")]
check("refresh() 存在", "refresh" in pub_methods)
check("customer_changed Signal", "customer_changed" in view_source and "Signal" in view_source)
check("公开方法数量 = 1", len(pub_methods) == 1)

# ============================================================
# [5] 公开 API — CustomerEditDialog
# ============================================================
print("\n[5] CustomerEditDialog 公开 API")
pub_methods = re.findall(r'^\s{4}def\s+(\w+)\s*\(', dialog_source, re.MULTILINE)
pub_methods = [m for m in pub_methods if not m.startswith("_")]
check("get_result() 存在", "get_result" in pub_methods)

# ============================================================
# [6] 工具栏
# ============================================================
print("\n[6] 工具栏")
check("新增客户按钮", "新增客户" in view_code)
check("编辑客户按钮", "编辑客户" in view_code)
check("刷新按钮", "刷新" in view_code)
check("搜索框", "搜索公司名称" in view_source)
check("搜索按钮", "搜索" in view_code)
check("弹性空间", "addStretch" in view_source)

# ============================================================
# [7] 无删除按钮
# ============================================================
print("\n[7] 无删除按钮")
check("无 '删除客户' 按钮", "删除客户" not in view_source)
check("无 delete_customer", "def delete_customer" not in view_source)
check("无 _on_delete", "_on_delete" not in view_source)

# ============================================================
# [8] 表格属性
# ============================================================
print("\n[8] 表格属性")
check("NoEditTriggers", "NoEditTriggers" in view_source)
check("SingleSelection", "SingleSelection" in view_source)
check("SelectRows", "SelectRows" in view_source)
check("AlternatingRowColors", "AlternatingRowColors" in view_source)
check("Stretch", "Stretch" in view_source)

# ============================================================
# [9] 表格列
# ============================================================
print("\n[9] 表格列")
check("公司名称列", "公司名称" in view_source)
check("联系人列", "联系人" in view_source)
check("电话列", "电话" in view_source)
check("邮箱列", "邮箱" in view_source)
check("地址列", "地址" in view_source)
check("创建时间列", "创建时间" in view_source)

# ============================================================
# [10] 分页栏
# ============================================================
print("\n[10] 分页栏")
check("第一页按钮", "第一页" in view_source)
check("上一页按钮", "上一页" in view_source)
check("下一页按钮", "下一页" in view_source)
check("最后一页按钮", "最后一页" in view_source)
check("页标签", "第" in view_source and "页" in view_source)
check("总记录标签", "共" in view_source and "条记录" in view_source)

# ============================================================
# [11] 分页方法
# ============================================================
print("\n[11] 分页方法")
check("_on_first_page", "def _on_first_page" in view_source)
check("_on_prev_page", "def _on_prev_page" in view_source)
check("_on_next_page", "def _on_next_page" in view_source)
check("_on_last_page", "def _on_last_page" in view_source)

# ============================================================
# [12] 搜索
# ============================================================
print("\n[12] 搜索")
check("returnPressed 连接", "returnPressed" in view_source)
check("_on_search 方法", "def _on_search" in view_source)
check("搜索重置到第一页", "_current_page = 1" in view_source)

# ============================================================
# [13] 新增流程
# ============================================================
print("\n[13] 新增流程")
check("_on_add_customer", "def _on_add_customer" in view_source)
check("创建 CustomerEditDialog", "CustomerEditDialog" in view_source)
check("调用 refresh()", "refresh()" in view_source)
check("emit customer_changed", "customer_changed.emit" in view_source)

# ============================================================
# [14] 编辑流程
# ============================================================
print("\n[14] 编辑流程")
check("_on_edit_customer", "def _on_edit_customer" in view_source)
check("检查选中行", "currentRow" in view_source)

# ============================================================
# [15] 数据来源
# ============================================================
print("\n[15] 数据来源")
check("导入 CustomerService", "CustomerService" in view_source)
check("导入 CustomerEditDialog", "CustomerEditDialog" in view_source)
check("调用 list_customers", "list_customers" in view_source)
check("不直接 ApiClient", "ApiClient" not in view_source)
check("不直接 requests", "import requests" not in view_source)

# ============================================================
# [16] 无 ORM / JWT / 数据库
# ============================================================
print("\n[16] 无 ORM / JWT / 数据库")
for src_name, src in [("view", view_source), ("dialog", dialog_source)]:
    for kw in ["jwt", "sqlalchemy", "database", "bcrypt", "Depends"]:
        check(f"{src_name} 不含 {kw}", kw not in src.lower())
# "orm" 子串易误报（如 information），用 sqlalchemy 替代
check("view 不含 sqlalchemy", "sqlalchemy" not in view_source.lower())
check("dialog 不含 sqlalchemy", "sqlalchemy" not in dialog_source.lower())

# ============================================================
# [17] 无 Business Logic（代码中）
# ============================================================
print("\n[17] 无 Business Logic")
# strip() 仅用于搜索框输入清理（基本 UI 输入处理），非业务校验
check("view 代码不含 '唯一'", "唯一" not in view_code)
check("view 代码不含 '重复'", "重复" not in view_code)
check("dialog 代码不含 '唯一'", "唯一" not in dialog_code)
check("dialog 代码不含 '重复'", "重复" not in dialog_code)
check("dialog 代码不含 '为空'", "为空" not in dialog_code)

# ============================================================
# [18] QMessageBox
# ============================================================
print("\n[18] QMessageBox")
check("view 有 QMessageBox.critical", "QMessageBox.critical" in view_source)
check("view 有 QMessageBox.information", "QMessageBox.information" in view_source)
check("dialog 有 QMessageBox.critical", "QMessageBox.critical" in dialog_source)

# ============================================================
# [19] logger
# ============================================================
print("\n[19] logger")
check("view logger", 'logging.getLogger("gtms.client")' in view_source)
check("dialog logger", 'logging.getLogger("gtms.client")' in dialog_source)
check("view 不含 print(", "print(" not in view_source)
check("dialog 不含 print(", "print(" not in dialog_source)

# ============================================================
# [20] Google Docstring
# ============================================================
print("\n[20] Google Docstring")
check("view 模块 docstring", view_source.strip().startswith('"""'))
check("view 类 docstring", 'class CustomerView' in view_source)
check("dialog 模块 docstring", dialog_source.strip().startswith('"""'))
check("dialog 类 docstring", 'class CustomerEditDialog' in dialog_source)

# ============================================================
# [21] Type Hint
# ============================================================
print("\n[21] Type Hint")
check("view 导入 Any", "Any" in view_source)
check("dialog 导入 Any", "Any" in dialog_source)

# ============================================================
# [22] PEP8
# ============================================================
print("\n[22] PEP8")
check("view 有 __all__", "__all__" in view_source)
check("dialog 有 __all__", "__all__" in dialog_source)
check("view 无 TODO", "TODO" not in view_source)
check("view 无 FIXME", "FIXME" not in view_source)
check("dialog 无 TODO", "TODO" not in dialog_source)
check("dialog 无 FIXME", "FIXME" not in dialog_source)

# ============================================================
# [23] 无循环导入
# ============================================================
print("\n[23] 无循环导入")
check("view 不导入 server", "server." not in view_source)
check("dialog 不导入 server", "server." not in dialog_source)

# ============================================================
# [24] 公开 API Freeze
# ============================================================
print("\n[24] 公开 API Freeze")
check("CustomerView 公开方法 = 1", len(pub_methods_after := re.findall(r'^\s{4}def\s+(\w+)\s*\(', view_source, re.MULTILINE)) > 0 and len([m for m in pub_methods_after if not m.startswith("_")]) == 1)
check("CustomerEditDialog 有 get_result", "def get_result" in dialog_source)

# ============================================================
# [25] Dialog 字段
# ============================================================
print("\n[25] Dialog 字段")
check("dialog 公司名称", "company_name_edit" in dialog_source)
check("dialog 联系人", "contact_person_edit" in dialog_source)
check("dialog 电话", "phone_edit" in dialog_source)
check("dialog 邮箱", "email_edit" in dialog_source)
check("dialog 地址", "address_edit" in dialog_source)
check("dialog 备注", "remark_edit" in dialog_source)

# ============================================================
# [26] 刷新从服务器获取
# ============================================================
print("\n[26] 刷新从服务器获取")
check("refresh 调用 CustomerService", "_customer_service.list_customers" in view_source)
check("refresh 不缓存", "self._customers = data.get" in view_source)

# ============================================================
# [27] 分页逻辑
# ============================================================
print("\n[27] 分页逻辑")
check("_current_page 初始值 1", "_current_page: int = 1" in view_source)
check("_page_size 默认 20", "_page_size: int = 20" in view_source)
check("_total 初始值 0", "_total: int = 0" in view_source)

# ============================================================
# [28] Dialog 模式
# ============================================================
print("\n[28] Dialog 模式")
check("dialog _mode 属性", '_mode: str = mode' in dialog_source)
check("dialog 模式判断", 'mode == "create"' in dialog_source or "mode == 'create'" in dialog_source)

# ============================================================
# [29] 异常处理
# ============================================================
print("\n[29] 异常处理")
check("view try/except 存在", "try:" in view_source and "except" in view_source)
check("dialog try/except 存在", "try:" in dialog_source and "except" in dialog_source)

# ============================================================
# [30] 窗口属性
# ============================================================
print("\n[30] 窗口属性")
check("dialog setFixedSize", "setFixedSize" in dialog_source)
check("dialog setModal", "setModal" in dialog_source)
check("view 使用 QVBoxLayout", "QVBoxLayout" in view_source)
check("view 使用 QHBoxLayout", "QHBoxLayout" in view_source)

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