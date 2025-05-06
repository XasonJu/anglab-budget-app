import streamlit as st
import json
import os
from datetime import datetime

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calc_cash_balance(cash_records):
    total = 0
    for r in cash_records:
        total += r["amount"] if r["type"] == "inflow" else -r["amount"]
    return total

def cash_view():
    st.header("🏦 實驗室金庫")

    records = load_json("data/lab_cash.json", [])
    balance = calc_cash_balance(records)
    st.metric("💰 目前金庫餘額", f"${balance:,.0f}")

    st.subheader("➕ 記錄金庫流入")
    with st.form("cash_inflow"):
        amt = st.number_input("金額", min_value=0.0, format="%.0f")
        src = st.text_input("來源 / 備註")
        date = st.date_input("日期", value=datetime.today())
        if st.form_submit_button("紀錄流入"):
            records.append({
                "type": "inflow",
                "amount": amt,
                "source": src,
                "date": date.strftime("%Y-%m-%d")
            })
            save_json("data/lab_cash.json", records)
            st.success("流入已紀錄")
            st.rerun()

    st.subheader("📋 流水紀錄")
    for i, r in enumerate(records[::-1]):
        label = f"{r['date']} - {r.get('source', '')} - {'+' if r['type'] == 'inflow' else '-'}${r['amount']:.0f}"
        with st.expander(label):
            st.text(f"來源 / 備註：{r.get('source', '')}")
            st.text(f"類型：{'流入' if r['type'] == 'inflow' else '支出'}")
            st.text(f"金額：${r['amount']:.0f}")
            st.text(f"日期：{r['date']}")
