"""请求日志中间件 (Request Logging Middleware)

Sprint 2 — Task 2.7
严格依据 Development Roadmap.md、CODE_WIKI.md §6.3.1。

使用 FastAPI "@app.middleware("http")" 模式实现请求日志记录。
每个 HTTP 请求自动记录：
    - 请求开始/结束时间、处理耗时(ms)
    - HTTP Method、Request Path、Status Code
    - Client IP、User-Agent
    - Request ID（UUID，同时写入 request.state 和响应 Header X-Request-ID）
    - 异常信息（发生异常时记录 ERROR 级别日志 + Stack Trace）

Logger 名称: "gtms"，默认 INFO 级别，输出到 console。

公开 API:
    setup_request_logging(app: FastAPI) -> None

使用方式:
    from server.middleware.log_middleware import setup_request_logging

    app = FastAPI()
    setup_request_logging(app)
"""

import logging
import time
import traceback
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# ============================================================
# Logger 配置
# ============================================================

logger = logging.getLogger("gtms")
logger.setLevel(logging.INFO)

# 确保至少有一个 console handler（避免重复添加）
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# 阻止日志传播到 root logger（避免重复输出）
logger.propagate = False


# ============================================================
# 公开 API
# ============================================================


def setup_request_logging(app: FastAPI) -> None:
    """在 FastAPI 应用上注册请求日志中间件。

    使用 @app.middleware("http") 模式注册，
    自动记录每个 HTTP 请求的完整日志信息。

    Args:
        app: FastAPI 应用实例。

    Raises:
        TypeError: 如果 app 不是 FastAPI 实例。
    """
    if not isinstance(app, FastAPI):
        raise TypeError(
            f"app 必须是 FastAPI 实例，当前类型: {type(app).__name__}"
        )

    @app.middleware("http")
    async def log_request_middleware(
        request: Request,
        call_next: Callable,
    ) -> Response:
        """记录请求日志的中间件。

        流程:
            1. 生成 Request ID，写入 request.state.request_id
            2. 记录请求开始时间和请求信息
            3. 调用下一个中间件/路由处理
            4. 计算耗时
            5. 记录响应信息（状态码、耗时）
            6. 将 Request ID 写入响应 Header X-Request-ID
            7. 若发生异常，记录 ERROR 日志并重新抛出

        Args:
            request: ASGI 请求对象。
            call_next: 下一个中间件或路由处理函数。

        Returns:
            ASGI 响应对象。
        """
        # 生成 Request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始
        start_time = time.time()
        client_ip = _get_client_ip(request)
        user_agent = request.headers.get("user-agent", "-")

        response = None
        status_code = 0
        error_info = None

        try:
            # 调用下一个处理器
            response = await call_next(request)
            status_code = response.status_code

        except Exception as exc:
            # 记录异常日志
            status_code = 500
            error_info = {
                "exception": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
            # 重新抛出异常，交由全局异常处理器处理
            raise

        finally:
            # 计算耗时
            elapsed = (time.time() - start_time) * 1000  # 转毫秒

            # 构建日志消息
            log_parts = [
                f"request_id={request_id}",
                f"method={request.method}",
                f"path={request.url.path}",
                f"status={status_code}",
                f"duration={elapsed:.0f}ms",
                f"ip={client_ip}",
                f"ua={user_agent}",
            ]

            log_message = " | ".join(log_parts)

            if error_info:
                # 异常日志：ERROR 级别 + Stack Trace
                logger.error(
                    "%s | exception=%s | error=%s\n%s",
                    log_message,
                    error_info["exception"],
                    error_info["message"],
                    error_info["traceback"],
                )
            else:
                # 正常日志：INFO 级别
                logger.info(log_message)

            # 将 Request ID 写入响应 Header
            if response is not None:
                response.headers["X-Request-ID"] = request_id

        return response  # type: ignore[return-value]


# ============================================================
# 私有函数
# ============================================================


def _get_client_ip(request: Request) -> str:
    """获取客户端真实 IP 地址。

    优先从 X-Forwarded-For 头获取（适用于反向代理场景），
    其次使用 X-Real-IP 头，最后使用 request.client.host。

    Args:
        request: ASGI 请求对象。

    Returns:
        客户端 IP 地址字符串。
    """
    # 检查 X-Forwarded-For（取第一个 IP）
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # 检查 X-Real-IP
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    # 直连 IP
    if request.client:
        return request.client.host

    return "unknown"


__all__ = [
    "setup_request_logging",
]