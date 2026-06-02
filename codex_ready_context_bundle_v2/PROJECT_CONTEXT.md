# PROJECT_CONTEXT.md

## Background

This project turns a Codex handoff bundle into a browsable, searchable, downloadable frontend interface.

The app is meant to help a future coding agent quickly answer:

- What is this repository?
- What stack does it use?
- What validation commands are available?
- What data is known or missing?
- What should happen next?

## Confirmed State

- Stack: React + TypeScript + Vite
- Package manager: npm
- Icon library: lucide-react
- UI language: readable Traditional Chinese
- Main source: `src/App.tsx`, `src/handoffData.ts`, `src/styles.css`
- Validation entrypoint: `npm run validate`
- Browser walkthrough: Chrome headless via `scripts/browser-walkthrough.mjs`
- Content guard: `scripts/check-content.mjs`
- Formatter: Prettier
- Unit/component tests: Vitest + React Testing Library
- CI: GitHub Actions runs `npm ci` and `npm run validate`

## Implemented App Features

- Handoff dashboard
- Data inventory table
- Phase-based task list
- Search and status filters
- AGENTS.md preview
- Browser-based Markdown downloads
- Copy confirmation toast
- Responsive layout with contained table overflow

## Known Follow-Ups

- Automated visual diff is not configured.
- Screenshot archive can be captured on demand with `npm run capture:screenshots`.
- Deployment target is not defined.
