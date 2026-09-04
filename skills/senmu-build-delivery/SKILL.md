---
name: senmu-build-delivery
description: Govern development batches, non-routine Git, repository and release units, artifacts, deployment, rollback, and production state. Not for ordinary implementation.
---

# Delivery Management

Translate product intent into safe Git/release actions aligned with production facts and rollback. Routine commits do not activate.

## Route by Outcome

- Batches, worktrees, hotfixes, merges, multi-agent Git: [Code/Merges](references/代码管理与合并规范.md).
- Cross-session ownership or parallel lines: [Change Units](references/多Agent变更单元与版本线收口规范.md).
- Repository topology, projections, release units: [Repositories](references/仓库边界与发布单元治理规范.md).
- Work/version logs and handoffs: [Logs](references/协作日志与版本日志规范.md).
- Versions, tags, archives, artifacts: [Artifacts](references/版本制品与发布规范.md).
- Authorization, environments, production, rollback: [Authorization](references/发布授权与生产事实协议.md).
- Deployment, secrets, security, post-release: [Security](references/部署测试与安全规范.md).

Read-only advice never merges, tags, or deploys. A release entrypoint must be executable. Use Assurance only for disputes/hard gates.

## Core Contract

- Recover authority, lines, batch, release unit, authorization, and recovery from owners/Git. Ask only about outcome-changing ambiguity.
- Reuse `in_progress` for shared version/acceptance/release/rollback. Isolate real parallel work. Never write integration, reopen sealed work, or chain branches.
- Agent/session changes do not change the Change Unit. Resume it; use recoverable Release Control.
- One item does not complete a batch. Freeze after test/closeout intent; build, deploy, verify, and tag only after release authorization.
- Require `main` as `integration` or `release_ready`; stack only on sealed parents.
- Keep one mutable release source; verify identity before tags/artifacts.
- Separate candidate, build, deployment, production verification, and version. Tag established facts; preserve rollback.
- No release intent means no release; “do not release yet” persists. Behavior changes require Product; new commits invalidate approval.

Handoff implementation to Engineering, scope to Product, and state defects to Workflow.
