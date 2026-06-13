# Project Map

## Project

智慧飲食建議系統包含 React + TypeScript + Vite 前端與 FastAPI 後端。前端可部署到 GitHub Pages；後端可部署到 Render，負責 AI provider 呼叫、圖片辨識校正、URL 擷取、餐點資料集儲存與推薦 API。

## Frontend Files

- `src/App.tsx`: 主要 UI，包含系統介紹、AI 餐點分析、推薦條件、推薦結果、餐點資料集與查詢紀錄。
- `src/api.ts`: 前端 API client，透過 `VITE_API_BASE_URL` 呼叫後端 API。
- `src/mealData.ts`: 前端離線展示資料。
- `src/styles.css`: 響應式版面與視覺樣式。
- `src/App.test.tsx`: Vitest + React Testing Library component tests。
- `scripts/browser-walkthrough.mjs`: production build 的瀏覽器互動走查。
- `scripts/check-content.mjs`: 內容檢查，避免 mojibake 亂碼重新進入專案。

## Backend Structure

- `backend/app/main.py`: FastAPI app、CORS、health、analyze、meals、recommend endpoints。
- `backend/app/models.py`: Pydantic models。
- `backend/app/services/ai_provider.py`: AI provider、環境變數與餐點名稱正規化。
- `backend/app/services/openai_meal_analyzer.py`: 文字、圖片、URL 餐點分析流程與安全系統分析。
- `backend/app/services/web_food_verifier.py`: 圖片候選餐點校正、豚丼 / 親子丼 / 豬排丼 rerank 規則、Gemini Search grounding best-effort 流程。
- `backend/app/services/url_fetcher.py`: 使用 httpx + BeautifulSoup 擷取單一 URL 內容。
- `backend/app/storage/meals_store.py`: JSON 餐點資料集讀取、使用者餐點 upsert / merge、推薦過濾。
- `backend/data/meals.json`: 內建基礎餐點資料。
- `backend/data/user_meals.json`: 本機執行時的使用者新增餐點資料，執行期產生且不提交。
- `backend/tests/test_api.py`: FastAPI endpoint 與正規化 / rerank 測試。

## Deployment Files

- `.github/workflows/deploy-pages.yml`: push 到 `main` 時部署前端到 GitHub Pages。
- `render.yaml`: Render Web Service blueprint，部署 `backend`。
- `.env.example`: 前端本機 API URL 範本。
- `.env.production.example`: 前端 production API URL 與 GitHub Pages base path 範本。
- `backend/.env.example`: 後端本機與 Render 環境變數範本。

## API Endpoints

- `GET /api/health`
- `POST /api/analyze/text`
- `POST /api/analyze/image`
- `POST /api/analyze/url`
- `GET /api/meals`
- `POST /api/meals`
- `POST /api/recommend`

## Public Deployment

- Frontend: GitHub Pages
- Backend: Render
- Frontend API base URL: `VITE_API_BASE_URL`
- Backend allowed origins: `FRONTEND_ORIGIN`, supports comma-separated origins
- API keys: stored only in Render environment variables

## Validation

- Frontend: `npm run validate`
- Backend: `cd backend && python -m pytest`

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
