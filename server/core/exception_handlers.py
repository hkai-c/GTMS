"""全局异常处理器 (Global Exception Handler)

Sprint 2 — Task 2.9
严格依据 Development Roadmap.md、CODE_WIKI.md §6.2.3。

统一 FastAPI 全局异常处理，将所有异常转换为统一 JSON 格式：
    {
        "code": <HTTP状态码>,
        "message": "<错误信息>",
        "detail": "<详细说明>"
    }

支持异常类型:
    - BaseAppException 子类 (BusinessLogicException, AuthenticationException,
      PermissionDeniedException, NotFoundException, DuplicateException)
    - HTTPException (FastAPI 自带)
    - RequestValidationError (FastAPI 参数校验)
    - Exception (未知异常)

公开 API:
    register_exception_handlers(app: FastAPI) -> None

使用方式:
    from server.core.exception_handlers import register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)
"""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from server.core.exceptions import BaseAppException

# ============================================================
# Logger 配置
# ============================================================

_logger = logging.getLogger("gtms")


# ============================================================
# JSON 响应构建
# ============================================================


def _build_response(
    status_code: int,
    message: str,
    detail: str = "",
) -> JSONResponse:
    """构建统一 JSON 错误响应。

    Args:
        status_code: HTTP 状态码。
        message: 错误消息。
        detail: 详细说明。

    Returns:
        JSONResponse: 统一格式的 JSON 响应。
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "message": message,
            "detail": detail,
        },
    )


# ============================================================
# 异常处理器
# ============================================================


async def _base_app_exception_handler(
    request: Request,
    exc: BaseAppException,
) -> JSONResponse:
    """处理 BaseAppException 及其子类异常。

    业务异常不打印 traceback，直接返回统一格式。
    HTTP 状态码使用异常自带的 status_code。

    Args:
        request: ASGI 请求对象。
        exc: 业务异常实例。

    Returns:
        JSONResponse: 统一格式的 JSON 响应。
    """
    return _build_response(
        status_code=exc.status_code,
        message=exc.message,
        detail=str(exc.detail) if exc.detail else "",
    )


async def _http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """处理 FastAPI/Starlette HTTPException。

    将 HTTPException 转换为统一 JSON 格式。

    Args:
        request: ASGI 请求对象。
        exc: HTTPException 实例。

    Returns:
        JSONResponse: 统一格式的 JSON 响应。
    """
    return _build_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        detail="",
    )


async def _validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """处理 FastAPI 请求参数校验错误。

    使用 FastAPI 默认错误信息作为 detail。

    Args:
        request: ASGI 请求对象。
        exc: RequestValidationError 实例。

    Returns:
        JSONResponse: 统一格式的 JSON 响应。
    """
    # 提取 FastAPI 默认校验错误信息
    errors: list[dict[str, Any]] = exc.errors()
    detail_str = str(errors) if errors else ""

    return _build_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="请求参数错误",
        detail=detail_str,
    )


async def _unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """处理未知异常。

    记录完整 stack trace 到日志，但不暴露给客户端。
    统一返回 HTTP 500。

    Args:
        request: ASGI 请求对象。
        exc: 未知异常实例。

    Returns:
        JSONResponse: 统一格式的 JSON 响应。
    """
    _logger.exception(
        "未捕获异常 | method=%s | path=%s | exception=%s: %s",
        request.method,
        request.url.path,
        type(exc).__name__,
        str(exc),
    )

    return _build_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="服务器内部错误",
        detail="Internal Server Error",
    )


# ============================================================
# 公开 API
# ============================================================


def register_exception_handlers(app: FastAPI) -> None:
    """在 FastAPI 应用上注册所有全局异常处理器。

    注册顺序即为处理优先级（先注册先匹配）：
        1. BaseAppException 及其子类
        2. Starlette HTTPException
        3. RequestValidationError
        4. 未知 Exception（兜底）

    Args:
        app: FastAPI 应用实例。

    Raises:
        TypeError: 如果 app 不是 FastAPI 实例。
    """
    if not isinstance(app, FastAPI):
        raise TypeError(
            f"app 必须是 FastAPI 实例，当前类型: {type(app).__name__}"
        )

    app.add_exception_handler(
        BaseAppException,
        _base_app_exception_handler,
    )
    app.add_exception_handler(
        StarletteHTTPException,
        _http_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        _validation_exception_handler,
    )
    app.add_exception_handler(
        Exception,
        _unhandled_exception_handler,
    )


__all__ = [
    "register_exception_handlers",
]