# Senmu BuildOS — Engineering Coach and Operating Rules for AI Coding Projects

<p align="center">
  Help Codex, Claude Code, and Doubao build the right thing, then build it with less waste.
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a> · <a href="README.ja.md">日本語</a>
</p>

<p align="center">
  <a href="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml"><img src="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml/badge.svg" alt="Validate Senmu BuildOS"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/SenMuShare/senmu-buildos" alt="License"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/stargazers"><img src="https://img.shields.io/github/stars/SenMuShare/senmu-buildos?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/releases/latest"><img src="https://img.shields.io/github/v/release/SenMuShare/senmu-buildos" alt="Release"></a>
</p>

Senmu BuildOS is an open-source operating discipline and software-engineering coach for **AI coding agents**. It covers requirements, technical design, framework and component selection, frontend and backend implementation, testing, Git, releases, and reusable learning. The goal is sustainable work in real projects, not another ever-growing prompt.

It focuses on two outcomes:

1. **Run projects with fewer mistakes.** Confirm real requirements, project facts, and authorization first; then keep design, code, tests, branches, versions, and release evidence aligned.
2. **Improve code quality while reducing waste.** First decide whether a requirement needs implementation. Then reuse the project, framework and component APIs, platform, standard library, and mature dependencies. Write the smallest well-bounded custom code only when a real gap remains.

> BuildOS optimizes for less but correct code—not the fewest lines or the lowest token count. Security, accessibility, business semantics, testing, and maintainability are not removed to save tokens.

## Why BuildOS

| Common AI coding failure | BuildOS behavior |
| --- | --- |
| Coding starts before scope is clear, and unrequested features appear | Approved scope, non-goals, and observable acceptance constrain implementation; unapproved ideas remain candidates |
| An agent creates new folders, services, or a second source of state without reading the project | Inspect the real root, existing code, call paths, and source of truth before extending what is already there |
| One framework option would solve the problem, but the agent hand-rolls a component or watches internal DOM | Check public APIs for the installed version first; add a minimal adapter only when evidence shows a real gap |
| Code runs but becomes difficult to read, test, or change | Protect single ownership, module boundaries, explicit side effects, change locality, regression tests, and deletability |
| Abstractions, plugin systems, and generic platforms are built for imagined future needs | Close the current minimum value slice first; expand when a second real use case or an approved roadmap requires it |
| Every new chat repeats explanations and reloads long rules | Record decisions, progress, and evidence in project documents and tasks; load only relevant guidance and reuse information that is still valid |
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

## How it works

BuildOS does not wait until formatting or code review to catch mistakes. It starts before bad decisions become code:

```text
Real problem and approved scope
        ↓
Project facts, architecture boundaries, and existing capabilities
        ↓
Technical direction, frameworks, components, and public extension points
        ↓
Minimum correct frontend and backend implementation
        ↓
Risk-matched testing and product acceptance
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
- **Reuse before custom code.** Prefer public capabilities already provided by the project, framework, component system, platform, and standard library; add the smallest adapter only when a real gap remains.
- **Keep small work lightweight.** Routine changes need only the checks they justify; data, permissions, payments, production releases, and other high-risk work retain design, verification, and rollback evidence.
- **Use evidence to define done.** Passing tests, product acceptance, artifact creation, deployment, and production availability are different facts and cannot substitute for one another.
- **Let the project remember.** Important decisions, progress, and recovery entrypoints belong in the project, not in one conversation that may disappear.

For the full system design, see [System overview](docs/architecture/system-overview.md), [Skill boundaries](docs/architecture/skill-boundaries.md), and [Project artifact map](docs/architecture/project-artifact-map.md).

## Where it helps

- **New projects:** establish the smallest useful requirements, architecture, quality, and delivery baseline—not a document castle.
- **Mature projects:** inspect existing docs, configuration, code, tests, CI, and release facts before filling gaps; do not create a second governance tree.
- **Features and bugs:** follow project-local rules, reuse framework and existing implementation, make the smallest change, and run matching verification.
- **Long-running work:** preserve stages, decisions, evidence, and recovery entrypoints for cross-session and multi-agent handoffs.
- **Formal releases:** align scope, review, tests, versions, artifacts, deployment, production verification, and rollback identity.
- **Governance and learning:** review technical debt and duplicate implementations; turn verified lessons that apply across projects into reusable guidance.

## One plugin, seven focused Skills

| Skill | Use it when |
| --- | --- |
| `senmu-build-project` | A new project needs a basic operating structure, or a mature project needs its existing structure, rules, and durable task state identified |
| `senmu-build-product` | Requirements, scope, priority, roadmap, or acceptance criteria need to be defined or changed |
| `senmu-build-workflow` | A multi-step workflow, agent responsibility, material flow, recovery path, or delivery state needs to be designed |
| `senmu-build-engineering` | Technical design, architecture, technology selection, code quality, testing, refactoring, or technical debt needs governance |
| `senmu-build-delivery` | Complex Git collaboration, versions, artifacts, releases, rollback, or production verification needs governance |
| `senmu-build-assurance` | Independent reproduction, a POC, an audit, or an evidence-strength judgment is the requested result |
| `senmu-build-learning` | A problem needs a retrospective, feedback needs review, or external knowledge should become reusable guidance |

If project `AGENTS.md`, the active framework, and tests already govern an ordinary code change, BuildOS can stay out. When it is needed, load the closest Skill and only the relevant reference—not all seven manuals.

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

The current formal release is Senmu BuildOS `v2.0.6`. It supports Codex, Claude Code, and a Doubao adapter. Install the plugin as one unit; the seven Skills do not need separate downloads.

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

### Remove

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

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
