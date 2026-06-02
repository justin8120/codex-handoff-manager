import { render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, test } from "vitest"
import { App } from "./App"

describe("App", () => {
  test("renders the smart diet recommendation system", () => {
    render(<App />)

    expect(screen.getByRole("heading", { name: "智慧飲食建議系統" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "餐點推薦" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "餐點資料" })).toBeInTheDocument()
  })

  test("shows tea egg in the meal data section", () => {
    render(<App />)

    const mealData = screen.getByLabelText("完整餐點資料")
    expect(within(mealData).getByText("茶葉蛋")).toBeInTheDocument()
  })

  test("searches for tea egg", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByRole("searchbox"), "茶葉蛋")
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    const results = screen.getByLabelText("推薦清單")
    expect(within(results).getByText("茶葉蛋")).toBeInTheDocument()
    expect(within(results).queryByText("雞胸肉便當")).not.toBeInTheDocument()
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
