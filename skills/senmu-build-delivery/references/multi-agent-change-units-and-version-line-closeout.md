# Multi-Agent Change Units and Version-Line Integration

Use this standard for AI development with no permanent team lead, unknown concurrency, and continuous requests across one or several version lines. Responsibility follows the current action and durable evidence, not session identity: the implementer writes a Change Unit; the agent receiving integration/release intent closes integration; the agent executing merge gates reviews. Any later agent must recover the same truth from project task authority and Git.

## 1. Change Unit Contract

Acceptance, release/rollback boundary, and write ownership define a Change Unit—not message count. An independently deliverable bug, feature slice, or migration step may be one unit. One writer may keep a shared-acceptance/release/rollback batch `in_progress`. One release may include several parallel units.

At closeout, record target release unit/line, task/requirement ID, baseline commit; branch/worktree, sealed commit, actual scope/paths; matching tests/results, omissions, dependencies, conflicts, residual risk; and `in_progress | sealed | integrated | excluded | superseded`.

An in-progress handoff needs stable Change Unit ID, next action, and current authority. The successor uses `manage_change_unit.py resume`; it does not reconstruct a branch from prose.

`sealed` requires completed scope, verification to the stated limit, local commit, and no unit-owned uncommitted source. Dirty work is `in_progress`; releasers never guess it complete, commit unknown files, or include them. Write to an existing Durable Task State Owner rather than adding a ledger. Without a task system, short branch, commit, and concise handoff are the minimum fact chain.

Sealing closes that branch's write window. An open batch accepting requests remains `in_progress`; do not seal after one item. A later repair becomes a new Change Unit explicitly linked to the corrected head.

## 2. Select an Execution Surface

Codex projects are `parallel-capable`: future sessions may begin at any time, so absence of observed writers is not an exclusivity guarantee. Reuse the registered branch/surface for an existing open unit. Otherwise create a task branch, and add a worktree unless the entire modification window has guaranteed exclusive writing.

| Situation | Copy/small fix | Ordinary bug/feature | Large POC/long change |
| --- | --- | --- | --- |
| Default Codex, future writers unknown | Short branch + worktree | Short branch + worktree | POC/successor line + worktree |
| Harness guarantees exclusive window and clean tree | Current-directory task branch | Current-directory task branch | Short/special line worktree |
| Other writer exists or main has foreign/unknown changes | Short branch + worktree | Short branch + worktree | POC/successor line + worktree |
| Shared DB/generated dir/production resource cannot isolate | Serialize/lock | Serialize/lock | Phase work; Git cannot isolate resources |

Integration lines are not editing areas. Exclusivity permits a task branch in the current directory, never direct main edits. The first independent source write—even punctuation—uses a task branch; additions to one open unit reuse it. Unknown/real concurrency adds a worktree. Branches isolate history; worktrees isolate physical writes; concurrent writers need both.

Obtain passing project write-preflight evidence before the first edit, using an equivalent entrypoint or `manage_change_unit.py prepare`/`verify`. Stop if directory differs from registered worktree, branch has unregistered history, unit identity differs, or state is sealed. Do not edit first and ask integration to repair ownership later.

A POC proves a hypothesis and is not a product candidate by default. After acceptance, reconstruct or curate product changes into a Change Unit targeting the intended line. Do not dump experiment scaffolding, temporary data, or unapproved behavior into a formal line.

### 2.1 Dynamic Grouping, Routing, and Convergence

Route each arriving request to an existing `target line + release unit + open Change Unit` when acceptance and release/rollback boundaries match. Split only for changed boundaries or real parallelism; the final number of groups need not be known.

1. For a new session, classify current line, successor line, independent POC, or read-only analysis; find a matching open unit. New independent writes branch/worktree from the registered line baseline, never another group's directory.
2. Several groups may serve `current_line`; each seals independently and enters the next intake window by dependency. A long `successor_line` continues while maintenance fixes arrive.
3. Every current-line fix records successor applicability as `not_applicable | queued | integrated | verified | superseded`. This is propagation duty, not a requirement to pause or blindly merge the whole maintenance branch.
4. At successor release cutoff, collect every applicable sealed maintenance unit. Forward-integrate missing units, prove supersession, and block required units still in progress. Create the successor candidate only after closure.
5. After production verification, close temporary groups/branches/worktrees only when they contain no unique facts. Preserve commits, Tags, Release Records, and rollback history. Mark the old line EOL/history; do not erase it.
6. If one task remains one user result and rollback unit, update scope/risk/tests in the unit. If it becomes independently releasable or an experiment, split into dependent units or a POC.
7. When shared DBs, generated paths, ports, or production resources conflict, source branches may continue but conflicting steps serialize, lock, or use sandboxes. Git is not resource isolation.

