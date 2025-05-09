import streamlit as st
import json
import os
from datetime import datetime

# 全局常量
CATEGORIES = [
    "人事費", "業務費", "行政管理費", "雜支費",
    "設備費", "國外差旅費", "國內旅費", "資本門", "經常門"
]

# 輔助函數
def ensure_file(path, default):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

def load_json(path, default):
    try:
        ensure_file(path, default)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        st.error(f"無法讀取 {path}: {str(e)}")
        return default

def save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        st.error(f"無法寫入 {path}: {str(e)}")

def load_data():
    os.makedirs("data", exist_ok=True)
    ensure_file("data/budgets.json", [])
    ensure_file("data/expenses.json", [])
    ensure_file("data/plans.json", [])
    ensure_file("data/students.json", [])
    ensure_file("data/lab_cash.json", [])
    ensure_file("data/student_cash_log.json", [])
    ensure_file("data/vendors.json", [])
    ensure_file("data/notes.json", [])
    ensure_file("data/login_log.json", [])

# 身份驗證
def authenticate():
    try:
        st.image("ANG LAB LOGO.png", width=120)
    except FileNotFoundError:
        st.warning("未找到 ANG LAB LOGO.png，顯示預設標題")
    st.markdown("<h1 style='font-size:2em;margin-bottom:0;'>經費規劃器</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8em;color:gray;margin-top:0;'>made by YuCheng Xu</p>", unsafe_allow_html=True)

    st.markdown("---")
    password = st.text_input("請輸入密碼以登入", type="password")
    if st.button("登入"):
        if password.lower() == "ic203":
            st.session_state.jarvis_authenticated = True
            st.session_state.jarvis_username = "admin"
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            login_log = load_json("data/login_log.json", [])
            login_log.append({"username": st.session_state.jarvis_username, "login_time": login_time})
            save_json("data/login_log.json", login_log)
            st.rerun()
        else:
            st.error("密碼錯誤，請再試一次")

# 預算總覽
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
    st.markdown("## 📊 預算總覽")

    budgets = load_json("data/budgets.json", [])

    st.subheader("💰 實驗室金庫總額")
    st.metric("目前餘額", f"${get_cash_total():,.0f}")

    st.subheader("📁 各計畫執行情況")
    def get_sort_key(p):
        end = p.get("end_date", "")
        try:
            return datetime.strptime(end, "%Y-%m-%d")
        except:
            return datetime.max
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
        if st.button("✅ 已報銷", key=f"overview_convert_{i}"):
            expenses = load_json("data/expenses.json", [])
            expenses.append(plan)
            save_json("data/expenses.json", expenses)
            del plans[index]
            save_json("data/plans.json", plans)
            st.success("已轉為實際支出")
            st.rerun()

