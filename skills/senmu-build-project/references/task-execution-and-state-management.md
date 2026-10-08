# Task Execution, Planning, and State Management

**Read as needed:** [Create a task](#2-when-to-create-a-numbered-task-plan) · [Split and delegate](#4-split-plans-only-as-much-as-needed) · [Resume](#5-session-plans-and-authoritative-facts) · [Update status](#6-status-and-update-points) · [Close](#7-closeout-and-archive).

Multi-step/session work uses a project-owned Durable Task State Owner, not chat or a specialist Skill. Standard/release starters use numbered plans; core and mature projects may retain a trusted README, issue tracker, database, plan or external system.

## 1. Default Location

```text
governance/tasks/
├── TASK_REGISTER.md
├── TASK-0001-<slug>.md
├── TASK-0002-<slug>.md
└── TASK-0003-<slug>.md
```

In software projects, `governance/` is at the Git root. In non-software or material-heavy projects, the same structure lives in the sole Git repository, `00-project-system/`; large inputs, intermediates, runtime databases, deliverables, and archives remain outside the project system.

`TASK_REGISTER.md` contains only the task index and current status. Each `TASK-<NNNN>-<slug>.md` is that task's durable plan and state record. Do not create a same-named directory or default Discussion, Decision, Research, Validation, or reviews child files for ordinary tasks.

## 2. When to Create a Numbered Task Plan

Create one when any condition applies:

- Work needs multiple substantive steps, phases, or checkpoints with durable progress tracking.
- Work is expected to cross sessions, context compaction, people, or agents.
- Scope, non-goals, authority, prohibited actions, or write boundaries must persist.
- Work includes several discussion rounds, requirement/technical review, a POC, staged implementation, or complex verification.
- The task is G3-G4, or failure affects release, production, authorization, data, payments, privacy, migration, rollback, or destructive risk.
- The user explicitly requests a trackable, recoverable project plan.

An immediate, reversible, single action that needs no durable tracking may omit one. If scope grows during execution, create the plan then with current facts and the next step; do not transcribe the full chat.

## 3. Responsibilities of the Plan

At minimum, record:

1. Task ID, name, status, owner, and update time.
2. Objective, completion definition, scope, non-goals, and affected release/delivery units.
3. Current constraints and sources, authority, permitted actions, and prohibited boundaries.
4. Natural phases, current progress, results/evidence, and next step.
5. Links to authoritative requirement, workflow, engineering, delivery, assurance, and experiment owners.
6. Decisions that affect later execution: accepted/rejected options, evidence and rationale, constraints to preserve, unresolved questions, and reconsideration conditions.
7. Research and verification summaries, unverified items, and residual risks.
8. Recovery entrypoint, closeout, and release/delivery/rollback state.

Give executors the result, scope, observable completion and unknowns; link existing context. Avoid invented estimates, repeated background and obvious steps without omitting real constraints.

The plan coordinates without duplicating requirements, designs, code, runtime, experiments, reviews or release facts. Product tradeoffs stay in REQ/PRD, durable technical decisions in TD/ADR, and formal evidence at specialist owners.

Preserve `Decision Rationale`, `Rejected Alternatives`, `Preserved Constraints`, and `Revisit Trigger`: why an option won, why alternatives lost, constraints against restoring them, and evidence that reopens the decision. This distinguishes defects from intended limits. Keep task decisions here and durable product/architecture decisions at their owners. Supersede changed decisions without rewriting history or making them permanent.

## 4. Split Plans Only as Much as Needed

- Split by explainable phase outcomes, not mechanically by file count, code layers, or a fixed user-story template.
- Prefer vertical value slices. Each defined phase should cross the interface, logic, data, or process layers needed to produce an observable, verifiable, extensible result. A pure Setup, database, API, or UI phase may precede a slice only when it directly unlocks it; sustained horizontal groundwork is not end-to-end progress.
- A phase needs only its outcome, transition criterion, and real prerequisites. State `None` when no prerequisite exists; do not draw a dependency graph for appearances.
- When later scope depends on earlier discovery, leave it `Not yet specified` and record known constraints, current unknowns, and the evidence/checkpoint that will expand it. Do not invent tasks, dependencies, estimates, or acceptance criteria for completeness. Expand only the nearest executable slice when evidence arrives.
- Execute verifiable phases toward the full authorized outcome. Record results and evidence at transitions, then continue the next authorized phase when prerequisites hold. Context compaction and handoff preserve the goal; neither phase completion nor a session boundary is a reason to stop early.
- Express requirements, fixes, workflow changes, media delivery, POCs, and governance tasks in their natural form; do not force them into user stories.
- Do not create fixed Setup, Foundation, or Polish phases, and do not put scaffolding, generic platforms, or gate construction ahead of the value loop.

When the host permits delegation, delegate independent bounded work if it can save time or improve quality after coordination cost. Otherwise continue locally; do not create agents or review rounds for their own sake. Agent messages must be readable by people, with clear grammar and proper spacing.

Describe parallel boundaries only when work will actually be assigned to several executors. First define each result, shared state, overlapping write scope, and integration owner. Apply Delivery isolation within the authorized task; tool availability or delegation does not expand its scope.

### 4.1 Minimum Package for Actual Delegation

Create a task package only when work is actually handed to another person or agent. It references existing owners and enables execution without the full chat:

- `Current Task`: the one required outcome, completion test, and explicit exclusions.
- `Global Constraints`: still-valid user authority, prohibitions, risk gates, and stop conditions, with their source and applicable scope.
- `Interfaces`: read/write scope, inputs/outputs, shared state, dependencies and preserved contracts. Identify the accepted baseline, capability/API owners, relevant implementation/contract/check paths, assignment invariants and inspected worktree/revision. Do not mistake stale code or an unconnected consumer for a missing contract. Pointers aid retrieval, not authority or proof. Supply constraints the assignee cannot retrieve, not the full map, rulebook or transcript.
- `Output Contract`: slice completion, artifacts, actual changes, development/closeout checks and integrator-owned checks, evidence, deviations, remaining work, repair owner, temporary-resource disposition, and next action.

For controlled inputs, distinguish the registered worktree from shared resource roots; check both file existence and the required format/provenance before handing off a locator. A discovered path is a retrieval hint unless an explicit instruction makes it a binding input or access boundary. Within delegated read scope, an assignee may locate a candidate alternative, but must return a binding-input mismatch to the delegator with evidence rather than silently substitute it. The delegator may correct its own mistaken locator within existing user authority; an ordinary lookup correction is not a new product decision. User-pinned inputs, license requirements, access restrictions and cost limits remain binding; unresolved authority goes to the user, not around the boundary.

At handoff/interruption, retain useful navigation, unknowns and next action in the task owner. Successors check relevant worktree changes before reuse and reread only what is needed; changing executors warrants neither project-wide rediscovery nor a second recovery ledger.

Send task-relevant facts and stable project/specialist routes, not full conversations, rulebooks or unrelated history. Describe overlap, shared resources and integration only for real parallel work. Packages never expand authority; resolve apparent conflicts from current decisions before escalating uncovered ones. Update ownership and stale executor routes on reassignment. Titles do not prove review independence: an implementer, including a reviewer taking over, still needs separate evidence when required.

### 4.2 Work-Preserving Dependency Scheduling

- When another agent, CI, human acceptance, or external system is incomplete, identify the exact downstream step blocked and whether it competes for the same branch, file, database, port, deployment directory, or production object. “Someone else is not done” is not a dependency description.
- Preserve productive work by default. Exhaust independently executable development, documentation, static checks, builds, and preparation within current authority; mark only steps that truly require the external result as waiting. Pause related work only when that result changes the solution, shared resources conflict, or the next action is irreversible.
- A temporarily absent user, unanswered progress message, or lack of real-time supervision does not revoke existing authority. Continue work within the original scope when no new decision is needed. Stop only for an explicit pause or new authority concerning scope, permission, cost, release, production, or deletion.
- When all independent work is complete, use the host’s supported bounded wait for the specific pending result. A wait timeout is not task completion: reassess available work and resume waiting without repeated unchanged updates. End the execution chain only for a real blocker or a confirmed automatic wakeup mechanism; writing a recovery entrypoint or sending an asynchronous message does not establish that mechanism. Record the checkpoint, awaited result, recovery action, and any actual blocker in the task owner. Do not invent a background continuation or create a scheduler without user authorization.

### 4.3 Outcome-Driven Course Correction

At meaningful results, failures, interruptions or handoffs, compare the approved outcome and next observable result with actual progress. Disproving a hypothesis, reducing relevant uncertainty and enabling a necessary dependency count; duration alone is not drift. Do not add a checkpoint to every tool call.

If effort no longer helps, revisit goals, causal assumptions, evidence and real dependencies before repeating the method. Test preparation, product defects and stale bookkeeping differ. These examples are not exhaustive: investigate unfamiliar causes by the same comparison.

Choose the smallest useful response at the existing owner: continue productive inquiry, reuse/repair a capability, change the observation boundary, integrate eligible work, resolve a dependency or request an uncovered decision. Load matching guidance when local methods are ineffective, not every Skill. No fixed hierarchy, retry/time/test quota, scheduler or new ledger is required.

Retain acceptance, safety, permissions, unresolved failures and all pending commitments; never revive cancelled work. Preserve interrupted scope and next actions. Delegation must be executable under host permissions, not merely sent; blocked steps leave independent authorized work available.

Check the next meaningful result for the predicted correction. A revised plan or acknowledgement is not proof of changed execution. Keep useful results and limitations; update only changed recovery facts. Healthy work needs no extra ceremony.

## 5. Session Plans and Authoritative Facts

A Codex session plan schedules the current session only. The numbered task plan is local to the project and survives context loss; do not mechanically duplicate them. With an existing task plan, keep the session plan to the current phase and write actual results back after phase transitions.

Authoritative owners include:

- Product facts: `product/USER_REQUIREMENTS.md`, `versions/<version>/PRD.md`, `product/PRODUCT_SPECIFICATION.md`, or the registered equivalent.
- Formal technical design: `engineering/designs/TD-<NNNN>-<slug>.md` or an established engineering owner.
- Durable architecture decisions: `engineering/decisions/ADR-<NNNN>-<slug>.md`.
- Formal workflow: `workflows/` or a registered Workflow Contract.
- POC: `<registered-record-root>/EXP-<NNNN>-<slug>/`.
- Formal requirement/technical review: the corresponding Product/Engineering review owner.
- Version, artifact, and release: `delivery/`, Release Plan, and Release Record.
- Reusable learning: the declared Lessons Learned Register.

Keep ordinary discussion, research, decision, and verification summaries in the task plan. Move them to specialist owners only when they become independently maintained, formally reviewed, or reusable artifacts.

## 6. Status and Update Points

For a progress request over enumerated scope, lead with the actual total and mutually exclusive counts: not started, implementing, implemented-awaiting-verification, verified, and blocked. Report excluded/cancelled scope separately and explain denominator changes. Derive counts from the existing item owner; a parent and its children are not separate completions. Verification, product acceptance and release remain distinct. Name the few real blockers and the next authorized action; do not dump a work log or invent percentages. A waiting dependent step does not make all work blocked.


Use these statuses: `planned`, `active`, `blocked`, `verifying`, `completed`, `cancelled`, `archived`.

Use `blocked` only when no meaningful work remains within current scope and execution must await a user decision, new authority, or changed external fact. If one phase or runtime step is waiting, the task may stay `active`, but the plan must identify parallel work and the wakeup condition. Idle sessions are not progress. A progress question or incoming executor receipt updates the active task; answer the user’s question and then continue authorized work. An executor’s status message does not replace the user’s request.

Update plan/register at creation, scope/authority/completion changes, meaningful phase/review/POC conclusions, delegation, pause, transfer or status transitions. Not every file edit needs a register update.

Route newly discovered facts as follows:

| Change | Required owner |
| --- | --- |
| User behavior, product scope, business rule, or acceptance | REQ/PRD or established Product owner |
| Module, public interface, data, dependency, infrastructure, or durable technical direction | TD/ADR or established Engineering owner |
| Workflow input/output, step, state, recovery, or receipt contract | Workflow Contract or established Workflow owner |
| Execution order, current phase, delegation, pause, or recovery point | Numbered task plan or established task system |
| Local implementation detail that preserves all above contracts | Code, tests, and necessary comments |

Work Logs record events; task plans retain effective state. Replace superseded status/next actions instead of adding “latest” paragraphs. Preserve rationale and link history at its owner or in Git; neither record replaces the other.

An explicit applicable decision replaces the current constraint; retain history and its superseding source, not contradictory current paragraphs. Time, sessions, builds and stages alone revoke no authority or prohibition. Keep implementation, acceptance and deployment distinct at their owners; deployment may precede unfinished acceptance or a later repair. Resume from effective scope, remaining results and next action; resolve genuine authority conflicts without blocking independent permitted work.

## 7. Closeout and Archive

Before `completed`, reconcile the original commitment, approved changes, current authoritative owners, actual result, and verification evidence:

1. Formal requirements, technical designs, ADRs, workflows, experiment decisions, reviews, and delivery facts are in their proper owners.
2. Actual results cover committed scope; incomplete, partial, added-out-of-scope, and cancelled items are explicit.
3. Matching verification ran and links evidence; omitted or uncovered portions state their impact.
4. The plan retains only necessary current state, key decision summaries, and trace links; duplicated bodies and temporary content are removed.
5. Unverified items, residual risk, release responsibility, and rollback responsibility are explicit.

`completed` means this task's result and closeout conditions are satisfied; it does not replace specialist states such as `implemented`, `accepted`, or `released`. Keep numbered plans at stable paths by default and use `archived` for historical-only status. Before offline archival, update the Task Register and all references.

## 8. Hooks and Mature Projects

Hooks do not inject a complete task plan or turn chat inference into durable rules. Only after real verification shows that recovery entrypoints are repeatedly lost should a hook carry a short Task ID, hard-boundary, and plan-path summary.

When a mature project already has a trusted task system, register its owner, object ID, status semantics, and recovery method; do not create a second `governance/tasks/`. Chat cannot be the only source of task state.

For mature takeovers, link the frozen baseline, Finding, user decision, remediation identity, re-review and temporary-content disposition under the existing takeover standard; do not duplicate its schema.

### Valid Work and Stale Bookkeeping

A missing or stale progress note, hash or receipt alone does not invalidate an otherwise verified result. Repair the existing task record within authorization. Missing evidence blocks only the claim or action for which it establishes identity, authorization, security, external side effects or release truth; never manufacture that evidence or use bookkeeping to abandon independent authorized work.

At predictable task switches, handoff or meaningful stage closeout, update only changed recovery facts in the existing task owner: completed/remaining scope, branch/worktree/head, dirt location, decisions/Findings, checks/gaps, temporary resources and next action. Read-only work returns this in its report or authorized host task system instead of editing the reviewed project. After an unexpected crash, verify actual state and label unknowns; never invent a saved checkpoint.
