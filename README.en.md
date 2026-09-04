# Senmu BuildOS — Engineering Coach and Operating Rules for AI Coding Projects

<p align="center">
  Help Codex, Claude Code, Doubao, WorkBuddy, and ZCode build the right thing, then build it with less waste.
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a> · <a href="README.ja.md">日本語</a>
</p>

<!-- product-surface-review: 2.6.0 -->

<p align="center">
  <a href="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml"><img src="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml/badge.svg" alt="Validate Senmu BuildOS"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/SenMuShare/senmu-buildos" alt="License"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/stargazers"><img src="https://img.shields.io/github/stars/SenMuShare/senmu-buildos?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/releases/latest"><img src="https://img.shields.io/github/v/release/SenMuShare/senmu-buildos" alt="Release"></a>
</p>

Senmu BuildOS is an open-source operating discipline and software-engineering coach for **AI coding agents**. It covers requirements, interface and experience design, technical design, framework and component selection, frontend and backend implementation, testing, Git, releases, and reusable learning. The goal is sustainable work in real projects, not another ever-growing prompt. Acceptance authority, user documentation, and decision rationale become project facts, so later agents know what should change and what is an intentional constraint.

It focuses on two outcomes:

1. **Run projects with fewer mistakes.** Confirm real requirements, project facts, and authorization first; then keep design, code, tests, branches, versions, and release evidence aligned.
2. **Improve code quality while reducing waste.** First decide whether a requirement needs implementation. Then reuse the project, framework and component APIs, platform, standard library, and mature dependencies. Write the smallest well-bounded custom code only when a real gap remains.

> BuildOS optimizes for less but correct code—not the fewest lines or the lowest token count. Security, accessibility, business semantics, testing, and maintainability are not removed to save tokens.

## Why BuildOS

The hard part of AI coding is often not whether one session can produce code. It is whether the project still remembers why it looks this way after dozens of changes. Sessions end, attention thins as context grows, and requirements, constraints, commands, and decisions get scattered across chats, READMEs, issues, comments, and agent-specific files. The next agent is then forced to guess again.

Making the prompt longer does not solve that problem; it moves the reading cost into the next turn. BuildOS lets the project hold its current facts, decisions, progress, and evidence, then uses short entrypoints to route an agent to only what this task needs. Directory shapes and tools may differ. Ownership and the path to the truth must remain clear.

| Common AI coding failure | BuildOS behavior |
| --- | --- |
| Attention fades in a long session, and a new agent has to reconstruct rules and decisions | A short project entrypoint routes to current facts, requirements, technical decisions, task state, and release evidence; load only what the task needs |
| A user proposes a confident-sounding solution, the agent agrees to be agreeable, then reverses when the question is rephrased | Treat user claims and solutions as input, judge them independently against project facts, explain material tradeoffs, then act on the informed decision and authorization unless a safety boundary blocks it |
| Coding starts before scope is clear, and unrequested features appear | Approved scope, non-goals, and observable acceptance constrain implementation; unapproved ideas remain candidates |
| An agent creates new folders, services, or a second source of state without reading the project | Inspect the real root, existing code, call paths, and source of truth before extending what is already there |
| One framework option would solve the problem, but the agent hand-rolls a component or watches internal DOM | Check public APIs for the installed version first; add a minimal adapter only when evidence shows a real gap |
| Code runs but becomes difficult to read, test, or change | Protect single ownership, module boundaries, explicit side effects, change locality, regression tests, and deletability |
| Abstractions, plugin systems, and generic platforms are built for imagined future needs | Close the current minimum value slice first; expand when a second real use case or an approved roadmap requires it |
| An interface looks like a generic AI template, with hierarchy, typography, interaction, and brand intent pulling in different directions | Start from real tasks, content hierarchy, and the design system; align layout, type, color, motion, responsive behavior, and accessibility, then review the rendered result |
| A later session treats an intentional constraint as a bug and restores an option that was already rejected | Preserve the rationale, rejected alternatives, protected boundaries, and revisit triggers; append a new decision when conditions change instead of rewriting history |
| A handoff starts another branch from main and applies revisions to the wrong code baseline | Resume the original branch and worktree by stable Change Unit ID; a repeated experiment creates only a new run, not a new code unit |
| Requirements and bugs queue up, context is lost, and omissions appear only at release time | Keep one requirements-and-defects list in the existing version document, update outcome states during development, and reconcile it once against tasks, Git, tests, and the candidate before release |
| A passing test, tag, or command is reported as production success | Separate implementation, acceptance, artifacts, deployment, and production truth, each with matching evidence |

