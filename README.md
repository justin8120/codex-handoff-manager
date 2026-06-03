# 智慧飲食建議系統

智慧飲食建議系統包含 React + TypeScript + Vite 前端與 FastAPI 後端。前端部署在 GitHub Pages，後端負責安全呼叫 AI provider、分析餐點、儲存餐點資料集，並提供推薦 API。

## Features

- 文字描述、圖片上傳、連結輸入三種 AI 餐點分析方式
- 後端支援 `AI_PROVIDER=openai|gemini|mock|auto`
- OpenAI 與 Gemini 皆透過 OpenAI Python SDK 的 chat completions JSON mode 產生餐點分析 JSON
- `AI_FALLBACK_ENABLED=true` 時，quota、auth、model 或 API 錯誤會回傳 rule-based fallback，避免 endpoint 直接 500
- 分析結果包含餐點名稱、類型、估算熱量、估算蛋白質、標籤、主要食材、過敏原、推薦原因、信心分數與來源類型
- 可將 AI 分析結果加入餐點資料集，資料會寫回 `backend/data/meals.json`
- 前端餐點推薦優先呼叫後端 `POST /api/recommend`
- 後端未啟動時，前端會顯示「AI 後端尚未啟動，請先啟動 FastAPI server。」並進入離線展示模式
- 預設餐點資料集包含雞胸肉便當、茶葉蛋、鮭魚沙拉、豆腐蔬菜碗、燕麥優格杯、牛肉蔬菜飯、地瓜雞蛋餐、海鮮粥、蔬食便當
- 查無結果時顯示「未找到符合條件的餐點，請調整搜尋條件」

## Frontend

```bash
npm install
npm run dev
```

前端環境變數：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

GitHub Pages 只部署前端。OpenAI API Key 不可放在前端，也不可 commit 到 git。

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# 在 .env 填入 OPENAI_API_KEY 或 GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

`backend/.env`：

```bash
AI_PROVIDER=gemini
AI_FALLBACK_ENABLED=true

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.5-flash-lite
FRONTEND_ORIGIN=http://localhost:5173
```

## AI Analysis Flow

- `POST /api/analyze/text`: 使用文字描述呼叫目前選定 AI provider。
- `POST /api/analyze/image`: 圖片轉成 base64 data URL 後交給支援 vision 的模型分析。
- `POST /api/analyze/url`: 後端只擷取使用者提供的單一 URL，使用 httpx + BeautifulSoup 取得 title、meta description 與主要文字，再交給 OpenAI 分析。

AI 營養數值為估算值，實際數值仍需以餐點標示或專業資料為準。

## Validation

Frontend:

```bash
npm run validate
```

Backend:

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Deployment

- GitHub repository: https://github.com/justin8120/codex-handoff-manager
- GitHub Pages URL: https://justin8120.github.io/codex-handoff-manager/
- GitHub Pages deploys only the frontend
- FastAPI backend must be deployed separately for real AI analysis

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
- FastAPI backend still needs a production deployment target such as Render, Railway, or Fly.io
