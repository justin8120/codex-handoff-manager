import { useEffect, useMemo, useState } from "react"
import {
  Apple,
  Database,
  History,
  Search,
  ShieldCheck,
  Sparkles,
  SlidersHorizontal,
  Utensils,
} from "lucide-react"
import {
  addMeal,
  analyzeImage,
  analyzeText,
  analyzeUrl,
  fetchHealth,
  fetchMeals,
  recommendMeals,
  type BackendHealth,
} from "./api"
import {
  allergens,
  dietTags,
  healthGoals,
  meals,
  type Allergen,
  type DietTag,
  type HealthGoal,
  type Meal,
} from "./mealData"

type QueryRecord = {
  goal: HealthGoal
  tags: DietTag[]
  excludedAllergens: Allergen[]
  keyword: string
  resultCount: number
}

const defaultGoal: HealthGoal = "均衡飲食"

function toggleValue<T>(values: T[], value: T) {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value]
}

function formatList(values: string[]) {
  return values.length > 0 ? values.join("、") : "未指定"
}

function filterLocalMeals(
  mealDataset: Meal[],
  goal: HealthGoal,
  selectedTags: DietTag[],
  excludedAllergens: Allergen[],
  keyword: string,
) {
  const normalizedKeyword = keyword.trim().toLowerCase()
  return mealDataset.filter((meal) => {
    const matchesGoal = meal.goals.includes(goal)
    const matchesTags = selectedTags.every((tag) => meal.tags.includes(tag))
    const avoidsAllergens = excludedAllergens.every(
      (allergen) => !meal.allergens.includes(allergen),
    )
    const matchesKeyword =
      normalizedKeyword.length === 0 ||
      [meal.name, meal.type, meal.reason, ...meal.tags, ...meal.ingredients, ...meal.allergens]
        .join(" ")
        .toLowerCase()
        .includes(normalizedKeyword)

    return matchesGoal && matchesTags && avoidsAllergens && matchesKeyword
  })
}

function MealCard({ meal }: { meal: Meal }) {
  return (
    <article className="meal-card">
      <div className="meal-card-header">
        <div>
          <p className="meal-type">{meal.type}</p>
          <h3>{meal.name}</h3>
        </div>
        <span>{meal.calories} kcal</span>
      </div>
      <div className="meal-facts">
        <div>
          <span>蛋白質</span>
          <strong>{meal.protein}g</strong>
        </div>
        <div>
          <span>適合目標</span>
          <strong>{meal.goals.join(" / ")}</strong>
        </div>
      </div>
      <div className="tag-list" aria-label={`${meal.name} 飲食標籤`}>
        {meal.tags.map((tag) => (
          <span className="tag" key={tag}>
            {tag}
          </span>
        ))}
      </div>
      <p className="ingredients">
        <strong>主要食材：</strong>
        {meal.ingredients.join("、")}
      </p>
      <p className="ingredients">
        <strong>過敏原 / 禁忌食材：</strong>
        {formatList(meal.allergens)}
      </p>
      <p className="reason">
        <strong>推薦原因：</strong>
        {meal.reason}
      </p>
      {meal.sourceType || meal.confidence ? (
        <p className="source-note">
          {meal.sourceType ? `來源類型：${meal.sourceType}` : null}
          {meal.sourceType && meal.confidence ? "，" : null}
          {meal.confidence ? `信心分數：${Math.round(meal.confidence * 100)}%` : null}
          {meal.isAiGenerated ? "，AI 產生" : null}
        </p>
      ) : null}
    </article>
  )
}

