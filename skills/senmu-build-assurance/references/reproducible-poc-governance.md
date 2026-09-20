# Reproducible POC Governance

Use this standard when a prototype, model comparison, technology trial, performance test, algorithm tuning run, or experience comparison must support a decision. A POC must remain challengeable, reviewable, extendable, and reproducible instead of ending as a chat impression.

## 1. When It Applies

Use it when any of these is true:

- the POC affects technology, model, vendor, architecture, or production parameters;
- two or more alternatives need A/B, benchmark, or ablation comparison;
- outputs are large, costly, sensitive, or expected to be deleted;
- the conclusion includes subjective audio, visual, or interaction judgment;
- the run is long or dependency-heavy and may need reproduction;
- the project owner requests a durable ledger of reasoning, runs, and conclusions.

Match evidence depth to the decision and risk. Lightweight exploration may use one short report in an existing experiment/task owner instead of a fixed document kit; comparative claims still need recorded variables, inputs and evidence. Do not invent repeated runs or a statistical test for a simple connectivity demo. Paid use and production effects retain their applicable controls.

## 2. Gates and Guidance

### Hard Gates

- Final conclusions must not exist only in chat, a temporary README, or one agent's context.
- Before claiming A is better than B, record the shared baseline, planned variables, and accidental differences; disclose what could not be controlled fairly.
- Before deleting unique outputs, retain a stable ledger, structured manifest, and sufficient reproduction protocol.
- Preserve failed runs, warnings, and counterexamples. Correct through append/supersession, never silent historical edits.
- Pending human evaluation remains pending; engineering preference is not the owner's decision.
- POC conclusions are not production approval. Productization follows the applicable requirement, architecture, test and delivery controls; do not invent versions or deployments where none exist.
- Obtain cost and mutation authority before paid models, cloud resources, external recruiting, or irreversible writes. Approval of a design is not authority for unlimited reruns.
- For secrets, privacy, biometrics, or unlicensed material, record controlled locators and fingerprints rather than copying originals into a general ledger.
- Keep run assets under the registered `POC_ROOT` and stable records there or in the registered `split` record owner. Project authority is not the product's main worktree. Unregistered worktrees, clones, temporary folders and personal caches are execution surfaces only.
- Resolve one `POC_ROOT`, record owner, tracking/retention/backup policy, and validation entrypoint before stateful runs. First-time setup may establish these within existing setup/experiment authority; ask only for an unresolved choice that changes scope or authority. Unknown storage remains unconfigured, not permission to write into another task or invent a second root.
- Parallel POCs must not write active experiment state into release worktrees, iteration plans, formal business ledgers, or production state. If small records need Git, use a separate POC branch/repository until productization is approved.
- Validation must check physical ownership, not only internal consistency under arbitrary `--root`. POC closeout scans registered execution surfaces for unique facts; unrelated releases do not require an isolated running POC to stop or commit.
- Cross-task release/hotfix notices normally record facts and a suggested checkpoint only. Interrupt an isolated POC only on user instruction, a registered checkpoint, or evidenced risk to safety, data integrity, or shared production resources.

### Soft Gates

- For subjective comparisons, use random labels, fixed conditions, predefined dimensions, and blind evaluation.
- Let the runner emit manifests, timing, hashes, environment, and parameters.
- Prefer one question per experiment and one planned variable per ablation; open a child experiment when the question changes.
- Test important generalizations with a second input, device, or run.

### Storage Guidance

For frequent, model-heavy, or media POCs, prefer one project-level, Git-ignored POC root that physically groups plans, scripts, runs, evidence, and conclusions. Let retention class determine backups. Use split small-record/large-asset storage only when the owner explicitly requires Git-tracked evidence. Directory names remain project configuration, not universal Skill rules.

## 3. Project Storage Contract

Before the first stateful POC, register in the project AI entrypoint, governance config, or equivalent owner:

