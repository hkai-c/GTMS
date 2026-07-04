"""Sprint 2 — Task 2.9 Global Exception Handler 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  register_exception_handlers() 注册成功
    4.  BusinessLogicException → 400
    5.  AuthenticationException → 401
    6.  PermissionDeniedException → 403
    7.  NotFoundException → 404
    8.  DuplicateException → 409
    9.  HTTPException
    10. RequestValidationError → 422
    11. Exception → 500
    12. JSON 格式 (code/message/detail 三字段)
    13. HTTP Status 正确
    14. code 字段 = HTTP 状态码
    15. message 字段正确
    16. detail 字段正确
    17. traceback 不返回客户端
    18. logger.exception 被调用
    19. OpenAPI 正常
    20. 无循环导入
    禁止命名检查: ValidationException, AuthorizationException, ConflictException
"""

import io
import sys
import logging
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Query
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

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
print("  Task 2.9 — Global Exception Handler Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile

try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "core" / "exception_handlers.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
from server.core.exception_handlers import register_exception_handlers
check("register_exception_handlers 导入", register_exception_handlers is not None)

# 导入异常类
from server.core.exceptions import (
    BaseAppException,
    BusinessLogicException,
    AuthenticationException,
    PermissionDeniedException,
    NotFoundException,
    DuplicateException,
)

# ============================================================
# 准备测试 App
# ============================================================

# 捕获 gtms logger 输出
log_capture = io.StringIO()
capture_handler = logging.StreamHandler(log_capture)
capture_handler.setLevel(logging.DEBUG)
capture_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))

_gtms = logging.getLogger("gtms")
_gtms.handlers.clear()
_gtms.addHandler(capture_handler)
_gtms.setLevel(logging.DEBUG)
_gtms.propagate = False

# 创建测试用 FastAPI app
app = FastAPI()

# 注册异常处理器
register_exception_handlers(app)

# 注册测试路由
@app.get("/biz-error")
def biz_error():
    raise BusinessLogicException("业务逻辑错误", detail="订单状态不允许")

@app.get("/auth-error")
def auth_error():
    raise AuthenticationException("认证失败")

@app.get("/perm-error")
def perm_error():
    raise PermissionDeniedException("权限不足", detail="仅管理员可操作")

@app.get("/not-found")
def not_found():
    raise NotFoundException("任务不存在", detail={"task_id": 999})

@app.get("/dup-error")
def dup_error():
    raise DuplicateException("任务编号重复", detail={"task_no": "20260704-1"})

@app.get("/http-error")
def http_error():
    raise StarletteHTTPException(status_code=404, detail="Not Found")

@app.get("/http-error-400")
def http_error_400():
    raise StarletteHTTPException(status_code=400, detail="Bad Request")

@app.get("/validation-error")
def validation_error(q: int = Query(..., description="必填参数")):
    return {"q": q}

@app.get("/unhandled-error")
def unhandled_error():
    raise RuntimeError("测试运行时错误")

# 额外测试路由 — base exception
@app.get("/base-error")
def base_error():
    raise BaseAppException("基础异常", status_code=418, code="BASE", detail="detail info")

client = TestClient(app, raise_server_exceptions=False)

# ============================================================
# 3. register_exception_handlers() 注册成功
# ============================================================
print("\n[3] register_exception_handlers() 注册成功")
handlers = app.exception_handlers
check("异常处理器已注册", len(handlers) > 0)
check("至少注册 4 个处理器", len(handlers) >= 4,
      f"实际: {len(handlers)}")

# 验证各类异常有对应的 handler
handler_types = {h.__name__ for h in handlers.keys()}
check("BaseAppException 处理器已注册", "BaseAppException" in handler_types,
      f"已注册: {handler_types}")
check("StarletteHTTPException 处理器已注册",
      "HTTPException" in handler_types,
      f"已注册: {handler_types}")
check("RequestValidationError 处理器已注册",
      "RequestValidationError" in handler_types,
      f"已注册: {handler_types}")
check("Exception 处理器已注册",
      "Exception" in handler_types,
      f"已注册: {handler_types}")

# ============================================================
# 4. BusinessLogicException → 400
# ============================================================
print("\n[4] BusinessLogicException → 400")
log_capture.truncate(0)
log_capture.seek(0)
response = client.get("/biz-error")
check("HTTP 400", response.status_code == 400,
      f"实际: {response.status_code}")
data = response.json()
check("code = 400", data.get("code") == 400,
      f"实际: {data.get('code')}")
check("message = 业务逻辑错误", data.get("message") == "业务逻辑错误",
      f"实际: {data.get('message')}")
check("detail 正确", data.get("detail") == "订单状态不允许",
      f"实际: {data.get('detail')}")
