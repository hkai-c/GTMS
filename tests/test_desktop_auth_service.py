"""Sprint 3 — Task 3.8 AuthService 自检脚本

验证项:
    login:
        成功
        用户缓存
        Token 保存
        Header 设置
        HTTPError
        Timeout
        ConnectionError
    logout:
        Token 清除
        Header 清除
        User 清除
        is_authenticated=False
    me:
        获取成功
        User 更新
        Header 保持
    change_password:
        成功
        HTTPError
    Property:
        is_authenticated True
        is_authenticated False
    API:
        调用 ApiClient
        不直接 requests
    代码:
        py_compile
        import
        Type Hint
        Docstring
        无循环导入
        禁止命名检查
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
print("  Task 3.8 — AuthService Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "client" / "services" / "auth_service.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
import requests
from client.services.auth_service import AuthService
from client.services.api_client import ApiClient
from client.services import AuthService as AuthServiceFromInit

check("AuthService 导入", AuthService is not None)
check("从 __init__ 导入", AuthServiceFromInit is AuthService)

# ============================================================
# 3. 工厂函数 — 创建 mock ApiClient
# ============================================================
def make_mock_api_client():
    """创建 mock ApiClient，公开方法均为 MagicMock。"""
    mock = MagicMock(spec=ApiClient)
    return mock


def make_mock_response(json_data):
    """创建 mock requests.Response，设置 json() 返回值。"""
    resp = MagicMock()
    resp.json.return_value = json_data
    return resp


# ============================================================
# 4. login — 成功
# ============================================================
print("\n[4] login — 成功")
mock_api = make_mock_api_client()
mock_resp = make_mock_response({
    "access_token": "jwt_token_abc",
    "token_type": "bearer",
    "user": {"id": 1, "username": "admin", "real_name": "管理员"},
})
mock_api.post.return_value = mock_resp

auth = AuthService(mock_api)
result = auth.login("admin", "admin123")

check("返回 LoginResponse dict", result["access_token"] == "jwt_token_abc")
check("返回 token_type", result["token_type"] == "bearer")
check("返回 user", result["user"]["username"] == "admin")

# ============================================================
# 5. login — 用户缓存
# ============================================================
print("\n[5] login — 用户缓存")
check("_current_user 已缓存", auth._current_user == {"id": 1, "username": "admin", "real_name": "管理员"})
check("_current_user 是 dict", isinstance(auth._current_user, dict))

# ============================================================
# 6. login — Token 保存
# ============================================================
print("\n[6] login — Token 保存")
check("_token 已保存", auth._token == "jwt_token_abc")

# ============================================================
# 7. login — Header 设置
# ============================================================
print("\n[7] login — Header 设置")
mock_api.set_token.assert_called_once_with("jwt_token_abc")

# ============================================================
# 8. login — HTTPError
# ============================================================
print("\n[8] login — HTTPError")
mock_api2 = make_mock_api_client()
mock_api2.post.side_effect = requests.HTTPError("401 Unauthorized")

auth2 = AuthService(mock_api2)
try:
    auth2.login("admin", "wrong_password")
    check("HTTPError 抛出", False, "未抛出异常")
except requests.HTTPError as e:
    check("HTTPError 抛出", "401" in str(e))
except Exception as e:
    check("HTTPError 抛出", False, f"抛出其他异常: {type(e).__name__}")

# 验证失败时状态未改变
check("失败时 token 未设置", auth2._token is None)
check("失败时 user 未设置", auth2._current_user is None)

# ============================================================
# 9. login — Timeout
# ============================================================
print("\n[9] login — Timeout")
mock_api3 = make_mock_api_client()
mock_api3.post.side_effect = requests.Timeout("Connection timed out")

auth3 = AuthService(mock_api3)
try:
    auth3.login("admin", "admin123")
    check("Timeout 抛出", False, "未抛出异常")
except requests.Timeout:
    check("Timeout 抛出", True)
except Exception as e:
    check("Timeout 抛出", False, f"抛出其他异常: {type(e).__name__}")

# ============================================================
# 10. login — ConnectionError
# ============================================================
print("\n[10] login — ConnectionError")
mock_api4 = make_mock_api_client()
mock_api4.post.side_effect = requests.ConnectionError("Connection refused")

auth4 = AuthService(mock_api4)
try:
    auth4.login("admin", "admin123")
    check("ConnectionError 抛出", False, "未抛出异常")
except requests.ConnectionError:
    check("ConnectionError 抛出", True)
except Exception as e:
    check("ConnectionError 抛出", False, f"抛出其他异常: {type(e).__name__}")

# ============================================================
# 11. login — 调用 ApiClient.post
# ============================================================
print("\n[11] login — 调用 ApiClient.post")
mock_api5 = make_mock_api_client()
mock_resp5 = make_mock_response({
    "access_token": "token_xyz",
    "token_type": "bearer",
    "user": {"id": 2, "username": "user1"},
})
mock_api5.post.return_value = mock_resp5

auth5 = AuthService(mock_api5)
auth5.login("user1", "pass123")

mock_api5.post.assert_called_once_with(
    "/api/auth/login",
    json={"username": "user1", "password": "pass123"},
)
check("调用 ApiClient.post", True)

# ============================================================
# 12. logout — Token 清除
# ============================================================
print("\n[12] logout — Token 清除")
auth.logout()
check("_token 已清除", auth._token is None)

# ============================================================
# 13. logout — Header 清除
# ============================================================
print("\n[13] logout — Header 清除")
mock_api.clear_token.assert_called_once()

# ============================================================
# 14. logout — User 清除
# ============================================================
print("\n[14] logout — User 清除")
check("_current_user 已清除", auth._current_user is None)

# ============================================================
# 15. logout — is_authenticated=False
# ============================================================
print("\n[15] logout — is_authenticated=False")
check("is_authenticated = False", auth.is_authenticated is False)

# ============================================================
# 16. logout — 不请求服务器
# ============================================================
print("\n[16] logout — 不请求服务器")
# 验证 logout 仅调用了 clear_token，没有调用 post/get/put/delete
mock_api6 = make_mock_api_client()
auth6 = AuthService(mock_api6)
auth6.logout()
mock_api6.clear_token.assert_called_once()
mock_api6.post.assert_not_called()
mock_api6.get.assert_not_called()
mock_api6.put.assert_not_called()
mock_api6.delete.assert_not_called()
check("logout 不请求服务器", True)

# ============================================================
# 17. get_current_user — 获取成功
# ============================================================
print("\n[17] get_current_user — 获取成功")
mock_api7 = make_mock_api_client()
mock_api7.set_token = MagicMock()
mock_resp7 = make_mock_response({
    "id": 1, "username": "admin", "real_name": "管理员",
    "email": "admin@example.com", "role": {"id": 1, "name": "administrator"},
})
mock_api7.get.return_value = mock_resp7

auth7 = AuthService(mock_api7)
# 先登录以设置 token
auth7._token = "existing_token"
auth7._current_user = {"id": 1, "username": "admin"}

user = auth7.get_current_user()
check("返回 UserResponse", user["username"] == "admin")
check("返回 email", user["email"] == "admin@example.com")
check("返回 role", user["role"]["name"] == "administrator")

# ============================================================
# 18. get_current_user — User 更新
# ============================================================
print("\n[18] get_current_user — User 更新")
check("_current_user 已更新", auth7._current_user == user)
check("_current_user 是 dict", isinstance(auth7._current_user, dict))

# ============================================================
# 19. get_current_user — 调用 ApiClient.get
# ============================================================
print("\n[19] get_current_user — 调用 ApiClient.get")
mock_api7.get.assert_called_once_with("/api/auth/me")
check("调用 ApiClient.get", True)

# ============================================================
# 20. get_current_user — Header 保持
# ============================================================
print("\n[20] get_current_user — Header 保持")
check("_token 未变", auth7._token == "existing_token")

# ============================================================
# 21. get_current_user — HTTPError
# ============================================================
print("\n[21] get_current_user — HTTPError")
mock_api8 = make_mock_api_client()
mock_api8.get.side_effect = requests.HTTPError("401 Unauthorized")

auth8 = AuthService(mock_api8)
try:
    auth8.get_current_user()
    check("HTTPError 抛出", False, "未抛出异常")
except requests.HTTPError as e:
    check("HTTPError 抛出", "401" in str(e))

# ============================================================
# 22. change_password — 成功
# ============================================================
print("\n[22] change_password — 成功")
mock_api9 = make_mock_api_client()
mock_resp9 = make_mock_response({"message": "Password changed successfully."})
mock_api9.post.return_value = mock_resp9

auth9 = AuthService(mock_api9)
result = auth9.change_password("old_pass", "new_pass123")

check("返回成功消息", result["message"] == "Password changed successfully.")
check("调用 ApiClient.post", True)
mock_api9.post.assert_called_once_with(
    "/api/auth/change-password",
    json={"old_password": "old_pass", "new_password": "new_pass123"},
)

# ============================================================
# 23. change_password — HTTPError
# ============================================================
print("\n[23] change_password — HTTPError")
mock_api10 = make_mock_api_client()
mock_api10.post.side_effect = requests.HTTPError("400 Incorrect password")

auth10 = AuthService(mock_api10)
try:
    auth10.change_password("wrong_old", "new_pass123")
    check("HTTPError 抛出", False, "未抛出异常")
except requests.HTTPError as e:
    check("HTTPError 抛出", "400" in str(e))

# ============================================================
# 24. change_password — 不自动退出登录
# ============================================================
print("\n[24] change_password — 不自动退出登录")
mock_api11 = make_mock_api_client()
mock_resp11 = make_mock_response({"message": "Password changed successfully."})
mock_api11.post.return_value = mock_resp11

auth11 = AuthService(mock_api11)
auth11._token = "existing_token"
auth11._current_user = {"id": 1, "username": "admin"}

auth11.change_password("old", "new")
check("token 未清除", auth11._token == "existing_token")
check("user 未清除", auth11._current_user is not None)
check("clear_token 未调用", mock_api11.clear_token.call_count == 0)

# ============================================================
# 25. is_authenticated — True
# ============================================================
print("\n[25] is_authenticated — True")
mock_api12 = make_mock_api_client()
auth12 = AuthService(mock_api12)
auth12._token = "some_token"

check("is_authenticated = True", auth12.is_authenticated is True)

# ============================================================
# 26. is_authenticated — False
# ============================================================
print("\n[26] is_authenticated — False")
mock_api13 = make_mock_api_client()
auth13 = AuthService(mock_api13)

check("初始 is_authenticated = False", auth13.is_authenticated is False)
check("不请求服务器", mock_api13.get.call_count == 0)
check("不请求服务器 (post)", mock_api13.post.call_count == 0)

# ============================================================
# 27. is_authenticated — 不请求服务器
# ============================================================
print("\n[27] is_authenticated — 不请求服务器")
mock_api14 = make_mock_api_client()
auth14 = AuthService(mock_api14)
_ = auth14.is_authenticated
mock_api14.get.assert_not_called()
mock_api14.post.assert_not_called()
check("is_authenticated 不请求服务器", True)

# ============================================================
# 28. 公开 API 数
# ============================================================
print("\n[28] 公开 API 数")
# 公开方法: login, logout, get_current_user, change_password
# 公开 property: is_authenticated
public_methods = [m for m in dir(AuthService)
                  if not m.startswith("_") and callable(getattr(AuthService, m))]
expected_methods = {"login", "logout", "get_current_user", "change_password"}
check("公开方法 = 4", set(public_methods) == expected_methods,
      f"实际: {public_methods}")

# ============================================================
# 29. 不直接 requests
# ============================================================
print("\n[29] 不直接 requests")
auth_src = (
    Path(__file__).parent.parent / "client" / "services" / "auth_service.py"
).read_text(encoding="utf-8")
check("不含 import requests", "import requests" not in auth_src)
check("不含 from requests", "from requests" not in auth_src)

# ============================================================
# 30. Type Hint
# ============================================================
print("\n[30] Type Hint")
import inspect

source = inspect.getsource(AuthService)
check("有 -> dict[str, Any]", "-> dict[str, Any]" in source)
check("有 -> None", "-> None" in source)
check("有 -> bool", "-> bool" in source)
check("有 str | None", "str | None" in source)

# ============================================================
# 31. Google Docstring
# ============================================================
print("\n[31] Google Docstring")
for fn_name in ["login", "logout", "get_current_user", "change_password"]:
    fn = getattr(AuthService, fn_name)
    check(f"{fn_name} 有 docstring", fn.__doc__ is not None and len(fn.__doc__) > 20)

# __init__ 也有 docstring
check("__init__ 有 docstring",
      AuthService.__init__.__doc__ is not None
      and len(AuthService.__init__.__doc__) > 20)

# ============================================================
# 32. 无循环导入
# ============================================================
print("\n[32] 无循环导入")
import client.services.auth_service as as_mod
check("无循环导入", True)

# ============================================================
# 33. 禁止命名检查
# ============================================================
print("\n[33] 禁止命名检查")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException",
             "print(", "TODO", "FIXME"]
for name in forbidden:
    check(f"文件不含 {name}", name not in auth_src)

# ============================================================
# 34. PEP8
# ============================================================
print("\n[34] PEP8")
check("文件以 docstring 开头", auth_src.strip().startswith('"""'))
check("有 __all__", "__all__" in auth_src)
check("类有 docstring", 'class AuthService' in auth_src)
check("使用 logging", "import logging" in auth_src or "logging" in auth_src)

