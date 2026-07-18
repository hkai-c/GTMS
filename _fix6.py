with open("tests/test_query_service_client.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Fix [7] HTTP Mapping - replace 5 checks (lines 136-146, 0-indexed: 135-145)
# Each check is 2 lines (label + code line)
new_http = [
    'check("list_tasks -> GET /api/query",\n',
    '      "get" in code)\n',
    'check("get_statistics -> GET /api/query/statistics",\n',
    '      "get" in code)\n',
    'check("get_customer_ranking -> GET /api/query/ranking/customers",\n',
    '      "get" in code)\n',
    'check("get_machine_ranking -> GET /api/query/ranking/machines",\n',
    '      "get" in code)\n',
    'check("export_excel -> POST /api/query/export",\n',
    '      "post" in code)\n',
]
lines[135:146] = new_http

# Fix [12] Query params line 185 (0-indexed: 184) - just the label
lines[184] = 'check("list_tasks u4ec5u63d0u4ea4u975e None_id",\n'

# Fix [13] Body params - replace lines 198-205 (0-indexed: 197-204) with 3 checks
new_body = [
    'check("export_excel body u542b_by",\n',
    '      "file_name" in source)\n',
    'check("export_excel u4ec5u63d0u4ea4u975e None_id",\n',
    '      "if_id is not None:" in source)\n',
    'check("export_excel u4ec5u63d0u4ea4u975e None process_status",\n',
    '      "if process_status is not None:" in source)\n',
]
lines[196:204] = new_body

# Fix [20] logger line 268 (0-indexed: 267)
lines[267] = 'check("logger.debug u4f7fu7528", "logger.debug" in source)\n'

with open("tests/test_query_service_client.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Done")
