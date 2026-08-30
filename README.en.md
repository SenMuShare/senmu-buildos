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

## What it changes

| Common AI coding failure | BuildOS behavior |
| --- | --- |
| Coding starts before scope is clear, and unrequested features appear | Approved scope, non-goals, and observable acceptance constrain implementation; unapproved ideas remain candidates |
| An agent creates new folders, services, or a second state owner without reading the project | Inspect the real root, owners, call paths, and similar implementations before extending the existing capability |
| One framework option would solve the problem, but the agent hand-rolls a component or watches internal DOM | Check public APIs for the installed version first; add a minimal adapter only when evidence shows a real gap |
| Code runs but becomes difficult to read, test, or change | Protect single ownership, module boundaries, explicit side effects, change locality, regression tests, and deletability |
| Abstractions, plugin systems, and generic platforms are built for imagined future needs | Close the current minimum value slice first; expand when a second real use case or an approved roadmap requires it |
| Every new chat repeats explanations and reloads long rules | Keep decisions, progress, and evidence in project owners; load Skills and references on demand and reuse valid evidence |
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

## The full engineering chain

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
Validated learning returned to the correct owner
```

The chain is tailored to the task. A contract-preserving button style change does not need a PRD, ADR, and release report. A cross-module, permission, data, payment, or formal release change keeps the design, verification, and rollback evidence its risk requires.

### “Reuse before writing code” is executable

Before adding an implementation, an agent asks in this order:

1. Is the requirement already satisfied, or was the capability never approved? If it is not needed, do not implement it.
2. Does the project already have a canonical owner, public entrypoint, or safely extensible implementation?
3. Do the current framework, component system, platform, standard library, or installed dependencies fully match the required semantics?
4. Can a maintained solution fill the real gap at a lower total development and maintenance cost?
5. Only then write custom code with a clear boundary, verification, and the smallest useful maintenance surface.

Reuse still passes semantic and risk checks. If a framework capability fails business rules, security, authorization, accessibility, compatibility, or error semantics, BuildOS keeps the necessary adapter instead of distorting the requirement to achieve “zero custom code.”

## Where it helps

- **New projects:** establish the smallest useful requirements, architecture, quality, and delivery baseline—not a document castle.
- **Mature projects:** inspect existing docs, configuration, code, tests, CI, and release facts before filling gaps; do not create a second governance tree.
- **Features and bugs:** follow project-local rules, reuse framework and existing implementation, make the smallest change, and run matching verification.
- **Long-running work:** preserve stages, decisions, evidence, and recovery entrypoints for cross-session and multi-agent handoffs.
- **Formal releases:** align scope, review, tests, versions, artifacts, deployment, production verification, and rollback identity.
- **Governance and learning:** review technical debt, duplicate implementations, and feedback; promote cross-project lessons to one canonical owner.

## One plugin, seven on-demand Skills

| Skill | Owns | Does not own |
| --- | --- | --- |
| `senmu-build-project` | Project shape, structure, authority mapping, durable task state, mature-project adoption | Product, engineering, or release decisions |
| `senmu-build-product` | Requirements, scope, non-goals, priority, roadmap, iteration, and acceptance | Technical implementation or production release |
| `senmu-build-workflow` | Workflows, agents, data/materials, run state, recovery, and deliverables | Running an existing workflow or setting release policy |
| `senmu-build-engineering` | Technical design, architecture, selection, code quality, testing, refactoring, and debt | Product priority or release approval |
| `senmu-build-delivery` | Non-routine Git boundaries, versions, artifacts, deployment, rollback, and production truth | Ordinary coding or product acceptance |
| `senmu-build-assurance` | POCs, independent audits, reproduction, evidence grading, and causal findings | Remediation implementation or routine self-review |
| `senmu-build-learning` | Feedback review, retrospectives, external knowledge distillation, and cross-project promotion | Automatically turning one observation into a rule |

If project `AGENTS.md`, the active framework, and tests already govern an ordinary code change, BuildOS can stay out. When it is needed, load the closest Skill and only the relevant reference—not all seven manuals.

## Quick explanation for humans and AI

| Question | Answer |
| --- | --- |
| What is it? | Project operating rules, engineering decision methods, and installable Skills for AI coding agents |
| When should it be used? | When requirement or architecture rules are missing or conflicting, long work needs recovery, a mature project needs adoption, or Git/release/audit risk needs governance |
| How do I use it? | State the product outcome; the agent reads project-local facts and selects one primary Skill only when needed |
| Does it rewrite my project? | Read-only requests do not write; changes follow user authorization and existing owners; mature projects are not forced into a fixed directory layout |
| How many tokens will it save? | No fixed percentage is promised. It reduces avoidable cost through less unnecessary code, on-demand loading, evidence reuse, and durable state, then validates effects in real tasks |

## Why this is not one giant prompt

- **Project facts first:** current README, code, configuration, tests, CI, and runtime evidence outrank generic advice.
- **Progressive disclosure:** a short Kernel keeps universal boundaries; seven Skills route work; detailed references load only when relevant.
- **One owner per fact:** requirements, design, code, task state, runtime state, and release facts remain separate; chat is not the database.
- **Risk-proportional effort:** small changes stay light; data, permission, payment, production, and destructive actions fail closed.
- **Evidence over labels:** passing tests are not product acceptance, a tag is not deployment, and a deployment command is not production proof.
- **Tokens are a cost, not the objective:** information that changes decisions, prevents rework, or controls material risk is worth keeping.

For system details, see [System overview](docs/architecture/system-overview.md), [Skill boundaries](docs/architecture/skill-boundaries.md), [Project artifact map](docs/architecture/project-artifact-map.md), and [Codex harness boundary](docs/architecture/codex-harness-boundary.md).

## Install, update, and remove

The current formal release is Senmu BuildOS `v2.0.4`. It supports Codex, Claude Code, and a Doubao adapter. Install the plugin as one unit; the seven Skills do not need separate downloads.

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
2. Identify who owns requirements, architecture, state, tasks, and release facts.
3. Compare those facts with BuildOS to find missing, conflicting, duplicated, or stale rules.
4. Preserve sound existing practice and fill real gaps in the original owners.
5. Verify and migrate in stages; do not copy the entire BuildOS rulebook into the project.

The same BuildOS can therefore support React, Vue, Python, Go, Java, content production, and mixed workflows without hard-coding one project's absolute paths, framework preference, or directory layout as the answer for every project.

## Open iteration

Install a formal release or maintain your own fork. Web pages, books, public repositories, third-party Skills, and project experience remain candidates until deduplication, conflict resolution, owner mapping, context-cost review, and behavioral validation support promotion.

- To contribute code or rules, read [CONTRIBUTING.md](CONTRIBUTING.md).
- For planned work, see [ROADMAP.md](ROADMAP.md).
- For security reports, follow [SECURITY.md](SECURITY.md).

## Validation and current boundaries

The repository provides project-owned validation entrypoints:

```bash
python3 scripts/validate_package.py --strict
python3 scripts/validate_public_surface.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

These checks validate package structure, metadata, rule invariants, and script contracts. They do not prove that every model and project will save a fixed token percentage, and they do not replace real-task code quality, routing accuracy, Hook trust, deployment, or production verification.

BuildOS does not replace project owners, specialist security review, cloud permissions, CI/CD, or runtime monitoring. It will not commit, merge, tag, push, deploy, or publish without the relevant authorization.

## License

[Apache License 2.0](LICENSE)
