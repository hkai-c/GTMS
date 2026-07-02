"""
server.enums 包

GTMS 统一枚举定义。
所有状态值在此集中管理，禁止硬编码字符串。

枚举清单：
    TrialTaskProcessStatus  - 试磨任务流程状态
    TrialTaskResultStatus   - 试磨结果状态
    DestinationType         - 工件去向类型
"""

from server.enums.task_process_status import TrialTaskProcessStatus
from server.enums.task_result_status import TrialTaskResultStatus
from server.enums.destination import DestinationType

__all__ = [
    "TrialTaskProcessStatus",
    "TrialTaskResultStatus",
    "DestinationType",
]