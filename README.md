# 智慧飲食建議系統

智慧飲食建議系統是一個 React + TypeScript + Vite 展示網站。使用者可以依照健康目標、飲食標籤、關鍵字，以及過敏原或禁忌食材篩選餐點，系統會顯示推薦清單與推薦原因。

## Features

- 健康目標：減脂、增肌、均衡飲食、健康維持
- 飲食標籤：低卡、高蛋白、低脂、健康餐、素食
- 過敏原或禁忌食材排除：花生、牛肉、海鮮、乳製品
- 關鍵字搜尋，例如搜尋「茶葉蛋」可找到資料中的茶葉蛋
- 推薦結果區預設顯示可推薦餐點，查詢後顯示符合條件的餐點
- 餐點資料區完整顯示 9 筆資料，包含餐點名稱、類型、熱量、蛋白質、標籤、主要食材、禁忌食材與推薦原因
- 查無結果時顯示「未找到符合條件的餐點，請調整搜尋條件」
- 查詢紀錄顯示最近條件與結果數量
- 響應式版面支援桌面與手機

## Tech Stack

- React + TypeScript + Vite
- ESLint
- Prettier
- Vitest + React Testing Library
- Browser walkthrough script for production build checks
- GitHub Actions CI
- GitHub Pages deployment through GitHub Actions

## Scripts

```bash
npm run dev
npm run format
npm run format:check
npm run lint
npm run typecheck
npm run test
npm run test:watch
npm run build
npm run test:browser
npm run validate
```

`npm run validate` 會依序執行 content check、Prettier check、lint、typecheck、unit/component tests、production build 與 browser walkthrough。

## Deployment

- GitHub repository: https://github.com/justin8120/codex-handoff-manager
- GitHub Pages URL: https://justin8120.github.io/codex-handoff-manager/
- CI workflow: passed
- Deploy GitHub Pages workflow: passed

目前部署平台為 GitHub Pages。Vite production base 會在 GitHub Actions 中依 `GITHUB_REPOSITORY` 設定 repository page 路徑，本機開發與本機 build 不受影響。

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
