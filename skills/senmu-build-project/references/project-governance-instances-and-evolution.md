# Project Governance Instances and Evolution

A **Project Governance Instance** adopts BuildOS methods through actual entrypoints, owners, state, checks and delivery evidence. BuildOS supplies no project facts.

## 1. Two Kinds of Authority

- **Fact authority:** current code, documents, databases, task/runtime state and release receipts establish project facts; BuildOS defaults cannot override them.
- **Governance standard:** evaluate completeness, clarity, recovery, verification and evolution. Existing rules may be wrong; repair their original owner when missing, conflicting, duplicated, stale or immovable.

For gaps, propose a target and migration impact; update/merge/replace original owners within authority without parallel truth.

## 2. Standard Owners and Project Shape

Make domain facts and state discoverable. Use the persistent UI standard below; other layouts may adapt to actual capabilities and external systems.

- New projects use applicable `governance/`, `product/`, `design/`, `engineering/` roles; omit unused modules.
- Established workflows may keep task packages, databases, manifests, Makefiles, and receipts as owners.
- External requirement/task systems may be owners when the project entrypoint records system, object ID, access method, and offline recovery boundary.
- Small scripts may combine non-UI roles in README, tests and version records while preserving unique facts.

Keep cross-project language/framework/quality methods in BuildOS for conditional use. Projects retain selected stack, actual constraints, entries, exceptions and commands, not copied manuals.

### Placement Advice Is Not a Directory Command

For placement advice, name the owner, standard or preferred path, reason and affected files. Alternatives must preserve any applicable standard; advice alone authorizes no migration.

Create requested artifacts at a confirmed owner. For new durable truth, root changes or bulk migration, show target map and impact first. Separate plans (current/target state, mapping, sequence, compatibility, recovery) from authorized execution.

## 3. Three Capabilities

### Initialize a New Project

For new projects, classify lifecycle, composition, public model, release channels, real artifacts, governance level and modules separately from requirements, architecture, runtime and user acquisition. Inspect `--mode plan-new` with zero writes; authorized `--mode initialize-new` uses the same explicit parameters.