New units start from the registered integration line, not the preceding task branch. Integrate a prerequisite sealed unit first, then branch from the new line head. Use an explicit stacked unit only for a genuinely inseparable dependency, recording parent, baseline, and integration order.

If a current-directory task later meets a second writer, stop sharing. Seal a complete attributable change after verification, or transfer an attributable patch to a worktree. Never automatically stash, reset, or commit mixed dirty work; if it cannot be separated, mark blocked and reconcile ownership once.

## 3. Integration Without a Permanent Leader

An implementer may end after commit, verification, and seal. Sealed units without final disposition remain visible for intake. The agent receiving “finish this batch,” “integrate into current version,” “merge this work,” or “release latest” becomes the integration closer.

Ordinary single-project/single-source work adds no coordinator. Only a formal release crossing agents, repositories, or production units creates a temporary release coordinator for that window. Release Control freezes the intake matrix/candidate and binds authority to candidate, scope, environment, and rollback. Unchanged boundaries need no repeat confirmation. New commits require refreshed candidate evidence; the [authorization protocol](release-authorization-and-production-truth.md) determines whether the existing scope still covers execution. Effects outside that authority require confirmation. The temporary role ends on release, rollback, or cancellation and creates no second ledger.

1. Freeze intake cutoff and target line. Reconcile version requirements/defects, task owner, Harness-visible tasks, Git branches/worktrees/status/log, and branch register into one intake matrix. Include sealed units before cutoff; exclude continuing units unless required, in which case block. Never force partial commits for schedule.
2. Mark each `include | exclude | blocked`. Include only line-matching sealed units with stable commit, evidence, and traceable scope. Exclude history, POCs, incomplete, superseded, unrelated. Block possibly in-scope dirty, unproven, or unresolved-conflict units.
3. Integrate by shared foundations, dependencies, and conflicts—not session finish order. Preserve project merge/rebase/cherry-pick policy; otherwise retain traceable ancestry. An equivalent rewrite records source mapping.
4. Review each frozen `base..head`: actual diff, user behavior, interfaces/data/effects, comments, tests. Low risk may use evidence-based self-review; use independent review only when project rules or G3-G4 require it.
5. After each integration, run conflict-impact tests. After all inclusion, run full candidate gates in the one clean `release_source_root`. A new commit invalidates old review/candidate; review new diff and affected chains.
6. Release Control records `version item/task -> source commit -> tests -> disposition -> integration commit`. Every version item and plausible unit needs disposition; zero local branches does not prove closure.

Once integration begins, select one mutable `release_source_root`: either the target line or a temporary release train, never both. Unrelated branches after cutoff do not invalidate or require exclusion commits. Reopen only for release-root content, frozen scope, or shared production-resource change.

Prevent omissions through three-way reconciliation: version/task commitments, Git facts, and candidate diff. Stop on any mismatch; merging all branches is not completeness.

## 4. Current and Successor Lines

When production continues on one line while a confirmed replacement develops, define roles:

- `current_line`: production/maintenance line; hotfixes start from a controlled production Tag/commit and enter it after verification.
- `successor_line`: confirmed future replacement; successor features enter only this line, never flow backward.

Every current hotfix gets successor status `not_applicable | queued | integrated | verified | superseded`. Propagate security, authorization, data, payment, and shared-contract fixes immediately; ordinary fixes at registered checkpoints. Before successor freeze, all applicable fixes are `verified` or have supersession evidence. Never blind-merge current at the end or interrupt every successor slice for a low-risk fix.

Before promotion, freeze both lines and reconcile applicable hotfixes, migration/compatibility, full tests, version/artifact, and rollback. After verified successor production truth, promote it to sole current main; mark old line EOL/read-only history with immutable Tags, necessary branch, and rollback evidence. Never delete history or merge new main backward.

Roles do not follow version numbers. Use any SemVer, CalVer, build, channel, or nonnumeric branch. Establish `successor_line` only when the version owner declares replacement; the next patch remains current.

## 5. Invariants

- Sessions may be random; open-unit recovery IDs, Release Control, frozen candidates, and Release Records must survive chat.
- The project declares main as `integration` or `release_ready`. Without it, do not auto-integrate. No mode permits unfinished work or unapproved product behavior on main.
- Uncommitted code on main is unattributable risk, not fast delivery; before release, seal, return to owner, or exclude it.
- Merge, tests, Tag, deployment command, and production release are different evidence.
- Review occurs at integration without a permanent team lead; separate duties only by risk/project rule.
- Delete temporary branches/worktrees after release only when no unique facts remain and work is integrated or explicitly excluded with recovery reference.
