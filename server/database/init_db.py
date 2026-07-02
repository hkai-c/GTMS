"""
数据库初始化模块

负责创建所有表、初始化种子数据。
在 FastAPI 启动时调用。

使用方式:
    # 应用启动时
    from server.database.init_db import init_database
    init_database()

    # 命令行
    python -m server.database.init_db
"""

import logging

from server.config import settings
from server.database.engine import engine
from server.database.base import Base

logger = logging.getLogger(__name__)


def init_database() -> None:
    """初始化数据库

    创建所有 ORM 模型对应的表（表不存在时创建，已存在则跳过）。
    确保必需的目录存在。
    """
    logger.info("正在初始化数据库...")
    logger.info("数据库类型: %s", "SQLite" if "sqlite" in settings.DATABASE_URL else "MySQL")
    logger.info("数据库 URL: %s", settings.DATABASE_URL)

    # 确保上传、备份、日志目录存在
    settings.ensure_directories()

    # 创建所有表
    # 注意：需要在导入所有模型后才能正确执行
    Base.metadata.create_all(bind=engine)

    logger.info("数据库初始化完成")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
    print("数据库初始化成功！")