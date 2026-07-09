"""GTMS 桌面端可复用组件 (Client Widgets)

Sprint 5 — Task 5.5, 5.6

提供桌面端可复用 UI 组件：
    - status_badge: 状态标签组件（StatusBadge）
    - search_bar:   全局搜索栏组件（SearchBar）
"""

from client.widgets.search_bar import SearchBar
from client.widgets.status_badge import StatusBadge

__all__ = [
    "SearchBar",
    "StatusBadge",
]