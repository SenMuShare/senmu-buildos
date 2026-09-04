---
name: senmu-build-project
description: Create or repair project governance, authority mapping, structure, and durable cross-stage state. Not for routine work under an established project system.
---

# Project Governance

Own the governance instance, authority structure, and cross-domain ownership boundaries; this is not a parent skill. Return ordinary work when project entrypoints suffice. Continue only for missing/conflicting governance, structural evolution, state-owner repair, or explicit governance work.

## Route by Outcome

- Create, assess, evolve governance: [Governance Instances](references/project-governance-instances-and-evolution.md).
- Staged established-project takeover: [Project Takeover](references/established-project-takeover-governance.md).
- Lifecycle, capability composition, done: [Project Practice](references/project-lifecycle-guide.md).
- Roots, layout, document ownership, maps: [Directories](references/project-directories-and-documentation.md).
- Discover real standards/on-demand index: [Standards Discovery](references/project-standard-discovery-and-on-demand-loading.md).
- Create/select/repair cross-stage task state: [Task State](references/task-execution-and-state-management.md).
- Project situations, handoffs, skill boundaries: [Adoption and Routing](references/project-adoption-handoff-and-scenario-routing.md).
- Read [Governance Levels](references/governance-levels-and-gates.md) only for an actual G0-G4/gate decision.

Read only what the outcome needs. Delivery owns Git execution.

Use [init_project_governance.py](scripts/init_project_governance.py) for new projects and [assess_project_governance.py](scripts/assess_project_governance.py) for zero-write established-project inventory. Default to bounded output; use `--verbose` only for complete registers. Script output is candidate fact, not confirmation, authorization, or runtime proof.

## Core Contract

- Establish authoritative root, Git/subproject/release-unit boundaries, entrypoints, owners, authorization, and non-goals.
- For one placement question, give the preferred owner/path and reason; do not write unless requested.
- Run `init_project_governance.py --mode plan-new` before explicitly authorized `initialize-new`.
- Inventory established projects read-only, then confirm owners semantically. Never overwrite them with defaults or create parallel truth.
- Shape structure around actual capabilities, lifecycle, and release units; project types do not replace facts or justify speculative modules.
- Maps navigate owners, entrypoints, state, and boundaries. Root `AGENTS.md` holds project differences, real commands, and overrides only.
- Use one Durable Task State Owner across stages. Continuing an existing task does not reactivate Project.
- Authorize initialization, migration, and remediation separately. Plans, script output, and static checks are not execution facts.

Handoff only when ownership changes, carrying scope, entrypoints, facts, evidence, unknowns, and authorization. Finish with no parallel owner and with validation, risk, and recovery information.
