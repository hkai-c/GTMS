with open("tests/test_query_service_client.py","r",encoding="utf-8") as f:
    lines = f.readlines()

# Fix HTTP Mapping - use single quotes for outer string
lines[135] = "check(" + chr(34) + "list_tasks -> GET /api/query" + chr(34) + ",\n"
lines[136] = "      " + chr(39) + "get(" + chr(34) + "/api/query" + chr(34) + chr(39) + " in code)\n"
lines[137] = "check(" + chr(34) + "get_statistics -> GET /api/query/statistics" + chr(34) + ",\n"
lines[138] = "      " + chr(39) + "get(" + chr(34) + "/api/query/statistics" + chr(34) + chr(39) + " in code)\n"
lines[139] = "check(" + chr(34) + "get_customer_ranking -> GET /api/query/ranking/customers" + chr(34) + ",\n"
lines[140] = "      " + chr(39) + "get(" + chr(34) + "/api/query/ranking/customers" + chr(34) + chr(39) + " in code)\n"
lines[141] = "check(" + chr(34) + "get_machine_ranking -> GET /api/query/ranking/machines" + chr(34) + ",\n"
lines[142] = "      " + chr(39) + "get(" + chr(34) + "/api/query/ranking/machines" + chr(34) + chr(39) + " in code)\n"
lines[143] = "check(" + chr(34) + "export_excel -> POST /api/query/export" + chr(34) + ",\n"
lines[144] = "      " + chr(39) + "post(" + chr(34) + "/api/query/export" + chr(34) + chr(39) + " in code)\n"

# Fix Query params
lines[184] = "check(" + chr(34) + "list_tasks u4ec5u63d0u4ea4u975e None_id" + chr(34) + ",\n"

# Fix Body params
lines[198] = "check(" + chr(34) + "export_excel body u542b_by" + chr(34) + ",\n"
lines[199] = "check(" + chr(34) + "export_excel u4ec5u63d0u4ea4u975e None_id" + chr(34) + ",\n"
lines[201] = "check(" + chr(34) + "export_excel u4ec5u63d0u4ea4u975e None process_status" + chr(34) + ",\n"

# Fix logger
lines[267] = "check(" + chr(34) + "logger.debug u4f7fu7528" + chr(34) + ", " + chr(34) + "logger.debug" + chr(34) + " in source)\n"

with open("tests/test_query_service_client.py","w",encoding="utf-8") as f:
    f.welines(lines)
print("Done")
