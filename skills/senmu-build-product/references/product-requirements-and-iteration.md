# Requirements and Product Iteration

This standard governs how product documents are created, transitioned, frozen, and reconciled. Templates define content; Engineering owns implementation, the project task owner owns execution state, and Delivery owns artifacts and release facts.

## 1. Document Responsibilities

```text
Optional user requirements
    -> owner assigns a version
Version PRD
    -> optional technical design
    -> risk-based test cases
    -> current user-document walkthrough when usage contracts change
    -> development and acceptance
Current product specification
    -> current system specification when durable technical facts change
```

| Artifact | When | Sole responsibility | Template |
| --- | --- | --- | --- |
| `product/USER_REQUIREMENTS.md` | optional | durable ideas/feedback with adjacent status and target version | `USER_REQUIREMENTS.template.md` |
| `versions/<version>/PRD.md` | version enters development | version goals, changes, behavior, acceptance | `PRD.template.md` |
| `versions/<version>/TECHNICAL_DESIGN.md` | durable implementation decisions need explanation | how the version is implemented | `TECHNICAL_DESIGN.template.md` |
| `versions/<version>/TEST_CASES.md` | version-level test design must persist | risk-matched cases derived from PRD | `TEST_CASES.template.md` |
| `product/PRODUCT_SPECIFICATION.md` | durable whole-product view is needed | complete current product facts | `PRODUCT_SPECIFICATION.template.md` |
| `engineering/SYSTEM_TECHNICAL_SPECIFICATION.md` | long-lived code needs a durable system view | complete current technical facts | `SYSTEM_TECHNICAL_SPECIFICATION.template.md` |

Map existing documents or external systems to these roles; never create a second truth set.

Get Started guides, tutorials, manuals, and CLI/SDK/API references remain with the project's documentation owner. When installation, configuration, public calls, or operating paths change, Product records the affected contract, acceptance entrypoint, and current official documentation location in the PRD without copying its text or creating a documentation site for a project with no durable user entrypoint.

Public README, website, store listing, and repository description are current product surfaces. Before a formal release, review positioning, audience, problem, capabilities, principles, boundaries, and install/use entrypoints against actual changes; update affected text and maintained languages. A version-number substitution is not content review. Record the result in one existing product owner, including evidence when no semantic change was needed; do not expose internal tasks, research sources, or unsupported outcomes.

## 2. Template Use

After choosing to create an artifact, follow the user's requested format. For a complete template, retain sections and mark genuinely irrelevant content N/A; missing facts remain unknown. Otherwise copy its template and apply these defaults:

1. retain enough required content to identify the artifact, scope, and result; required does not mean every task needs the artifact;
2. retain optional content only when the product, change, ambiguity, or risk needs it;
3. remove writing comments, empty tables, `TBD`, and rows of `not applicable`;
4. rename, merge, or repeat modules as useful without losing facts required for implementation/acceptance;
5. keep small changes minimal; template prompts do not require expansion of every page, interface, permission, or performance topic.

Standardize document responsibility and broad organization, not heading count, fields, or length. Treat templates as outlines, not schemas, validators, or approval flows.

## 3. From Requirement to Version PRD

A backlog is optional. The owner may record ideas first or proceed directly to a version PRD. Match discussion depth to uncertainty and impact:

- **Exploratory:** when direction, user problem, or value is uncertain, compare goals, evidence, counterexamples, alternatives, and stopping conditions; output candidates and unknowns, not a frozen scope.
- **Boundary-focused:** for a clear, local, limited-risk change, clarify only what affects scope, behavior, acceptance, data, permission, cost, or risk; produce the minimum sufficient decision.
- **Architecture-level:** for cross-role workflows, state machines, permissions, billing, core data, migrations, or multiple release units, define end-to-end flow, invariants, recovery, non-goals, and observable acceptance before Engineering design.

Do not repeat questions or await separate approval when owners and context suffice. Unknowns block only when they would silently change outcome. Keep discussion in the task owner; the PRD stores current conclusions.

Assign implementation-ready work from product facts to the current open version, successor version, or uncommitted backlog. Add it to an open version when goal, acceptance, and delivery timing align. Ask only when placement would change scope/timing and cannot be inferred. Future unimplemented work records version intent without creating a code branch.

Follow project version policy and approved change, not version numbers alone. Fixes, compatible features, and incompatible changes may suggest patch/minor/major candidates; retain product roles such as current patch batch, later feature version, or successor until scope stabilizes.

