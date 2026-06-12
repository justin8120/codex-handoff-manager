import type { Allergen, DietTag, HealthGoal, Meal, MealGoal, MealSourceType } from "./mealData"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

export type BackendHealth = {
  status: string
  aiProvider: string
  aiConfigured: boolean
  model: string
  fallbackEnabled: boolean
}

export type BackendMeal = {
  id: string
  mealName: string
  mealType: string
  estimatedCalories: number
  estimatedProtein: number
  tags: string[]
  mainIngredients: string[]
  allergens: string[]
  recommendationReason: string
  confidence: number
  sourceType: "text" | "image" | "url"
  createdAt: string
  isAiGenerated: boolean
}

export type RecommendPayload = {
  healthGoal: HealthGoal
  tags: DietTag[]
  excludedIngredients: Allergen[]
  keyword: string | null
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: options?.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...options,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    const message = payload?.detail ?? "AI 後端請求失敗，請確認 FastAPI server 是否正常啟動。"
    throw new Error(message)
  }

  return response.json() as Promise<T>
}

export function backendMealToMeal(meal: BackendMeal): Meal {
  return {
    id: meal.id,
    name: meal.mealName,
    type: meal.mealType,
    calories: meal.estimatedCalories,
    protein: meal.estimatedProtein,
    tags: meal.tags as DietTag[],
    goals: inferGoals(meal),
    ingredients: meal.mainIngredients,
    allergens: meal.allergens as Allergen[],
    reason: meal.recommendationReason,
    confidence: meal.confidence,
    sourceType: sourceTypeLabel(meal.sourceType),
    createdAt: meal.createdAt,
    isAiGenerated: meal.isAiGenerated,
  }
}

export function mealToBackendMeal(meal: Meal): BackendMeal {
  return {
    id: meal.id,
    mealName: meal.name,
    mealType: meal.type,
    estimatedCalories: meal.calories,
    estimatedProtein: meal.protein,
    tags: meal.tags,
    mainIngredients: meal.ingredients,
    allergens: meal.allergens,
    recommendationReason: meal.reason,
    confidence: meal.confidence ?? 0.8,
    sourceType: sourceTypeValue(meal.sourceType),
    createdAt: meal.createdAt ?? new Date().toISOString(),
    isAiGenerated: meal.isAiGenerated ?? true,
  }
}

export async function fetchHealth(): Promise<BackendHealth> {
  return request<BackendHealth>("/api/health")
}

export async function fetchMeals(): Promise<Meal[]> {
  const payload = await request<BackendMeal[]>("/api/meals")
  return payload.map(backendMealToMeal)
}

export async function analyzeText(description: string): Promise<Meal> {
  const payload = await request<BackendMeal>("/api/analyze/text", {
    method: "POST",
    body: JSON.stringify({ description }),
  })
  return backendMealToMeal(payload)
}

export async function analyzeImage(file: File, description = ""): Promise<Meal> {
  const formData = new FormData()
  formData.append("file", file)
  if (description.trim()) {
    formData.append("text", description.trim())
    formData.append("description", description.trim())
  }
  const payload = await request<BackendMeal>("/api/analyze/image", {
    method: "POST",
    body: formData,
  })
  return backendMealToMeal(payload)
}

export async function analyzeUrl(url: string): Promise<Meal> {
  const payload = await request<BackendMeal>("/api/analyze/url", {
    method: "POST",
    body: JSON.stringify({ url }),
  })
  return backendMealToMeal(payload)
}

export async function addMeal(meal: Meal): Promise<Meal> {
  const payload = await request<BackendMeal>("/api/meals", {
    method: "POST",
    body: JSON.stringify(mealToBackendMeal(meal)),
  })
  return backendMealToMeal(payload)
}

export async function recommendMeals(payload: RecommendPayload): Promise<Meal[]> {
  const response = await request<BackendMeal[]>("/api/recommend", {
    method: "POST",
    body: JSON.stringify(payload),
  })
  return response.map(backendMealToMeal)
}

export function inferGoals(meal: BackendMeal): MealGoal[] {
  const goals = new Set<MealGoal>()
  const tags = meal.tags.join(" ")
  const profile = `${meal.mealName} ${meal.mealType} ${tags} ${meal.recommendationReason}`
  const isFriedOrHighFat = /炸物|油炸|高脂肪|高熱量/.test(profile)
  const isHighCalorie = meal.estimatedCalories >= 700
  const isExplicitLowCalorie = meal.tags.includes("低卡")
  const isHealthyLeanMeal =
    !isFriedOrHighFat &&
    (/雞胸肉健康餐|水煮餐|沙拉|蔬菜/.test(profile) ||
      meal.tags.includes("健康餐") ||
      meal.tags.includes("低脂"))

  if (
    (meal.estimatedCalories <= 450 || isExplicitLowCalorie || isHealthyLeanMeal) &&
    !isFriedOrHighFat &&
    (!isHighCalorie || isExplicitLowCalorie)
  ) {
    goals.add("減脂")
  }
  if (meal.estimatedProtein >= 25 || meal.tags.includes("高蛋白")) {
    goals.add("增肌")
    goals.add("高蛋白補充")
  }
  if (isFriedOrHighFat) {
    goals.add("偶爾享用")
    return [...goals]
  }
  if (isHealthyLeanMeal || meal.estimatedProtein >= 15) goals.add("均衡飲食")
  if (meal.estimatedCalories <= 450 || isHealthyLeanMeal) goals.add("健康維持")
  return [...goals]
}

function sourceTypeLabel(sourceType?: MealSourceType | BackendMeal["sourceType"]): MealSourceType {
  if (sourceType === "image") return "圖片"
  if (sourceType === "url") return "連結"
  if (sourceType === "資料集") return "資料集"
  return "文字"
}

function sourceTypeValue(sourceType?: MealSourceType): BackendMeal["sourceType"] {
  if (sourceType === "圖片") return "image"
  if (sourceType === "連結") return "url"
  return "text"
}
