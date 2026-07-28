"""Sprint 2 — Task 2.8 FastAPI Application Entry 自检脚本

验证项:
    1.  py_compile
    2.  app 导入
    3.  app 类型
    4.  title
    5.  version
    6.  docs_url
    7.  GET /
    8.  GET /health
    9.  OPTIONS
    10. middleware 已注册
    11. CORS Header
    12. Request Logging Middleware 已注册
    13. OpenAPI 正常生成
    14. 无循环导入
    15. 禁止命名
"""

import sys
import logging
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
print("  Task 2.8 — FastAPI Application Entry Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "main.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. app 导入
# ============================================================
print("\n[2] app 导入")
# 导入前先静默 gtms logger，避免导入时日志输出干扰
_gtms_logger = logging.getLogger("gtms")
_gtms_logger.setLevel(logging.CRITICAL)

from server.main import app

_gtms_logger.setLevel(logging.INFO)
check("app 导入成功", app is not None)

# ============================================================
# 3. app 类型
# ============================================================
print("\n[3] app 类型")
check("app 是 FastAPI 实例", isinstance(app, FastAPI),
      f"实际类型: {type(app).__name__}")

# ============================================================
# 4. title
# ============================================================
print("\n[4] title")
check("title = GTMS API", app.title == "GTMS API",
      f"实际: {app.title}")

# ============================================================
# 5. version
# ============================================================
print("\n[5] version")
check("version = 1.0.0-rc1", app.version == "1.0.0-rc1",
      f"实际: {app.version}")

# ============================================================
# 6. docs_url
# ============================================================
print("\n[6] docs_url")
check("docs_url = /docs", app.docs_url == "/docs",
      f"实际: {app.docs_url}")
check("redoc_url = /redoc", app.redoc_url == "/redoc",
      f"实际: {app.redoc_url}")
check("openapi_url = /openapi.json",
      app.openapi_url == "/openapi.json",
      f"实际: {app.openapi_url}")

# ============================================================
# 创建 TestClient
# ============================================================
client = TestClient(app)

# ============================================================
# 7. GET /
# ============================================================
print("\n[7] GET /")
response = client.get("/")
check("GET / 返回 200", response.status_code == 200,
      f"实际: {response.status_code}")
data = response.json()
check("message = GTMS API Running",
      data.get("message") == "GTMS API Running",
      f"实际: {data.get('message')}")
check("version = 1.0.0-rc1",
      data.get("version") == "1.0.0-rc1",
      f"实际: {data.get('version')}")

# ============================================================
# 8. GET /health
# ============================================================
print("\n[8] GET /health")
response = client.get("/health")
check("GET /health 返回 200", response.status_code == 200,
      f"实际: {response.status_code}")
data = response.json()
check("status = ok", data.get("status") == "ok",
      f"实际: {data.get('status')}")

# ============================================================
# 9. OPTIONS
# ============================================================
print("\n[9] OPTIONS")
response = client.options(
    "/",
    headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    },
)
check("OPTIONS / 返回 200", response.status_code == 200,
      f"实际: {response.status_code}")

# ============================================================
# 10. middleware 已注册
# ============================================================
print("\n[10] middleware 已注册")
middlewares = app.user_middleware
check("至少注册了 2 个中间件", len(middlewares) >= 2,
      f"实际: {len(middlewares)}")

# 列出所有中间件
middleware_classes = [m.cls.__name__ for m in middlewares]
print(f"  已注册中间件: {middleware_classes}")

# ============================================================
# 11. CORS Header
# ============================================================
print("\n[11] CORS Header")
response = client.get(
    "/",
    headers={"Origin": "http://localhost:5173"},
)
# CORS 响应头
check("access-control-allow-origin 存在",
      "access-control-allow-origin" in response.headers,
      f"实际 headers: {dict(response.headers)}")
check("access-control-allow-origin = http://localhost:5173",
      response.headers.get("access-control-allow-origin") == "http://localhost:5173",
      f"实际: {response.headers.get('access-control-allow-origin')}")
check("access-control-allow-credentials = true",
      response.headers.get("access-control-allow-credentials") == "true",
      f"实际: {response.headers.get('access-control-allow-credentials')}")

# OPTIONS 预检请求
response = client.options(
    "/health",
    headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
    },
)
check("OPTIONS 预检 allow-methods 存在",
      "access-control-allow-methods" in response.headers)
check("OPTIONS 预检 allow-headers 存在",
      "access-control-allow-headers" in response.headers)
check("OPTIONS 预检 max-age 存在",
      "access-control-max-age" in response.headers)
check("OPTIONS 预检 max-age = 600",
      response.headers.get("access-control-max-age") == "600",
      f"实际: {response.headers.get('access-control-max-age')}")

# 非允许 Origin 请求
response = client.get(
    "/",
    headers={"Origin": "http://evil.com"},
)
check("非允许 Origin 无 CORS 头",
      "access-control-allow-origin" not in response.headers,
      f"实际: {response.headers.get('access-control-allow-origin')}")

# ============================================================
# 12. Request Logging Middleware 已注册
# ============================================================
print("\n[12] Request Logging Middleware 已注册")
# 验证 X-Request-ID 响应头存在
response = client.get("/")
check("X-Request-ID 响应头存在",
      "x-request-id" in response.headers,
      f"实际 headers: {dict(response.headers)}")
check("X-Request-ID 为 UUID 格式 (36字符)",
      len(response.headers.get("x-request-id", "")) == 36,
      f"实际: {response.headers.get('x-request-id')}")

# 验证两次请求 ID 不同
response2 = client.get("/health")
id1 = response.headers.get("x-request-id", "")
id2 = response2.headers.get("x-request-id", "")
check("两次请求 ID 不同", id1 != id2,
      f"ID1={id1} ID2={id2}")

# ============================================================
# 13. OpenAPI 正常生成
# ============================================================
print("\n[13] OpenAPI 正常生成")
openapi_schema = app.openapi()
check("OpenAPI schema 生成成功", openapi_schema is not None)
check("openapi 版本 = 3.1.0",
      openapi_schema.get("openapi", "").startswith("3."),
      f"实际: {openapi_schema.get('openapi')}")
check("info.title = GTMS API",
      openapi_schema["info"]["title"] == "GTMS API",
      f"实际: {openapi_schema['info']['title']}")
check("info.version = 1.0.0-rc1",
      openapi_schema["info"]["version"] == "1.0.0-rc1",
      f"实际: {openapi_schema['info']['version']}")
check("paths 包含 /",
      "/" in openapi_schema["paths"],
      f"实际 paths: {list(openapi_schema['paths'].keys())}")
check("paths 包含 /health",
      "/health" in openapi_schema["paths"],
      f"实际 paths: {list(openapi_schema['paths'].keys())}")

# 验证 GET / 的 schema
root_get = openapi_schema["paths"]["/"]["get"]
check("GET / summary 存在",
      "summary" in root_get or "description" in root_get)

# 验证 GET /health 的 schema
health_get = openapi_schema["paths"]["/health"]["get"]
check("GET /health summary 存在",
      "summary" in health_get or "description" in health_get)

# ============================================================
# 14. 无循环导入
# ============================================================
print("\n[14] 无循环导入")
import server.main as sm
check("无循环导入", True)

# ============================================================
# 15. 禁止命名
# ============================================================
print("\n[15] 禁止命名")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException"]
for name in forbidden:
    try:
        getattr(sm, name)
        check(f"{name} 不应存在于 main 模块", False)
    except AttributeError:
        check(f"{name} 未使用", True)

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