Project type suggests candidates. `release` proves no deployment target, container, installer or retention need. Follow approved target maps over optional defaults; create minimum owners and register path roles/relationships. Finish [dual-track authoring](project-standard-discovery-and-on-demand-loading.md#dual-track-instruction-authoring): calibrate project facts and adopt applicable principles in the chosen language. An English scaffold proves neither localization nor semantic acceptance.

### Assess an Existing Project

Remain strictly read-only through two stages:

1. **Authority-first inventory:** use assessment root, navigation, release/worktree registration and current baseline to inventory maps, policy, Git-root and owner candidates. Exclude caches, backups, archives, retired copies and linked worktrees. Git roots remain repository candidates; worktrees are not release units. Mark registered but unscanned worktrees `authority_reference_not_scanned` until baseline confirmation. Supported `repositories.json` declarations may identify release units, ledgers and retired evidence. One-off/POC/experiment/cache records cannot become project task, quality or production owners. Confirm delivery boundaries from registration/runtime. `assess_project_governance.py` provides this bounded deterministic inventory; `--verbose` expands it.
2. **Semantic assessment:** read entrypoints/evidence per release unit; confirm requirement, applicable design, technical, Durable Task State, Run State, quality, production and recovery owners. Report mappings, conflicts, gaps, duplication and migration risk.

Assessment exceeds file lists/pass-fail: separate facts, governance judgment, preferred evolution, alternatives, retained exceptions, risk and authority. For branches/worktrees, Project checks roots, entries and identity drift; Delivery checks reachability, unique facts and safe cleanup. Directory neatness proves no waste.

Filenames are candidates, not semantic owners; candidate counts prove no conflict. Both stages remain zero-write.

### Evolve an Existing Project

After assessment and implementation authorization, evolve original owners. Changed requirements, architecture, installation, deployment, public strategy, release channels or artifacts require affected capability/path reassessment and an incremental target. Dockerfiles, Xcode projects and packaging scripts are signals; artifact lifecycle needs a real consumer, release contract or rollback dependency.

Repair requirements, responsibilities, directories, interfaces, data ownership, defaults and workflows. Fill missing roles, merge duplicate owners, migrate immovable paths and retain recovery. Project entries, policy, schema, tools and evidence own routine work.

For multi-domain audit, remediation waves, cross-session recovery and final review, use [Established Project Takeover](established-project-takeover-governance.md): existing task state, fact-first assessment, authority and original-owner evolution. Scoped audit-and-repair authority persists.

For in-scope business-agent content, use [Workflow governance](../../senmu-build-workflow/references/business-agent-content-governance.md); root AGENTS-only work does not authorize it.

### UI Adoption

Infer UI capability from user goals and current facts, not project type or filenames. A new browser tool needs this judgment even when the user never says UI. `plan-new` without a declaration reports `unassessed`; before `initialize-new`, choose `--ui-scope none|one_off|persistent`. Unassessed initialization refuses without writing. No UI and `one_off` add no permanent UI file; exploration stays task-local.

Persistent UI, including one maintained page, uses `design/UI_SPECIFICATION.md`. Project renders Design's [UI Specification template](../../senmu-build-design/assets/design-governance/UI_SPECIFICATION.template.md) and links it from AGENTS/map; full rules never belong in those routers. `--ui-owner` accepts only an equivalent canonical path for new declarations. `ui_management` stores scope and `basis_path`, not acceptance. Keep the approved scope/revision, real theme/token/components, representative pages/states/viewports, exceptions and verification under [Design](../../senmu-build-design/references/visual-systems-and-design-language.md). Unimplemented entries stay task gaps.

Recovery preserves explicit saved scopes and existing bytes, including legacy bases; missing legacy declarations remain unassessed, not proven `none`. Nonstandard legacy bases require [UI migration](established-project-takeover-governance.md#ui-standard-migration): normal validation warns, strict validation cannot certify standardization; role collisions or escaping paths are errors. Do not use the initializer to overwrite a mature project. Keep selected prototypes linked through [Product](../../senmu-build-product/references/product-requirements-and-iteration.md#23-requirement-linked-visual-assets).

First adoption rehearses an authorized representative task from basis to implementation, rendered comparison and user flow. Later, select/reuse impact/risk-based evidence under [Testing](../../senmu-build-engineering/references/software-testing-and-quality-verification.md); shared changes check representative consumers. Record runtime/access gaps in the task. No UI impact adds no checks. Scaffolds prove no host loading, model adherence, UI quality or acceptance.

### Experiment Adoption

When POCs are in scope, resolve one experiment contract before creating run assets. New scaffolds declare a draft `poc_management` pointer; core projects may keep the storage contract in README; active reports still belong to the registered, isolated record root. Multi-run comparisons use the existing experiment register. Calibrate storage, protected development/release worktrees, tracking, retention and backup under Assurance's [POC contract](../../senmu-build-assurance/references/reproducible-poc-governance.md#3-project-storage-contract). Generated templates do not activate that contract.

For an established project, evolve its original owner in place; use an `existing_contract` pointer when an equivalent already works rather than copying it into a second policy. Follow the entrypoint to one representative experiment or disposable fixture and check isolation, retained evidence and resource-closeout routing. Existing runs, rejected decisions and legacy manifests are historical evidence, not initializer output to overwrite. Do not read all experiments for ordinary implementation or execute real cleanup as a governance test.

## 4. State Owners

Register the existing Durable Task State Owner; use [Task Execution](task-execution-and-state-management.md) for cross-stage/session state and recovery.

Task State owns cross-stage goal, scope, progress and recovery; Run State owns one run's step, attempt, checkpoint and output. Product, Design, Engineering, Delivery and review owners retain domain facts. Link stable IDs, never bodies.

## 5. Relocatable Identity

A committed governance instance must not identify a project by machine-specific absolute path. Prefer Git toplevel, repository/domain IDs, a root containing `.senmu-buildos/config.json`, workspace path roles, and relative relationships. New-project policy uses `root_locator.kind=git_toplevel|governance_policy_root` and relative `.`. Register roles for private authority, public projection, runtime data, staging, delivery, and archive before mapping project-relative paths. Absolute paths are runtime resolution or uncommitted local configuration only; generated content must not vary by machine, username, or parent business folder.

## 6. Learning

Keep project facts and SOPs in the instance. Assurance may propose a lesson to BuildOS only after reproduction or cross-project verification shows it changes general decisions without broad overhead. Each project still decides when to upgrade its instance.