# 經費紀錄與規劃
def finance_view():
    st.header("💸 經費紀錄 / 規劃")

    expenses = load_json("data/expenses.json", [])
    plans = load_json("data/plans.json", [])
    budgets = load_json("data/budgets.json", [])
    project_names = [b["name"] for b in budgets]

    st.subheader("✅ 實際支出")
    with st.form("add_expense"):
        p1 = st.selectbox("計畫", project_names, key="finance_ep1")
        c1 = st.selectbox("分類", CATEGORIES, key="finance_ec1")
        a1 = st.number_input("金額", min_value=0.0, format="%.0f", key="finance_ea1")
        note1 = st.text_input("備註", key="finance_en1")
        d1 = st.date_input("日期", value=datetime.today(), key="finance_ed1")
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
        p2 = st.selectbox("計畫", project_names, key="finance_pp2")
        c2 = st.selectbox("分類", CATEGORIES, key="finance_pc2")
        a2 = st.number_input("金額", min_value=0.0, format="%.0f", key="finance_pa2")
        note2 = st.text_input("備註", key="finance_pn2")
        d2 = st.date_input("預計日期", value=datetime.today(), key="finance_pd2")
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
            with st.form(f"finance_edit_{uid}"):
                amt = st.number_input("金額", value=e["amount"], key=f"finance_ea_{uid}")
                note = st.text_input("備註", value=e["note"], key=f"finance_en_{uid}")
                date = st.date_input("日期", value=datetime.strptime(e["date"], "%Y-%m-%d"), key=f"finance_ed_{uid}")
                if st.form_submit_button("更新"):
                    expenses[len(expenses) - 1 - i]["amount"] = amt
                    expenses[len(expenses) - 1 - i]["note"] = note
                    expenses[len(expenses) - 1 - i]["date"] = date.strftime("%Y-%m-%d")
                    save_json("data/expenses.json", expenses)
                    st.success("已更新")
                    st.rerun()
            if st.button("❌ 刪除", key=f"finance_del_{uid}"):
                del expenses[len(expenses) - 1 - i]
                save_json("data/expenses.json", expenses)
                st.warning("已刪除")
                st.rerun()

    st.subheader("📋 規劃列表")
    for i, p in enumerate(plans[::-1]):
        uid = f"plan_{i}_{p['project']}_{p['category']}"
        with st.expander(f"{p['project']} - {p['category']} - ${p['amount']:.0f}"):
            with st.form(f"finance_edit_{uid}"):
                amt = st.number_input("金額", value=p["amount"], key=f"finance_pa_{uid}")
                note = st.text_input("備註", value=p["note"], key=f"finance_pn_{uid}")
                date = st.date_input("日期", value=datetime.strptime(p["date"], "%Y-%m-%d"), key=f"finance_pd_{uid}")
                if st.form_submit_button("更新"):
                    plans[len(plans) - 1 - i]["amount"] = amt
                    plans[len(plans) - 1 - i]["note"] = note
                    plans[len(plans) - 1 - i]["date"] = date.strftime("%Y-%m-%d")
                    save_json("data/plans.json", plans)
                    st.success("已更新")
                    st.rerun()
            if st.button("❌ 刪除", key=f"finance_del_{uid}"):
                del plans[len(plans) - 1 - i]
                save_json("data/plans.json", plans)
                st.warning("已刪除")
                st.rerun()

