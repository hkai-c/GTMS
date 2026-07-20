import os

init_path = os.path.join(
    os.path.dirname(__file__), "server", "schemas", "__init__.py"
)

with open(init_path, "r", encoding="utf-8") as f:
    content = f.read()

# 添加 notification_schema import
old_import = """from server.schemas.log_schema import (
    LogBase,
    LogResponse,
    LogListResponse,
    LogQuery,
)"""

new_import = """from server.schemas.log_schema import (
    LogBase,
    LogResponse,
    LogListResponse,
    LogQuery,
)
from server.schemas_notification_schema import (
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationQuery,
)"""

content = content.replace(old_import, new_import)

# 添加到 __all__
old_export = """    # Log
    "LogBase",
    "LogResponse",
    "LogListResponse",
    "LogQuery",
]"""

new_export = """    # Log
    "LogBase",
    "LogResponse",
    "LogListResponse",
    "LogQuery",
    # Notification
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationQuery",
]"""

content = content.replace(old_export, new_export)

with open(init_path, "w", encoding="utf-8") as f:
    f.write(content)

print("OK")