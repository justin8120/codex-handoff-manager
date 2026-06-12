import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest"
import { App } from "./App"
import { backendMealToMeal, inferGoals, type BackendMeal } from "./api"

const backendMeals: BackendMeal[] = [
  {
    id: "seed-tea-egg",
    mealName: "茶葉蛋",
    mealType: "蛋白點心",
    estimatedCalories: 80,
    estimatedProtein: 7,
    tags: ["低卡", "高蛋白", "低脂"],
    mainIngredients: ["雞蛋", "茶葉"],
    allergens: ["蛋"],
    recommendationReason: "茶葉蛋熱量低且含蛋白質，適合作為份量較小的蛋白質補充。",
    confidence: 1,
    sourceType: "text",
    createdAt: "2026-06-03T00:00:00+00:00",
    isAiGenerated: false,
    recommendedGoals: ["減脂", "健康維持"],
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
    recommendationReason: "鮭魚提供蛋白質與脂肪酸，搭配蔬菜可作為清爽主餐。",
    confidence: 1,
    sourceType: "text",
    createdAt: "2026-06-03T00:00:00+00:00",
    isAiGenerated: false,
    recommendedGoals: ["減脂", "健康維持"],
  },
  {
    id: "seed-seafood-congee",
    mealName: "海鮮粥",
    mealType: "粥品",
    estimatedCalories: 420,
    estimatedProtein: 25,
    tags: ["低脂", "健康餐"],
    mainIngredients: ["白飯", "蝦仁", "蛤蜊"],
    allergens: ["海鮮"],
    recommendationReason: "粥品口感溫和並含海鮮蛋白質，但海鮮禁忌者需避免。",
    confidence: 1,
    sourceType: "text",
    createdAt: "2026-06-03T00:00:00+00:00",
    isAiGenerated: false,
    recommendedGoals: ["均衡飲食", "健康維持"],
  },
]

const analysisMeal: BackendMeal = {
  id: "ai-tea-egg",
  mealName: "茶葉蛋",
  mealType: "蛋白點心",
  estimatedCalories: 80,
  estimatedProtein: 7,
  tags: ["低卡", "高蛋白", "低脂"],
  mainIngredients: ["雞蛋", "茶葉", "醬油"],
  allergens: ["蛋"],
  recommendationReason: "系統辨識此餐點為茶葉蛋，熱量較低並可補充蛋白質。",
  confidence: 0.91,
  sourceType: "text",
  createdAt: "2026-06-03T00:00:00+00:00",
  isAiGenerated: true,
  recommendedGoals: ["減脂", "健康維持"],
}

const cinnamonRollMeal: BackendMeal = {
  id: "url-cinnamon",
  mealName: "肉桂捲",
  mealType: "甜點 / 烘焙點心",
  estimatedCalories: 320,
  estimatedProtein: 6,
  tags: ["甜點", "烘焙", "高糖", "高碳水"],
  mainIngredients: ["麵粉", "糖", "肉桂", "奶油"],
  allergens: ["麩質", "奶類"],
  recommendationReason: "系統根據 URL 產品名稱推測為肉桂捲，屬甜點，建議偶爾享用。",
  confidence: 0.55,
  sourceType: "url",
  createdAt: "2026-06-12T00:00:00+00:00",
  isAiGenerated: true,
  recommendedGoals: ["偶爾享用", "甜點", "高糖提醒"],
}

const friedChickenCutletMeal: BackendMeal = {
  id: "fried-chicken-cutlet",
  mealName: "炸雞排",
  mealType: "炸物 / 小吃",
  estimatedCalories: 600,
  estimatedProtein: 35,
  tags: ["炸物", "雞肉", "高蛋白"],
  mainIngredients: ["雞肉", "麵衣", "油"],
  allergens: ["麩質"],
  recommendationReason:
    "系統根據圖片中可見的大型裹粉油炸雞排判斷此餐點為炸雞排，油炸料理熱量與油脂也較高。",
  confidence: 0.85,
  sourceType: "image",
  createdAt: "2026-06-12T00:00:00+00:00",
  isAiGenerated: true,
}