export function App() {
  const [mealDataset, setMealDataset] = useState<Meal[]>(meals)
  const [backendHealth, setBackendHealth] = useState<BackendHealth | null>(null)
  const [backendError, setBackendError] = useState("")
  const [isOfflineMode, setIsOfflineMode] = useState(false)
  const [goal, setGoal] = useState<HealthGoal>(defaultGoal)
  const [selectedTags, setSelectedTags] = useState<DietTag[]>([])
  const [excludedAllergens, setExcludedAllergens] = useState<Allergen[]>([])
  const [keyword, setKeyword] = useState("")
  const [hasSearched, setHasSearched] = useState(false)
  const [recommendedMeals, setRecommendedMeals] = useState<Meal[]>(meals)
  const [history, setHistory] = useState<QueryRecord[]>([])
  const [description, setDescription] = useState("")
  const [mealLink, setMealLink] = useState("")
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [analysisResult, setAnalysisResult] = useState<Meal | null>(null)
  const [analysisMessage, setAnalysisMessage] = useState("")
  const [analysisError, setAnalysisError] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  useEffect(() => {
    async function loadBackendData() {
      try {
        const [health, backendMeals] = await Promise.all([fetchHealth(), fetchMeals()])
        setBackendHealth(health)
        setMealDataset(backendMeals)
        setRecommendedMeals(backendMeals)
        setBackendError("")
        setIsOfflineMode(false)
      } catch {
        setBackendError("AI 後端尚未啟動，請先啟動 FastAPI server。")
        setIsOfflineMode(true)
      }
    }

    void loadBackendData()
  }, [])

  const displayedMeals = hasSearched ? recommendedMeals : mealDataset
  const aiStatusLabel = backendError ? "未連線" : "已連線"
  const apiStatusLabel = backendHealth?.aiConfigured ? "已設定" : "未設定"

  const localRecommendation = useMemo(
    () => filterLocalMeals(mealDataset, goal, selectedTags, excludedAllergens, keyword),
    [excludedAllergens, goal, keyword, mealDataset, selectedTags],
  )

  const handleAnalyzeMeal = async () => {
    setIsAnalyzing(true)
    setAnalysisError("")
    setAnalysisMessage("")

    try {
      let result: Meal
      if (imageFile) {
        result = await analyzeImage(imageFile)
      } else if (mealLink.trim()) {
        result = await analyzeUrl(mealLink.trim())
      } else {
        result = await analyzeText(description.trim())
      }
      setAnalysisResult(result)
      setAnalysisMessage("AI 分析完成，可檢視後加入餐點資料集。")
    } catch (error) {
      setAnalysisError(error instanceof Error ? error.message : "AI 分析失敗。")
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleAddAnalysis = async () => {
    if (!analysisResult) return

    try {
      const savedMeal = isOfflineMode ? analysisResult : await addMeal(analysisResult)
      setMealDataset((current) => [savedMeal, ...current])
      setRecommendedMeals((current) => [savedMeal, ...current])
      setAnalysisMessage(`${analysisResult.name} 已加入餐點資料集，並可用於推薦。`)
      setAnalysisError("")
    } catch (error) {
      setAnalysisError(error instanceof Error ? error.message : "加入餐點資料集失敗。")
    }
  }

  const handleRecommend = async () => {
    setHasSearched(true)
    let results = localRecommendation

    if (!isOfflineMode) {
      try {
        results = await recommendMeals({
          healthGoal: goal,
          tags: selectedTags,
          excludedIngredients: excludedAllergens,
          keyword: keyword.trim() || null,
        })
        setBackendError("")
      } catch {
        setBackendError("AI 後端尚未啟動，請先啟動 FastAPI server。")
        setIsOfflineMode(true)
      }
    }

    setRecommendedMeals(results)
    setHistory((records) =>
      [
        {
          goal,
          tags: selectedTags,
          excludedAllergens,
          keyword: keyword.trim(),
          resultCount: results.length,
        },
        ...records,
      ].slice(0, 5),
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="主要導覽">
        <div className="brand">
          <div className="brand-mark">
            <Apple size={22} aria-hidden="true" />
          </div>
          <div>
            <strong>智慧飲食建議系統</strong>
            <span>OpenAI 後端分析</span>
          </div>
        </div>
        <nav>
          <a href="#home">
            <Utensils size={18} aria-hidden="true" />
            系統介紹
          </a>
          <a href="#ai-analysis">
            <Sparkles size={18} aria-hidden="true" />
            AI 餐點分析
          </a>
          <a href="#recommendation">
            <SlidersHorizontal size={18} aria-hidden="true" />
            餐點推薦
          </a>
          <a href="#results">
            <ShieldCheck size={18} aria-hidden="true" />
            推薦結果
          </a>
          <a href="#meal-dataset">
            <Database size={18} aria-hidden="true" />
            餐點資料集
          </a>
          <a href="#history">
            <History size={18} aria-hidden="true" />
            查詢紀錄
          </a>
        </nav>
      </aside>

      <main>
        <section className="hero" id="home">
          <div className="eyebrow">Smart Diet Recommendation System</div>
          <h1>智慧飲食建議系統</h1>
          <p>
            本系統包含 React 前端與 FastAPI 後端。正式 AI 分析會透過後端呼叫 OpenAI API，
            使用者可用文字、圖片或連結分析餐點，並將結果加入餐點資料集。
          </p>
          <div className="hero-actions">
            <a className="primary-action" href="#ai-analysis">
              AI 分析餐點
            </a>
            <a href="#meal-dataset">查看餐點資料集</a>
          </div>
        </section>

        <section className="metrics" aria-label="餐點資料概況">
          <div>
            <span>{mealDataset.length}</span>
            <p>筆餐點資料</p>
          </div>
          <div>
            <span>{dietTags.length}</span>
            <p>種飲食標籤</p>
          </div>
          <div>
            <span>{allergens.length}</span>
            <p>種禁忌食材</p>
          </div>
        </section>

        {backendError ? (
          <p className="status-message">{backendError} 目前為離線展示模式。</p>
        ) : null}

        <section className="section" id="ai-analysis">
          <div className="section-heading">
            <div>
              <div className="eyebrow">OpenAI Analysis</div>
              <h2>AI 餐點分析與資料集擴充</h2>
            </div>
            <p>
              AI 後端狀態：{aiStatusLabel}，API 狀態：{apiStatusLabel}
              {backendHealth
                ? `，Provider：${backendHealth.aiProvider}，Model：${backendHealth.model}，Fallback：${
                    backendHealth.fallbackEnabled ? "啟用" : "停用"
                  }`
                : ""}
            </p>
          </div>

          <div className="analysis-panel">
            <p className="notice">
              AI 分析結果僅供參考，實際營養數值仍需以餐點標示或專業資料為準。
            </p>
            <div className="control-row">
              <label className="control-group">
                文字描述
                <textarea
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="例如：雞胸肉便當，白飯半碗，青菜"
                />
              </label>
              <div className="control-group">
                <label htmlFor="meal-image">圖片上傳</label>
                <input
                  id="meal-image"
                  type="file"
                  accept="image/*"
                  onChange={(event) => setImageFile(event.target.files?.[0] ?? null)}
                />
                <span className="helper-text">{imageFile?.name || "尚未選擇餐點照片"}</span>
              </div>
            </div>
            <label className="control-group">
              連結輸入
              <input
                type="url"
                value={mealLink}
                onChange={(event) => setMealLink(event.target.value)}
                placeholder="貼上餐點介紹或菜單網址"
              />
            </label>
            <button
              className="primary-action recommend-button"
              onClick={handleAnalyzeMeal}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? "分析中..." : "AI 分析餐點"}
            </button>
            {analysisMessage ? <p className="status-message">{analysisMessage}</p> : null}
            {analysisError ? <p className="error-message">{analysisError}</p> : null}

            {analysisResult ? (
              <div className="analysis-result" aria-label="AI 分析結果">
                <MealCard meal={analysisResult} />
                <button className="utility-button" onClick={handleAddAnalysis}>
                  加入餐點資料集
                </button>
              </div>
            ) : null}
          </div>
        </section>

        <section className="section" id="recommendation">
          <div className="section-heading">
            <div>
              <div className="eyebrow">Recommendation</div>
              <h2>餐點推薦</h2>
            </div>
            <p>選擇健康目標、飲食標籤與要排除的食材，系統會篩選符合條件的餐點並附上推薦原因。</p>
          </div>

          <div className="recommendation-panel">
            <div className="control-row">
              <div className="control-group">
                <label htmlFor="health-goal">健康目標</label>
                <select
                  id="health-goal"
                  value={goal}
                  onChange={(event) => setGoal(event.target.value as HealthGoal)}
                >
                  {healthGoals.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>

              <label className="control-group">
                關鍵字搜尋
                <span className="search-field">
                  <Search size={17} aria-hidden="true" />
                  <input
                    type="search"
                    value={keyword}
                    onChange={(event) => setKeyword(event.target.value)}
                    placeholder="搜尋餐點、食材或推薦原因"
                  />
                </span>
              </label>
            </div>

            <fieldset className="control-group">
              <legend>飲食標籤</legend>
              <div className="choice-grid">
                {dietTags.map((tag) => (
                  <label className="choice" htmlFor={`tag-${tag}`} key={tag}>
                    <input
                      id={`tag-${tag}`}
                      type="checkbox"
                      checked={selectedTags.includes(tag)}
                      onChange={() => setSelectedTags((tags) => toggleValue(tags, tag))}
                    />
                    {tag}
                  </label>
                ))}
              </div>
            </fieldset>

            <fieldset className="control-group">
              <legend>過敏原或禁忌食材</legend>
              <div className="choice-grid">
                {allergens.map((allergen) => (
                  <label className="choice" htmlFor={`allergen-${allergen}`} key={allergen}>
                    <input
                      id={`allergen-${allergen}`}
                      type="checkbox"
                      checked={excludedAllergens.includes(allergen)}
                      onChange={() => setExcludedAllergens((items) => toggleValue(items, allergen))}
                    />
                    {allergen}
                  </label>
                ))}
              </div>
            </fieldset>

            <button className="primary-action recommend-button" onClick={handleRecommend}>
              搜尋 / 推薦
            </button>
          </div>
        </section>

        <section className="section" id="results">
          <div className="section-heading">
            <div>
              <div className="eyebrow">Results</div>
              <h2>推薦結果</h2>
            </div>
            <p>
              目前條件：{goal}，標籤：{formatList(selectedTags)}，排除：
              {formatList(excludedAllergens)}
            </p>
          </div>

          {!hasSearched ? (
            <p className="empty-state">請選擇條件後開始推薦，下方先顯示所有可推薦餐點。</p>
          ) : null}

          {hasSearched && recommendedMeals.length === 0 ? (
            <p className="empty-state">未找到符合條件的餐點，請調整搜尋條件</p>
          ) : null}

          <div className="meal-grid" aria-label="推薦清單">
            {displayedMeals.map((meal) => (
              <MealCard meal={meal} key={meal.id} />
            ))}
          </div>
        </section>

        <section className="section" id="meal-dataset">
          <div className="section-heading">
            <div>
              <div className="eyebrow">Dataset</div>
              <h2>餐點資料集</h2>
            </div>
            <p>完整列出目前系統用來推薦的餐點資料，包含營養資訊、飲食標籤、主要食材與禁忌食材。</p>
          </div>

          <div className="meal-data-grid" aria-label="完整餐點資料集">
            {mealDataset.map((meal) => (
              <MealCard meal={meal} key={meal.id} />
            ))}
          </div>
        </section>

        <section className="section" id="history">
          <div className="section-heading">
            <div>
              <div className="eyebrow">History</div>
              <h2>查詢紀錄</h2>
            </div>
            <p>每次查詢後會在下方保留最近條件與結果數量，方便比較不同飲食需求的推薦差異。</p>
          </div>

          {history.length === 0 ? (
            <p className="empty-state">目前尚無查詢紀錄，請先按下搜尋 / 推薦。</p>
          ) : (
            <div className="history-list" aria-label="最近查詢紀錄">
              {history.map((record, index) => (
                <article className="history-item" key={`${record.goal}-${record.keyword}-${index}`}>
                  <strong>查詢 {history.length - index}</strong>
                  <p>目標：{record.goal}</p>
                  <p>標籤：{formatList(record.tags)}</p>
                  <p>排除：{formatList(record.excludedAllergens)}</p>
                  <p>關鍵字：{record.keyword || "未指定"}</p>
                  <span>結果數量：{record.resultCount}</span>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
