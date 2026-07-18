with open("tests/test_query_service_client.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Fix HTTP Mapping (lines 136-147, 0-indexed: 135-146)
# Replace each 2-line check (label + code) with new versions
# Line 136-137: list_tasks
lines[135] = "check(" + chr(34) + "list_tasks -> GET /api/query" + chr(34) + ",\n"
lines[136] = "      " + chr(34) + "get" + chr(34) + " in code)\n"

# Line 138-139: get_statistics  
lines[137] = "check(" + chr(34) + "get_statistics -> GET /api/query/statistics" + chr(34) + ",\n"
lines[138] = "      " + chr(34) + "get" + chr(34) + " in code)\n"

# Line 140-141: get_customer_ranking
lines[139] = "check(" + chr(34) + "get_customer_ranking -> GET /api/query/ranking/customers" + chr(34) + ",\n"
lines[140] = "      " + chr(34) + "get" + chr(34) + " in code)\n"

# Line 142-143: get_machine_ranking
lines[141] = "check(" + chr(34) + "get_machine_ranking -> GET /api/query/ranking/machines" + chr(34) + ",\n"
lines[142] = "      " + chr(34) + "get" + chr(34) + " in code)\n"

# Line 144-145: export_excel
lines[143] = "check(" + chr(34) + "export_excel -> POST /api/query/export" + chr(34) + ",\n"
lines[144] = "      " + chr(34) + "post" + chr(34) + " in code)\n"

# Fix Query params (line 185)
lines[184] = "check(" + chr(34) + "list_tasks u4ec5u63d0u4ea4u975e None_id" + chr(34) + ",\n"

# Fix Body params (lines 199-204)
lines[198] = "check(" + chr(34) + "export_excel body u542b_by" + chr(34) + ",\n"
lines[199] = "      " + chr(34) + "file_name" + chr(34) + " in source)\n"
lines[200] = "check(" + chr(34) + "export_excel u4ec5u63d0u4ea4u975e None_id" + chr(34) + ",\n"
lines[201] = "      " + chr(34) + "if_id is not None:" + chr(34) + " in source)\n"
lines[202] = "check(" + chr(34) + "export_excel u4ec5u63d0u4ea4u975e None process_status" + chr(34) + ",\n"
lines[203] = "      " + chr(34) + "if process_status is not None:" + chr(34) + " in source)\n"

# Fix logger (line 268)
lines[267] = "check(" + chr(34) + "logger.debug u4f7fu7528" + chr(34) + ", " + chr(34) + "logger.debug" + chr(34) + " in source)\n"

with open("tests/test_query_service_client.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Done")
