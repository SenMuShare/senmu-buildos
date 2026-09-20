# Project Governance Instances and Evolution

BuildOS supplies methods, not project facts. A **Project Governance Instance** adopts them through actual entrypoints, owners, state sources, quality commands and delivery evidence.

## 1. Two Kinds of Authority

- **Fact authority:** local code, documents, databases, task systems, runtime state, and release receipts describe what the project is now. BuildOS defaults cannot overrule those facts.
- **Governance standard:** BuildOS evaluates whether the fact chain is complete, clear, recoverable, verifiable, and evolvable. Existing rules are not correct merely because they exist; repair the original owner when rules are missing, conflicting, duplicated, stale, or immovable.

Respecting facts does not freeze the current state. When a gap exists, propose the target instance and migration impact, then update, merge, or replace the original owner after authorization. Do not create a permanent parallel truth source.

## 2. Unify Meaning, Not Shape

An instance must make actual responsibility discoverable for objective/scope, requirements/acceptance, technical direction, task state, run state, quality entrypoints, delivery/release facts, and recovery. File and directory names may differ.

- New projects may use BuildOS defaults such as `governance/`, `product/`, and `engineering/`, combine roles, or use a better project-specific layout after responsibilities are known.
- Established workflows may keep task packages, databases, manifests, Makefiles, and receipts as owners.
- External requirement/task systems may be owners when the project entrypoint records system, object ID, access method, and offline recovery boundary.
- Small scripts may combine roles in README, tests, and version records if each fact remains unique and discoverable.

Keep stable cross-project knowledge such as Python, frontend frameworks, and code quality in BuildOS for conditional use. Projects retain selected stack, actual constraints, entrypoints, exceptions, and validation commands—not copied manuals.

Design context also belongs to the project instance. Create a minimum design owner for a new UI project only when brand, tokens, components, or cross-page rules have stable reuse. Established projects reuse their design system, theme, tokens, component standards, or brand guide. If absent, Design may reconstruct a baseline from real interfaces while separating observation, inference, conflict, and unknown. Installing BuildOS, reading its design library, or analyzing a reference never creates a parallel `BuildOS Design Context` automatically.

### Placement Advice Is Not a Directory Command

For “where should this live?”, identify the semantic owner, then give preferred path, reason, acceptable alternative, relationship to existing files, and whether a directory is needed. Defaults are comparisons, not mandates. Advice alone never creates or migrates files.

When a specific artifact is requested, create it in a confirmed owner. If it introduces durable truth, changes the project root, or requires bulk migration, show target map and impact first. Distinguish a reorganization plan—current state, target, mapping, sequence, compatibility, recovery—from authorized execution.

## 3. Three Capabilities

### Initialize a New Project

For a blank or confirmed new project, determine lifecycle intent, composition, public model, release channels, confirmed artifacts, governance level, and modules separately from requirements, expected architecture, runtime, and user acquisition. Inspect a zero-write candidate with `--mode plan-new`; after implementation authority, run `--mode initialize-new` with the same explicit parameters.

