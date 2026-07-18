"""Update client/services/__init__.py to add QueryService."""
path = 'client/services/__init__.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update docstring
content = content.replace(
    "    - dispatch_service:   桌面端工件派发管理服务",
    "    - dispatch_service:   桌面端工件派发管理服务\n    - query_service:     桌面端查询统计管理服务"
)

# Add import
content = content.replace(
    "from client.services.dispatch_service import DispatchService",
    "from client.services.dispatch_service import DispatchService\nfrom client.services.query_service import QueryService"
)

# Add to __all__
content = content.replace(
    '"DispatchService",',
    '"DispatchService",\n    "QueryService",'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')