# 代墊永動機
def funds_view():
    lab_cash = load_json("data/lab_cash.json", [])
    lab_total = sum(c["amount"] if c["type"] == "inflow" else -c["amount"] for c in lab_cash)
    st.header("🌀 代墊永動機")
    st.metric("實驗室金庫總額", f"${lab_total:,.0f}")

    students = load_json("data/students.json", [])
    records = load_json("data/student_cash_log.json", [])

    with st.expander("➕ 新增學生"):
        with st.form("funds_add_student"):
            new_name = st.text_input("學生姓名", key="funds_new_name")
            new_balance = st.number_input("初始餘額", step=100.0, value=0.0, key="funds_new_balance")
            if st.form_submit_button("新增"):
                students.append({"name": new_name, "balance": new_balance})
                save_json("data/students.json", students)
                st.success("已新增學生")
                st.rerun()

    st.subheader("✏️ 編輯學生")
    student_names = [s["name"] for s in students]
    selected_student = st.selectbox("選擇學生", student_names if student_names else ["尚無學生"], key="funds_edit_student")
    if selected_student and selected_student != "尚無學生":
        for s in students:
            if s["name"] == selected_student:
                with st.form(f"funds_edit_student_{selected_student}_{s['name']}"):
                    new_student_name = st.text_input("學生姓名", value=s["name"], key=f"funds_edit_name_{selected_student}_{s['name']}")
                    new_student_balance = st.number_input("餘額", value=s["balance"], step=100.0, key=f"funds_edit_balance_{selected_student}_{s['name']}")
                    if st.form_submit_button("儲存修改"):
                        s["name"] = new_student_name
                        s["balance"] = new_student_balance
                        save_json("data/students.json", students)
                        st.success("已更新學生資訊")
                        st.rerun()
                break

    st.subheader("💰 學生帳戶餘額")
    for s in students:
        st.markdown(f"<div style='font-size:1.3em'><b>{s['name']}</b>：${s['balance']:.0f}</div>", unsafe_allow_html=True)

    st.subheader("🎓 學生資金異動")
    selected = st.selectbox("學生", student_names if student_names else ["尚無學生"], key="funds_action_select")
    action = st.selectbox("動作", ["代墊", "報銷", "發獎金", "手動調整"], key="funds_action_type")
    amount = st.number_input("金額", min_value=0.0, step=100.0, key="funds_amount")
    note = st.text_input("備註", key="funds_note")
    date = st.date_input("日期", value=datetime.today(), key="funds_date")

    if st.button("執行異動", key="funds_execute"):
        if selected and selected != "尚無學生":
            if action == "報銷" and lab_total < amount:
                st.error("金庫餘額不足，無法報銷")
            else:
                for s in students:
                    if s["name"] == selected:
                        if action == "代墊":
                            s["balance"] -= amount
                            records.append({
                                "name": selected,
                                "action": action,
                                "amount": -amount,
                                "note": note,
                                "date": date.strftime("%Y-%m-%d")
                            })
                        elif action == "報銷":
                            s["balance"] += amount
                            records.append({
                                "name": selected,
                                "action": action,
                                "amount": amount,
                                "note": note,
                                "date": date.strftime("%Y-%m-%d")
                            })
                            lab_cash.append({
                                "amount": amount,
                                "type": "outflow",
                                "note": f"報銷給 {selected}",
                                "date": date.strftime("%Y-%m-%d")
                            })
                            save_json("data/lab_cash.json", lab_cash)
                        elif action == "發獎金":
                            s["balance"] += amount
                            records.append({
                                "name": selected,
                                "action": action,
                                "amount": amount,
                                "note": note,
                                "date": date.strftime("%Y-%m-%d")
                            })
                            lab_cash.append({
                                "amount": amount,
                                "type": "outflow",
                                "note": f"發獎金給 {selected}",
                                "date": date.strftime("%Y-%m-%d")
                            })
                            save_json("data/lab_cash.json", lab_cash)
                        elif action == "手動調整":
                            s["balance"] = amount
                            records.append({
                                "name": selected,
                                "action": action,
                                "amount": amount,
                                "note": note,
                                "date": date.strftime("%Y-%m-%d")
                            })
                        break
                save_json("data/students.json", students)
                save_json("data/student_cash_log.json", records)
                st.success("資金異動完成")
                st.rerun()

    st.subheader("📄 資金異動紀錄")
    for i, r in enumerate(records[::-1]):
        idx = len(records) - 1 - i
        with st.expander(f"{r.get('date', '-')}: {r.get('name', '-')} - {r.get('action', '-')} - ${r.get('amount', 0):.0f}"):
            st.markdown(f"**學生**: {r.get('name', '-')}")
            st.markdown(f"**動作**: {r.get('action', '-')}")
            st.markdown(f"**金額**: ${r.get('amount', 0):.0f}")
            st.markdown(f"**備註**: {r.get('note', '-')}")
            st.markdown(f"**日期**: {r.get('date', '-')}")
            if st.button("🗑️ 刪除", key=f"funds_del_{i}_{r.get('name', '')}_{r.get('note', '')}"):
                del records[idx]
                save_json("data/student_cash_log.json", records)
                st.success("已刪除紀錄")
                st.rerun()

    with st.expander("🧰 手動調整金庫餘額"):
        with st.form("funds_adjust_cash"):
            cash_amount = st.number_input("金額", step=100.0, key="funds_cash_amount")
            cash_type = st.radio("類型", ["inflow", "outflow"], key="funds_cash_type")
            cash_note = st.text_input("備註（必填）", key="funds_cash_note")
            cash_date = st.date_input("日期", value=datetime.today(), key="funds_cash_date")
            if st.form_submit_button("新增紀錄"):
                if cash_note.strip():
                    lab_cash.append({
                        "amount": cash_amount,
                        "type": cash_type,
                        "note": cash_note,
                        "date": cash_date.strftime("%Y-%m-%d")
                    })
                    save_json("data/lab_cash.json", lab_cash)
                    records.append({
                        "name": "Lab Cash",
                        "action": "Adjustment",
                        "amount": cash_amount if cash_type == "inflow" else -cash_amount,
                        "note": cash_note,
                        "date": cash_date.strftime("%Y-%m-%d")
                    })
                    save_json("data/student_cash_log.json", records)
                    st.success("已更新金庫")
                    st.rerun()
                else:
                    st.error("備註欄位不能為空")

