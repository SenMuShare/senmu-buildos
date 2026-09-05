# Collaboration Logs and Changelogs

This standard governs three distinct records:

- **Changelog:** release and user-visible changes, internal traceability, rollback.
- **Work Log:** what a person/agent changed and verified, with remaining risk for handoff.
- **Lessons Learned Register:** verified recurring failures, source corrections, required constraints, and justified residual-risk controls.

They answer “what shipped in this version,” “what happened in this work,” and “which future signal requires which anti-regression action.” They do not replace one another or Git history. Do not copy entries for every mechanical commit. Log substantive tasks, integration, release, and interruption; changelog user-visible/delivery changes entering a version. Preserve project commit conventions; otherwise use concise intent/scope.

## 1. Purpose of the Work Log

In multi-person/agent work, a Work Log makes previous actions, evidence versus code-only state, task-owned versus historical files, integration/release readiness, deferred problems, and recovery discoverable without chat.

Record substantive change, release, integration, deployment, diagnosis, or important decision concisely. An explicitly read-only or proposal-before-edit task produces its report in the requested channel; logging is not an exception to its write boundary. Update durable files only when that write is authorized. It provides continuity, explicit completed/incomplete/verified/unverified commitments, and recovery after network, context, tool, or task interruption.

## 2. Locations and Ownership

Suggested:

```text
governance/
  logs/WORKLOG.md
  logs/2026-06.md
  lessons/LESSONS_LEARNED.md
  CHANGELOG_RULES.md
projects/<app-or-service>/
  CHANGELOG.md
  VERSION
```

Small projects may keep `governance/logs/WORKLOG.md`, `governance/lessons/LESSONS_LEARNED.md`, `CHANGELOG.md`, and `VERSION`.

Project owns Work Log schema/lifecycle; Learning owns Lessons. Delivery appends actual integration/build/deploy/release/rollback facts to the one Work Log and sends reusable evidenced candidates to Learning. Each independent release unit owns VERSION/CHANGELOG. Repository handoffs use `governance/logs/`; do not create logs per Skill, agent, or ordinary subdirectory. A release unit gets its own Work Log only when Project Map registers it as an independent project owner. Keep one project lessons owner unless trigger/gates are completely independent.

Durable Task State owns progress/recovery; WORKLOG appends chronological facts. Read task authority first and logs only for process history.

## 3. Changelog Rules

Each formal release unit maintains `VERSION` and `CHANGELOG.md`. When useful, separate:

- Internal: implementation, interfaces, database, deployment, tests, risks, rollback.
- User-facing: understandable features, experience, and redacted fixes—no internals, security detail, secrets, costs/pricing policy, payment configuration, or unpublished plans.

Record version, date, impact scope, additions, fixes, technical/deployment changes, tests/evidence, known risks, and rollback/previous stable version.

Every released Bug/Hotfix records issue, scope, evidence, release version, rollback, and unreleased changes. Redact user-visible explanation while retaining internal traceability.

## 4. Work Log Rules

Tools may prefill time, branch, commit, and files; the executor confirms actual completion, evidence, and gaps. Hooks do not edit logs or make a second commit after every ordinary commit.

Log feature/fix completion; requirement/design/deployment/version-rule changes; integration/release/deploy/rollback; local/production diagnosis; takeover of unfinished work; deferred risk; correction of an agent failure, owner correction, repeat rework, or governance gap; interruption by network/tool/context/permission; and an explicit unfinished next step.

G1 contract-preserving local work does not automatically log. Combine successive presentation-equivalent edits under one contract into a substantive batch entry at direction confirmation, commit/handoff preparation, or G2 escalation. With several logs, write only the registered task/unit collaboration owner and link/summarize elsewhere.

After a verified but unreleased bug fix, record branch/commit, why unreleased, release trigger, unreleased risk, and rollback/recovery basis.

At minimum include time; executor/thread/branch; G2-G4 level or release/retrospective gate; objective; changed files; decisions; performed checks; omitted checks; residual risk; next step; `Doc Impact` (changed authorities or reviewed applicability to which unit/version); retrospective conclusion when triggered; and interruption reason when incomplete.