# 业务异常不应有 ERROR 日志
log_output = log_capture.getvalue()
check("业务异常无 ERROR 日志", "ERROR" not in log_output,
      f"日志内容: {log_output}")

# ============================================================
# 5. AuthenticationException → 401
# ============================================================
print("\n[5] AuthenticationException → 401")
response = client.get("/auth-error")
check("HTTP 401", response.status_code == 401,
      f"实际: {response.status_code}")
data = response.json()
check("code = 401", data.get("code") == 401)
check("message = 认证失败", data.get("message") == "认证失败")
check("detail 为空", data.get("detail") == "")

# ============================================================
# 6. PermissionDeniedException → 403
# ============================================================
print("\n[6] PermissionDeniedException → 403")
response = client.get("/perm-error")
check("HTTP 403", response.status_code == 403,
      f"实际: {response.status_code}")
data = response.json()
check("code = 403", data.get("code") == 403)
check("message = 权限不足", data.get("message") == "权限不足")
check("detail 正确", data.get("detail") == "仅管理员可操作")

# ============================================================
# 7. NotFoundException → 404
# ============================================================
print("\n[7] NotFoundException → 404")
response = client.get("/not-found")
check("HTTP 404", response.status_code == 404,
      f"实际: {response.status_code}")
data = response.json()
check("code = 404", data.get("code") == 404)
check("message = 任务不存在", data.get("message") == "任务不存在")
# detail 是 dict，转为 str
check("detail 包含 task_id", "task_id" in data.get("detail", ""),
      f"实际: {data.get('detail')}")

# ============================================================
# 8. DuplicateException → 409
# ============================================================
print("\n[8] DuplicateException → 409")
response = client.get("/dup-error")
check("HTTP 409", response.status_code == 409,
      f"实际: {response.status_code}")
data = response.json()
check("code = 409", data.get("code") == 409)
check("message = 任务编号重复", data.get("message") == "任务编号重复")
check("detail 包含 task_no", "task_no" in data.get("detail", ""),
      f"实际: {data.get('detail')}")

# ============================================================
# 9. HTTPException
# ============================================================
print("\n[9] HTTPException")
response = client.get("/http-error")
check("HTTP 404", response.status_code == 404,
      f"实际: {response.status_code}")
data = response.json()
check("code = 404", data.get("code") == 404)
check("message = Not Found", data.get("message") == "Not Found",
      f"实际: {data.get('message')}")
check("detail 为空", data.get("detail") == "")

# HTTPException 400
response = client.get("/http-error-400")
check("HTTP 400", response.status_code == 400)
data = response.json()
check("code = 400", data.get("code") == 400)
check("message = Bad Request", data.get("message") == "Bad Request")

# ============================================================
# 10. RequestValidationError → 422
# ============================================================
print("\n[10] RequestValidationError → 422")
# 不传必填参数 q
response = client.get("/validation-error")
check("HTTP 422", response.status_code == 422,
      f"实际: {response.status_code}")
data = response.json()
check("code = 422", data.get("code") == 422,
      f"实际: {data.get('code')}")
check("message = 请求参数错误", data.get("message") == "请求参数错误",
      f"实际: {data.get('message')}")
check("detail 不为空", len(data.get("detail", "")) > 0,
      f"实际: {data.get('detail')}")

# ============================================================
# 11. Exception → 500
# ============================================================
print("\n[11] Exception → 500")
log_capture.truncate(0)
log_capture.seek(0)
response = client.get("/unhandled-error")
check("HTTP 500", response.status_code == 500,
      f"实际: {response.status_code}")
data = response.json()
check("code = 500", data.get("code") == 500)
check("message = 服务器内部错误", data.get("message") == "服务器内部错误",
      f"实际: {data.get('message')}")
check("detail = Internal Server Error",
      data.get("detail") == "Internal Server Error",
      f"实际: {data.get('detail')}")

# ============================================================
# 12. JSON 格式 (code/message/detail 三字段)
# ============================================================
print("\n[12] JSON 格式")
response = client.get("/not-found")
data = response.json()
check("三字段: code", "code" in data)
check("三字段: message", "message" in data)
check("三字段: detail", "detail" in data)
check("无多余字段", len(data) == 3,
      f"实际字段: {list(data.keys())}")

# 验证各字段类型
check("code 为 int", isinstance(data.get("code"), int))
check("message 为 str", isinstance(data.get("message"), str))
check("detail 为 str", isinstance(data.get("detail"), str))

