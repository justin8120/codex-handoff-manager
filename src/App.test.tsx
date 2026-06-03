import { render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, test } from "vitest"
import { App } from "./App"

describe("App", () => {
  test("renders the smart diet recommendation system", () => {
    render(<App />)

    expect(screen.getByRole("heading", { name: "智慧飲食建議系統" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "AI 餐點分析與資料集擴充" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "餐點資料集" })).toBeInTheDocument()
  })

  test("accepts meal text and analyzes tea egg", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByLabelText("文字描述"), "茶葉蛋")
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))

    const analysis = screen.getByLabelText("AI 分析結果")
    expect(within(analysis).getByText("茶葉蛋")).toBeInTheDocument()
    expect(within(analysis).getByText("來源類型：文字，信心分數：92%")).toBeInTheDocument()
  })

  test("adds analysis result to the meal dataset", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByLabelText("文字描述"), "炸雞")
    await user.click(screen.getByRole("button", { name: "AI 分析餐點" }))
    await user.click(screen.getByRole("button", { name: "加入餐點資料集" }))

    const mealDataset = screen.getByLabelText("完整餐點資料集")
    expect(within(mealDataset).getByText("炸雞餐")).toBeInTheDocument()
    expect(screen.getByText("炸雞餐 已加入餐點資料集，並可用於推薦。")).toBeInTheDocument()
  })

  test("meal dataset includes tea egg", () => {
    render(<App />)

    const mealDataset = screen.getByLabelText("完整餐點資料集")
    expect(within(mealDataset).getByText("茶葉蛋")).toBeInTheDocument()
  })

  test("excludes seafood meals", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByLabelText("海鮮"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    const results = screen.getByLabelText("推薦清單")
    expect(within(results).queryByText("海鮮粥")).not.toBeInTheDocument()
    expect(within(results).queryByText("鮭魚沙拉")).not.toBeInTheDocument()
    expect(within(results).getByText("茶葉蛋")).toBeInTheDocument()
  })

  test("shows an empty state when no meals match", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByRole("searchbox"), "不存在的餐點")
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    expect(screen.getByText("未找到符合條件的餐點，請調整搜尋條件")).toBeInTheDocument()
  })

  test("adds query history after searching", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByLabelText("低卡"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    const history = screen.getByLabelText("最近查詢紀錄")
    expect(within(history).getByText("目標：均衡飲食")).toBeInTheDocument()
    expect(within(history).getByText("標籤：低卡")).toBeInTheDocument()
    expect(within(history).getByText(/結果數量：/)).toBeInTheDocument()
  })
})
