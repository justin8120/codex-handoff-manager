export type HealthGoal = "減脂" | "增肌" | "均衡飲食" | "健康維持"

export type DietTag = "低卡" | "高蛋白" | "低脂" | "健康餐" | "素食"

export type Allergen = "花生" | "牛肉" | "海鮮" | "乳製品"

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
  sourceType?: "文字" | "圖片" | "連結" | "資料集"
}

export const healthGoals: HealthGoal[] = ["減脂", "增肌", "均衡飲食", "健康維持"]

export const dietTags: DietTag[] = ["低卡", "高蛋白", "低脂", "健康餐", "素食"]

export const allergens: Allergen[] = ["花生", "牛肉", "海鮮", "乳製品"]

export const meals: Meal[] = [
  {
    id: "chicken-bento",
    name: "雞胸肉便當",
    type: "便當",
    calories: 480,
    protein: 38,
    tags: ["高蛋白", "低脂", "健康餐"],
    goals: ["減脂", "增肌", "均衡飲食"],
    ingredients: ["雞胸肉", "糙米", "花椰菜", "水煮蛋"],
    allergens: [],
    reason: "蛋白質充足且油脂較低，適合需要控制熱量又維持飽足感的使用者。",
    sourceType: "資料集",
  },
  {
    id: "tea-egg",
    name: "茶葉蛋",
    type: "點心",
    calories: 80,
    protein: 7,
    tags: ["低卡", "高蛋白", "低脂"],
    goals: ["減脂", "均衡飲食", "健康維持"],
    ingredients: ["雞蛋", "茶葉", "醬油", "香料"],
    allergens: [],
    reason: "熱量低且容易取得，適合作為補充蛋白質的小點心。",
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
    reason: "提供優質蛋白與好油脂，適合想吃清爽主餐的人。",
    sourceType: "資料集",
  },
  {
    id: "tofu-veggie-bowl",
    name: "豆腐蔬菜碗",
    type: "素食主餐",
    calories: 410,
    protein: 22,
    tags: ["低卡", "低脂", "健康餐", "素食"],
    goals: ["減脂", "均衡飲食", "健康維持"],
    ingredients: ["板豆腐", "糙米", "菠菜", "菇類"],
    allergens: [],
    reason: "以植物性蛋白搭配高纖蔬菜，適合素食與日常均衡飲食。",
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
    ingredients: ["燕麥", "希臘優格", "藍莓", "奇亞籽"],
    allergens: ["乳製品"],
    reason: "富含纖維並有穩定蛋白質，適合作為輕量早餐。",
    sourceType: "資料集",
  },
  {
    id: "beef-veggie-rice",
    name: "牛肉蔬菜飯",
    type: "主餐",
    calories: 610,
    protein: 40,
    tags: ["高蛋白", "健康餐"],
    goals: ["增肌", "均衡飲食"],
    ingredients: ["牛肉", "糙米", "青花菜", "甜椒"],
    allergens: ["牛肉"],
    reason: "蛋白質與複合碳水比例高，適合訓練日補充能量。",
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
    allergens: [],
    reason: "以天然澱粉搭配蛋白質，適合需要溫和飽足感的餐點。",
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
    ingredients: ["白米", "蝦仁", "魚片", "青蔥"],
    allergens: ["海鮮"],
    reason: "口感清淡且脂肪較低，適合想吃溫熱主食的人。",
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
    ingredients: ["毛豆", "糙米", "季節蔬菜", "豆干"],
    allergens: [],
    reason: "蔬菜、豆類與全穀搭配完整，適合追求日常均衡的素食者。",
    sourceType: "資料集",
  },
]
