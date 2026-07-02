"""
数据库引擎模块

负责创建 SQLAlchemy Engine，支持 SQLite 和 MySQL。
所有配置从 server.config.settings 读取。

使用方式:
    from server.database.engine import engine
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from server.config import settings


def create_database_engine() -> Engine:
    """创建数据库引擎

    根据 DATABASE_URL 自动适配 SQLite / MySQL：
    - SQLite: 需要 check_same_thread=False
    - MySQL: 需要 pool_pre_ping=True + pool_recycle

    Returns:
        SQLAlchemy Engine 实例
    """
    database_url: str = settings.DATABASE_URL

    # SQLite 专用参数
    connect_args: dict = {}
    pool_kwargs: dict = {}

    if "sqlite" in database_url:
        connect_args["check_same_thread"] = False
    else:
        # MySQL / PostgreSQL 连接池配置
        pool_kwargs["pool_pre_ping"] = True
        pool_kwargs["pool_recycle"] = 3600
        pool_kwargs["pool_size"] = 10
        pool_kwargs["max_overflow"] = 20

    engine: Engine = create_engine(
        database_url,
        echo=settings.DEBUG,  # 调试模式打印 SQL
        connect_args=connect_args,
        **pool_kwargs,
    )

    return engine


# 全局引擎实例
engine: Engine = create_database_engine()