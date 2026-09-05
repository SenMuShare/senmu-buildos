# Code Management and Integration

Use this standard only for non-routine Git decisions, parallel execution surfaces, integration, and version-line governance. Current project branching policy prevails. Local Git is complete by itself; use remotes, PR/MR, CI, and platform Releases only when they exist and authority covers them.

## 1. Establish the Scene

Read-only recover authority root/repository, Git state, integration line, open batch, release unit, concurrent writers, shared resources, and authority. Decide line, branch, surface, and phase from product-version placement -> batch/Change Unit -> writer/worktree -> delivery intent. Agent count does not decide product versions or topology.

Infer and proceed when owners, tasks, Git, and context suffice. Ask once in product language only when a choice changes version placement, batch cutoff, cost, data safety, or production outcome—not Git mechanics.

Defaults:

- Continue one `in_progress` unit for successive requirements in the same open batch with shared acceptance/release/rollback. One item is not batch completion.
- Without test/closeout intent, remain in development; without release intent, remain unreleased. Implementation does not authorize seal, integration, full candidate gates, or release.
- “Send for testing/close this batch/prepare release” freezes and forms a candidate without production authority. “Integrate into current version” permits integration only. “Release/go live” opens a bounded session for an exact candidate.
- Create a new unit only for another target version, independent acceptance/release/rollback, a sealed current unit, or required parallel isolation. Future unimplemented requirements go to Product, not empty branches.

Read-only inspection:

```bash
python3 skills/senmu-build-delivery/scripts/inspect_git_workspace.py \
  --repo <repo> --target <integration-branch> \
  --intent <read|write|parallel-write|release-closeout> --compact
```

`write` uses the matching unit branch: resume the same owner or create new. Use `--exclusive-writer` in the current directory only when project/Harness guarantees exclusivity for the whole window; it never permits integration-line edits and “no writer observed” is not a guarantee.

When the project lacks a write entrypoint, first source write uses:

```bash
python3 skills/senmu-build-delivery/scripts/manage_change_unit.py prepare \
  --repo <repo> --target <integration-branch> \
  --unit <stable-task-or-change-unit-id> --slug <short-scope> \
  --worktree <new-isolated-path>

python3 skills/senmu-build-delivery/scripts/manage_change_unit.py verify \
  --repo <returned-worktree> --unit <same-id>
```

`prepare` branches/worktrees from a frozen commit and records identity in the Git common dir; mismatched, foreign, or sealed records fail closed. It does not replace Durable Task State.

Reuse frozen facts within a task and re-inspect only on HEAD, tree, surface, or release-scope change. Complex Git advice states facts, blind spots, rationale, exceptions, and closeout. Diagnosis does not authorize deletion or a new ledger. Engineering owns routine local commits.

## 2. Branches and Commits

One independent Change Unit uses one short branch; it belongs to the unit, not a session/item. Continue the same open batch and use checkpoint commits. Create new only when sealed, boundaries differ, or work is independently deliverable. Add worktrees for unknown/real concurrency. Without policy use `main + codex/<scope>/<topic>`; add `next/*` or `release/*` only for long-lived replacement lines or independent candidate roots. Never edit integration directly.

- Inspect branch, short status, recent commits first.
- Preserve merge strategy; explain divergence/conflict instead of forcing.
- Repair authority excludes merge, Tag, push, release.
- User-visible behavior must trace to approved prior behavior, current Product decision, and candidate reality. PRD/code/tests agreeing on one branch does not self-authorize change.
- The implementer develops/checkpoints during an open batch, freezes and verifies on test/closeout request, and the agent receiving explicit release intent closes that release. No permanent agent role.

The project declares `main_mode` in policy/branch authority:

- `release_ready`: only complete, verified, accepted units enter main; it always supports candidate formation.
- `integration`: complete accepted slices may enter main, while production identity comes from frozen candidate/artifact/release facts. Incomplete work still cannot enter.

Without declaration, BuildOS may advise once but cannot auto-integrate until the owner records it. Names do not substitute for semantics.

### 2.1 Version-Line Topology

