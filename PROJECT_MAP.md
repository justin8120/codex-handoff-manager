# Project Map

## Project

智慧飲食建議系統是一個前端展示網站，用來示範依照健康目標、飲食標籤、關鍵字與禁忌食材推薦餐點。專案保留 React + TypeScript + Vite 架構，以及 ESLint、Prettier、Vitest、GitHub Actions 與 GitHub Pages 部署流程。

## Main Files

- `src/App.tsx`: 主要 UI、推薦條件狀態、篩選邏輯、推薦結果、餐點資料與查詢紀錄。
- `src/mealData.ts`: 9 筆靜態餐點資料、健康目標、飲食標籤與過敏原型別。
- `src/styles.css`: 響應式版面、推薦表單、餐點卡片、餐點資料與查詢紀錄樣式。
- `src/App.test.tsx`: Vitest + React Testing Library component tests。
- `scripts/browser-walkthrough.mjs`: production build 的瀏覽器互動走查。
- `scripts/check-content.mjs`: 文字內容檢查，避免提交亂碼。
- `.github/workflows/ci.yml`: CI workflow，執行 `npm ci` 與 `npm run validate`。
- `.github/workflows/deploy-pages.yml`: GitHub Pages deploy workflow。
- `vite.config.ts`: Vite 設定，包含 GitHub Pages repository page base 支援。
- `DEPLOYMENT_OPTIONS.md`: 部署方案與 GitHub Pages 狀態。

## Completed Work

- converted UI and content to the smart diet recommendation system topic
- added visible meal data section with 9 complete meal records
- added required sample meals: 雞胸肉便當, 茶葉蛋, 鮭魚沙拉, 豆腐蔬菜碗, 燕麥優格杯, 牛肉蔬菜飯, 地瓜雞蛋餐, 海鮮粥, 蔬食便當
- added recommendation filtering by health goal, diet tags, keyword, and forbidden ingredients
- added no-result messaging
- added recent query history
- removed obsolete source content that described unrelated project materials
- updated unit/component tests for render, meal data, tea egg search, seafood exclusion, no-result state, and query history
- updated browser walkthrough for meal data, tea egg search, seafood exclusion, no-result state, anchor navigation, and mobile overflow
- preserved ESLint, Prettier, Vitest, GitHub Actions, and GitHub Pages deployment setup

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
