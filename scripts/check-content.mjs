import { readFileSync } from "node:fs"
import { join, resolve } from "node:path"

const root = resolve(".")
const filesToCheck = [
  "README.md",
  "PROJECT_MAP.md",
  "DEPLOYMENT_OPTIONS.md",
  "package.json",
  ".gitignore",
  ".env.example",
  ".env.production.example",
  ".prettierrc",
  ".prettierignore",
  "eslint.config.js",
  "vite.config.ts",
  "tsconfig.app.json",
  ".github/workflows/ci.yml",
  ".github/workflows/deploy-pages.yml",
  "render.yaml",
  "src/App.tsx",
  "src/App.test.tsx",
  "src/mealData.ts",
  "src/main.tsx",
  "src/styles.css",
  "src/test/setup.ts",
  "src/vite-env.d.ts",
  "scripts/browser-walkthrough.mjs",
  "scripts/check-content.mjs",
  "backend/README.md",
  "backend/.env.example",
  "backend/requirements.txt",
  "backend/app/main.py",
  "backend/app/models.py",
  "backend/app/services/ai_provider.py",
  "backend/app/services/openai_meal_analyzer.py",
  "backend/app/services/url_fetcher.py",
  "backend/app/services/web_food_verifier.py",
  "backend/app/storage/meals_store.py",
  "backend/tests/test_api.py",
  "backend/data/meals.json",
]

const mojibakeTokens = [
  0xfffd, 0x648c, 0x8763, 0x9788, 0x929d, 0x5697, 0x96ff, 0x761d, 0x6470, 0x969e, 0x8761, 0x769c,
  0x82a3, 0x747c, 0x8130, 0x8751, 0x61aa, 0x92c6, 0x64bd, 0x657a, 0x6723, 0xf634, 0xf45d, 0xec27,
  0xe73f,
].map((codePoint) => String.fromCodePoint(codePoint))

const failures = []

for (const relativePath of filesToCheck) {
  const content = readFileSync(join(root, relativePath), "utf8")
  const lines = content.split(/\r?\n/)

  lines.forEach((line, index) => {
    if (mojibakeTokens.some((token) => line.includes(token))) {
      failures.push(`${relativePath}:${index + 1}: ${line.trim()}`)
    }
  })
}

if (failures.length > 0) {
  console.error("Content check failed. Possible mojibake found:")
  for (const failure of failures) console.error(`- ${failure}`)
  process.exitCode = 1
} else {
  console.log("Content check passed")
}