- Integration lines are registered `current_line`, `successor_line`, necessary `maint/*`, or the one `release_source_root` for a release window.
- Task branches start from frozen target-line commits and return to the same line. Later tasks start from the integrated line, not the preceding task branch.
- Use a stacked unit only for a genuine dependency on an unintegrated parent; record parent ID, require parent sealed, and state integration order.
- Successive additions within one target/acceptance/release/rollback boundary keep the unit `in_progress`; do not seal, integrate, run full gates, or add worktrees after every clarification/fix.

`prepare` treats `--target` as integration line and fails if it is owned by another unit. Use `--target-role stacked-unit --parent-unit <id>` for dependency or `--target-role frozen-commit` for an exact baseline.

Cross-session continuation passes the stable ID:

```bash
python3 skills/senmu-build-delivery/scripts/manage_change_unit.py resume \
  --repo <repo> --unit <same-id>
```

`resume` creates no branch and stops on missing registration, sealed state, or surface conflict. A new run/attempt does not create a Change Unit automatically.

## 3. Worktrees and Parallel Surfaces

| Situation | Default |
| --- | --- |
| Read-only analysis/monitoring | Current authority directory; no branch |
| Default Codex write; future sessions possible | Short branch + worktree for each new unit; reuse registered surface for same open unit |
| Guaranteed exclusive clean window | Task branch in current directory; no extra worktree |
| Several sessions/agents | Branch + worktree per writing unit |
| Unknown/foreign dirty changes | Preserve; move to clean worktree or return unclear baseline to owner |
| Shared DB/generated path/port/production object | Serialize, lock, or pause conflict; Git cannot isolate it |

Projects may serialize when worktrees are prohibited/costly, baseline is unclear, or another state owner would result. Only verifiable exclusivity permits current-directory reuse.

Record purpose, baseline, integration target, shared resources, and exit. Business ledgers, databases, POC state, media, and receipts remain with their unique owners and are not copied with source worktrees. Stop if authority root is unclear or two active owners appear.

One writer owns one open unit; a single writer may accept same-batch additions, while multiple writers isolate. On test/handoff, freeze, verify, commit, then:

```bash
python3 skills/senmu-build-delivery/scripts/manage_change_unit.py seal \
  --repo <worktree> --unit <same-id>
```

`seal` requires a clean tree and a post-baseline commit and permanently closes branch recovery. A later repair is a new unit.

Later agents inspect intake without chat:

```bash
python3 skills/senmu-build-delivery/scripts/manage_change_unit.py list --repo <repo>
```

It derives `pending_integration` for sealed units not reachable from target and `integrated` when reachable. For squash/rebase/cherry-pick or exclusion/supersession, first record disposition in task authority, then `close --disposition <integrated|excluded|superseded> --owner-ref <owner#section>`; `integrated` also requires `--integration-commit`. This receipt mirrors owner decisions and commit mapping; it is not task state.

Never auto-stash/reset/commit mixed dirty changes. After integration and target verification, inspect uncommitted/untracked/ignored assets, processes, and unique commits. With no unique fact and proper authority, remove the explicit worktree then `git branch -d`; remote deletion is separate. Never default to `-D`, `--force`, or raw directory deletion.

## 4. Hotfix and Successor Line

Before hotfix, confirm production/release baseline, current version, rollback, unreleased work, and candidate version. Reproduce and run matching regressions. Propagate high-risk shared causes immediately; ordinary fixes at checkpoints; all applicable low-risk items by RC freeze/successor promotion.

Propagation is a registered fact/checkpoint, not interruption of another agent. A successor line is a future replacement, not a second project; it shares governance, state owners, and release entrypoint, absorbs applicable maintenance fixes, and after promotion leaves one current main plus old-line history/rollback evidence.

## 5. Integration and Review

