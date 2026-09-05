---
name: senmu-build-delivery
description: Govern development batches, non-routine Git, repository and release units, artifacts, deployment, rollback, and production state. Not for ordinary implementation.
---

# Delivery Management

Translate product intent into safe Git/release actions aligned with production facts and rollback. Routine commits do not activate.

## Route by Outcome

- Batches, worktrees, hotfixes, merges, multi-agent Git: [Code/Merges](references/code-management-and-integration.md).
- Cross-session ownership or parallel lines: [Change Units](references/multi-agent-change-units-and-version-line-closeout.md).
- Repository topology, projections, release units: [Repositories](references/repository-boundaries-and-release-units.md).
- Work/version logs and handoffs: [Logs](references/collaboration-and-version-logs.md).
- Versions, tags, archives, artifacts: [Artifacts](references/version-artifacts-and-release.md).
- Authorization, environments, production, rollback: [Authorization](references/release-authorization-and-production-truth.md).
- Deployment, secrets, security, post-release: [Security](references/deployment-testing-and-security.md).

Read-only advice never merges, tags, or deploys. A release entrypoint must be executable. Use Assurance only for disputes/hard gates.

## Core Contract

- Recover authority, lines, batch, release unit, authorization, and recovery from owners/Git. Ask only about outcome-changing ambiguity.
- Reuse `in_progress` for shared version/acceptance/release/rollback. Isolate real parallel work. Never write integration, reopen sealed work, or chain branches.
- Agent/session changes do not change the Change Unit. Resume it; use recoverable Release Control.
- One item does not complete a batch. Freeze after test/closeout intent; perform authorized local builds/checks; distribute, deploy, verify production changes, and tag under release authority.
- Require `main` as `integration` or `release_ready`; stack only on sealed parents.
- Keep one mutable release source; verify identity before tags/artifacts.
- Separate candidate, build, deployment, production verification, and version. Tag established facts; preserve rollback.
- No release intent means no release; “do not release yet” persists. Behavior changes require Product; new commits require candidate re-review, not automatic renewal of unchanged task authority.

Handoff implementation to Engineering, scope to Product, and state defects to Workflow.
