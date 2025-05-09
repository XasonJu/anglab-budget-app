import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import pandas as pd

# 初始化 Google Sheet 客戶端
def get_sheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)
    return client

# 載入 JSON 檔案並轉成 DataFrame
def load_json_to_df(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def upload_to_sheet(sheet, sheet_name, df):
    try:
        worksheet = sheet.worksheet(sheet_name)
        sheet.del_worksheet(worksheet)
    except:
        pass
    worksheet = sheet.add_worksheet(title=sheet_name, rows=str(len(df)+10), cols=str(len(df.columns)+5))
    worksheet.update([df.columns.tolist()] + df.fillna("").astype(str).values.tolist())

def main():
    st.title("📤 上傳本地 JSON 到 Google Sheet")
    sheet_id = "1GnoZuEm6PI8421qSJ471vrsINsAulApXsmYvBQz6gHU"
    sheet = get_sheet_client().open_by_key(sheet_id)

    st.success("✅ 成功連線 Google Sheet")

    file_map = {
        "budgets.json": "budgets",
        "expenses.json": "expenses",
        "lab_cash.json": "lab_cash",
        "plans.json": "plans",
        "student_cash_log.json": "student_cash_log",
        "students.json": "students",
        "vendors.json": "vendors",
        "notes.json": "notes",          # 新增
        "login_log.json": "login_log"   # 新增
    }

    json_dir = Path("data")  # 改成與 app.py 一致的路徑
    if not json_dir.exists():
        st.error("⚠️ 找不到 data 目錄，請上傳資料或建資料夾")
        return

    for file, sheet_name in file_map.items():
        json_path = json_dir / file
        if json_path.exists():
            df = load_json_to_df(json_path)
            upload_to_sheet(sheet, sheet_name, df)
            st.success(f"✅ 上傳 {file} -> Sheet: {sheet_name}")
        else:
            st.warning(f"⚠️ 缺少 {file}")

if __name__ == "__main__":
    main()