```yaml
project_authority_root: <owner-recognized project boundary>
poc_root: <single POC state root within that boundary>
tracking_mode: untracked | split
protected_roots: [<active development and release worktrees>]
retention_classes: [ephemeral, reproducible, retained]
backup_policy: <snapshot, backup, or no-backup policy by class>
validator: <project command that exits nonzero on failure>
```

`project_authority_root` may contain several repositories, release units, and one separate POC area; it is not a repository's main worktree. `protected_roots` records active development and release worktrees to avoid; legacy `release_source_roots` remains a release-only input, not proof that other active writers were considered. Persist relocatable location rules, not machine-specific absolute paths. Declaration alone does not prove writer, port, database or container isolation.

- `untracked`: all experiment facts live together under an ignored `POC_ROOT`. Verify non-tracking with `.gitignore` and `git ls-files`.
- `split`: track small ledgers, manifests, protocols, and necessary source only in a separate POC branch/repository or registered non-release owner; keep large files in the single ignored run root. Both sides share `experiment_id` and cross-reference paths, versions, and hashes.
- Use one project default; register justified exceptions within existing authority, not an unregistered third location.
- The POC root stays within project authority and outside concurrently developed/released worktrees. Registered POC-only worktrees or repositories may hold small records in `split` mode; unrelated or temporary execution surfaces and personal caches cannot become durable owners. A tracked experiment record may be promoted to the project decision owner after review without merging experimental runtime code.
- `untracked` does not mean disposable. `retained` requires verified external backup; `reproducible` requires recoverable inputs and protocol; `ephemeral` still requires a frozen conclusion and deletion record.

### Project Adoption and Checks

At initialization or the first governed POC, use the existing project experiment owner. Generated projects declare `poc_management` in `.senmu-buildos/config.json`; only projects using POCs need it. Its `contract_path` points to the existing register (README for a core project), not a second ledger. Paths in this object are relative to the configured project `workspace_root`, except `contract_path`, which is relative to the governance root.

For `owner_kind=project_policy`, calibrate `poc_root`, `tracking_mode`, `record_root` (required only for `split`), `protected_roots`, `retention_policy` and `backup_policy`, then mark `activation_status=active`. Null roots/unknown protection are drafts, not working defaults. Under `untracked`, `record_root=null` means records stay in `poc_root`; confirm ignored/non-tracked status and backup before relying on it. Under `split`, the record root and large-asset root must be distinct and outside protected worktrees. Never exclude the only copy of retained evidence merely because it is ignored.

An established equivalent can use `owner_kind=existing_contract`, `contract_path`, and `activation_status` without duplicating its storage policy in JSON. The project validator checks that this pointer is reachable and reports that its isolation/retention semantics need the existing owner's checks; it does not claim to validate an opaque external system. Existing histories are not migrated or overwritten merely to fill new fields.

Use the existing project validator for the declared path/tracking contract; it does not run experiments, evaluate scientific merit, verify backups or authorize cleanup. At adoption, follow the actual route from the AI entrypoint to the contract and one representative experiment/fixture. Correct missing or contradictory roots at their one owner. Ordinary runs then load just that contract and the selected experiment, not all past experiments.

## 4. Experiment Package

```text
<POC_ROOT>/EXP-0001-<slug>/
  EXPERIMENT.md              # decision, hypothesis, boundary, success
  PLAN.md                    # variables, samples, steps, reproduction
  RESULTS.md                 # appended runs, measurements, reviews, limits
  DECISION.md                # adopt, reject, continue, or defer
  experiment-manifest.json  # input, environment, run, output references
  scripts/                   # only necessary experiment code
  evidence/                  # small reviewable evidence
```

