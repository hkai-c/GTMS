"""GTMS 桌面端系统设置页面 (SettingsView)

Sprint 13 — Task 13.7
严格依据 SRS §4.12 FR-SETTINGS、
    §15.16 Read-Only View Principle、
    §15.20 Desktop HTTP Mapping Principle、
    §15.22 Settings Principle。

提供系统设置编辑界面：
    - 系统信息（名称、公司、主题、语言、时区）
    - 数据库路径
    - 备份设置（目录、时间、启用、保留天数）
    - 上传设置（目录、图片/文档/视频大小限制）
    - 通知设置（收件/试磨/报告延迟、检查间隔）
    - 日志保留天数
    - 保存按钮
    - 状态栏

所有业务逻辑委托 Desktop SettingsService。
禁止直接访问 ApiClient、Router、ORM、Database、Config File。
"""

import logging
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from client.services.settings_service import SettingsService

logger = logging.getLogger("gtms.client")

# ============================================================
# 常量定义
# ============================================================

WINDOW_TITLE: str = "系统设置"

STATUS_READY: str = "就绪"
STATUS_SAVED: str = "保存成功"
STATUS_REFRESHED: str = "刷新完成"
STATUS_SAVING: str = "保存中..."
STATUS_REFRESHING: str = "刷新中..."
STATUS_FAILED: str = "操作失败"

BUTTON_TEXT: dict[str, str] = {
    "save": "保存设置",
    "refresh": "刷新",
}

GROUP_TITLES: dict[str, str] = {
    "system": "系统信息",
    "database": "数据库",
    "backup": "备份设置",
    "upload": "上传设置",
    "notification": "通知设置",
    "log": "日志设置",
}

THEME_OPTIONS: list[str] = ["light", "dark"]
LANGUAGE_OPTIONS: list[str] = ["zh-CN", "en-US"]

OBJECT_NAMES: dict[str, str] = {
    "title_label": "title_label",
    "scroll_area": "scroll_area",
    "system_group": "system_group",
    "database_group": "database_group",
    "backup_group": "backup_group",
    "upload_group": "upload_group",
    "notification_group": "notification_group",
    "log_group": "log_group",
    "system_name_input": "system_name_input",
    "company_name_input": "company_name_input",
    "theme_combo": "theme_combo",
    "language_combo": "language_combo",
    "timezone_input": "timezone_input",
    "database_path_input": "database_path_input",
    "backup_directory_input": "backup_directory_input",
    "backup_time_input": "backup_time_input",
    "backup_enabled_check": "backup_enabled_check",
    "backup_retention_spin": "backup_retention_spin",
    "upload_directory_input": "upload_directory_input",
    "max_image_size_spin": "max_image_size_spin",
    "max_document_size_spin": "max_document_size_spin",
    "max_video_size_spin": "max_video_size_spin",
    "receipt_delay_spin": "receipt_delay_spin",
    "grinding_delay_spin": "grinding_delay_spin",
    "report_missing_spin": "report_missing_spin",
    "check_interval_spin": "check_interval_spin",
    "log_retention_spin": "log_retention_spin",
    "save_btn": "save_btn",
    "refresh_btn": "refresh_btn",
    "status_bar": "status_bar",
}

MESSAGE_TEXT: dict[str, str] = {
    "save_failed": "保存系统设置失败",
    "refresh_failed": "刷新系统设置失败",
    "save_success": "系统设置已保存成功",
}


