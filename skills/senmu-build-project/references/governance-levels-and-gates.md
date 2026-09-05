# Governance Levels and Gate Policy

Use this standard to choose the amount of project governance a task needs. Avoid burdening small tasks with heavy process and letting major fixes, releases, or high-risk changes bypass gates because they appear small.

## 0. Govern at the Source; Use Gates as a Backstop

Default to quality built in, not an expanding inspection layer after defects are created. Identify the production step that creates the defect, then correct requirements, ownership, architecture, interfaces, data models, defaults, implementation, or operations so the correct path is the easiest and default path.

Tests, validators, checklists, prompts, approvals, and release gates detect regressions or control residual risk that cannot be eliminated; they do not replace root-cause correction. One failure does not automatically justify a new gate, and adding a gate does not prove the problem is solved.

Before adding or strengthening a gate, determine:

1. What verified root cause and production step create the defect, and whether that cause can be removed or made less likely directly.
2. What risk remains after correcting the production step, and whether its impact, reversibility, and probability justify a gate.
3. Whether the decision is deterministic, stable, important, or frequent; whether a real execution entrypoint can evaluate it with low false-positive rates; and whether semantic guesses, prompts, or long checklists would fail under context, model, or execution-cost limits.
4. Whether runtime, context, time, maintenance, and false-positive costs are proportional to risk and can be limited to critical paths.
5. Who maintains the gate and when it will be reviewed, weakened, or retired so temporary patches do not accumulate permanently.

For a new or changed deterministic gate, test at least one real violation, one legitimate exception or an explicit no-exception case, and one adjacent but unrelated case. Repeated false positives require narrowing or removing the gate, not transferring its cost to later agents.

Retain fail-closed gates for unacceptable risks such as security, privacy, payments, authorization, production data, destructive operations, and formal-release integrity. This policy limits gate substitution for engineering fixes and excessive defense in low-risk work; it does not remove necessary verification.

### 0.1 Self-Check, Formal Review, and Independent Assurance

- The current specialist owner performs ordinary self-checks: Product for requirements, Engineering for technical design, implementation, and tests, Workflow for process, and Delivery for release. Return findings directly to the original owner; do not create a separate review process or report.
- Conduct formal review only when the project process, governance level, or owner explicitly requires it. Reuse existing requirement, technical, or release-review owners and tailor checks to current risk.
- Use Assurance only when an independent conclusion is explicitly requested, a cross-domain dispute exists, or a formal review genuinely requires separation of duties. G3-G4 raises evidence, verification, and closeout strength but does not automatically invoke Assurance.
- Run consistency checks at natural transitions: requirements to design/implementation, design to implementation, implementation to acceptance/release, and task closeout. Do not repeat the full suite for every small step or ordinary file edit.
- Do not create `checklists/` or one-off checklist files by default. Establish a durable checklist only when checks recur, risk is material, content is stable, no existing owner can carry it, and maintenance ownership, review cadence, and retirement conditions are explicit. Otherwise record findings in the current task or existing review.

## 1. Classify Before Execution

Determine the governance level when entering a task. Escalate when investigation reveals greater risk; never downgrade for convenience.

| Level | Typical work | Minimum requirement |
| --- | --- | --- |
| G0 Lightweight inquiry/read | Explain code or process, organize ideas, no file changes | State the basis; no work log unless a project decision results |
| G1 Contract-preserving local change | Local implementation or content adjustment that preserves product, runtime, and delivery contracts | Check contract and impact scope; run an available targeted quality check or disclose what was not verified |
| G2 Ordinary engineering task | Small feature, ordinary bug, local refactor, read-only engineering governance review, documentation completion | Read relevant references; run formatting, lint, applicable type checks, and matching tests; for architecture review, report evidence without automatically expanding into refactoring; write a work log when needed |
| G3 Release or structural task | Hotfix, formal release, cross-module architecture change, public contract or data-structure change, deployment, versioning, rollback, production verification | Explain relevant architecture impact; run matching checks and project-required gates. For an authorized release, satisfy the applicable version, log, Tag, artifact, production-verification, and rollback contract |
| G4 High-risk or organizational-learning task | Security, payments, permissions, data migration, production incident, repeated failure, cross-agent rework | Verify the actual high-risk path. Retrospect on an incident, material rework, or explicit review request; update standards and submit BuildOS feedback only when eligible |

Use the highest applicable level.

## 2. Gate Types

Classify each rule as one of the following whenever possible.

### Hard Gate

Completion cannot be claimed unless the gate passes or the project owner explicitly grants and records an exception.

Typical Hard Gates:

