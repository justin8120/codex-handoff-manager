# Deployment Options

## Selected Option: GitHub Pages

The project is configured to deploy the 智慧飲食建議系統 frontend through GitHub Actions to GitHub Pages.

- GitHub repository: https://github.com/justin8120/codex-handoff-manager
- GitHub Pages URL: https://justin8120.github.io/codex-handoff-manager/
- CI workflow: passed
- Deploy GitHub Pages workflow: passed
- latest confirmed successful workflow commit: a87a459

## GitHub Pages

GitHub Pages remains the current best fit for the frontend demo because the app is a static React + Vite展示網站 and the repository already uses GitHub Actions. It can host the UI, static assets, demo analysis flow, recommendation UI, and in-memory dataset expansion.

GitHub Pages cannot safely host secrets or run a private backend. OpenAI API Key must not be placed in the frontend. A formal AI version that analyzes images, links, menu pages, and nutrition data needs a separate backend deployment.

Repository pages use a path like:

```text
https://使用者名稱.github.io/repository-name/
```

For that reason, `vite.config.ts` sets the production `base` from `GITHUB_REPOSITORY` when the workflow runs on GitHub Actions. Local development and local production build remain unaffected.

Deployment flow:

```bash
npm ci
npm run validate
npm run build
upload dist
deploy to GitHub Pages
```

## Backend Requirement For Real AI

The current frontend provides demo fallback analysis only. To support real OpenAI API calls, image understanding, link scraping, and nutrition data lookup, deploy a backend separately. The frontend should send text, uploaded image metadata or image files, and URLs to that backend. The backend should own API keys, model calls, validation, and nutrition-source integration.

## Vercel

Vercel supports both frontend hosting and serverless functions, so it can be considered if the project later needs a lightweight backend in the same platform. The current GitHub Pages setup is still sufficient for the frontend demo.

## Netlify

Netlify supports static hosting and serverless functions. It is a reasonable alternative if the project later needs Netlify Functions for a small backend. The current project does not require moving away from GitHub Pages for the frontend.

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
- production AI analysis requires backend deployment and OpenAI API integration