const leanChickenMeal: BackendMeal = {
  id: "lean-chicken",
  mealName: "雞胸肉健康餐",
  mealType: "健康餐",
  estimatedCalories: 420,
  estimatedProtein: 32,
  tags: ["低卡", "高蛋白", "低脂", "健康餐"],
  mainIngredients: ["雞胸肉", "蔬菜", "糙米"],
  allergens: [],
  recommendationReason: "雞胸肉搭配蔬菜與糙米，適合日常均衡飲食。",
  confidence: 0.8,
  sourceType: "text",
  createdAt: "2026-06-12T00:00:00+00:00",
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
      return jsonResponse({
        status: "ok",
        aiProvider: "gemini",
        aiConfigured: true,
        model: "gemini-2.5-flash-lite",
        fallbackEnabled: true,
      })
    }
    if (url.endsWith("/api/meals") && init?.method === "POST") return jsonResponse(analysisMeal)
    if (url.endsWith("/api/meals")) return jsonResponse(backendMeals)
    if (url.endsWith("/api/analyze/text")) return jsonResponse(analysisMeal)
    if (url.endsWith("/api/analyze/image"))
      return jsonResponse({ ...analysisMeal, sourceType: "image" })
    if (url.endsWith("/api/analyze/url")) return jsonResponse(cinnamonRollMeal)
    if (url.endsWith("/api/recommend")) {
      const body = JSON.parse(String(init?.body))
      if (body.keyword === "不存在的餐點") return jsonResponse([])
      if (body.excludedIngredients?.includes("豬肉")) return jsonResponse([])
      if (body.excludedIngredients?.includes("海鮮")) return jsonResponse([backendMeals[0]])
      return jsonResponse([backendMeals[0]])
    }
    return jsonResponse({ detail: "Not found" }, { status: 404 })
  })
}