# 計畫管理
def calc_total_spending(project_name):
    expenses = load_json("data/expenses.json", [])
    return sum(float(e["amount"]) for e in expenses if e["project"] == project_name)

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

            with st.form(f"project_edit_{idx}"):
                new_name = st.text_input("計畫名稱", value=name, key=f"project_name_{idx}")
                new_start = st.date_input("開始日期", value=datetime.strptime(start, "%Y-%m-%d") if start else datetime.today(), key=f"project_start_{idx}")
                new_end = st.date_input("結束日期", value=datetime.strptime(end, "%Y-%m-%d") if end else datetime.today(), key=f"project_end_{idx}")
                new_cats = {}
                for cat in CATEGORIES:
                    amt = categories.get(cat, 0)
                    new_cats[cat] = st.number_input(f"{cat}", value=amt, min_value=0.0, format="%.0f", key=f"project_{cat}_{idx}")
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

            if st.button("❌ 刪除", key=f"project_del_{idx}"):
                del budgets[idx]
                save_json("data/budgets.json", budgets)
                st.warning("已刪除")
                st.rerun()

    st.subheader("➕ 新增計畫")
    with st.form("project_new_project"):
        pname = st.text_input("計畫名稱", key="project_new_name")
        start = st.date_input("開始日期", key="project_new_start")
        end = st.date_input("結束日期", key="project_new_end")
        cats = {}
        for cat in CATEGORIES:
            cats[cat] = st.number_input(f"{cat}", min_value=0.0, format="%.0f", key=f"project_new_{cat}")
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

# 廠商管理
def vendor_view():
    st.header("🏢 廠商資料與寄款管理")
    vendors = load_json("data/vendors.json", [])

    st.subheader("📋 廠商列表")
    total = sum(v["deposit"] for v in vendors)
    st.metric("總寄放金額", f"${total:,.0f}")

    for i, v in enumerate(vendors):
        with st.expander(f"{v['name']} - ${v['deposit']:.0f}"):
            st.markdown(f"📇 統編：{v['vat']}")
            st.markdown(f"🏠 地址：{v['address']}")
            st.markdown(f"📞 電話：{v['phone']}")
            st.markdown(f"📧 信箱：{v['email']}")
            st.markdown(f"🌐 網站：{v['website']}")
            st.markdown(f"👤 業務：{v['representative']}")
            st.markdown(f"📝 備註：{v['note']}")

            with st.form(f"vendor_edit_{i}_{v['name']}"):
                new_deposit = st.number_input("更新寄放金額", value=v["deposit"], min_value=0.0, format="%.0f", key=f"vendor_dep_{i}_{v['name']}")
                if st.form_submit_button("儲存修改"):
                    vendors[i]["deposit"] = new_deposit
                    save_json("data/vendors.json", vendors)
                    st.success("已更新金額")
                    st.rerun()

    st.subheader("➕ 新增廠商")
    with st.form("vendor_add_vendor"):
        name = st.text_input("公司名稱", key="vendor_name")
        vat = st.text_input("統一編號", key="vendor_vat")
        addr = st.text_input("地址", key="vendor_addr")
        tel = st.text_input("電話", key="vendor_tel")
        email = st.text_input("電子信箱", key="vendor_email")
        web = st.text_input("公司網站", key="vendor_web")
        rep = st.text_input("負責業務", key="vendor_rep")
        note = st.text_area("備註", key="vendor_note")
        deposit = st.number_input("目前寄放金額", min_value=0.0, format="%.0f", key="vendor_deposit")
        if st.form_submit_button("新增"):
            vendors.append({
                "name": name,
                "vat": vat,
                "address": addr,
                "phone": tel,
                "email": email,
                "website": web,
                "representative": rep,
                "note": note,
                "deposit": deposit
            })
            save_json("data/vendors.json", vendors)
            st.success("已新增廠商")
            st.rerun()

