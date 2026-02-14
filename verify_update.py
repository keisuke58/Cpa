
import json
import os

# Verify vocab.json
if os.path.exists("assets/vocab.json"):
    with open("assets/vocab.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for category, items in data.items():
            print(f"{category}: {len(items)} items")
else:
    print("assets/vocab.json does not exist")

# Verify app.py syntax
try:
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    compile(content, "app.py", "exec")
    print("app.py syntax is valid")
except Exception as e:
    print(f"app.py syntax error: {e}")
