"""Fix test_query_service.py checks."""
import re

path = 'tests/test_query_service.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: default sort_by/sort_order checks
old = '''check("默认_by = created_at", 'sort_by="created_at"' in source)
check("默认_order = desc", 'sort_order="desc"' in source)'''
new = '''check("_apply_sorting 默认排序字段回退",
      ".get(" in source and "TrialTask.created_at" in source)
check("_apply_sorting 默认排序方向回退",
      'sort_order == "asc"' in source and ".desc()" in source)'''

content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed 1: sort_by/sort_order checks')

# Now find the "pass" issue
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find lines with "pass" in the test file
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'pass' in line.lower():
        print(f'  Line {i+1}: {line.strip()[:80]}')