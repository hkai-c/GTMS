with open("tests/test_query_service_client.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
 lines[184]
lines[196] = 'check("export_excel body 含_by",\n'
lines[197] = '      "file_name" in source)\n'
lines[198] = 'check("export_excel 仅提交非 None_id",\n'
lines[199] = '      "if customer_id is not None:" in source)\n'
lines[200] = 'check("export_excel 仅提交非 None process_status",\n'
lines[201] = '      "if process_status is not None:" in source)\n'
lines[266] = 'check("logger.debug 使用", "logger.debug" in source)\n'
with open("tests/test_query_service_client.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Done")
