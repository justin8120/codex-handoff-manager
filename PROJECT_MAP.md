# Project Map

## Project

智慧飲食建議系統是一個前端展示網站，目標是示範如何依照健康目標、飲食標籤與禁忌食材推薦餐點。專案保留既有 React + TypeScript + Vite 架構與自動化品質流程。

## Main Files

- `src/App.tsx`: 智慧飲食建議系統 UI、推薦條件狀態、篩選邏輯與查詢紀錄。
- `src/handoffData.ts`: 靜態餐點資料、健康目標、飲食標籤與過敏原型別。
- `src/styles.css`: 響應式版面、推薦表單、餐點卡片與查詢紀錄樣式。
- `src/App.test.tsx`: Vitest + React Testing Library component tests。
- `scripts/browser-walkthrough.mjs`: production build 的瀏覽器互動走查。
- `.github/workflows/ci.yml`: CI workflow，執行 `npm ci` 與 `npm run validate`。
- `.github/workflows/deploy-pages.yml`: GitHub Pages deploy workflow。
- `vite.config.ts`: Vite 設定，包含 GitHub Pages repository page base 支援。
- `DEPLOYMENT_OPTIONS.md`: 部署方案與 GitHub Pages 狀態。

## Completed Work

- converted UI and content to the smart diet recommendation system topic
- added static meal data with calories, protein, tags, ingredients, allergens, and recommendation reasons
- added recommendation filtering by health goal and diet tags
- added exclusion for allergens or forbidden ingredients
- added no-result messaging
- added recent query history
- updated unit/component tests for the recommendation system
- updated browser walkthrough for recommendation flow, filtering, no-result state, anchor navigation, and mobile overflow
- preserved ESLint, Prettier, Vitest, GitHub Actions, and GitHub Pages deployment setup
- pushed repository to GitHub
- enabled GitHub Pages deployment through GitHub Actions
- fixed CI formatting / line-ending issue
- fixed Chrome executable path resolution for CI/Linux
- confirmed CI and Deploy workflows pass

## Deployment Status

- GitHub repository URL: https://github.com/justin8120/codex-handoff-manager
- GitHub Pages URL: https://justin8120.github.io/codex-handoff-manager/
- CI workflow passed
- Deploy GitHub Pages workflow passed
- latest confirmed successful workflow commit: a87a459
- current deployment target: GitHub Pages

## Validation

`npm run validate` is the primary quality gate. It runs content check, formatting check, lint, typecheck, tests, build, and browser walkthrough.

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
