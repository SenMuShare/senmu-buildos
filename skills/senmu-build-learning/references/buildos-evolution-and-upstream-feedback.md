# BuildOS Evolution and Upstream Feedback

Use this standard for authorized repair of concrete BuildOS component defects and for justified promotion of reusable engineering knowledge into the BuildOS source project. The feedback target is the complete BuildOS Git project, not a private directory inside one installed Skill.

## 1. Keep Three Objects Distinct

| Object | Meaning | Authority boundary |
| --- | --- | --- |
| Application project | Software, workflow, content, experiment, or composite project using BuildOS | Its own entrypoints, facts, tasks, lessons, Git, and release/delivery units |
| BuildOS source project | Declared product source root, either an independent repository or a subtree of a maintenance workspace | Repository revision plus source-relative path, manifests, Skills, Hooks, docs, scripts, tests, migrations and version history |
| Installed BuildOS instance | Plugin and Skills installed or cached for Codex execution | Executable derivative; not maintenance authority unless installation explicitly links source |

Close application-project learning in that project first. Raw local-inbox items are not rules. Only items centrally adjudicated as `buildos_candidate` enter the BuildOS source project. Never edit an installed instance directly from an application project or merge the two projects' Git histories into a fictitious shared completion state.

## 2. Admission to the BuildOS Project

Keep defect repair and general policy promotion distinct. A concrete Skill, template, script, Hook or routing defect may enter the existing candidate/adjudication path with reviewable source evidence, a counterexample or a reproducible fixture from one project. Authorized repair does not require the defect to cause incidents in several projects first, or require proof of the cure before repair may begin.

For a new general policy, establish its mechanism, affected decisions, scope, exceptions and maintenance/context cost. Evidence may include engineering reasoning, applicable specifications, source analysis, observed tasks and focused verification; its strength must match the conclusion. A personal preference or one unsatisfactory answer is not automatically a universal rule.

Keep raw feedback and author-private work outside the distributable source tree. Product rules, tests and contributor documentation must work without a private sibling directory; authorized decisions may link a private candidate to its resulting source change without copying raw evidence. Keep private data, credentials, local paths and unpublished business facts out of public proposals. Find the existing semantic owner and distinguish changes to source, installed instances and release channels. The candidate grants no write, install or release authority.

Direct checks support bounded source corrections. A semantic walkthrough is not a real model run; actual behavior or performance claims require corresponding observations. No universal A/B or multi-model competition is a prerequisite to an engineering correction, and passing structural checks alone does not prove reduced Token use.

For external webpages, papers, repositories or Skills, use [Engineering Knowledge Distillation and Standard Promotion](engineering-knowledge-distillation-and-standard-promotion.md). External reputation does not create project authority.


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
7. Complete source changes, matching checks, and scoped local commits within the authorized BuildOS improvement task. Push, version, tag, candidate-install, and publication follow their own applicable authority; feedback intake alone authorizes none of them.

## 5. Version and Git Rules

- Version BuildOS as one product source tree and plugin package, not independent products per Skill. A containing private workspace is not a public release artifact or public history.
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
