import streamlit as st
import json
import os
from modules.utils import load_json, save_json

VENDOR_FILE = "data/vendors.json"

def load_vendors():
    if not os.path.exists(VENDOR_FILE):
        return []
    with open(VENDOR_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_vendors(data):
    with open(VENDOR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def vendor_view():
    st.header("🏢 廠商資料與寄款管理")

    vendors = load_vendors()

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

            with st.form(f"edit_{i}_{v['name']}"):
                new_deposit = st.number_input("更新寄放金額", value=v["deposit"], min_value=0.0, format="%.0f", key=f"dep_{i}_{v['name']}")
                if st.form_submit_button("儲存修改"):
                    vendors[i]["deposit"] = new_deposit
                    save_vendors(vendors)
                    st.success("已更新金額")
                    st.rerun()

    st.subheader("➕ 新增廠商")
    with st.form("add_vendor"):
        name = st.text_input("公司名稱")
        vat = st.text_input("統一編號")
        addr = st.text_input("地址")
        tel = st.text_input("電話")
        email = st.text_input("電子信箱")
        web = st.text_input("公司網站")
        rep = st.text_input("負責業務")
        note = st.text_area("備註")
        deposit = st.number_input("目前寄放金額", min_value=0.0, format="%.0f")
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
            save_vendors(vendors)
            st.success("已新增廠商")
            st.rerun()
