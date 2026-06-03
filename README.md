# 智慧飲食建議系統

智慧飲食建議系統是一個 React + TypeScript + Vite 展示網站。使用者可以透過文字描述、餐點照片或餐點連結取得前端 demo AI 分析結果，將結果加入餐點資料集，再依健康目標、飲食標籤、關鍵字與禁忌食材進行餐點推薦。

## Features

- AI 餐點分析與資料集擴充區塊
- 三種 demo 輸入方式：文字描述、圖片上傳、連結輸入
- 分析結果顯示餐點名稱、類型、估算熱量、估算蛋白質、飲食標籤、主要食材、過敏原、推薦原因、信心分數與來源類型
- 可將分析結果加入餐點資料集，並立即用於推薦
- 健康目標：減脂、增肌、均衡飲食、健康維持
- 飲食標籤：低卡、高蛋白、低脂、健康餐、素食
- 過敏原或禁忌食材排除：花生、牛肉、海鮮、乳製品
- 餐點資料集預設包含 9 筆資料：雞胸肉便當、茶葉蛋、鮭魚沙拉、豆腐蔬菜碗、燕麥優格杯、牛肉蔬菜飯、地瓜雞蛋餐、海鮮粥、蔬食便當
- 查無結果時顯示「未找到符合條件的餐點，請調整搜尋條件」
- 查詢紀錄顯示最近條件與結果數量
- 響應式版面支援桌面與手機

## AI Demo Notes

目前前端提供 demo AI 分析流程，會根據輸入關鍵字產生合理的示範分析結果。例如「雞胸肉」偏向高蛋白、低脂，「炸雞」偏向高熱量，「茶葉蛋」偏向低熱量與蛋白質補充。

此 demo 不會呼叫真正的 OpenAI API，也不會真正解析圖片或網頁內容。正式 AI 版本需新增後端服務並在後端串接 OpenAI API。OpenAI API Key 不可放在前端或 GitHub Pages 靜態頁面中。

GitHub Pages 只能部署前端。若要真正分析圖片、連結與營養資料，後端需另外部署，並由前端呼叫後端 API。

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
- 正式 AI 版本需要後端 API、OpenAI API 整合、圖片/連結解析與營養資料來源