- A formal release satisfies the project-declared version, changelog, Tag/channel, target verification, and rollback contract; enable only applicable delivery layers.
- A hotfix requires confirmation of release unit, current version, rollback point, and the boundary of unreleased changes.
- Production data, payments, authorization, deletion, export, and upload require backend validation and verification evidence.
- Real secrets, user-private information, and production data must not enter Git or public logs.
- Formatting, lint, type, test, and build checks declared by the project as merge or release blockers must pass. The owner must explicitly approve and record risk when a check cannot run or is waived.
- Declared forbidden dependencies, cycles, internal references across release units, and destructive public-contract changes must block. To change the rule, update the architecture contract first and record impact and approval.
- G3-G4 additions of modules, public interfaces, database schemas, or foundational dependencies require an impact statement, matching tests, and rollback or compatibility evidence.
- Formal release requires an authoritative-document impact decision: update changed bodies, confirm the applicable version when unchanged, and preserve historical snapshots at their original version.
- When G3-G4 work uses branches, worktrees, clones, or migration staging, source, runtime assets, ledgers, deliverables, and verification must return to each formal owner registered by the responsible owner. Completion in a temporary directory is insufficient. A project-level POC root may remain separate from product release source; POC closeout clears its own residue, while ordinary product release checks candidate and shared-resource effects.
- Requirement and technical check items are review aids, not fixed gates for every task. They block transition only when a G3-G4 change actually concerns that area, enters formal review, or the owner explicitly requires it and blocking findings remain. Tailor G0-G2 coverage to risk and record omissions instead of adding ceremonial process.
- Before deleting a POC that affects a technical or product decision, preserve a stable experiment ledger, structured manifest, and reproduction protocol sufficient to reconstruct the experiment. When human evaluation is part of the declared acceptance, complete it before that conclusion; otherwise use the applicable objective evidence.

### Soft Gate

Perform it by default; if omitted, state why it is inapplicable or deferred.

Typical Soft Gates:

- Write a work log after an ordinary feature is completed.
- Synchronize requirements or technical plans when business rules change.
- Prefer a mature component library for frontend pages.
- Before a repetitive production, media-composition, or code-generation pipeline, select the main route and audit reusable capability; record no match or inapplicability when reuse is rejected.
- Visually verify important UI changes in a browser.
- Add useful comments, types, and matching tests with new or changed code; explain when inapplicable.
- Before adding a module, dependency, abstraction layer, cross-module state, or a second equivalent capability, search existing implementation and explain architectural impact. Split the task or add independent review when the project change budget is exceeded.
- Register known temporary patches, long-term suppressions, and structural hotspots with a technical-debt ID, impact, and closeout condition. Do not force unrelated work to clear them.

### Guidance

Prefer these practices, but adapt them to project stage, technology, or owner direction.

- Prefer mature component ecosystems compatible with the project's technical baseline.
- Choose storage from data volume, consistency, runtime, and team capability; project type alone is not an argument.
- Choose deployment form from delivery, isolation, observability, and operational constraints; containerization is not universally mandatory.

## 3. Execution Matrix

| Level | Read | Code quality | Log | Version | Retrospective | Production verification |
| --- | --- | --- | --- | --- | --- | --- |
| G0 | As the question requires | Usually none | No | No | No | No |
| G1 | Relevant code/docs | Targeted checks | Usually no | No | Only after a notable failure | Usually no |
| G2 | Relevant references | Format, lint, applicable types, matching tests; evidence-based structural review | Usually yes | For user-visible change or release | After rework/failure | By impact scope |
| G3 | Affected architecture or delivery standards | Impact-based checks and project-required gates | By material work | For authorized release | For material incidents/rework or explicit request | For applicable release target or risky path |
| G4 | Relevant risk standards; retrospective when triggered | G3 plus affected security, data, authorization, or real-path review | By material work | By release ownership | For material incidents/rework or explicit request | By risk path |

## 4. Noise Reduction

- Do not add unrelated documents, versions, or release records for lightweight work.
- For G1, use Engineering's contract-preserving fast path: normally do not combine Product, Workflow, or Delivery; do not edit PRD, ADR, or Changelog; do not write a Work Log; retain only the affected implementation and one targeted check. Project rules or actual contract/risk escalation override this default.
- Engineering testing standards determine development batches and test timing; a governance level does not mechanically trigger every full gate after each small edit.
- Do not add a prompt, checklist item, or validator for every fixed defect; first prove a residual risk still needs control.
- Final replies should name only gates material to the task, not reproduce a complete PMO checklist.
- Do not present Guidance as mandatory or a Hard Gate as optional.
- State why the level escalated, such as discovered production impact, data risk, or repeated failure.

## 5. Minimum Report

The final report must state at least:

- the actual governance level, or implicitly why the work was lightweight;
- the key verification completed;
- any incomplete or inapplicable gates;
- where a retrospective or document update landed, if any.
