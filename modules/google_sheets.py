import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_gsheet(sheet_key):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_key)
    return sheet
