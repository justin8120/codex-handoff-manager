# code_review.md

## Review Focus

Prioritize issues in this order:

1. Correctness: Search, filters, downloads, copy feedback, and navigation behave as expected.
2. Accessibility: Navigation, buttons, tables, and inputs have clear labels.
3. Responsiveness: Mobile layout does not overflow the page; wide tables remain scrollable inside their container.
4. Maintainability: Data types, status labels, and generated Markdown are easy to update.
5. Validation: `npm run validate` is reproducible on the target machine.

## Current Automated Coverage

`npm run test:browser` checks:

- Hero, navigation, and metrics render with readable text.
- Inventory search narrows to the expected item.
- Inventory and task filters return expected rows/cards.
- Copy action shows a confirmation toast.
- Downloads section is reachable through anchor navigation.
- `TASKS.md` downloads successfully.
- Mobile layout collapses without page-level horizontal overflow.

## Known Gaps

- No unit/component test framework.
- No automated visual diff for screenshot artifacts.
- No deployment target.
