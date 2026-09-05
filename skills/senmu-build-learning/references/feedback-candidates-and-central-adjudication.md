# Feedback Candidates and Central Adjudication

This standard is the intake boundary for BuildOS organizational learning. It lets agents submit high-signal BuildOS problems found in real projects to a local inbox for later user-triggered adjudication. It is not a user requirement pool, business-project inbox, board, analytics system, second project ledger, or automatic Skill editor.

## 1. What to Capture

A candidate must identify a BuildOS Skill, reference, template, script, Hook, rule, or runtime guidance and at least one real effect:

- Incorrect, conflicting, or misleading content caused a wrong decision, regression, or rework.
- Abstract, vague, or impractical content forced extra guessing or research.
- A rule, process, or default artifact created unnecessary work, over-implementation, or material inefficiency.
- The Skill conflicted with a real project, framework, or platform capability and had to be bypassed.
- Template/specification guidance produced an unclear, incomplete, or non-executable artifact.
- The same BuildOS-use failure recurred, showing that its true owner was not fixed.

Do not submit ordinary business requirements, feature bugs, project-specific facts, user product changes, general writing preferences, a one-off command typo, unverified hypotheses, or routine progress. A project issue qualifies only when the specific BuildOS content and resulting effect are identifiable.

## 2. One Capture Path

The agent using BuildOS decides and submits feedback; it does not infer a candidate from every user message. When a user says BuildOS is difficult, resolve the current request first, then test the BuildOS-target and real-effect criteria. If eligible, route through Learning:

```text
node <plugin-root>/hooks/feedback-cli.js submit \
  --component "<BuildOS Skill/reference/template/script/Hook>" \
  --summary "<problem>" \
  --impact "<error, confusion, extra work, inefficiency, or poor output>" \
  --project-root "<source-project-root>" \
  --evidence "<evidence-reference>" \
  --quiet
```

`--component` and `--impact` prevent business requests from masquerading as BuildOS feedback. `--evidence` may reference a session, file, command output, or workaround. `--quiet` emits no candidate ID or receipt. If the CLI is unavailable, do not claim the item was saved. Return only the minimum result when the user explicitly asks to query or process the inbox.

## 3. Local Inbox

The default inbox is `~/.senmu-buildos/feedback/`; `SENMU_BUILDOS_DATA_DIR` may select another local data root. The source project records where the problem occurred; the candidate is always feedback about BuildOS. Submission creates no business-project README, ledger, or governance structure, uploads nothing, and changes no Git state.

Each candidate is an independent JSON file with a stable fingerprint to prevent duplicate writes of one event. Store only:

- candidate ID, time, source Harness, and signal type;
- local project root, session ID, and available transcript reference;
- BuildOS component, concrete impact, and a length-limited short summary redacted for common secret patterns.

Use `0600` for files and `0700` for directories on systems supporting POSIX permissions. Redaction reduces risk but is not complete DLP; never put secrets or customer data in the summary.

## 4. Central Adjudication

When the user asks to process or organize the BuildOS inbox:

1. Locate the plugin root from the loaded Skill. Run `node <plugin-root>/hooks/feedback-cli.js pending --summary` for count, components, source projects, and time range. Then page only the candidates needed with `--json --limit <n> --offset <n>`; do not load the entire inbox by default.
2. Cluster by root cause, scope, and specialist owner—not wording or count. If a current Skill already covers the decision, inspect whether the actual Harness, project entrypoint, script, validator, and behavior tests consume it. Wrong behavior despite existing prose usually indicates an execution-source gap, not a need to repeat the rule. For chat-derived candidates or reports, a final summary is candidate evidence only: retrieve relevant original turns as needed to verify premises, user corrections, alternatives, and evidence against project/runtime facts. User statements are important input but not automatically verified facts; neither read the whole transcript mechanically nor rely only on the final answer.
3. Propose exactly one disposition per group: `discard`, `project`, `buildos_candidate`, or `needs_evidence`, with rationale.
4. Confirm classification and abstraction with the user before modifying any project, BuildOS source, installed instance, or release state.
5. After confirmation, write an independent decision receipt with `feedback-cli.js decide`. Preserve the original candidate; never rewrite history by deletion.

Minimum commands:

```bash
node <plugin-root>/hooks/feedback-cli.js pending --summary
node <plugin-root>/hooks/feedback-cli.js pending --json --limit 10 --offset 0
node <plugin-root>/hooks/feedback-cli.js decide --id <FB-id> --disposition <value> --note "<reason>"
```

## 5. Post-Adjudication Boundaries

- `discard`: one-off, noise, already governed but not followed, or cannot become a decidable action.
- `project`: specific to the source project; return it to requirement, architecture, implementation, process, or delivery authority without copying prose into the BuildOS inbox.
- `needs_evidence`: record the required reproduction, verification, or second-project sample; do not execute it as a durable rule.
- `buildos_candidate`: independent input to the BuildOS source project, implemented under BuildOS source-change authority with whole-repository impact analysis and matching tests; installation and release need their applicable authority.

An optional scheduled task may read pending candidates and propose adjudication. It must never modify or publish BuildOS without human review.
