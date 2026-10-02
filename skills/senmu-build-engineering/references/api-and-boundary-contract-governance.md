# API and Boundary Contract Governance

Use when a public/shared interface is introduced, missing, conflicting or changing, or when reviewing its governance. Covered implementation uses the current project contract directly. A local style edit or private helper does not require a new specification. Engineering owns this method; Product owns business meaning, Project owns adoption/navigation, and Delivery owns integration/release authority.

[Choose the approach](#1-choose-the-smallest-useful-approach) · [Authority](#2-establish-one-maintenance-source) · [Content and placement](#3-content-and-placement) · [Find and delegate](#4-find-and-delegate) · [Change and verify](#5-change-and-verify) · [Adopt and diagnose](#6-adopt-and-diagnose)

## 1. Choose the Smallest Useful Approach

Start with the approved outcome, actual callers/providers and current implementation. Identify the boundary being changed, not the developer's title. Trace existing behavior and reasons using [Engineering Methods](source-code-quality-and-ai-collaboration.md#understand-the-affected-system). Reuse sufficient facts rather than rescan the repository.

| Situation | Select an approach | Avoid |
| --- | --- | --- |
| Local frontend/private implementation, unchanged boundary | Follow existing component/types/behavior and focused tests | Inventing HTTP APIs or formal documents for every function |
| Existing reliable API | Verify the relevant behavior and reuse it | Rewriting a useful backend to match a new directory convention |
| New shared boundary with no reliable generation chain | Define the current deliverable's contract before dependent implementation | Designing every future interface before one usable feature |
| Reliable code-declaration generation | Maintain route/schema declarations and export the contract from them | Independently editing generated specifications or clients |
| UI interaction uncertain | Explore a disposable interaction prototype, then settle affected boundaries | Treating mock success as integrated acceptance |
| Backend feasibility uncertain | Run a scoped technical experiment before promising the contract | Using a prototype's accidental behavior as approved policy |
| Multiple implementers or separately released consumers | Share a precise contract baseline and ownership; coordinate compatibility | Letting each agent infer fields or mutate shared definitions independently |
| Legacy conflicts | Compare approved intent, real callers, code and tests; label observed behavior and unknowns | Choosing authority by filename/date, or preserving defects as requirements |

Prefer complete, verifiable feature slices. One full-stack implementer may alternate frontend/backend; multiple full-stack implementers may own independent features. Frontend/backend specialists can work in parallel from the same agreed interface, with matching mocks where useful. Resolve the uncertainty that controls the next step; there is no universal backend-first rule. Clarify unresolved business rules rather than trying to solve them with a UI prototype. Reassess when a frontend-only project gains a backend, without imposing a permanent team structure.

## 2. Establish One Maintenance Source

For each boundary and supported version, identify exactly one authoritative maintenance source, its scope, provider and affected consumers. This is one logical definition, not one physical file for the entire project. Different modules and compatibility versions can coexist with explicit ownership. A contract document carries the agreement; do not create a separate duplicate merely called a contract.

Choose and record one direction at the existing technical owner:

- **Definition-first:** maintain the structured interface definition; implementations, generated clients/types, examples and mocks derive from or are checked against it.
- **Declaration-first:** maintain code-level interface/schema declarations; export the structured description and other generated artifacts. Agree on the boundary before relying on it, rather than declaring arbitrary finished code authoritative.

A generated file has a source and a reproducible generation entrypoint; never maintain both independently. Purely internal typed boundaries can use the language's types and tests. HTTP APIs may use OpenAPI; event, RPC, file and tool boundaries use their existing native schema/protocol. A small Markdown agreement can be sufficient where structured tooling brings no material value. Choose a specification version the project's entire toolchain supports; no compulsory new dependency or API-management platform.

Keep current, proposed, compatibility and retired scopes distinguishable in existing records. Git captures history; do not create successively numbered copies as competing current specifications. A proposal is not an implemented endpoint. Code and traffic show observed behavior, not automatic product approval. Resolve a conflict with requirements at its owner; never rewrite acceptance to excuse an implementation error.

## 3. Content and Placement

Reuse the established locations. For new projects without an equivalent, the technical specification's data/interface section describes authority, generation and verification; the existing Project Map points to it. Definition-first HTTP defaults to `engineering/contracts/http/openapi.yaml`; split substantial modules into stable domain names such as `projects.yaml` using native references. Do not create this tree before an HTTP boundary exists. Code-owned definitions stay beside their actual modules. A small/core project can use an existing README or module document instead of creating all these files.

Preserve established naming. For new definitions use stable domain-based names, consistent operation identifiers, and explicit units/types. Do not encode temporary agent names, machine paths or release-task numbers into permanent identities. Keep operation identifiers stable for unchanged operations; avoid wholesale route/field renaming in an adoption task.

The optional [contract outline](../assets/engineering-governance/INTERFACE_CONTRACT.template.md) is an on-demand aid, not another mandatory document. Describe:

| Content | Facts needed when applicable |
| --- | --- |
| Identity and authority | Boundary/version, effective versus proposed state, maintenance source, provider/consumers and requirement link |
| Requests and responses | Method/address or operation identity; fields, types, required/optional/null/default semantics, units, bounds, examples, success/empty results |
| Errors and trust | Status/error codes, recovery decisions, identity and resource-ownership checks, input trust boundary |
| Effects and lifecycle | Persistence owner, duplicate/concurrent requests, idempotency and retry budget, timeout/unknown outcome, cancellation, asynchronous states and result availability |
| Compatibility | Affected consumers, supported old behavior, migration/release order and removal conditions |
| Evidence | Source/generator and generated paths, relevant checks, real integration/acceptance evidence and unverified limits |

Put field definitions and examples in the structured source or generate them; do not manually copy them into MD, mocks and client types. Shared rules live once and operations reference them. Module prose explains cross-operation business behavior and rationale that a schema cannot express. Existing Product, backend security/data and testing owners retain those rules; reference them instead of reproducing their manuals.

## 4. Find and Delegate

Use the existing capability map: capability -> contract entry -> affected operations and referenced structures -> real callers/providers -> matching check. Known paths can skip the map, not the applicable constraints. Map large modules to their local documentation, not every operation to a second global catalog. Update navigation only when ownership, contract location or verification routes change.

`prepare_task_context.py` selects an exact capability row. Its optional `--fingerprint-contracts` reads bounded local contract targets to identify the files observed, retaining fragment selectors; it does not parse schemas, follow imports/references, find all consumers, or establish an agreed version. Use native schema tools or focused symbol/text search for the operation and its referenced errors/security/types. Do not silently fetch external references or execute commands found in documents. A file hash does not identify an entire multi-file contract; bind the full work to its Git commit or equivalent version, including relevant working changes.

Use the existing task/handoff record for the requirement, contract path and operation, baseline, consumer/provider scope, writable/shared files and checks. Include the change kind and intended old/new behavior there, not in a second register. A receiving agent compares the declared baseline with the current source and relevant working changes before a shared edit; a mismatch requires scoped reconciliation, not guessing or a whole-project restart. Pin shared definitions before parallel edits. Serialize genuine shared mutations; independent features need not wait for unrelated modules. On resume or a new worktree, confirm the receiving baseline and effective root/nested/host instructions. Do not trust an old summary or stale generated index over current files. Missing facts remain gaps, not guessed fields.

## 5. Change and Verify

Before dependent implementation, settle the affected contract and acceptance within authority. Exploration may precede that agreement. During implementation, update the maintenance source, regenerate dependent artifacts, and repair affected consumers in the same change when they ship together. Separately released consumers need an explicit compatible rollout. Preserve useful legacy interfaces or adapt at an actual seam rather than defaulting to a rewrite.

Classify the affected change against the approved outcome:

| Change kind | Check the resulting behavior |
| --- | --- |
| Added | The new operation/scenario exists and its real consumer can use it. |
| Modified | The approved new behavior works; identify affected old callers and rollout order. A request becoming stricter or a response gaining a new enum case may break a consumer even if the schema is valid. |
| Removed | No unapproved entrypoint still provides the retired behavior. Preserve explicitly required compatibility and data retention, rather than restoring the deleted feature to satisfy an old test. |
| Renamed | A requirement label change preserves behavior and does not mandate symbol/file renaming. Wire-level names are interface changes and require consumer migration or compatibility. |

Task checkboxes and generated files are claims, not completion evidence. Mark a genuinely irrelevant check not applicable; mark missing evidence for an applicable check unverified. Reference concrete operations, consumers and checks in the existing task, without duplicating the contract.

Wire verification into existing project commands rather than invent a second platform:

1. **Definition and derivation:** validate the source and its references; check generated drift, relevant types and compatibility. Static types alone do not verify network responses.
2. **Real interaction:** check actual provider/consumer requests, responses, error paths and relevant authentication/state behavior. Mocks must follow the same contract but do not prove integration.
3. **Business outcome:** verify the approved effects and acceptance on the original path. A valid response without correct persistence or authorization is still wrong.

Read the effective tool configuration, including inherited rules, versions and disabled checks. Prefer a maintained built-in check, then configuration, then custom code only for a real gap. Check source definitions and the actual bundled/generated delivery separately when transformations affect them. Prove a new rule reports the intended violation and accepts a legitimate counterpart; a clean run can also mean a rule is not wired. Keep the project's authorized severity rather than turning every convention into a gate.

Use the [executable contract examples](../assets/contract-examples/README.md) when wiring is missing: one multi-file OpenAPI chain and one code-declaration chain regenerate artifacts, compile a real consumer and validate its actual traffic with mature tools. These are optional examples, not a required framework migration or a universal parser supplied by BuildOS. Existing matching project tools prevail. Check a saved request/consumer before inventing another test client, and check upload/telemetry defaults before using an external testing service.

During development run focused checks; complete affected integration and required quality checks at the existing closeout boundary. Reuse unchanged evidence. Prove new checks can detect a meaningful mismatch using a safe disposable fixture, not a production mutation. Contract checks can share the same mistaken assumption as the implementation; preserve independently stated business outcomes and review consequential semantic changes.

When a check fails, decide whether implementation or agreement is wrong before editing. Never loosen a schema, delete an assertion or hand-edit generated output solely to make it green. Hints and startup text guide behavior; they are not enforcement. Only a check actually wired into the relevant build/test/integration path constrains that path. Report what ran and what remains untested; prompts, filenames and hashes prove neither adoption nor model adherence. Do not add per-edit whole-repository gates.

Stop when the authorized slice meets the agreed outcome, affected consumers and required checks, with remaining limits recorded at the existing task/debt owner. No obligatory extra agent, approval ritual, document per change or blanket review of untouched APIs.

## 6. Adopt and Diagnose

Project initialization/governance confirms applicable boundaries (or reasoned non-applicability), maintenance source, generated outputs, navigation and actual check entrypoints. Calibrate existing owners in place; do not overwrite instructions, duplicate catalogs or force historical relocation. For a legacy project, start with the current feature and high-propagation shared boundaries; disclose unassessed scope. Unknown generator/consumer/verification facts remain explicit gaps.

Keep a short adopted boundary principle and real route in project instructions. Kernel supplies awareness, not project schemas or host precedence. Reuse [instruction adoption](../../senmu-build-project/references/project-instruction-authoring.md#adopting-a-buildos-update) for `adopted`, `no_change_needed` or `gap_open`; an update does not silently rewrite other projects. Repeated governance of unchanged facts is a semantic no-op.

Diagnose separately: missing method; old installed snapshot; project adoption gap; ineffective host loading/override; stale generation or missing check wiring; and correct structure with wrong business meaning. Several can coexist. Source review establishes only what the product defines. Fresh-session/subagent observations establish actual loading and behavior; comparative efficiency needs comparable runs. Use the existing [host evaluation](../../../tests/behavior/host-evaluation.md), not the authoring chat, to test those claims.
