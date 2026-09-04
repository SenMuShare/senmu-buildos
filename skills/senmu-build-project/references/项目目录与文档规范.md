# Project Directories and Document Ownership

Use this standard to select project roots, path roles, document owners, and project maps without imposing one shape. Map established structures first; candidate names never justify parallel directories.

## 1. Boundaries and Roles First

Before layout, confirm the authoritative project root; Git repositories and subprojects/external workspaces; work object, lifecycle, delivery model, release units; source input, run state, intermediates, deliverables, evidence, archives; existing domain owners; and real build, test, deploy, recovery, and release entrypoints.

Code, media, databases, artifacts, and runtime state may occupy different physical roots, but a short project map must relate them. Do not infer authority by searching upward for `Makefile` or `package.json`.

## 2. Optional Layouts

Software/composite projects may begin with roles such as:

```text
project-root/
  README.md / AGENTS.md / .senmu-buildos/
  product/ engineering/ workflows/ governance/
  delivery/ operations/ projects/ scripts/ tests/
```

A subproject is a release unit only when it builds, deploys, and rolls back independently with distinct responsibility. Version frontend/backend together when cadence is shared; when independently released, register each artifact, command, health check, and rollback.

Content, media, data, or mixed projects may use:

```text
project-root/
  project-system/  # sole Git project system
  sources/         # immutable inputs
  workspace/       # intermediates and run state
  deliveries/      # accepted deliveries
  archive/          # history and closed work
```

Keep existing numbered Chinese paths, `inputs`, `staging`, `outputs`, or `receipts`; map their roles. Git project systems do not imply tracking large media, production databases, caches, or outputs. Small projects may combine files. Do not prebuild unconfirmed modules.

## 3. Entrypoints and Project Map

- `README.md`: identity, startup, primary applications/services, key entrypoints.
- Root `AGENTS.md`: under BuildOS, project differences, real commands, authority paths, explicit overrides only; never copied BuildOS/domain standards. Subdirectories may add narrower delta layers.
- `.senmu-buildos/config.json`: governance-instance identity, layout, modules, relocatable location.
- `governance/PROJECT_MAP.md` or equivalent: routes owners, state sources, commands, release units, legacy boundaries without copied bodies or current mutable state.
- Project agents get a register and sole definition only when actually enabled. Skill `agents/openai.yaml` is not a business agent.

Runtime evidence and the nearest active domain owner determine project facts. Explicit project overrides beat BuildOS defaults. Ask the user when freshness is unknown, several owners conflict, or an override would weaken a non-negotiable Hard Gate.

## 4. Domain Owners

| Fact | Default owner |
| --- | --- |
| users, requirements, business rules, roadmap, acceptance | Product |
| architecture, design, quality, language, testing, debt | Engineering |
| Workflow Contract, Run Manifest, material, recovery | Workflow |
| Git, version, tag, artifact, deployment, production, rollback | Delivery/Operations |
| cross-stage plan and recovery entrypoint | existing Durable Task State Owner |
| review findings, POC evidence, re-review | Assurance |
| feedback candidates, lesson lifecycle, rule-promotion index | Learning |

Project selects owners, paths, and index relationships; it does not copy domain writing rules. Update equivalent owners in place and do not create empty ledgers.

### Default Product/Technical Roles

For new product projects, create version paths only after the actual version is known:

```text
product/USER_REQUIREMENTS.md
product/PRODUCT_SPECIFICATION.md
versions/<version>/PRD.md
versions/<version>/TECHNICAL_DESIGN.md       # optional
versions/<version>/TEST_CASES.md             # PRD-derived, risk-proportional
engineering/SYSTEM_TECHNICAL_SPECIFICATION.md
```

Paths provide navigation; document sections are adaptable outlines. Initialization must not create empty PRDs, technical designs, test cases, roadmaps, iterations, or review ledgers for unknown work. Map established owners first, then add current specifications and future-version structure incrementally.

## 5. Minimum Document Responsibility

A durable project must make discoverable: identity and real commands; current requirements/goals and acceptance; architecture/implementation boundaries and quality entrypoints; workflow input/state/output/recovery; release units and production rollback; and cross-stage task scope, progress, evidence, and next entrypoint. These need not be separate files or identical sections.

Plans, candidates, frozen references, history, and current documents cannot impersonate one another. State, applicable release unit/version/delivery ID, and calibration evidence must match use. A local fix reviews only affected owners; it does not mass-update unrelated documents for a version advance.

Keep high-churn facts—version, commit, candidate/production state, policy ID, calibration time—in one machine-readable owner. Other documents reference it, retain only unique explanation, or form reproducible projections through declared generation/validation. Never hand-edit unrelated bodies for duplicate headers or let projections become authority.

Synchronize on contract change: behavior/acceptance -> Product; modules/interfaces/data/dependencies/infrastructure/permissions/security -> Engineering; run steps/recovery -> Workflow; version/deployment/production/rollback -> Delivery. For contract-preserving implementation changes, update tests, necessary comments, and the project's minimum record only.

## 6. Security and Public Boundary

Git excludes real secrets, production data, uploads, runtime databases, caches, and unauthorized material. Commit configuration templates; store values in approved local/secret systems.

Private authority projects to public repositories through a one-way allowlist. The public repository is a reproducible release surface, not an editable second owner. Internal tasks, logs, customer data, run state, absolute paths, and private assets never enter it. Regenerate public revisions through the authority lifecycle.

A governed layout must answer authoritative root, owner of each fact, minimum reading for the task, real commands, delivery entrypoint, and recovery entrypoint.
