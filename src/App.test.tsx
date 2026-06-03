import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest"
import { App } from "./App"

const backendMeals = [
  {
    id: "seed-tea-egg",
    mealName: "茶葉蛋",
    mealType: "點心",
    estimatedCalories: 80,
    estimatedProtein: 7,
    tags: ["低卡", "高蛋白", "低脂"],
    mainIngredients: ["雞蛋", "茶葉"],
    allergens: [],
    recommendationReason: "熱量低且容易取得，適合作為補充蛋白質的小點心。",
    confidence: 1,
    sourceType: "text",
    createdAt: "2026-06-03T00:00:00+00:00",
    isAiGenerated: false,
  },
  {
    id: "seed-salmon-salad",
    mealName: "鮭魚沙拉",
    mealType: "沙拉",
    estimatedCalories: 360,
    estimatedProtein: 28,
    tags: ["低卡", "高蛋白", "健康餐"],
    mainIngredients: ["鮭魚", "生菜"],
    allergens: ["海鮮"],
    recommendationReason: "提供優質蛋白與好油脂，適合想吃清爽主餐的人。",
    confidence: 1,
    sourceType: "text",
    createdAt: "2026-06-03T00:00:00+00:00",
    isAiGenerated: false,
  },
  {
    id: "seed-seafood-congee",
    mealName: "海鮮粥",
    mealType: "粥品",
    estimatedCalories: 420,
    estimatedProtein: 25,
    tags: ["低脂", "健康餐"],
    mainIngredients: ["白米", "蝦仁", "魚片"],
    allergens: ["海鮮"],
    recommendationReason: "口感清淡且脂肪較低，適合想吃溫熱主食的人。",
    confidence: 1,
    sourceType: "text",
    createdAt: "2026-06-03T00:00:00+00:00",
    isAiGenerated: false,
  },
]

const analysisMeal = {
  id: "ai-tea-egg",
  mealName: "茶葉蛋",
  mealType: "點心",
  estimatedCalories: 80,
  estimatedProtein: 7,
  tags: ["低卡", "高蛋白", "低脂"],
  mainIngredients: ["雞蛋", "茶葉", "醬油"],
  allergens: [],
  recommendationReason: "OpenAI 分析判斷此餐點熱量低，適合作為蛋白質補充。",
  confidence: 0.91,
  sourceType: "text",
  createdAt: "2026-06-03T00:00:00+00:00",
  isAiGenerated: true,
}

function jsonResponse(payload: unknown, init?: ResponseInit) {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  })
}

function mockOnlineApi() {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    if (url.endsWith("/api/health")) {
      return jsonResponse({ status: "ok", aiConfigured: true, model: "gpt-4.1-mini" })
    }
    if (url.endsWith("/api/meals") && init?.method === "POST") return jsonResponse(analysisMeal)
    if (url.endsWith("/api/meals")) return jsonResponse(backendMeals)
    if (url.endsWith("/api/analyze/text")) return jsonResponse(analysisMeal)
    if (url.endsWith("/api/recommend")) {
      const body = JSON.parse(String(init?.body))
      if (body.keyword === "不存在的餐點") return jsonResponse([])
      if (body.excludedIngredients?.includes("海鮮")) return jsonResponse([backendMeals[0]])
      return jsonResponse([backendMeals[0]])
    }
    return jsonResponse({ detail: "Not found" }, { status: 404 })
  })
}

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", mockOnlineApi())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test("renders the smart diet recommendation system and AI analysis section", async () => {
    render(<App />)

    expect(screen.getByRole("heading", { name: "智慧飲食建議系統" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "AI 餐點分析與資料集擴充" })).toBeInTheDocument()
    await waitFor(() =>
      expect(screen.getByText("AI 後端狀態：已連線，OpenAI API 狀態：已設定")).toBeInTheDocument(),
    )
  })

  test("loads meal dataset from the backend", async () => {
    render(<App />)

    const mealDataset = await screen.findByLabelText("完整餐點資料集")
    expect(within(mealDataset).getByText("茶葉蛋")).toBeInTheDocument()
  })

  test("runs mocked AI text analysis and adds the result to the dataset", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByLabelText("文字描述"), "茶葉蛋")
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))

    const analysis = await screen.findByLabelText("AI 分析結果")
    expect(within(analysis).getByText("茶葉蛋")).toBeInTheDocument()

    await user.click(screen.getByRole("button", { name: "加入餐點資料集" }))
    await waitFor(() =>
      expect(screen.getByText("茶葉蛋 已加入餐點資料集，並可用於推薦。")).toBeInTheDocument(),
    )
  })

  test("shows backend offline message when API is unavailable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => Promise.reject(new Error("offline"))),
    )
    render(<App />)

    expect(
      await screen.findByText(/AI 後端尚未啟動，請先啟動 FastAPI server。/),
    ).toBeInTheDocument()
    expect(screen.getByText(/目前為離線展示模式/)).toBeInTheDocument()
  })

  test("excludes seafood meals through mocked recommendation API", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByLabelText("海鮮"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    const results = screen.getByLabelText("推薦清單")
    await waitFor(() => expect(within(results).getByText("茶葉蛋")).toBeInTheDocument())
    expect(within(results).queryByText("海鮮粥")).not.toBeInTheDocument()
    expect(within(results).queryByText("鮭魚沙拉")).not.toBeInTheDocument()
  })

  test("shows no-result message", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByRole("searchbox"), "不存在的餐點")
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    expect(await screen.findByText("未找到符合條件的餐點，請調整搜尋條件")).toBeInTheDocument()
  })

  test("adds query history after searching", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByLabelText("低卡"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    const history = await screen.findByLabelText("最近查詢紀錄")
    expect(within(history).getByText("目標：均衡飲食")).toBeInTheDocument()
    expect(within(history).getByText("標籤：低卡")).toBeInTheDocument()
    expect(within(history).getByText(/結果數量：/)).toBeInTheDocument()
  })
})