- Freeze base/head, unit, requirement/defect scope, and full diff.
- Inspect each substantive function, interface, state, effect, error, comment, and matching test.
- Run only risk/stack-relevant gates, not universal checklists.
- Do not integrate with failed Hard Gates/quality commands or open blocking Findings.
- Review approval binds the frozen head; a new commit requires candidate re-review. Continued task or release authority is decided by the [Authorization Protocol](release-authorization-and-production-truth.md#3-authorization-boundary).
- Self-review does not replace required separation, but low risk does not require independent review.
- Review belongs to the frozen set, not a permanent agent. The integration/release closer may self-review low risk; use independence only by hard gate/risk.

## 6. Release Source and Parallel Exclusions

Build formal candidates from one `release_source_root`. Block only unapproved reachable changes, included-but-unclosed facts, shared production conflicts, or release scripts reading other worktree/POC roots.

Interpret “release latest/everything just fixed” as release closeout, not merge every branch:

1. Freeze intake; reconcile current-version PRD/equivalent commitments with tasks, worktrees, branches, dirty changes, and registered scope.
2. Each in-version item has evidence or an explicit defer/cancel/remove decision. Required analyzed/in-progress/unverified items block; finish when already approved and scoped, asking only if inclusion cannot be determined.
3. Include only unit-owned, complete, verified stable commits in dependency order. Exclude merged history, POCs, incomplete/unclear/unrelated branches.
4. Return unknown dirt to its owner or explicitly exclude it; the releaser does not guess/package it.
5. Review/integrate/conflict-test/preflight/freeze in the sole clean source. Continue to Tag/artifact/deploy only under release authority.

Instantiate `RELEASE_CONTROL.template.json` or equivalent for scope, intake matrix, gates, evidence, and recovery, closing `scope_accounted -> integration_complete -> candidate_verified -> release_authorized -> release_verified -> git_execution_closed` and validating:

```bash
python3 skills/senmu-build-delivery/scripts/validate_release_control.py <release-control.json>
```

Release Control owns what to check/current progress/recovery; Release Record owns actual external actions. Do not repeat full gates at intermediate checkpoints. Reuse unchanged candidate evidence; after change rerun affected checks and any entrypoint-required gate.

### Standard Release Fast Path

A standard release entrypoint is one project-owned executable command/workflow accepting frozen commit, version/change summary, one full preflight, immutable artifact, deployment precheck/action, production identity/health, and Release Record. It loads configuration from the environment owner, supports idempotent retry or receipt-based resume, and emits machine-readable stage state. Markdown sequences, scattered scripts, or the phrase “one entrypoint” are insufficient.

With one unit/target/entrypoint:

1. Read project `AGENTS.md`, release owner, compact unit/branch closure index, and Git. Do not load Assurance or broadly search memory/logs/sessions.
2. Integrate sealed units with commit-bound tests and run only conflict-impact checks; do not replay each team's specialist tests.
3. After version/changelog/candidate commit, invoke full preflight once; do not manually repeat its subchecks.
4. Build the frozen artifact once, deploy, then verify identity, health, and affected core flow—not every page.
5. Rerun only for candidate-code changes, behavior-changing conflict resolutions, or gate-fix changes. Appending release records does not invalidate tests.

Without that top-level driver, the project has release scripts, not a standard pipeline. An emergency release uses existing safe entrypoints and one necessary gate; register the driver as automation debt afterward.

A dirty legacy shared main has no fast path. Do only minimum recovery needed to attribute scope, form one recovery/consolidation commit, then freeze and preflight once. Do not replay all historical tests and then duplicate the same preflight. Record this as unsealed-session recovery cost.

Isolated candidate-unreachable POCs/branches/worktrees that do not write shared production resources do not block release or require pause/commit/cleanup/integration. Record `branch@HEAD` as exclusion evidence without interrupting them.

Closeout records authority root, integration commit, source, delivery path, rollback, parallel exclusions, and temporary-surface disposition. Facts only in temporary directories, or two “current/formal” directories, mean incomplete closure.

### 6.1 Release Train and Cutoff

One release has one mutable integration root. If `release/*` worktree is used, candidate fixes return there and preflight reruns; do not also advance `main`. If `main` is the root, create no second candidate branch.

- Cutoff snapshots accepted units, not future branch prohibition. Later candidate-unreachable/no-shared-resource tasks are automatically excluded; record `branch@HEAD` without candidate commits.
- Version/changelog/candidate state may be mutable release-train preparation before full preflight; only a passing head freezes.
- Fix preflight failures in the same root, invalidating the old candidate; rerun affected checks and full preflight before freezing.
- Before candidate/artifact, run `verify_release_identity.py` to establish `reviewed_commit = tested_commit = release_source_head = artifact_source_commit`. A formal Tag is not candidate input. After target verification, the promotion entrypoint verifies the exact commit receipt before creating/pushing the Tag.
