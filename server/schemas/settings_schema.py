"""系统设置 Schema (Settings Schema)

Sprint 13 — Task 13.3
严格依据 SRS §4.12 FR-SETTINGS、CODE_WIKI §15.22 Settings Principle。
使用 Pydantic v2 Field()、field_validator、ConfigDict。

Schema 列表:
    - SettingsBase:     系统设置基础字段
    - SettingsUpdate:   系统设置更新（所有字段可选）
    - SettingsResponse: 系统设置响应（含 id/created_at/updated_at）

注意: 系统设置模块不涉及 Workflow 和 Status Machine。
      Schema 仅定义数据结构，不包含业务逻辑。
      不得直接读取或修改配置文件。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================
# 系统设置基础 Schema
# ============================================================


class SettingsBase(BaseModel):
    """系统设置基础字段。

    依据 SRS §4.12 FR-SETTINGS-01 配置项定义。
    包含所有可配置的系统设置字段。

    Attributes:
        database_path: 数据库文件路径。
        backup_directory: 备份文件存储目录。
        backup_enabled: 是否启用自动备份。
        backup_time: 自动备份执行时间（格式 HH:MM）。
        backup_retention_days: 备份文件保留天数。
        upload_directory: 文件上传根目录。
        max_image_size_mb: 图片上传大小限制（MB）。
        max_document_size_mb: 文档上传大小限制（MB）。
        max_video_size_mb: 视频上传大小限制（MB）。
        receipt_delay_hours: 收件超时提醒阈值（小时）。
        grinding_delay_hours: 试磨超时提醒阈值（小时）。
        report_missing_hours: 报告缺失提醒阈值（小时）。
        check_interval_minutes: 定时检查提醒间隔（分钟）。
        system_name: 系统名称。
        company_name: 公司名称。
        theme: 界面主题。
        language: 界面语言。
        timezone: 时区。
        log_retention_days: 日志保留天数。
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    # 数据库与备份
    database_path: str = Field(
        default="database/gtms.db",
        min_length=1,
        description="数据库文件路径",
    )
    backup_directory: str = Field(
        default="backup/",
        min_length=1,
        description="备份文件存储目录",
    )
    backup_enabled: bool = Field(
        default=True,
        description="是否启用自动备份",
    )
    backup_time: str = Field(
        default="02:00",
        min_length=1,
        description="自动备份执行时间（格式 HH:MM）",
    )
    backup_retention_days: int = Field(
        default=30,
        gt=0,
        description="备份文件保留天数（> 0）",
    )

    # 上传
    upload_directory: str = Field(
        default="uploads/",
        min_length=1,
        description="文件上传根目录",
    )
    max_image_size_mb: int = Field(
        default=10,
        gt=0,
        description="图片上传大小限制（MB）",
    )
    max_document_size_mb: int = Field(
        default=50,
        gt=0,
        description="文档上传大小限制（MB）",
    )
    max_video_size_mb: int = Field(
        default=200,
        gt=0,
        description="视频上传大小限制（MB）",
    )

    # 通知
    receipt_delay_hours: int = Field(
        default=48,
        gt=0,
        description="收件超时提醒阈值（小时）",
    )
    grinding_delay_hours: int = Field(
        default=120,
        gt=0,
        description="试磨超时提醒阈值（小时）",
    )
    report_missing_hours: int = Field(
        default=72,
        gt=0,
        description="报告缺失提醒阈值（小时）",
    )
    check_interval_minutes: int = Field(
        default=60,
        gt=0,
        description="定时检查提醒间隔（分钟）",
    )

    # 系统
    system_name: str = Field(
        default="GTMS",
        min_length=1,
        description="系统名称",
    )
    company_name: str = Field(
        default="",
        min_length=0,
        description="公司名称",
    )
    theme: str = Field(
        default="light",
        min_length=1,
        description="界面主题",
    )
    language: str = Field(
        default="zh-CN",
        min_length=1,
        description="界面语言",
    )
    timezone: str = Field(
        default="Asia/Shanghai",
        min_length=1,
        description="时区",
    )
    log_retention_days: int = Field(
        default=90,
        gt=0,
        description="日志保留天数（> 0）",
    )

    # ============================================================
    # 字段校验
    # ============================================================

    @field_validator("backup_time")
    @classmethod
    def validate_backup_time(cls, v: str) -> str:
        """校验备份时间格式。

        格式为 HH:MM，例如 "02:00"。

        Args:
            v: 备份时间字符串。

        Returns:
            str: 校验通过的备份时间。

        Raises:
            ValueError: 格式不正确。
        """
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("备份时间格式必须为 HH:MM")
        try:
            hour = int(parts[0])
            minute = int(parts[1])
        except ValueError:
            raise ValueError("备份时间必须为有效数字")
        if not (0 <= hour <= 23):
            raise ValueError("小时必须在 0-23 之间")
        if not (0 <= minute <= 59):
            raise ValueError("分钟必须在 0-59 之间")
        return v


