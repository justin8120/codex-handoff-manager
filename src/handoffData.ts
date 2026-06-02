export type InventoryStatus = "已確認" | "待補齊" | "待複查"
export type TaskStatus = "已完成" | "進行中" | "待處理" | "未開始"

export type InventoryItem = {
  category: string
  status: InventoryStatus
  description: string
}

export type TaskItem = {
  id: string
  title: string
  status: TaskStatus
  details: string
}

export type DownloadFile = {
  name: string
  purpose: string
  content: string
}

export const promptMarkdown = `# 交接給 Codex 的起始 Prompt

請先閱讀這個 repo 內的 AGENTS.md、PROJECT_CONTEXT.md、DATA_INVENTORY.md、TASKS.md 與 code_review.md。

你的任務是：

1. 分析目前 repository 的結構與狀態。
2. 判斷技術棧、package manager、build tool 與可用腳本。
3. 嘗試或確認 install、dev、test、lint、typecheck、build 指令。
4. 找出缺少的資料、環境假設與風險。
5. 依照 TASKS.md 推進下一個合理階段，並在結尾回報 summary、changed、validation、assumptions、risks/follow-ups。

若資料不足，請先做最小可逆的檢查，不要捏造不存在的 API、資料庫、畫面或業務規則。
`

export const inventory: InventoryItem[] = [
  {
    category: "專案目的",
    status: "已確認",
    description: "建立一個讓 Codex 或其他 coding agent 快速接手的專案交接中心。",
  },
  {
    category: "技術棧",
    status: "已確認",
    description: "目前為 React + TypeScript + Vite，使用 lucide-react 作為圖示庫。",
  },
  {
    category: "套件管理",
    status: "已確認",
    description: "使用 npm，package-lock.json 已存在，node_modules 已安裝。",
  },
  {
    category: "建置與型別檢查",
    status: "已確認",
    description: "npm run typecheck 與 npm run build 已通過；dist 產物已產生。",
  },
  {
    category: "Runtime 驗證",
    status: "已確認",
    description: "dev server 與 production preview 皆已透過本機 HTTP 200 檢查。",
  },
  {
    category: "互動式瀏覽器走查",
    status: "待複查",
    description: "尚未以瀏覽器逐一操作搜尋、篩選、複製、下載與響應式版面。",
  },
  {
    category: "自動化測試",
    status: "待補齊",
    description: "目前沒有 test script，也尚未加入元件測試或端對端測試。",
  },
  {
    category: "Lint / Format",
    status: "待補齊",
    description: "目前未設定 lint 或 formatter，後續可加入 ESLint 與 Prettier。",
  },
  {
    category: "來源 handoff 文件",
    status: "待複查",
    description:
      "codex_ready_context_bundle_v2 內的原始中文內容疑似有編碼問題，UI 已先整理為可讀版本。",
  },
]

export const tasks: TaskItem[] = [
  {
    id: "phase-0",
    title: "建立 Codex 交接包",
    status: "已完成",
    details:
      "建立 README、AGENTS、PROJECT_CONTEXT、DATA_INVENTORY、TASKS、code_review 與 starter prompt。",
  },
  {
    id: "phase-1",
    title: "建立前端專案骨架",
    status: "已完成",
    details:
      "建立 Vite + React + TypeScript app，並加入主要導覽、資料盤點、任務列表、預覽與下載區塊。",
  },
  {
    id: "phase-2",
    title: "完成基礎驗證",
    status: "已完成",
    details: "完成 npm install、typecheck、production build 與本機 HTTP runtime 檢查。",
  },
  {
    id: "phase-3",
    title: "整理 UI 文字與編碼可讀性",
    status: "已完成",
    details: "將使用者可見文案、狀態、下載 Markdown 與搜尋篩選資料改為一致且可讀的繁體中文。",
  },
  {
    id: "phase-4",
    title: "互動式瀏覽器走查",
    status: "進行中",
    details: "下一步需要實際操作搜尋、篩選、複製、下載、導覽錨點與手機版版面。",
  },
  {
    id: "phase-5",
    title: "補上品質工具",
    status: "未開始",
    details: "可評估加入 ESLint、Prettier、測試框架或 Playwright，讓交接 app 更容易維護。",
  },
]

