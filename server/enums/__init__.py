"""
server.enums 包

GTMS 统一枚举定义。
所有状态值在此集中管理，禁止硬编码字符串。

枚举清单：
    TrialTaskProcessStatus  - 试磨任务流程状态
    TrialTaskResultStatus   - 试磨结果状态
    DestinationType         - 工件去向类型
    InspectionResult        - 检测结果（pass/fail）
    FileType                - 附件类型（image/document/cad/video）
    NotifyType              - 消息提醒类型（receipt_delay/grinding_delay/report_missing）
    ActionType              - 系统操作类型（create/update/delete/status_change）"""

from server.enums.task_process_status import TrialTaskProcessStatus
from server.enums.task_result_status import TrialTaskResultStatus
from server.enums.destination import DestinationType
from server.enums.inspection_result import InspectionResult
from server.enums.file_type import FileType
from server.enums.notify_type import NotifyType
from server.enums.action_type import ActionType

__all__ = [
    "TrialTaskProcessStatus",
    "TrialTaskResultStatus",
    "DestinationType",
    "InspectionResult",
    "FileType",
    "NotifyType",
    "ActionType",
]