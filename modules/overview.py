from datetime import datetime
import streamlit as st
import json
from modules.utils import save_json
import os

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_spending(project_name):
    expenses = load_json("data/expenses.json", [])
    return sum(e["amount"] for e in expenses if e["project"] == project_name)

def get_planned(project_name):
    plans = load_json("data/plans.json", [])
    return sum(p["amount"] for p in plans if p["project"] == project_name)

def get_cash_total():
    cash = load_json("data/lab_cash.json", [])
    return sum(c["amount"] if c["type"] == "inflow" else -c["amount"] for c in cash)

def render_multicolor_bar(percent_spent, percent_plan):
    green_width = int(percent_spent * 100)
    yellow_width = int(percent_plan * 100)
    return f"""
    <div style='background:#eee;width:100%;border-radius:6px;height:20px;overflow:hidden;border:1px solid #ccc'>
        <div style='width:{green_width}%;background:#4caf50;height:100%;float:left'></div>
        <div style='width:{yellow_width}%;background:#ffeb3b;height:100%;float:left'></div>
    </div>
    """

def overview_view():
    st.markdown("<p style='font-size: 0.8em; color: gray;'>made by YuCheng Xu</p>", unsafe_allow_html=True)
    st.markdown("<div style='position:absolute;top:10px;right:20px;font-size:0.9em;color:#999;'>Powered by ChatGPT</div>", unsafe_allow_html=True)
    st.markdown("## 📊 預算總覽")

    budgets = load_json("data/budgets.json", [])

    st.subheader("💰 實驗室金庫總額")
    st.metric("目前餘額", f"${get_cash_total():,.0f}")

    st.subheader("📁 各計畫執行情況")
        # 依照到期日排序，最早到期在最前面
    def get_sort_key(p):
        end = p.get("end_date", "")
        try:
            return datetime.strptime(end, "%Y-%m-%d")
        except:
            return datetime.max  # 無日期的排最後
    budgets.sort(key=get_sort_key)
    for proj in budgets:

        name = proj["name"]
        cat = proj.get("categories", {})
        total_budget = sum(cat.values())
        spent = get_spending(name)
        planned = get_planned(name)
        remaining = total_budget - spent - planned

        percent_spent = spent / total_budget if total_budget > 0 else 0
        percent_plan = planned / total_budget if total_budget > 0 else 0
        percent_total = percent_spent + percent_plan
        if percent_total > 1:
            percent_plan = 1 - percent_spent
            percent_total = 1

                # 驗算距離結束的月份
        end_date_str = proj.get("end_date", "")
        expiry_note = ""
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                today = datetime.today()
                months_left = (end_date.year - today.year) * 12 + (end_date.month - today.month)
                if 0 <= months_left <= 2:
                    expiry_note = " ⚠️" * (3 - months_left)
            except:
                pass
        st.markdown(f"### {name}{expiry_note}")

        st.markdown(render_multicolor_bar(percent_spent, percent_plan), unsafe_allow_html=True)
        st.text(f"實際執行率：{percent_spent*100:.1f}%")
        st.text(f"預計執行率：{percent_plan*100:.1f}%")
        st.text(f"總執行率：{percent_total*100:.1f}%")
        st.text(f"預算：${total_budget:.0f} ｜ 已花：${spent:.0f} ｜ 預計：${planned:.0f} ｜ 剩餘：${remaining:.0f}")

    st.subheader("📝 規劃支出清單")
    plans = load_json("data/plans.json", [])
    for i, plan in enumerate(plans[::-1]):
        index = len(plans) - 1 - i
        st.markdown(f"- **{plan['project']}** | {plan['category']} | ${plan['amount']:.0f} | {plan['note']} | {plan['date']}")
        if st.button("✅ 已報銷", key=f"convert_{i}"):
            expenses = load_json("data/expenses.json", [])
            expenses.append(plan)
            save_json("data/expenses.json", expenses)
            del plans[index]
            save_json("data/plans.json", plans)
            st.success("已轉為實際支出")
            st.rerun()