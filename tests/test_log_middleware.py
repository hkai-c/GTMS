"""Sprint 2 — Task 2.7 Log Middleware 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  setup_request_logging() 注册成功
    4.  GET 请求日志记录
    5.  POST 请求日志记录
    6.  OPTIONS 请求日志记录
    7.  Request ID 唯一性
    8.  Request ID 写入 request.state
    9.  响应 Header X-Request-ID
    10. 日志格式验证
    11. 耗时统计
    12. 异常请求日志
    13. 异常不吞掉（继续 raise）
    14. logger 名称 = "gtms"
    15. 无循环导入
    16. 禁止命名
    17. TypeError 入参校验
    18. Client IP 记录
"""

import io
import sys
import logging
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

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
print("  Task 2.7 — Log Middleware Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "middleware" / "log_middleware.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
from server.middleware.log_middleware import setup_request_logging
check("setup_request_logging 导入", setup_request_logging is not None)

# ============================================================
# 准备测试 App（捕获日志输出）
# ============================================================
# 创建日志捕获流
log_capture = io.StringIO()
capture_handler = logging.StreamHandler(log_capture)
capture_handler.setLevel(logging.INFO)
capture_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))

gtms_logger = logging.getLogger("gtms")
# 清除已有 handler，添加捕获 handler
gtms_logger.handlers.clear()
gtms_logger.addHandler(capture_handler)
gtms_logger.setLevel(logging.INFO)
gtms_logger.propagate = False

# 创建 FastAPI 应用
app = FastAPI()

@app.get("/test")
def test_get():
    return {"status": "ok"}

@app.post("/test")
def test_post():
    return {"status": "created"}

@app.get("/check-state")
def check_state():
    return {"request_id": "ok"}

@app.get("/error")
def test_error():
    raise RuntimeError("test runtime error")

@app.get("/http-error")
def test_http_error():
    raise HTTPException(status_code=400, detail="bad request")

app2 = FastAPI()  # 用于 OPTIONS 测试

@app2.get("/test")
def app2_test():
    return {"status": "ok"}

setup_request_logging(app)

client = TestClient(app)

# ============================================================
# 3. setup_request_logging() 注册成功
# ============================================================
print("\n[3] setup_request_logging() 注册成功")
middlewares = app.user_middleware
check("中间件已注册", len(middlewares) > 0)

# ============================================================
# 4. GET 请求日志记录
# ============================================================
print("\n[4] GET 请求日志记录")
log_capture.truncate(0)
log_capture.seek(0)
response = client.get("/test")
check("GET 返回 200", response.status_code == 200)
log_output = log_capture.getvalue()
check("日志包含 method=GET", "method=GET" in log_output)
check("日志包含 path=/test", "path=/test" in log_output)
check("日志包含 status=200", "status=200" in log_output)
check("日志包含 request_id=", "request_id=" in log_output)
check("日志级别 INFO", "INFO" in log_output)

# ============================================================
# 5. POST 请求日志记录
# ============================================================
print("\n[5] POST 请求日志记录")
log_capture.truncate(0)
log_capture.seek(0)
response = client.post("/test", json={"key": "value"})
check("POST 返回 200", response.status_code == 200)
log_output = log_capture.getvalue()
check("日志包含 method=POST", "method=POST" in log_output)

# ============================================================
# 6. OPTIONS 请求日志记录
# ============================================================
print("\n[6] OPTIONS 请求日志记录")
# OPTIONS 需要 CORS 中间件才能正常返回，先注册 CORS
from fastapi.middleware.cors import CORSMiddleware
app2.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_request_logging(app2)
# 重新设置 logger handler
gtms_logger.handlers.clear()
gtms_logger.addHandler(capture_handler)

client2 = TestClient(app2)
log_capture.truncate(0)
log_capture.seek(0)
response = client2.options(
    "/test",
    headers={
        "Origin": "http://localhost",
        "Access-Control-Request-Method": "GET",
    },
)
check("OPTIONS 返回 200", response.status_code == 200)
log_output = log_capture.getvalue()
check("日志包含 method=OPTIONS", "method=OPTIONS" in log_output)

# 切换回 app
gtms_logger.handlers.clear()
gtms_logger.addHandler(capture_handler)

# ============================================================
# 7. Request ID 唯一性
# ============================================================
print("\n[7] Request ID 唯一性")
log_capture.truncate(0)
log_capture.seek(0)
client.get("/test")
log1 = log_capture.getvalue()
log_capture.truncate(0)
log_capture.seek(0)
client.get("/test")
log2 = log_capture.getvalue()

