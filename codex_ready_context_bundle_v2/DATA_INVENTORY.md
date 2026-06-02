# DATA_INVENTORY.md

## Project Data Inventory

| Category             | Status    | Notes                                                                                                        |
| -------------------- | --------- | ------------------------------------------------------------------------------------------------------------ |
| Project purpose      | Confirmed | Build a Codex handoff manager for project continuation.                                                      |
| Frontend stack       | Confirmed | React + TypeScript + Vite.                                                                                   |
| Package manager      | Confirmed | npm with `package-lock.json`.                                                                                |
| Icon system          | Confirmed | lucide-react.                                                                                                |
| Runtime validation   | Confirmed | Local HTTP checks and browser walkthrough are available.                                                     |
| Content readability  | Confirmed | UI, generated downloads, and source handoff docs have been repaired.                                         |
| Content guard        | Confirmed | `npm run check:content` scans readable project files for obvious mojibake.                                   |
| Full validation      | Confirmed | `npm run validate` runs content check, format check, lint, typecheck, tests, build, and browser walkthrough. |
| Unit/component tests | Confirmed | Vitest + React Testing Library covers render, search, filters, and download actions.                         |
| Lint/format tools    | Confirmed | ESLint and Prettier are configured.                                                                          |
| CI                   | Confirmed | GitHub Actions runs `npm ci` and `npm run validate` on push and pull request.                                |
| Deployment target    | Missing   | No deployment environment is defined.                                                                        |
| Screenshot archive   | Confirmed | `npm run capture:screenshots` saves desktop and mobile screenshots.                                          |
| Visual diff          | Missing   | Screenshot capture exists, but automated visual comparison is not configured.                                |
