# Workflow, Material, and Deliverable Governance

Use this standard for automation, agent harnesses, media/content production, batch processing, and other projects combining code, state, and file delivery. It defines asset responsibility, recoverability, and delivery state without imposing directory names.

## 1. Asset Roles

| Role | Meaning | Default governance |
| --- | --- | --- |
| Source input | user material, original media, frozen copy, business parameters | retain source, authority, version, fingerprint; never overwrite during processing |
| Workspace | decomposition, transformation, human review | mutable; isolated from formal delivery |
| Temporary/cache | reproducible downloads, proxies, render cache | excluded from Git by default; safely disposable |
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
- Before deletion, payment, review submission, notification, production switch, or another irreversible action, show object, impact, and final confirmation. Preparation is not execution authority.
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
