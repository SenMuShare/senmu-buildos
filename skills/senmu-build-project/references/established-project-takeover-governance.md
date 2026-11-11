# Established Project Takeover

Use for established projects with confused code, documents, directories, tasks, branches or release facts. Preserve business facts, operation and recovery while making governance understandable, changeable, verifiable and transferable.

Project coordinates root, scope, task state, owner mapping, and authorization checkpoints. Product, Design, Workflow, Engineering, and Delivery repair their own facts; Assurance freezes reviews, findings, and re-review. Do not create a governance architecture that copies domain standards.

## 1. Activation and Authorization Scope

Activate when the user requests takeover, governance, reorganization, system audit, or staged remediation of an established project across stages, sessions, or domains. Do not activate for ordinary bugs, one refactor, a placement question, or read-only Q&A.

Separate:

1. **Audit authorization:** permits read-only inventory, non-mutating checks, baselines, and remediation candidates. Candidates do not become project facts.
2. **Implementation authorization:** after assessment, change only the scope covered by existing implementation authority. A compound audit-and-repair request does not require a second generic approval. It does not authorize later expansion, release, deletion, data migration, or production work.

If initial authority includes safe audit and remediation, continue through both phases. Ask only when an unresolved choice materially changes the result or the next action lacks authority; sensitive categories require coverage checks, not automatic repeated approval.

## 2. One State Owner and Workspace

Use the single Durable Task State Owner selected under [Task Execution and State Management](task-execution-and-state-management.md). This standard adds objective, authorization, findings, evidence, and review entrypoints; it does not add another task system.

Reuse existing temporary/work locations for substantial intermediates; record purpose, owner, sensitivity, retention and recovery in the current task. Create locations only when needed and authorized. Disposition may be authorized retention, archive, cleanup or justified non-applicability. Pending decisions preserve materials without automatic reapproval; policy may justify retention without invented approver metadata. Movement/deletion still needs authority; retained is not cleaned.

The optional BuildOS implementation uses [Takeover Task](../assets/mature-project-governance/TAKEOVER_TASK.template.md) and [Governance Control](../assets/mature-project-governance/GOVERNANCE_CONTROL.template.json). These are not mandatory directory commands.

## 3. Execution Protocol

### A. Freeze the Baseline

- Confirm project root, Git/worktrees/subrepositories, release units, current version, runtime objects, and verified recovery points.
- Record audit time, commit/data revision/environment identity, and evidence freshness. Preserve dirty work and parallel tasks.
- Run zero-write `assess_project_governance.py`, then semantically confirm requirement, applicable design, technical, task, run, quality, delivery, and recovery owners.

### B. Coverage and Findings

