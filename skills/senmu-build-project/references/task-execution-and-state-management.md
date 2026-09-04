# Task Execution, Planning, and State Management

Use this standard for work that spans meaningful steps, phases, or sessions. Task plans belong to the project, not chat memory or a specialist Skill. A project that needs recovery must declare a Durable Task State Owner. New BuildOS standard/release projects default to numbered task-plan files; core and mature projects may map a trusted README, issue tracker, database, plan file, or external system.

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

The plan is a coordination entrypoint. It does not duplicate formal requirements, technical design, code, runtime state, experiments, review reports, or release facts. Material product tradeoffs belong in REQ/PRD; durable technical decisions in TD/ADR; formal reviews, POCs, tests, and release evidence in their specialist owners.

A key decision record must let a later agent distinguish a defect from an intentional constraint. Preserve `Decision Rationale`, `Rejected Alternatives`, `Preserved Constraints`, and `Revisit Trigger`: why the option won, which alternatives were rejected and why, what unchanged conditions prohibit silently restoring them, and what evidence or environmental change reopens the decision. Keep task-scoped decisions in the plan and promote durable product/architecture decisions to their original owner. Append a superseding decision when conditions change; do not rewrite history or make an old decision permanent.

## 4. Split Plans Only as Much as Needed

- Split by explainable phase outcomes, not mechanically by file count, code layers, or a fixed user-story template.
- Prefer vertical value slices. Each defined phase should cross the interface, logic, data, or process layers needed to produce an observable, verifiable, extensible result. A pure Setup, database, API, or UI phase may precede a slice only when it directly unlocks it; sustained horizontal groundwork is not end-to-end progress.
- A phase needs only its outcome, transition criterion, and real prerequisites. State `None` when no prerequisite exists; do not draw a dependency graph for appearances.
- When later scope depends on earlier discovery, leave it `Not yet specified` and record known constraints, current unknowns, and the evidence/checkpoint that will expand it. Do not invent tasks, dependencies, estimates, or acceptance criteria for completeness. Expand only the nearest executable slice when evidence arrives.
- Execute only the phase that current context can complete, verify, and hand off. At phase end, record actual results, evidence, remaining work, and the next step.
- Express requirements, fixes, workflow changes, media delivery, POCs, and governance tasks in their natural form; do not force them into user stories.
- Do not create fixed Setup, Foundation, or Polish phases, and do not put scaffolding, generic platforms, or gate construction ahead of the value loop.

Describe parallel boundaries only when work will actually be assigned to several executors. First define each result, shared state, overlapping write scope, and integration owner. Parallelism does not authorize a branch or worktree automatically.

### 4.1 Minimum Package for Actual Delegation

Create a task package only when work is actually handed to another person or agent. It references existing owners and enables execution without the full chat:

- `Current Task`: the one required outcome, completion test, and explicit exclusions.
- `Global Constraints`: still-valid user authority, prohibitions, risk gates, and stop conditions.
- `Interfaces`: permitted read/write scope, inputs/outputs, shared state, dependencies, and contracts that must remain intact.
- `Output Contract`: required artifacts, actual changes, tests/evidence, deviations, incomplete work, and next action.

Send only facts needed for the current task, not the entire conversation, all BuildOS standards, or unrelated executor history. Read specialist rules through stable links and project entrypoints. Add overlap, shared-resource, and integration responsibility only for real parallel work. A package cannot expand original authority; return conflicts or scope changes to the original owner.

### 4.2 Work-Preserving Dependency Scheduling

- When another agent, CI, human acceptance, or external system is incomplete, identify the exact downstream step blocked and whether it competes for the same branch, file, database, port, deployment directory, or production object. “Someone else is not done” is not a dependency description.
- Preserve productive work by default. Exhaust independently executable development, documentation, static checks, builds, and preparation within current authority; mark only steps that truly require the external result as waiting. Pause related work only when that result changes the solution, shared resources conflict, or the next action is irreversible.
- A temporarily absent user, unanswered progress message, or lack of real-time supervision does not revoke existing authority. Continue work within the original scope when no new decision is needed. Stop only for an explicit pause or new authority concerning scope, permission, cost, release, production, or deletion.
- When all independent work is complete, record the checkpoint, stable identity of the awaited result, wakeup entrypoint, timeout/escalation condition, and next action in the task owner, then release the idle execution chain. Prefer event/message wakeup. Keep waiting only for short bounded tool calls or high-risk operations requiring live supervision. Do not repeatedly poll unchanged state or send repeated “still waiting” updates.

## 5. Session Plans and Authoritative Facts

A Codex session plan schedules the current session only. The numbered task plan is local to the project and survives context loss; do not mechanically duplicate them. With an existing task plan, keep the session plan to the current phase and write actual results back after phase transitions.

Authoritative owners include:

- Product facts: `product/USER_REQUIREMENTS.md`, `versions/<version>/PRD.md`, `product/PRODUCT_SPECIFICATION.md`, or the registered equivalent.
- Formal technical design: `engineering/designs/TD-<NNNN>-<slug>.md` or an established engineering owner.
- Durable architecture decisions: `engineering/decisions/ADR-<NNNN>-<slug>.md`.
- Formal workflow: `workflows/` or a registered Workflow Contract.
- POC: `experiments/EXP-<NNNN>-<slug>/`.
- Formal requirement/technical review: the corresponding Product/Engineering review owner.
- Version, artifact, and release: `delivery/`, Release Plan, and Release Record.
- Reusable learning: the declared Lessons Learned Register.

Keep ordinary discussion, research, decision, and verification summaries in the task plan. Move them to specialist owners only when they become independently maintained, formally reviewed, or reusable artifacts.

## 6. Status and Update Points

Use these statuses: `planned`, `active`, `blocked`, `verifying`, `completed`, `cancelled`, `archived`.

Use `blocked` only when no meaningful work remains within current scope and execution must await a user decision, new authority, or changed external fact. If one phase or runtime step is waiting, the task may stay `active`, but the plan must identify parallel work and the wakeup condition. Idle sessions are not progress.

Update the task plan and Task Register when the task is created; scope, authority, or completion definition changes; a meaningful phase or review round completes; a POC reaches a phase conclusion; delegation, pause, or session transfer occurs; or status changes to verifying, completed, cancelled, or archived. Do not refresh the register for every small file edit.

Route newly discovered facts as follows:

| Change | Required owner |
| --- | --- |
| User behavior, product scope, business rule, or acceptance | REQ/PRD or established Product owner |
| Module, public interface, data, dependency, infrastructure, or durable technical direction | TD/ADR or established Engineering owner |
| Workflow input/output, step, state, recovery, or receipt contract | Workflow Contract or established Workflow owner |
| Execution order, current phase, delegation, pause, or recovery point | Numbered task plan or established task system |
| Local implementation detail that preserves all above contracts | Code, tests, and necessary comments |

A Work Log records what happened; a numbered task plan records the current effective plan and state. Neither replaces the other.

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

A mature-project takeover task must also link the frozen baseline, assurance Finding, user decision, remediation task/change identity, re-review evidence, and disposition of temporary content. The mature-project takeover standard owns those semantics; do not duplicate its schema here.
