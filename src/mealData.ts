export type HealthGoal = "減脂" | "增肌" | "均衡飲食" | "健康維持"

export type DietTag =
  | "低卡"
  | "高蛋白"
  | "低脂"
  | "健康餐"
  | "素食"
  | "飯類"
  | "日式"
  | "丼飯"
  | "豬肉"

export type Allergen = "花生" | "牛肉" | "海鮮" | "乳製品" | "蛋"

export type MealSourceType = "文字" | "圖片" | "連結" | "資料集"

export type Meal = {
  id: string
  name: string
  type: string
  calories: number
  protein: number
  tags: DietTag[]
  goals: HealthGoal[]
  ingredients: string[]
  allergens: Allergen[]
  reason: string
  confidence?: number
  sourceType?: MealSourceType
  createdAt?: string
  isAiGenerated?: boolean
}

export const healthGoals: HealthGoal[] = ["減脂", "增肌", "均衡飲食", "健康維持"]

export const dietTags: DietTag[] = ["低卡", "高蛋白", "低脂", "健康餐", "素食"]

export const allergens: Allergen[] = ["花生", "牛肉", "海鮮", "乳製品"]

export const meals: Meal[] = [
  {
    id: "chicken-bento",
    name: "雞胸肉便當",
    type: "健康便當",
    calories: 480,
    protein: 38,
    tags: ["高蛋白", "低脂", "健康餐"],
    goals: ["減脂", "增肌", "均衡飲食"],
    ingredients: ["雞胸肉", "糙米", "青花菜", "紅蘿蔔"],
    allergens: [],
    reason: "雞胸肉提供高蛋白與低脂肪，搭配糙米與蔬菜，適合減脂或增肌族群。",
    sourceType: "資料集",
  },
  {
    id: "tea-egg",
    name: "茶葉蛋",
    type: "蛋白點心",
    calories: 80,
    protein: 7,
    tags: ["低卡", "高蛋白", "低脂"],
    goals: ["減脂", "均衡飲食", "健康維持"],
    ingredients: ["雞蛋", "茶葉", "醬油", "香料"],
    allergens: ["蛋"],
    reason: "茶葉蛋熱量低且方便取得，可作為補充蛋白質的小點心。",
    sourceType: "資料集",
  },
  {
    id: "salmon-salad",
    name: "鮭魚沙拉",
    type: "沙拉",
    calories: 360,
    protein: 28,
    tags: ["低卡", "高蛋白", "健康餐"],
    goals: ["減脂", "均衡飲食", "健康維持"],
    ingredients: ["鮭魚", "生菜", "番茄", "酪梨"],
    allergens: ["海鮮"],
    reason: "鮭魚富含蛋白質與 Omega-3，搭配大量蔬菜可提升飽足感。",
    sourceType: "資料集",
  },
  {
    id: "tofu-veggie-bowl",
    name: "豆腐蔬菜碗",
    type: "素食餐",
    calories: 410,
    protein: 22,
    tags: ["低卡", "低脂", "健康餐", "素食"],
    goals: ["減脂", "均衡飲食", "健康維持"],
    ingredients: ["板豆腐", "蔬菜", "藜麥", "菇類"],
    allergens: [],
    reason: "豆腐提供植物性蛋白質，搭配蔬菜與藜麥，營養均衡且適合素食者。",
    sourceType: "資料集",
  },
  {
    id: "oat-yogurt-cup",
    name: "燕麥優格杯",
    type: "早餐",
    calories: 290,
    protein: 18,
    tags: ["低卡", "低脂", "健康餐"],
    goals: ["減脂", "均衡飲食", "健康維持"],
    ingredients: ["燕麥", "希臘優格", "莓果", "堅果"],
    allergens: ["乳製品"],
    reason: "燕麥與優格可提供膳食纖維與蛋白質，適合早餐或點心。",
    sourceType: "資料集",
  },
  {
    id: "beef-veggie-rice",
    name: "牛肉蔬菜飯",
    type: "飯類",
    calories: 610,
    protein: 40,
    tags: ["高蛋白", "健康餐"],
    goals: ["增肌", "均衡飲食"],
    ingredients: ["牛肉", "蔬菜", "白飯", "洋蔥"],
    allergens: ["牛肉"],
    reason: "牛肉提供鐵質與蛋白質，適合需要較高熱量與蛋白質的增肌需求。",
    sourceType: "資料集",
  },
  {
    id: "sweet-potato-egg-plate",
    name: "地瓜雞蛋餐",
    type: "輕食",
    calories: 330,
    protein: 16,
    tags: ["低卡", "低脂", "健康餐"],
    goals: ["減脂", "均衡飲食", "健康維持"],
    ingredients: ["地瓜", "雞蛋", "小黃瓜", "番茄"],
    allergens: ["蛋"],
    reason: "地瓜提供複合碳水化合物，雞蛋補充蛋白質，整體熱量容易控制。",
    sourceType: "資料集",
  },
  {
    id: "seafood-congee",
    name: "海鮮粥",
    type: "粥品",
    calories: 420,
    protein: 25,
    tags: ["低脂", "健康餐"],
    goals: ["均衡飲食", "健康維持"],
    ingredients: ["白飯", "蝦仁", "魚片", "青菜"],
    allergens: ["海鮮"],
    reason: "粥品口感清淡，海鮮提供蛋白質，但海鮮過敏者需避免。",
    sourceType: "資料集",
  },
  {
    id: "veggie-bento",
    name: "蔬食便當",
    type: "素食便當",
    calories: 450,
    protein: 20,
    tags: ["低脂", "健康餐", "素食"],
    goals: ["均衡飲食", "健康維持"],
    ingredients: ["豆干", "蔬菜", "糙米飯", "菇類"],
    allergens: [],
    reason: "蔬食便當以植物性食材為主，搭配全穀類可維持均衡營養。",
    sourceType: "資料集",
  },
]
