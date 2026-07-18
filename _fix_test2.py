"""Fix test_query_service.py: pass check and sort checks."""
import re

path = 'tests/test_query_service.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 2: "pass" check should use regex for standalone pass keyword
old = 'check("无 pass", "pass" not in source)'
new = 'check("无 pass", not re.search(r"\\bpass\\b", extract_code_text(SOURCE_PATH)))'

content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed 2: pass check now uses regex')

# Verify the fix
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if '无 pass' in line:
        print(f'  Line {i+1}: {line.strip()[:100]}')
    if 'sort_by' in line and 'default' in line.lower():
        print(f'  Line {i+1}: {line.strip()[:100]}')