# ============================================================
# 系统设置更新 Schema
# ============================================================


class SettingsUpdate(BaseModel):
    """系统设置更新 Schema。

    所有字段均为可选，仅更新传入的字段。
    禁止传入 id、created_at、updated_at 等系统字段。

    使用 extra="forbid" 禁止额外字段。
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    # 数据库与备份
    database_path: Optional[str] = Field(
        default=None,
        min_length=1,
        description="数据库文件路径",
    )
    backup_directory: Optional[str] = Field(
        default=None,
        min_length=1,
        description="备份文件存储目录",
    )
    backup_enabled: Optional[bool] = Field(
        default=None,
        description="是否启用自动备份",
    )
    backup_time: Optional[str] = Field(
        default=None,
        min_length=1,
        description="自动备份执行时间（格式 HH:MM）",
    )
    backup_retention_days: Optional[int] = Field(
        default=None,
        gt=0,
        description="备份文件保留天数（> 0）",
    )

    # 上传
    upload_directory: Optional[str] = Field(
        default=None,
        min_length=1,
        description="文件上传根目录",
    )
    max_image_size_mb: Optional[int] = Field(
        default=None,
        gt=0,
        description="图片上传大小限制（MB）",
    )
    max_document_size_mb: Optional[int] = Field(
        default=None,
        gt=0,
        description="文档上传大小限制（MB）",
    )
    max_video_size_mb: Optional[int] = Field(
        default=None,
        gt=0,
        description="视频上传大小限制（MB）",
    )

    # 通知
    receipt_delay_hours: Optional[int] = Field(
        default=None,
        gt=0,
        description="收件超时提醒阈值（小时）",
    )
    grinding_delay_hours: Optional[int] = Field(
        default=None,
        gt=0,
        description="试磨超时提醒阈值（小时）",
    )
    report_missing_hours: Optional[int] = Field(
        default=None,
        gt=0,
        description="报告缺失提醒阈值（小时）",
    )
    check_interval_minutes: Optional[int] = Field(
        default=None,
        gt=0,
        description="定时检查提醒间隔（分钟）",
    )

    # 系统
    system_name: Optional[str] = Field(
        default=None,
        min_length=1,
        description="系统名称",
    )
    company_name: Optional[str] = Field(
        default=None,
        min_length=0,
        description="公司名称",
    )
    theme: Optional[str] = Field(
        default=None,
        min_length=1,
        description="界面主题",
    )
    language: Optional[str] = Field(
        default=None,
        min_length=1,
        description="界面语言",
    )
    timezone: Optional[str] = Field(
        default=None,
        min_length=1,
        description="时区",
    )
    log_retention_days: Optional[int] = Field(
        default=None,
        gt=0,
        description="日志保留天数（> 0）",
    )

    # ============================================================
    # 字段校验
    # ============================================================

    @field_validator("backup_time")
    @classmethod
    def validate_backup_time(cls, v: Optional[str]) -> Optional[str]:
        """校验备份时间格式（可选字段）。

        Args:
            v: 备份时间字符串或 None。

        Returns:
            Optional[str]: 校验通过的值。
        """
        if v is None:
            return v
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("备份时间格式必须为 HH:MM")
        try:
            hour = int(parts[0])
            minute = int(parts[1])
        except ValueError:
            raise ValueError("备份时间必须为有效数字")
        if not (0 <= hour <= 23):
            raise ValueError("小时必须在 0-23 之间")
        if not (0 <= minute <= 59):
            raise ValueError("分钟必须在 0-59 之间")
        return v


# ============================================================
# 系统设置响应 Schema
# ============================================================


class SettingsResponse(SettingsBase):
    """系统设置响应 Schema。

    继承 SettingsBase 所有字段，新增系统字段。
    用于 API 响应，包含完整的配置信息。

    Attributes:
        id: 配置记录 ID。
        created_at: 创建时间。
        updated_at: 更新时间。
    """

    id: int = Field(
        ...,
        description="配置记录 ID",
    )
    created_at: datetime = Field(
        ...,
        description="创建时间",
    )
    updated_at: datetime = Field(
        ...,
        description="更新时间",
    )


__all__ = [
    "SettingsBase",
    "SettingsResponse",
    "SettingsUpdate",
]
