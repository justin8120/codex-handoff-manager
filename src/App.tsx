import { useMemo, useState } from "react";
import {
  Archive,
  Bot,
  CheckCircle2,
  Copy,
  Download,
  FileText,
  Home,
  ListChecks,
  PackageCheck,
  Search,
} from "lucide-react";
import { agentsMarkdown, downloads, inventory, promptMarkdown, tasks } from "./handoffData";

const navItems = [
  { label: "總覽", href: "#home", icon: Home },
  { label: "資料盤點", href: "#inventory", icon: Archive },
  { label: "階段任務", href: "#tasks", icon: ListChecks },
  { label: "AGENTS.md", href: "#agents", icon: Bot },
  { label: "下載", href: "#downloads", icon: Download },
];

const statusClass = {
  已確認: "status known",
  待補齊: "status missing",
  待複查: "status review",
  已完成: "status done",
  進行中: "status active",
  待處理: "status waiting",
  未開始: "status missing",
};

const inventoryStatuses = ["全部", "已確認", "待補齊", "待複查"] as const;
const taskStatuses = ["全部", "已完成", "進行中", "待處理", "未開始"] as const;

function downloadTextFile(name: string, content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

async function copyText(content: string) {
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(content);
    return;
  }

  const textArea = document.createElement("textarea");
  textArea.value = content;
  textArea.style.position = "fixed";
  textArea.style.left = "-9999px";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  document.execCommand("copy");
  document.body.removeChild(textArea);
}

