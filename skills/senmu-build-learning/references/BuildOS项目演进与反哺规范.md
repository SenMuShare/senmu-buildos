# BuildOS Evolution and Upstream Feedback

Use this standard to convert validated cross-project learning into reviewable improvements to the Senmu BuildOS source project. The feedback target is the complete BuildOS Git project, not a private directory inside one installed Skill.

## 1. Keep Three Objects Distinct

| Object | Meaning | Authority boundary |
| --- | --- | --- |
| Application project | Software, workflow, content, experiment, or composite project using BuildOS | Its own entrypoints, facts, tasks, lessons, Git, and release/delivery units |
| BuildOS source project | Independent Git repository maintaining the plugin product | Repository root, manifests, Skills, Hooks, docs, scripts, tests, migrations, and version history |
| Installed BuildOS instance | Plugin and Skills installed or cached for Codex execution | Executable derivative; not maintenance authority unless installation explicitly links source |

Close application-project learning in that project first. Raw local-inbox items are not rules. Only items centrally adjudicated as `buildos_candidate` enter the BuildOS source project. Never edit an installed instance directly from an application project or merge the two projects' Git histories into a fictitious shared completion state.

## 2. Admission to the BuildOS Project

A candidate must satisfy all of the following:

- Root cause and effective treatment have reviewable evidence, not just chat judgment or one accidental result.
- The issue recurs across projects or is demonstrably a stable mechanism affecting several project forms.
- It can be stated without customer data, accounts, secrets, personal paths, or unpublished business facts.
- The rule changes an agent's actual decision, artifact, or verification—not merely asks for greater care.
- Expected benefit exceeds added reading, routing, execution, maintenance, and context cost.

Otherwise retain it in the application project's Work Log, Lessons Learned Register, or specialist standard.

Runtime value is not established by token counts, length, load frequency, or green tests alone. State which decision or artifact changes, which repeated implementation, wrong edit, invalid verification, or risk is prevented, why the result is correct, and the added costs. Tokens are a cost, not the optimization objective. A short rule with no observable behavior or necessary risk-control benefit does not qualify. Static behavior matrices freeze expectations; real candidate-environment tasks must still verify routing, implementation direction, and misleading effects.

For public webpages, PDFs, books, repositories, third-party Skills, or team manuals that are not project-experience candidates, use [Engineering Knowledge Distillation and Standard Promotion](工程知识蒸馏与标准晋级规范.md). External reputation does not grant rule authority.

## 3. Whole-Repository Impact Analysis

On entry to the BuildOS source project, confirm Git root, branch, baseline, uncommitted changes, and authorized modification scope, then find the unique existing owner. Check at least:

1. Whether README or product positioning changes.
2. Whether system model, Skill boundaries, project artifacts, and Harness responsibilities under `docs/architecture/` remain consistent.
3. Which Skill description, entrypoint, reference, or asset owns the meaning.
4. Whether initializer, validator, Hook, plugin metadata, or behavior tests consume the changed rule.
5. Whether Changelog, Roadmap, version, or release notes require synchronization.

Whole-repository analysis does not require editing every file. A final change may touch one Markdown file or Skill, but must explain why other consumers are unaffected. When a concept crosses owners, update relationships and routing rather than duplicating the full rule.

## 4. Implementation Order

1. Freeze candidate source, problem, scope, evidence, and expected change.
2. Search existing BuildOS rules, adjacent responsibilities, and migrations; classify as supplement, correction, merge, replacement, or rejection.
3. Select one semantic owner. Use `$skill-creator` when Skill entry, structure, or triggering changes.
4. Correct the principle, responsibility, template, script, or default production path that creates the problem. Gates cover only material residual risk that cannot be removed.
5. Synchronize affected routes, docs, tests, and migration declarations.
6. Run matching Skill, package, script, and behavior checks; record unverified runtime assumptions.
7. Commit, push, version, tag, candidate-install, or publish only under separate explicit authority.

## 5. Version and Git Rules

- Version BuildOS as one Git repository and plugin package, not independent products per Skill.
- One change may cross Skills, Hooks, docs, and scripts and receives project-level review and verification.
- Application fixes and BuildOS generalization commits occur in their respective repositories; evidence links relate them without sharing a false completion state.
- Local source changes, candidate package generation, local installation, and public release are distinct states.

## 6. Feedback Result

Every BuildOS feedback result states:

- the type of project evidence and how private facts were removed;
- why the finding is project-specific or cross-project;
- which source-project owners changed and why whole-repository closure is complete;
- which checks ran and which behaviors still need candidate-environment verification;
- whether this is source-only and the separate states of commit, install, activation, and publication.