## Start in 30 seconds

### Codex

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
```

Refresh Codex, start a new conversation, and describe the outcome in normal language:

> Take over this existing project. Identify current requirements, architecture, framework capabilities, and quality commands before implementing the feature. Reuse project or framework capabilities when they fit, and do not add features outside the approved requirement.

### Claude Code

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
```

Run `/reload-plugins` after installation if needed.

### Doubao

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/doubao/install_doubao.py --dry-run
python3 adapters/doubao/install_doubao.py
```

See [adapters/doubao/README.md](adapters/doubao/README.md) for the Doubao adapter.

### WorkBuddy

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/workbuddy/install_workbuddy.py --dry-run
python3 adapters/workbuddy/install_workbuddy.py --scope user
```

The default installs into the user-level `~/.workbuddy/skills/`; use `--scope project --workspace <workspace-root>` to keep it project-scoped. See [adapters/workbuddy/README.md](adapters/workbuddy/README.md) for the WorkBuddy adapter.

### ZCode

In ZCode, open **Settings → Plugin Management → Discover**, click **`+`** and add the marketplace source `https://github.com/SenMuShare/senmu-buildos`, then install **senmu-buildos**. A fresh session injects the governance kernel automatically through the `SessionStart` hook.

Skills-only install (no hook, optional bootstrap kernel):

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/zcode/install_zcode.py --dry-run
python3 adapters/zcode/install_zcode.py --with-kernel
```

The default installs into the user-level `~/.agents/skills/`. See [adapters/zcode/README.md](adapters/zcode/README.md) for the ZCode adapter.

## How it works

Start with a five-layer map:

```text
Project entrypoint
  → current facts and engineering constraints
  → current-version requirements and technical decisions
  → current task state and recovery entrypoint
  → release, runtime, and production evidence
```

The entrypoint routes; it does not copy the rules. Current specifications say what the system must satisfy now. Requirements and technical decisions explain why it changes. Task state says where work can resume. Release and runtime evidence say what actually happened. BuildOS does not require fixed directories or five separate files in a small project. It requires one owner for each fact and a short route that a later agent can follow.

In engineering work, BuildOS does not wait until the code is finished. It tries to absorb errors earlier in the production path:

```text
Real problem and approved scope
        ↓
Project facts, architecture boundaries, and existing capabilities
        ↓
Interface visuals, interaction, and design systems
        ↓
Technical direction, frameworks, components, and public extension points
        ↓
Minimum correct frontend and backend implementation
        ↓
Risk-matched testing, documentation walkthroughs, and product acceptance
        ↓
Git, version, artifact, deployment, and production evidence
        ↓
