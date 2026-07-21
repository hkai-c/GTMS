"""数据库备份管理器 (Backup Manager)

Sprint 13 — Task 13.1
依据 CODE_WIKI §6.6.2、§15.21 Backup Principle。

提供统一的数据库备份、恢复、清理功能。
BackupManager 属于 Infrastructure Layer，不参与任何业务逻辑。

Public API:
    create_backup() -> str           — 创建数据库备份
    restore(backup_path) -> None     — 从备份恢复数据库
    cleanup_old_backups(days) -> int — 清理过期备份文件

使用方式:
    from server.utils.backup import BackupManager

    manager = BackupManager()
    path = manager.create_backup()
    manager.restore(path)
    count = manager.cleanup_old_backups(30)
"""

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from server.config import BASE_DIR, settings
from server.core.exceptions import BusinessLogicException

logger = logging.getLogger("gtms.server")

# ============================================================
# 统一常量
# ============================================================

BACKUP_FILE_PREFIX: str = "gtms_backup_"
"""备份文件名前缀。"""

BACKUP_FILE_SUFFIX: str = ".db"
"""备份文件扩展名。"""

DEFAULT_RETENTION_DAYS: int = 30
"""默认备份保留天数。"""

TIMESTAMP_FORMAT: str = "%Y%m%d_%H%M%S"
"""备份文件名时间戳格式。"""