# ============================================================
# 13. HTTP Status 正确（综合验证）
# ============================================================
print("\n[13] HTTP Status 正确")
status_map = {
    "/biz-error": 400,
    "/auth-error": 401,
    "/perm-error": 403,
    "/not-found": 404,
    "/dup-error": 409,
    "/validation-error": 422,
    "/unhandled-error": 500,
}
for path, expected_status in status_map.items():
    r = client.get(path)
    check(f"{path} → {expected_status}",
          r.status_code == expected_status,
          f"实际: {r.status_code}")

# ============================================================
# 14. code 字段 = HTTP 状态码
# ============================================================
print("\n[14] code 字段 = HTTP 状态码")
for path in status_map:
    r = client.get(path)
    data = r.json()
    check(f"{path} code={data['code']} 匹配 status={r.status_code}",
          data["code"] == r.status_code,
          f"code={data['code']} vs status={r.status_code}")

# ============================================================
# 15. message 字段正确
# ============================================================
print("\n[15] message 字段正确")
check("message 非空 (biz)", len(client.get("/biz-error").json()["message"]) > 0)
check("message 非空 (auth)", len(client.get("/auth-error").json()["message"]) > 0)
check("message 非空 (perm)", len(client.get("/perm-error").json()["message"]) > 0)
check("message 非空 (404)", len(client.get("/not-found").json()["message"]) > 0)
check("message 非空 (409)", len(client.get("/dup-error").json()["message"]) > 0)
check("message 非空 (500)", len(client.get("/unhandled-error").json()["message"]) > 0)

# ============================================================
# 16. detail 字段正确
# ============================================================
print("\n[16] detail 字段正确")
# BaseAppException with detail
r = client.get("/base-error")
check("BaseAppException detail 透传", r.json()["detail"] == "detail info")
# HTTPException detail = ""
r = client.get("/http-error")
check("HTTPException detail 为空", r.json()["detail"] == "")
# 500 detail = "Internal Server Error"
r = client.get("/unhandled-error")
check("500 detail 固定", r.json()["detail"] == "Internal Server Error")

# ============================================================
# 17. traceback 不返回客户端
# ============================================================
print("\n[17] traceback 不返回客户端")
r = client.get("/unhandled-error")
data = r.json()
body = str(data)
check("不含 Traceback", "Traceback" not in body)
check("不含 File", "File \"" not in body)
check("不含 line", "line " not in body)
check("不含 RuntimeError", "RuntimeError" not in body,
      f"实际: {body[:200]}")

# ============================================================
# 18. logger.exception 被调用
# ============================================================
print("\n[18] logger.exception 被调用")
log_capture.truncate(0)
log_capture.seek(0)
client.get("/unhandled-error")
log_output = log_capture.getvalue()
check("未知异常日志含 ERROR", "ERROR" in log_output,
      f"日志: {log_output[:200]}")
check("未知异常日志含 RuntimeError", "RuntimeError" in log_output,
      f"日志: {log_output[:200]}")
check("未知异常日志含 测试运行时错误", "测试运行时错误" in log_output,
      f"日志: {log_output[:200]}")
# 检查包含 traceback（日志中应有，但不应返回客户端）
check("日志包含 Traceback", "Traceback" in log_output,
      f"日志: {log_output[:200]}")

# ============================================================
# 19. OpenAPI 正常
# ============================================================
print("\n[19] OpenAPI 正常")
openapi_schema = app.openapi()
check("OpenAPI schema 生成成功", openapi_schema is not None)
check("openapi 版本 3.x",
      openapi_schema.get("openapi", "").startswith("3."))
check("paths 包含所有测试路由",
      all(f"/{p}" in str(openapi_schema["paths"].keys()) for p in [
          "biz-error", "auth-error", "perm-error", "not-found",
          "dup-error", "http-error", "http-error-400",
          "validation-error", "unhandled-error", "base-error",
      ]),
      f"实际: {list(openapi_schema['paths'].keys())}")

# ============================================================
# 20. 无循环导入
# ============================================================
print("\n[20] 无循环导入")
import server.core.exception_handlers as eh
check("无循环导入", True)

# ============================================================
# 禁止命名检查
# ============================================================
print("\n[21] 禁止命名检查")
forbidden = ["ValidationException", "AuthorizationException", "ConflictException"]
for name in forbidden:
    try:
        getattr(eh, name)
        check(f"{name} 不应存在", False)
    except AttributeError:
        check(f"{name} 未使用", True)

# ============================================================
# TypeError 入参校验
# ============================================================
print("\n[22] TypeError 入参校验")
try:
    register_exception_handlers("not_a_fastapi_app")  # type: ignore
    check("应抛 TypeError", False)
except TypeError:
    check("非法入参→TypeError", True)

# ============================================================
# 清理
# ============================================================
_gtms.handlers.clear()
_gtms.addHandler(logging.StreamHandler())

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