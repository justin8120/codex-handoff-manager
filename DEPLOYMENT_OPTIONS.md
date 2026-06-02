# Deployment Options

## Selected Option: GitHub Pages

The project is configured to deploy the 智慧飲食建議系統 site through GitHub Actions to GitHub Pages.

- GitHub repository: https://github.com/justin8120/codex-handoff-manager
- GitHub Pages URL: https://justin8120.github.io/codex-handoff-manager/
- CI workflow: passed
- Deploy GitHub Pages workflow: passed
- latest confirmed successful workflow commit: a87a459

## GitHub Pages

GitHub Pages is the current best fit because the system is a static React + Vite展示網站 and the repository already uses GitHub Actions. It keeps CI and deployment in one place and works well for school project demos.

Repository pages use a path like:

```text
https://使用者名稱.github.io/repository-name/
```

For that reason, `vite.config.ts` sets the production `base` from `GITHUB_REPOSITORY` when the workflow runs on GitHub Actions. Local development and local production build remain unaffected.

Deployment flow:

```bash
npm ci
npm run validate
npm run build
upload dist
deploy to GitHub Pages
```

## Vercel

Vercel also supports Vite apps and provides fast preview deployments. It is useful when branch previews, serverless functions, or team preview URLs are required. Those needs are not required for the current static展示網站.

## Netlify

Netlify supports Vite static builds and simple drag-and-drop or Git-based deploys. It is a strong alternative if form handling, redirect rules, or Netlify-specific preview workflows are needed. The current project does not require those features.

## Risks / Follow-Ups

- automated visual diff is not configured
- project documents should stay synchronized after deployment changes
