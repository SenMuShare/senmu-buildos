# Workflow, Material, and Deliverable Governance

Use this standard for automation, agent harnesses, media/content production, batch processing, and other projects combining code, state, and file delivery. It defines asset responsibility, recoverability, and delivery state without imposing directory names.

## 1. Asset Roles

| Role | Meaning | Default governance |
| --- | --- | --- |
| Source input | user material, original media, frozen copy, business parameters | retain source, authority, version, fingerprint; never overwrite during processing |
| Workspace | decomposition, transformation, human review | mutable; isolated from formal delivery |
| Temporary/cache | reproducible downloads, proxies, render cache | normally excluded from Git; dispose only under verified regeneration, retention and authority conditions |
| Run state | database, manifest, queue, cursor, machine task state | one writable authority with backup/migration rules |
| Deliverable | candidate or formal result for users/downstream systems | stable name, version/delivery ID, checksum; separate acceptance/release state |
| Evidence/receipt | parameters, source locators, checks, release/non-release facts | traceable to one run and deliverable |
| Archive | closed versions and historical deliveries | read-only/controlled recovery; never current state |

Projects may use Chinese or existing path names, but their README/AI entrypoint must map real paths to these roles.

Machine task state above means one workflow run's queue, cursor, manifest, or run state. Cross-stage progress belongs to the project's Durable Task State Owner. Relate them by task/run ID without merging their content.

## 2. Workflow and Harness Contract

A durable or repeatable workflow defines:

- one public entrypoint and input schema/configuration;
- `run_id` or equivalent and input version/hash;
- one writable state owner: database, manifest, ledger, or external system;
- each step's input, output, failure state, and retry boundary;
- resume, idempotency, or explicit restart rules;
- target acceptance, final delivery location, and run receipt;
- when legacy entrypoints, caches, and outputs become historical only.

The workflow contract stores durable rules, never a run cursor. Put attempts, checkpoints, errors, and recovery actions in a Run Manifest or existing system under [Workflow Run State and Recovery](workflow-run-state-and-recovery.md). Chat cannot be the sole state source; an agent must recover progress from project entrypoints, state, and receipts.

### 2.1 Human-Operator Guide

For login, secrets, codes, payment, approval, account ownership, or human-only irreversible judgment, compile a recoverable human-agent guide:

- The agent first performs authorized reading, preparation, validation, and no-side-effect work; it does not dump the full setup process on the user.
- Present only the current human step: where to open, field to identify, valid input boundary, expected result, return signal, and failure stop.
- Users enter secrets, passwords, cookies, codes, and payment data directly in trusted interfaces—not chat, logs, Git, screenshots, or client code. The agent checks redacted state and outcomes.
- Save verifiable checkpoints. On recovery, read actual state first; retries must be idempotent or disclose new side effects.
- Before deletion, payment, review submission, notification, production switch, or another irreversible action, verify that existing authority covers its object, content, impact, and scope. If it does, proceed through the authorized entrypoint; ask only for an uncovered decision after preparing a concrete result. Preparation alone is not execution authority; required host permissions and human-only steps still apply.
- Reuse an existing native guide, CLI, or platform process and fill only missing boundaries; do not create a second durable owner.

This section owns guide design, not routine execution. To follow an existing reliable setup once, use its project entrypoint. Load Workflow only to repair missing entrypoints, unrecoverable steps, unclear secret handling, or irreversible confirmation gaps.

## 3. Directory Mapping

Map roles rather than copying names:

```text
project-root/
  README.md / AGENTS.md       entrypoint and authority order
  scripts/ or src/            maintained code
  workflows/                  contracts, schemas, configuration
  sources/ or inputs/         original/frozen input
  work/ or staging/           current workspace
  data/ or state/             database, Run Manifest, cursors
  outputs/ or deliveries/     final deliverables
  evidence/ or receipts/      verification and receipts
  archive/                    historical versions and closed work
```

Small projects may combine directories, but source, intermediate, and final outputs must not overwrite one another. System temporary directories hold disposable data only; anything needed for handoff, review, or recovery returns to project authority.

## 4. Git and Large Files

- Git normally tracks code, configuration, schemas, workflow documents, small manifests, and necessary reproducible examples.
- Keep large media, runtime databases, caches, and reproducible intermediates in project-approved storage; retain indexes, manifests, hashes, or recovery instructions in Git.
- Decide final-deliverable tracking from size, privacy, license, recovery cost, and release method—not merely finality.
- `.gitignore` is not data governance. Ignored assets still require an authority, retention period, and recovery method.

## 5. POC, Production, and Delivery

