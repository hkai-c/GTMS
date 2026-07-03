"""附件类型枚举 (FileType)

对应 DB_DESIGN.md attachments.file_type ENUM('image','document','cad','video')。

表示附件文件的分类。
"""

from enum import Enum


class FileType(str, Enum):
    """附件类型"""

    IMAGE = "image"
    """图片 — 工件照片、缺陷照片等"""

    DOCUMENT = "document"
    """文档 — 检测报告、加工记录等"""

    CAD = "cad"
    """CAD 图纸 — 产品图、工序图等"""

    VIDEO = "video"
    """视频 — 试磨过程录像等"""

    # ============================================================
    # UI 显示名映射
    # ============================================================

    @property
    def display_name(self) -> str:
        """返回中文显示名"""
        _name_map = {
            FileType.IMAGE: "图片",
            FileType.DOCUMENT: "文档",
            FileType.CAD: "CAD 图纸",
            FileType.VIDEO: "视频",
        }
        return _name_map[self]