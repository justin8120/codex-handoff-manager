# PROJECT_MAP.md

## Project Map

This repository contains a React + TypeScript website for managing a Codex project handoff bundle. It also keeps repaired source handoff documents under `codex_ready_context_bundle_v2/`.

## Detected Stack

- Frontend framework: React
- Language: TypeScript
- Build tool: Vite
- Unit/component test runner: Vitest + React Testing Library
- Browser walkthrough: Chrome headless via DevTools Protocol
- Formatter: Prettier
- Linter: ESLint flat config
- Icon library: lucide-react
- Package manager: npm, based on `package.json`

## File Structure

```text
.
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- .gitignore
|-- .prettierignore
|-- .prettierrc
|-- README.md
|-- PROJECT_MAP.md
|-- DEPLOYMENT_OPTIONS.md
|-- eslint.config.js
|-- index.html
|-- package-lock.json
|-- package.json
|-- tsconfig.json
|-- tsconfig.app.json
|-- tsconfig.node.json
|-- vite.config.ts
|-- scripts/
|   |-- browser-walkthrough.mjs
|   `-- check-content.mjs
|-- src/
|   |-- App.test.tsx
|   |-- App.tsx
|   |-- handoffData.ts
|   |-- main.tsx
|   |-- styles.css
|   `-- test/
|       `-- setup.ts
`-- codex_ready_context_bundle_v2/
    |-- AGENTS.md
    |-- DATA_INVENTORY.md
    |-- PROJECT_CONTEXT.md
    |-- PROMPT_FOR_CODEX.md
    |-- README.md
    |-- TASKS.md
    `-- code_review.md
```

Generated locally after validation:

```text
dist/
node_modules/
artifacts/browser-walkthrough/
```

## Key Files

- `package.json`: npm scripts, app dependencies, and quality tooling dependencies.
- `package-lock.json`: locked npm dependency graph.
- `DEPLOYMENT_OPTIONS.md`: Deployment decision document comparing GitHub Pages, Vercel, and Netlify.
- `index.html`: Vite HTML entry point.
- `vite.config.ts`: Vite React plugin configuration plus Vitest `jsdom` setup.
- `eslint.config.js`: ESLint flat config for JavaScript, TypeScript, browser code, Node scripts, and React Hooks rules.
- `.prettierrc`: Prettier formatting configuration.
- `.prettierignore`: Paths skipped by Prettier.
- `.github/workflows/ci.yml`: GitHub Actions workflow that runs `npm ci` and `npm run validate` on push and pull request.
- `src/main.tsx`: React application mount point.
- `src/App.tsx`: Main UI, readable Traditional Chinese navigation, filtering, copy, preview, and download interactions.
- `src/App.test.tsx`: Vitest + React Testing Library component tests.
- `src/test/setup.ts`: Test setup for jest-dom matchers and RTL cleanup.
- `src/handoffData.ts`: Typed static handoff bundle data and readable downloadable Markdown content.
- `src/styles.css`: Layout, responsive behavior, table, task card, preview, toolbar, and download styles.
- `scripts/browser-walkthrough.mjs`: Chrome headless production walkthrough for search, filters, copy, download, anchor navigation, mobile layout, and optional screenshots.
- `scripts/check-content.mjs`: Dependency-free content guard that checks readable project files for obvious mojibake fragments.
- `artifacts/browser-walkthrough/`: Optional generated screenshot archive from `npm run capture:screenshots`.
- `codex_ready_context_bundle_v2/`: Repaired readable source handoff documents.

## Available Commands

These commands are declared in `package.json`:

```bash
npm install
npm run dev
npm run check:content
npm run format
npm run format:check
npm run lint
npm run typecheck
npm run test
npm run test:watch
npm run build
npm run test:browser
npm run capture:screenshots
npm run validate
npm run preview
```

## Validation Flow

The standard project validation entrypoint is:

```bash
npm run validate
```

It runs in order:

1. `npm run check:content`
2. `npm run format:check`
3. `npm run lint`
4. `npm run typecheck`
5. `npm run test`
6. `npm run build`
7. `npm run test:browser`

## Unit/Component Test Coverage

`npm run test` runs Vitest with React Testing Library and currently covers:

- `App` renders the main handoff manager headings.
- Search filters inventory and task content.
- Inventory and task status filters switch visible results.
- Download section files and download buttons are present.

## Browser Walkthrough Coverage

`npm run test:browser` verifies the production build with Chrome headless:

- Readable hero, navigation, and metric values.
- Inventory search narrows results to `Runtime 驗證`.
- Inventory and task status filters return expected items.
- Copy action shows the `Prompt 已複製` toast.
- Anchor navigation reaches the downloads section.
- `TASKS.md` downloads successfully.
- Mobile layout collapses without page-level horizontal overflow.
- Wide table overflow remains contained inside the table scroller.

Optional screenshot capture:

```bash
npm run capture:screenshots
```

This writes:

- `artifacts/browser-walkthrough/desktop.png`
- `artifacts/browser-walkthrough/mobile.png`

## Completed Work

- Confirmed project structure and Vite React configuration.
- Installed dependencies with npm and generated `package-lock.json`.
- Built a readable Traditional Chinese UI for the handoff manager.
- Rebuilt generated Markdown downloads with readable handoff content.
- Repaired the source handoff documents under `codex_ready_context_bundle_v2/`.
- Added a dependency-free content check for readable project files.
- Added ESLint with TypeScript and React Hooks rules.
- Added Prettier formatter configuration and format check scripts.
- Added Vitest + React Testing Library unit/component tests.
- Added Chrome headless browser walkthrough coverage.
- Added optional desktop and mobile screenshot capture.
- Added GitHub Actions CI for `npm ci` and `npm run validate`.
- Fixed mobile grid overflow by allowing direct `.app-shell` children to shrink with `min-width: 0`.
- Prepared git version-control baseline and deployment decision document.

## Current Validation Result

Last completed validation:

```bash
npm run validate
```

Results:

- Content check completed successfully.
- Prettier format check completed successfully.
- ESLint completed successfully.
- TypeScript typecheck completed successfully.
- Vitest unit/component tests completed successfully.
- Production build completed successfully.
- Browser walkthrough completed successfully.
- Git baseline validation completed before the initial commit.

Screenshot capture was also run successfully:

```bash
npm run capture:screenshots
```

## Environment Status

Node.js/npm are installed at `C:\Program Files\nodejs`. The user shell reports normal PATH resolution for both `node` and `npm`.

To run the project in a normal shell:

```bash
npm install
npm run validate
npm run dev
npm run preview
```

## Risks / Follow-Ups

- Deployment target is not finalized. `DEPLOYMENT_OPTIONS.md` recommends GitHub Pages, pending user confirmation.
- Automated visual diff is not configured.