Use stable, non-reused project IDs; `EXP-<NNNN>-<slug>` is the bundled default, not a mandate to rename existing experiments. A compact report may combine the sections below and reference an existing manifest; do not create empty parallel files just to match the package layout. In `untracked`, records and run assets stay together. In `split`, an ignored run root such as `inputs/ engine/ models/ cache/ outputs/ reports/` may hold large inputs, models, databases, caches, and outputs, but it must cross-reference the small-record owner and cannot become the sole history. Active POCs do not enter product iteration state. Only approved productization creates a formal engineering slice in the target PRD/task owner.

### Promote a Conclusion

- Success: promote the conclusion into a requirement, technical design, ADR, or Workflow Contract.
- Failure: retain the question, evidence, and rejection reason.
- Insufficient evidence: state conditions for further work; do not present an interim observation as production fact.

Productization requires an explicit promotion contract: source experiment/conclusion, approved scope and non-goals, formal requirement/technical owners, current baseline, accepted/discarded POC changes, integration target, and verification/release boundaries. Continue the original task only when new authority and scope are clear; otherwise create a new durable task.

After promotion, directory, branch, task state, and purpose must agree. Whether to create a worktree still depends on concurrent writes, isolation, and closeout cost; if reusing the surface, formally rename or re-register it while preserving the frozen POC conclusion.

## 5. Registration Fields

Freeze at least:

1. `experiment_id`, owner, executor, date, status;
2. decision question, production baseline, falsifiable hypothesis, applicability;
3. success/failure criteria and machine/human measures;
4. samples, repetitions, variance/uncertainty handling, stopping rule, and disclosed evidence strength;
5. control, variant matrix, invariants, planned variables, known uncontrollables;
6. input source/version/hash, authority, privacy boundary;
7. code commit/diff, model ID/revision, dependencies, device, seed, timing definition;
8. authority/POC/release roots, tracking/retention, backup, deletion, scratch locations;
9. who may conclude and who may approve productization.

Record deviations from preregistration instead of rewriting them as planned. Keep concise, reviewable hypotheses, assumptions, evidence and decision rationale, not verbatim chats or hidden model reasoning. Record actual times and tested variants; mark proposed or untested alternatives explicitly.

### Baseline Checkpoints

Freeze per run or declared checkpoint, not forever. Queue ordinary upstream style, copy, or low-risk changes for the next checkpoint. Interrupt only when instruction or a registered trigger shows impact on safety, data integrity, a core contract, or comparability.

When updating, preserve the previous identity and record new commit/version, trigger, affected variables, and evidence to rerun. Never silently rebase or overwrite old results into appearing comparable.

## 6. Append Each Run

Record run/parent IDs, times, executor, command/exit; motivation and prior issue; sole planned variable and accidental differences; input/prompt/parameters/code/model/dependencies/device; raw measures, output format/duration/hash, warnings, failures, and checks; separate machine observation, executor interpretation, and owner evaluation; next hypothesis or stopping reason.

Failed runs are evidence. Correct bad data by retaining old/new values, reason, and date or by appending a run. Do not stop early on favorable results, retain only best samples, switch primary metrics afterward, or delete unfavorable variants. Mark new exploratory hypotheses `post hoc` and validate them with a new experiment or independent data before formal use.

## 7. Human Blind Evaluation

Record randomized candidate IDs, dimensions, scale, reviewer, date, device/environment, timecode or steps, raw comments, and overall choice. Evaluate before revealing identities. Performance measures do not replace quality preference; preference cannot bypass safety, semantic integrity, error, cost, or compatibility gates.

### Agent, Prompt, Skill, Hook, or Plugin Comparisons

- Use isolated configuration roots and clean sessions; isolate global `AGENTS.md`, personal skills, plugins, hooks, caches, summaries, and undeclared environment variables.
- Before scoring, probe what each group actually loaded and whether event output/behavior differs. Invalidate and rerun contaminated results.
- Freeze exact model version, reasoning settings, harness version, tool permissions, code baseline, task order, and repetitions.
- Evaluate semantic correctness, risk boundaries, and implementation cost together. Less code is not better if contracts, validation, or safety fail.
- Prefer actual diffs, files, dependencies, executable tests, and observable results. Agent explanations, savings claims, and response length are not artifact evidence.
- General benchmarks apply only to their frozen conditions. Without a comparable project control, do not claim project-specific line, dependency, or token savings.

