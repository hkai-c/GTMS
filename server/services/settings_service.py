"""系统设置业务层 (Settings Service)

Sprint 13 — Task 13.4
严格依据 SRS §4.12 FR-SETTINGS、CODE_WIKI §15.15、§15.22、§15.23。

提供系统设置的单例读取与更新功能：
    - 读取配置（get_settings）
    - 更新配置（update_settings）

公开 API:
    - get_settings() -> SettingsResponse
    - update_settings(db, data, operator_id) -> SettingsResponse

约束:
    - Settings 为 Singleton，整个系统仅一份配置
    - 禁止 create/delete/list/search/batch 操作
    - 所有更新通过 LogService 写入审计日志
    - 配置持久化到 server/config.py Settings 单例 + .env 文件
    - 禁止 Router/Desktop/View/Scheduler 直接访问配置
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from server.config import BASE_DIR, Settings, settings
from server.core.exceptions import BusinessLogicException
from server.enums.action_type import ActionType
from server.schemas.log_schema import LogBase
from server.schemas.settings_schema import (
    SettingsResponse,
    SettingsUpdate,
)
from server.services.log_service import LogService

logger = logging.getLogger("gtms.server")

# ============================================================
# 统一常量
# ============================================================

MODULE_NAME: str = "settings"
"""审计日志模块名称。"""

TARGET_TYPE: str = "settings"
"""审计日志对象类型。"""

SETTINGS_ID: int = 1
"""系统设置固定 ID（单例）。"""

ENV_FILE_PATH: Path = BASE_DIR / ".env"
""".env 配置文件路径。"""


class SettingsService:
    """系统设置业务服务。

    Sprint 13 — Task 13.4
    依据 SRS §4.12 FR-SETTINGS、CODE_WIKI §15.22、§15.23。

    Settings 为 Singleton，整个系统仅维护一份配置。
    配置通过 server/config.py Settings 单例读取，通过 .env 文件持久化。
    所有更新操作写入审计日志。

    公开 API:
        - get_settings() -> SettingsResponse
        - update_settings(db, data, operator_id) -> SettingsResponse
    """

    # ============================================================
    # Public API
    # ============================================================

    def get_settings(self) -> SettingsResponse:
        """获取当前系统唯一配置。

        从 server.config.settings 单例读取所有配置项，
        映射为 SettingsResponse 返回。

        Returns:
            SettingsResponse: 当前系统配置。

        Raises:
            BusinessLogicException: 配置读取失败。
        """
        try:
            now = datetime.now()
            base_data = self._load_settings()

            return SettingsResponse(
                id=SETTINGS_ID,
                created_at=now,
                updated_at=now,
                **base_data,
            )
        except Exception as e:
            logger.error("读取系统配置失败: %s", e)
            raise BusinessLogicException(
                "读取系统配置失败",
                detail={"error": str(e)},
            )

    def update_settings(
        self,
        db: Session,
        data: SettingsUpdate,
        operator_id: int,
    ) -> SettingsResponse:
        """更新系统配置。

        仅更新传入的非 None 字段，保持其他字段不变。
        更新后立即持久化到 .env 文件，并写入审计日志。

        Args:
            db: 数据库会话。
            data: 待更新的配置数据（仅非 None 字段生效）。
            operator_id: 操作人 ID。

        Returns:
            SettingsResponse: 更新后的完整配置。

        Raises:
            BusinessLogicException: 更新失败。
        """
        try:
            # 1. 获取当前配置
            current = self._load_settings()

            # 2. 合并更新（仅非 None 字段）
            update_data = data.model_dump(exclude_none=True)
            changed_fields: dict[str, Any] = {}
            for key, new_value in update_data.items():
                old_value = current.get(key)
                if old_value != new_value:
                    current[key] = new_value
                    changed_fields[key] = {"old": old_value, "new": new_value}

            # 3. 持久化
            self._save_settings(current)

            # 4. 审计日志
            if changed_fields:
                description = json.dumps(
                    {"changed_fields": changed_fields},
                    ensure_ascii=False,
                )
                self._write_log(db, operator_id, description)

            now = datetime.now()
            return SettingsResponse(
                id=SETTINGS_ID,
                created_at=now,
                updated_at=now,
                **current,
            )

        except BusinessLogicException:
            raise
        except Exception as e:
            logger.error("更新系统配置失败: %s", e)
            raise BusinessLogicException(
                "更新系统配置失败",
                detail={"error": str(e)},
            )

    # ============================================================
    # Private Methods
    # ============================================================

    def _load_settings(self) -> dict[str, Any]:
        """从 settings 单例加载当前配置。

        将 server.config.settings 中的配置字段映射为
        SettingsBase 字段名，构建字典返回。

        Returns:
            dict[str, Any]: 当前配置的字段字典。
        """
        # 备份时间格式转换
        backup_hour = settings.BACKUP_CRON_HOUR
        backup_minute = settings.BACKUP_CRON_MINUTE
        backup_time = f"{backup_hour:02d}:{backup_minute:02d}"

        # 数据库路径提取
        db_url = settings.DATABASE_URL
        if db_url.startswith("sqlite:///"):
            database_path = db_url[len("sqlite:///"):]
        else:
            database_path = db_url

        return {
            # 数据库与备份
            "database_path": database_path,
            "backup_directory": settings.BACKUP_DIR,
            "backup_enabled": settings.BACKUP_ENABLED,
            "backup_time": backup_time,
            "backup_retention_days": settings.BACKUP_RETENTION_DAYS,
            # 上传
            "upload_directory": settings.UPLOAD_DIR,
            "max_image_size_mb": settings.MAX_IMAGE_SIZE_MB,
            "max_document_size_mb": settings.MAX_DOCUMENT_SIZE_MB,
            "max_video_size_mb": settings.MAX_VIDEO_SIZE_MB,
            # 通知
            "receipt_delay_hours": settings.NOTIFY_RECEIPT_DELAY_HOURS,
            "grinding_delay_hours": settings.NOTIFY_GRINDING_DELAY_HOURS,
            "report_missing_hours": settings.NOTIFY_REPORT_MISSING_HOURS,
            "check_interval_minutes": settings.NOTIFY_CHECK_INTERVAL_MINUTES,
            # 系统
            "system_name": settings.SYSTEM_NAME,
            "company_name": settings.COMPANY_NAME,
            "theme": settings.THEME,
            "language": settings.LANGUAGE,
            "timezone": settings.TIMEZONE,
            "log_retention_days": settings.LOG_RETENTION_DAYS,
        }

    def _save_settings(self, data: dict[str, Any]) -> None:
        """持久化配置到 .env 文件并更新内存单例。

        将配置数据写入 .env 文件，同时更新内存中的 settings 单例。

        Args:
            data: 完整的配置字段字典。

        Raises:
            BusinessLogicException: 持久化失败。
        """
        try:
            # Schema 字段名 → (config.py 字段名, 值转换函数)
            mapping: dict[str, tuple[str, Any]] = {
                "database_path": (
                    "DATABASE_URL",
                    lambda v: (
                        f"sqlite:///{v}"
                        if not str(v).startswith("sqlite:///") else str(v)
                    ),
                ),
                "backup_directory": ("BACKUP_DIR", lambda v: str(v)),
                "backup_enabled": (
                    "BACKUP_ENABLED",
                    lambda v: str(v).lower(),
                ),
                "backup_retention_days": (
                    "BACKUP_RETENTION_DAYS",
                    lambda v: str(int(v)),
                ),
                "upload_directory": ("UPLOAD_DIR", lambda v: str(v)),
                "max_image_size_mb": (
                    "MAX_IMAGE_SIZE_MB",
                    lambda v: str(int(v)),
                ),
                "max_document_size_mb": (
                    "MAX_DOCUMENT_SIZE_MB",
                    lambda v: str(int(v)),
                ),
                "max_video_size_mb": (
                    "MAX_VIDEO_SIZE_MB",
                    lambda v: str(int(v)),
                ),
                "receipt_delay_hours": (
                    "NOTIFY_RECEIPT_DELAY_HOURS",
                    lambda v: str(int(v)),
                ),
                "grinding_delay_hours": (
                    "NOTIFY_GRINDING_DELAY_HOURS",
                    lambda v: str(int(v)),
                ),
                "report_missing_hours": (
                    "NOTIFY_REPORT_MISSING_HOURS",
                    lambda v: str(int(v)),
                ),
                "check_interval_minutes": (
                    "NOTIFY_CHECK_INTERVAL_MINUTES",
                    lambda v: str(int(v)),
                ),
                "system_name": ("SYSTEM_NAME", lambda v: str(v)),
                "company_name": ("COMPANY_NAME", lambda v: str(v)),
                "theme": ("THEME", lambda v: str(v)),
                "language": ("LANGUAGE", lambda v: str(v)),
                "timezone": ("TIMEZONE", lambda v: str(v)),
                "log_retention_days": (
                    "LOG_RETENTION_DAYS",
                    lambda v: str(int(v)),
                ),
            }

            # 构建 env 更新字典（env_key → value_str）
            env_updates: dict[str, str] = {}

            # backup_time 特殊处理：拆分为 BACKUP_CRON_HOUR + BACKUP_CRON_MINUTE
            if "backup_time" in data:
                parts = str(data["backup_time"]).split(":")
                if len(parts) == 2:
                    env_updates["BACKUP_CRON_HOUR"] = str(int(parts[0]))
                    env_updates["BACKUP_CRON_MINUTE"] = str(int(parts[1]))

            for schema_key, value in data.items():
                if schema_key == "backup_time":
                    continue
                if schema_key in mapping:
                    env_key, converter = mapping[schema_key]
                    env_updates[env_key] = converter(value)

            # 更新内存中的 settings 单例
            for env_key, value_str in env_updates.items():
                if env_key in Settings.model_fields:
                    field_info = Settings.model_fields[env_key]
                    field_type = field_info.annotation
                    if field_type is int:
                        setattr(settings, env_key, int(value_str))
                    elif field_type is bool:
                        setattr(
                            settings,
                            env_key,
                            value_str.lower() == "true",
                        )
                    else:
                        setattr(settings, env_key, value_str)

            # 写入 .env 文件
            self._write_env_file(env_updates)

            logger.info("系统配置已保存到 .env 文件")
        except BusinessLogicException:
            raise
        except Exception as e:
            logger.error("保存系统配置失败: %s", e)
            raise BusinessLogicException(
                "保存系统配置失败",
                detail={"error": str(e)},
            )

    @staticmethod
    def _write_env_file(updates: dict[str, str]) -> None:
        """写入 .env 文件，保留现有内容。

        仅更新或追加指定的键值对，不修改其他行。

        Args:
            updates: 待写入的键值对（env_key → value_str）。
        """
        env_path = ENV_FILE_PATH

        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = []

        updated_keys: set[str] = set()
        new_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and "=" in stripped
            ):
                key = stripped.split("=", 1)[0].strip()
                if key in updates:
                    new_lines.append(f"{key}={updates[key]}\n")
                    updated_keys.add(key)
                    continue
            new_lines.append(line)

        # 追加新增的键
        for key, value in updates.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    @staticmethod
    def _write_log(
        db: Session,
        operator_id: int,
        description: str,
    ) -> None:
        """写入审计日志。

        委托 LogService.create_log() 写入操作日志。

        Args:
            db: 数据库会话。
            operator_id: 操作人 ID。
            description: 操作描述（JSON 格式）。
        """
        log_base = LogBase(
            operator_id=operator_id,
            operation=ActionType.UPDATE,
            module=MODULE_NAME,
            target_type=TARGET_TYPE,
            target_id=None,
            description=description,
            created_at=datetime.now(),
        )
        log_service = LogService()
        log_service.create_log(db, log_base)


__all__ = [
    "SettingsService",
]