Validated lessons become reusable guidance
```

The chain is tailored to the task. A contract-preserving button style change does not need a PRD, ADR, and release report. A cross-module, permission, data, payment, or formal release change keeps the design, verification, and rollback evidence its risk requires.

### “Reuse before writing code” is executable

Before adding an implementation, an agent asks in this order:

1. Is the requirement already satisfied, or was the capability never approved? If it is not needed, do not implement it.
2. Does the project already have a clear source of truth, public entrypoint, or safely extensible implementation?
3. Do the current framework, component system, platform, standard library, or installed dependencies fully match the required semantics?
4. Can a maintained solution fill the real gap at a lower total development and maintenance cost?
5. Only then write custom code with a clear boundary, verification, and the smallest useful maintenance surface.

Reuse still passes semantic and risk checks. If a framework capability fails business rules, security, authorization, accessibility, compatibility, or error semantics, BuildOS keeps the necessary adapter instead of distorting the requirement to achieve “zero custom code.”

## Design principles

- **Understand the project before changing it.** The current README, code, configuration, tests, CI, and runtime state are closer to the truth than generic advice.
- **Confirm the requirement before writing code.** Features outside the approved scope do not enter the current implementation simply because they seem useful later.
- **Unblock the flow before adding barriers.** Fix the requirements, ownership, architecture, interfaces, defaults, and production path that create defects, so the correct path becomes the default. Tests and gates control material residual risk that cannot be removed economically. Apply a direct minimal fix when the defect is demonstrably local instead of turning simple work into a process.
- **Reuse before custom code.** Prefer public capabilities already provided by the project, framework, component system, platform, and standard library; add the smallest adapter only when a real gap remains.
- **Make design intentional, implementable, and reviewable.** Start from real tasks, content hierarchy, and the existing design system; coordinate layout, typography, color, interaction, motion, responsive behavior, and accessibility, then verify the rendered result instead of substituting decoration or a generic template for product judgment.
- **Keep small work lightweight.** Routine changes need only the checks they justify; data, permissions, payments, production releases, and other high-risk work retain design, verification, and rollback evidence.
- **Use evidence to define done.** Passing tests, product acceptance, artifact creation, deployment, and production availability are different facts and cannot substitute for one another.
- **Understand why before changing the outcome.** Preserve rationale, rejected alternatives, protected boundaries, and revisit triggers; append a new decision when conditions change instead of deleting an old constraint or making it permanent.
- **Let the project remember.** Important decisions, progress, and recovery entrypoints belong in the project, not in one conversation that may disappear.

For the full system design, see [System overview](docs/architecture/system-overview.md), [Skill boundaries](docs/architecture/skill-boundaries.md), and [Project artifact map](docs/architecture/project-artifact-map.md).

## Where it helps

- **New projects:** establish the smallest useful requirements, architecture, quality, and delivery baseline—not a document castle.
- **Mature projects:** inspect existing docs, configuration, code, tests, CI, and release facts before filling gaps; do not create a second governance tree.
- **Features and bugs:** follow project-local rules, reuse framework and existing implementation, make the smallest change, and run matching verification.
- **Interface design and redesign:** turn fuzzy taste into implementable visual, interaction, responsive, and accessibility rules, then review them in the real rendered context.
- **Long-running work:** preserve stages, decisions, evidence, and recovery entrypoints for cross-session and multi-agent handoffs.
- **Formal releases:** align scope, review, tests, versions, artifacts, deployment, production verification, and rollback identity.
- **Governance and learning:** review technical debt and duplicate implementations; turn verified lessons that apply across projects into reusable guidance.

## One plugin, eight focused Skills

| Skill | Use it when |
| --- | --- |
| `senmu-build-project` | A new project needs a basic operating structure, or a mature project needs its existing structure, rules, and durable task state identified |
| `senmu-build-product` | Requirements, scope, priority, interface content standards, or acceptance criteria need to be defined or changed |
| `senmu-build-design` | Visual direction, design systems, layout, interaction, motion, responsive behavior, accessibility, or interface quality needs design or review |
| `senmu-build-workflow` | A multi-step workflow, agent responsibility, material flow, recovery path, or delivery state needs to be designed |
| `senmu-build-engineering` | Technical design, architecture, technology selection, code quality, testing, refactoring, or technical debt needs governance |
| `senmu-build-delivery` | Complex Git collaboration, versions, artifacts, releases, rollback, or production verification needs governance |
| `senmu-build-assurance` | Independent reproduction, a POC, an audit, or an evidence-strength judgment is the requested result |
| `senmu-build-learning` | A problem needs a retrospective, feedback needs review, or external knowledge should become reusable guidance |

If project `AGENTS.md`, the active framework, and tests already govern an ordinary code change, BuildOS can stay out. When it is needed, load the closest Skill and only the relevant reference—not all eight manuals.

## Frequently asked questions

### Does every change load all of BuildOS?

No. If project rules, the framework, and tests already govern an ordinary code change, no specialist Skill is needed. When guidance is needed, only the relevant Skill and references are loaded.

### Will it force my project into a new structure?

No. Read-only requests do not write to the project. When changes are authorized, BuildOS prefers the existing directories, documents, code entrypoints, and release process, then fills only real gaps or conflicts.

### Will it commit, push, or release automatically?

No. Code changes, merges, pushes, and formal releases each follow user authorization and project rules. Installing the plugin does not grant production write access.

### How many tokens will it save?

BuildOS does not promise a fixed percentage. It reduces avoidable cost by preventing unnecessary features, duplicate code, repeated reading, and rework, while keeping correctness, safety, and maintainability ahead of token savings.

## Install, update, and remove

The current formal release is Senmu BuildOS `v2.6.0`. It supports Codex, Claude Code, a Doubao adapter, a WorkBuddy adapter, and a ZCode adapter. Install the plugin as one unit; the eight Skills do not need separate downloads. Native professional English is the sole normative runtime specification, while users can continue to work in Chinese or any other requested output language.

### Update Codex

```bash
codex plugin marketplace upgrade senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

