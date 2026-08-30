# Senmu BuildOS — Project Governance for AI Coding Agents

🌐 **Documentation languages:** [简体中文](./README.md) | **English** | [日本語](./README.ja.md)

> Help Codex, Claude Code, and Doubao make fewer mistakes, avoid rework, preserve context, and deliver with evidence.

[![Validate Senmu BuildOS](https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml/badge.svg)](https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/SenMuShare/senmu-buildos)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/SenMuShare/senmu-buildos?style=social)](https://github.com/SenMuShare/senmu-buildos/stargazers)
[![Release](https://img.shields.io/github/v/release/SenMuShare/senmu-buildos)](https://github.com/SenMuShare/senmu-buildos/releases/latest)

Senmu BuildOS is an open-source **project governance plugin for AI coding agents**. It packages project management, product requirements, software engineering, Git collaboration, assurance, releases, and feedback into seven Skills that load only when relevant. Agents inspect the real project before changing it instead of relying on an ever-growing prompt.

It is not a traditional project-management app, and it does not force mature repositories into one directory template. It currently supports **OpenAI Codex**, **Claude Code**, and **Doubao**.

## From agent chaos to sustainable delivery

| Common problem | What BuildOS changes |
| --- | --- |
| Agents create new folders or duplicate features without reading the codebase | Inspect the project root, existing implementation, and semantic owner before deciding to reuse, extend, or create |
| A new session or agent needs the whole project explained again | Keep progress, decisions, evidence, and recovery points in project-owned durable state |
| Requirements, code, tests, and docs drift; retired behavior comes back | Track current requirement authority and close replacement, cleanup, and regression proof as one change |
| POCs, hotfixes, long-running branches, and releases block one another | Govern Git branches, worktrees, release candidates, and explicit exclusions by real scope |
| “The command passed” becomes “it is finished” or “it is live” | Separate implementation, acceptance, artifacts, release, and production truth with matching evidence |
| Skills and prompts grow while tokens are spent rereading irrelevant rules | Load seven professional Skills by task, reducing irrelevant context, repeated reminders, and re-explanation |

## Translate product intent into Git behavior

People should not need to learn branches, worktrees, rebases, or cherry-picks before they can build with an AI Agent. State the product intent instead:

> Keep maintaining the current version; start a long-running successor; treat these notes as one batch; integrate them but do not publish yet; release after verification.

BuildOS translates that intent into engineering actions. Every source change uses a task branch; concurrent writers receive isolated worktrees; continuous feedback stays in one open result; long-running replacements use a successor line; and any Agent can close out completed work without a permanent team lead.

A project keeps one current main line and declares whether it is always release-ready or is a continuous integration line. Production is never guessed from the newest `main`; it is established by a frozen commit, artifacts, and a real release record. A formal Tag is created only after the target release has been verified. Before that point, the candidate is frozen by commit, candidate identity, and artifact identity. “Do not publish yet” remains an authorization constraint across sessions and commits.

## Start in 30 seconds

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
```

For Claude Code:

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
```

For Doubao, clone the repository and run the adapter installer:

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos && python3 adapters/doubao/install_doubao.py
```

Refresh the tool and start a new conversation after installation. See [Install, update, and remove](#install-update-and-remove) for updates, removal, and Hook trust guidance.

**Quick navigation:** [What it solves](#from-agent-chaos-to-sustainable-delivery) · [What makes it different](#what-makes-buildos-different) · [Install and update](#install-update-and-remove) · [How it works](#how-it-works) · [Seven Skills](#one-plugin-seven-peer-skills) · [Current boundaries](#current-boundaries)

## What makes BuildOS different

1. **Designed for agent work.** BuildOS is used directly by AI agents and agent harnesses. People retain goals, judgment, and authorization; agents receive an executable, recoverable, and verifiable contract for project work.
2. **Governs the full project lifecycle—not only code generation.** From initialization and requirements through implementation, workflows, testing, delivery, production truth, and organizational learning, every durable fact has a clear home.
3. **Respects mature projects instead of forcing a directory template.** It first inspects existing entrypoints, repositories, state sources, and delivery boundaries without writing. Defaults serve new projects; established projects evolve their original owners.
4. **One plugin, seven peer professional Skills.** Project, Product, Workflow, Engineering, Delivery, Assurance, and Learning route by objective. There is no mandatory “master agent” that loads the entire system for every task.
5. **Moves memory out of chat and back into the project.** Long-running work uses durable state, stable identifiers, evidence links, and recovery entrypoints. A chat may end; the project must not forget.
6. **Turns completion into a verifiable fact.** Passing tests, producing an artifact, completing a deployment, and serving a healthy production system are different states, each requiring the right evidence.
7. **Scales rigor with risk and improves the source of failure.** Small tasks stay lightweight; high-risk releases and data operations remain fail-closed. Gates cover only material residual risk that cannot yet be removed at the source.
8. **Acts as an engineering coach, not a directory police.** Agents inspect the real situation and authorization first, classify the current scenario, then recommend a preferred path, rationale, acceptable alternatives, and closure conditions instead of substituting one fixed directory, branch model, or long checklist for professional judgment.
9. **Respects user intent without echoing unverified conclusions.** The user decides goals, preferences, and authorization; the agent separates desired state, fact, inference, and recommendation, then forms an independent judgment from project evidence and applicable authoritative external knowledge, stating uncertainty when evidence is insufficient.
10. **Closes release resources and execution surfaces together.** By default, keep the verified current version and one verified rollback version, while honoring an explicit project policy. Check the build host, runtime host, remote artifact store, and included Git branches/worktrees separately instead of substituting a global prune for project-level closure.
11. **Acts as the translator between people and Git.** Users describe versions, batches, integration, and release intent; BuildOS chooses branches, worktrees, intake, candidates, and Tags while keeping the technical safety burden inside the system.

## How it works

```text
Understand the real project → Map facts and owners → Select the primary Skill
      → Execute and persist state → Verify with evidence → Deliver or release
      → Learn and feed improvements forward
```

This is not a rigid pipeline that every task must traverse. BuildOS selects only the steps justified by project shape, objective, and risk: a small change can move directly into implementation and verification; a large requirement keeps separate specifications, plans, task state, and acceptance; a mature project is assessed before it evolves; stronger gates appear only for higher-risk delivery.

## Open iteration flywheel

Senmu BuildOS can be used directly as a plugin or cloned and forked as a complete source project. In your own branch, you can continuously absorb useful guidance from web pages, PDFs, books, public repositories, or third-party Skills, then keep the result private or contribute it upstream through a Pull Request.

```text
Install a release or fork the source
      → Open a short branch and form a distillation batch
      → Read → extract candidates → deduplicate/adjudicate → update one owner → verify
      → Keep using locally, or submit a Pull Request
      → Maintainers review, re-distill, merge, and publish a new release
```

There is no magic phrase to remember. Give the agent the material and desired outcome directly, for example:

> Read this web page, PDF, repository, or Skill and absorb the reusable engineering rules into my BuildOS. Merge duplicates, reject inapplicable material, do not retain a raw source library, and prove the improvement through the repository's existing validation entrypoints.

> Create a short branch in my fork, apply the BuildOS knowledge-distillation workflow, validate the improvement, and prepare a Pull Request. Do not push or publish without my authorization.

`clone` downloads the repository for local study or modification; a `fork` is your long-lived GitHub copy; a `branch` isolates one improvement; a Pull Request contributes a mature candidate upstream. External material and community contributions remain untrusted candidates until source and license review, deduplication, conflict adjudication, owner mapping, behavioral tests, context-budget checks, and full-repository validation succeed. See the [contribution guide](CONTRIBUTING.md#开放迭代飞轮贡献流程) for the executable workflow.

## Who is it for?

- Individuals and teams using Codex or Claude Code as a continuing participant in real projects, not merely as a one-off code generator;
- projects that must continue complex work across sessions, agents, or tools;
- established codebases with substantial history, scripts, directories, and facts where a second system would cause harm;
- mixed projects spanning software, automation, data, content, media, POCs, or several delivery types;
- serious delivery environments that must distinguish “attempted,” “tested,” “delivered,” “released,” and “healthy in production.”

If you have watched an agent duplicate files, lose context, disrupt an existing project, or call a successful command “done,” **Star** or **Watch** this repository to follow future BuildOS releases and evolution.

## Current status

The current formal release is Senmu BuildOS `v2.0.2`. **Codex and Claude Code** share the same seven peer Skills and have separate plugin manifests, marketplaces, and lifecycle Hook adapters; **Doubao** uses the same Skills with a separate bootstrap adapter (`adapters/doubao/`) installed as hook-less user Skills. None of the adapters changes user-wide configuration or project files, and none accesses the network. Feedback capture writes only high-signal candidates to local `~/.senmu-buildos/feedback/` and exposes no internal marker or ID in normal answers. Installation, enablement, and removal remain explicit user actions.

## Install, update, and remove

### Install on Codex

You need a Codex build that provides the `codex plugin` commands, plus Git access to GitHub. Senmu BuildOS installs as one plugin; its seven Skills do not need to be downloaded separately.

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

After installation, restart or refresh Codex and begin a new conversation. When enabling the plugin for the first time—or whenever its Hook changes—review and trust the Hook in Codex. Downloaded files alone do not prove that a Hook is active.

### Install on Claude Code

Use a current Claude Code release that provides `claude plugin`:

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
claude plugin list
```

Plugin Skills use the `senmu-buildos:` namespace, so they do not replace existing user Skills. Run `/reload-plugins` after installation if needed. The adapter registers `SessionStart`, `SubagentStart`, and `UserPromptSubmit`; it requests no additional tool permissions and does not modify `~/.claude` or project files. `UserPromptSubmit` writes only explicit corrections or submission actions to the local review inbox.

### Install on Doubao

Doubao has no plugin manifest or lifecycle Hook: Skills are plain folders under `workspace/.user_skills/`. Two options:

**Option A — hand the repository to Doubao (recommended if you are not comfortable with the command line).** Paste the repository URL into a Doubao conversation and ask it to read `adapters/doubao/README.md`, then copy the seven `senmu-build-*` Skills and the `senmu-build-kernel` bootstrap from `skills/` and `adapters/doubao/kernel/` into Doubao `.user_skills` (excluding Codex-only `agents/` metadata), and write an install identity. See [the Doubao adapter](adapters/doubao/README.md).

**Option B — clone and run the installer.**

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/doubao/install_doubao.py --dry-run   # preview, zero writes
python3 adapters/doubao/install_doubao.py             # install into Doubao .user_skills
```

The installer copies the seven Skills and the `senmu-build-kernel` bootstrap into `.user_skills/` (stripping Codex-only `agents/` metadata) and writes `.senmu-buildos-install.json`. Because Doubao has no Hook, the governance kernel cannot be force-injected every session; `senmu-build-kernel` provides it on demand. Re-running the installer updates the install.

### Update on Codex

Codex does not automatically watch a local source directory or GitHub commits. It updates the **Senmu BuildOS plugin** as a unit; it does not track seven independent Skill versions. Every formal release aligns `VERSION`, the plugin manifest, Git Tag, Release, and Marketplace target. Refresh the Marketplace and reinstall the plugin:

```bash
codex plugin marketplace upgrade senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

Then restart or refresh Codex and start a new conversation so it reloads the Skill inventory and Hooks. Public users should install formal releases only. If you modify the source locally, validate the repository-wide impact and give candidate installs a local prerelease version or build identifier distinct from the formal release, preventing Codex from reusing a same-version cache.

### Update on Claude Code

```bash
claude plugin marketplace update senmu-buildos
claude plugin update senmu-buildos@senmu-buildos
claude plugin list
```

The maintainer flow for unified version preparation, Tag validation, and Release artifacts is documented in the [contribution guide](CONTRIBUTING.md#正式版本准备). The release script prepares metadata only; it never creates a Tag or bypasses release authorization.

### Remove

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

### Give the repository directly to Codex

You can also give Codex the repository URL with this prompt. It explicitly asks the agent to inspect the external code before installation:

> Install `https://github.com/SenMuShare/senmu-buildos` as a Codex plugin. First review `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `skills/`, and `hooks/`; then follow the README to add the Marketplace and install the plugin. Remind me to review Hook trust, and report only the version actually installed and its enabled state.

For Claude Code, replace “Codex plugin” with “Claude Code plugin” and ask it to review `.claude-plugin/`, `adapters/claude-code/`, `skills/`, and the bounded local feedback write, no-network, and no-user-configuration-change boundaries.

### Give the repository directly to Doubao

Doubao users can paste the repository URL (or this README) into a Doubao conversation and let Doubao install. There is no plugin manifest or Hook; the install path is to read `adapters/doubao/README.md` and copy the Skills into `.user_skills`:

> Install `https://github.com/SenMuShare/senmu-buildos` as Doubao user Skills. First read `adapters/doubao/README.md` and `adapters/doubao/install_doubao.py` to understand the adapter and install logic; then copy the seven `senmu-build-*` Skills from `skills/` and the `senmu-build-kernel` bootstrap from `adapters/doubao/kernel/` into Doubao `.user_skills` (excluding `agents/` and `__pycache__`), and write `.senmu-buildos-install.json`. Report only the Skill list and version actually installed.

## Core design philosophy

- **Create the minimum governance instance for a new project proactively:** When a user explicitly asks to create or start a project, the agent treats project classification, the authoritative entrypoint, the minimum directory structure, and recovery as normal startup work. The user does not need to name each document individually. “Proactively” means acting after the task is triggered, not letting a SessionStart Hook silently modify arbitrary directories.
- **Identify mature projects before evolving them:** First perform a read-only review of the real entrypoints, owners, state sources, and delivery boundaries. Then, with authorization, repair missing, conflicting, duplicated, or outdated structures. Do not build a second directory and fact system beside a mature project merely to fit a template.
- **Make exhaustive source governance auditable:** Enable exhaustive mode only when the user explicitly asks for it, then inventory every first-party source file, function or method, and existing comment. Any unreviewed unit blocks completion, and full review coverage is verified separately from post-remediation conformance.
- **Close daily code quality before merge:** Individual work-in-progress commits do not each need a separate review, but every complete code change set entering the integration baseline must be reviewed down to its changed files, functions or methods, and comments before merge. Approval binds the exact `base..head`, becomes stale after any new commit, and release only verifies that review evidence and artifact identity.
- **Discover project rules from real evidence and load them on demand:** For a mature project, derive stable rules from entrypoints, implementation, configuration, tests, and runtime evidence. Write complete rules back to their original professional owner, and use only a short index to help the agent choose what to load for the current task. Do not create a second rules library or inject every rule into context.
- **Give project Agents one authoritative contract:** Enable the Agent Definition System only when a project genuinely maintains custom Agents or system prompts. Connect real Workflows and Harnesses through an Agent Register, stable keys and versions, one definition per Agent, and deterministic validation. Root `AGENTS.md` remains the Codex project entrypoint, while a Skill's `agents/openai.yaml` remains presentation metadata.
- **Follow a reuse ladder before implementing:** First decide whether implementation is necessary. Then check existing project capabilities, the standard library, platform-native features, current dependencies, and mature open-source solutions. Write the smallest clearly bounded custom implementation only when a real gap remains.
- **Close the value loop before polishing infrastructure:** Establish a runnable, verifiable, deliverable minimum value loop first, then strengthen it in stages using real feedback. Scaffolding, abstractions, general platforms, checklists, and gates must not remain ahead of the core path indefinitely.
- **Improve flow at the source:** Prefer fixing the requirement, responsibility, architecture, interface, data owner, default, implementation, or production process that creates a problem. Gates should cover only material residual risks that cannot yet be removed at the source. Safety, privacy, permissions, payments, production data, destructive operations, and formal release integrity still require fail-closed protection.
- **Close resources as part of release:** A formally deployed project keeps the verified current version and one verified rollback version by default, while an explicit project policy takes precedence. The `release` profile initializes project-scoped retention settings, precise artifact or image cleanup scripts, and contract tests. After production verification, the single release entrypoint closes the runtime host, build host, optional remote artifact store, and included Git execution surfaces separately, without relying on agent memory or a global prune.
- **Treat context efficiency as architecture:** A single source of truth, short entrypoints, clear owners, on-demand Skills, task slicing, and durable state reduce rereading, repeated prompting, token consumption, and ambiguity during multi-agent handoff.
- **Feed validated lessons into a flywheel:** Hooks capture explicit corrections, rework, and regressions. When an agent discovers a high-signal gap, it may submit silently through the local CLI; normal answers expose no internal marker or candidate ID. Both paths create review candidates only. The user triggers Learning to batch-deduplicate, verify, and disposition them. A project first closes its own problem; only authorized cross-project candidates enter the BuildOS source repository for repository-wide impact analysis instead of automatically rewriting a Skill after one report.

## BuildOS and the Project Governance Instance

Senmu BuildOS provides project architects and AI agents with general methods, decision criteria, default implementations, and professional playbooks. It is not the PRD, technical design, or runtime ledger of any particular project. Each project should form its own **Project Governance Instance**, grounding the applicable principles in that project's entrypoints, directories, owners, state sources, quality commands, and delivery evidence.

```text
Senmu BuildOS: general principles, professional methods, defaults, decision criteria
                                  ↓ calibrate
Project Governance Instance: project-specific selection, mapping, and evolution
                                  ↓ operate
Local requirements, code, task/run state, validation, delivery, and release facts
                                  ↓ feed back after validation
The next general evolution of Senmu BuildOS
```

A governance instance standardizes responsibilities and semantics, not physical shape. A large software product may use PRDs, architecture contracts, and a release system. A small script may combine those responsibilities in its README, tests, and version history. A mature workflow may keep task packages, databases, manifests, Makefiles, and receipts as owners. Stable knowledge about Python, TypeScript, Go, Java, frontend frameworks, and general code quality remains available from BuildOS on demand; each project records only its own choices, constraints, entrypoints, exceptions, and validation commands.

### Two kinds of authority

- **Fact authority:** Project-local code, documents, databases, runtime state, and release receipts describe what the project currently is. Default templates must not override real facts.
- **Governance standard:** BuildOS assesses whether the current fact chain is complete, clear, recoverable, verifiable, and evolvable. A rule is not automatically correct merely because it already exists. Missing, conflicting, duplicated, outdated, or non-portable owners should be governed at the source after authorization.

Respecting a mature project does not mean freezing it. Identify the current state, define the target instance and migration boundary, then upgrade, merge, or complete the original owners instead of establishing a long-term parallel system.

## Source project and installed runtime

In GitHub and Git, Senmu BuildOS is one complete, independent product project. Its plugin manifests, all Skills, Hooks, documentation, scripts, and tests form one source repository and one release unit. Codex and Claude Code both install the complete plugin and expose its seven Skills as on-demand entrypoints. The Skills are not seven separately versioned products.

Every BuildOS improvement therefore begins with a repository-wide impact check. The final change may affect only one Skill, one Markdown file, or one script, but adjacent owners, routing, templates, Hooks, tests, and release metadata must still remain aligned. Application-project learning, BuildOS source changes, candidate installation, and public release each have independent states and authorization; none can impersonate another as complete.

### Five project capabilities

| Capability | Applies to | Behavior |
| --- | --- | --- |
| Recommend Placement | One document, directory, or responsibility | Recommend a primary existing owner/path, rationale, and alternatives without creating anything merely because advice was requested |
| Plan / Initialize New Project | An empty or explicitly new project | First produce a zero-write plan from explicit classification, profile, and modules; generate only the reviewed instance after authorization |
| Assess Existing Project | An existing project | Inventory authoritative entrypoints, release units, candidates, and excluded evidence with zero writes, then semantically confirm owners, gaps, conflicts, and migration risks |
| Evolve Existing Project | A reviewed project with explicit authorization | Complete missing owners, resolve conflicts, merge duplicates, migrate non-portable paths, and verify recovery within the original authority structure |
| Govern a Mature Project | A historically tangled project needing cross-stage takeover | Link a read-only baseline, finding decisions, user authorization, remediation waves, re-review, recovery, and temporary-artifact disposition through one durable task owner |

`senmu-build-project` provides zero-write `--mode plan-new`, explicit `--mode initialize-new`, the read-only `assess_project_governance.py`, and an optional validator for a file-backed mature-project takeover record. Project type and profile are required, while `--modules` can override the type recommendation. The assessor returns a bounded summary by default and expands the complete candidate list only with `--verbose`. Mature-project work still follows a proposed map, project evidence, and user authorization rather than blind transformation.

`core` is the genuinely lightweight profile. It creates only README, AGENTS, a governance charter, a machine-readable policy, and one validation entrypoint; it does not pre-create tasks, logs, lessons, or professional documents. Use `standard` when ongoing collaboration, durable tasks, and professional owners are needed, and `release` for formal deployment, release, and artifact lifecycle closure. `plan-new` (and the compatible `--dry-run`) emits only JSON, listing candidates under `planned` while preserving zero writes.

`Initialize New Project` is an agent behavior triggered by the semantics of a “create/start a project” task. The agent should proactively select `senmu-build-project`, classify the project from its goals and evidence, and generate the minimum instance before substantive implementation. It is not a background process watching all new directories, and a Hook will not write into a non-empty directory automatically.

When a project genuinely maintains custom Agents or system prompts, initialization of an empty project may explicitly add `--with-agents`. It adds only `agents/AGENT_REGISTER.md`, the Agent Definition template, and its validator. It does not invent Agents for every project or turn root `AGENTS.md` or Skill metadata into a business prompt.

## One plugin, seven peer Skills

| Skill | Professional name | Responsibility | Load when |
| --- | --- | --- | --- |
| `senmu-build-project` | Project Management | Project management | Project initialization, directory or authority conflicts, governance profile, durable task state, cross-lifecycle coordination |
| `senmu-build-product` | Product Management | Product and requirements management | Requirement intake, PRD, prioritization, roadmap, iteration commitment, acceptance, scope change |
| `senmu-build-workflow` | Workflow Governance | Workflow and material governance | Harnesses, Agent contracts, data/material flow, run state, recovery, deliverables, receipts |
| `senmu-build-engineering` | Software Engineering | Software engineering governance | Technology choices, architecture, implementation efficiency, coding, testing, refactoring, dependencies, technical debt |
| `senmu-build-delivery` | Delivery Management | Collaboration, version, and delivery management | Git, repositories and release units, versions, artifacts, deployment, release, production verification, rollback |
| `senmu-build-assurance` | Governance Assurance | Governance review and evidence assurance | POCs, read-only reviews, debt inventories, evidence grading, disputed causal verification |
| `senmu-build-learning` | Organizational Learning & Continual Improvement | Organizational learning and continual improvement | Retrospectives, lesson capture, knowledge maintenance, source-level improvement, repository-wide BuildOS feedback |

The seven Skills are peers both technically and in responsibility. `senmu-build-project` is not a parent Skill that must always load first. In a stable existing project, a single-domain task should select the matching Skill directly. Add a second supporting Skill only when the work genuinely crosses boundaries, and do not load the entire suite at once.

Codex selects the primary Skill from each Skill's `description` and the user's intended outcome; users can also invoke one explicitly. When responsibility truly changes, the current Skill hands off only the identifier, scope, authoritative entrypoints, facts and evidence, unresolved questions, next result, and authorization boundary. It does not copy the entire playbook. Senmu BuildOS has no eighth “master director” Skill and does not force the seven Skills into a fixed pipeline.

## Three-layer operating model

```text
Codex / AI Agent
├── Lifecycle Hook: restore extremely short, cross-domain, non-optional governance boundaries
├── Professional Skill: load one primary domain and, when necessary, one supporting domain
└── Project-local facts: README, AGENTS, policy, schema, code, tasks, ledgers, release evidence
```

Project-local facts are authoritative for the current state, while Senmu BuildOS is the governance standard used to assess and evolve those facts. BuildOS helps create, locate, validate, and improve owners, but it does not store a specific project's requirements, progress, or release state inside the plugin.

### Lifecycle Hooks

`SessionStart` injects a fixed governance kernel of no more than 950 characters after startup, resume, clearing, or context compression. `SubagentStart` injects a delegation boundary of no more than 500 characters. `UserPromptSubmit` matches only explicit corrections or submission actions; questions about the feedback mechanism are not captured. When an agent discovers a high-signal governance gap, it may submit it silently through the local CLI. Matches are redacted, deduplicated, and written to the local inbox, while normal user-facing answers expose no internal marker or candidate ID. Hooks do not read the entire project, guess the current role, load complete Skills, change task state, or promote rules automatically.

This restores boundaries such as “real project facts first,” “do not exceed authorization,” “load on demand,” “preserve evidence,” and “unverified is not complete” without repeatedly placing product, engineering, and release rules into every turn. Users must still review and trust plugin Hooks after installation or change. Source code presence does not mean a Hook is enabled at runtime.

### Durable task state

Work spanning multiple dependent steps, stages, agents, or sessions needs a project-declared **Durable Task State Owner**. `governance/tasks/` is the BuildOS default for new `standard` and `release` projects. A `core` project may continue to use its README, Issues, or an external task system, while a mature project maps and retains an existing task package, database, or external system.

The default Markdown implementation is:

- `TASK_REGISTER.md` records only tasks and their current states.
- `TASK-<NNNN>-<slug>.md` is a numbered durable task plan containing the boundary, stages, progress, key decision summaries, evidence links, and recovery entrypoint. It does not create a separate directory for every task by default.
- Professional facts such as the PRD, technical design, Run Manifest, test evidence, and Release Record remain in their unique owners. The task record links to them instead of duplicating their content.

Codex's temporary plan is appropriate for scheduling the current session. Create a numbered project task plan only when work spans multiple steps, stages, agents, or sessions, or requires audit and recovery. Do not mechanically duplicate the two.

## Repository structure

```text
.agents/         Public plugin catalog used for Git Marketplace installation
.github/         Repository CI that reuses local validation entrypoints
.codex-plugin/   Codex plugin identity and presentation metadata
.claude-plugin/  Claude Code plugin identity and marketplace
adapters/        Harness adapters for Codex, Claude Code, and Doubao
hooks/           Codex Hook entrypoint and shared short governance kernel
bin/             Local feedback query, submission, and batch-review entrypoint
skills/          Seven professional Skills loaded on demand
docs/            System architecture, responsibility boundaries, and artifact maps
scripts/         Plugin structure, product identity, and link validation
tests/           Hook, initialization, package-structure, and behavioral tests
```

This is the public source surface, generated by allowlist from the project's private authority repository. Internal tasks, work logs, raw feedback, machine paths, and private reviews are excluded. See the [source publication boundary](docs/architecture/publication-boundary.md).

See [Skill boundaries and collaboration](docs/architecture/skill-boundaries.md) for detailed responsibilities, [project artifact and directory ownership](docs/architecture/project-artifact-map.md) for project-local locations, and the [Codex Harness boundary](docs/architecture/codex-harness-boundary.md) for the division of responsibility between Codex and BuildOS.

## Alignment with official harness mechanisms

- Deliver multiple related Skills in one plugin instead of requiring users to install seven isolated Skills.
- Use each Skill's short `description` for discovery and triggering. Keep the complete entrypoint focused on routing and load detailed knowledge from `references/` only when needed.
- Codex uses `hooks/hooks.json` and `${PLUGIN_ROOT}`; Claude Code uses `.claude-plugin/plugin.json`, `${CLAUDE_PLUGIN_ROOT}`, and an isolated Hook configuration.
- Claude Code namespaces plugin Skills so existing user Skills are not replaced; both platforms share short governance context and a bounded local feedback-candidate protocol.
- Project entry files, permissions, sandboxing, session plans, and context compression remain owned by the harness. BuildOS does not duplicate state the host already owns reliably.

## Validation

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

GitHub Actions reuses only these three project-owned entrypoints. Each Skill should also pass Skill Creator's `quick_validate.py`, and the plugin manifest should pass Plugin Creator's `validate_plugin.py`. Passing format and static assertions does not prove real Agent routing, Hook trust, or task behavior; those still require behavioral testing in an isolated candidate environment.

## Current boundaries

- `v1.0.0` is the first formal source release for Codex; its Tag, GitHub Release, `VERSION`, plugin version, and Changelog identify the same baseline.
- The Git Marketplace install, update, and removal path has command-level validation. Hook trust and enablement, plus Skill routing in real tasks, must still be verified in the active Codex environment.
- `v1.1.0` formally supports Codex and Claude Code. The Claude Code adapter has passed official manifest validation, an isolated install/removal smoke, Hook-protocol checks, and side-effect-boundary validation.
- The current system covers low-noise feedback capture, batch review, retrospectives, and organizational learning, but it does not provide feedback dashboards, statistics, or automatic rule generation. Growth and metrics operations remain outside the current scope.
- This repository uses the [Apache License 2.0](LICENSE). The license permits use, modification, and distribution of the source without expanding the platform or compatibility commitments stated above.

## License

Senmu BuildOS is open source under the [Apache License 2.0](LICENSE).
