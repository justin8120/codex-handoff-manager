# Codex Ready Context Bundle

This folder contains the source handoff documents for the Codex Handoff Manager project.

## Purpose

Use these files as the first reading path for a coding agent that needs to understand, validate, or continue the project.

The bundle is intentionally practical:

- It identifies the repository purpose and current stack.
- It records known data, missing context, and follow-up risks.
- It gives the next agent a compact operating guide.
- It provides a starter prompt that can be pasted into a new Codex session.

## Files

- `AGENTS.md`: Collaboration rules and working expectations for coding agents.
- `PROJECT_CONTEXT.md`: Project background, confirmed state, and open questions.
- `DATA_INVENTORY.md`: Known, missing, and review-needed data.
- `TASKS.md`: Phase-based task plan and current progress.
- `code_review.md`: Review checklist and quality focus areas.
- `PROMPT_FOR_CODEX.md`: Starter prompt for the next Codex handoff.

## Current Status

The frontend app is implemented with React, TypeScript, and Vite. It has readable Traditional Chinese UI copy, downloadable Markdown content, and automated validation through:

```bash
npm run validate
```

That validation runs content checks, TypeScript typecheck, production build, and a Chrome headless browser walkthrough.
