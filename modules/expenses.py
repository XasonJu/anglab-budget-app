import streamlit as st
import json
import os
from datetime import datetime

CATEGORIES = [
    "人事費", "業務費", "行政管理費", "雜支費",
    "設備費", "國外差旅費", "國內旅費", "資本門", "經常門"
]

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def expense_view():
    st.header("💸 經費紀錄")

    expenses = load_json("data/expenses.json", [])
    budgets = load_json("data/budgets.json", [])

    project_names = [p["name"] for p in budgets]

    st.subheader("➕ 新增支出紀錄")
    with st.form("add_expense"):
        project = st.selectbox("計畫名稱", project_names)
        category = st.selectbox("支出類別", CATEGORIES)
        amount = st.number_input("金額", min_value=0.0, format="%.0f")
        note = st.text_input("備註")
        date = st.date_input("日期", value=datetime.today())
        if st.form_submit_button("新增支出"):
            expenses.append({
                "project": project,
                "category": category,
                "amount": amount,
                "note": note,
                "date": date.strftime("%Y-%m-%d")
            })
            save_json("data/expenses.json", expenses)
            st.success("已新增支出紀錄")
            st.rerun()

    st.subheader("📋 支出紀錄列表")
    for i, e in enumerate(expenses[::-1]):
        unique_id = f"{e['project']}_{e['category']}_{e['amount']}_{e['date']}_{i}"
        with st.expander(f"{e['project']} - {e['category']} - ${e['amount']:.0f}"):
            st.text(f"🗓 日期：{e['date']}")
            st.text(f"📝 備註：{e['note']}")

            with st.form(f"edit_{unique_id}"):
                new_amount = st.number_input("金額", value=float(e["amount"]), key=f"amount_{unique_id}")
                new_note = st.text_input("備註", value=e["note"], key=f"note_{unique_id}")
                new_date = st.date_input("日期", value=datetime.strptime(e["date"], "%Y-%m-%d"), key=f"date_{unique_id}")
                if st.form_submit_button("儲存修改"):
                    target_index = len(expenses) - 1 - i  # 因為是 reversed 顯示
                    expenses[target_index]["amount"] = new_amount
                    expenses[target_index]["note"] = new_note
                    expenses[target_index]["date"] = new_date.strftime("%Y-%m-%d")
                    save_json("data/expenses.json", expenses)
                    st.success("已更新")
                    st.rerun()

            if st.button("❌ 刪除", key=f"del_{unique_id}"):
                del expenses[len(expenses) - 1 - i]
                save_json("data/expenses.json", expenses)
                st.warning("已刪除")
                st.rerun()
