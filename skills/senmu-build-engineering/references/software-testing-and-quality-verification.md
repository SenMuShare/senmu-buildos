# Software Testing and Quality Verification

**Key sections (read as needed):** [Choosing checks](#0-minimum-sufficient-verification) · [Layers and Responsibilities](#2-layers-and-responsibilities) · [Non-Functional Verification](#6-non-functional-verification) · [Impact and Regression Selection](#7-impact-and-regression-selection) · [Flaky, Skipped, and Failed Tests](#8-flaky-skipped-and-failed-tests)

Select sufficient testing evidence from behavior, risk, boundaries and failure cost, not a universal pyramid or coverage target. Product owns acceptance; Delivery owns release. Tests support but replace neither decision.

## 0. Minimum Sufficient Verification

Distinguish authoring, execution and reruns. Optimize total task cost at unchanged acceptance, not test counts or zero checking. These decisions need no per-test form or approval ritual.

- **Author:** reuse existing coverage; add or extend tests for a real behavior/risk gap, not merely a changed file. Avoid implementation-mirroring assertions; exact output, schema and security checks remain valid contracts.
- **Execute:** use the least costly sufficient check at the boundary that observes the result. Code-hosted prompts and executable examples are not harmless prose. Refactors reuse behavior tests; visual changes need rendered evidence. High-risk boundaries are checked early. A fast suite may cost less than elaborate filtering.
- **Expand or stop:** broaden for affected behavior, unresolved risk, failure or required gates. Reuse evidence under section 7. Stop when the agreed outcome and required evidence are supported and blockers resolved; disclose gaps, do not add speculative cases or rerun to obtain green.

A message, commit, formatting pass, handoff or new stage alone does not justify a full cycle. Follow actual effects, not line counts or suffixes.

## 1. Strategy Inputs

Use approved acceptance/invariants, affected docs, modules/interfaces/data owners, dependencies and effects. Consider runtime compatibility, release/recovery, failure impact/likelihood/detectability, existing tests/CI/environments and defects; include money, authorization, storage, network and messaging risks.

For low-impact changes, avoid implementation-mirroring or instruction-wording tests. Expand required checks only for changed inputs, failure or unresolved risk. Instruction audits also use Project's routing check; shorter text or valid links do not prove model performance.

Choose layers by risk. Unit/property tests may suffice for pure functions; transactions and authorization need evidence at trust/persistence boundaries. Atomicity, forward migration and release rollback are distinct. A migration verifies transformation, order, constraints, rerun safety and final state, not an automatic rollback drill. Follow the approved recovery strategy. Probe concrete unresolved invariants or defects, not every possible write point.

Version `TEST_CASES.md` derives directly from that PRD's pages/features/capabilities, product behavior, interaction, errors, boundaries, and acceptance and mirrors its content structure. Shared version/sections provide linkage; do not create a traceability matrix. Retain an existing test-management owner. Templates are adaptable outlines: a low-risk change keeps only matching cases.

For installation, configuration, operation, API/CLI/SDK or recovery changes, use affected current user docs as black-box acceptance. Execute real commands/examples from representative PRD starting states to observable outcomes. Automate relevant code blocks in the existing quality entrypoint or record environment, steps, results and gaps. Links, doc builds and highlighting prove surface only. Unchanged-use refactors and one-off exploration without durable entrypoints need no documentation tests.

## 2. Layers and Responsibilities

| Layer | Proves | Must not own |
| --- | --- | --- |
| Unit | Local rules, boundaries, deterministic computation | Real database/network/deployment availability |
| Module/component | A module fulfills responsibility through its public entrypoint | Brittle assertions through internals |
| Contract/API | Request, response, event, schema, error, compatibility | Consumer end-to-end reality |
| Integration | Database, queue, file, adapter, transaction collaboration | Mocks presented as real dependencies |
| End-to-end/real flow | Main user/system path completes near reality | Every detail or precise root-cause isolation |
| Product acceptance | Requirement/acceptance is met | Production deployment |
| Release verification | Artifact, deployment, version, traffic, rollback facts | Repeating all development tests |

Layers may combine, responsibilities may not disappear. Verify a business invariant at the nearest boundary where untrusted input becomes trusted state; downstream layers reuse that result and test only added risk, not duplicate probes, error-code tables, or human reconciliation states. Retain defense across trust domains, independent consumer contracts, or safety boundaries and state what each layer proves. Small scripts may combine module/E2E with examples; large services must not put all confidence in slow brittle E2E.

For a multi-step user capability, derive the starting state and observable final result from approved acceptance. Check the transitions connecting implemented modules, not just their isolated success: payment or preparation passing does not close a journey with no usable next action. Follow the same operation to the required result and verify applicable interruption recovery. A direction to run each real main flow once prevents duplicate expensive executions; it does not remove completion criteria, safety checks or impact-based regression after a fix.

## 3. Test Design

Cover only relevant dimensions: normal/core outcomes; null/min/max/format/locale/time; invalid state, duplicate, reorder, timeout, cancellation, partial success; permissions, tenancy, ownership, sensitive data; commit/rollback, idempotency, race, retry effects; dependency failure, degradation, recovery, compensation, cleanup; schema/API/config/file/version compatibility; and legacy, migration equivalence, rollback.

A defect needs a failing-before/passing-after regression or explained repeatable alternative. Avoid equivalent cases for count. Evaluate contract observability and defect sensitivity, not assertion names. Definedness, emptiness, absence and negative checks can be valid; do not delete them mechanically or claim results without inspecting semantics.

Prefer test-first when behavior is clear, feedback is fast and checks need no private internals: show failure, implement, then refactor. For exploratory algorithms, one-off POCs, visual choices or costly unstable environments, stabilize the problem or prototype first. Writing order is not a gate; the final check must observe real behavior and detect regression.

A complete replacement proves the new entrypoint works and is unique and the old one is unreachable. Approved compatibility proves bounded, non-default behavior and exit conditions. Historical tests asserting an old control/entrypoint exists are not requirement authority; delete or rewrite against the current contract.

Permanent retirement tests prove not only UI removal but that direct APIs/routes, jobs/events, flags/configuration, permissions, and restart defaults cannot revive the capability, while remaining/replacement behavior survives. Test approved historical-data read, migration, compatibility, or rollback separately with scope and exit. Deleting tests or making requests always fail does not prove executable legacy was removed.

## 4. Doubles and Real Dependencies

- Use fakes, stubs, and mocks at boundaries you own; do not simulate until behavior no longer resembles the third-party/framework contract.
- A mock proves caller behavior, not compatibility. Critical integration needs contract tests, sandbox, or controlled real-service evidence.
- For identity, payment, storage, queues, protocols, or SDK defects, preserve a minimum production-shaped fixture including behavior-changing fields, secret type, order, state, and error. Simplification must not remove the risky difference.
- Inject/fix time, randomness, network, filesystem, and environment through explicit boundaries rather than machine accident.
- Do not copy production algorithms into expected results. Use business rules, fixed examples, independent oracles, or properties.
- Repair the contract owner when doubles drift from schemas/interfaces; do not add mocks to conceal it.
- Names and failures should identify the production behavior at risk. Assert public result, state, persistence, or side effect. Mock calls, private order, or internal field existence alone do not prove business outcome. Adapter tests may assert call contracts, but an upper layer still proves the correct result.

State each real-service receipt's scope and achieved stage: provider/model/route, relevant environment and observation time, request accepted, terminal success, or result retrieved and checked. Acceptance of an asynchronous request does not prove completion or application integration. A sample for one model/language cannot attest another model or every supported language. Reuse valid contract and entitlement evidence without demanding exhaustive paid probes; disclose the remaining gaps. Use existing operation/receipt owners rather than a parallel evidence framework, and reconcile uncertain external outcomes before another write.

## 5. Data and Environment

- State test-data provenance, construction, privacy boundary, isolation, and cleanup.
- Do not copy personal data, secrets, production databases, or restricted assets by default.
- Tests are independent, repeatable, and parallelizable. If order is essential, model it as one scenario rather than relying on case order.
- Database tests define transactions, migrations, time zones, encodings, constraints, and cleanup.
- Tests requiring real credentials, paid calls, or external writes are opt-in and obey authority/stop conditions.

## 6. Non-Functional Verification

Load only for actual requirements/risks:

- Performance: representative data, baseline, metric, environment, repetitions, threshold.
- Reliability: timeout, retry, recovery, degradation, capacity, exhaustion.
- Security: authentication, authorization, input, sensitive data, dependencies, supply chain; specialist security audit remains separate.
- Accessibility: keyboard, semantics, focus, labels, contrast, assistive technology.
- Observability: critical success/failure signals, structured logs, metrics, traces, alerts.

A local quick run cannot become a production-capacity conclusion. Record environment/limits and distinguish measurement from inference.

## 7. Impact and Regression Selection

Derive impact from diff, call chains, public contracts, data and configuration. Check behavior, consumers, shared state/effects, compatibility/migration/rollback and analogous history. For each key safety fact, trace failure and use the nearest affordable real-code/artifact check. Label source support, experimental proof or uncertainty; search and plausibility do not prove no impact. Report confirmed, cleared and unknown risks without invented probabilities.

For small changes, run targeted tests/checks. Cross-module, public interface, schema, dependency, or release-unit changes require impact-based checks and relevant real paths, plus any full gate required by the project. Once matching and required checks pass, expand or repeat only for new changes, failures, or unresolved concerns. One new test does not prove old behavior unaffected.

First answer whether the original issue is fixed: close root cause with an original-path or production-shaped test that fails before and passes after. Then run impacted regressions, and run complete project gates only on a frozen candidate. Many generic regressions cannot replace the key dependency shape/current main path; a passing key path cannot replace its impacted regressions.

During implementation check original failures/affected behavior; at review/closeout cover scope and consumers; on the frozen integrated candidate run required full gates and unmet acceptance. Branch passes are not integration. Reuse valid evidence, not stale approval; stages, sessions or commits alone do not justify reruns. Repair redundant project commands within authority, never bypass them.

Safety, data, authorization, billing, production, and irreversible boundaries receive checks with the first affected slice, not first at batch end. Presentation-equivalent edits may form one interaction batch; once semantics, hierarchy, operation, state, accessibility, or acceptance changes, reassess impact and batch.

### Evidence Reuse and Handoff

Engineering owns evidence scope and expiry. Reuse passing results only with equivalent behavior and inputs: source/tests, resolved dependencies/toolchain, configuration, commands/options, fixtures/data and environment. Results must remain available, without unresolved failure or external-state drift. A matching commit alone does not prove equivalence; a different one does not invalidate unrelated evidence.

Rerun changed inputs/dependent behavior and retain unaffected results. Resolve unknown impact without automatic whole-suite repetition. Refresh time-sensitive evidence such as service health. Reuse builds only with matching relevant inputs and retained output integrity; identical commands do not equate local/container builds. Rebuild affected artifacts when outputs are missing, altered or untraceable.

Existing task/CI receipts retain scope, input identity, environment, result, gaps and reuse rationale; no new ledger, universal fingerprints or cache. Delivery maps valid evidence to the candidate and checks unmet release obligations. Renew changed-candidate conclusions without relabelling old runs. Separate reused/new checks; totals prove neither requirements nor visual acceptance.

### Efficient Execution and Waiting

Keep one check instance. Use supported completion notifications or suitable waits; poll at intervals suited to duration, not repeated model turns with no new output. Read exit status, discovery/skips and failures first; retain full logs without repeatedly loading them. Empty discovery or a running process is not a pass. Test time and model-token cost differ.

Use existing job dependencies or trusted candidate-bound receipts for pipeline reuse, never an arbitrary latest green run. Keep independent artifact/environment checks and repair redundant commands at their authorized owner; no new universal cache is required.

## 8. Flaky, Skipped, and Failed Tests

- A flaky test is a quality defect; do not rerun indefinitely for green.
- One later pass does not erase an unexplained earlier failure for the same candidate. Overall status remains unstable until root cause is fixed or the test is quarantined with owner, risk, and exit condition.
- Quarantine/skip records owner, reason, risk, trigger, and restoration deadline.
- Green CI with key tests skipped, undiscovered, or disconnected from real dependencies must report actual coverage, not “full pass.”
- Preserve first-failure output and distinguish product, test, and environment defects when repairing infrastructure.
- Do not weaken assertions, delete tests, or downgrade failures to warnings merely to pass unless the contract truly changed and authority is synchronized.

## 9. Quality Entrypoints and Evidence

Local `engineering/TESTING_STRATEGY.md` records test layers/directories, risk mapping, data/double boundaries, unified commands, CI jobs, real flows, skips, and release blockers.

Unified commands should share configuration:

- Fast: affected formatting, lint, types, targeted tests.
- Full quality: all lint, types, unit/integration tests, build.
- Architecture/contract: dependencies, API/schema, migration compatibility.
- Real flow: main path, authorization, data, recovery in a controlled environment.
- User docs: executable affected commands/examples and walkthrough from representative start to core result.

### Make the Real Verification Path Usable

Without a usable real check, add the smallest recipe to the existing testing owner/commands/map, not a parallel catalog. Specify setup, readiness/version/auth, real actions, results/effects, evidence and cleanup, with cost, credentials, isolation and mutation boundaries.

Exercise a new/repaired recipe on one affected path before calling it verified. Observe results and retain evidence after cleanup; stop only its own processes/scratch state. Missing access leaves a draft. One path proves neither all features nor all environments.

Maintain affected recipes as behavior changes. Distinguish document drift, harness defects and product regressions; never rewrite expected behavior to conceal a regression. Diagnostic injection and external effects still need authority.

Report commands, results, failures/skips, environment and remaining risk. Tool success is not acceptance, deployment or release.

### Diagnose the Verification Method

Repeated preparation failures or green tests with an unusable capability require method review, not more cases by default. Inspect native runner/framework APIs, actual schema, fixtures and observation boundary; exercise one representative setup-to-result path before expanding. Informative long checks are not inherently waste.

Prefer supported tools to custom parsers/comparators. A justified helper must distinguish equivalent inputs from meaningful differences; normalization must not erase names, values, order or state. Green counts cannot rescue an unsound oracle. External fakes may be valid, but tests must not replace missing application dispatch, persistence or recovery by manually advancing internal steps.

Expose setup/collection/execution/result, discovered/executed/skipped scope and failure location through existing receipts; classify product/test/environment/unknown from evidence. Rerun affected work before closeout gates. Choose safe resume or disposable-fixture reconstruction from actual state; reconcile uncertain effects first. Bind evidence to its claim, not every unchanged file after each edit.

## 10. Incremental Adoption in Legacy Projects

1. Baseline current behavior and high-risk invariants.
2. Add matching verification for new/changed code; do not expand untested areas.
3. Add regressions by defect frequency, change frequency, and failure impact.
4. Consolidate duplicate entrypoints, excessive mocks, and long-lived skips.
5. Put strategy, commands, and real capabilities in project authority—not CI or chat alone.


A later scheduled regression supplements focused checks; work awaiting required evidence remains unverified, and release obligations still apply.
