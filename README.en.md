# Senmu BuildOS — Agent Skills for Codex & Claude Code

**Understand the project. Reuse what works. Verify the result.**

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

Senmu BuildOS is a set of agent skills for real software projects. Help your coding agent understand the existing implementation, clarify requirements and constraints, reuse code and mature components, and verify the result with appropriate tests and delivery evidence. Use it for requirements, UI/UX, architecture, debugging, code review and release work—without turning every edit into a full process.

**One plugin. Eight on-demand capabilities. Keep existing projects intact and small changes lightweight.**

[![License](https://img.shields.io/github/license/SenMuShare/senmu-buildos)](LICENSE) [![Public release](https://img.shields.io/github/v/release/SenMuShare/senmu-buildos?label=public%20release)](https://github.com/SenMuShare/senmu-buildos/releases/latest)

[Quick start](#quickstart) · [Try it first](#first-use) · [Eight skills](#skills) · [FAQ](#faq) · [Update and uninstall](#maintenance)

<a id="quickstart"></a>
<a id="30-second-start"></a>
## Quick start

Use a plugin-capable version of Codex or Claude Code, with Git and Node.js available locally. Review the [hooks](hooks/hooks.json) and [security notes](SECURITY.md) before enabling the plugin; trust only a source you have reviewed.

### Codex

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

Refresh the client and start a new project conversation. Confirm the listed source and version, then try a task below.

### Claude Code

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
claude plugin list
```

Start a new session or run `/reload-plugins` in the current one. Confirm the plugin's status in the Installed tab of `/plugin`. See the [Claude Code adapter](adapters/claude-code/README.md) for instruction compatibility and troubleshooting.

These commands install the version available from the **public marketplace**, which may differ from this source version. Private artifacts follow their authorized installation process. Installation, activation in the current session, and actual task behavior are separate checks. For command differences, consult your client's `--help`, the [Codex reference](https://developers.openai.com/codex/cli/reference/) and [Claude Code documentation](https://code.claude.com/docs/en/discover-plugins).

<details>
<summary>Doubao, WorkBuddy, ZCode and skills-only installation</summary>

The adapters share the same eight professional capabilities, but copying skills is not equivalent to installing lifecycle hooks. Start from trusted source, in the product root containing `skills/` and `adapters/`. Python adapters require Python 3. The following clone uses the public repository.

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
```

| Host | Preview first | Install after review and read more |
| --- | --- | --- |
| Doubao | `python3 adapters/doubao/install_doubao.py --dry-run` | `python3 adapters/doubao/install_doubao.py`; [targets and removal](adapters/doubao/README.md) |
| WorkBuddy | `python3 adapters/workbuddy/install_workbuddy.py --dry-run` | `python3 adapters/workbuddy/install_workbuddy.py --scope user`; [project scope and removal](adapters/workbuddy/README.md) |
| ZCode | `python3 adapters/zcode/install_zcode.py --dry-run` | `python3 adapters/zcode/install_zcode.py --with-kernel`; [plugin mode and removal](adapters/zcode/README.md) |

ZCode also accepts the marketplace `https://github.com/SenMuShare/senmu-buildos` in its plugin manager; start a new session after installation. Skills-only adapters provide a discoverable bootstrap capability according to their configuration, not guaranteed automatic injection in every session. Avoid duplicate installations.

</details>

<a id="first-use"></a>
## Try one real task

Open a project and choose a starting point. You do not need to memorize the skill names. These are suggested inputs, not guaranteed outcomes.

### 1. Understand an existing project without changing it

> Inspect this project read-only. Find the runtime entrypoints, current rules and test commands. Explain what this requirement can reuse. Do not edit code yet.

**Check for:** real paths, current constraints, reusable capabilities and open questions—not a second project structure or unrequested edits.

### 2. Fix a recurring bug

> Investigate this bug thoroughly. Reproduce the original symptom and establish the cause before making the smallest appropriate repair. Verify the original path and affected regressions. State what you could not reproduce.

**Check for:** evidence separated from hypotheses, the actual change, commands that ran and the remaining verification gaps—not just a claim that it should work.

### 3. Add a feature to an existing codebase

> Clarify the scope and completion criteria, reuse the existing structure and components, then implement and verify in small steps. Do not add unrequested features.

**Check for:** changes tied to requirements, justified reuse, and a clear distinction between completed work and work awaiting verification.

When drafting or updating requirements, each feature retains its target version and four parts: requirement context, capability, business logic, and frontend interaction including exceptions. Link relevant prototypes/UI to the specific requirement and record adoption scope. Missing artwork does not require generating it; an explicitly requested replacement format takes priority. See [requirement writing and design linkage](skills/senmu-build-product/references/product-requirements-and-iteration.md#21-per-feature-requirement-contract).

For a review, ask “Review requirement fidelity and engineering quality separately.” For work only you can do in a third-party console, ask “Turn the steps only I can perform into a resumable operator guide.” Open the [skill table](#skills) when you need an explicit entrypoint.

<a id="why"></a>
<a id="why-buildos"></a>
## Problems it helps you address

| What goes wrong | How BuildOS approaches it | What to look for |
| --- | --- | --- |
| The agent starts coding before understanding the request | Clarify scope, non-goals and completion criteria | Implementation that matches the request, not extra features |
| Existing components and state are rebuilt from scratch | Inspect the project, framework and component capabilities first | A necessary, focused change and a reason for reuse |
| Every fix makes the code harder to maintain | Follow causes, responsibilities and callers; verify real behavior | An evidenced repair, clear boundaries and regression results |
| A new session starts guessing; passing tests become “deployed” | Keep decisions, progress and evidence with existing project owners | Resumable work and accurate implementation, acceptance and release status |

BuildOS is for independent developers, product builders and small teams maintaining real projects. It is not a code generator or hosted execution platform, and more documents or approvals are not substitutes for engineering judgment.

<a id="example"></a>
## An example you can inspect

The repository's [Python and TypeScript quality-wiring examples](skills/senmu-build-engineering/assets/code-quality/examples/README.md) show how a rule reaches an executable check, rather than ending at “follow the standards.”

In the Python pricing example, [`total()`](skills/senmu-build-engineering/assets/code-quality/examples/python/sample_app/domain.py) subtracts a discount and rejects a negative result. [`check.py`](skills/senmu-build-engineering/assets/code-quality/examples/python/check.py) connects formatting, static rules, types, dependency boundaries and business tests through one command.

```text
Valid implementation → the shared check passes
Introduce a specific violation → the relevant check fails
Restore the implementation → the shared check passes again
```

For example, returning a string probes type checking; replacing subtraction with addition probes the business test. Follow the example instructions in a disposable copy and keep existing project tools. These are repeatable tool fixtures, not customer testimonials or measurements of a model's performance gain.

Optional [executable contract examples](skills/senmu-build-engineering/assets/contract-examples/README.md) connect definitions or code declarations to generated artifacts, real calls and business checks. Their dependencies are example-only, not a required project stack.

<a id="skills"></a>
<a id="one-plugin-eight-capabilities"></a>
## One plugin, eight skills

| Skill | When to use it |
| --- | --- |
| [Project](skills/senmu-build-project/SKILL.md) | Take over a project; reconcile AGENTS.md, existing rules and durable task state |
| [Product](skills/senmu-build-product/SKILL.md) | Clarify requirements, scope, priorities, interface content and acceptance |
| [Design](skills/senmu-build-design/SKILL.md) | Design or review UI/UX, layout, interaction, responsiveness and accessibility |
| [Workflow](skills/senmu-build-workflow/SKILL.md) | Define business agents, prompts, materials, recovery and delivery contracts |
| [Engineering](skills/senmu-build-engineering/SKILL.md) | Understand systems, diagnose bugs, design architecture, apply language guidance, test and review code |
| [Delivery](skills/senmu-build-delivery/SKILL.md) | Handle complex Git collaboration, versions, artifacts and authorized releases or rollback |
| [Assurance](skills/senmu-build-assurance/SKILL.md) | Reproduce, experiment, audit and assess evidence; independent review needs an actually independent reviewer |
| [Learning](skills/senmu-build-learning/SKILL.md) | Turn verified lessons and useful external methods into the appropriate existing rules |

These are peer capabilities, not eight agents that must run together. Engineering loads applicable language/runtime guidance for Python, TypeScript, Go, Java, Rust and other stacks—not the whole catalog. Each entry uses its directory name. Runtime guidance is written in English; you can work in Chinese, English, Japanese or another requested language.

<a id="how-it-works"></a>
## Working with your existing project

**Organize interface collaboration around actual boundaries.** Full-stack, multiple full-stack or frontend/backend specialists can deliver complete feature slices: find the current contract, consumers and checks before choosing implementation order. Initialization and authorized governance calibrate the maintenance source and navigation; ordinary work reuses them. A local frontend-only edit needs no HTTP document. See [contract guidance](skills/senmu-build-engineering/references/api-and-boundary-contract-governance.md).

Sessions end and attention thins as context grows. BuildOS favors recoverable project facts over an ever-longer prompt.

```text
Project entrypoint
  → Current facts and engineering constraints
  → Requirements and design decisions
  → Task progress and recovery points
  → Release, runtime and production evidence
```

This is not a requirement to create five files. Small projects can combine records; established projects retain their README, AGENTS.md, issues, design documents and quality commands. Within authorized work, address real gaps while preserving effective principles, exceptions and other contributors' changes.

**Fix the source of the problem before adding another gate.** Improve the requirement, responsibility, interface or default process that creates errors. Use tests and gates for material residual risk; make a small repair when the cause is clear. Reuse must still preserve business meaning, security, permissions and compatibility.

Connect understanding, design, implementation, verification and delivery at the scale of the task. Read more in the [system overview](docs/architecture/system-overview.md), [skill boundaries](docs/architecture/skill-boundaries.md) and [project artifact map](docs/architecture/project-artifact-map.md).

<a id="faq"></a>
## Common questions

**Does every edit load the entire rulebook?** No. Routine work already covered by project rules and tests may need no specialist skill. Other tasks load matching references. Actual loading depends on the client and task; file presence alone does not establish activation.

**Will it rewrite my project, commit or publish automatically?** Installation grants none of those permissions. Reading, editing, committing, pushing and production operations follow the user's authority and project rules. Read-only requests stay read-only; already approved work should not be interrupted by repeated approval rituals.

**Is this just another AGENTS.md?** No. AGENTS.md keeps frequently used project principles and navigation; skills provide task-specific methods; scripts and existing tools perform deterministic checks. They complement one another rather than copy the full manual.

**How many tokens or bugs will it save?** There is no fixed percentage promise. The goal is less duplicate implementation, unrelated reading and rework, with correctness, security and maintainability first. Source tests, host activation and model performance require different evidence; see the [evaluation notes](tests/behavior/host-evaluation.md).

**What do the hooks do?** Supported full-plugin entrypoints supply a short governance prompt at lifecycle events. Skills-only adapters do not offer the same automatic injection. Feedback goes to a local review inbox, without automatic upload or project-rule rewriting. Review hooks on first enablement and when they change; see the [lifecycle notes](docs/architecture/hook-lifecycle.md) and [security notes](SECURITY.md).

<a id="maintenance"></a>
<a id="installation-updates-and-removal"></a>
## Version, updates and removal

The current source version is Senmu BuildOS `v2.24.1`. Source, private release, public marketplace availability and local installation are separate states. The badge above links to the public channel, not your installed version.

<!-- product-surface-review: 2.24.1 -->

This release repairs three requirement-checker omissions and adds two executable contract chains: modular definitions and code-owned declarations, connected to type generation, real consumer validation and SQLite outcome checks. Fault-injection and restoration cases preserve drafts, custom version labels, meaningful lists and the lightweight 2.24.0 governance model. Native Agent behavior remains separate from source evidence. See [release notes](RELEASE_NOTES.md).

<details>
<summary>Update an existing installation</summary>

**Codex**

```bash
codex plugin marketplace upgrade senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

**Claude Code**

```bash
claude plugin marketplace update senmu-buildos
claude plugin update senmu-buildos@senmu-buildos
claude plugin list
```

Start a new session after updating; Claude Code also supports `/reload-plugins`. Check the actual source, version and enabled state. A successful download does not update an already running session by itself. Other hosts use their adapter's update instructions; script-based installations first need the trusted source version you intend to install.

</details>

<details>
<summary>Uninstall</summary>

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

Use the same installation scope as the original installation, consulting the client's help where needed. For other hosts, follow the adapter's removal instructions and remove only this plugin's directories and installation record—not other skills, configuration or project data.

</details>

<a id="contributing"></a>
## Documentation, feedback and contributions

For usage problems, open a [public issue](https://github.com/SenMuShare/senmu-buildos/issues) with the host, BuildOS source and version, reproduction steps, expected result and observed result. Redact sensitive information. Report security problems through [SECURITY.md](SECURITY.md), not in a public issue containing secrets.

Real-world feedback and improvements through forks and pull requests are welcome. You do not need to read every reference before using the plugin. See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and release checks, [ROADMAP.md](ROADMAP.md) for direction, and the [trilingual README policy](CONTRIBUTING.md#github-readme-sync) for documentation changes.

## License

[Apache License 2.0](LICENSE). BuildOS does not replace the project owner, a professional security audit, cloud permissions or CI/CD. It is not an officially certified OpenAI or Anthropic product.
