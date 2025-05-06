import streamlit as st
import json
import os
from modules.utils import load_json, save_json

def funds_view():
    lab_cash = load_json("data/lab_cash.json", [])
    lab_total = sum(c["amount"] if c["type"] == "inflow" else -c["amount"] for c in lab_cash)
    st.header("🌀 代墊永動機")
    st.metric("實驗室金庫總額", f"${lab_total:,.0f}")

    students = load_json("data/students.json", [])
    records = load_json("data/student_cash_log.json", [])

    # ➕ 新增學生
    with st.expander("➕ 新增學生"):
        with st.form("add_student"):
            new_name = st.text_input("學生姓名")
            new_balance = st.number_input("初始餘額", step=100.0, value=0.0)
            if st.form_submit_button("新增"):
                students.append({"name": new_name, "balance": new_balance})
                save_json("data/students.json", students)
                st.success("已新增學生")
                st.rerun()

    # 💵 學生資金異動
    st.subheader("🎓 學生資金異動")
    student_names = [s["name"] for s in students]
    selected = st.selectbox("學生", student_names if student_names else ["尚無學生"])
    action = st.selectbox("動作", ["代墊", "報銷", "發獎金", "手動調整"])
    amount = st.number_input("金額", min_value=0.0, step=100.0)
    note = st.text_input("備註")
    date = st.date_input("日期")

    if st.button("執行異動"):
        if selected and selected != "尚無學生":
            for s in students:
                if s["name"] == selected:
                    if action == "代墊":
                        s["balance"] -= amount
                        records.append({"name": selected, "action": action, "amount": -amount, "note": note, "date": str(date)})
                    elif action == "報銷":
                        s["balance"] += amount
                        records.append({"name": selected, "action": action, "amount": amount, "note": note, "date": str(date)})
                    elif action == "發獎金":
                        records.append({"name": selected, "action": action, "amount": amount, "note": note, "date": str(date)})
                        lab_cash.append({"amount": amount, "type": "outflow", "note": f"發獎金給 {selected}", "date": str(date)})
                        save_json("data/lab_cash.json", lab_cash)
                    elif action == "手動調整":
                        s["balance"] = amount
                        records.append({"name": selected, "action": action, "amount": amount, "note": note, "date": str(date)})
                    break
            save_json("data/students.json", students)
            save_json("data/student_cash_log.json", records)
            st.success("資金異動完成")
            st.rerun()

    # 💰 各學生餘額顯示
    st.subheader("💰 學生帳戶餘額")
    for s in students:
        st.markdown(f"<div style='font-size:1.3em'><b>{s['name']}</b>：${s['balance']:.0f}</div>", unsafe_allow_html=True)

    # 🗑️ 異動紀錄
    st.subheader("📄 資金異動紀錄")
    for i, r in enumerate(records[::-1]):
        idx = len(records) - 1 - i
        with st.container():
            st.markdown(f"- **{r.get('name', '-')}**｜{r.get('action', '-')}｜${r.get('amount', 0):.0f}｜{r.get('note', '-')}｜{r.get('date', '-')}")
            if st.button("🗑️ 刪除", key=f"del_{i}_{r.get('name', '')}_{r.get('note', '')}"):
                del records[idx]
                save_json("data/student_cash_log.json", records)
                st.success("已刪除紀錄")
                st.rerun()

    # 🔧 手動調整金庫
    with st.expander("🧰 手動調整金庫餘額"):
        with st.form("adjust_cash"):
            cash_amount = st.number_input("金額", step=100.0)
            cash_type = st.radio("類型", ["inflow", "outflow"])
            cash_note = st.text_input("備註")
            cash_date = st.date_input("日期")
            if st.form_submit_button("新增紀錄"):
                lab_cash.append({
                    "amount": cash_amount,
                    "type": cash_type,
                    "note": cash_note,
                    "date": str(cash_date)
                })
                save_json("data/lab_cash.json", lab_cash)
                st.success("已更新金庫")
                st.rerun()
