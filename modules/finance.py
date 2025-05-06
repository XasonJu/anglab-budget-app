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

def finance_view():
    st.header("💸 經費紀錄 / 規劃")

    expenses = load_json("data/expenses.json", [])
    plans = load_json("data/plans.json", [])
    budgets = load_json("data/budgets.json", [])
    project_names = [b["name"] for b in budgets]

    st.subheader("✅ 實際支出")
    with st.form("add_expense"):
        p1 = st.selectbox("計畫", project_names, key="ep1")
        c1 = st.selectbox("分類", CATEGORIES, key="ec1")
        a1 = st.number_input("金額", min_value=0.0, format="%.0f", key="ea1")
        note1 = st.text_input("備註", key="en1")
        d1 = st.date_input("日期", value=datetime.today(), key="ed1")
        if st.form_submit_button("新增支出"):
            expenses.append({
                "project": p1, "category": c1, "amount": a1,
                "note": note1, "date": d1.strftime("%Y-%m-%d")
            })
            save_json("data/expenses.json", expenses)
            st.success("已新增支出")
            st.rerun()

    st.subheader("📝 經費規劃（尚未執行）")
    with st.form("add_plan"):
        p2 = st.selectbox("計畫", project_names, key="pp2")
        c2 = st.selectbox("分類", CATEGORIES, key="pc2")
        a2 = st.number_input("金額", min_value=0.0, format="%.0f", key="pa2")
        note2 = st.text_input("備註", key="pn2")
        d2 = st.date_input("預計日期", value=datetime.today(), key="pd2")
        if st.form_submit_button("新增規劃"):
            plans.append({
                "project": p2, "category": c2, "amount": a2,
                "note": note2, "date": d2.strftime("%Y-%m-%d")
            })
            save_json("data/plans.json", plans)
            st.success("已新增規劃")
            st.rerun()

    st.divider()
    st.subheader("📋 支出紀錄")
    for i, e in enumerate(expenses[::-1]):
        uid = f"exp_{i}_{e['project']}_{e['category']}"
        with st.expander(f"{e['project']} - {e['category']} - ${e['amount']:.0f}"):
            with st.form(f"edit_{uid}"):
                amt = st.number_input("金額", value=e["amount"], key=f"ea_{uid}")
                note = st.text_input("備註", value=e["note"], key=f"en_{uid}")
                date = st.date_input("日期", value=datetime.strptime(e["date"], "%Y-%m-%d"), key=f"ed_{uid}")
                if st.form_submit_button("更新"):
                    expenses[len(expenses) - 1 - i]["amount"] = amt
                    expenses[len(expenses) - 1 - i]["note"] = note
                    expenses[len(expenses) - 1 - i]["date"] = date.strftime("%Y-%m-%d")
                    save_json("data/expenses.json", expenses)
                    st.success("已更新")
                    st.rerun()
            if st.button("❌ 刪除", key=f"del_{uid}"):
                del expenses[len(expenses) - 1 - i]
                save_json("data/expenses.json", expenses)
                st.warning("已刪除")
                st.rerun()

    st.subheader("📋 規劃列表")
    for i, p in enumerate(plans[::-1]):
        uid = f"plan_{i}_{p['project']}_{p['category']}"
        with st.expander(f"{p['project']} - {p['category']} - ${p['amount']:.0f}"):
            with st.form(f"edit_{uid}"):
                amt = st.number_input("金額", value=p["amount"], key=f"pa_{uid}")
                note = st.text_input("備註", value=p["note"], key=f"pn_{uid}")
                date = st.date_input("日期", value=datetime.strptime(p["date"], "%Y-%m-%d"), key=f"pd_{uid}")
                if st.form_submit_button("更新"):
                    plans[len(plans) - 1 - i]["amount"] = amt
                    plans[len(plans) - 1 - i]["note"] = note
                    plans[len(plans) - 1 - i]["date"] = date.strftime("%Y-%m-%d")
                    save_json("data/plans.json", plans)
                    st.success("已更新")
                    st.rerun()
            if st.button("❌ 刪除", key=f"del_{uid}"):
                del plans[len(plans) - 1 - i]
                save_json("data/plans.json", plans)
                st.warning("已刪除")
                st.rerun()
