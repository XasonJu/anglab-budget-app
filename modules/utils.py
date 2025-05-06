import os
import json

def ensure_file(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

def load_data():
    os.makedirs("data", exist_ok=True)
    ensure_file("data/budgets.json", [])
    ensure_file("data/expenses.json", [])
    ensure_file("data/students.json", [])
    ensure_file("data/lab_cash.json", [])
    ensure_file("data/student_cash_log.json", [])


def save_json(path, data):
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path, default):
    import os, json
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
