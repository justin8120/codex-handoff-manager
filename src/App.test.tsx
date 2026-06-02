import { render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, test } from "vitest"
import { App } from "./App"

describe("App", () => {
  test("renders the smart diet recommendation system", () => {
    render(<App />)

    expect(screen.getByRole("heading", { name: "智慧飲食建議系統" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "餐點推薦" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "查詢紀錄" })).toBeInTheDocument()
  })

  test("filters meals by low-calorie and high-protein tags", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.selectOptions(screen.getByLabelText("健康目標"), "減脂")
    await user.click(screen.getByLabelText("低卡"))
    await user.click(screen.getByLabelText("高蛋白"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    const results = screen.getByLabelText("推薦清單")
    expect(within(results).getByText("鮮蝦酪梨沙拉")).toBeInTheDocument()
    expect(within(results).getByText("希臘優格莓果杯")).toBeInTheDocument()
    expect(within(results).queryByText("牛肉地瓜增肌盤")).not.toBeInTheDocument()
  })

  test("excludes meals with selected allergens or forbidden ingredients", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.selectOptions(screen.getByLabelText("健康目標"), "健康維持")
    await user.click(screen.getByLabelText("高蛋白"))
    await user.click(screen.getByLabelText("海鮮"))
    await user.click(screen.getByRole("button", { name: "搜尋 / 推薦" }))

    const results = screen.getByLabelText("推薦清單")
    expect(within(results).getByText("希臘優格莓果杯")).toBeInTheDocument()
    expect(within(results).queryByText("鮮蝦酪梨沙拉")).not.toBeInTheDocument()
    expect(within(results).queryByText("鮭魚糙米餐盒")).not.toBeInTheDocument()
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
