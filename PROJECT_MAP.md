# Project Map

## Project

智慧飲食建議系統現在包含前端與後端。前端負責使用者介面、離線展示模式與 GitHub Pages 靜態部署；FastAPI 後端負責 OpenAI Responses API 餐點分析、URL 擷取、圖片分析、餐點資料 JSON 儲存與推薦 API。

## Frontend Files

- `src/App.tsx`: 主要 UI、後端狀態、AI 分析表單、資料集載入、推薦流程、離線展示模式與查詢紀錄。
- `src/api.ts`: 前端 API client，呼叫 `/api/health`、`/api/meals`、`/api/analyze/*`、`/api/recommend`。
- `src/mealData.ts`: 前端離線展示資料與型別。
- `src/styles.css`: 響應式版面、AI 分析區、推薦表單、餐點卡片、資料集與查詢紀錄樣式。
- `src/App.test.tsx`: mock API 的前端 component tests。
- `scripts/browser-walkthrough.mjs`: production build 的瀏覽器走查，驗證離線展示模式與推薦流程。

## Backend Structure

- `backend/app/main.py`: FastAPI app、CORS、health、analyze、meals、recommend endpoints。
- `backend/app/models.py`: Pydantic models：`MealAnalysisResult`、`TextAnalyzeRequest`、`UrlAnalyzeRequest`、`RecommendRequest`。
- `backend/app/services/openai_meal_analyzer.py`: OpenAI Python SDK + Responses API 串接，使用 JSON schema 要求模型回傳結構化 JSON。
- `backend/app/services/url_fetcher.py`: 使用 httpx + BeautifulSoup 擷取單一 URL 的 title、meta description 與主要文字。
- `backend/app/storage/meals_store.py`: JSON 檔案資料讀寫與推薦篩選。
- `backend/data/meals.json`: 9 筆預設餐點資料與後續新增 AI 分析結果。
- `backend/tests/test_api.py`: FastAPI endpoint tests，不實際呼叫 OpenAI API。
- `backend/requirements.txt`: 後端 Python 依賴。
- `backend/.env.example`: 後端環境變數範例。
- `backend/README.md`: 後端啟動、測試與 endpoint 說明。

## API Endpoints

- `GET /api/health`
- `POST /api/analyze/text`
- `POST /api/analyze/image`
- `POST /api/analyze/url`
- `GET /api/meals`
- `POST /api/meals`
- `POST /api/recommend`

## OpenAI Flow

後端從 `.env` 讀取 `OPENAI_API_KEY` 與 `OPENAI_MODEL`。`openai_meal_analyzer.py` 使用 OpenAI Python SDK 的 Responses API，並要求模型只回傳符合 `MealAnalysisResult` schema 的 JSON，不回傳 markdown。若 `OPENAI_API_KEY` 未設定，分析 API 回傳清楚錯誤：

```text
AI analysis service is not configured. Please set OPENAI_API_KEY.
```

OpenAI API Key 不可放在前端，也不可 commit 到 git。

## Validation

- Frontend: `npm run validate`
- Backend: `cd backend && pip install -r requirements.txt && pytest`

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
- FastAPI backend needs separate production deployment before GitHub Pages frontend can use real AI online
