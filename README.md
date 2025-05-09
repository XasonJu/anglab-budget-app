# ANG Lab Budget App

With Google Sheets integration.

# 經費規劃器
這是一個用 Streamlit 開發的經費管理應用程式，支援預算管理、代墊永動機、計畫管理、廠商紀錄和筆記功能，並可將數據上傳至 Google Sheets。

## 功能
- 📊 預算總覽：查看各計畫的預算執行情況。
- 💸 經費紀錄與規劃：記錄實際支出和預計支出。
- 🌀 代墊永動機：管理學生代墊與報銷。
- 📁 計畫管理：新增與編輯計畫。
- 🏢 廠商紀錄：管理廠商資料與寄款金額。
- 📒 經費規劃筆記：記錄相關筆記。
- 📤 Google Sheets 整合：將本地 JSON 數據上傳至 Google Sheets。

## 運行方式
1. 安裝依賴：`pip install -r requirements.txt`
2. 運行應用程式：`streamlit run app.py`

## 部署至 Streamlit Community Cloud
1. 將程式碼推送至 GitHub 儲存庫（需為公開儲存庫）。
2. 在 Streamlit Community Cloud 中建立新應用程式，選擇 GitHub 儲存庫。
3. 設置 Google Sheets 憑證（見下方）。

## Google Sheets 憑證設置
1. 獲取 Google Cloud Platform (GCP) 服務帳戶憑證 JSON 檔案。
2. 在 Streamlit Community Cloud 中，進入「Manage app」 -> 「Secrets」，添加以下內容：