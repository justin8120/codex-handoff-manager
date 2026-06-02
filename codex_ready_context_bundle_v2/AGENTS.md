# AGENTS.md

## Purpose

This repository is a Codex project handoff center. Treat it as the entry point for understanding and continuing the work.

## Working Rules

1. Read `README.md`, `PROJECT_MAP.md`, and the files in `codex_ready_context_bundle_v2/` before making changes.
2. Check `package.json` to confirm available scripts.
3. Before editing, identify the current project state and the next most reasonable phase.
4. Prefer small, reversible changes that improve handoff quality.
5. After changes, run the narrowest relevant validation. For normal project validation, use:

```bash
npm run validate
```

6. Do not invent APIs, database schemas, authentication flows, deployment targets, or business rules that are not present in the repo.

## Current Validation Flow

`npm run validate` runs:

1. `npm run check:content`
2. `npm run typecheck`
3. `npm run build`
4. `npm run test:browser`

## Reporting Format

When finishing a task, report:

- Summary: What changed.
- Changed: Files or behavior touched.
- Validation: Commands run and results.
- Assumptions: Important assumptions.
- Risks / Follow-ups: Remaining work or constraints.
