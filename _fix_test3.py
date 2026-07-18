"""Fix test_query_service.py line 217-218."""
path = 'tests/test_query_service.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Print lines 215-220 for reference
for i in range(214, 220):
    print(f'{i+1}: {repr(lines[i])}')

# Fix lines 217-218 (0-indexed: 216-217)
old_217 = lines[216]
old_218 = lines[217]
print(f'\nOld 217: {old_217.strip()}')
print(f'Old 218: {old_218.strip()}')

lines[216] = '''check("_apply_sorting 默认排序字段回退",
      ".get(" in source and "TrialTask.created_at" in source)
'''
lines[217] = '''check("_apply_sorting 默认排序方向回退",
      'sort_order == "asc"' in source and ".desc()" in source)
'''

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('\nFixed!')