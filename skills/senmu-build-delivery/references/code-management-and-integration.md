# Code Management and Integration

Use for non-routine Git, parallel work, integration and version lines. Project branching policy prevails. Local Git needs no remote; remotes, PR/MR, CI and platform Releases apply only when present and authorized.

## Contents

- [Scope](#1-establish-the-scene) · [Branches](#2-branches-and-commits) · [Worktrees](#3-worktrees-and-parallel-surfaces)
- [Hotfixes](#4-hotfix-and-successor-line) · [Review](#5-integration-and-review) · [Release](#6-release-source-and-parallel-exclusions) · [Retirement](#7-local-worktree-retirement)

## 1. Establish the Scene

Read-only identify the authority root, Git state, target line, batch, release unit, writers, shared resources and permissions. Choose line/surface/phase by version placement, Change Unit, writer/worktree and delivery intent, not agent count.

Proceed from available owners, tasks and Git. Ask only about unresolved version placement, cutoff, cost, data safety or production outcomes, in product language—not Git mechanics.

Defaults:

- Continue one `in_progress` unit for successive requirements in the same open batch with shared acceptance/release/rollback. One item is not batch completion.
- Without test/closeout intent, remain in development; without release intent, remain unreleased. Implementation does not authorize seal, integration, full candidate gates, or release.
- “Send for testing/review” fixes a review commit while the batch stays open. “Close this batch/prepare release” requests completed-scope closeout, not immediate sealing before repairs. Neither grants production authority. “Integrate into current version” permits integration only; “release/go live” opens a bounded session for an exact candidate.
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

`prepare` records the frozen baseline in the Git common dir. Lifecycle commands share identity and ancestry checks, not task or acceptance state.

Reuse unchanged source facts; reassess HEAD/tree/surface/scope changes. Diagnosis grants no deletion or new ledger; Engineering owns routine commits.

## 2. Branches and Commits

A short branch belongs to its Change Unit, not a session/item. Checkpoint within the open batch; new-unit conditions are in section 1. Unknown/real concurrency adds worktrees. Without policy use `main + codex/<scope>/<topic>`; reserve `next/*` or `release/*` for long-lived replacement lines or independent candidate roots. Never edit integration directly.

- Inspect branch, short status, recent commits first.
- Preserve merge strategy; explain divergence/conflict instead of forcing.
- When receiving changes to AGENTS, overrides or referenced policies, compare them with the receiving baseline and preserve current instruction ownership. Reconcile stale rules through Project only where needed; an ordinary code merge does not trigger a full Markdown audit.
- Repair authority excludes merge, Tag, push, release.
- User-visible behavior must trace to approved prior behavior, current Product decision, and candidate reality. PRD/code/tests agreeing on one branch does not self-authorize change.

The project declares `main_mode` in policy/branch authority:

- `release_ready`: only complete, verified, accepted units enter main; it always supports candidate formation.
- `integration`: complete accepted slices may enter main, while production identity comes from frozen candidate/artifact/release facts. Incomplete work still cannot enter.

Without declaration, BuildOS may advise once but cannot auto-integrate until the owner records it. Names do not substitute for semantics.

### 2.1 Version-Line Topology

- Integration lines are registered `current_line`, `successor_line`, necessary `maint/*`, or the one `release_source_root` for a release window.
- Task branches start from frozen target-line commits and return to the same line. Later tasks start from the integrated line, not the preceding task branch.
- Use a stacked unit only for a genuine dependency on an unintegrated parent; record parent ID, require parent sealed, and state integration order.

`prepare` treats `--target` as integration line and fails if it is owned by another unit. Use `--target-role stacked-unit --parent-unit <id>` for dependency or `--target-role frozen-commit` for an exact baseline.

For a known unit, `manage_change_unit.py inspect --repo <repo> --unit <same-id>` reads its registered path/head/state without restoring it. Missing paths do not prove deleted commits. Authorized continuation:

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

Record purpose, baseline, target, shared resources and exit. Keep business ledgers, databases, POC state, media and receipts at their unique owners, not copied into worktrees. Stop on an unclear authority root or competing active owners.

One writer owns an open unit. Use `manage_change_unit.py review --repo <registered-worktree> --unit <same-id>` to capture a fixed review commit; optional `--since <previous-review-commit>` reports a repair delta. It does not seal, approve or run tests.

Seal only after authorized batch scope, checks and required review/repairs are complete and the tree is clean:

```bash
python3 skills/senmu-build-delivery/scripts/manage_change_unit.py seal \
  --repo <worktree> --unit <same-id>
```

`seal` checks a clean tree and a post-baseline commit and permanently closes branch recovery. These Git checks do not prove scope completion or business acceptance. A later repair uses a linked unit; do not seal merely to request review.

```bash
python3 skills/senmu-build-delivery/scripts/manage_change_unit.py list --repo <repo>
# Bounded v2: --state all, --offset N. Legacy JSON: --format full.
```

Full output retains v1: sealed units are `pending_integration`; `candidate_reachable` only hints at ancestry. After authorized reception, record the disposition with `close --disposition <integrated|excluded|superseded> --owner-ref <owner#section>`. Integrated closeout requires `--integration-commit <receipt>` on the registered target and an unchanged sealed source.

`close` verifies either the exact sealed commit or the full frozen delta replayed onto the receiving base, comparing the entire resulting Git tree. Rewritten history defaults to the receipt's first parent; pass `--integration-base <target-before-reception>` for a multi-commit rebase/cherry-pick range. Clean ordinary merges, squash and exact-content rewrites are supported. Unrelated, partial or extra receipt changes fail. Conflicts, missing Git merge-tree capability or unproven semantic rewrites remain sealed; review a target-specific candidate rather than asserting equivalence.

Replay may write Git objects, not branches, index or working files. The existing record stores `integration_proof`; legacy receipts gain no proof automatically. This proves reception at that commit, not current behavior, review, acceptance or release. Existing task authority and target verification remain necessary.

Never auto-stash/reset/commit mixed dirt. After integration and target verification, use [Local Worktree Retirement](#7-local-worktree-retirement); preserve unique material and active work, and never default to force removal. Remote deletion remains separate.

## 4. Hotfix and Successor Line

Before a hotfix, confirm production baseline, current/candidate versions, rollback and unreleased work; reproduce and test. Propagate shared high-risk fixes immediately, ordinary fixes at checkpoints and all applicable low-risk fixes by RC freeze/successor promotion.

Register propagation without interrupting other agents. A successor replaces the current line, not the project: share governance, state owners and release entrypoint, absorb applicable fixes, then retain one current main and old history/rollback evidence.

## 5. Integration and Review

- Freeze base/head, unit, requirement/defect scope, and full diff.
- Inspect each substantive function, interface, state, effect, error, comment, and matching test.
- Run only risk/stack-relevant gates, not universal checklists.
- Do not integrate with failed Hard Gates/quality commands or open blocking Findings.
- Review approval binds the frozen head; a new commit requires candidate re-review. Continued task or release authority is decided by the [Authorization Protocol](release-authorization-and-production-truth.md#3-authorization-boundary).
- Review belongs to the frozen set, not a permanent role. The integration/release closer may self-review low risk; required separation and risk/hard-gate independence still apply.

### Review Identity at the Project Gate

Engineering determines needed review separation from actual risk, duties and project policy. Delivery enforces that requirement for the frozen candidate; risk level alone is not a universal reviewer assignment. Keep routine checks in their domain. Use the structured review validator only when the project adopts that merge-record format, not on every edit.

An adopted merge entrypoint passes its required identity with `--required-review self`, `--required-review peer` or `--required-review independent`. `self` permits evidence-based self-review or stronger separation; `peer` permits peer or independent review; `independent` permits only independent review. The existing record still identifies the actual author, reviewer and evidence. An exception inside the reviewed record cannot relax an explicit requirement. An explicit `--required-review` also requires `status=approved`; a draft or unfinished review cannot pass the merge gate.

```bash
python3 skills/senmu-build-delivery/scripts/validate_change_review.py \
  --record <review.json> --repo <repo> --require-current-head \
  --required-review <self|peer|independent>
```

Bind the argument in the trusted project merge/CI entrypoint from the approved policy, not from candidate-controlled data or an implementer's ad hoc choice. Review policy changes against the receiving baseline. Mandatory safety or separation controls cannot be waived by changing the argument to obtain green. The validator checks declared evidence and identities; it cannot authenticate reviewers or prove their independence.

Omitting the argument validates structure, permits drafts, and preserves legacy identity checks on approved records: peer review, an owner-recorded self-review exception where allowed, and independent review for G4. Structure success is not merge readiness. This fallback protects existing installations; it is not a universal BuildOS task policy. Calibrate the existing project caller under governance authority to use the explicit mode. Do not automatically migrate project policies or weaken their gates on upgrade. Approval still rejects failed checks, stale heads and open/blocking findings.

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

Without this driver, scripts are not a standard pipeline. Emergency release uses existing safe entrypoints and one necessary gate; record the missing driver as automation debt.

A dirty legacy shared main has no fast path. Do only minimum recovery needed to attribute scope, form one recovery/consolidation commit, then freeze and preflight once. Do not replay all historical tests and then duplicate the same preflight. Record this as unsealed-session recovery cost.

Isolated candidate-unreachable POCs/branches/worktrees that do not write shared production resources do not block release or require pause/commit/cleanup/integration. Record `branch@HEAD` as exclusion evidence without interrupting them.

Closeout records root, integration commit, source, delivery, rollback, parallel exclusions and temporary-surface disposition. Temporary-only facts or two current/formal directories mean incomplete closure.

### 6.1 Release Train and Cutoff

One release has one mutable integration root. If a `release/*` worktree is used, integrate candidate repairs there, not also into `main`. If `main` is the root, create no second candidate root. For already-integrated defects, repair on a scoped task branch from the current release-root baseline, then integrate back. This is not a second candidate root or permission to edit integration or sealed lines.

- Cutoff snapshots accepted units, not future branch prohibition. Later candidate-unreachable/no-shared-resource tasks are automatically excluded; record `branch@HEAD` without candidate commits.
- Version/changelog/candidate state may be mutable release-train preparation before full preflight; only a passing head freezes.
- Fix preflight failures through the registered repair unit and integrate back into the sole release root; invalidate the old candidate and rerun affected checks and required preflight before freezing. Reuse scoped authority; ask only for uncovered effects.
- Before candidate/artifact, run `verify_release_identity.py` to establish `reviewed_commit = tested_commit = release_source_head = artifact_source_commit`. A formal Tag is not candidate input. After target verification, the promotion entrypoint verifies the exact commit receipt before creating/pushing the Tag.

## 7. Local Worktree Retirement

Retire only after integration or explicit exclusion/supersession with recovery evidence and covered authorization. Check tracked dirt, untracked/ignored files, nested repos, unique commits/materials and active writers/processes. Preserve needed review/repair/handoff resources first; clean Git alone is insufficient. Use `git worktree remove <registered-path>`, never directory deletion or `--force`. Retire branches through governed Git; squash ancestry alone is not disposal proof. Local retirement excludes remote deletion, history changes and release. Pending retention does not block unrelated delivery.
