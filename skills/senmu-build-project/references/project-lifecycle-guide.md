# Project Engineering Governance Guide

**Read as needed:** [Position and Scope](#1-position-and-scope) · [Entry Order](#2-entry-order) · [Common Work Loop](#3-common-work-loop) · [Initialization Modules](#4-initialization-modules) · [Initialization Architecture Gate](#5-initialization-architecture-gate) · [Choosing Technology](#6-choosing-technology) · [Governance and Delivery Strength](#7-governance-and-delivery-strength) · [Project Handoff](#8-project-handoff) · [Completion Definition](#9-completion-definition) · [Minimum Technology Baseline](#minimum-technology-baseline)

This guide is the second-level navigation for project entry, initialization, execution, release, and learning. It defines lifecycle and decision order without duplicating specialist standards. Load details conditionally from the `SKILL.md` index.

## 1. Position and Scope

Treat Senmu BuildOS as a cross-project governance baseline, not a project's PRD, technical design, or daily runbook. It applies to software, scripts, workflows/harnesses, media production, POCs, and composite delivery; each project selects only the modules it needs.

- When a project has clear rules, use them as the current factual entrypoint. Evolve the original owner under BuildOS governance only for omissions, conflicts, duplication, staleness, or portability defects.
- Use this guide when rules are missing, conflicting, or stale, or after a structural or high-risk governance event.
- After calibration, write durable rules back to project authority; the project must not depend permanently on this Skill.
- Technology, directories, and delivery methods may change. Objective/source, responsibility boundaries, state, verification, delivery evidence, and recovery must remain discoverable.

## 2. Entry Order

Establish facts in this order; do not infer them from chat memory:

1. Confirm objective, permitted modification scope, explicit exclusions, and completion definition.
2. Use README/AI entrypoints to identify project form, current objective, real paths, state source, and deliverables. Do not assume a software product.
3. Select only the governance modules needed for this task, then read matching requirement, technical, workflow, Git, POC, delivery, or runtime owners.
4. For work spanning dependent steps, phases, agents, or sessions, use the project's Durable Task State Owner for boundaries, progress, evidence, and recovery. New standard/release projects default to `governance/tasks/`; core projects may retain README, issues, or an external task system.
5. Check the authoritative project root, Git root, branch/workspace, release or delivery unit, and current runtime entrypoint.
6. Search for existing implementation, shared capability, public contracts, data/material owners, and legacy entrypoints.
7. Choose G0-G4 from risk and reversibility; escalate on newly discovered risk.
8. Determine whether owner confirmation or a safety, production, release, data, authorization, or destructive-action gate applies before proposing, reviewing, or implementing.

Pause only when an unresolved choice materially changes scope, architecture, deployment, maintenance cost, or risk. Otherwise state the basis and proceed. Requirements, plans, development facts, and release facts belong in separate authoritative owners.

## 3. Common Work Loop

```text
Confirm objective and authority -> Identify project form -> Select governance modules
-> Implement/run -> Verify -> Deliver/release/archive -> Learn and hand off
```

Typical variants:

| Project form | Typical path |
| --- | --- |
| Software product | Requirements -> product planning -> iteration -> technical design -> development/testing -> version/deployment |
| Script/automation | Input/output contract -> implementation -> repeatable verification -> Git/version or delivery |
| Workflow/harness | Process/schema -> state and run identity -> execution/recovery -> receipt and delivery |
| Video/image/content | Source and frozen input -> production/staging -> review/acceptance -> final material -> publication/archive |
| POC | Question -> frozen input -> reproducible experiment -> evidence -> decision -> promotion or archive |

Every path must answer: Where is authority? What is current state? What can be rebuilt? How is completion verified? Where does the final result live? How is failure recovered?

Large projects should not require an agent to read the entire repository. Provide a short entrypoint and `PROJECT_MAP` that identify responsible module, authoritative path, state source, public interface, and delivery unit before reading only the task slice. Context efficiency comes from clear structure and one owner per fact, not omitted evidence.

## 4. Initialization Modules

Initialization is not merely directory creation. Select modules by project form: product projects need requirements and planning; code projects need technical, quality, and Git rules; workflow/media projects need input, state, staging, delivery, and receipt boundaries; POCs need an experiment ledger and promotion/archive conditions. Files may combine, but responsibilities and routes must remain discoverable.

The `standard` and `release` profiles create `governance/PROJECT_MAP.md` as a draft navigation owner. A core or established project may keep a sufficient README or existing equivalent. Calibrate real capabilities, responsibilities, implementation entrypoints, applicable contracts and verification under the [Index Contract](project-standard-discovery-and-on-demand-loading.md#4-index-contract). Ordinary files inherit module ownership; an existing known route does not require a map read before every edit. Update only navigation facts changed by the task. Template generation is not semantic completion, and unknown implementation or testing paths must remain explicit gaps.

Record work object, lifecycle intent, delivery model, and composition separately. Software, workflow, media, or research is the work object. Exploration/POC, pilot, production, migration, or one-off delivery is lifecycle intent. Continuous product, source distribution, versioned artifact, managed service, project deliverable, or internal process is delivery model. Composite means several work objects or delivery units; it does not make POC or mixed an exclusive project type.

## 5. Initialization Architecture Gate

Before implementing a new project, independently released/delivered unit, material subsystem, durable harness, or technical-direction rewrite, apply `architecture-constraints-and-technical-debt.md`. Confirm at least: clear boundaries, high module cohesion, necessary and explicit cross-module coupling, unique dependency direction and data/material ownership, and design complexity proportional to quality attributes.

The project-local technical design or architecture contract must record module table, allowed/forbidden dependencies, public interfaces, data ownership, side-effect boundaries, business invariants, runtime/release boundaries, key quality attributes, change triggers, check commands, and accepted debt.

Architecture diagrams are not the objective. A diagram that cannot be verified against real paths, configuration, dependencies, or tests cannot replace the contract.

## 6. Choosing Technology

Choose from the problem, not preference:

1. Identify product form, runtime, delivery, team capability, quality attributes, and existing constraints.
2. Reuse project capabilities before evaluating mature standards, frameworks, components, SDKs, or services.
3. Compare candidates by fit, maintainability, interoperability, security, license, ecosystem, observability, migration, and exit cost.
4. Small scripts, CLIs, one-off automation, and bounded offline work may use the standard library and few dependencies; do not impose an application framework for appearances.
5. Once selected, the main framework/component system is an architecture baseline. Extend compatibly for local gaps; replacement requires impact, migration, and rollback plans.
6. Use a minimum POC only when evidence is insufficient and the choice is material; preserve a reproducible experiment record.

Framework and product names are examples, never universal rules. Ecosystem-specific use belongs in project-local specialist standards or conditional references.

## 7. Governance and Delivery Strength

- G0-G1: preserve basis, impact scope, and targeted verification; avoid unrelated process.
- G2: synchronize affected documents, run matching quality/architecture/test checks, and write a work log when needed.
- G3: include relevant architecture impact and project-required verification; version, artifact, target confirmation, and rollback apply to the authorized release scope.
- G4: add affected risk-path coverage and evidence; retrospective and rule updates follow material incidents, rework, or explicit review scope.

Do not claim completion with an unmet Hard Gate. Explain omitted Soft Gates. Adapt Guidance to project facts.

## 8. Project Handoff

For an empty new project, begin with a zero-write plan:

```bash
python3 <senmu-build-project>/scripts/init_project_governance.py \
  --mode plan-new \
  --root <project-root> --project-name <name> \
  --project-type <software|script|workflow|media|poc|mixed> \
  [--lifecycle-intent <exploration|pilot|production|migration|one_off>] \
  [--delivery-model <continuous_product|source_distribution|versioned_artifact|managed_service|project_delivery|internal_process>] \
  [--publication-model <private_only|public_native|private_authority_public_projection>] \
  [--release-channel <channel> ...] [--artifact-kind <kind> ...] \
  [--composition <single_domain|composite>] \
  [--modules <product|workflow|code|architecture|git|poc|delivery|agents> ...] \
  --profile <core|standard|release>
```

When the candidate structure is selected within existing initialization authority, reuse the full command and the same explicit parameter set, changing `--mode plan-new` to `--mode initialize-new`. Add `--with-agents` or `--commit-baseline` only when the corresponding need exists.

Project type and profile are required. Without `--modules`, recommended modules for that type apply; an explicit list wins, while `--modules` alone creates a base instance without specialist modules. `initialize-new` refuses to generate default directories inside a mature project with existing content. For an existing project, run the zero-write `assess_project_governance.py --root <project-root>` first, then evolve original owners under authorization using the project-governance instance standard.

After generation, run structural validation, calibrate placeholders, change policy status to `active`, then run the copied `python3 .senmu-buildos/validate.py --root . --strict`. Use `core` for small exploration: it creates only README, AGENTS, governance charter, machine policy, and one validation entrypoint, not tasks, logs, lessons, or specialist documents. Combine those responsibilities in current entrypoints until durable collaboration justifies `standard`. Use `release` for formal publication, deployment, or stable delivery, while tailoring documents and directories to reality; a template is not completed design.

`--commit-baseline` is only for an empty new project or recovery of the initializer's own draft. It runs non-strict structural validation, stages only known initializer-managed files, and creates a governance-skeleton baseline commit. It never runs `git add .`, creates a tag, handles an established project, or commits through a Hook. If Git identity is missing or the index already contains staged content, it skips the commit and reports why.

Use `--with-agents` only when the project maintains its own agents/system prompts. It adds an Agent Register, definition template, and validator but invents no business agent. Using AI to develop an ordinary software, script, or content project does not enable this module automatically.

After initialization/calibration, the project must make these facts directly discoverable; files may combine, responsibilities may not disappear:

- Project form, current objective, authoritative entrypoint, applicable constraints and the requested delivery outcome.
- For actual multi-step or cross-session work: the existing task state and unresolved next steps; immediate small work need not create a task system.
- For enabled Product work: requirements, terminology and acceptance ownership.
- For real code modules: capability-to-implementation, contract and verification routes; use a combined README for a small core project when sufficient.
- For architecture decisions that need durable explanation: the existing technical owner, selected baseline and relevant rationale. No empty ADR or debt register is required.
- For code/tooling: actual quality commands and applicable language/framework guidance, loaded only for the current need.
- For files/media: real input, work, temporary, delivery and recovery locations with applicable retention; do not invent unused resource roles.
- For enabled project-owned agents: their registry/definition/runtime relationship. Using an AI to code does not by itself enable this module.
- For Git work: actual repository and permitted worktree/branch/integration rules.
- For formal delivery in scope: release/delivery identity, artifact, target verification and recovery ownership.
- For meaningful history or reusable learning that actually exists: the existing log and lesson routes, without creating blank parallel ledgers.


Prefer short entrypoints routing to authority, machine-readable configuration, and one validator. Do not duplicate long standards.

## 9. Completion Definition

Before delivery, confirm:

- The result is in the authoritative project and correct release unit, not only a temporary directory or chat.
- No unexplained conflict exists among input, rules, implementation/runtime, state, verification, and deliverables in enabled modules.
- Risk-proportional verification ran, with actual results, omissions, and residual risk recorded.
- When formal delivery/release is within the authorized outcome, it has its required identity, evidence and recovery basis. A navigation-only or source-only task does not acquire deployment obligations or permission by entering closeout.
- Project-specific learning updates project standards only. A concrete BuildOS component and reviewable harm suffice for feedback intake through `senmu-build-learning`; promotion to a general rule requires cross-project evidence or a stable mechanism affecting multiple project types, without disproportionate burden.

## Minimum Technology Baseline

Before sustained software implementation without a current baseline, route the technical decision to Engineering's [Technology Selection](../../senmu-build-engineering/references/technology-and-component-selection.md#5-baseline-and-incremental-extension). Project records the owner and route, not a competing technical decision. An explicit plan-and-initialize request continues after the zero-write plan unless an unresolved outcome-changing choice or uncovered authority remains. One-off scripts and bounded prototypes use a provisional minimum baseline with limits and revisit triggers; do not create speculative architecture modules.
