# Deployment Options

## Current Setup

GitHub Pages remains the deployment target for the React frontend only.

- GitHub repository: https://github.com/justin8120/codex-handoff-manager
- GitHub Pages URL: https://justin8120.github.io/codex-handoff-manager/
- Frontend env var: `VITE_API_BASE_URL`
- Backend env vars: `AI_PROVIDER`, `AI_FALLBACK_ENABLED`, `OPENAI_API_KEY`, `GEMINI_API_KEY`

GitHub Pages cannot run FastAPI and cannot safely store AI provider keys. OpenAI or Gemini API calls must be made from the backend.

## Frontend: GitHub Pages

GitHub Pages is still suitable for:

- React + Vite static frontend
- UI for AI meal analysis
- Offline展示模式
- Calling a separately deployed backend through `VITE_API_BASE_URL`

It is not suitable for:

- Running Python / FastAPI
- Storing `OPENAI_API_KEY` or `GEMINI_API_KEY`
- Calling OpenAI or Gemini directly from browser code

## Backend Deployment Options

FastAPI should be deployed separately to a service that can store environment variables securely.

Recommended options:

- Render
- Railway
- Fly.io
- A VPS or school server with HTTPS

Backend deployment must set:

```bash
AI_PROVIDER=gemini
AI_FALLBACK_ENABLED=true
OPENAI_API_KEY=...
GEMINI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
GEMINI_MODEL=gemini-2.5-flash-lite
FRONTEND_ORIGIN=https://justin8120.github.io
```

After deployment, set the frontend build variable:

```bash
VITE_API_BASE_URL=https://your-backend.example.com
```

## OpenAI API Key Safety

Never place `OPENAI_API_KEY` in:

- frontend source code
- `.env` files committed to git
- GitHub Pages static assets
- browser-visible JavaScript bundles

Only the FastAPI backend should read and use provider keys.

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
- backend production deployment is still required for real AI analysis on the public GitHub Pages site
