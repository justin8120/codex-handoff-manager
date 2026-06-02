# Starter Prompt for Codex

Please read `README.md`, `PROJECT_MAP.md`, and every file in `codex_ready_context_bundle_v2/`.

Your task:

1. Analyze the current repository structure and project state.
2. Identify the stack, package manager, build tool, and available scripts.
3. Run or confirm the validation flow.
4. Identify missing data, assumptions, and risks.
5. Move the next reasonable phase forward with small, reversible changes.

Use this validation command as the default project health check:

```bash
npm run validate
```

Do not invent APIs, schemas, deployment settings, authentication flows, or product requirements that are not present in the repository.

When done, report:

- Summary
- Changed
- Validation
- Assumptions
- Risks / Follow-ups
