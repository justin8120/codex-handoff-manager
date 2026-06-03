# Project Map

## Project

智慧飲食建議系統是一個前端展示網站，用來示範 AI 餐點分析、餐點資料集擴充與條件式餐點推薦。專案保留 React + TypeScript + Vite 架構，以及 ESLint、Prettier、Vitest、GitHub Actions 與 GitHub Pages 部署流程。

## Main Files

- `src/App.tsx`: 主要 UI、demo AI 分析流程、資料集擴充、推薦條件狀態、篩選邏輯、推薦結果與查詢紀錄。
- `src/mealData.ts`: 9 筆初始餐點資料、健康目標、飲食標籤、過敏原與餐點型別。
- `src/styles.css`: 響應式版面、AI 分析區、推薦表單、餐點卡片、餐點資料集與查詢紀錄樣式。
- `src/App.test.tsx`: Vitest + React Testing Library component tests。
- `scripts/browser-walkthrough.mjs`: production build 的瀏覽器互動走查。
- `scripts/check-content.mjs`: 文字內容檢查，避免提交亂碼。
- `.github/workflows/ci.yml`: CI workflow，執行 `npm ci` 與 `npm run validate`。
- `.github/workflows/deploy-pages.yml`: GitHub Pages deploy workflow。
- `vite.config.ts`: Vite 設定，包含 GitHub Pages repository page base 支援。
- `DEPLOYMENT_OPTIONS.md`: 部署方案與 GitHub Pages 狀態。

## Completed Work

- added AI 餐點分析與資料集擴充 section
- added text, image upload, and link input controls for demo analysis
- added demo analysis result format with meal name, type, estimated calories, estimated protein, tags, ingredients, allergens, recommendation reason, confidence score, and source type
- added clear demo disclaimer: formal AI version requires a backend connected to OpenAI API
- added nutrition disclaimer for AI analysis results
- added ability to add analysis results to the meal dataset
- recommendation flow now uses the expanded in-memory meal dataset
- preserved forbidden ingredient exclusion and no-result messaging
- kept the initial 9 required meals in the meal dataset
- updated unit/component tests for AI analysis, dataset expansion, seafood exclusion, no-result state, and query history
- updated browser walkthrough for AI analysis, dataset expansion, recommendation flow, seafood exclusion, no-result state, and mobile overflow

## Deployment Status

- GitHub repository URL: https://github.com/justin8120/codex-handoff-manager
- GitHub Pages URL: https://justin8120.github.io/codex-handoff-manager/
- CI workflow passed
- Deploy GitHub Pages workflow passed
- latest confirmed successful workflow commit: a87a459
- current deployment target: GitHub Pages

## AI Integration Notes

The current app is frontend-only and uses demo fallback logic. A production AI version needs a separate backend service to call OpenAI API securely. OpenAI API Key must stay on the backend and must not be exposed in the frontend bundle or GitHub Pages.

GitHub Pages can host the frontend only. Real image analysis, link parsing, nutrition lookup, and model calls require a separately deployed backend.

## Validation

`npm run validate` is the primary quality gate. It runs content check, formatting check, lint, typecheck, tests, build, and browser walkthrough.

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
- production AI analysis requires backend deployment and OpenAI API integration
