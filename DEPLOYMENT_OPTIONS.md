# Deployment Options

## Current Setup

GitHub Pages remains the deployment target for the React frontend only.

- GitHub repository: https://github.com/justin8120/codex-handoff-manager
- GitHub Pages URL: https://justin8120.github.io/codex-handoff-manager/
- Frontend env var: `VITE_API_BASE_URL`
- Backend env var: `OPENAI_API_KEY`

GitHub Pages cannot run FastAPI and cannot safely store OpenAI API keys. The OpenAI API must be called from the backend.

## Frontend: GitHub Pages

GitHub Pages is still suitable for:

- React + Vite static frontend
- UI for AI meal analysis
- Offline展示模式
- Calling a separately deployed backend through `VITE_API_BASE_URL`

It is not suitable for:

- Running Python / FastAPI
- Storing `OPENAI_API_KEY`
- Calling OpenAI directly from browser code

## Backend Deployment Options

FastAPI should be deployed separately to a service that can store environment variables securely.

Recommended options:

- Render
- Railway
- Fly.io
- A VPS or school server with HTTPS

Backend deployment must set:

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
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

Only the FastAPI backend should read and use the key.

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
- backend production deployment is still required for real AI analysis on the public GitHub Pages site