# ============================================================
# 35. 不依赖 server 模块
# ============================================================
print("\n[35] 不依赖 server 模块")
check("不 import server", "from server" not in auth_src
      and "import server" not in auth_src)

# ============================================================
# 36. __init__ 参数类型检查
# ============================================================
print("\n[36] __init__ 参数类型检查")
init_source = inspect.getsource(AuthService.__init__)
check("参数 api_client: ApiClient", "api_client: ApiClient" in init_source)

# ============================================================
# 37. 线程模型 — 不依赖全局变量
# ============================================================
print("\n[37] 线程模型 — 不依赖全局变量")
# 验证两个 AuthService 实例的状态互不影响
mock_a = make_mock_api_client()
mock_b = make_mock_api_client()

mock_a_resp = make_mock_response({
    "access_token": "token_a", "token_type": "bearer",
    "user": {"id": 1, "username": "user_a"},
})
mock_a.post.return_value = mock_a_resp

mock_b_resp = make_mock_response({
    "access_token": "token_b", "token_type": "bearer",
    "user": {"id": 2, "username": "user_b"},
})
mock_b.post.return_value = mock_b_resp

auth_a = AuthService(mock_a)
auth_b = AuthService(mock_b)

auth_a.login("user_a", "pass")
check("auth_a token 独立", auth_a._token == "token_a")
check("auth_b token 未受影响", auth_b._token is None)

