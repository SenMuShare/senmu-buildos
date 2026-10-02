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

For substantive document editing, apply [Writing](../../senmu-build-engineering/references/technical-documentation-writing.md) as needed without transferring release authority or running another mandatory pass. Preserve candidate identity, compatibility limits and the distinction between prepared source and an actual release.

Each formal release unit maintains `VERSION` and `CHANGELOG.md`. When useful, separate:

- Internal: implementation, interfaces, database, deployment, tests, risks, rollback.
- User-facing: verified changes, user impact, compatibility and actions needed to upgrade. Exclude secrets, exploitable security details, private implementation facts and unpublished plans. A product's approved public model names, queue concepts or prices are not secret merely because they are technical or commercial.

Write for the upgrade decision: what changed, who is affected and what action is needed. Put real breaking changes and migration steps first when present. Use the project's existing format; remove unsupported praise and repeated summaries, not caveats, scope or recovery information. Claims come from the actual candidate and evidence; do not invent a benchmark, benefit, deadline or migration command. Do not impose a fixed line count or a separate style-review pass.

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

Learning owns lesson classification, evidence, promotion, retrieval and retirement under [Organizational Learning](../../senmu-build-learning/references/organizational-learning-and-governance-closure.md). Delivery records the actual incident or delivery outcome and links an existing applicable lesson or a justified candidate; it does not maintain another lesson schema or promotion threshold.

A second error alone does not prove a repeated cause or require a new rule, lesson or validator. Repair the confirmed source first; Learning decides whether durable reuse and residual-risk controls are justified. Apply relevant existing lessons without loading the entire history or starting Learning for every ordinary log entry. Stable domain contracts stay with their original owner, and every write remains subject to the current task's authority.


## 6. AI Logging Requirements

Follow the project's actual logging obligations. Mention log updates when they matter to recovery, delivery or the user's request; routine replies need not repeat a logging-status formula. If a durable record is genuinely needed and none exists, propose the smallest existing-owner-compatible location rather than silently creating a new ledger.

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

Record material delivery facts in the existing Work Log, then route reusable experience to Learning's current contract. A one-off execution error may need no durable rule change; a domain-rule or discoverability gap is repaired at its actual owner. Repeated failure is evidence to investigate, not automatic permission to create a Lessons ID, schema or executable gate.

Describe the actual mechanism, evidence, treatment and remaining uncertainty. Do not invent causes, timelines, wrong turns, owners or deadlines to make a report look complete. Use concrete source changes instead of generic promises to improve communication or be more careful.

A specific BuildOS component defect may enter its existing candidate path. Correct the application and BuildOS in their respective authorized repositories; do not confuse their version histories, installed snapshots or release states. Use the [BuildOS evolution](../../senmu-build-learning/references/buildos-evolution-and-upstream-feedback.md) method only when source improvement is in scope.
