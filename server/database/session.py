"""
数据库会话模块

提供 SessionLocal 工厂和 FastAPI 依赖注入函数 get_db()。

使用方式:
    # 手动创建会话
    from server.database.session import SessionLocal
    db = SessionLocal()
    try:
        ...
    finally:
        db.close()

    # FastAPI 依赖注入
    from server.database.session import get_db

    @router.get("/")
    def api(db: Session = Depends(get_db)):
        ...
"""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker
from server.database.engine import engine


# 会话工厂
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入：获取数据库会话

    请求进入时创建会话，请求结束时自动关闭。

    Yields:
        SQLAlchemy Session 实例
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()