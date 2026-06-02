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
}

export const healthGoals: HealthGoal[] = ["減脂", "增肌", "均衡飲食", "健康維持"]

export const dietTags: DietTag[] = ["低卡", "高蛋白", "低脂", "健康餐", "素食"]

export const allergens: Allergen[] = ["花生", "牛肉", "海鮮", "乳製品"]

export const meals: Meal[] = [
  {
    id: "chicken-quinoa-bowl",
    name: "舒肥雞胸藜麥碗",
    type: "主餐",
    calories: 480,
    protein: 38,
    tags: ["高蛋白", "低脂", "健康餐"],
    goals: ["減脂", "增肌", "均衡飲食"],
    ingredients: ["雞胸肉", "藜麥", "花椰菜", "甜椒"],
    allergens: [],
    reason: "蛋白質充足且油脂較低，適合需要控制熱量又想維持飽足感的使用者。",
  },
  {
    id: "tofu-veggie-bowl",
    name: "豆腐蔬食能量碗",
    type: "素食主餐",
    calories: 410,
    protein: 22,
    tags: ["低卡", "低脂", "健康餐", "素食"],
    goals: ["減脂", "均衡飲食", "健康維持"],
    ingredients: ["板豆腐", "糙米", "菠菜", "菇類"],
    allergens: [],
    reason: "以植物性蛋白搭配高纖蔬菜，熱量穩定且適合素食需求。",
  },
  {
    id: "salmon-rice-box",
    name: "鮭魚糙米餐盒",
    type: "主餐",
    calories: 520,
    protein: 34,
    tags: ["高蛋白", "健康餐"],
    goals: ["增肌", "均衡飲食", "健康維持"],
    ingredients: ["鮭魚", "糙米", "毛豆", "青花菜"],
    allergens: ["海鮮"],
    reason: "提供優質蛋白與好油脂，適合需要穩定能量與心血管保養的族群。",
  },
  {
    id: "beef-sweet-potato-plate",
    name: "牛肉地瓜增肌盤",
    type: "訓練餐",
    calories: 610,
    protein: 42,
    tags: ["高蛋白", "健康餐"],
    goals: ["增肌"],
    ingredients: ["牛肉", "地瓜", "蘆筍", "洋蔥"],
    allergens: ["牛肉"],
    reason: "蛋白質與複合碳水比例高，適合重量訓練後補充。",
  },
  {
    id: "greek-yogurt-berry-cup",
    name: "希臘優格莓果杯",
    type: "點心",
    calories: 260,
    protein: 20,
    tags: ["低卡", "高蛋白", "低脂", "健康餐"],
    goals: ["減脂", "健康維持"],
    ingredients: ["希臘優格", "藍莓", "燕麥", "奇亞籽"],
    allergens: ["乳製品"],
    reason: "低熱量且蛋白質密度高，適合作為下午點心或運動後輕補給。",
  },
  {
    id: "lentil-curry-rice",
    name: "扁豆咖哩蔬菜飯",
    type: "素食主餐",
    calories: 460,
    protein: 24,
    tags: ["高蛋白", "健康餐", "素食"],
    goals: ["增肌", "均衡飲食", "健康維持"],
    ingredients: ["扁豆", "糙米", "紅蘿蔔", "番茄"],
    allergens: [],
    reason: "豆類蛋白搭配全穀主食，能兼顧飽足、纖維與日常營養均衡。",
  },
  {
    id: "shrimp-avocado-salad",
    name: "鮮蝦酪梨沙拉",
    type: "沙拉",
    calories: 340,
    protein: 26,
    tags: ["低卡", "高蛋白", "低脂", "健康餐"],
    goals: ["減脂", "健康維持"],
    ingredients: ["蝦仁", "酪梨", "生菜", "小黃瓜"],
    allergens: ["海鮮"],
    reason: "熱量較低但蛋白質足夠，適合希望清爽進食又避免澱粉過量的人。",
  },
  {
    id: "peanut-chicken-noodles",
    name: "花生醬雞絲冷麵",
    type: "冷麵",
    calories: 550,
    protein: 31,
    tags: ["高蛋白"],
    goals: ["增肌", "均衡飲食"],
    ingredients: ["雞胸肉", "蕎麥麵", "花生醬", "小黃瓜"],
    allergens: ["花生"],
    reason: "適合需要較高熱量與蛋白質的訓練日，但花生過敏者應避開。",
  },
  {
    id: "chickpea-veggie-wrap",
    name: "鷹嘴豆蔬菜卷",
    type: "輕食",
    calories: 360,
    protein: 18,
    tags: ["低脂", "健康餐", "素食"],
    goals: ["均衡飲食", "健康維持"],
    ingredients: ["鷹嘴豆", "全麥餅皮", "生菜", "番茄"],
    allergens: [],
    reason: "蔬菜與豆類比例高，適合想要輕量但仍有飽足感的日常餐點。",
  },
]
