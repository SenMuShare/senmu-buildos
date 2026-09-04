# Workflow Run State and Recovery

Use this protocol for multi-step, retryable, interruptible, cross-agent, or side-effecting workflows. It defines how one run is identified, recorded, verified, and recovered; it does not replace project task management, release ledgers, or conversation history.

## 1. Separate Three Facts

| Object | Question | Sole owner | Typical location |
| --- | --- | --- | --- |
| Workflow contract | How should this workflow operate over time? | definition, schema, config | `workflows/` |
| Run Manifest | What happened in this run and where is it now? | manifest/runtime database | `state/`, `data/`, existing system |
| Durable task state | Why, overall progress, next cross-stage action? | project-declared Durable Task State Owner | new-project default `governance/tasks/TASK-<NNNN>-<slug>.md`; established projects map existing owners |

A task may have several runs and a run several deliverables. Relate them through `task_id`, `run_id`, delivery IDs, and evidence links without copying content.

Code Change Units and Release Control are Delivery facts. Changing agents or rerunning a workflow does not change the code unit; formal release scope, gates, and Git closeout do not enter the Run Manifest.

## 2. Run Identity and Input Snapshot

Every recoverable run records:

- stable `workflow_id` and executed `workflow_version`;
- globally unique, immutable `run_id`; retry attempts are not new business runs;
- optional `task_id`, start time, executor, and actual public entrypoint;
- stable input IDs, versions, hashes, or unambiguous locators;
- configuration, code, model, tool, and environment versions that affect results;
- idempotency/deduplication rules, especially for payment, notification, release, upload, and database writes.

Chat descriptions are not input snapshots. Material input changes require a new run or explicit invalidation boundary; never rewrite old run facts silently.

## 3. State Model

| Run state | Meaning |
| --- | --- |
| `created` | identity exists; prerequisites incomplete |
| `ready` | inputs, permissions, prerequisites passed preflight |
| `running` | at least one step executes |
| `waiting` | awaiting an external system, async result, or human input |
| `paused` | intentionally stopped with a recovery entrypoint |
| `failed` | current attempt failed; error and recoverability recorded |
| `cancelled` | authorized termination; no automatic progress |
| `completed` | contract steps and run-level verification complete |
| `superseded` | another run replaced it as current |
| `archived` | read-only historical run |

Recommended step states: `pending`, `running`, `succeeded`, `failed`, `skipped`, `cancelled`. Each step stores attempt, input/output references, times, verification, and error receipt.

`completed` means run-contract completion only—not product acceptance, delivery, or release. Their owners record those facts.

## 4. Transitions

- Only the state owner advances state; logs, chat, and output folders cannot override it.
- Use public entrypoints, controlled commands, or transactions; do not bypass the owner by editing database/JSON state manually.
- After tool success, verify output identity, integrity, count, format, and business conditions before `succeeded`.
- Preserve partial success at step level. Do not mark the whole run successful or erase valid outputs.
- `waiting` is recoverable state, not perpetual polling. Only dependent steps wait; other ready steps continue. When all remaining work waits, store checkpoint, awaited event/result identity, timeout, and wake entrypoint, then release the worker. Prefer event wakeups; never poll without bounds.
- Around external side effects, record intent, authorization, idempotency key, and receipt. Mark uncertain outcomes for reconciliation; do not retry blindly.
- Write JSON state atomically or through an equivalent transaction.

## 5. Recovery Decision

Before recovery:

1. locate `run_id` in authoritative state and verify workflow version/input snapshot;
2. refresh external facts; distinguish submitted, completed, and verified;
3. inspect step evidence upstream to downstream and find the earliest invalid/unverified step;
4. decide reuse from input meaning, target version, real dependencies, and output result. A hash is an identity clue; it blocks reuse only when it carries product integrity/exact-revision semantics or reveals a material input change. Missing/stale administrative hashes, receipts, or progress records do not invalidate verified outputs;
5. record a recovery action, then execute through the public entrypoint.

Distinguish:

- **Resume:** continue the same run from a verified checkpoint.
- **Retry:** repeat a failed step in the same run with a new attempt and preserved idempotency.
- **Restart:** create a new run because input, rules, or environment make checkpoints untrusted.
- **Rollback:** reverse side effects or restore known-safe state; not a rerun.
- **Manual reconciliation:** stop automatic writes when external results cannot be determined.

Rerun minimally from the earliest genuinely invalid layer. Invalidate downstream outputs only when upstream meaning, target revision, or actual consumer dependency changed. Administrative changes alone must not rewind cursors, widen reruns, overwrite deliveries, or delete failure evidence.

If orchestration blocks solely on an administrative marker while an authorized controlled entrypoint exists for the target step, execute that step, verify output, continue, then repair or downgrade the bad gate. This exception never permits manual state edits or bypass of permissions, idempotency, safety, fees, irreversible side effects, or release authorization.

## 6. Minimum Run Manifest

The manifest or database must express:

- schema, workflow, run, task, current state;
- input snapshot, actual versions, environment;
- step states, attempts, inputs/outputs, verification, errors;
- current checkpoint, earliest invalid step, next recovery action;
- side effects with authorization/receipts;
- final outputs, evidence, delivery-state references, archive state.

Use the [Run Manifest template](../assets/workflow-governance/WORKFLOW_RUN_MANIFEST.template.json) to define a project schema. If an existing database/orchestrator owns all facts, register its table/object and query entrypoint; do not create a JSON copy.

## 7. Multi-Agent and Harness Boundary

- Harnesses own sessions, tool calls, compaction, and lifecycle events; project run facts remain recoverable without one session.
- Agent handoff carries `task_id`, `run_id`, current step, input/output references, failure evidence, authorization, and next action.
- System prompts define stable behavior, not cursors, current steps, or “already released” claims.
- Hooks recover a short governance baseline; they do not scan/inject full manifests, infer state, or advance runs.

## 8. Closeout

- Project entrypoints locate contract, state owner, current run, and recovery command.
- Run identity, input snapshot, and step evidence agree.
- Retries did not duplicate irreversible side effects; uncertain results remain pending reconciliation.
- Run completion, product acceptance, delivery, and release remain distinct.
- Superseded, failed, and cancelled runs remain auditable but never current.
