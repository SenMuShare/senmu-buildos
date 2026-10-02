# Requirements and Product Iteration

This standard governs how product documents are created, transitioned, frozen, and reconciled. Templates define content; Engineering owns implementation, the project task owner owns execution state, and Delivery owns artifacts and release facts.

## 1. Document Responsibilities

```text
Optional user requirements
    -> owner assigns a version
Version PRD
    -> version technical design
    -> risk-based test cases
    -> current user-document walkthrough when usage contracts change
    -> development and acceptance
Current product specification
    -> current system specification when durable technical facts change
```

| Artifact | When | Sole responsibility | Template |
| --- | --- | --- | --- |
| `product/USER_REQUIREMENTS.md` | optional | durable ideas/feedback with adjacent status and target version | `USER_REQUIREMENTS.template.md` |
| `versions/<version>/PRD.md` | requirement drafting/planning and subsequent development | version goals, changes, behavior, acceptance | `PRD.template.md` |
| `versions/<version>/TECHNICAL_DESIGN.md` | every formal version entering development | how and why this version is implemented, including unchanged design carried forward | `TECHNICAL_DESIGN.template.md` |
| `versions/<version>/TEST_CASES.md` | version-level test design must persist | risk-matched cases derived from PRD | `TEST_CASES.template.md` |
| `product/PRODUCT_SPECIFICATION.md` | durable whole-product view is needed | complete current product facts | `PRODUCT_SPECIFICATION.template.md` |
| `engineering/SYSTEM_TECHNICAL_SPECIFICATION.md` | long-lived code needs a durable system view | complete current technical facts | `SYSTEM_TECHNICAL_SPECIFICATION.template.md` |

Map existing documents or external systems to these roles; never create a second truth set. Every formal development version has identifiable requirements and a technical account. Existing combined version documents may carry both as distinct sections. Small versions state the approved change, inherited design, affected implementation and verification briefly; they do not omit the technical account or expand empty headings. An ordinary task updates its existing version, not a new document set. Unversioned exploration does not acquire a formal version merely to satisfy this rule.

Get Started guides, tutorials, manuals, and CLI/SDK/API references remain with the project's documentation owner. When installation, configuration, public calls, or operating paths change, Product records the affected contract, acceptance entrypoint, and current official documentation location in the PRD without copying its text or creating a documentation site for a project with no durable user entrypoint.

Public README, website, store listing, and repository description are current product surfaces. Before a formal release, review positioning, audience, problem, capabilities, principles, boundaries, and install/use entrypoints against actual changes; update affected text and maintained languages. A version-number substitution is not content review. Record the result in one existing product owner, including evidence when no semantic change was needed; do not expose internal tasks, research sources, or unsupported outcomes.

## 2. Template Use

Follow the user's requested format. Preserve it in the existing product owner and reuse it across sessions and updates unless the user explicitly replaces or localizes it. A complete requested template retains its sections, explaining genuine non-applicability; unknown facts are not invented. Otherwise retain required scope/result content and only relevant optional modules. Remove writing comments, empty tables and unused optional fields, not unresolved decisions in drafts. Optional modules may be renamed, merged or repeated without losing facts; required feature sections may not. Keep small changes brief without inventing pages, interfaces or performance targets.

Templates outside an adopted format are outlines, not universal schemas, validators or approval flows. The following feature contract governs formal requirements by default; it does not force an artifact for every task.

## 2.1 Per-feature Requirement Contract

Use for formal requirement drafts, new-version planning and additions/updates during development. Ordinary discussion, exploration and raw-idea backlogs need no four-part reply or invented version. Do not rewrite accepted history merely to adopt this format.

Each feature/capability has its own name or existing ID, `需求对应版本号`, and exactly four ordered sections:

| Section | Required meaning |
| --- | --- |
| `1. 需求描述` | Usage scenario, background, problem, business goal and user need. |
| `2. 功能描述` | What the capability does, for whom, its scope and intended result. |
| `3. 功能逻辑` | Backend business behavior: triggers, rules, validation, decisions, state changes, data flow, boundaries, failure handling and observable results. |
| `4. 前端交互描述` | Elements, operation paths, feedback copy and applicable exceptions: disabled/unselectable controls, errors, empty states, validation failure, permissions, timeout and recovery. Explain trigger, UI response, message and next action. |

Version is metadata, not a fifth section, and means the target product version, not BuildOS's package version. One document-wide set cannot replace each feature's set. Small changes may use one sentence per part, never omit parts. Identify inherited backend rules when unchanged. Non-UI capabilities keep section 4 with a reason for non-applicability. Unknown versions remain explicit draft questions.

Keep observable acceptance in sections 3/4 and shared acceptance authority at version level, not a fifth feature section. Reference shared rules precisely while explaining affected behavior. Components, functions, schemas and deployment belong in technical design; neither code nor images replace the written requirement.

## 2.2 Clarification and Output Review

