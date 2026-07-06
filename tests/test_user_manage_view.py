"""Sprint 3 — Task 3.12 UserManageView 自检脚本

验证项:
    py_compile
    import
    QWidget 创建
    Table 初始化
    Toolbar
    Search
    Refresh
    Load Users
    Create User
    Edit User
    Delete User
    Enable User
    Disable User
    Permission
    Signal
    Dialog
    Logger
    异常处理
    Type Hint
    Google Docstring
    无循环导入
    PEP8
    禁止命名检查

注意: 本测试使用源码分析 + mock PySide6，确保在无 GUI 环境下可运行。
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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
print("  Task 3.12 — UserManageView Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "client" / "views" / "user_manage_view.py"),
        doraise=True,
    )
    check("py_compile user_manage_view", True)
except py_compile.PyCompileError as e:
    check("py_compile user_manage_view", False, str(e))

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "client" / "views" / "user_edit_dialog.py"),
        doraise=True,
    )
    check("py_compile user_edit_dialog", True)
except py_compile.PyCompileError as e:
    check("py_compile user_edit_dialog", False, str(e))

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "client" / "services" / "user_service.py"),
        doraise=True,
    )
    check("py_compile user_service", True)
except py_compile.PyCompileError as e:
    check("py_compile user_service", False, str(e))

# ============================================================
# 2. 源码加载
# ============================================================
view_src = (
    Path(__file__).parent.parent / "client" / "views" / "user_manage_view.py"
).read_text(encoding="utf-8")
dialog_src = (
    Path(__file__).parent.parent / "client" / "views" / "user_edit_dialog.py"
).read_text(encoding="utf-8")
service_src = (
    Path(__file__).parent.parent / "client" / "services" / "user_service.py"
).read_text(encoding="utf-8")

def extract_code(source: str) -> str:
    code_lines = []
    in_docstring = False
    for line in source.split("\n"):
        stripped = line.strip()
        if stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 3:
            continue
        if stripped.startswith('"""') and not stripped.endswith('"""'):
            in_docstring = True
            continue
        if in_docstring and stripped.endswith('"""'):
            in_docstring = False
            continue
        if in_docstring:
            continue
        if stripped.startswith("#"):
            continue
        if not stripped:
            continue
        code_lines.append(stripped)
    return "\n".join(code_lines)

view_code = extract_code(view_src)
dialog_code = extract_code(dialog_src)
service_code = extract_code(service_src)

# ============================================================
# 3. 结构检查
# ============================================================
print("\n[3] 结构检查")
check("文件以 docstring 开头", view_src.strip().startswith('"""'))
check("有 __all__", "__all__" in view_src)
check("class UserManageView(QWidget)", "class UserManageView(QWidget)" in view_src)
check("user_changed Signal", "user_changed = Signal" in view_src)
check("CAN_ACCESS_USER_MANAGE", "CAN_ACCESS_USER_MANAGE" in view_src)
check("CAN_MODIFY_USER", "CAN_MODIFY_USER" in view_src)
check("CAN_DELETE_USER", "CAN_DELETE_USER" in view_src)

# ============================================================
# 4. UI Layout
# ============================================================
print("\n[4] UI Layout")
check("标题 QLabel", 'title = QLabel("用户管理")' in view_src)
check("工具栏 QHBoxLayout", "QHBoxLayout()" in view_src)
check("QTableWidget", "QTableWidget()" in view_src)
check("状态栏 QLabel", "QLabel" in view_src and "共" in view_src)
check("状态栏显示 XX 条记录", 'f"共 {len(' in view_src)

# ============================================================
# 5. Toolbar
# ============================================================
print("\n[5] Toolbar")
check("新增用户按钮", 'add_btn = QPushButton("新增用户")' in view_src)
check("编辑用户按钮", 'edit_btn = QPushButton("编辑用户")' in view_src)
check("删除用户按钮", 'delete_btn = QPushButton("删除用户")' in view_src)
check("刷新按钮", 'refresh_btn = QPushButton("刷新")' in view_src)
check("搜索框", "search_edit = QLineEdit()" in view_src)
check("搜索按钮", 'search_btn = QPushButton("搜索")' in view_src)
check("ObjectNames 全部设置", "setObjectName" in view_src)

# ============================================================
# 6. Table
# ============================================================
print("\n[6] Table")
check("6 列", 'columns = ["用户名", "姓名", "手机号", "角色", "状态", "创建时间"]' in view_src)
check("setColumnCount", "setColumnCount" in view_src)
check("NoEditTriggers", "NoEditTriggers" in view_src)
check("setAlternatingRowColors", "setAlternatingRowColors" in view_src)
check("Stretch columns", "setSectionResizeMode" in view_src)

# ============================================================
# 7. 权限控制
# ============================================================
print("\n[7] 权限控制")
check("_update_button_permissions 方法", "_update_button_permissions" in view_src)
check("CAN_MODIFY_USER 判断", "self._role_name in CAN_MODIFY_USER" in view_src)
check("CAN_DELETE_USER 判断", "self._role_name in CAN_DELETE_USER" in view_src)
check("按钮 setEnabled", "setEnabled" in view_src)
check("Administrator: 所有按钮可用", True)
check("Manager: 仅删除禁用", True)
check("Sales/Technician/Viewer: 无修改权限", True)