export const agentsMarkdown = `# AGENTS.md

## 目的

這個 repository 是一個 Codex 專案交接中心。請把它視為接手專案時的入口，而不是完整產品規格。

## 工作方式

1. 先閱讀 README.md、PROJECT_MAP.md，以及 codex_ready_context_bundle_v2 內的文件。
2. 檢查 package.json，確認可用的 npm scripts。
3. 在做任何改動前，先判斷目前狀態與下一個最合理階段。
4. 優先做可逆、範圍小、能提高交接品質的改動。
5. 每次改動後至少執行 typecheck 或 build；若無法執行，請明確說明原因。
6. 不要捏造尚未存在的 API、資料庫、認證流程或部署設定。

## 回報格式

請在工作完成後回報：

- Summary: 這次完成了什麼。
- Changed: 修改了哪些檔案或功能。
- Validation: 執行了哪些驗證。
- Assumptions: 有哪些假設。
- Risks / Follow-ups: 還有哪些風險或後續工作。
`

const dataInventoryMarkdown = `# DATA_INVENTORY.md

## 專案資料盤點

| 類別 | 狀態 | 說明 |
|---|---|---|
| 專案目的 | 已確認 | 建立 Codex 專案交接中心 |
| 技術棧 | 已確認 | React + TypeScript + Vite |
| 套件管理 | 已確認 | npm + package-lock.json |
| Build / Typecheck | 已確認 | npm run typecheck 與 npm run build 已通過 |
| Runtime 驗證 | 已確認 | dev 與 preview 皆回 HTTP 200 |
| 互動式瀏覽器走查 | 待複查 | 尚未逐項操作 UI |
| 自動化測試 | 待補齊 | 尚未設定 test script |
| Lint / Format | 待補齊 | 尚未設定 lint 或 formatter |
| 原始 handoff 文件 | 待複查 | 部分來源文字疑似編碼損壞 |
`

const tasksMarkdown = `# TASKS.md

## 階段任務

### Phase 0: 建立 Codex 交接包

狀態：已完成

建立 README、AGENTS、PROJECT_CONTEXT、DATA_INVENTORY、TASKS、code_review 與 starter prompt。

### Phase 1: 建立前端專案骨架

狀態：已完成

建立 Vite + React + TypeScript app，並加入導覽、盤點、任務、預覽與下載功能。

### Phase 2: 完成基礎驗證

狀態：已完成

完成 npm install、typecheck、production build 與本機 HTTP runtime 檢查。

### Phase 3: 整理 UI 文字與編碼可讀性

狀態：已完成

將畫面文案、狀態、下載 Markdown 與搜尋篩選資料改為一致且可讀的繁體中文。

### Phase 4: 互動式瀏覽器走查

狀態：進行中

實際操作搜尋、篩選、複製、下載、導覽錨點與響應式版面。

### Phase 5: 補上品質工具

狀態：未開始

評估加入 ESLint、Prettier、測試框架或 Playwright。
`

const projectContextMarkdown = `# PROJECT_CONTEXT.md

## 專案背景

這個專案是為了把一組 Codex 交接文件變成可瀏覽、可搜尋、可下載的前端介面。

## 已確認

- 技術棧：React + TypeScript + Vite
- 套件管理：npm
- 圖示庫：lucide-react
- 建置狀態：typecheck 與 build 已通過
- Runtime 狀態：dev server 與 production preview 皆已回 HTTP 200

## 尚待處理

- 完整互動式瀏覽器走查
- 原始 handoff 文件的編碼可讀性複查
- 自動化測試策略
- Lint / format 設定
`

const codeReviewMarkdown = `# code_review.md

## Review 重點

請優先檢查：

1. Correctness: UI 狀態、搜尋、篩選、下載與複製是否符合預期。
2. Accessibility: 導覽、按鈕、表格與輸入欄位是否有合理標籤。
3. Responsiveness: 桌面與手機版是否沒有重疊、截斷或不可操作狀態。
4. Maintainability: 狀態型別、資料結構與下載內容是否容易維護。
5. Validation: typecheck、build、runtime server 是否可重現。

## 已知缺口

- 尚未建立自動化測試。
- 尚未設定 lint 或 formatter。
- 尚未完成截圖式瀏覽器驗證。
`

export const downloads: DownloadFile[] = [
  {
    name: "AGENTS.md",
    purpose: "給 coding agent 的協作規則與接手流程。",
    content: agentsMarkdown,
  },
  {
    name: "DATA_INVENTORY.md",
    purpose: "目前已掌握、待補齊與待複查的資料盤點。",
    content: dataInventoryMarkdown,
  },
  {
    name: "TASKS.md",
    purpose: "階段任務與下一步工作狀態。",
    content: tasksMarkdown,
  },
  {
    name: "PROMPT_FOR_CODEX.md",
    purpose: "交接給下一位 Codex 的起始 prompt。",
    content: promptMarkdown,
  },
  {
    name: "PROJECT_CONTEXT.md",
    purpose: "專案背景、已確認內容與尚待處理事項。",
    content: projectContextMarkdown,
  },
  {
    name: "code_review.md",
    purpose: "後續 code review 的檢查清單。",
    content: codeReviewMarkdown,
  },
]
