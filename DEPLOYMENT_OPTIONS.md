# Deployment Options

## Current Deployment Plan

本專案採用前後端分離公開部署：

- Frontend: GitHub Pages
- Backend: Render Web Service
- API URL: 前端透過 `VITE_API_BASE_URL` 指向 Render 後端
- API keys: 只放在 Render environment variables

## GitHub Pages Frontend

GitHub Pages 適合部署：

- React + Vite static frontend
- AI 餐點分析與推薦 UI
- 離線展示模式
- 呼叫 Render FastAPI backend

GitHub Pages 不適合：

- 執行 Python / FastAPI
- 儲存 `OPENAI_API_KEY` 或 `GEMINI_API_KEY`
- 直接從瀏覽器呼叫 OpenAI 或 Gemini

`deploy-pages.yml` 在 push 到 `main` 時會：

1. checkout repository
2. setup Node.js
3. run `npm ci`
4. run `npm run build`
5. upload `dist`
6. deploy to GitHub Pages

Build environment:

```bash
VITE_BASE_PATH=/${{ github.event.repository.name }}/
VITE_API_BASE_URL=${{ secrets.VITE_API_BASE_URL }}
```

## Render Backend

Render 適合部署 FastAPI，並安全保存環境變數。

`render.yaml` 設定：

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Render 必要環境變數：

```bash
AI_PROVIDER=auto
AI_FALLBACK_ENABLED=true
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.5-flash-lite
FRONTEND_ORIGIN=http://localhost:5173,https://your-username.github.io
WEB_VERIFY_ENABLED=false
WEB_VERIFY_PROVIDER=gemini_grounding
```

## CORS

後端 `FRONTEND_ORIGIN` 支援逗號分隔多個 origin：

```bash
FRONTEND_ORIGIN=http://localhost:5173,https://justin8120.github.io
```

## Security

不要提交：

- `.env`
- `.env.*`
- `backend/.env`
- `backend/.env.*`
- OpenAI / Gemini API keys

可提交的範本：

- `.env.example`
- `.env.production.example`
- `backend/.env.example`

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
