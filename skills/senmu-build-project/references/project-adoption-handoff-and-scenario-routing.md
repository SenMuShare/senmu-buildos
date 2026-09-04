# Project Adoption, Handoff, and Scenario Routing

Use this standard to keep Senmu BuildOS from becoming overhead after project adoption. BuildOS is a conditionally invoked governance baseline; the project entrypoint is its delta layer. A project records real facts, authoritative entrypoints, executable commands, project-specific rules, and explicit overrides—not copies of BuildOS prose.

## Navigation

1. Lifecycle entry; 2. Project form and modules; 3. Adoption artifacts; 4. Post-adoption invocation; 5. Scenario routing; 6. Minimum deliverables; 7. Rule precedence; 8. Executable-contract handoff; 9. Anti-bloat maintenance.

## 1. Project Situation and Lifecycle Entry

Choose the entrypoint from the current situation; do not create four separate Skills:

| Situation | Correct entry | Prohibited behavior |
| --- | --- | --- |
| New project not started | Confirm objective, form, and real delivery method; generate a zero-write initialization candidate; create minimum owners after user approval | Generating a full directory/document/branch/release system before scope confirmation |
| New project in normal development | Read adopted requirement, code, quality, and delivery entrypoints; invoke one matching specialist owner for the task | Reinitializing or rereading all BuildOS material for every requirement |
| Existing project continuing development | Inherit existing facts, current development version, and registered task/branch; complete incremental work directly when rules suffice | Rebuilding directories, Git, documents, or governance merely because the project is old |
| Existing project receiving whole-project governance | First inventory authority, structure, quality, and delivery facts read-only; evolve original owners only within approved scope; use mature-project takeover governance for multi-stage work | Overwriting reality with defaults or mixing governance and ordinary feature work into an unbounded rewrite |

After initialization, write project facts and project-specific contracts into existing README, AI entrypoint, code/architecture, requirement, process, and delivery owners. Do not copy methods identical to BuildOS. Daily work follows project entrypoints. Return to BuildOS calibration only when rules are missing, conflicting, stale, or the user explicitly requests whole-project governance.

## 2. Project Form and Module Selection

Project form selects defaults; it does not constrain the project. Choose the primary form, then add secondary modules:

| Project form | Default modules | Usually unnecessary |
|---|---|---|
| Software product/service | Requirement planning, architecture/code, Git, testing, release/deployment | Media-material directories |
| Script/CLI/automation | Input/output, code quality, Git, repeatable verification | PRD, roadmap, iteration |
| Workflow/Codex harness | Process contract, state source, run identity, recovery, receipts, material delivery | Product version unless externally released |
| Video/image/content production | Source, staging, review, final material, publication state, archive | Software architecture documents unless code complexity requires them |
| POC/research | Experiment question, frozen input, evidence, decision, promotion/archive | Formal release process |
| Composite | Relevant modules with separate release/delivery units | One ambiguous version for everything |

When the actual project includes code, databases, media, external assets, or formal release, add each corresponding module. Real risk and delivery determine module selection, not directory names.

## 3. Adoption and Handoff Artifacts

After initialization, the project needs at least one internal entrypoint telling later agents where rules live.

For a BuildOS project, `AGENTS.md` or its equivalent is the **Project Delta Layer**, not a copy of BuildOS. It locates project facts and commands but need not reproduce the full governance method when BuildOS is absent. Before removing BuildOS, migrate any still-needed rules to a new authoritative baseline.

Suggested owner paths:

```text
AGENTS.md or equivalent AI entrypoint
README.md
engineering/CODE_QUALITY.md
engineering/SYSTEM_TECHNICAL_SPECIFICATION.md, established architecture owner,
  or an as-needed TECHNICAL_DESIGN.md
engineering/TECH_DEBT.md                 # only when real debt exists
engineering/languages/<LANGUAGE>.md
governance/GOVERNANCE.md
.senmu-buildos/config.json
governance/tasks/TASK_REGISTER.md
.senmu-buildos/templates/TASK.md
delivery/BRANCHING.md
delivery/RELEASE_PLAN.md
governance/logs/WORKLOG.md
governance/lessons/LESSONS_LEARNED.md
operations/DEPLOYMENT.md
engineering/TESTING_STRATEGY.md
```

A small project may combine files, but must answer:

- What is the project and its current scope?
- Where are requirements and technical design?
- Where are quality rules, current language standards, and the unified check command?
- Where are module responsibilities, dependency direction, data ownership, architecture checks, and debt?
- How do local startup, tests, and deployment work?
- How do branches, versions, changelog, release, and rollback work?
- Where do POCs live, are they in Git, how are they retained/backed up, and what validates them?
- What changed recently, which failure modes must not recur, and which command detects them?
- Which files should a later agent read first?
- Which tasks require durable tracking, what is each status, and where does recovery start?

## 4. Invocation After Adoption

When project owners provide the facts, rules, and commands needed for the current task, execute directly and stop governance routing. “Read the project first” does not mean rereading all BuildOS text.

Load one matching Skill and only necessary references when the work establishes or changes a durable governance decision and project rules are missing, conflicting, clearly stale, or governance/review is explicitly requested. Continue obeying clear, effective project controls for high-risk work. When controls are missing or conflict, fill only the specialist gap; do not compose every Skill automatically.

