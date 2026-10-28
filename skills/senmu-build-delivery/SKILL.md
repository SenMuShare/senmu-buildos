---
name: senmu-build-delivery
description: "Design or run deployments, releases and rollback; resume operations; manage non-routine Git. Reuse adopted workflows."
---

# Delivery Management

Follow project release/recovery routes; reuse unchanged guidance in scope. Tie authorized actions to production and rollback facts. Routine commits do not activate.

## Route by Outcome

- Batches, worktrees, merges, hotfixes: [Code/Merges](references/code-management-and-integration.md).
- Cross-session or parallel work: [Change Units](references/multi-agent-change-units-and-version-line-closeout.md).
- Resumable review coverage: [Review Execution](../senmu-build-assurance/references/frozen-review-execution.md).
- Topology, projections, release units: [Repositories](references/repository-boundaries-and-release-units.md).
- Work/version logs, handoffs: [Logs](references/collaboration-and-version-logs.md).
- Versions, composition, retention: [Artifacts](references/version-artifacts-and-release.md).
- Authority, production, rollback: [Authorization](references/release-authorization-and-production-truth.md).
- Deployment design, recovery, secrets: [Deployments](references/deployment-testing-and-security.md). Public exposure: [Security baseline](references/security/public-service-security-baseline.md).

Read-only advice never merges, tags or deploys. Release entrypoints must be executable. Assurance handles explicit audits, disputes or required independent verdicts, not routine checks.

## Core Contract

- Recover authority, lines, batch, release unit and recovery from owners/Git. Ask only about consequential ambiguity.
- Reuse `in_progress` for shared version/acceptance/release/rollback. Isolate real parallel work. Never edit an integration line or reopen sealed work. Unrelated tasks cannot chain from another task branch; inseparable dependencies may use registered sealed-parent stacks with explicit baselines and integration order under Change Units.
- Changing agents/sessions preserves the Change Unit. `manage_change_unit.py inspect` locates its registered state; resume within existing write authority.
- One item does not finish a batch. `review` freezes a commit without sealing; repair open batches in place. Seal completed scope only after checks and required review/repairs. Releases require release authority.
- Declare `main` as `integration` or `release_ready`; stack only on sealed parents.
- Keep one release source; verify identity before tags/artifacts. Reuse valid source evidence; check artifacts/environments separately.
- Distinguish candidate, build, deployment, production verification and version. Tag established facts; preserve rollback.
- No release intent means no release; “do not release yet” persists. Product owns behavior changes. New commits renew candidate conclusions through changed/affected scope, not repeated full review or renewed unchanged authority.

Handoff implementation to Engineering, scope to Product, and state defects to Workflow.