If a prompt principle behaves differently across model families, state the applicability boundary; do not keep changing wording until only favorable samples remain.

## 8. Conclusion States

```text
planned -> running -> pending_human_evaluation -> concluded -> archived
          |          \-> blocked
          |          \-> invalidated
          \-> cancelled
concluded -> superseded
```

Mark interim conclusions `interim` with evidence and unknowns. Final conclusions record each considered alternative, tested/untested status, selection/rejection or deferral, supporting run/evidence IDs, rationale, scope, uncertainty, signer, and date. State why the plan changed and what future evidence, price, interface or version change would justify reopening the decision. Supersede rather than rewrite conclusions overturned by new evidence. State whether generalization across data, hardware, versions, or users was retested. `invalidated` means design, contamination, or missing critical evidence made a run unusable; it is not a falsified hypothesis and remains in the ledger.

## 9. Deletion and Reproduction

Before deleting large outputs, verify recoverable versioned/hashed inputs; repository commit and patches; model/dependency identities; source or full protocol for custom algorithms, prompts, segmentation, post-processing, and validation; explicit commands without remembered steps; stable summaries, output hashes, failures, and human reviews; disclosed limits from randomness, drivers, hardware, or upstream deletion; and a deletion record with time, scope, recoverability, and executor.

Retain the smallest evidence set that still supports the conclusion: plan, relevant experiment code/patches, versioned parameters, run measurements and failures, decision rationale, and representative media or counterexamples when the judgement depends on them. A modified engine is not merely a redownloadable dependency. Non-deterministic or unavailable outputs essential to the decision require retention or an explicit reduction of the reproducibility claim; a hash or download URL alone is insufficient.

Classify bulk groups (models/engines, environments, cache, generated outputs) by ownership, regeneration and retention, not age or size alone. Shared caches, active processes, credentials, volumes and unique data remain protected. Record disposal in the existing experiment manifest/decision: planned scope, retained evidence, recovery source, authority, actual result/date and remaining action. Follow Workflow's ordinary-file recovery rules and Delivery's native resource rules; no experiment tool silently acquires deletion authority. Conclusion status and resource-closeout status are separate: a rejected or inconclusive experiment may be archived with evidence, while cleanup may still be pending. Non-release experiments close on their own lifecycle, not the next production release.

Before retiring execution surfaces, preserve records in the registered record owner and assets in `POC_ROOT`, reconcile inventories/hashes, validate their locations, and confirm no unique experiment files remain on the retiring surface. Scratch space may hold declared downloads, extraction, or intermediates only; migrate, delete per policy, or register retention before closeout. Under `untracked`, verify backup/reproducibility by retention class; Git history is not recovery.

A hash without a retrievable source is not reproducible; an environment name without exact versions is not comparable; a success screenshot without raw measures cannot support the conclusion.

## 10. Record Boundaries

- Experiment ledger: hypotheses, variables, runs, observations, evaluations, conclusions.
- Work log: collaboration changes, verification, remaining risk.
- ADR/technical design: approved system decision.
- Changelog: changes actually released.
- Business ledger: formal business facts only, not POC state by default.

If productization is chosen, translate approved conclusions into formal requirements, design, tests, and release records. Production must not depend indefinitely on the POC ledger as its operating procedure.

## 11. Templates

Use `assets/poc-experiment-governance/` or the project's equivalent, not a parallel ledger. New manifests add project/evidence/closeout locators; legacy `external_workspace` is only an execution locator. Preserve old manifests and `evaluating` records as history; new pending human review uses `pending_human_evaluation`.
