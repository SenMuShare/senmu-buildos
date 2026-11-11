---
name: senmu-build-project
description: "Start a project from an idea or reconcile missing/conflicting governance: structure, standards, AGENTS.md and task state. Infer needed capabilities from the requested work. Not routine implementation or business-agent prompts."
---

# Project Governance

Own governance, authority and cross-domain boundaries. Ordinary work follows project entrypoints; load methods for gaps, conflicts or requested evolution.

## Route by Outcome

- Create, assess, evolve governance: [Governance Instances](references/project-governance-instances-and-evolution.md).
- Staged takeover: [Takeover](references/established-project-takeover-governance.md).
- Lifecycle, capabilities, done: [Project Practice](references/project-lifecycle-guide.md).
- Roots, layout, document owners, maps: [Directories](references/project-directories-and-documentation.md).
- Low-cost task entry and maintenance: [Task Entry](references/task-entry-and-maintenance-economy.md).
- Reconcile AGENTS/host instructions and distill working principles: [Instruction Authoring](references/project-instruction-authoring.md). Preserve language, exceptions and code/non-code applicability; complete both tracks.
- Effective rules and conditional loading: [Standards Discovery](references/project-standard-discovery-and-on-demand-loading.md).
- Cross-stage task state: [Task State](references/task-execution-and-state-management.md).
- Handoffs and skill boundaries: [Adoption and Routing](references/project-adoption-handoff-and-scenario-routing.md).
- Actual G0-G4/gate decisions only: [Governance Levels](references/governance-levels-and-gates.md).

Read matching references only; Delivery owns Git.

New projects use [Initializer](scripts/init_project_governance.py); existing projects use read-only [Assessment](scripts/assess_project_governance.py). Output is bounded (`--verbose` expands registers), and proves neither acceptance, authority nor runtime behavior.

## Core Contract

- Establish roots, Git/subproject/release boundaries, entrypoints, owners, authority and non-goals. User intent outranks defaults within host permissions.
- Placement advice names the preferred owner/path and reason; advice alone does not authorize writes.
- Run `init_project_governance.py --mode plan-new` before authorized `initialize-new`; calibrate the draft and its language before adoption.
- Inventory existing projects read-only; confirm semantic ownership and migrate approved facts within authority, preserving recovery and one current standard.
- Infer needed capabilities from the user's goal, including implicit UI; complete classification before initialization. Scope structure to actual work and lifecycle.
- Persistent UI uses `design/UI_SPECIFICATION.md`, linked implementation and rendered checks under [UI Adoption](references/project-governance-instances-and-evolution.md#ui-adoption); no UI or one-off work stays light.
- Map task signals to Skills and real project owners/commands under [Index Contract](references/project-standard-discovery-and-on-demand-loading.md#4-index-contract). AGENTS keeps usable principles, constraints and routes, not manuals.
- Use one Durable Task State Owner across stages; resuming a task does not reactivate Project.
- Plan/audit first; authorized repair or initialization continues in scope, audit-only remains read-only. Preserve exceptions; merge equivalents without repeated growth. Source edits do not prove installation or model behavior.

Handoff ownership with scope, facts, evidence, gaps, authority and recovery.
