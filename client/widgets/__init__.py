"""GTMS 桌面端可复用组件 (Client Widgets)

Sprint 5 — Task 5.5, 5.6 / Sprint 6 — Task 6.6, 6.7

提供桌面端可复用 UI 组件：
    - status_badge:  状态标签组件（StatusBadge）
    - search_bar:    全局搜索栏组件（SearchBar）
    - file_uploader: 通用文件上传组件（FileUploader）
    - image_viewer:  通用图片查看组件（ImageViewer）
"""

from client.widgets.file_uploader import FileUploader
from client.widgets.image_viewer import ImageViewer
from client.widgets.search_bar import SearchBar
from client.widgets.status_badge import StatusBadge

__all__ = [
    "FileUploader",
    "ImageViewer",
    "SearchBar",
    "StatusBadge",
]