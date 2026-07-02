"""
server.database 包

数据库基础设施层，提供：
- engine:     SQLAlchemy 引擎
- session:    会话工厂 + FastAPI 依赖注入
- base:       ORM 模型基类
- init_db:    数据库初始化
"""

from server.database.engine import engine
from server.database.session import SessionLocal, get_db
from server.database.base import Base
from server.database.init_db import init_database

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "Base",
    "init_database",
]