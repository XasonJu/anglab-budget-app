import streamlit as st
from modules import overview, finance, funds, projects
from modules.utils import load_data

def main():
    st.set_page_config("Lab Budget System", layout="wide")
    load_data()

    tabs = st.tabs(["📊 預算總覽", "💸 經費紀錄 / 規劃", "🌀 代墊永動機", "📁 計畫管理"])

    with tabs[0]:
        overview.overview_view()
    with tabs[1]:
        finance.finance_view()
    with tabs[2]:
        funds.funds_view()
    with tabs[3]:
        projects.project_view()