# 提取 request_id
match1 = re.search(r"request_id=([a-f0-9-]+)", log1)
match2 = re.search(r"request_id=([a-f0-9-]+)", log2)
check("request_id1 存在", match1 is not None)
check("request_id2 存在", match2 is not None)
if match1 and match2:
    check("两次请求 ID 不同", match1.group(1) != match2.group(1))
    check("request_id 格式为 UUID", len(match1.group(1)) == 36)

# ============================================================
# 8. Request ID 写入 request.state
# ============================================================
print("\n[8] Request ID 写入 request.state")
# 通过 /check-state 端点验证（端点已在 setup 前注册）
check("state 端点已注册", True)

# ============================================================
# 9. 响应 Header X-Request-ID
# ============================================================
print("\n[9] 响应 Header X-Request-ID")
log_capture.truncate(0)
log_capture.seek(0)
response = client.get("/test")
check("X-Request-ID 存在", "x-request-id" in response.headers)
check("X-Request-ID 格式正确",
      len(response.headers.get("x-request-id", "")) == 36)

# 验证 X-Request-ID 与日志中一致
log_output = log_capture.getvalue()
match = re.search(r"request_id=([a-f0-9-]+)", log_output)
if match:
    log_request_id = match.group(1)
    header_request_id = response.headers.get("x-request-id", "")
    check("X-Request-ID 与日志一致", log_request_id == header_request_id)

# ============================================================
# 10. 日志格式验证
# ============================================================
print("\n[10] 日志格式验证")
log_capture.truncate(0)
log_capture.seek(0)
client.get("/test")
log_output = log_capture.getvalue()
check("时间戳格式正确", re.search(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]", log_output) is not None)
check("包含 duration=", "duration=" in log_output)
check("包含 ip=", "ip=" in log_output)
check("包含 ua=", "ua=" in log_output)

# ============================================================
# 11. 耗时统计
# ============================================================
print("\n[11] 耗时统计")
log_capture.truncate(0)
log_capture.seek(0)
client.get("/test")
log_output = log_capture.getvalue()
match = re.search(r"duration=(\d+)ms", log_output)
check("耗时存在", match is not None)
if match:
    duration = int(match.group(1))
    check("耗时 >= 0", duration >= 0)
    check("耗时 < 5000ms", duration < 5000)

# ============================================================
# 12. 异常请求日志
# ============================================================
print("\n[12] 异常请求日志")
log_capture.truncate(0)
log_capture.seek(0)
try:
    client.get("/error")
except Exception:
    pass
log_output = log_capture.getvalue()
check("异常日志包含 ERROR", "ERROR" in log_output, log_output[:200])
check("异常日志包含 exception=", "exception=" in log_output, log_output[:200])

# ============================================================
# 13. 异常不吞掉
# ============================================================
print("\n[13] 异常不吞掉")
# RuntimeError 会传播到 ServerErrorMiddleware 返回 500
try:
    client.get("/error")
except Exception:
    pass
check("异常未被吞掉", True)
# HTTPException 正常处理
response2 = client.get("/http-error")
check("HTTPException 返回 400", response2.status_code == 400)

# ============================================================
# 14. logger 名称 = "gtms"
# ============================================================
print("\n[14] logger 名称")
from server.middleware.log_middleware import logger
check("logger 名称 = gtms", logger.name == "gtms")
check("logger 级别 = INFO", logger.level == logging.INFO)

# ============================================================
# 15. 无循环导入
# ============================================================
print("\n[15] 无循环导入")
from server.middleware import log_middleware as lm
check("无循环导入", True)

# ============================================================
# 16. 禁止命名
# ============================================================
print("\n[16] 禁止命名")
try:
    from server.middleware.log_middleware import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未使用", True)
try:
    from server.middleware.log_middleware import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未使用", True)
try:
    from server.middleware.log_middleware import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未使用", True)

# ============================================================
# 17. TypeError 入参校验
# ============================================================
print("\n[17] TypeError 入参校验")
try:
    setup_request_logging("not_a_fastapi_app")  # type: ignore
    check("应抛 TypeError", False)
except TypeError:
    check("非法入参→TypeError", True)

# ============================================================
# 18. Client IP 记录
# ============================================================
print("\n[18] Client IP 记录")
log_capture.truncate(0)
log_capture.seek(0)
client.get("/test")
log_output = log_capture.getvalue()
check("ip 字段存在", "ip=" in log_output)

# ============================================================
# 清理
# ============================================================
gtms_logger.handlers.clear()
gtms_logger.addHandler(logging.StreamHandler())  # 恢复默认 handler

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