POC output begins in experiment/staging. Promote it only after explicit quality, cost, license, and reproducibility conditions. Generation is not delivery; delivery is not release. Record generated result, acceptance, delivery location, and when applicable release state/receipt separately.

## 6. Closeout

- Project entrypoints recover current workflow, state owner, and progress.
- Sources, temporary content, and final deliveries are separated and never overwrite one another.
- Final material has delivery ID/version, provenance, verification, and separate acceptance/delivery/release references.
- Unreleased, unaccepted, failed, and interrupted states remain truthful.
- Disposable and archival material have explicit boundaries.

## 7. Authorized Local Cleanup

This section owns ordinary material cleanup. Existing safe project commands remain the first entrypoint; a one-off cleanup does not require workflow redesign. Names, age, size, ignored status and a successful plan confer no deletion authority. Preserve unknown ownership, active writes, source inputs, databases, accepted deliverables and review/recovery evidence. Recheck scope against existing user authorization; ask only when it is uncovered.

For authorized ordinary local files on macOS/Windows, use native Trash/Recycle Bin. Failure, missing backend, cancellation or uncertain recyclability never permits permanent deletion, elevation, clearing Trash or a handwritten recycle format. Permanent removal is limited to explicitly governed, reproducible disposable resources through their existing scoped native lifecycle entrypoint; test fixtures may use the test framework lifecycle. Git worktrees and container resources use Delivery's native operations, not the ordinary-file helper.

The bundled thin helper is `scripts/safe_local_cleanup.py` (relative to this skill). It has only `plan` and `trash`, no global scan or purge. It uses Python's standard library and macOS Foundation through system `osascript`; no application dependency or global installation. Windows and other unimplemented backends reject execution. Native OS recovery acceptance remains pending until an explicitly authorized dedicated-fixture test; isolated injected-backend tests do not prove native behavior.

```bash
python3 <workflow-skill>/scripts/safe_local_cleanup.py plan --root <absolute-project-root> --authorization <existing-task-or-decision-reference> <absolute-target> > <plan-outside-targets.json>
python3 <workflow-skill>/scripts/safe_local_cleanup.py trash --plan <plan-outside-targets.json> --writers-stopped
```

Before execution, the caller verifies ownership, Git tracked/untracked/ignored state, governed-resource exclusions, retention and stopped writers; `--writers-stopped` records that assertion, it does not detect processes or acquire a lock. A saved plan is not approval. Do not send worktrees, container/image storage, databases or other managed resources to this helper. Review its bounded metadata-only inventory and logical bytes; no file contents or Home scan. Incomplete inspection, inaccessible descendants, nested repositories/`.git` files or directories, links/reparse points, mount boundaries and overlapping targets reject the entire affected plan before any backend call. It never skips a protected child and then trashes its parent.

Revalidation checks observable root/target identity and descendant metadata before execution and each call. It cannot atomically exclude external concurrent writes; if writer exclusion cannot be established, retain the material. Native volume locality must be established before moving. Results distinguish `rejected_before_call`, `confirmed_retained`, `confirmed_trashed`, `unknown` and `not_called`. After a backend attempt, reconcile source and returned destination, including partial failures. Cancellation/error/unknown stops remaining items and dependent cleanup. Never report an all-or-nothing success or assume an exception means no move. Preserve receipts for inspection; do not automatically retry unknown items or restore over existing paths.

The native API returns the resulting Trash URL: [Apple Foundation trashItem](https://developer.apple.com/documentation/foundation/filemanager/trashitem(at:resultingitemurl:)). The helper uses no permanent-delete fallback.

## 8. Task Resource Closeout

At a meaningful task/stage closeout, group temporary resources in the existing Task/Run owner: location or native ID, purpose, responsible owner, and retention/cleanup condition. Do not create a parallel ledger or per-file inventory. Preserve resources needed for review, repair, handoff or recovery, including interrupted tasks. Dispose only when conditions and authority are satisfied; otherwise record retained/pending with the next action. Pending cleanup does not invalidate delivered business behavior.

Ordinary files follow §7; worktrees and build/container resources follow Delivery's Git and artifact owners. Non-release tasks follow their own lifecycle rather than waiting for a production release. Distinguish logical bytes moved to Trash from measured disk space reclaimed; native layers may share storage or retain recoverable data.


Only reconcile resources created by this task or explicitly brought into its scope; no Home sweep, recurring scan or empty cleanup report. Stop only an identified task-owned temporary process after its run, never name-match shared/user services. Preserve media revision windows and failed-run evidence until their conditions close. Disk exhaustion pauses only affected writes; continue independent safe work.