For each feature, check scenario, goal, scope, normal flow, rules, permissions, state/data, frontend feedback, exceptions and recovery together; compare settled decisions and affected features for omissions or conflicts. Retrieve existing facts first. Discuss consequential unknowns in multiple rounds as needed, stating gap, impact, recommendation and choice. Reuse settled answers; distinguish decisions from assumptions/advice. Mark unresolved draft content in its relevant section and block only implementation whose outcome would otherwise be guessed.

Review per-feature version, four ordered substantive sections, semantic consistency, exceptions and visual associations. For the default Chinese format, use the read-only [structure checker](../scripts/check_requirement_structure.py) at the actual installed Skill path:

```bash
python3 <product-skill-root>/scripts/check_requirement_structure.py --document <existing-PRD.md>
# Allow an explicitly unresolved target version only in a draft:
python3 <product-skill-root>/scripts/check_requirement_structure.py --document <existing-PRD.md> --draft
```

It checks recognizable feature blocks, versions, section order and nonempty content, not coverage, business correctness, meaningful exceptions, adoption, asset availability or archival completion. Review those from evidence. Do not apply it to a different user-adopted format or turn it into a universal Hook/approval gate.

## 2.3 Requirement-linked Visual Assets

Preserve requirement-related prototypes/UI supplied by the user or adopted from any human/AI source. Clear selection establishes adoption scope without another archive instruction. Record adopted, partially adopted, reference-only, superseded or unresolved disposition and what is included/excluded; choosing layout does not approve sample prices, copy, fields or business rules.

Save available files in the project's existing authorized design/prototype location or document store, not only chat or the installed BuildOS package. Embed or reference them in section 4 of each affected feature, identifying requirement version and feature/ID, exact file or durable design revision/frame, disposition and scope. Use the existing asset index, design record or colocated note for a backlink to the requirement. Reuse one asset across multiple features or multiple state images per feature; do not copy a file for every relation or create a parallel registry.

Read back saved artifacts and requirement anchors before claiming linkage. Temporary links require an authorized copy or revision-stable snapshot; a live editable URL is not a frozen baseline. Preserve source and usable snapshots under existing access/retention rules. Missing bytes, permission or durable storage must be recorded with their impact, never replaced with fictional paths or archival claims. Do not publish private material or delete originals/alternatives without authority.

On replacement, update current forward/back links, disposition and scope while preserving prior requirements' exact design basis through existing revision history. Current specifications keep applicable adopted references; frozen PRDs keep historical ones. Reconcile image/text conflicts with approved business decisions and the owner, not automatically with the newest image. Images never replace written exceptional states and recovery.

Without relevant assets, omit the attachment subsection: do not generate images, empty ledgers or blockers. Unrelated uploads and every intermediate AI variation need not become requirement evidence. Product owns requirement association/adoption meaning, Design owns design decisions, and the existing material owner retains custody.

## 3. From Requirement to Version PRD

A backlog is optional. The owner may record ideas first or proceed directly to a version PRD. Match discussion depth to uncertainty and impact:

- **Exploratory:** when direction, user problem, or value is uncertain, compare goals, evidence, counterexamples, alternatives, and stopping conditions; output candidates and unknowns, not a frozen scope.
- **Boundary-focused:** for a clear, local, limited-risk change, clarify only what affects scope, behavior, acceptance, data, permission, cost, or risk; produce the minimum sufficient decision.
- **Architecture-level:** for cross-role workflows, state machines, permissions, billing, core data, migrations, or multiple release units, define end-to-end flow, invariants, recovery, non-goals, and observable acceptance before Engineering design.

Do not repeat questions or await separate approval when owners and context suffice. Unknowns block only when they would silently change outcome. Keep discussion in the task owner; the PRD stores current conclusions.

When overloaded terms or inconsistent names would change behavior, permissions, billing, state or acceptance, resolve the concept against existing decisions and a concrete boundary scenario. For example, distinguish retrying the same intent from starting a new potentially billable intent when that distinction matters; do not invent the project's answer. Retrieve discoverable facts yourself and ask only for a material unresolved choice, with a recommendation and consequence. Group independently answerable questions rather than exhausting future branches. Record adopted meaning in the existing product/terminology owner within write authority, then reuse it in technical mappings. Do not create a new CONTEXT file, ADR or glossary service for each term, re-ask settled choices, or turn observed code into permission to change approved intent.

When a term needs clarification, keep its canonical name, short meaning, easily confused alternative and one boundary example together at that existing owner. For example, distinguish submission from verified completion and same-intent retry from a new request; the project's approved contract determines the actual semantics. A settled glossary entry is reused, not re-interviewed. At intake, distinguish already implemented, rejected, deferred and awaiting evidence; retain the reason and revisit condition rather than treating every closed item as forbidden work.

Assign implementation-ready work from product facts to the current open version, successor version, or uncommitted backlog. Add it to an open version when goal, acceptance, and delivery timing align. Ask only when placement would change scope/timing and cannot be inferred. Future unimplemented work records version intent without creating a code branch.

