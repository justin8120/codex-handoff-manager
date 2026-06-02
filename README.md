# 智慧飲食建議系統

智慧飲食建議系統是一個 React + TypeScript + Vite 展示網站，可依照使用者的健康目標、飲食標籤、過敏原或禁忌食材推薦餐點。系統目前使用靜態餐點資料，並在每次查詢後顯示最近查詢條件與結果數量。

## Features

- 健康目標篩選：減脂、增肌、均衡飲食、健康維持
- 飲食標籤篩選：低卡、高蛋白、低脂、健康餐、素食
- 過敏原或禁忌食材排除：花生、牛肉、海鮮、乳製品
- 關鍵字搜尋餐點、食材與推薦原因
- 餐點推薦清單顯示熱量、蛋白質、主要食材、標籤與推薦原因
- 查無結果時顯示清楚提示
- 最近查詢紀錄顯示查詢條件與結果數量
- 響應式版面支援桌面與手機瀏覽

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

部署平台目前使用 GitHub Pages。Vite base 透過 `GITHUB_REPOSITORY` 支援 repository page 路徑，避免影響本機 build。

## Current Status

- 已將網站主題轉換為智慧飲食建議系統
- 已保留 React + TypeScript + Vite、ESLint、Prettier、Vitest、GitHub Actions 與 GitHub Pages 架構
- 已更新 unit/component tests 與 browser walkthrough 以覆蓋推薦流程

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
