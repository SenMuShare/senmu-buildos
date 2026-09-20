---
name: senmu-build-project
description: Initialize or improve project governance and AGENTS.md, including shared working principles, project language, routing, authority and task state. Not for routine implementation or business runtime agents.
---

# Project Governance

Own governance instances, authority and cross-domain boundaries, not other Skills. Use project entrypoints for ordinary work; continue for governance gaps, conflicts, evolution or explicit requests.

## Route by Outcome

- Create, assess, evolve governance: [Governance Instances](references/project-governance-instances-and-evolution.md).
- Staged established-project takeover: [Project Takeover](references/established-project-takeover-governance.md).
- Lifecycle, capabilities, done: [Project Practice](references/project-lifecycle-guide.md).
- Roots, layout, document owners, maps: [Directories](references/project-directories-and-documentation.md).
- Reconcile AGENTS/host instructions and adopt working principles: [Instruction Authoring](references/project-instruction-authoring.md). Preserve project language and exceptions; complete both tracks.
- Effective rules and conditional loading: [Standards Discovery](references/project-standard-discovery-and-on-demand-loading.md).
- Cross-stage task state: [Task State](references/task-execution-and-state-management.md).
- Handoffs and skill boundaries: [Adoption and Routing](references/project-adoption-handoff-and-scenario-routing.md).
- Actual G0-G4/gate decisions only: [Governance Levels](references/governance-levels-and-gates.md).

Read only matching references. Delivery owns Git execution.

Use [init_project_governance.py](scripts/init_project_governance.py) for new projects and [assess_project_governance.py](scripts/assess_project_governance.py) for read-only existing-project inventory. Keep output bounded; `--verbose` expands registers. Script output is candidate evidence, not acceptance, authority or runtime proof.

## Core Contract

- Establish the actual root, Git/subproject/release boundaries, entrypoints, owners, authority and non-goals. User intent outranks Skill defaults; host permissions apply.
- Placement advice names the preferred owner/path and reason; advice alone does not authorize writes.
- Run `init_project_governance.py --mode plan-new` before authorized `initialize-new`; calibrate the draft and its language before adoption.
- Inventory existing projects read-only, then confirm owners semantically. Evolve original owners within authority; never overwrite them with defaults or create parallel truth.
- Shape structure around actual capabilities and lifecycle, not speculative modules.
- Maps route real capabilities to implementation, rules and checks under [Index Contract](references/project-standard-discovery-and-on-demand-loading.md#4-index-contract). AGENTS carries concise working principles, project constraints, commands and routes, not full manuals. Shared principles need not be unique to the project.
- Use one Durable Task State Owner across stages; resuming a task does not reactivate Project.
- Plan/audit first. An audit-and-repair or plan-and-initialize request covers scoped follow-through; audit-only stays read-only. Preserve exceptions, merge equivalent principles and avoid growth on repeated governance. Source edits do not prove installation or model behavior.

Handoff changed ownership with scope, facts, evidence, gaps, authority and recovery.
