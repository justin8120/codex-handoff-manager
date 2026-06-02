import { render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, test } from "vitest"
import { App } from "./App"

describe("App", () => {
  test("renders the handoff manager", () => {
    render(<App />)

    expect(screen.getByRole("heading", { name: "Codex 專案交接管理器" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "資料盤點" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "階段任務" })).toBeInTheDocument()
  })

  test("filters inventory and tasks with search", async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(screen.getByRole("searchbox"), "Runtime")

    const inventory = screen.getByRole("table")
    expect(within(inventory).getByText("Runtime 驗證")).toBeInTheDocument()
    expect(within(inventory).queryByText("專案目的")).not.toBeInTheDocument()

    expect(screen.getByText("完成基礎驗證")).toBeInTheDocument()
    expect(screen.queryByText("建立 Codex 交接包")).not.toBeInTheDocument()
  })

  test("switches inventory and task status filters", async () => {
    const user = userEvent.setup()
    render(<App />)

    const inventorySection = screen.getByRole("heading", { name: "資料盤點" }).closest("section")
    expect(inventorySection).not.toBeNull()
    await user.click(
      within(inventorySection as HTMLElement).getByRole("button", { name: "待補齊" }),
    )

    const inventory = screen.getByRole("table")
    expect(within(inventory).getByText("自動化測試")).toBeInTheDocument()
    expect(within(inventory).getByText("Lint / Format")).toBeInTheDocument()
    expect(within(inventory).queryByText("專案目的")).not.toBeInTheDocument()

    const taskSection = screen.getByRole("heading", { name: "階段任務" }).closest("section")
    expect(taskSection).not.toBeNull()
    await user.click(within(taskSection as HTMLElement).getByRole("button", { name: "進行中" }))

    expect(screen.getByText("互動式瀏覽器走查")).toBeInTheDocument()
    expect(screen.queryByText("建立 Codex 交接包")).not.toBeInTheDocument()
  })

  test("renders download actions", () => {
    render(<App />)

    const downloads = screen.getByRole("heading", { name: "下載交接檔案" }).closest("section")
    expect(downloads).not.toBeNull()
    expect(within(downloads as HTMLElement).getByText("AGENTS.md")).toBeInTheDocument()
    expect(within(downloads as HTMLElement).getByText("TASKS.md")).toBeInTheDocument()
    expect(
      within(downloads as HTMLElement).getAllByRole("button", { name: "下載" }).length,
    ).toBeGreaterThan(0)
  })
})
