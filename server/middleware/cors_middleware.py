"""CORS 中间件 (CORS Middleware)

Sprint 2 — Task 2.6
严格依据 Development Roadmap.md、CODE_WIKI.md §6。

采用 FastAPI 官方 CORSMiddleware 进行统一 CORS 配置。
唯一公开函数 setup_cors(app) 用于注册 CORS 中间件。

配置规则:
    - 允许的源: localhost, 127.0.0.1, Vue Dev Server, 微信开发者工具, 预留生产域名
    - 允许的方法: GET, POST, PUT, PATCH, DELETE, OPTIONS
    - 允许的请求头: Authorization, Content-Type, Accept, Origin, X-Requested-With
    - 允许携带凭证 (Credentials)
    - 暴露 Authorization 响应头
    - 预检请求缓存 600 秒

使用方式:
    from server.middleware.cors_middleware import setup_cors

    app = FastAPI()
    setup_cors(app)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# 配置常量
# ============================================================

# 允许的源（Origin）列表
# 包含开发环境及生产环境预留域名
_ALLOW_ORIGINS: list[str] = [
    # 本地开发
    "http://localhost",
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost:5173",   # Vite 默认端口
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    # Vue Dev Server
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    # 微信开发者工具
    "https://servicewechat.com",
    # 预留生产域名
    # 后续部署时在此添加实际生产域名
]

# 允许的 HTTP 方法
_ALLOW_METHODS: list[str] = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# 允许的请求头
_ALLOW_HEADERS: list[str] = [
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-Requested-With",
]

# 暴露的响应头
_EXPOSE_HEADERS: list[str] = [
    "Authorization",
]

# 预检请求缓存时间（秒）
_MAX_AGE: int = 600


# ============================================================
# 公开 API
# ============================================================


def setup_cors(app: FastAPI) -> None:
    """在 FastAPI 应用上注册 CORS 中间件。

    将 CORS 配置集中应用于指定的 FastAPI 实例，
    所有配置从本模块常量中读取，不分散到其他文件。

    Args:
        app: FastAPI 应用实例。

    Raises:
        TypeError: 如果 app 不是 FastAPI 实例。
    """
    if not isinstance(app, FastAPI):
        raise TypeError(
            f"app 必须是 FastAPI 实例，当前类型: {type(app).__name__}"
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_ALLOW_ORIGINS,
        allow_methods=_ALLOW_METHODS,
        allow_headers=_ALLOW_HEADERS,
        allow_credentials=True,
        expose_headers=_EXPOSE_HEADERS,
        max_age=_MAX_AGE,
    )


__all__ = [
    "setup_cors",
]