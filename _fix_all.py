with open("tests/test_query_service_client.py","r",encoding="utf-8") as f:
    lines = f.readlines()

# Fix HTTP Mapping (lines 136-147, 0-indexed: 135-146)
# Line 136: label
lines[135] = 'check("list_tasks -> GET /api/query",\n'
# Line 137: code
lines[136] = '      ' + chr(34) + 'get("/api/query"' + chr(34) + ' in code)\n'
# Line 138: label
lines[137] = 'check("get_statistics -> GET /api/query/statistics",\n'
# Line 139: code
lines[138] = '      ' + chr(34) + 'get("/api/query/statistics"' + chr(34) + ' in code)\n'
# Line 140: label
lines[139] = 'check("get_customer_ranking -> GET /api/query/ranking/customers",\n'
# Line 141: code
lines[140] = '      ' + chr(34) + 'get("/api/query/ranking/customers"' + chr(34) + ' in code)\n'
# Line 142: label
lines[141] = 'check("get_machine_ranking -> GET /api/query/ranking/machines",\n'
# Line 143: code
lines[142] = '      ' + chr(34) + 'get("/api/query/ranking/machines"' + chr(34) + ' in code)\n'
# Line 144: label
lines[143] = 'check("export_excel -> POST /api/query/export",\n'
# Line 145: code
lines[144] = '      ' + chr(34) + 'post("/api/query/export"' + chr(34) + ' in code)\n'

# Fix Query params (line 185, 0-indexed: 184)
lines[184] = 'check("list_tasks u4ec5u63d0u4ea4u975e None_id",\n'

# Fix Body params (lines 199-204, 0-indexed: 198-203)
lines[198] = 'check("export_excel body u542b sort_by",\n'
lines[199] = 'check("export_excel u4ec5u63d0u4ea4u975e None_id",\n'
lines[201] = 'check("export_excel u4ec5u63d0u4ea4u975e None process_status",\n'

# Fix logger.info -> logger.debug (line 268, 0-indexed: 267)
lines[267] = 'check("logger.debug u4f7fu7528", "logger.debug" in source)\n'

with open("tests/test_query_service_client.py","w",encoding="utf-8") as f:
    f.writelines(lines)
print("Done")