Follow project version policy and approved change, not version numbers alone. Fixes, compatible features, and incompatible changes may suggest patch/minor/major candidates; retain product roles such as current patch batch, later feature version, or successor until scope stabilizes.

When a backlog exists, put status and target version beside each item; do not add a relationship table or complex state machine. Add a stable ID only for durable independent tracking. Use opportunity assessment for high investment, weak evidence, uncertain direction, or difficult rollback, not low-cost reversible experiments.

Each version in development has one PRD that removes material ambiguity for Product, Engineering, testing, and AI:

- organize UI products by page, capability, and concrete requirement;
- organize non-UI capabilities by flow, trigger, rules, result, exceptions, and acceptance within the same four feature sections;
- state only user-observable or business-required behavior across frontend/backend; put components, functions, schemas, and deployment in technical design.

Maintain one version requirement/defect list in the PRD or equivalent owner, not one per item, agent, or branch. Each entry needs type, target/acceptance, result state, and implementation/verification evidence or disposition. Use project states, or concise states distinguishing pending, analyzed, implementing, implemented-unverified, verified, and excluded. Execution steps remain in the task owner.

A field, copy, or local behavior change may need only a brief sentence in each required feature section, preserving version, change and acceptance. Expand details for actual workflow, state, permission, billing, data, compliance, or release-unit risk. A fix that restores the current specification does not rewrite approved product behavior. Track it in the existing version requirement/defect record and keep its implementation and verification account in the version technical design.

Resolve the object and intent of cancellation from the request and existing product decisions. Cancelling unimplemented work removes that work from the plan; stopping a run follows its cancellation contract; explicitly retiring an existing capability removes its executable entrypoints under the approved retirement scope. Do not infer permanent capability removal from the word cancel alone. Record replacement behavior and required historical-data, compliance, compatibility or rollback boundaries. Retirement of code never by itself authorizes destroying business data, audit records or recovery evidence.

## 4. Development, Testing, and Acceptance

The PRD is product input, not technical design or execution state:

- Engineering maintains the version technical design using `TECHNICAL_DESIGN.template.md` or its existing equivalent. Explain unchanged design by reference; record new decisions and their reasons before implementing the affected boundary.
- Engineering creates `TEST_CASES.template.md` only when version-level tests must persist, matching PRD structure and risk.
- The project's Durable Task State Owner stores decomposition and progress.

Before implementation, require only sufficient goal, change, critical rules, failure/permission/data impact, and observable acceptance; unresolved items must not silently change scope or acceptance. Low-risk changes do not need an independent review or full document chain.

The PRD or equivalent owner declares **Acceptance Authority**: who may move the exact candidate from `implemented` to `accepted`, which objective checks may be delegated to agents/tests, and which product meaning, experience tradeoffs, or business risks require the owner. Verification may be delegated; acceptance and release authority cannot be self-granted by implementers, green tests, or documents. Acceptance binds a candidate identity. Later code, config, behavior, or affected user-document changes invalidate only the relevant accepted scope.

When a version changes installation, configuration, user operation, public API, CLI, SDK, or recovery, list affected current documentation and observable results. Acceptance walks one affected core task from a representative documented start; commands, examples, and results must match the candidate. Builds, valid links, and polished prose are partial evidence only. Do not manufacture tutorials for products without external users or durable entrypoints.

Implementation completion, passing tests, product acceptance, and release are four distinct facts.

## 5. Reconcile Current Specifications

After acceptance, record authority, candidate, and evidence; freeze the version PRD, technical design and any test cases, then:

- merge effective behavior and applicable adopted-design references into the relevant `PRODUCT_SPECIFICATION.md` section and remove superseded current logic;
- merge durable technical changes into `SYSTEM_TECHNICAL_SPECIFICATION.md` and remove superseded facts;
- rely on Git/version documents and preserved asset revisions for history rather than accumulating generations in current specifications;
- continue reading deployment, production, and rollback from Delivery facts.

Large products may split current specifications into indexes and page/module documents while retaining one logical current owner each.

## 6. New and Established Projects

For new projects, these paths are default responsibility mappings, not mandatory empty scaffolding:

```text
product/USER_REQUIREMENTS.md              # optional
product/PRODUCT_SPECIFICATION.md          # current product facts
versions/<version>/PRD.md                 # requirement draft and current development version
versions/<version>/TECHNICAL_DESIGN.md    # each formal development version; concise when unchanged
versions/<version>/TEST_CASES.md          # optional, derived from PRD
engineering/SYSTEM_TECHNICAL_SPECIFICATION.md # current technical facts
```

For established projects, inventory existing product documents, UI, code, interfaces, tests, and runtime facts, then map real owners. If a current overview is absent, reconstruct product and system specifications from evidence while labeling confirmed facts, inferences, conflicts, and unknowns; do not invent historical backlogs or PRDs. Apply the transition to future versions without reorganizing everything for directory aesthetics.

Directories, transitions, and templates must not create empty documents, duplicate text, approval waits, or useless context.
