import os

test_path = os.path.join(os.path.dirname(__file__), "tests", "test_notification_schema.py")
with open(test_path, "r", encoding="utf-8") as f:
    content = f.read()

old = '    def test_zero_status_machine(self):\n        with open(self._source_path, "r", encoding="utf-8") as f:\n            source = f.read()\n        self.assertNotIn("status", source.lower())'

new = '''    def test_zero_status_machine(self):
        with open(self._source_path, "r", encoding="utf-8") as f:
            source = f.read()
        # 排除 docstring 中的 "status"（如 "Status Machine" 描述）
        lines = source.split("\\n")
        code_lines = []
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(chr(34) + chr(34) + chr(34)):
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            code_lines.append(stripped)
        code_source = "\\n".join(code_lines).lower()
        self.assertNotIn("status", code_source)'''

content = content.replace(old, new)
with open(test_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")