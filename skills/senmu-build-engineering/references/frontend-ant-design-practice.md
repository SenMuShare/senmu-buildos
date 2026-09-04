# Ant Design Frontend Profile

This profile owns implementation-changing Ant Design decisions: whether to adopt it, how to reuse it, and when to customize. It is not a component manual or design tutorial. Load for React/Web/SaaS/admin/tooling work when Ant Design is installed or explicitly evaluated.

Precedence: explicit product requirements and backend business boundaries > project design system, installed version, wrappers, and implementation > current official Ant Design material > this profile. Never replace a stable component system merely to apply this profile.

## 1. Adoption Boundary

- In an Ant Design project, preserve the installed major version, theme, wrappers, and page shell; do not add a second base UI system for an ordinary feature.
- Evaluate Ant Design first for new enterprise admin, operations, configuration, and data workbenches. On marketing or highly branded surfaces, reuse only suitable capabilities rather than forcing admin aesthetics.
- Compose mature components for standard tables, forms, filters, dialogs, drawers, pagination, feedback, and navigation.
- Add local customization only for explicit business interaction, performance, accessibility, compliance, security, or design-fidelity needs the ecosystem cannot meet.

The installed version is implementation fact. Read `package.json`, lockfile, and current usage before coding. Do not freeze one Ant Design version or recall props, tokens, and DOM structure from memory.

## 2. The Component Library Does Not Own Business Rules

Backend and business owners decide identity, roles, permissions, resource/data ownership, orders, balances, limits, billing, approval, audit, upload/import/export/transcoding, async jobs, retry/idempotency, AI calls, rate limits, safety, and sensitive data.

Hidden buttons, route redirects, and client validation improve experience but never replace server enforcement.

Built-in Confirm/Cancel labels, errors, and prompts are technical defaults. Cross-page nouns, actions, statuses, recovery, and tone come from Product content standards. This profile only chooses the component that carries them.

## 3. Ecosystem Selection Order

- General UI: use existing Ant Design components and project wrappers.
- AI interaction: evaluate a compatible Ant Design X only for concrete conversation, quick-intent, attachment, generation-state, or result-handoff needs.
- Ordinary charts: evaluate Ant Design Charts first; use ECharts/custom graphics only for evidenced expressiveness, performance, or existing-asset needs.
- Entry/exit, expansion, and feedback motion: prefer built-in behavior or CSS transitions. Reassess complex timelines, scroll-driven, or SVG motion through [Technology and Component Selection](技术路线与组件选型.md).

Before adding an ecosystem dependency, verify React/Ant Design compatibility, bundle cost, and maintenance. Do not add wrappers/tooling for “consistency” when current dependencies already solve one page.

## 4. Stable Page Boundaries

- Extend the existing shell, navigation, toolbar, table, detail, dialog, and drawer patterns.
- Start list-heavy business flows from mature tables with stable filter, pagination, batch action, and row action placement; cards are not the default table replacement.
- Let the form system own errors, required indicators, help, save, and cancel states.
- Show pending, processing, success, failure, and retry states for async actions; destructive operations require clear confirmation.
- A chart answers a concrete trend, comparison, proportion, distribution, or relationship question. Metrics come from business authority, never frontend invention.
- Wrap only stable repeated business compositions. Keep one-off styles local and theme/CSS overrides scoped.

## 5. AI Uses Hybrid Interaction

An AI feature is not automatically a universal chat box. First define its task—such as import, inspection, analysis, configuration, or pre-release checking—then decide whether Ant Design X is needed.

- When intent is unclear, offer selectable tasks, context sources, and capability boundaries.
- Make generation, failure, retry, and completion visible. Land results in actionable tables, forms, lists, citations, file cards, or navigable objects rather than text alone.
- Put high-risk actions behind GUI confirmation; AI does not execute irreversible work directly.
- Preserve the ordinary business flow when AI fails. Tasks suitable for standard forms, tables, or detail pages remain GUI operations.

Specific components such as `Welcome`, `Prompts`, `Sender`, and `Bubble` depend on current official APIs for the installed version; this profile does not maintain a catalog.

## 6. When Customization Is Allowed

Customize locally or choose a specialist solution for high-density workspaces, editors, players, timelines, canvases, maps, and diagrams; explicit designs that components cannot reasonably compose; evidenced performance/accessibility/compliance/security gaps; or stable repeated business compositions whose extraction removes real duplication.

Still compose existing primitives and preserve theme, typography, spacing, and interaction. Do not rely on private DOM, class names, or internals. A temporary bypass needs a version boundary and exit condition.

## 7. Query Current Official Knowledge

APIs, version differences, deprecations, tokens, semantic style hooks, and ecosystem capabilities change:

1. Prefer an available official Ant Design Skill, MCP, or CLI for components, examples, tokens, semantic structure, and changelog.
2. Otherwise use current official docs and migration guides.
3. Save a sourced/versioned temporary snapshot only to reproduce a specific old version when official access is insufficient; never copy the full external docs into BuildOS.

Align all findings to the installed version. Tool names and commands may change; do not hard-code a command catalog or make optional tools a BuildOS runtime dependency.

## 8. Completion

Check only result-changing boundaries: project version/wrappers preserved, mature capability reused, business rules left with authority, customization/dependencies justified, and AI results returned to actionable UI. This profile and project Engineering own component implementation. Route creation/review of visual direction, design system, accessibility, responsive behavior, and interaction quality to `senmu-build-design`; do not duplicate its manual here.