# 經費規劃筆記
def notes_view():
    st.header("📒 經費規劃筆記")
    notes = load_json("data/notes.json", [])

    st.subheader("➕ 新增筆記")
    with st.form("notes_add_note"):
        note_date = st.date_input("日期", value=datetime.today(), key="notes_date")
        note_content = st.text_area("筆記內容", key="notes_content")
        if st.form_submit_button("新增"):
            if note_content.strip():
                notes.append({
                    "date": note_date.strftime("%Y-%m-%d"),
                    "content": note_content,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_json("data/notes.json", notes)
                st.success("已新增筆記")
                st.rerun()
            else:
                st.error("筆記內容不能為空")

    st.subheader("📋 歷史筆記")
    for i, note in enumerate(notes[::-1]):
        idx = len(notes) - 1 - i
        with st.expander(f"{note['date']} - {note['content'][:30]}..."):
            st.markdown(f"**日期**: {note['date']}")
            st.markdown(f"**內容**: {note['content']}")
            st.markdown(f"**創建時間**: {note['created_at']}")

            with st.form(f"notes_edit_note_{idx}"):
                new_date = st.date_input("日期", value=datetime.strptime(note["date"], "%Y-%m-%d"), key=f"notes_date_{idx}")
                new_content = st.text_area("筆記內容", value=note["content"], key=f"notes_content_{idx}")
                if st.form_submit_button("更新"):
                    notes[idx]["date"] = new_date.strftime("%Y-%m-%d")
                    notes[idx]["content"] = new_content
                    save_json("data/notes.json", notes)
                    st.success("已更新筆記")
                    st.rerun()

            if st.button("❌ 刪除", key=f"notes_del_{idx}"):
                del notes[idx]
                save_json("data/notes.json", notes)
                st.warning("已刪除筆記")
                st.rerun()

# 主應用
def main():
    load_data()
    st.set_page_config("Lab Budget System", layout="wide")
    try:
        st.image("ANG LAB LOGO.png", width=150)
    except FileNotFoundError:
        st.warning("未找到 ANG LAB LOGO.png，顯示預設標題")
    st.markdown("<h1 style='font-size:2.2em;margin-bottom:0;'>經費規劃器</h1>", unsafe_allow_html=True)

    st.markdown(f"**使用者**: {st.session_state.jarvis_username}")
    login_log = load_json("data/login_log.json", [])
    if login_log:
        last_login = login_log[-1]["login_time"]
        st.markdown(f"**最近登入時間**: {last_login}")

    tabs = st.tabs(["📊 預算總覽", "💸 經費紀錄 / 規劃", "🌀 代墊永動機", "📁 計畫管理", "🏢 廠商紀錄", "📒 經費規劃筆記"])
    with tabs[0]: overview_view()
    with tabs[1]: finance_view()
    with tabs[2]: funds_view()
    with tabs[3]: project_view()
    with tabs[4]: vendor_view()
    with tabs[5]: notes_view()

if __name__ == "__main__":
    if "jarvis_authenticated" not in st.session_state:
        st.session_state.jarvis_authenticated = False
    if not st.session_state.jarvis_authenticated:
        authenticate()
    else:
        main()