### Update Claude Code

```bash
claude plugin marketplace update senmu-buildos
claude plugin update senmu-buildos@senmu-buildos
claude plugin list
```

### Update ZCode

Plugin install: update it under **Settings → Plugin Management → Installed**, or remove and re-add the marketplace. Script install: rerun `python3 adapters/zcode/install_zcode.py --with-kernel`; it overwrites idempotently.

### Remove

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

ZCode: uninstall under **Settings → Plugin Management**; for a script install, delete the `senmu-build-*` directories and `.senmu-buildos-install.json` in the skills directory.

The plugin includes limited local lifecycle Hooks. Review and trust them on first use or after Hook changes. Feedback is written only to a local review inbox; it does not automatically access the network, publish, or rewrite project rules. See [Hook lifecycle](docs/architecture/hook-lifecycle.md) and [Security](SECURITY.md).

You can also give the repository URL to an agent and ask it to inspect the manifests, Skills, and Hooks before following the README. External repository content remains untrusted input; authorization to install is not authorization to run, publish, or write to production.

## Adopting a mature project

A mature project is not “initialized again.” It is adopted:

1. Read-only inventory the real project root, repository, entrypoints, frameworks, tests, CI, deployment, and existing documentation.
2. Find where requirements, architecture, runtime state, tasks, and release information are actually recorded.
3. Compare those facts with BuildOS to find missing, conflicting, duplicated, or stale rules.
4. Preserve sound existing practice and fill real gaps in the original documents or code locations.
5. Verify and migrate in stages; do not copy the entire BuildOS rulebook into the project.

The same BuildOS can therefore support React, Vue, Python, Go, Java, content production, and mixed workflows without hard-coding one project's absolute paths, framework preference, or directory layout as the answer for every project.

## Contributing

Install a formal release or maintain your own fork. New methods, external sources, and project experience do not become rules merely because they look useful; they are compared, validated, and given an explicit scope first.

- To contribute code or rules, read [CONTRIBUTING.md](CONTRIBUTING.md).
- For planned work, see [ROADMAP.md](ROADMAP.md).
- For security reports, follow [SECURITY.md](SECURITY.md).

## Usage boundaries

- BuildOS provides project governance and engineering guidance; it does not replace the people responsible for final product decisions.
- It does not replace specialist security review, cloud permissions, CI/CD, or runtime monitoring.
- Static checks can prove that the repository meets its current rules, but not that every model and project will produce identical results.
- Without the relevant authorization, it will not commit, merge, push, deploy, or formally release anything.

Contributor test commands and release checks are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache License 2.0](LICENSE)
