import os
import shutil

init_path = os.path.join(os.path.dirname(__file__), "server", "schemas", "__init__.py")
bak_path = os.path.join(os.path.dirname(__file__), "server", "schemas", "__init__.py.bak")

# Backup
shutil.copy(init_path, bak_path)

with open(init_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the notification_schema import block
old_import = """
from server.schemasification_schema import (
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationQuery,
)
"""
content = content.replace(old_import, "\n")

# Remove from __all__
old_export = """    # Notification
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationQuery",
"""
content = content.replace(old_export, "")

with open(init_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done - removed notification_schema from __init__.py")