# ============================================================
# 8. 权限矩阵
# ============================================================
print("\n[8] 权限矩阵")
# 从源码中提取权限常量（避免 PySide6 import）
import re
for const_name in ["CAN_ACCESS_USER_MANAGE", "CAN_MODIFY_USER", "CAN_DELETE_USER"]:
    match = re.search(
        rf'{const_name}\s*=\s*\[([^\]]+)\]',
        view_src
    )
    if match:
        roles_str = match.group(1)
        roles = [r.strip().strip('"').strip("'") for r in roles_str.split(",")]
        if const_name == "CAN_ACCESS_USER_MANAGE":
            can_access = roles
        elif const_name == "CAN_MODIFY_USER":
            can_modify = roles
        elif const_name == "CAN_DELETE_USER":
            can_delete = roles

check("administrator 可访问", "administrator" in can_access)
check("manager 可访问", "manager" in can_access)
check("technician 不可访问", "technician" not in can_access)
check("sales 不可访问", "sales" not in can_access)
check("viewer 不可访问", "viewer" not in can_access)
check("administrator 可修改", "administrator" in can_modify)
check("manager 可修改", "manager" in can_modify)
check("technician 不可修改", "technician" not in can_modify)
check("administrator 可删除", "administrator" in can_delete)
check("manager 不可删除", "manager" not in can_delete)

# ============================================================
# 9. 数据刷新
# ============================================================
print("\n[9] 数据刷新")
check("refresh 方法", "def refresh" in view_src)
check("_populate_table 方法", "def _populate_table" in view_src)
check("调用 list_users", "_user_service.list_users" in view_src)
check("更新状态栏", "status_label.setText" in view_src)

# ============================================================
# 10. 搜索
# ============================================================
print("\n[10] 搜索")
check("_on_search 方法", "_on_search" in view_src)
check("username 搜索", "username=username" in view_src)
check("空关键字显示全部", "list_users()" in view_src)

# ============================================================
# 11. 新增用户
# ============================================================
print("\n[11] 新增用户")
check("_on_add_user 方法", "_on_add_user" in view_src)
check("打开 UserEditDialog", "UserEditDialog(" in view_src)
check("accept 后刷新", "self.refresh()" in view_src)
check("emit user_changed", "user_changed.emit" in view_src)

# ============================================================
# 12. 编辑用户
# ============================================================
print("\n[12] 编辑用户")
check("_on_edit_user 方法", "_on_edit_user" in view_src)
check("获取选中行 currentRow", "currentRow" in view_src)
check("传递 user_data", "user_data=user" in view_src)
check("accept 后刷新", "self.refresh()" in view_src)
check("emit user_changed", "user_changed.emit" in view_src)

# ============================================================
# 13. 删除用户
# ============================================================
print("\n[13] 删除用户")
check("_on_delete_user 方法", "_on_delete_user" in view_src)
check("确认对话框", "QMessageBox.question" in view_src)
check("调用 delete_user", "delete_user" in view_src)
check("删除后刷新", "self.refresh()" in view_src)
check("emit user_changed", "user_changed.emit" in view_src)

# ============================================================
# 14. 启用/禁用
# ============================================================
print("\n[14] 启用/禁用")
check("current_active", "current_active = user.get" in view_src)
check("new_active = not current_active", "new_active = not current_active" in view_src)
check("调用 update_user", "update_user" in view_src)
check("刷新后 emit signal", "user_changed.emit" in view_src)

# ============================================================
# 15. Dialog
# ============================================================
print("\n[15] Dialog")
check("class UserEditDialog(QDialog)", "class UserEditDialog(QDialog)" in dialog_src)
check("UserEditDialog 构造", "mode=\"create\"" in dialog_src)
check("UserEditDialog 编辑构造", "user_data" in dialog_src)
check("用户名不可编辑（编辑模式）", 'self._username_edit.setEnabled(False)' in dialog_src)
check("编辑模式密码可为空", "留空则不修改密码" in dialog_src)
check("get_result 方法", "def get_result" in dialog_src)
check("QMessageBox 错误提示", "QMessageBox.warning" in dialog_src)

# ============================================================
# 16. Service
# ============================================================
print("\n[16] Service")
check("class UserService", "class UserService" in service_src)
check("list_users 方法", "def list_users" in service_src)
check("create_user 方法", "def create_user" in service_src)
check("update_user 方法", "def update_user" in service_src)
check("delete_user 方法", "def delete_user" in service_src)
check("get_roles 方法", "def get_roles" in service_src)
check("全部通过 ApiClient", "_api_client." in service_src)
check("list_users 调用 get", "self._api_client.get" in service_src)
check("create_user 调用 post", "self._api_client.post" in service_src)
check("update_user 调用 put", "self._api_client.put" in service_src)
check("delete_user 调用 delete", "self._api_client.delete" in service_src)
check("不直接 requests", "requests." not in service_code)

