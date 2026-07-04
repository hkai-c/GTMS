"""
server.utils 包

GTMS 工具模块，包含：
    - id_generator: 任务编号生成器
"""

from server.utils.id_generator import generate_task_no

__all__ = [
    "generate_task_no",
]