class BackupManager:
    """数据库备份管理器。

    Sprint 13 — Task 13.1
    依据 CODE_WIKI §6.6.2、§15.21 Backup Principle。

    职责：
        - 数据库备份（create_backup）
        - 数据库恢复（restore）
        - 历史备份清理（cleanup_old_backups）

    BackupManager 属于 Infrastructure Layer，
    不得包含任何业务逻辑、Workflow、Status Machine、ORM 操作。
    """

    def __init__(self) -> None:
        """初始化 BackupManager。

        从 server.config.settings 读取备份目录和数据库路径配置。
        自动创建备份目录（如不存在）。
        """
        self._backup_dir: Path = self._resolve_backup_dir()
        self._db_path: Path = self._resolve_db_path()

    # ============================================================
    # 内部方法
    # ============================================================

    @staticmethod
    def _resolve_backup_dir() -> Path:
        """解析备份目录路径。

        使用 settings.BACKUP_DIR_ABS 获取备份目录绝对路径，
        并确保目录存在。

        Returns:
            Path: 备份目录的绝对路径。
        """
        backup_dir: Path = settings.BACKUP_DIR_ABS
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    @staticmethod
    def _resolve_db_path() -> Path:
        """解析数据库文件路径。

        从 settings.DATABASE_URL 中提取 SQLite 数据库文件的实际路径。
        仅支持 SQLite 数据库。

        Returns:
            Path: 数据库文件的绝对路径。

        Raises:
            BusinessLogicException: 数据库类型不支持。
        """
        db_url: str = settings.DATABASE_URL

        if db_url.startswith("sqlite:///"):
            # SQLite: sqlite:///./database/gtms.db → ./database/gtms.db
            relative_path: str = db_url[len("sqlite:///"):]
            db_path: Path = (BASE_DIR / relative_path).resolve()
            return db_path

        raise BusinessLogicException(
            "不支持的数据库类型，当前仅支持 SQLite 备份",
            detail={"database_url": db_url},
        )

    @staticmethod
    def _generate_backup_filename() -> str:
        """生成备份文件名。

        格式：gtms_backup_YYYYMMDD_HHMMSS.db

        Returns:
            str: 带时间戳的备份文件名。
        """
        timestamp: str = datetime.now().strftime(TIMESTAMP_FORMAT)
        return f"{BACKUP_FILE_PREFIX}{timestamp}{BACKUP_FILE_SUFFIX}"

    # ============================================================
    # Public API
    # ============================================================

    def create_backup(self) -> str:
        """创建数据库备份。

        将当前数据库文件复制到备份目录，生成带时间戳的备份文件。
        每次调用均生成独立备份，不会覆盖已有备份。

        Returns:
            str: 备份文件的绝对路径。

        Raises:
            BusinessLogicException: 数据库文件不存在或备份过程失败。
        """
        if not self._db_path.exists():
            raise BusinessLogicException(
                "数据库文件不存在，无法创建备份",
                detail={"db_path": str(self._db_path)},
            )

        backup_filename: str = self._generate_backup_filename()
        backup_path: Path = self._backup_dir / backup_filename

        try:
            shutil.copy2(self._db_path, backup_path)
            logger.info("数据库备份成功: %s", backup_path)
            return str(backup_path)
        except Exception as e:
            logger.error("数据库备份失败: %s", e)
            raise BusinessLogicException(
                "数据库备份失败",
                detail={
                    "db_path": str(self._db_path),
                    "backup_path": str(backup_path),
                    "error": str(e),
                },
            )

    def restore(self, backup_path: str) -> None:
        """从备份文件恢复数据库。

        将指定的备份文件复制回数据库文件位置，覆盖当前数据库。

        Args:
            backup_path: 备份文件的路径（绝对路径或相对路径）。

        Raises:
            BusinessLogicException: 备份文件不存在、路径无效或恢复过程失败。
        """
        backup_file: Path = Path(backup_path)

        if not backup_file.exists():
            raise BusinessLogicException(
                "备份文件不存在，无法恢复",
                detail={"backup_path": str(backup_file)},
            )

        if not backup_file.is_file():
            raise BusinessLogicException(
                "备份路径不是有效的文件",
                detail={"backup_path": str(backup_file)},
            )

        try:
            shutil.copy2(backup_file, self._db_path)
            logger.info("数据库恢复成功: %s -> %s", backup_file, self._db_path)
        except Exception as e:
            logger.error("数据库恢复失败: %s", e)
            raise BusinessLogicException(
                "数据库恢复失败",
                detail={
                    "backup_path": str(backup_file),
                    "db_path": str(self._db_path),
                    "error": str(e),
                },
            )

    def cleanup_old_backups(
        self, retention_days: int = DEFAULT_RETENTION_DAYS
    ) -> int:
        """清理超过保留期限的历史备份文件。

        仅清理符合命名规范（gtms_backup_*.db）的备份文件。
        根据文件的修改时间判断是否过期。

        Args:
            retention_days: 保留天数，默认 30 天。必须大于 0。

        Returns:
            int: 本次清理的备份文件数量。

        Raises:
            BusinessLogicException: retention_days 无效或清理过程失败。
        """
        if retention_days <= 0:
            raise BusinessLogicException(
                "保留天数必须大于 0",
                detail={"retention_days": retention_days},
            )

        cutoff_time: datetime = datetime.now() - timedelta(days=retention_days)
        cleaned_count: int = 0

        try:
            for backup_file in self._backup_dir.iterdir():
                if not backup_file.is_file():
                    continue
                if not backup_file.name.startswith(BACKUP_FILE_PREFIX):
                    continue
                if not backup_file.suffix == BACKUP_FILE_SUFFIX:
                    continue

                # 根据文件修改时间判断是否过期
                file_mtime: datetime = datetime.fromtimestamp(
                    backup_file.stat().st_mtime
                )
                if file_mtime < cutoff_time:
                    backup_file.unlink()
                    cleaned_count += 1
                    logger.info(
                        "清理过期备份: %s (修改时间: %s)",
                        backup_file.name,
                        file_mtime.strftime(TIMESTAMP_FORMAT),
                    )

            logger.info(
                "备份清理完成: 共清理 %d 个过期备份文件",
                cleaned_count,
            )
            return cleaned_count

        except Exception as e:
            logger.error("备份清理失败: %s", e)
            raise BusinessLogicException(
                "备份清理失败",
                detail={
                    "backup_dir": str(self._backup_dir),
                    "retention_days": retention_days,
                    "error": str(e),
                },
            )


__all__ = [
    "BackupManager",
    "BACKUP_FILE_PREFIX",
    "BACKUP_FILE_SUFFIX",
    "DEFAULT_RETENTION_DAYS",
    "TIMESTAMP_FORMAT",
]