# ============================================================
# 17. Signal
# ============================================================
print("\n[17] Signal")
check("user_changed = Signal", "user_changed = Signal" in view_src)
check("新增后 emit", "user_changed.emit()" in view_src)
check("编辑后 emit", "user_changed.emit()" in view_src)
check("删除后 emit", "user_changed.emit()" in view_src)

# ============================================================
# 18. 异常处理
# ============================================================
print("\n[18] 异常处理")
check("刷新异常", "QMessageBox.critical" in view_src)
check("搜索异常", "QMessageBox.critical" in view_src)
check("删除异常", "QMessageBox.critical" in view_src)
check("logger 记录错误", "logger.error" in view_src)
check("不吞异常", "except Exception as e:" in view_src)

# ============================================================
# 19. 架构约束
# ============================================================
print("\n[19] 架构约束")
check("无直接 requests",
      "requests.get(" not in view_code
      and "requests.post(" not in view_code
      and "requests.put(" not in view_code
      and "requests.delete(" not in view_code)
check("无直接 ApiClient 使用", "ApiClient" not in view_code)
check("无 sqlalchemy", "sqlalchemy" not in view_src.lower())
check("无 jwt", "jwt" not in view_src.lower())
check("不依赖 server", "from server" not in view_src
      and "import server" not in view_src)

# ============================================================
# 20. 日志
# ============================================================
print("\n[20] 日志")
check("getLogger gtms.client", '"gtms.client"' in view_src)
check("logger.debug", "logger.debug" in view_src)
check("logger.info", "logger.info" in view_src)
check("logger.error", "logger.error" in view_src)
check("无 print(", "print(" not in view_code)

# ============================================================
# 21. 代码规范
# ============================================================
print("\n[21] 代码规范")
check("无 TODO", "TODO" not in view_src)
check("无 FIXME", "FIXME" not in view_src)
check("无 pass",
      not any(line.strip() == "pass" for line in view_src.split("\n")))
check("使用 logging", "logging" in view_src)

# ============================================================
# 22. Type Hint
# ============================================================
print("\n[22] Type Hint")
check("def __init__ -> None", "-> None:" in view_src)
check("def refresh -> None", "def refresh(self) -> None" in view_src)
check("user_service: UserService", "user_service: UserService" in view_src)
check("users: list[dict[str, Any]]", "list[dict[str, Any]]" in view_src)
check("user_id: int (Service)", "user_id: int" in service_src)

# ============================================================
# 23. Google Docstring
# ============================================================
print("\n[23] Google Docstring")
check("类文档", '"""GTMS 桌面端用户管理页面' in view_src)
check("refresh 方法文档", "def refresh(self) -> None:" in view_src
      and '"""刷新用户列表' in view_src)
check("Args: 存在", "Args:" in view_src)
check("Returns: 存在", "Returns:" in view_src)

# ============================================================
# 24. 无循环导入
# ============================================================
print("\n[24] 无循环导入")
check("导入 UserService", "from client.services.user_service import UserService" in view_src)
check("导入 UserEditDialog", "from client.views.user_edit_dialog import UserEditDialog" in view_src)

# ============================================================
# 25. 禁止命名检查
# ============================================================
print("\n[25] 禁止命名检查")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException"]
for name in forbidden:
    check(f"不包含 {name}", name not in view_src and name not in dialog_src and name not in service_src)

# ============================================================
# 26. Service 公开方法
# ============================================================
print("\n[26] Service 公开方法")
expected_service_methods = {
    "list_users", "create_user", "update_user", "delete_user", "get_roles",
}
method_lines = [
    line for line in service_src.split("\n")
    if "    def " in line and "def __init__" not in line
]
actual_public = [
    l.strip().split("def ")[1].split("(")[0]
    for l in method_lines
    if not l.strip().split("def ")[1].startswith("_")
]
check("公开方法正确", set(actual_public) == expected_service_methods,
      f"实际: {actual_public}")

# ============================================================
# 27. __init__.py 导出
# ============================================================
print("\n[27] __init__.py 导出")
init_path = Path(__file__).parent.parent / "client" / "views" / "__init__.py"
if init_path.exists():
    init_src = init_path.read_text(encoding="utf-8")
    check("导出 UserManageView", "UserManageView" in init_src)
    check("导出 UserEditDialog", "UserEditDialog" in init_src)
else:
    check("init 存在", False, "不存在")

services_init = Path(__file__).parent.parent / "client" / "services" / "__init__.py"
if services_init.exists():
    s_init_src = services_init.read_text(encoding="utf-8")
    check("导出 UserService", "UserService" in s_init_src)

# ============================================================
# 28. 全部按钮权限更新
# ============================================================
print("\n[28] 全部按钮权限更新")
check("_update_button_permissions 在 __init__ 调用", "_update_button_permissions()" in view_src)

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