class SettingsView(QWidget):
    """GTMS 桌面端系统设置页面。

    提供系统配置编辑界面。
    所有业务逻辑委托 Desktop SettingsService。

    Signals:
        settings_changed: 设置变更信号（保存成功/刷新完成后发射）。

    Attributes:
        _settings_service: SettingsService 实例。

    Usage:
        view = SettingsView(settings_service)
        view.settings_changed.connect(on_settings_changed)
        view.refresh()
    """

    # ============================================================
    # Signals
    # ============================================================

    settings_changed: Signal = Signal()
    """设置变更信号。"""

    # ============================================================
    # 初始化
    # ============================================================

    def __init__(
        self,
        settings_service: SettingsService,
        parent: QWidget | None = None,
    ) -> None:
        """初始化系统设置页面。

        Args:
            settings_service: SettingsService 实例。
            parent: 父窗口（可选）。
        """
        super().__init__(parent)
        self._settings_service: SettingsService = settings_service

        self._setup_ui()

        logger.debug("SettingsView 初始化")

    # ============================================================
    # UI 构建
    # ============================================================

    def _setup_ui(self) -> None:
        """构建系统设置页面 UI。

        布局: 标题 → ScrollArea（分组表单） → Toolbar → StatusBar。
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # --- 标题 ---
        self._title_label = QLabel(WINDOW_TITLE)
        self._title_label.setObjectName(OBJECT_NAMES["title_label"])
        self._title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #333333;"
        )
        layout.addWidget(self._title_label)

        # --- 滚动区域 ---
        scroll_area = QScrollArea()
        scroll_area.setObjectName(OBJECT_NAMES["scroll_area"])
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(12)

        # 系统信息组
        scroll_layout.addWidget(self._create_system_group())

        # 数据库组
        scroll_layout.addWidget(self._create_database_group())

        # 备份设置组
        scroll_layout.addWidget(self._create_backup_group())

        # 上传设置组
        scroll_layout.addWidget(self._create_upload_group())

        # 通知设置组
        scroll_layout.addWidget(self._create_notification_group())

        # 日志设置组
        scroll_layout.addWidget(self._create_log_group())

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area, 1)

        # --- 工具栏 ---
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)

        # --- 状态栏 ---
        self._status_bar = QLabel(STATUS_READY)
        self._status_bar.setObjectName(OBJECT_NAMES["status_bar"])
        self._status_bar.setStyleSheet(
            "color: #888888; font-size: 12px; padding: 4px 0;"
        )
        layout.addWidget(self._status_bar)

    # ============================================================
    # 系统信息组
    # ============================================================

    def _create_system_group(self) -> QGroupBox:
        """创建系统信息设置组。

        Returns:
            QGroupBox: 系统信息组。
        """
        group = QGroupBox(GROUP_TITLES["system"])
        group.setObjectName(OBJECT_NAMES["system_group"])
        form = QFormLayout(group)
        form.setSpacing(6)

        self._system_name_input = QLineEdit()
        self._system_name_input.setObjectName(
            OBJECT_NAMES["system_name_input"]
        )
        form.addRow("系统名称:", self._system_name_input)

        self._company_name_input = QLineEdit()
        self._company_name_input.setObjectName(
            OBJECT_NAMES["company_name_input"]
        )
        form.addRow("公司名称:", self._company_name_input)

        self._theme_combo = QComboBox()
        self._theme_combo.setObjectName(OBJECT_NAMES["theme_combo"])
        self._theme_combo.addItems(THEME_OPTIONS)
        form.addRow("主题:", self._theme_combo)

        self._language_combo = QComboBox()
        self._language_combo.setObjectName(
            OBJECT_NAMES["language_combo"]
        )
        self._language_combo.addItems(LANGUAGE_OPTIONS)
        form.addRow("语言:", self._language_combo)

        self._timezone_input = QLineEdit()
        self._timezone_input.setObjectName(
            OBJECT_NAMES["timezone_input"]
        )
        form.addRow("时区:", self._timezone_input)

        return group

    # ============================================================
    # 数据库组
    # ============================================================

    def _create_database_group(self) -> QGroupBox:
        """创建数据库设置组。

        Returns:
            QGroupBox: 数据库组。
        """
        group = QGroupBox(GROUP_TITLES["database"])
        group.setObjectName(OBJECT_NAMES["database_group"])
        form = QFormLayout(group)
        form.setSpacing(6)

        self._database_path_input = QLineEdit()
        self._database_path_input.setObjectName(
            OBJECT_NAMES["database_path_input"]
        )
        form.addRow("数据库路径:", self._database_path_input)

        return group

    # ============================================================
    # 备份设置组
    # ============================================================

    def _create_backup_group(self) -> QGroupBox:
        """创建备份设置组。

        Returns:
            QGroupBox: 备份设置组。
        """
        group = QGroupBox(GROUP_TITLES["backup"])
        group.setObjectName(OBJECT_NAMES["backup_group"])
        form = QFormLayout(group)
        form.setSpacing(6)

        self._backup_directory_input = QLineEdit()
        self._backup_directory_input.setObjectName(
            OBJECT_NAMES["backup_directory_input"]
        )
        form.addRow("备份目录:", self._backup_directory_input)

        self._backup_time_input = QLineEdit()
        self._backup_time_input.setObjectName(
            OBJECT_NAMES["backup_time_input"]
        )
        self._backup_time_input.setPlaceholderText("HH:MM")
        form.addRow("备份时间:", self._backup_time_input)

        self._backup_enabled_check = QCheckBox("启用自动备份")
        self._backup_enabled_check.setObjectName(
            OBJECT_NAMES["backup_enabled_check"]
        )
        form.addRow("", self._backup_enabled_check)

        self._backup_retention_spin = QSpinBox()
        self._backup_retention_spin.setObjectName(
            OBJECT_NAMES["backup_retention_spin"]
        )
        self._backup_retention_spin.setRange(1, 365)
        form.addRow("备份保留天数:", self._backup_retention_spin)

        return group

    # ============================================================
    # 上传设置组
    # ============================================================

    def _create_upload_group(self) -> QGroupBox:
        """创建上传设置组。

        Returns:
            QGroupBox: 上传设置组。
        """
        group = QGroupBox(GROUP_TITLES["upload"])
        group.setObjectName(OBJECT_NAMES["upload_group"])
        form = QFormLayout(group)
        form.setSpacing(6)

        self._upload_directory_input = QLineEdit()
        self._upload_directory_input.setObjectName(
            OBJECT_NAMES["upload_directory_input"]
        )
        form.addRow("上传目录:", self._upload_directory_input)

        self._max_image_size_spin = QSpinBox()
        self._max_image_size_spin.setObjectName(
            OBJECT_NAMES["max_image_size_spin"]
        )
        self._max_image_size_spin.setRange(1, 1024)
        self._max_image_size_spin.setSuffix(" MB")
        form.addRow("图片大小限制:", self._max_image_size_spin)

        self._max_document_size_spin = QSpinBox()
        self._max_document_size_spin.setObjectName(
            OBJECT_NAMES["max_document_size_spin"]
        )
        self._max_document_size_spin.setRange(1, 1024)
        self._max_document_size_spin.setSuffix(" MB")
        form.addRow("文档大小限制:", self._max_document_size_spin)

        self._max_video_size_spin = QSpinBox()
        self._max_video_size_spin.setObjectName(
            OBJECT_NAMES["max_video_size_spin"]
        )
        self._max_video_size_spin.setRange(1, 10240)
        self._max_video_size_spin.setSuffix(" MB")
        form.addRow("视频大小限制:", self._max_video_size_spin)

        return group

    # ============================================================
    # 通知设置组
    # ============================================================

    def _create_notification_group(self) -> QGroupBox:
        """创建通知设置组。

        Returns:
            QGroupBox: 通知设置组。
        """
        group = QGroupBox(GROUP_TITLES["notification"])
        group.setObjectName(OBJECT_NAMES["notification_group"])
        form = QFormLayout(group)
        form.setSpacing(6)

        self._receipt_delay_spin = QSpinBox()
        self._receipt_delay_spin.setObjectName(
            OBJECT_NAMES["receipt_delay_spin"]
        )
        self._receipt_delay_spin.setRange(1, 720)
        self._receipt_delay_spin.setSuffix(" 小时")
        form.addRow("收件超时提醒:", self._receipt_delay_spin)

        self._grinding_delay_spin = QSpinBox()
        self._grinding_delay_spin.setObjectName(
            OBJECT_NAMES["grinding_delay_spin"]
        )
        self._grinding_delay_spin.setRange(1, 720)
        self._grinding_delay_spin.setSuffix(" 小时")
        form.addRow("试磨超时提醒:", self._grinding_delay_spin)

        self._report_missing_spin = QSpinBox()
        self._report_missing_spin.setObjectName(
            OBJECT_NAMES["report_missing_spin"]
        )
        self._report_missing_spin.setRange(1, 720)
        self._report_missing_spin.setSuffix(" 小时")
        form.addRow("报告缺失提醒:", self._report_missing_spin)

        self._check_interval_spin = QSpinBox()
        self._check_interval_spin.setObjectName(
            OBJECT_NAMES["check_interval_spin"]
        )
        self._check_interval_spin.setRange(1, 1440)
        self._check_interval_spin.setSuffix(" 分钟")
        form.addRow("检查间隔:", self._check_interval_spin)

        return group

    # ============================================================
    # 日志设置组
    # ============================================================

    def _create_log_group(self) -> QGroupBox:
        """创建日志设置组。

        Returns:
            QGroupBox: 日志设置组。
        """
        group = QGroupBox(GROUP_TITLES["log"])
        group.setObjectName(OBJECT_NAMES["log_group"])
        form = QFormLayout(group)
        form.setSpacing(6)

        self._log_retention_spin = QSpinBox()
        self._log_retention_spin.setObjectName(
            OBJECT_NAMES["log_retention_spin"]
        )
        self._log_retention_spin.setRange(1, 3650)
        self._log_retention_spin.setSuffix(" 天")
        form.addRow("日志保留天数:", self._log_retention_spin)

        return group

    # ============================================================
    # 工具栏
    # ============================================================

    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏。

        Returns:
            QHBoxLayout: 工具栏布局。
        """
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._save_btn = QPushButton(BUTTON_TEXT["save"])
        self._save_btn.setObjectName(OBJECT_NAMES["save_btn"])
        self._save_btn.setFixedHeight(32)
        self._save_btn.clicked.connect(self._on_save)
        toolbar.addWidget(self._save_btn)

        self._refresh_btn = QPushButton(BUTTON_TEXT["refresh"])
        self._refresh_btn.setObjectName(OBJECT_NAMES["refresh_btn"])
        self._refresh_btn.setFixedHeight(32)
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)

        toolbar.addStretch()
        return toolbar

    # ============================================================
    # 公开 API：刷新
    # ============================================================

    def refresh(self) -> None:
        """刷新系统设置数据。

        唯一刷新入口。
        流程: SettingsService.get_settings() → populate_form() →
            update_status_bar() → 发射 settings_changed 信号。

        Raises:
            Exception: 刷新失败时弹出 QMessageBox 错误提示。
        """
        try:
            self._status_bar.setText(STATUS_REFRESHING)
            logger.debug("刷新系统设置")

            data = self._settings_service.get_settings()

            self._populate_form(data)
            self._update_status_bar()

            self._status_bar.setText(STATUS_REFRESHED)
            self.settings_changed.emit()
            logger.info("系统设置刷新完成")

        except Exception as e:
            self._status_bar.setText(STATUS_FAILED)
            logger.error("系统设置刷新失败: %s", e, exc_info=True)
            QMessageBox.critical(
                self,
                "错误",
                f"{MESSAGE_TEXT['refresh_failed']}: {e}",
            )

    # ============================================================
    # 填充表单
    # ============================================================

    def _populate_form(self, data: dict[str, Any]) -> None:
        """将服务器返回的配置数据填充到表单中。

        Args:
            data: GET /api/settings 返回的配置 JSON。
        """
        self._system_name_input.setText(
            str(data.get("system_name", ""))
        )
        self._company_name_input.setText(
            str(data.get("company_name", ""))
        )

        theme = str(data.get("theme", "light"))
        theme_index = self._theme_combo.findText(theme)
        if theme_index >= 0:
            self._theme_combo.setCurrentIndex(theme_index)

        language = str(data.get("language", "zh-CN"))
        lang_index = self._language_combo.findText(language)
        if lang_index >= 0:
            self._language_combo.setCurrentIndex(lang_index)

        self._timezone_input.setText(
            str(data.get("timezone", ""))
        )
        self._database_path_input.setText(
            str(data.get("database_path", ""))
        )
        self._backup_directory_input.setText(
            str(data.get("backup_directory", ""))
        )
        self._backup_time_input.setText(
            str(data.get("backup_time", ""))
        )
        self._backup_enabled_check.setChecked(
            bool(data.get("backup_enabled", True))
        )
        self._backup_retention_spin.setValue(
            int(data.get("backup_retention_days", 30))
        )
        self._upload_directory_input.setText(
            str(data.get("upload_directory", ""))
        )
        self._max_image_size_spin.setValue(
            int(data.get("max_image_size_mb", 10))
        )
        self._max_document_size_spin.setValue(
            int(data.get("max_document_size_mb", 50))
        )
        self._max_video_size_spin.setValue(
            int(data.get("max_video_size_mb", 500))
        )
        self._receipt_delay_spin.setValue(
            int(data.get("receipt_delay_hours", 48))
        )
        self._grinding_delay_spin.setValue(
            int(data.get("grinding_delay_hours", 72))
        )
        self._report_missing_spin.setValue(
            int(data.get("report_missing_hours", 24))
        )
        self._check_interval_spin.setValue(
            int(data.get("check_interval_minutes", 30))
        )
        self._log_retention_spin.setValue(
            int(data.get("log_retention_days", 90))
        )

    # ============================================================
    # 更新状态栏
    # ============================================================

    def _update_status_bar(self) -> None:
        """更新状态栏。"""
        self._status_bar.setText(STATUS_READY)

    # ============================================================
    # 保存
    # ============================================================

    def _on_save(self) -> None:
        """保存按钮回调。

        流程: 收集界面数据 → SettingsService.update_settings() →
            refresh() → 发射 settings_changed 信号。
        """
        try:
            self._status_bar.setText(STATUS_SAVING)
            logger.debug("保存系统设置")

            self._settings_service.update_settings(
                system_name=self._system_name_input.text().strip(),
                company_name=self._company_name_input.text().strip(),
                theme=self._theme_combo.currentText(),
                language=self._language_combo.currentText(),
                timezone=self._timezone_input.text().strip(),
                database_path=self._database_path_input.text().strip(),
                backup_directory=(
                    self._backup_directory_input.text().strip()
                ),
                backup_time=self._backup_time_input.text().strip(),
                backup_enabled=self._backup_enabled_check.isChecked(),
                backup_retention_days=(
                    self._backup_retention_spin.value()
                ),
                upload_directory=(
                    self._upload_directory_input.text().strip()
                ),
                max_image_size_mb=self._max_image_size_spin.value(),
                max_document_size_mb=(
                    self._max_document_size_spin.value()
                ),
                max_video_size_mb=self._max_video_size_spin.value(),
                receipt_delay_hours=self._receipt_delay_spin.value(),
                grinding_delay_hours=self._grinding_delay_spin.value(),
                report_missing_hours=(
                    self._report_missing_spin.value()
                ),
                check_interval_minutes=(
                    self._check_interval_spin.value()
                ),
                log_retention_days=self._log_retention_spin.value(),
            )

            self._status_bar.setText(STATUS_SAVED)
            QMessageBox.information(
                self,
                "提示",
                MESSAGE_TEXT["save_success"],
            )
            self.settings_changed.emit()
            self.refresh()
            logger.info("系统设置保存成功")

        except Exception as e:
            self._status_bar.setText(STATUS_FAILED)
            logger.error("系统设置保存失败: %s", e, exc_info=True)
            QMessageBox.critical(
                self,
                "错误",
                f"{MESSAGE_TEXT['save_failed']}: {e}",
            )


__all__ = [
    "SettingsView",
]