export function App() {
  const [inventoryStatus, setInventoryStatus] = useState<(typeof inventoryStatuses)[number]>("全部");
  const [taskStatus, setTaskStatus] = useState<(typeof taskStatuses)[number]>("全部");
  const [searchTerm, setSearchTerm] = useState("");
  const [copiedLabel, setCopiedLabel] = useState<string | null>(null);

  const completedTasks = tasks.filter((task) => task.status === "已完成").length;
  const progress = Math.round((completedTasks / tasks.length) * 100);
  const normalizedSearch = searchTerm.trim().toLowerCase();

  const filteredInventory = useMemo(
    () =>
      inventory.filter((item) => {
        const matchesStatus = inventoryStatus === "全部" || item.status === inventoryStatus;
        const matchesSearch =
          normalizedSearch.length === 0 ||
          `${item.category} ${item.status} ${item.description}`.toLowerCase().includes(normalizedSearch);
        return matchesStatus && matchesSearch;
      }),
    [inventoryStatus, normalizedSearch],
  );

  const filteredTasks = useMemo(
    () =>
      tasks.filter((task) => {
        const matchesStatus = taskStatus === "全部" || task.status === taskStatus;
        const matchesSearch =
          normalizedSearch.length === 0 ||
          `${task.title} ${task.status} ${task.details}`.toLowerCase().includes(normalizedSearch);
        return matchesStatus && matchesSearch;
      }),
    [taskStatus, normalizedSearch],
  );

  const handleCopy = async (label: string, content: string) => {
    await copyText(content);
    setCopiedLabel(label);
    window.setTimeout(() => setCopiedLabel(null), 1600);
  };

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="主要導覽">
        <div className="brand">
          <div className="brand-mark">
            <PackageCheck size={22} aria-hidden="true" />
          </div>
          <div>
            <strong>Codex Handoff</strong>
            <span>專案交接中心</span>
          </div>
        </div>
        <nav>
          {navItems.map((item) => (
            <a key={item.href} href={item.href}>
              <item.icon size={18} aria-hidden="true" />
              {item.label}
            </a>
          ))}
        </nav>
      </aside>

      <main>
        <section className="hero" id="home">
          <div className="eyebrow">React + TypeScript Handoff App</div>
          <h1>Codex 專案交接管理器</h1>
          <p>
            集中管理目前的專案背景、資料盤點、階段任務、AGENTS.md 預覽與下載內容，讓下一位 coding agent 可以快速接手。
          </p>
          <div className="hero-actions">
            <a className="primary-action" href="#inventory">
              查看資料盤點
            </a>
            <button onClick={() => downloadTextFile("AGENTS.md", agentsMarkdown)}>下載 AGENTS.md</button>
            <button onClick={() => handleCopy("Prompt", promptMarkdown)}>
              <Copy size={17} aria-hidden="true" />
              複製 Prompt
            </button>
          </div>
        </section>

        {copiedLabel ? <div className="toast">{copiedLabel} 已複製</div> : null}

        <section className="metrics" aria-label="專案狀態摘要">
          <div>
            <span>{inventory.length}</span>
            <p>盤點項目</p>
          </div>
          <div>
            <span>{tasks.length}</span>
            <p>階段任務</p>
          </div>
          <div>
            <span>{progress}%</span>
            <p>任務完成率</p>
          </div>
        </section>

        <section className="section" id="inventory">
          <div className="section-heading">
            <div>
              <div className="eyebrow">Inventory</div>
              <h2>資料盤點</h2>
            </div>
            <p>追蹤交接包目前掌握的上下文、缺口與仍需複查的環境資訊。</p>
          </div>
          <div className="toolbar" aria-label="資料盤點篩選工具">
            <label className="search-field">
              <Search size={17} aria-hidden="true" />
              <input
                type="search"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="搜尋資料、狀態或說明"
              />
            </label>
            <div className="segmented" aria-label="資料狀態篩選">
              {inventoryStatuses.map((status) => (
                <button
                  className={inventoryStatus === status ? "selected" : ""}
                  key={status}
                  onClick={() => setInventoryStatus(status)}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>類別</th>
                  <th>狀態</th>
                  <th>說明</th>
                </tr>
              </thead>
              <tbody>
                {filteredInventory.map((item) => (
                  <tr key={item.category}>
                    <td>{item.category}</td>
                    <td>
                      <span className={statusClass[item.status]}>{item.status}</span>
                    </td>
                    <td>{item.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filteredInventory.length === 0 ? <p className="empty-state">沒有符合條件的盤點項目。</p> : null}
        </section>

        <section className="section" id="tasks">
          <div className="section-heading">
            <div>
              <div className="eyebrow">Tasks</div>
              <h2>階段任務</h2>
            </div>
            <p>以階段方式呈現目前已完成、進行中與尚未開始的交接工作。</p>
          </div>
          <div className="toolbar" aria-label="任務篩選工具">
            <div className="segmented" aria-label="任務狀態篩選">
              {taskStatuses.map((status) => (
                <button
                  className={taskStatus === status ? "selected" : ""}
                  key={status}
                  onClick={() => setTaskStatus(status)}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>
          <div className="task-list">
            {filteredTasks.map((task) => (
              <article className="task-card" key={task.id}>
                <div className="task-icon">
                  <CheckCircle2 size={20} aria-hidden="true" />
                </div>
                <div>
                  <div className="task-title-row">
                    <h3>{task.title}</h3>
                    <span className={statusClass[task.status]}>{task.status}</span>
                  </div>
                  <p>{task.details}</p>
                </div>
              </article>
            ))}
          </div>
          {filteredTasks.length === 0 ? <p className="empty-state">沒有符合條件的任務。</p> : null}
        </section>

        <section className="section" id="agents">
          <div className="section-heading">
            <div>
              <div className="eyebrow">Preview</div>
              <h2>AGENTS.md 預覽</h2>
            </div>
            <p>提供給 coding agent 的協作規則與接手流程，可直接複製或下載。</p>
          </div>
          <div className="toolbar">
            <button className="utility-button" onClick={() => handleCopy("AGENTS.md", agentsMarkdown)}>
              <Copy size={17} aria-hidden="true" />
              複製 AGENTS.md
            </button>
          </div>
          <pre className="markdown-preview">
            <code>{agentsMarkdown}</code>
          </pre>
        </section>

        <section className="section" id="downloads">
          <div className="section-heading">
            <div>
              <div className="eyebrow">Downloads</div>
              <h2>下載交接檔案</h2>
            </div>
            <p>下載整理後的 Markdown 檔案，用於提交、交接或貼給下一位 agent。</p>
          </div>
          <div className="download-grid">
            {downloads.map((file) => (
              <article className="download-card" key={file.name}>
                <FileText size={24} aria-hidden="true" />
                <h3>{file.name}</h3>
                <p>{file.purpose}</p>
                <button onClick={() => downloadTextFile(file.name, file.content)}>
                  <Download size={17} aria-hidden="true" />
                  下載
                </button>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