Ordinary implementation, bug fixes, code explanation, a single copy edit, local styling under clear design rules, and execution of an established process do not invoke BuildOS by default. If implementation exposes a real Product, Design, Engineering, Workflow, Delivery, or Project contract gap, route to the single primary Skill below.

## 5. Specialist Routing When BuildOS Is Needed

| Result to establish or change | Primary Skill | Boundary |
| --- | --- | --- |
| Project initialization, structure, authority mapping, governance migration, or cross-stage state owner | `senmu-build-project` | Project-governance instance only; daily use of an existing task system does not trigger |
| Durable product scope, version placement, priority, acceptance, or cross-page content standard | `senmu-build-product` | A contract-preserving copy edit or ordinary clarification does not trigger |
| Visual direction, design system, layout, responsive behavior, interaction, motion, accessibility, or UI/UX review | `senmu-build-design` | Ordinary implementation under clear design rules does not trigger; component APIs remain with project/specialist Skills |
| Workflow contract, project agent, material flow, receipt, or recoverable run state | `senmu-build-workflow` | Executing an established process does not trigger |
| Engineering contract, architecture, testing strategy, technical debt, or refactoring rule | `senmu-build-engineering` | Trigger only when project rules are missing, conflicting, changing, or governance is explicit |
| POC, independent audit, reproduction, or disputed-cause verdict | `senmu-build-assurance` | Trigger for an evidence-based independent conclusion; it does not implement the fix |
| Open development batch, non-routine Git boundary, version, artifact, deployment, rollback, or production state | `senmu-build-delivery` | Ordinary implementation inside a governed batch does not trigger; keep unreleased unless release is explicit |
| BuildOS feedback adjudication, formal retrospective, lesson promotion, or distillation of external guidance | `senmu-build-learning` | Ordinary user corrections and project business requirements do not enter the feedback inbox |

When any scenario spans dependent steps, phases, agents, or sessions, follow [Task Execution, Planning, and State Management](task-execution-and-state-management.md) using the project's declared Durable Task State Owner. Specialist documents own domain facts; task state owns current boundaries, progress, evidence links, and recovery. Neither replaces the other.

## 6. Minimum Deliverables

| Level | Minimum deliverable |
| --- | --- |
| G0 | Basis, key assumptions, and suggested next step |
| G1 | Change, impact scope, and verification or disclosure of omissions |
| G2 | Change, matching tests, necessary document sync, necessary work log |
| G3 | Version, changelog, release/deployment record, production verification, rollback point |
| G4 | Risk treatment, verification evidence, retrospective, and rule update or reason not to update |

## 7. Project Rule Precedence

When project rules and Senmu BuildOS differ:

- Real runtime/delivery evidence and active specialist owners determine project facts; explicit project overrides beat BuildOS defaults.
- Semantically identical rules are not conflicts. Remove the project copy and retain the BuildOS baseline; the project entrypoint may retain authoritative paths or real commands.
- If a project rule appears stale, project owners conflict, or an override weakens a non-negotiable BuildOS Hard Gate, do not guess. Present the specific conflict, evidence, impact, and recommendation to the user for decision.
- After decision, update one project specialist owner and retain only necessary navigation or override in the delta layer. Never maintain synonymous bodies in several files.

## 8. Executable-Contract Handoff

Durable repetitive production, release, data-processing, content-generation, or material-processing chains need more than a human-readable SOP. After repeated agent rework or owner correction on the same chain, hand project rules over as an executable contract.

Apply the same principle to source quality and architecture boundaries: use a short AI entrypoint to route to authority; express machine facts through architecture contracts, debt registers, ecosystem-standard configuration, and one quality command; reuse that contract locally, before commit, and in CI.

The minimum handoff includes:

- one public entrypoint or clear project-type routing entrypoint;
- one machine-readable policy/config/schema recording the current standard and version;
- entry scripts, database/ledger, intermediate manifest, or release plan carrying that policy/config/schema ID;
- one doctor or validator command checking consistency among entrypoint, configuration, scripts, ledgers, and artifact fields;
- for POCs, the policy also registers one `POC_ROOT`, `tracking_mode`, retention level, backup strategy, and forbidden destinations; the validator tests physical ownership from an external-worktree counterexample and scans historical residue;
- one legacy rule stating when old scripts, caches, artifacts, demos, and releases are historical-only and cannot seed new work by default.

Only with these elements has a rule moved from chat/document memory into a project capability that later agents can execute reliably.

## 9. Anti-Bloat Maintenance

When maintaining Senmu BuildOS:

- Extend an existing reference first; add a file only when a new topic cannot fit naturally.
- Every new reference must be directly discoverable from `SKILL.md`.
- Never put private project SOPs, customer information, server paths, or commercial details in a general Skill.
- Never copy BuildOS prose into project `AGENTS.md`, business agents, or specialist documents; projects retain only deltas, facts, paths, and commands.
- Keep deep technology/vendor documentation as conditional attachments, outside the entry flow.
- Prefer official tools for ecosystems with an official MCP/CLI, such as Ant Design. Keep vendor material for ECharts, players, or editors as small summaries, metadata, or out-of-project snapshots. If a topic warrants a durable frontend/admin specialist Skill, Engineering should retain only principles and routing.
- After each version update, check whether entrypoints grew heavier, rules were duplicated, or governance levels still constrain trigger scope.
