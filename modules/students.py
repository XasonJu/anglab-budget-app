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

def student_view():
    st.header("👨‍🎓 學生帳戶")

    students = load_json("data/students.json", [])
    log = load_json("data/student_cash_log.json", [])

    student_names = [s["name"] for s in students]

    # 顯示餘額
    st.subheader("學生餘額")
    for s in students:
        st.metric(label=s["name"], value=f"${s['balance']:.0f}")

    st.divider()

    # ➕ 增加學生（初始餘額為 0）
    with st.expander("➕ 新增學生"):
        new_name = st.text_input("學生姓名")
        if st.button("新增學生"):
            if new_name and new_name not in student_names:
                students.append({"name": new_name, "balance": 0})
                save_json("data/students.json", students)
                st.success("已新增")
                st.rerun()

    # ➖ 代墊支出（扣學生錢）
    st.subheader("🧾 代墊支出")
    with st.form("advance_form"):
        sname = st.selectbox("學生", student_names, key="advance_name")
        amt = st.number_input("金額", min_value=0.0, format="%.0f", key="advance_amt")
        note = st.text_input("備註", key="advance_note")
        date = st.date_input("日期", key="advance_date", value=datetime.today())
        if st.form_submit_button("紀錄代墊"):
            for s in students:
                if s["name"] == sname:
                    s["balance"] -= amt
                    break
            log.append({
                "student": sname,
                "type": "代墊",
                "amount": -amt,
                "note": note,
                "date": date.strftime("%Y-%m-%d")
            })
            save_json("data/students.json", students)
            save_json("data/student_cash_log.json", log)
            st.success("已紀錄代墊")
            st.rerun()

    # ✅ 報銷（加錢）
    st.subheader("✅ 報銷 / 發還")
    with st.form("reimburse_form"):
        sname = st.selectbox("學生", student_names, key="reb_name")
        amt = st.number_input("金額", min_value=0.0, format="%.0f", key="reb_amt")
        note = st.text_input("備註", key="reb_note")
        date = st.date_input("日期", key="reb_date", value=datetime.today())
        if st.form_submit_button("報銷"):
            for s in students:
                if s["name"] == sname:
                    s["balance"] += amt
                    break
            log.append({
                "student": sname,
                "type": "報銷",
                "amount": amt,
                "note": note,
                "date": date.strftime("%Y-%m-%d")
            })
            save_json("data/students.json", students)
            save_json("data/student_cash_log.json", log)
            st.success("報銷成功")
            st.rerun()

    # 🎁 發獎金
    st.subheader("🎁 發獎金")
    with st.form("bonus_form"):
        sname = st.selectbox("學生", student_names, key="bonus_name")
        amt = st.number_input("金額", min_value=0.0, format="%.0f", key="bonus_amt")
        note = st.text_input("備註", key="bonus_note")
        date = st.date_input("日期", key="bonus_date", value=datetime.today())
        if st.form_submit_button("發獎金"):
            for s in students:
                if s["name"] == sname:
                    s["balance"] += amt
                    break
            log.append({
                "student": sname,
                "type": "獎金",
                "amount": amt,
                "note": note,
                "date": date.strftime("%Y-%m-%d")
            })
            save_json("data/students.json", students)
            save_json("data/student_cash_log.json", log)
            st.success("獎金已發放")
            st.rerun()
