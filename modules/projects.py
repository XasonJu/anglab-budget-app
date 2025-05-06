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

def calc_total_spending(project_name):
    expenses = load_json("data/expenses.json", [])
    total = sum(float(e["amount"]) for e in expenses if e["project"] == project_name)
    return total

def project_view():
    st.header("📁 計畫清單")

    budgets = load_json("data/budgets.json", [])

    st.subheader("📊 現有計畫")
    for idx, proj in enumerate(budgets):
        name = proj["name"]
        categories = proj.get("categories", {})
        start = proj.get("start_date", "")
        end = proj.get("end_date", "")
        total_budget = sum(categories.values())
        spent = calc_total_spending(name)
        remaining = total_budget - spent
        percent = min(int(spent / total_budget * 100), 100) if total_budget > 0 else 0

        with st.expander(f"📁 {name}"):
            st.text(f"預算總額：${total_budget:.0f}")
            st.progress(percent)
            st.text(f"已花費：${spent:.0f} / 剩餘：${remaining:.0f}")
            st.text(f"期間：{start or '未設定'} ➜ {end or '未設定'}")

            with st.form(f"edit_{idx}"):
                new_name = st.text_input("計畫名稱", value=name, key=f"name_{idx}")
                new_start = st.date_input("開始日期", value=datetime.strptime(start, "%Y-%m-%d") if start else datetime.today(), key=f"start_{idx}")
                new_end = st.date_input("結束日期", value=datetime.strptime(end, "%Y-%m-%d") if end else datetime.today(), key=f"end_{idx}")
                new_cats = {}
                for cat in CATEGORIES:
                    amt = categories.get(cat, 0)
                    new_cats[cat] = st.number_input(f"{cat}", value=amt, min_value=0.0, format="%.0f", key=f"{cat}_{idx}")
                submit = st.form_submit_button("更新")
                if submit:
                    budgets[idx] = {
                        "name": new_name,
                        "start_date": new_start.strftime("%Y-%m-%d"),
                        "end_date": new_end.strftime("%Y-%m-%d"),
                        "categories": new_cats
                    }
                    save_json("data/budgets.json", budgets)
                    st.success("已更新")
                    st.rerun()

            if st.button("❌ 刪除", key=f"del_{idx}"):
                del budgets[idx]
                save_json("data/budgets.json", budgets)
                st.warning("已刪除")
                st.rerun()

    st.subheader("➕ 新增計畫")
    with st.form("new_project"):
        pname = st.text_input("計畫名稱")
        start = st.date_input("開始日期")
        end = st.date_input("結束日期")
        cats = {}
        for cat in CATEGORIES:
            cats[cat] = st.number_input(f"{cat}", min_value=0.0, format="%.0f", key=f"new_{cat}")
        submit = st.form_submit_button("新增")
        if submit:
            budgets.append({
                "name": pname,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "categories": cats
            })
            save_json("data/budgets.json", budgets)
            st.success("計畫已新增")
            st.rerun()