Project type suggests candidates only. `release` means formal release governance, not proof of a deployment target, container, installer, or retention need. If the approved path differs from script defaults, follow the target map: create minimum owners and record path roles/relationships in policy. Defaults are optional implementations. Finish instruction adoption through [dual-track authoring](project-standard-discovery-and-on-demand-loading.md#dual-track-instruction-authoring): calibrate real project facts and adopt applicable shared working principles in the chosen project language. An English generated scaffold is not completed localization or semantic acceptance.

### Assess an Existing Project

Remain strictly read-only through two stages:

1. **Authority-first inventory:** from assessment root, navigation, release-unit/worktree registration, current baseline, and Git-root candidates, inventory project map, policy, and candidate owners. Exclude caches, backups, archives, retired copies, and linked worktrees explicitly. A Git root is only a repository candidate; a worktree is not a new repository/release unit. Show registered but unscanned worktrees as `authority_reference_not_scanned` until the current baseline is semantically confirmed. Supported `repositories.json` declarations may confirm release units, ledgers, and retirement evidence. One-off tasks, POCs, experiments, and third-party caches cannot masquerade as project-level task, quality, or production owners. Confirm delivery boundaries from registration and runtime facts. `assess_project_governance.py` performs this deterministic stage with bounded output; `--verbose` expands the full inventory.
2. **Semantic assessment:** read entrypoints and real evidence per release unit; confirm requirement, technical, Durable Task State, Run State, quality, production, and recovery owners; then report confirmed mapping, conflict, gap, duplication, and migration risk.

Do not reduce assessment to a file list or pass/fail. For complex cases, separate observed facts, governance judgment, preferred evolution, acceptable alternatives, retained exceptions, risk, and authorization. For many branches/worktrees, Project confirms roots, entrypoints, and identity drift; Delivery evaluates reachability, unique facts, and safe cleanup. Never classify them as waste for directory neatness.

Filename matches are candidates, not semantic owners. Multiple maps, databases, or task files are not conflicts by count alone. Both stages are zero-write.

### Evolve an Existing Project

After assessment and authorization, evolve the original project. When requirements, architecture, installation, deployment, public strategy, release channels, or artifact types change, reassess affected capabilities/path roles and propose an incremental target map. A Dockerfile, Xcode project, or packaging script is only a signal; enable artifact lifecycle after a real consumer, release contract, or rollback dependency exists.

Repair causes in requirements, responsibility, directories, interfaces, data ownership, defaults, and workflows; fill missing roles, merge duplicate owners, migrate immovable paths, and retain recovery points. Project entrypoints, policy, schema, tools, and evidence then own routine execution.

For multi-domain audit, several remediation waves, cross-session recovery, and final review, use [Established Project Takeover](established-project-takeover-governance.md). It maps the existing Durable Task State Owner and preserves fact-first assessment, existing authorization boundaries, and original-owner evolution. A compound audit-and-repair request covers its scoped phases without another generic approval.

For in-scope business-agent content, use [Workflow governance](../../senmu-build-workflow/references/business-agent-content-governance.md); root AGENTS-only work does not authorize it.

### Experiment Adoption

When POCs are in scope, resolve one experiment contract before creating run assets. New scaffolds declare a draft `poc_management` pointer; core projects may keep the storage contract in README; active reports still belong to the registered, isolated record root. Multi-run comparisons use the existing experiment register. Calibrate storage, protected development/release worktrees, tracking, retention and backup under Assurance's [POC contract](../../senmu-build-assurance/references/reproducible-poc-governance.md#3-project-storage-contract). Generated templates do not activate that contract.

For an established project, evolve its original owner in place; use an `existing_contract` pointer when an equivalent already works rather than copying it into a second policy. Follow the entrypoint to one representative experiment or disposable fixture and check isolation, retained evidence and resource-closeout routing. Existing runs, rejected decisions and legacy manifests are historical evidence, not initializer output to overwrite. Do not read all experiments for ordinary implementation or execute real cleanup as a governance test.

## 4. State Owners

Follow [Task Execution and State Management](task-execution-and-state-management.md) for cross-stage/session state ownership and recovery. The instance only registers the chosen Durable Task State Owner.

Task State stores cross-stage goal, boundary, progress, and recovery entrypoint. Run State stores one run's step, attempt, checkpoint, and output. Product, engineering, delivery, and review artifacts store their domain facts. Link by stable IDs; never copy bodies.

## 5. Relocatable Identity

A committed governance instance must not identify a project by machine-specific absolute path. Prefer Git toplevel, repository/domain IDs, a root containing `.senmu-buildos/config.json`, workspace path roles, and relative relationships. New-project policy uses `root_locator.kind=git_toplevel|governance_policy_root` and relative `.`. Register roles for private authority, public projection, runtime data, staging, delivery, and archive before mapping project-relative paths. Absolute paths are runtime resolution or uncommitted local configuration only; generated content must not vary by machine, username, or parent business folder.

## 6. Learning

Keep project facts and SOPs in the instance. Assurance may propose a lesson to BuildOS only after reproduction or cross-project verification shows it changes general decisions without broad overhead. Each project still decides when to upgrade its instance.
