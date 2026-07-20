import os

schema_path = os.path.join(os.path.dirname(__file__), "server", "schemas", "notification_schema.py")
with open(schema_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: NotificationUpdate - add extra='forbid'
old = """    model_config = ConfigDict(
        from_attributes=True,
    )

    is_read: Optional[bool] = Field(
        default=None,
        description="是否已读",
    )"""

new = """    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    is_read: Optional[bool] = Field(
        default=None,
        description="是否已读",
    )"""

content = content.replace(old, new)

with open(schema_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")