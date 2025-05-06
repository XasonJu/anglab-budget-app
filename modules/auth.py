import streamlit as st
from modules import overview, finance, funds, projects, vendor
from modules.utils import load_data

def authenticate():
    st.image("ANG LAB LOGO.png", width=120)
    st.markdown("<h1 style='font-size:2em;margin-bottom:0;'>經費規劃器</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8em;color:gray;margin-top:0;'>made by YuCheng Xu</p>", unsafe_allow_html=True)
    st.markdown("<div style='position:absolute;top:10px;right:20px;font-size:0.9em;color:#999;'>Powered by ChatGPT</div>", unsafe_allow_html=True)

    st.markdown("---")
    password = st.text_input("請輸入密碼以登入", type="password")
    if st.button("登入"):
        if password.lower() == "ic203":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密碼錯誤，請再試一次")

def main():
    load_data()
    st.image("ANG LAB LOGO.png", width=150)
    st.markdown("<h1 style='font-size:2.2em;margin-bottom:0;'>經費規劃器</h1>", unsafe_allow_html=True)

    tabs = st.tabs(["📊 預算總覽", "💸 經費紀錄 / 規劃", "🌀 代墊永動機", "📁 計畫管理", "🏢 廠商紀錄"])
    with tabs[0]: overview.overview_view()
    with tabs[1]: finance.finance_view()
    with tabs[2]: funds.funds_view()
    with tabs[3]: projects.project_view()
    with tabs[4]: vendor.vendor_view()

def run_app():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        authenticate()
    else:
        main()