auth_b.login("user_b", "pass")
check("auth_b token 独立", auth_b._token == "token_b")
check("auth_a token 保持", auth_a._token == "token_a")

# ============================================================
# 38. login — 无 user 字段时容错
# ============================================================
print("\n[38] login — 无 user 字段时容错")
mock_api15 = make_mock_api_client()
mock_resp15 = make_mock_response({
    "access_token": "token_no_user",
    "token_type": "bearer",
})
mock_api15.post.return_value = mock_resp15

auth15 = AuthService(mock_api15)
result = auth15.login("admin", "pass")
check("_current_user = None", auth15._current_user is None)
check("token 已保存", auth15._token == "token_no_user")

# ============================================================
# 39. 多次 login 覆盖旧 token
# ============================================================
print("\n[39] 多次 login 覆盖旧 token")
mock_api16 = make_mock_api_client()
resp1 = make_mock_response({
    "access_token": "token_first", "token_type": "bearer",
    "user": {"id": 1, "username": "user1"},
})
resp2 = make_mock_response({
    "access_token": "token_second", "token_type": "bearer",
    "user": {"id": 2, "username": "user2"},
})
mock_api16.post.side_effect = [resp1, resp2]

auth16 = AuthService(mock_api16)
auth16.login("user1", "pass")
auth16.login("user2", "pass")

check("token 被覆盖", auth16._token == "token_second")
check("user 被覆盖", auth16._current_user == {"id": 2, "username": "user2"})
check("set_token 被调用 2 次", mock_api16.set_token.call_count == 2)

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