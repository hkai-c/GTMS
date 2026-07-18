with open("tests/test_query_service_client.py", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace('\"_name\" in source)', '"sort_by\" in source)')
with open("tests/test_query_service_client.py", "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed")
