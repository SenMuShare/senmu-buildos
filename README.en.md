# Senmu BuildOS — Agent Skills for Codex & Claude Code

**Turn an idea into a product you can keep improving.**

*Understand the goal. Make the right decisions. Carry the work through.*

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

You know what you want to build. You may not yet know which product, design, engineering or delivery decisions it needs. Senmu BuildOS gives your AI coding assistant a project coach's methods: start from your goal and the codebase, identify the professional work the task requires, and connect decisions to implementation and checkable results.

It covers product, UI/UX, engineering, project governance, workflows, delivery, assurance and learning. New projects get a practical starting point; existing projects retain useful capabilities; small changes stay direct. Different models and sessions can continue from the same project facts.

**Describe your goal. BuildOS helps the agent work out the next step, why it matters and what completion means.**

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

You can also say “Build a browser-based inventory system,” “This page feels messy,” or “Implement this screenshot.” BuildOS identifies the product, design and engineering work the goal needs; a requirements-only request stays within that stage. Maintained UI uses `design/UI_SPECIFICATION.md`. Governance migration preserves valid existing decisions, while AGENTS.md and the project map connect the standard, actual components and review entrypoints.

For a review, ask “Review requirement fidelity and engineering quality separately.” For work only you can do in a third-party console, ask “Turn the steps only I can perform into a resumable operator guide.” Open the [skill table](#skills) when you need an explicit entrypoint.

<a id="why"></a>
<a id="why-buildos"></a>
## A different way to move a project forward

**Bring professional judgment into everyday requests.** “Build an inventory system” carries questions about user actions, data meaning, interface states and delivery. BuildOS guides the agent to recognize the work needed at the current stage. You can speak in product terms without naming a Skill or an engineering technique.

**Fit the method to the project.** A disposable prototype, a maintained product, a backend service and an established repository need different work. Start with actual capabilities and gaps, then choose guidance. Small changes covered by existing rules remain straightforward.

**Reduce rework at its source.** Find the existing component, contract and state owner before creating another. Trace bugs to their cause, resolve conflicting standards into adopted decisions, and choose checks that can expose the actual failure. Clear responsibilities and necessary code matter more than an ever-growing list of prohibitions.

**Leave the next agent a usable starting point.** Requirement versions, design decisions, task progress and verification results stay with the project. Resume through known entrypoints when the session or model changes. Implementation, user acceptance, deployment and release remain distinct facts.

BuildOS is for independent developers, product builders and small teams maintaining real products. You decide the goals and tradeoffs; the agent gets shared methods for organizing the professional work.

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
<a id="one-plugin-eight-skills"></a>
## Eight skills, each with a job to do

### Product · Turn a rough idea into something you can accept

A feature request often leaves failure, cancellation, switching and recovery unspecified. Product connects goals, scope, business behavior, interface feedback and acceptance, then places features in the appropriate version. Linked prototypes retain an explicit adoption scope.

You get implementable requirements and a clear decision about what belongs in this version. Try: “Complete the bulk-export requirements, especially retries and permissions.” [Explore Product](skills/senmu-build-product/SKILL.md)

### Design · Make the screens belong together and the task work

“More polished” becomes concrete choices about hierarchy, layout, type, color, density and state. Design starts with user tasks and references, distinguishes new interfaces from existing-project corrections and faithful reconstruction, and uses page families, representative samples and real components to maintain consistency with intentional variants.

Maintained UI uses `design/UI_SPECIFICATION.md`, linked to the actual theme, tokens and components. Review checks the rendered interface and relevant user path. Try: “These pages feel messy. Find the causes and bring them together.” [Explore Design](skills/senmu-build-design/SKILL.md)

### Engineering · Reuse what works and repair the cause

Understand entrypoints, consumers, data and state before choosing an implementation. Engineering covers stack selection, architecture, frontend/backend contracts, language guidance, debugging and code review. It starts with capabilities already available in the project and mature components.

A repair returns to the original failure and affected consumers. You see the rationale, actual changes and checks that ran. Try: “This bug keeps coming back. Find its cause and fix it within the existing architecture.” [Explore Engineering](skills/senmu-build-engineering/SKILL.md)

### Project · Give new projects a start and existing ones clear rules

Project identifies roots, existing constraints, responsibilities and actual capabilities. New projects get the governance they need; existing projects reconcile standards through discovery and migration while preserving valid decisions. AGENTS.md provides working principles and routes; professional detail stays with its domain.

You get conventions that can be found, used and resumed: whether there is UI, who maintains its standard and where work continues. Try: “Take over this project, identify the missing conventions and put the necessary ones in place.” [Explore Project](skills/senmu-build-project/SKILL.md)

### Workflow · Make a process recoverable after interruption

Multiple agents, file-processing stages and external consoles often fail at handoffs. Workflow defines inputs, outputs, run identity, stage state, human steps and recovery. Source material, intermediates, deliverables and archives have distinct roles so a retry can resume from the right point.

It also helps design business agents and prompts. You get executable process contracts and specific handoffs. Try: “A failed batch always starts over. Make recovery and delivery explicit.” [Explore Workflow](skills/senmu-build-workflow/SKILL.md)

### Delivery · Know exactly how far the work has shipped

A commit, a successful build, a deployment and production verification establish different things. Delivery connects isolated branches and worktrees, parallel integration, versioned artifacts, release authority, rollback and environment checks through the project's adopted delivery routes.

You get an identified candidate, verification results, actual release state and recovery facts. Try: “Integrate this batch into a version and release through our existing process once the checks pass.” [Explore Delivery](skills/senmu-build-delivery/SKILL.md)

### Assurance · Turn a concern into an evidence-based conclusion

“Is this design wrong?” needs a defined subject, version, scope and standard. Assurance examines hypotheses through source, reproductions, comparisons or POCs. It separates facts, inferences and unknowns, then explains impact, remediation and re-review conditions.

You get traceable findings and priorities. Independence depends on actual reviewer separation; explicit audits and routine self-checks have different scopes. Try: “Assess this deployment plan objectively and show where the problems are.” [Explore Assurance](skills/senmu-build-assurance/SKILL.md)

### Learning · Turn a solved problem into reusable experience

Adding a new rule after every mistake eventually creates conflicting instructions. Learning checks the problem and improvement evidence before deciding whether it needs a local correction, a project lesson or a reusable BuildOS method. External guidance also passes applicability and duplication review.

You get selected lessons with a clear authoritative home. Try: “Review this rework: what is specific to this project, and what should improve our general methods?” [Explore Learning](skills/senmu-build-learning/SKILL.md)

These are peer capabilities selected for the task; one may be enough. Engineering loads Python, TypeScript, Go, Java, Rust and other guidance as needed. Runtime guidance is written in English; collaborate in Chinese, English, Japanese or another language.

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

Keep these facts continuous at a scale appropriate to the task. Progress can remain in issues or existing task records; maintained UI has its current standard in `design/UI_SPECIFICATION.md`. Governance migration preserves valid decisions, while project entrypoints and quality commands stay connected to the actual implementation.

**Fix the source of the problem before adding another gate.** Improve the requirement, responsibility, interface or default process that creates errors. Use tests and gates for material residual risk; make a small repair when the cause is clear. Reuse must still preserve business meaning, security, permissions and compatibility.

Connect understanding, design, implementation, verification and delivery at the scale of the task. Read more in the [system overview](docs/architecture/system-overview.md), [skill boundaries](docs/architecture/skill-boundaries.md) and [project artifact map](docs/architecture/project-artifact-map.md).

<a id="faq"></a>
## Common questions

**Does every edit load the entire rulebook?** No. Routine work already covered by project rules and tests may need no specialist skill. Other tasks load matching references. Actual loading depends on the client and task; file presence alone does not establish activation.

**Will it rewrite my project, commit or publish automatically?** Installation grants none of those permissions. Reading, editing, committing, pushing and production operations follow the user's authority and project rules. Read-only requests stay read-only; already approved work should not be interrupted by repeated approval rituals.

**Is this just another AGENTS.md?** No. AGENTS.md keeps frequently used project principles and navigation; skills provide task-specific methods; scripts and existing tools perform deterministic checks. They complement one another rather than copy the full manual.

The project entrypoint can route release/recovery to Delivery and its existing procedure/command; files alone do not prove adoption. Put stable actions in the existing script or CI, leaving applicability, necessary maintenance and outcome checks to the agent. Reuse the runner across versions and update it when the process changes; ordinary edits do not load the whole rulebook.

**How many tokens or bugs will it save?** There is no fixed percentage promise. The goal is less duplicate implementation, unrelated reading and rework, with correctness, security and maintainability first. Source tests, host activation and model performance require different evidence; see the [evaluation notes](tests/behavior/host-evaluation.md).

**What do the hooks do?** Supported full-plugin entrypoints supply a short governance prompt at lifecycle events. Skills-only adapters do not offer the same automatic injection. Feedback goes to a local review inbox, without automatic upload or project-rule rewriting. Review hooks on first enablement and when they change; see the [lifecycle notes](docs/architecture/hook-lifecycle.md) and [security notes](SECURITY.md).

<a id="maintenance"></a>
<a id="installation-updates-and-removal"></a>
## Version, updates and removal

The current source version is Senmu BuildOS `v2.32.0`. Source, private release, public marketplace availability and local installation are separate states. The badge above links to the public channel, not your installed version.

<!-- product-surface-review: 2.32.0 -->

This version strengthens the handoff from everyday requests to product, design and engineering, standardizes the maintained UI entrypoint and migration of existing guidance, and distinguishes an unassessed UI scope from no UI. The product introduction now explains each skill through its principles, methods and outcomes. Small changes remain lightweight. See [release notes](RELEASE_NOTES.md).

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
