"""Sprint 2 — Task 2.6 CORS Middleware 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  setup_cors() 注册成功
    4.  CORSMiddleware 注册成功
    5.  allow_origins 正确
    6.  allow_methods 正确
    7.  allow_headers 正确
    8.  allow_credentials=True
    9.  expose_headers 正确
    10. max_age 正确
    11. OPTIONS 预检请求允许
    12. 非 OPTIONS 请求 CORS 头正确
    13. 非允许 Origin 请求拒绝
    14. 无循环导入
    15. 禁止命名
    16. FastAPI 正常启动
    17. TypeError 入参校验
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

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
print("  Task 2.6 — CORS Middleware Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "middleware" / "cors_middleware.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
from server.middleware.cors_middleware import setup_cors
check("setup_cors 导入", setup_cors is not None)

# ============================================================
# 准备测试 App
# ============================================================
app = FastAPI()

@app.get("/test")
def test_endpoint():
    return {"status": "ok"}

@app.post("/test")
def test_post():
    return {"status": "created"}

setup_cors(app)
client = TestClient(app)

# ============================================================
# 3. setup_cors() 注册成功
# ============================================================
print("\n[3] setup_cors() 注册成功")
middlewares = app.user_middleware
check("中间件已注册", len(middlewares) > 0)

# ============================================================
# 4. CORSMiddleware 注册成功
# ============================================================
print("\n[4] CORSMiddleware 注册成功")
cors_found = False
cors_mw = None
for mw in middlewares:
    if mw.cls == CORSMiddleware:
        cors_found = True
        cors_mw = mw
        break
check("CORSMiddleware 已注册", cors_found)

# ============================================================
# 检查 CORS 中间件配置
# ============================================================
cors_options = cors_mw.options if cors_mw else {}

# ============================================================
# 5. allow_origins 正确
# ============================================================
print("\n[5] allow_origins 正确")
origins = cors_options.get("allow_origins", [])
check("包含 localhost", "http://localhost" in origins)
check("包含 127.0.0.1", "http://127.0.0.1" in origins)
check("包含 Vue Dev Server", "http://localhost:5173" in origins)
check("包含微信开发者工具", "https://servicewechat.com" in origins)

# ============================================================
# 6. allow_methods 正确
# ============================================================
print("\n[6] allow_methods 正确")
methods = cors_options.get("allow_methods", [])
check("包含 GET", "GET" in methods)
check("包含 POST", "POST" in methods)
check("包含 PUT", "PUT" in methods)
check("包含 PATCH", "PATCH" in methods)
check("包含 DELETE", "DELETE" in methods)
check("包含 OPTIONS", "OPTIONS" in methods)

# ============================================================
# 7. allow_headers 正确
# ============================================================
print("\n[7] allow_headers 正确")
headers = cors_options.get("allow_headers", [])
check("包含 Authorization", "Authorization" in headers)
check("包含 Content-Type", "Content-Type" in headers)
check("包含 Accept", "Accept" in headers)
check("包含 Origin", "Origin" in headers)
check("包含 X-Requested-With", "X-Requested-With" in headers)

# ============================================================
# 8. allow_credentials=True
# ============================================================
print("\n[8] allow_credentials=True")
check("allow_credentials=True", cors_options.get("allow_credentials") is True)

# ============================================================
# 9. expose_headers 正确
# ============================================================
print("\n[9] expose_headers 正确")
expose = cors_options.get("expose_headers", [])
check("包含 Authorization", "Authorization" in expose)

# ============================================================
# 10. max_age 正确
# ============================================================
print("\n[10] max_age 正确")
check("max_age=600", cors_options.get("max_age") == 600)

# ============================================================
# 11. OPTIONS 预检请求允许
# ============================================================
print("\n[11] OPTIONS 预检请求允许")
response = client.options(
    "/test",
    headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Authorization",
    },
)
check("OPTIONS 返回 200", response.status_code == 200)
check("Access-Control-Allow-Origin 正确",
      response.headers.get("access-control-allow-origin") == "http://localhost:5173")
check("Access-Control-Allow-Methods 存在",
      "access-control-allow-methods" in response.headers)
check("Access-Control-Allow-Credentials",
      response.headers.get("access-control-allow-credentials") == "true")
check("Access-Control-Max-Age",
      response.headers.get("access-control-max-age") == "600")

# ============================================================
# 12. 非 OPTIONS 请求 CORS 头正确
# ============================================================
print("\n[12] GET 请求 CORS 头正确")
response = client.get(
    "/test",
    headers={"Origin": "http://localhost:3000"},
)
check("GET 返回 200", response.status_code == 200)
check("Access-Control-Allow-Origin 正确",
      response.headers.get("access-control-allow-origin") == "http://localhost:3000")
check("Access-Control-Allow-Credentials",
      response.headers.get("access-control-allow-credentials") == "true")
check("Access-Control-Expose-Headers",
      "authorization" in response.headers.get("access-control-expose-headers", "").lower())

# ============================================================
# 13. 非允许 Origin 请求拒绝
# ============================================================
print("\n[13] 非允许 Origin 请求")
response = client.get(
    "/test",
    headers={"Origin": "http://evil.com"},
)
# CORSMiddleware 默认行为：不匹配的 Origin 不返回 CORS 头
check("非允许 Origin 无 CORS 头",
      "access-control-allow-origin" not in response.headers)

# ============================================================
# 14. 无循环导入
# ============================================================
print("\n[14] 无循环导入")
from server.middleware import cors_middleware as cm
check("无循环导入", True)

# ============================================================
# 15. 禁止命名
# ============================================================
print("\n[15] 禁止命名")
try:
    from server.middleware.cors_middleware import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未使用", True)
try:
    from server.middleware.cors_middleware import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未使用", True)
try:
    from server.middleware.cors_middleware import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未使用", True)

# ============================================================
# 16. FastAPI 正常启动
# ============================================================
print("\n[16] FastAPI 正常启动")
check("TestClient 可用", client is not None)
check("app 路由可用", len(app.routes) > 0)

# ============================================================
# 17. TypeError 入参校验
# ============================================================
print("\n[17] TypeError 入参校验")
try:
    setup_cors("not_a_fastapi_app")  # type: ignore
    check("应抛 TypeError", False)
except TypeError:
    check("非法入参→TypeError", True)

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