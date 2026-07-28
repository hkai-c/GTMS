"""GTMS FastAPI 应用入口 (Application Entry)

Sprint 2 — Task 2.8
严格依据 Development Roadmap.md、CODE_WIKI.md §6.1。

启动流程:
    ① 创建 FastAPI 实例
    ② 注册 CORS 中间件 (Task 2.6)
    ③ 注册请求日志中间件 (Task 2.7)
    ④ 注册全局异常处理器 (Task 2.9)
    ⑤ 注册路由 (Sprint 3)
    ⑥ 注册健康检查路由
    ⑦ 启动后台调度器 (Sprint 13 — Task 13.2)

启动方式:
    uvicorn server.main:app --reload

访问:
    http://localhost:8000/docs     — Swagger UI
    http://localhost:8000/redoc    — ReDoc
    http://localhost:8000/health   — 健康检查
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from server.core.exception_handlers import register_exception_handlers
from server.middleware.cors_middleware import setup_cors
from server.middleware.log_middleware import setup_request_logging
from server.routers.auth_router import router as auth_router
from server.routers.customer_router import router as customer_router
from server.routers.dispatch_router import router as dispatch_router
from server.routers.query_router import router as query_router
from server.routers.log_router import router as log_router
from server.routers.receipt_router import router as receipt_router
from server.routers.role_router import router as role_router
from server.routers.trial_task_router import router as trial_task_router
from server.routers.upload_router import router as upload_router
from server.routers.user_router import router as user_router
from server.routers.notification_router import router as notification_router
from server.routers.settings_router import router as settings_router
from server.scheduler import start_scheduler

# ============================================================
# ① 创建 FastAPI 实例
# ============================================================

app = FastAPI(
    title="GTMS API",
    version="1.0.0-rc1",
    description="Grinding Trial Management System API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================================
# ② 注册 CORS 中间件
# ============================================================

setup_cors(app)

# ============================================================
# ③ 注册请求日志中间件
# ============================================================

setup_request_logging(app)

# ============================================================
# ④ 注册全局异常处理器
# ============================================================

register_exception_handlers(app)

# ============================================================
# ⑤ 注册路由
# ============================================================

app.include_router(auth_router)
app.include_router(customer_router)
app.include_router(dispatch_router)
app.include_router(query_router)
app.include_router(log_router)
app.include_router(receipt_router)
app.include_router(role_router)
app.include_router(trial_task_router)
app.include_router(upload_router)
app.include_router(user_router)
app.include_router(notification_router)
app.include_router(settings_router)

# ============================================================
# ⑥ 健康检查路由
# ============================================================


@app.get("/")
async def root() -> JSONResponse:
    """根路由 — 返回 API 基本信息。

    Returns:
        JSONResponse: 包含 message 和 version 的 JSON 响应。
    """
    return JSONResponse(
        content={
            "message": "GTMS API Running",
            "version": "1.0.0-rc1",
        },
    )


@app.get("/health")
async def health_check() -> JSONResponse:
    """健康检查路由。

    Returns:
        JSONResponse: status=ok, HTTP 200。
    """
    return JSONResponse(
        content={"status": "ok"},
    )


# ============================================================
# ⑦ 启动后台调度器
# ============================================================

start_scheduler()


# ============================================================
# 开发模式直接启动
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )