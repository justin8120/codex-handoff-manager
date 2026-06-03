# FastAPI 後端

這個後端提供智慧飲食建議系統的 OpenAI 餐點分析 API、餐點資料集儲存與推薦 API。OpenAI API Key 只放在後端環境變數，不可放在前端或 commit 到 git。

## 啟動方式

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# 在 .env 填入 OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

macOS / Linux 可使用：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 在 .env 填入 OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key，必填才能執行真 AI 分析。
- `OPENAI_MODEL`: 預設 `gpt-4.1-mini`。
- `FRONTEND_ORIGIN`: 前端開發網址，預設 `http://localhost:5173`。

## API Endpoints

- `GET /api/health`: 回傳後端狀態與 OpenAI API 是否已設定。
- `POST /api/analyze/text`: 使用文字描述呼叫 OpenAI Responses API 分析餐點。
- `POST /api/analyze/image`: 上傳餐點圖片並呼叫 OpenAI vision 分析。
- `POST /api/analyze/url`: 擷取單一 URL 的 title、description 與主要文字，再交給 OpenAI 分析。
- `GET /api/meals`: 回傳 JSON 檔案中的餐點資料集。
- `POST /api/meals`: 將 AI 分析結果加入資料集並寫回 `backend/data/meals.json`。
- `POST /api/recommend`: 依健康目標、標籤、禁忌食材與關鍵字推薦餐點。

## Tests

```bash
pytest
```

測試不會真的呼叫 OpenAI API；未設定 `OPENAI_API_KEY` 時會檢查 API 是否回傳清楚錯誤訊息。
