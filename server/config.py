"""
GTMS 服务端统一配置模块

基于 pydantic-settings，支持 .env 文件和环境变量。
所有配置项必须从此模块读取，禁止硬编码。

使用方式:
    from server.config import settings
    db_url = settings.DATABASE_URL
"""

import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """GTMS 全局配置（从 .env 文件加载）"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================
    # 运行环境
    # ============================================================

    # 环境模式: development / production
    ENV_MODE: Literal["development", "production"] = "development"

    # 是否开启调试模式
    DEBUG: bool = True

    # ============================================================
    # 数据库配置
    # ============================================================

    # 数据库连接 URL
    # 开发环境: sqlite:///./database/gtms.db
    # 生产环境: mysql+pymysql://user:pass@localhost:3306/gtms
    DATABASE_URL: str = "sqlite:///./database/gtms.db"

    # ============================================================
    # 安全配置
    # ============================================================

    # JWT 密钥（生产环境必须更换）
    SECRET_KEY: str = "change-me-to-a-random-secret-key-in-production"

    # JWT 加密算法
    ALGORITHM: str = "HS256"

    # Token 过期时间（分钟），默认 8 小时
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # ============================================================
    # 文件上传配置
    # ============================================================

    # 上传文件根目录
    UPLOAD_DIR: str = "./uploads"

    # 图片最大大小（MB）
    MAX_IMAGE_SIZE_MB: int = 10

    # 文档最大大小（MB）
    MAX_DOCUMENT_SIZE_MB: int = 50

    # CAD 文件最大大小（MB）
    MAX_CAD_SIZE_MB: int = 50

    # 视频最大大小（MB）
    MAX_VIDEO_SIZE_MB: int = 200

    # 允许的图片格式（逗号分隔）
    ALLOWED_IMAGE_TYPES: str = "jpg,jpeg,png"

    # 允许的文档格式（逗号分隔）
    ALLOWED_DOCUMENT_TYPES: str = "pdf,docx,xlsx"

    # 允许的 CAD 格式（逗号分隔）
    ALLOWED_CAD_TYPES: str = "dwg,dxf"

    # 允许的视频格式（逗号分隔）
    ALLOWED_VIDEO_TYPES: str = "mp4"

    # ============================================================
    # 服务配置
    # ============================================================

    # 服务监听地址
    SERVER_HOST: str = "0.0.0.0"

    # 服务监听端口
    SERVER_PORT: int = 8000

    # 日志级别
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # 日志文件目录
    LOG_DIR: str = "./logs"

    # ============================================================
    # 备份配置
    # ============================================================

    # 备份文件存储目录
    BACKUP_DIR: str = "./backup"

    # 自动备份时间 — 小时
    BACKUP_CRON_HOUR: int = 2

    # 自动备份时间 — 分钟
    BACKUP_CRON_MINUTE: int = 0

    # ============================================================
    # 消息提醒配置
    # ============================================================

    # 收件超时提醒阈值（小时）
    NOTIFY_RECEIPT_DELAY_HOURS: int = 48

    # 试磨超时提醒阈值（小时）
    NOTIFY_GRINDING_DELAY_HOURS: int = 120

    # 报告缺失提醒阈值（小时）
    NOTIFY_REPORT_MISSING_HOURS: int = 72

    # 定时检查间隔（分钟）
    NOTIFY_CHECK_INTERVAL_MINUTES: int = 60

    # ============================================================
    # 系统设置
    # ============================================================

    # 系统名称
    SYSTEM_NAME: str = "GTMS"

    # 公司名称
    COMPANY_NAME: str = ""

    # 界面主题
    THEME: str = "light"

    # 界面语言
    LANGUAGE: str = "zh-CN"

    # 时区
    TIMEZONE: str = "Asia/Shanghai"

    # 日志保留天数
    LOG_RETENTION_DAYS: int = 90

    # 备份保留天数
    BACKUP_RETENTION_DAYS: int = 30

    # 是否启用自动备份
    BACKUP_ENABLED: bool = True

    # ============================================================
    # 派生属性（计算得出）
    # ============================================================

    @property
    def IS_PRODUCTION(self) -> bool:
        """是否为生产环境"""
        return self.ENV_MODE == "production"

    @property
    def IS_DEVELOPMENT(self) -> bool:
        """是否为开发环境"""
        return self.ENV_MODE == "development"

    @property
    def UPLOAD_DIR_ABS(self) -> Path:
        """上传目录的绝对路径"""
        upload_path = Path(self.UPLOAD_DIR)
        if not upload_path.is_absolute():
            upload_path = BASE_DIR / upload_path
        return upload_path.resolve()

    @property
    def BACKUP_DIR_ABS(self) -> Path:
        """备份目录的绝对路径"""
        backup_path = Path(self.BACKUP_DIR)
        if not backup_path.is_absolute():
            backup_path = BASE_DIR / backup_path
        return backup_path.resolve()

    @property
    def LOG_DIR_ABS(self) -> Path:
        """日志目录的绝对路径"""
        log_path = Path(self.LOG_DIR)
        if not log_path.is_absolute():
            log_path = BASE_DIR / log_path
        return log_path.resolve()

    @property
    def IMAGE_EXTENSIONS(self) -> list[str]:
        """允许的图片扩展名列表"""
        return [ext.strip() for ext in self.ALLOWED_IMAGE_TYPES.split(",")]

    @property
    def DOCUMENT_EXTENSIONS(self) -> list[str]:
        """允许的文档扩展名列表"""
        return [ext.strip() for ext in self.ALLOWED_DOCUMENT_TYPES.split(",")]

    @property
    def CAD_EXTENSIONS(self) -> list[str]:
        """允许的 CAD 扩展名列表"""
        return [ext.strip() for ext in self.ALLOWED_CAD_TYPES.split(",")]

    @property
    def VIDEO_EXTENSIONS(self) -> list[str]:
        """允许的视频扩展名列表"""
        return [ext.strip() for ext in self.ALLOWED_VIDEO_TYPES.split(",")]

    @property
    def MAX_IMAGE_SIZE_BYTES(self) -> int:
        """图片最大大小（字节）"""
        return self.MAX_IMAGE_SIZE_MB * 1024 * 1024

    @property
    def MAX_DOCUMENT_SIZE_BYTES(self) -> int:
        """文档最大大小（字节）"""
        return self.MAX_DOCUMENT_SIZE_MB * 1024 * 1024

    @property
    def MAX_CAD_SIZE_BYTES(self) -> int:
        """CAD 文件最大大小（字节）"""
        return self.MAX_CAD_SIZE_MB * 1024 * 1024

    @property
    def MAX_VIDEO_SIZE_BYTES(self) -> int:
        """视频最大大小（字节）"""
        return self.MAX_VIDEO_SIZE_MB * 1024 * 1024

    def ensure_directories(self) -> None:
        """确保所有必需的目录存在"""
        directories = [
            self.UPLOAD_DIR_ABS,
            self.UPLOAD_DIR_ABS / "images",
            self.UPLOAD_DIR_ABS / "reports",
            self.UPLOAD_DIR_ABS / "cad",
            self.UPLOAD_DIR_ABS / "videos",
            self.BACKUP_DIR_ABS,
            self.LOG_DIR_ABS,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# 全局单例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例（依赖注入用）"""
    return settings