When a backlog exists, put status and target version beside each item; do not add a relationship table or complex state machine. Add a stable ID only for durable independent tracking. Use opportunity assessment for high investment, weak evidence, uncertain direction, or difficult rollback, not low-cost reversible experiments.

Each version in development has one PRD that removes material ambiguity for Product, Engineering, testing, and AI:

- organize UI products by page, capability, and concrete requirement;
- organize non-UI capabilities by flow, trigger, rules, result, exceptions, and acceptance;
- state only user-observable or business-required behavior across frontend/backend; put components, functions, schemas, and deployment in technical design.

Maintain one version requirement/defect list in the PRD or equivalent owner, not one per item, agent, or branch. Each entry needs type, target/acceptance, result state, and implementation/verification evidence or disposition. Use project states, or concise states distinguishing pending, analyzed, implementing, implemented-unverified, verified, and excluded. Execution steps remain in the task owner.

A field, copy, or local behavior change may need only version, change, and acceptance. By default expand template areas for actual workflow, state, permission, billing, data, compliance, or release-unit risk. A fix that restores the current specification changes code/tests, not the PRD.

When the owner says a feature is no longer wanted, should be deleted, cancelled, or permanently removed, default to **permanent retirement**: no user, system, or external caller can trigger it. Acceptance states replacement behavior and historical-data read/migration/compliance boundaries. Treat hiding, pausing, gradual disablement, or retained rollback/compatibility as the goal only when explicitly requested, with scope and exit conditions. Permanent retirement does not authorize destruction of business data, audit records, or rollback evidence.

## 4. Development, Testing, and Acceptance

The PRD is product input, not technical design or execution state:

- Engineering creates `TECHNICAL_DESIGN.template.md` only when implementation decisions need durable explanation.
- Engineering creates `TEST_CASES.template.md` only when version-level tests must persist, matching PRD structure and risk.
- The project's Durable Task State Owner stores decomposition and progress.

Before implementation, require only sufficient goal, change, critical rules, failure/permission/data impact, and observable acceptance; unresolved items must not silently change scope or acceptance. Low-risk changes do not need an independent review or full document chain.

The PRD or equivalent owner declares **Acceptance Authority**: who may move the exact candidate from `implemented` to `accepted`, which objective checks may be delegated to agents/tests, and which product meaning, experience tradeoffs, or business risks require the owner. Verification may be delegated; acceptance and release authority cannot be self-granted by implementers, green tests, or documents. Acceptance binds a candidate identity. Later code, config, behavior, or affected user-document changes invalidate only the relevant accepted scope.

When a version changes installation, configuration, user operation, public API, CLI, SDK, or recovery, list affected current documentation and observable results. Acceptance walks one affected core task from a representative documented start; commands, examples, and results must match the candidate. Builds, valid links, and polished prose are partial evidence only. Do not manufacture tutorials for products without external users or durable entrypoints.

Implementation completion, passing tests, product acceptance, and release are four distinct facts.

## 5. Reconcile Current Specifications

After acceptance, record authority, candidate, and evidence; freeze the version PRD and any technical design/test cases, then:

- merge effective behavior into the relevant `PRODUCT_SPECIFICATION.md` section and remove superseded logic;
- merge durable technical changes into `SYSTEM_TECHNICAL_SPECIFICATION.md` and remove superseded facts;
- rely on Git/version documents for history rather than accumulating generations in current specifications;
- continue reading deployment, production, and rollback from Delivery facts.

Large products may split current specifications into indexes and page/module documents while retaining one logical current owner each.

## 6. New and Established Projects

For new projects, these paths are default responsibility mappings, not mandatory empty scaffolding:

```text
product/USER_REQUIREMENTS.md              # optional
product/PRODUCT_SPECIFICATION.md          # current product facts
versions/<version>/PRD.md                 # current development version
versions/<version>/TECHNICAL_DESIGN.md    # optional
versions/<version>/TEST_CASES.md          # optional, derived from PRD
engineering/SYSTEM_TECHNICAL_SPECIFICATION.md # current technical facts
```

For established projects, inventory existing product documents, UI, code, interfaces, tests, and runtime facts, then map real owners. If a current overview is absent, reconstruct product and system specifications from evidence while labeling confirmed facts, inferences, conflicts, and unknowns; do not invent historical backlogs or PRDs. Apply the transition to future versions without reorganizing everything for directory aesthetics.

Directories, transitions, and templates must not create empty documents, duplicate text, approval waits, or useless context.
