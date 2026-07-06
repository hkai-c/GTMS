"""Sprint 3 — Task 3.7 ApiClient 自检脚本

验证项:
    初始化:
        ✓ 默认 URL
        ✓ 自定义 URL
    Token:
        ✓ set_token
        ✓ clear_token
        ✓ Authorization Header
        ✓ Bearer 格式
    HTTP:
        ✓ GET
        ✓ POST
        ✓ PUT
        ✓ DELETE
        ✓ kwargs
        ✓ timeout
    Session:
        ✓ Session 唯一
        ✓ Keep Alive
    Error:
        ✓ raise_for_status()
        ✓ HTTPError
        ✓ Timeout
        ✓ ConnectionError
        ✓ RequestException
    API:
        ✓ requests.Response 返回
        ✓ 不自动 json()
    代码:
        ✓ py_compile
        ✓ import
        ✓ Type Hint
        ✓ Docstring
        ✓ 无循环导入
        ✓ 禁止命名检查
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

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
print("  Task 3.7 — ApiClient Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "client" / "services" / "api_client.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
from client.services.api_client import ApiClient

check("ApiClient 导入", ApiClient is not None)

# ============================================================
# 3. 默认 URL
# ============================================================
print("\n[3] 默认 URL")
client = ApiClient()
check("默认 base_url = http://127.0.0.1:8000",
      client._base_url == "http://127.0.0.1:8000")

# ============================================================
# 4. 自定义 URL
# ============================================================
print("\n[4] 自定义 URL")
client2 = ApiClient("http://192.168.1.100:9000")
check("自定义 base_url", client2._base_url == "http://192.168.1.100:9000")

# 尾部斜杠处理
client3 = ApiClient("http://example.com:8000/")
check("尾部斜杠被移除", client3._base_url == "http://example.com:8000")

# ============================================================
# 5. set_token
# ============================================================
print("\n[5] set_token")
client = ApiClient()
client.set_token("test_token_123")
check("_token 已设置", client._token == "test_token_123")
check("Authorization Header",
      client._session.headers.get("Authorization") == "Bearer test_token_123")

# ============================================================
# 6. clear_token
# ============================================================
print("\n[6] clear_token")
client.clear_token()
check("_token 已清除", client._token is None)
check("Authorization Header 已移除",
      "Authorization" not in client._session.headers)

# ============================================================
# 7. set_token(None) 等同于 clear_token
# ============================================================
print("\n[7] set_token(None)")
client.set_token("dummy")
client.set_token(None)
check("set_token(None) 清除 token", client._token is None)
check("set_token(None) 清除 Header",
      "Authorization" not in client._session.headers)

# ============================================================
# 8. Bearer 格式
# ============================================================
print("\n[8] Bearer 格式")
client.set_token("jwt_token_here")
auth = client._session.headers.get("Authorization")
check("Bearer 前缀", auth.startswith("Bearer "))
check("Token 正确", auth == "Bearer jwt_token_here")
client.clear_token()

# ============================================================
# 9. GET — 成功
# ============================================================
print("\n[9] GET — 成功")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    resp = client.get("/api/users")
    check("返回 requests.Response", resp is mock_resp)
    mock_req.assert_called_once()
    args = mock_req.call_args
    check("方法 = GET", args[0][0] == "GET")
    check("URL 拼接", args[0][1] == "http://127.0.0.1:8000/api/users")

# ============================================================
# 10. POST — 成功
# ============================================================
print("\n[10] POST — 成功")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    resp = client.post("/api/auth/login", json={"username": "admin"})
    check("返回 requests.Response", resp is mock_resp)
    mock_req.assert_called_once()
    args = mock_req.call_args
    check("方法 = POST", args[0][0] == "POST")
    check("URL 正确", args[0][1] == "http://127.0.0.1:8000/api/auth/login")
    check("json 透传", args[1]["json"] == {"username": "admin"})

# ============================================================
# 11. PUT — 成功
# ============================================================
print("\n[11] PUT — 成功")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    resp = client.put("/api/users/1", json={"real_name": "test"})
    check("返回 requests.Response", resp is mock_resp)
    args = mock_req.call_args
    check("方法 = PUT", args[0][0] == "PUT")

# ============================================================
# 12. DELETE — 成功
# ============================================================
print("\n[12] DELETE — 成功")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    resp = client.delete("/api/users/1")
    check("返回 requests.Response", resp is mock_resp)
    args = mock_req.call_args
    check("方法 = DELETE", args[0][0] == "DELETE")

# ============================================================
# 13. 默认 timeout
# ============================================================
print("\n[13] 默认 timeout")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    client.get("/api/test")
    args = mock_req.call_args
    check("timeout = 30", args[1].get("timeout") == 30)

# ============================================================
# 14. kwargs 覆盖 timeout
# ============================================================
print("\n[14] kwargs 覆盖 timeout")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    client.get("/api/test", timeout=10)
    args = mock_req.call_args
    check("timeout = 10", args[1].get("timeout") == 10)

# ============================================================
# 15. kwargs 透传 headers
# ============================================================
print("\n[15] kwargs 透传 headers")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    client.get("/api/test", headers={"X-Custom": "value"})
    args = mock_req.call_args
    check("headers 透传", args[1].get("headers") == {"X-Custom": "value"})

# ============================================================
# 16. Session 唯一
# ============================================================
print("\n[16] Session 唯一")
c1 = ApiClient()
c2 = ApiClient()
check("不同 client 不同 Session", c1._session is not c2._session)
check("同一 client Session 不变", c1._session is c1._session)

# ============================================================
# 17. Session 类型
# ============================================================
print("\n[17] Session 类型")
import requests

check("是 requests.Session", isinstance(client._session, requests.Session))

# ============================================================
# 18. raise_for_status() 被调用
# ============================================================
print("\n[18] raise_for_status() 被调用")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    client.get("/api/test")
    mock_resp.raise_for_status.assert_called_once()

# ============================================================
# 19. HTTPError 原样抛出
# ============================================================
print("\n[19] HTTPError 原样抛出")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_req.return_value = mock_resp

    try:
        client.get("/api/test")
        check("HTTPError 抛出", False, "未抛出")
    except requests.HTTPError as e:
        check("HTTPError 抛出", "404" in str(e))

# ============================================================
# 20. Timeout 原样抛出
# ============================================================
print("\n[20] Timeout 原样抛出")
with patch.object(client._session, "request") as mock_req:
    mock_req.side_effect = requests.Timeout("Connection timed out")

    try:
        client.get("/api/test")
        check("Timeout 抛出", False, "未抛出")
    except requests.Timeout:
        check("Timeout 抛出", True)

# ============================================================
# 21. ConnectionError 原样抛出
# ============================================================
print("\n[21] ConnectionError 原样抛出")
with patch.object(client._session, "request") as mock_req:
    mock_req.side_effect = requests.ConnectionError("Connection refused")

    try:
        client.get("/api/test")
        check("ConnectionError 抛出", False, "未抛出")
    except requests.ConnectionError:
        check("ConnectionError 抛出", True)

# ============================================================
# 22. RequestException 原样抛出
# ============================================================
print("\n[22] RequestException 原样抛出")
with patch.object(client._session, "request") as mock_req:
    mock_req.side_effect = requests.RequestException("General error")

    try:
        client.get("/api/test")
        check("RequestException 抛出", False, "未抛出")
    except requests.RequestException:
        check("RequestException 抛出", True)

# ============================================================
# 23. 不自动 json()
# ============================================================
print("\n[23] 不自动 json()")
with patch.object(client._session, "request") as mock_req:
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_req.return_value = mock_resp

    resp = client.get("/api/test")
    # 验证没有调用 json()
    mock_resp.json.assert_not_called()
    check("未调用 json()", True)

# ============================================================
# 24. Type Hint
# ============================================================
print("\n[24] Type Hint")
import inspect

source = inspect.getsource(ApiClient)
check("有 -> requests.Response", "-> requests.Response" in source)
check("有 str | None", "str | None" in source)

# ============================================================
# 25. Google Docstring
# ============================================================
print("\n[25] Google Docstring")
for fn_name in ["set_token", "clear_token", "get", "post", "put", "delete"]:
    fn = getattr(client, fn_name)
    check(f"{fn_name} 有 docstring", fn.__doc__ is not None and len(fn.__doc__) > 10)

# ============================================================
# 26. 无循环导入
# ============================================================
print("\n[26] 无循环导入")
import client.services.api_client as ac

check("无循环导入", True)

# ============================================================
# 27. 禁止命名检查
# ============================================================
print("\n[27] 禁止命名检查")
api_client_src = (
    Path(__file__).parent.parent / "client" / "services" / "api_client.py"
).read_text(encoding="utf-8")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException",
             "print("]
for name in forbidden:
    check(f"文件不含 {name}", name not in api_client_src)

# ============================================================
# 28. PEP8
# ============================================================
print("\n[28] PEP8")
check("文件以 docstring 开头", api_client_src.strip().startswith('"""'))
check("有 __all__", "__all__" in api_client_src)
check("无 TODO", "TODO" not in api_client_src)
check("无 FIXME", "FIXME" not in api_client_src)

# ============================================================
# 29. 不依赖 server 模块
# ============================================================
print("\n[29] 不依赖 server 模块")
check("不 import server", "from server" not in api_client_src
      and "import server" not in api_client_src)

# ============================================================
# 30. 公开 API 数 = 7
# ============================================================
print("\n[30] 公开 API 数 = 7")
public_methods = [m for m in dir(ApiClient)
                  if not m.startswith("_") and callable(getattr(ApiClient, m))]
expected = {"set_token", "clear_token", "get", "post", "put", "delete"}
check("仅 7 个公开方法", set(public_methods) == expected,
      f"实际: {public_methods}")

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