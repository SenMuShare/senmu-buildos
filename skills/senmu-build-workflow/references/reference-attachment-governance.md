# Reference Attachment Governance

Use this standard to decide how a project or skill references external knowledge without loading large vendor manuals, stale snapshots, or irrelevant material into context.

## 1. Source Order

1. Use approved in-project rules that match the current version.
2. When an official MCP, CLI, API, or structured query exists, retrieve the specific relevant content.
3. If the tool is insufficient, read the official page or a small project summary.
4. Save a dated snapshot in the project or a temporary cache only for offline use, audits, or fixed-version reproduction.

## 2. Skill Package Boundary

- Retain only material required to execute the workflow and unavailable reliably on demand.
- Put references directly under `references/` and link them from `SKILL.md`; do not create nested vendor knowledge trees.
- Do not package complete `llms-full.txt`, whole-site documentation, or vendor material that might be useful later.
- Route ecosystem-specific rules conditionally and do not load them before the project selects that ecosystem.
- Put executable code in `scripts/` and output templates/reusable resources in `assets/`; do not mix them into references.
- Exclude secrets, accounts, real user data, customer information, and private project paths.

## 3. Project Snapshots

When a fixed snapshot is necessary, record source URL/title, acquisition date, applicable product/version and license, reason, refresh/expiry conditions, and relationship to the project's technical baseline or audit conclusion.

Keep large snapshots in the project or a disposable cache. A general skill retains the method for querying, validating, and refreshing—not the snapshot corpus.

## 4. Reading and Verification

- Read only references matched to the task.
- Verify current official material for specific APIs, components, configuration, and version differences; do not infer from stale examples.
- If tool output conflicts with the project's locked version, use the real dependency and corresponding version's official material, and record the difference.
- When the project repeatedly needs costly knowledge retrieval, maintain a small project summary; do not promote a one-off query automatically into a general skill.
