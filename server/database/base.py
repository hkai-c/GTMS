"""
ORM 模型基类

所有数据库模型必须继承此 Base 类。

使用方式:
    from server.database.base import Base

    class User(Base):
        __tablename__ = "users"
        ...
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy ORM 模型基类

    所有模型继承此类以自动获得：
    - 表名自动推断
    - metadata 统一管理
    - create_all / drop_all 支持
    """
    pass