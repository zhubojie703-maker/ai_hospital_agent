---
name: vibe-frontend-skeleton
description: Plan and enforce a frontend skeleton before asking AI to build or refactor UI. Use when a task involves creating, redesigning, or expanding a web/app frontend and needs decisions about visual style, frontend stack, UI component library, directory structure, module boundaries, component reuse, design tokens, responsive rules, or an implementation plan.
---

# Vibe Frontend Skeleton

Use this skill before building or heavily changing frontend pages. The goal is to make AI-generated UI grow from one coherent skeleton instead of becoming a collection of unrelated screens.

## Workflow

1. Define the product role and page purpose.
   - Identify the target user, core workflow, and first-screen task.
   - Decide whether the interface should feel operational, editorial, consumer, clinical, financial, playful, etc.

2. Lock the visual language.
   - Specify color roles, typography scale, spacing, radius, borders, shadows, density, card style, button shape, and chart style.
   - Prefer a small set of reusable design tokens over one-off CSS values.

3. Choose the frontend technical skeleton.
   - Name the framework, charting library, state/session pattern, data access pattern, and any UI library already used.
   - Keep choices consistent with the existing project unless there is a clear reason to change.

4. Define information architecture and module boundaries.
   - List pages/views and what each owns.
   - Separate navigation, layout shell, data access, chart rendering, domain copy, and page-specific logic.
   - Avoid putting all UI, data, and styling decisions in one long page file when the project is growing.

5. Define component reuse rules.
   - Identify repeated components such as KPI cards, filter bars, insight panels, chart blocks, tables, chat panels, status badges, and action buttons.
   - Give each component stable dimensions and responsive behavior.
   - Make variants explicit instead of duplicating near-identical markup.

6. Prepare the style system.
   - Centralize tokens for colors, type, spacing, radius, and chart palettes.
   - Document page density, table behavior, mobile behavior, empty states, loading states, and error states.
   - For AI/product dashboards, keep text concise and avoid feature-explaining copy inside the app.

7. Write an implementation plan before editing.
   - Convert the skeleton into a short checklist.
   - Implement the shared structure first, then page-specific content.
   - Verify by running the app and checking representative desktop/mobile views.

## Output Expectations

When applying this skill, produce or update these artifacts when useful:

- A frontend skeleton/spec document under `docs/`.
- Shared style tokens or constants in the frontend code.
- Reusable page/component helpers for repeated UI blocks.
- A concise change log explaining which skeleton decisions were applied.

## Quality Checks

- Pages share the same spacing, card density, typography, and chart language.
- Navigation labels, page titles, and action buttons follow one naming style.
- Repeated components are implemented once or clearly parameterized.
- Tables and charts have predictable sizes and do not shift when data changes.
- The first screen is the usable product experience, not a marketing explanation.
- The implementation is small enough to maintain and aligned with the existing stack.
