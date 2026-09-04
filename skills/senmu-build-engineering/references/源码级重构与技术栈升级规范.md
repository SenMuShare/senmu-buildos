# Source-Level Refactoring and Technology-Stack Upgrades

Use this standard for restarting delivered legacy systems, modernization, stack upgrades, and admin-console rewrites when documentation, people, or business memory is incomplete; behavior must remain but framework/UI/structure may change; source contains business truth beyond PRD/chat; and hidden pages, dialogs, charts, permission controls, or API details can be missed.

Core rule:

```text
The legacy source defines existing behavior; the new stack re-expresses it.
```

## 1. Classify the Refactor

| Type | Definition | Allowed method |
| --- | --- | --- |
| New product prototype | No usable old source; business objective is primary | Implement from PRD/design |
| UI renewal | Business/API mostly unchanged; visual system changes | Map every old behavior; improve UI |
| Stack upgrade | Framework upgrade or cross-framework rewrite | Source-level migration; never infer from requirements alone |
| Business redesign | Business flow changes too | Requirement change and acceptance first |

Treat “logic cannot change,” “code-level refactor,” “page-by-page migration,” or “miss no functionality” as source-level migration by default.

The current design owner or `senmu-build-design` owns visual direction, system, interaction, motion, responsiveness, and accessibility. This standard owns legacy coverage, stack, and implementation migration.

## 2. Sources of Truth

Use this order for existing behavior:

1. Old routes, menus, and page entrypoints.
2. Old page source.
3. Old API wrappers and backend routes.
4. Controllers, models, services, helpers, middleware.
5. Tables, fields, enums, and states.
6. Screenshots from runnable production/local pages.
7. Historical PRD, API docs, and chat.

When source and documents conflict, provisionally follow source and register the conflict for confirmation.

## 3. Prohibited Methods

Never rewrite from PRD alone; present a mock shell as completed migration; migrate only main menus and omit hidden detail pages; migrate tables but omit dialogs, batch actions, charts, and permission controls; migrate frontend without reading backend/data fields; rename endpoints, parameter meaning, or state enums casually; or silently delete a feature because the new UI template lacks it.

## 4. Migration Matrices

Create matrices before business code. Durable Task State owns overall progress/recovery; matrices own domain coverage of routes, APIs, data models, and pages, not task status.

```text
governance/migration/
  ROUTE_MATRIX.md
  API_MATRIX.md
  DATA_MODEL_MATRIX.md
  PAGE_MIGRATION_TEMPLATE.md
```

For an admin system, record old route/title/source, new route/source, parent menu, hidden-page status, old APIs, table columns, filters, buttons, dialogs, navigation, charts, permission conditions, migration state, omissions, and risk.

Every old page is `not_started`, `in_progress`, `implemented`, `accepted`, or `deferred`. A deferred page states why; it cannot disappear.

## 5. Page Migration Loop

```text
Locate old route
  -> Read old page source section by section
  -> Extract APIs and backend methods
  -> Extract fields and states
  -> Record page migration
  -> Implement new page
  -> Compare old and new side by side
  -> Update matrix, tests, and Work Log
```

“Line by line” means inspect every line for business meaning, not mechanically translate languages. Every old method, condition, API call, and user action is classified as migrated, merged, deferred, or retirement-pending-confirmation.

## 6. Ant Design Pro Admin Upgrades

For React/Web/admin systems, prefer Ant Design for base UI; Ant Design Pro for layout and common admin templates; ProComponents for ProLayout, ProTable, ProForm, PageContainer; Ant Design Charts/AntV for ordinary business charts; and Ant Design X for assistant/chat/intelligent input/streaming UI.

- Compose available Pro/ProComponents rather than custom-building generic admin primitives.
- Prefer ProTable or Table for tables; ProForm or Form for forms; ProLayout/PageContainer for shell, breadcrumbs, menus, header.
- Prefer Ant Design Charts/AntV for trends, proportions, ranking, comparison; add ECharts only for complexity not reasonably expressible.
- Use Ant Design X for an AI assistant. If AI is new, label it separately and do not count it as legacy migration.

Audit new ProComponents, Ant Design X, Charts, ECharts, and related dependencies. For security findings, record risk, version, alternatives, and acceptance. Do not respond by hand-building everything; first seek a safe version, overrides, alternatives, or staged adoption.

## 7. Backend Source-Level Upgrade

Read routes, controllers/handlers, services/helpers, models/ORM, middleware/guards, validators/request parsing, table schemas/state fields, scheduled/async jobs, callbacks, payments, messaging, uploads, and other boundary code—not API docs alone.

For a new backend framework, record old/new endpoint, old-address compatibility, request/response mapping, enum mapping, permission/data-scope rules, and old-method migration status. Never invent replacement APIs without mapping the old implementation.

## 8. New Features

New capability is allowed but managed separately:

- Mark it new in the target-version PRD.
- Do not count it toward old-function migration.
- Do not change old-function acceptance.
- For AI, charts, reports, or automation, state business objects read, permission boundaries, and safety limits.

For example, an AI assistant absent from the old system is new. Migrate old functions from source, build the assistant shell with Ant Design X, then implement intelligence later under API, permission, and audit contracts.

## 9. Acceptance

Per page:

- Old page is runnable or has screenshot/source evidence; new page is runnable.
- Columns, filters, buttons, dialogs, details, navigation, charts, and permissions align item by item.
- Old/new API mappings are recorded; mock fields match old interface fields.
- No material layout or console errors remain.

Per phase:

- Matrices are current and omissions explicit.
- Quality gates ran.
- Work Log records changes, verification, risk, and next step.
- The owner can inspect old/new comparison evidence.

## 10. Required Alignment

Before coding, establish whether this is a new product or source migration; whether old behavior may be deleted/merged; whether old endpoint addresses require compatibility; whether UI may change style or must preserve it; which items are migration versus new capability; and whether backend semantics/data models migrate too.

If these materially changing choices remain unresolved, do not start implementation.
