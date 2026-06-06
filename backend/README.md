# FastAPI Backend

此後端提供「智慧飲食建議系統」的 AI 餐點分析、餐點資料集與推薦 API。OpenAI / Gemini API key 只可放在後端環境變數，不可寫入前端或 commit 到 git。

## Local Development

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# 在 .env 填入 OPENAI_API_KEY 或 GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 在 .env 填入 OPENAI_API_KEY 或 GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

## Render Deployment

Render start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Root Directory:

```text
backend
```

Build Command:

```bash
pip install -r requirements.txt
```

## Environment Variables

- `AI_PROVIDER`: `openai`, `gemini`, `mock`, or `auto`
- `AI_FALLBACK_ENABLED`: AI provider 失敗時是否改用系統分析規則
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: 預設 `gpt-4.1-mini`
- `GEMINI_API_KEY`: Gemini API key
- `GEMINI_BASE_URL`: Gemini OpenAI-compatible endpoint
- `GEMINI_MODEL`: 預設 `gemini-2.5-flash-lite`
- `FRONTEND_ORIGIN`: CORS 允許來源，支援逗號分隔多個 origin
- `WEB_VERIFY_ENABLED`: 圖片分析後是否啟用網路比對校正
- `WEB_VERIFY_PROVIDER`: 目前支援 `gemini_grounding`

## API Endpoints

- `GET /api/health`
- `POST /api/analyze/text`
- `POST /api/analyze/image`
- `POST /api/analyze/url`
- `GET /api/meals`
- `POST /api/meals`
- `POST /api/recommend`

## Tests

```bash
python -m pytest
```