Use only the matching variant from [Work Log Entry Templates](../assets/delivery-governance/WORKLOG_ENTRY.template.md) and tailor to reality; fields are not a universal form.

## 5. Lessons Learned Register

The formal Lessons Learned Register is structured, decidable, and retireable—not a complaint/story collection. Promote from logs/retrospectives only when recurrence is plausible or repeated; cause/treatment are evidenced; scope, trigger, required/prohibited actions are explicit; and a repeatable check exists, preferably a test/doctor/validator/CI gate for important paths.

Each entry contains ID, state, scope, trigger, symptom, confirmed cause, source-governance action, must, prohibited, repair verification, authoritative rule, source log, owner/review date, and supersession. Add an automatic gate plus cost/retirement only for justified residual risk.

States:

- `candidate`: insufficient evidence; not a hard rule.
- `active`: future agents must retrieve and execute it when in scope.
- `superseded`: historical, points to replacement.
- `retired`: trigger gone, preserves exit evidence.

Hard Gates:

- Retrieve all in-scope `active` entries at start; on trigger, execute required/prohibited actions and detection.
- On second occurrence, do not append another log only. Create/promote a lesson, explain why production still manufactures the defect and why source correction failed, and decide whether residual risk merits a gate.
- A lesson is not a second PRD, architecture, or deployment standard. Put stable rules in authority; retain failure, trigger, and anti-regression index in lessons.
- After mechanization, retain the lesson but use correct production entrypoints/defaults/executable contracts as primary defense and validators/tests for regression. Do not rely on an agent remembering prose.

Learning uniquely owns `assets/learning-governance/LESSONS_LEARNED.template.md`.

## 6. AI Logging Requirements

After substantive work, the final reply states whether a Work Log was written. Follow project rules. If no Work Log exists, suggest `governance/logs/WORKLOG.md` rather than creating it without scope.

Never log secrets, passwords, tokens, private keys, personal data, plaintext server configuration, or restricted business details without approved internal access controls.

Log actual work, changed files, performed/omitted checks, unfinished items, cause classification/repair/future constraint after rework, a Lessons ID when promotion criteria apply, and interruption/recovery point when incomplete.

## 7. Integration and Release Log Gates

Before integration, check that the Work Log covers main branch work; changelog covers user-visible/release changes; Bug/Hotfix has patch version, rollback, production-verification plan, and unreleased-work note; gaps and risks are explicit; Doc Impact is resolved (including unchanged-body applicability and immutable historical snapshots); and applicable active lessons/validators and new IDs are handled.

After release, add release version, commit, Tag, deployed services, artifact version, production results, rollback, unreleased work, actual local Tag/remote/remote Tag/PR/MR/platform Release state (`not_configured`, `local_only`, or `not_authorized` as applicable), and current base-document applicability calibration.

## 8. Boundary with Task Management

- Todo -> task/iteration/issue owner.
- Requirement change -> PRD/requirement.
- Technical decision -> technical design.
- Release change -> changelog.
- Process/handoff -> Work Log.
- Verified recurring failure/trigger/gate -> Lessons.

Information affecting future requirements, architecture, or release must also update the formal owner; Work Log alone is insufficient.

## 9. Retrospective Relationship

A retrospective affecting future execution enters the Work Log and follows Learning's retrospective standard for authority updates or BuildOS feedback. The Work Log keeps this event; Lessons accepts only evidenced recurring conclusions. One-off errors may stay in the log; project-rule gaps also update authority; repeated failures need a Lessons ID and executable control.

The retrospective entry includes problem, detection, cause, treatment, evidence, classification (`one-off execution error`, `project-specific rule gap`, or `general governance gap`), changed project/Skill owner, and future constraint.

If BuildOS may change, record cross-project abstraction evidence and create a separate task in the BuildOS source repository through `senmu-build-learning`, adding `$skill-creator` for entry/structure/trigger changes. An application Work Log does not own BuildOS version history.