For instruction updates, apply [delta adoption](project-instruction-authoring.md#adopting-a-buildos-update) at existing owners, not a whole-template rewrite.

For UI scope, confirm sources under [Design](../../senmu-build-design/references/visual-systems-and-design-language.md) and select/reuse evidence under [Testing](../../senmu-build-engineering/references/software-testing-and-quality-verification.md). Candidates grant no redesign permission. Apply the standard migration below during authorized UI governance; ordinary local edits preserve current rules.

- Map the authorized coverage: real release units, primary journeys, owning modules, data/permission boundaries and executable entrypoints. For each capability governed in this task, establish a usable route to implementation, applicable rules and verification under the [Index Contract](project-standard-discovery-and-on-demand-loading.md#4-index-contract). Reuse existing navigation, inspect the destinations and mark uncovered domains or missing checks explicitly. A generated template or an existing path alone is not a verified route.
- Each domain records current fact, target, retain/merge/move/add candidate, impact, recovery, and acceptance evidence for its owner.
- Give findings stable IDs with evidence, P0-P3, status, impact, responsible owner, minimum remediation, and re-review conditions. Audit creates candidates, not write authority.

If product documentation is missing, do not invent historical backlogs or PRDs. Product reconstructs the current product specification from interfaces, features, code, APIs, tests, runtime, and user confirmation; Engineering reconstructs the current system specification. Separate confirmed facts, reasonable inferences, conflicts, and unknowns. For each future formal development version, keep its PRD and technical account; persist version test cases only when the risk needs them. Do not invent historical version documents.

<a id="ui-standard-migration"></a>
### UI Standard Migration

For persistent UI, converge on `design/UI_SPECIFICATION.md` within each registered governance root:

1. Confirm current sources, approved scope/revision, real pages, theme/token/components and recovery baseline.
2. In the existing task, map each old location/section to retain, extract/merge, move/archive or temporary redirect; name affected consumers and recovery. Design resolves rule conflicts by approved scope, version and valid variants, not newest timestamp.
3. Put current UI rules at the standard entry. Retain business facts with Product, implementation values in code and progress in the task. External design sources keep exact object/revision and update ownership; preserve frozen prototype/PRD historical links.
4. Switch AGENTS, README, Project Map, `ui_management.basis_path`, `required_paths` and `placeholder_scan_paths` where present. Routers link the standard and actual checks; they hold no full UI specification.
5. Retire the old current authority: archive superseded design material or leave a short redirect for live consumers with an exit condition. Preserve mixed documents' unrelated contents and recovery history.
6. Verify one current entry per scope, links, source mappings and recoverability. Reuse valid evidence for document-only moves; first adoption runs a representative task, shared design changes check representative consumers. Record unavailable runtime checks.

Consolidate approved rules rather than copying whole documents; retain one editable current standard per scope.

### C. Decisions and Remediation Waves

Record a disposition for every confirmed finding using the existing decision values `remediate`, `accept_risk`, `defer` or `false_positive`. Stopped or replaced scope uses the existing task cancellation/supersession contract, not a new finding-decision value. Tie a decision to its real authority, scope and revisit condition; a current request or project policy may already cover it. Do not invent a new human approval for each item. P0-P1 cannot be vaguely deferred; accepting material risk still requires the responsible owner's authority and evidence. In the optional file-backed record, remediate is an authorized decision to do work, not proof that the work has finished.

Organize waves by verifiable outcome, not file count, fixed sprint, or “all directories first.” Prioritize: prevent irreversible harm; restore authority and critical paths; remove duplicate truth and high-propagation coupling; improve local comprehensibility. Each wave links finding IDs, tasks, change identity (commit, release unit, data revision, or non-Git receipt), verification, and recovery.

### D. Verification and Closeout

- Keep in-progress decisions and results truthful: an authorized remediation may have no changes yet and verification may be pending or failed. Use resolved_unverified only after an actual correction exists. Claim verified_resolved only with change references and sufficient verification of the original problem and affected behavior, plus any required review tied to the target. For a navigation or rule defect, verify that actual defect and its consumers; do not invent an unrelated runtime failure to replay.
- At each wave, update completed/incomplete work, new risk, recovery, and one next action in task state; do not depend on chat memory.
- Final review freezes the target again and checks approved scope, open findings, formal owners, critical paths, quality commands, release/rollback state, and residual risk.
- Close the material-disposition obligation using existing policy or current authority: record what is retained and why, what authorized movement/cleanup actually happened, or why no relevant materials exist. Preserve unique recovery evidence. An unresolved cost, privacy or recovery choice remains open; retention must not be reported as requested physical cleanup. This record authorizes no deletion by itself.

## 4. Verifiable Control

When using the BuildOS file implementation, place the tailored control record in the registered task/review owner and run:

```bash
python3 <buildos>/skills/senmu-build-project/scripts/validate_mature_project_governance.py \
  --record <project-control-record.json>
```

The validator checks relationships and closeout invariants only; it does not judge technical quality or perform fixes, branches, releases, or deletion. Other state systems may implement the same invariants natively without exporting duplicate JSON.

Before `completed`, verify baseline/coverage, finding dispositions, authorized corrections with changes/evidence, required P0-P1 review, final-review target/limits, resolved or inapplicable temporary disposition, and separate release/production facts. For navigation work, follow actual code/rule/check routes and record gaps. Structural/semantic checks do not prove model behavior or Token savings; disclose missing observations without requiring an unrequested model experiment.