describe("App", () => {
  beforeEach(() => {
    window.localStorage.clear()
    vi.stubGlobal("fetch", mockOnlineApi())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    window.localStorage.clear()
  })

  test("renders the smart diet recommendation system and AI analysis section", async () => {
    render(<App />)

    expect(screen.getByRole("heading", { name: "智慧飲食建議系統" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "AI 餐點分析與資料集擴充" })).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText(/Provider：gemini/)).toBeInTheDocument())
  })

  test("loads meal dataset from the backend", async () => {
    render(<App />)

    const mealDataset = await screen.findByLabelText("餐點資料集清單")
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
      expect(screen.getByText("茶葉蛋 已加入餐點資料集，可用於推薦。")).toBeInTheDocument(),
    )
  })

  test("does not call analysis API when all analysis inputs are empty", async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn(mockOnlineApi())
    vi.stubGlobal("fetch", fetchMock)
    render(<App />)

    await screen.findByText(/Provider：gemini/)
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))

    expect(
      screen.getByText("請至少輸入文字描述、上傳餐點圖片，或貼上餐點連結。"),
    ).toBeInTheDocument()
    expect(fetchMock.mock.calls.some(([input]) => String(input).includes("/api/analyze/"))).toBe(
      false,
    )
  })

  test("analyzes with only text description", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByLabelText("文字描述"), "茶葉蛋")
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))

    expect(await screen.findByLabelText("AI 分析結果")).toBeInTheDocument()
  })

  test("analyzes with only image upload", async () => {
    const user = userEvent.setup()
    render(<App />)
    const file = new File(["fake"], "meal.jpg", { type: "image/jpeg" })

    await user.upload(screen.getByLabelText("圖片上傳"), file)
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))

    expect(await screen.findByLabelText("AI 分析結果")).toBeInTheDocument()
  })

  test("sends text description as image analysis hint when text and image are provided", async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn(mockOnlineApi())
    vi.stubGlobal("fetch", fetchMock)
    render(<App />)
    const file = new File(["fake"], "meal.jpg", { type: "image/jpeg" })

    await user.type(screen.getByLabelText("文字描述"), "小籠包")
    await user.upload(screen.getByLabelText("圖片上傳"), file)
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))

    await screen.findByLabelText("AI 分析結果")
    const imageCall = fetchMock.mock.calls.find(([input]) =>
      String(input).endsWith("/api/analyze/image"),
    )
    expect(imageCall?.[1]?.body).toBeInstanceOf(FormData)
    expect((imageCall?.[1]?.body as FormData).get("text")).toBe("小籠包")
    expect((imageCall?.[1]?.body as FormData).get("description")).toBe("小籠包")
  })

  test("analyzes with only URL input and displays backend recommendation categories", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByLabelText("連結輸入"), "https://example.com/cinnamon-swirl.html")
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))

    const analysis = await screen.findByLabelText("AI 分析結果")
    expect(within(analysis).getByText("肉桂捲")).toBeInTheDocument()
    expect(within(analysis).getByText("偶爾享用 / 甜點 / 高糖提醒")).toBeInTheDocument()
  })

  test("uses URL analysis without sending stale image text hint when URL is provided", async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn(mockOnlineApi())
    vi.stubGlobal("fetch", fetchMock)
    render(<App />)
    const file = new File(["fake"], "dumpling.jpg", { type: "image/jpeg" })

    await user.type(screen.getByLabelText("文字描述"), "小籠包")
    await user.upload(screen.getByLabelText("圖片上傳"), file)
    await user.type(screen.getByLabelText("連結輸入"), "https://example.com/menu")
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))

    await screen.findByLabelText("AI 分析結果")
    expect(fetchMock.mock.calls.some(([input]) => String(input).endsWith("/api/analyze/url"))).toBe(
      true,
    )
    expect(
      fetchMock.mock.calls.some(([input]) => String(input).endsWith("/api/analyze/image")),
    ).toBe(false)
  })

  test("shows backend offline message when API is unavailable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => Promise.reject(new Error("offline"))),
    )
    render(<App />)

    expect(await screen.findByText(/AI 後端尚未啟動/)).toBeInTheDocument()
    expect(screen.getByText(/目前使用離線展示資料/)).toBeInTheDocument()
  })

  test("adds custom diet tag and sends it in recommendation payload", async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn(mockOnlineApi())
    vi.stubGlobal("fetch", fetchMock)
    render(<App />)

    await user.type(screen.getByLabelText("自訂飲食標籤"), "少油")
    await user.click(screen.getByRole("button", { name: "新增標籤" }))
    await user.click(screen.getByLabelText("少油"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    expect(screen.getByText("標籤已新增。")).toBeInTheDocument()
    const recommendCall = fetchMock.mock.calls.find(([input]) =>
      String(input).endsWith("/api/recommend"),
    )
    expect(JSON.parse(String(recommendCall?.[1]?.body)).tags).toContain("少油")
  })

  test("rejects blank and duplicate custom diet tags", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByRole("button", { name: "新增標籤" }))
    expect(screen.getByText("標籤不可為空。")).toBeInTheDocument()

    await user.type(screen.getByLabelText("自訂飲食標籤"), "低鈉")
    await user.click(screen.getByRole("button", { name: "新增標籤" }))
    await user.type(screen.getByLabelText("自訂飲食標籤"), "低鈉")
    await user.click(screen.getByRole("button", { name: "新增標籤" }))
    expect(screen.getByText("此標籤已存在。")).toBeInTheDocument()
  })

  test("custom diet tag persists after rerender and can be deleted", async () => {
    const user = userEvent.setup()
    const { unmount } = render(<App />)

    await user.type(screen.getByLabelText("自訂飲食標籤"), "高纖")
    await user.click(screen.getByRole("button", { name: "新增標籤" }))
    expect(window.localStorage.getItem("smartDiet.customDietTags")).toContain("高纖")
    unmount()

    render(<App />)
    expect(await screen.findByLabelText("高纖")).toBeInTheDocument()
    await user.click(screen.getByLabelText("高纖"))
    await user.click(screen.getByRole("button", { name: "刪除高纖" }))
    expect(screen.queryByLabelText("高纖")).not.toBeInTheDocument()
    expect(window.localStorage.getItem("smartDiet.customDietTags")).not.toContain("高纖")
  })

  test("adds custom avoid ingredient and sends it in recommendation payload", async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn(mockOnlineApi())
    vi.stubGlobal("fetch", fetchMock)
    render(<App />)

    await user.type(screen.getByLabelText("自訂禁忌食材"), "不吃辣")
    await user.click(screen.getByRole("button", { name: "新增禁忌食材" }))
    await user.click(screen.getByLabelText("不吃辣"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    expect(screen.getByText("禁忌食材已新增。")).toBeInTheDocument()
    const recommendCall = fetchMock.mock.calls.find(([input]) =>
      String(input).endsWith("/api/recommend"),
    )
    expect(JSON.parse(String(recommendCall?.[1]?.body)).excludedIngredients).toContain("不吃辣")
  })

  test("sends custom pork exclusion and shows empty result when backend filters all meals", async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn(mockOnlineApi())
    vi.stubGlobal("fetch", fetchMock)
    render(<App />)

    await user.type(screen.getByLabelText("自訂禁忌食材"), "豬肉")
    await user.click(screen.getByRole("button", { name: "新增禁忌食材" }))
    await user.click(screen.getByLabelText("豬肉"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    const recommendCall = fetchMock.mock.calls.find(([input]) =>
      String(input).endsWith("/api/recommend"),
    )
    expect(JSON.parse(String(recommendCall?.[1]?.body)).excludedIngredients).toContain("豬肉")
    expect(
      await screen.findByText("目前沒有符合條件的餐點，請調整飲食標籤或移除部分禁忌食材。"),
    ).toBeInTheDocument()
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

    expect(
      await screen.findByText("目前沒有符合條件的餐點，請調整飲食標籤或移除部分禁忌食材。"),
    ).toBeInTheDocument()
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

  test("uses backend recommendation goals when provided", () => {
    const meal = backendMealToMeal(cinnamonRollMeal)

    expect(meal.goals).toEqual(["偶爾享用", "甜點", "高糖提醒"])
  })

  test("infers conservative goals for fried chicken cutlet", () => {
    const goals = inferGoals(friedChickenCutletMeal)

    expect(goals).toContain("增肌")
    expect(goals).toContain("高蛋白補充")
    expect(goals).toContain("偶爾享用")
    expect(goals).toContain("油炸提醒")
    expect(goals).not.toContain("健康維持")
    expect(goals).not.toContain("均衡飲食")
    expect(goals).not.toContain("減脂")
  })

  test("infers fat loss and health maintenance goals for lean high-protein meals", () => {
    const goals = inferGoals(leanChickenMeal)

    expect(goals).toContain("減脂")
    expect(goals).toContain("健康維持")
    expect(goals).toContain("均衡飲食")
    expect(goals).toContain("增肌")
  })
})
