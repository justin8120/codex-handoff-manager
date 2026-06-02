# Codex Handoff Manager

React + TypeScript website for managing a Codex project handoff bundle.

The project is now managed in git with a validated baseline commit. GitHub Pages deployment preparation is complete, but the project has not yet been pushed to GitHub or deployed.

## Features

- Home dashboard for the handoff bundle.
- Data inventory table.
- Phase-based task list.
- AGENTS.md preview.
- Browser-based Markdown downloads.
- Search and status filters for inventory and tasks.
- Copy buttons for AGENTS.md and the starter prompt.
- Readable Traditional Chinese UI copy and downloadable handoff Markdown.

## Stack

- React
- TypeScript
- Vite
- lucide-react

## Deployment

GitHub Pages is the selected deployment target. `DEPLOYMENT_OPTIONS.md` compares GitHub Pages, Vercel, and Netlify, and documents the remaining manual GitHub setup steps.

The deployment workflow is prepared at `.github/workflows/deploy-pages.yml`. It validates the app, builds with a GitHub Pages repository base path, uploads `dist`, and deploys through GitHub Pages Actions. Deployment has not been run yet because the repository has not been pushed to GitHub and Pages has not been enabled.

## Commands

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

## Environment requirements

- Node.js
- npm

Install Node.js/npm before running project commands. After the environment is ready, run:

```bash
npm install
npm run validate
```

## Current validation status

Current validation completed with Node.js `v24.16.0` and npm `11.13.0`:

```bash
npm install
npm run validate
```

The production build completed successfully. Local runtime verification was also completed:

- `npm run dev -- --host 127.0.0.1 --port 5173` returned HTTP 200 for the app shell.
- `npm run preview -- --host 127.0.0.1 --port 4173` returned HTTP 200 for the production build.
- `npm run test:browser` completed a production browser walkthrough with Chrome headless.
- `npm run capture:screenshots` can save desktop and mobile walkthrough screenshots under `artifacts/browser-walkthrough/`.
- `npm run validate` now runs the content check, Prettier check, ESLint, typecheck, unit/component tests, production build, and browser walkthrough.

Current UI/content cleanup status:

- User-facing UI copy, filter statuses, task details, and generated Markdown downloads have been rewritten into readable Traditional Chinese.
- A source scan of readable project files, including `codex_ready_context_bundle_v2/`, found no obvious mojibake fragments after cleanup.
- Automated browser interaction testing now covers search, status filters, copy confirmation, download, anchor navigation, and mobile layout.
- `npm run check:content` guards the readable project files against obvious mojibake regressions.
- `npm run capture:screenshots` has been used to generate desktop and mobile reference screenshots in `artifacts/browser-walkthrough/`.
- `npm run lint` runs ESLint with TypeScript and React Hooks rules.
- `npm run format:check` runs Prettier formatting verification.
- `npm run test` runs Vitest + React Testing Library component tests.
- Git version control is initialized with a validated project baseline.
- GitHub Pages deployment workflow is prepared, but GitHub repository push and Pages activation are still pending.

See `PROJECT_MAP.md` for the current project map and static read-check summary.
