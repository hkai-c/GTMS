"""
GTMS 桌面客户端配置模块

客户端配置优先级:
    1. 环境变量（GTMS_ 前缀）
    2. 代码默认值

使用方式:
    from client.config import client_config
    api_url = client_config.API_BASE_URL
"""

import os
from pathlib import Path


class ClientConfig:
    """桌面客户端配置"""

    # ============================================================
    # API 连接配置
    # ============================================================

    # API 服务基础地址
    API_BASE_URL: str = os.getenv(
        "GTMS_API_BASE_URL",
        "http://localhost:8000/api",
    )

    # HTTP 请求超时（秒）
    HTTP_TIMEOUT: int = int(os.getenv("GTMS_HTTP_TIMEOUT", "30"))

    # ============================================================
    # 界面配置
    # ============================================================

    # 列表每页条数
    PAGE_SIZE: int = int(os.getenv("GTMS_PAGE_SIZE", "20"))

    # 应用标题
    APP_TITLE: str = "GTMS - 磨床试磨管理系统"

    # 应用版本
    APP_VERSION: str = "1.0.0"

    # 窗口最小宽度
    WINDOW_MIN_WIDTH: int = 1280

    # 窗口最小高度
    WINDOW_MIN_HEIGHT: int = 720

    # ============================================================
    # 本地存储配置
    # ============================================================

    # Token 存储键名
    TOKEN_KEY: str = "gtms_token"

    # 用户信息存储键名
    USER_KEY: str = "gtms_user"

    # 记住的用户名存储键名
    REMEMBER_USERNAME_KEY: str = "gtms_remember_username"

    # 上次服务器地址存储键名
    LAST_SERVER_KEY: str = "gtms_last_server"

    # ============================================================
    # 文件类型过滤
    # ============================================================

    # 图片文件过滤器
    IMAGE_FILTER: str = "图片文件 (*.jpg *.jpeg *.png)"

    # 文档文件过滤器
    DOCUMENT_FILTER: str = "文档文件 (*.pdf *.docx *.xlsx)"

    # CAD 文件过滤器
    CAD_FILTER: str = "CAD 文件 (*.dwg *.dxf)"

    # 视频文件过滤器
    VIDEO_FILTER: str = "视频文件 (*.mp4)"

    # ============================================================
    # 派生属性
    # ============================================================

    @property
    def API_AUTH_URL(self) -> str:
        """认证接口地址"""
        return f"{self.API_BASE_URL}/auth/login"

    @property
    def API_TASKS_URL(self) -> str:
        """任务接口地址"""
        return f"{self.API_BASE_URL}/tasks"

    @property
    def API_CUSTOMERS_URL(self) -> str:
        """客户接口地址"""
        return f"{self.API_BASE_URL}/customers"

    @property
    def API_UPLOAD_URL(self) -> str:
        """文件上传接口地址"""
        return f"{self.API_BASE_URL}/upload"

    @property
    def IS_DEVELOPMENT(self) -> bool:
        """是否为开发环境（本地 localhost）"""
        return "localhost" in self.API_BASE_URL or "127.0.0.1" in self.API_BASE_URL


# 全局单例
client_config = ClientConfig()