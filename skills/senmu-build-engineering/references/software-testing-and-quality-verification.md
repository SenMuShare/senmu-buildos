# Software Testing and Quality Verification

**Read as needed:** [Checks](#0-minimum-sufficient-verification) · [Layers](#2-layers-and-responsibilities) · [UI evidence](#ui-evidence-and-runtime) · [Non-functional](#6-non-functional-verification) · [Impact](#7-impact-and-regression-selection) · [Failures](#8-flaky-skipped-and-failed-tests)

Choose evidence by behavior, risk, boundaries and failure cost, not a universal pyramid or coverage target. Tests support but do not replace Product's acceptance or Delivery's release decision.

## 0. Minimum Sufficient Verification

Separate authoring, execution and reruns. Minimize total cost without changing acceptance or adding per-test forms/approval rituals.

- **Author:** reuse coverage and fill behavior/risk gaps; a changed file alone needs no new test. Avoid implementation mirrors; exact output/schema/security contracts remain valid.
- **Execute:** use the least costly sufficient observable check. Code-hosted prompts and executable examples are not harmless prose. Reuse behavior tests for refactors; render visual changes; check high risk early. A fast suite may beat filtering.
- **Expand or stop:** broaden for affected behavior, unresolved risk, failure or required gates; reuse evidence under section 7. Stop when outcome/evidence are supported and blockers resolved. Disclose gaps; do not add speculative cases or rerun merely for green.

Messages, commits, formatting, handoffs and stages alone do not justify full cycles; effects do.

## 1. Strategy Inputs

Start with approved acceptance/invariants, affected docs/owners, dependencies/effects, runtime/recovery and existing tests/CI/environments/defects. Assess impact, likelihood and detectability, including money, authorization, storage, network and messaging.

Match evidence to its claim; derive expectations from requirements, independent oracles or justified properties. Conformance does not prove fitness for intended use; one check may support both. Return conflicts to Product. Verify promised dependency quality and usable downstream results; do not invent thresholds or change acceptance.

Low-impact work needs no instruction-wording tests. Instruction audits use Project's routing check; brevity/links do not prove model performance.

Unit/property tests may suffice for pure functions; transactions and authorization need trust/persistence-boundary evidence. Distinguish atomicity, forward migration and release rollback. Verify migration transformation, order, constraints, rerun safety and final state under approved recovery, without an automatic rollback drill. Probe unresolved invariants or defects, not every write point.

Keep version `TEST_CASES.md` aligned to PRD pages/features/capabilities, behavior, interaction, errors, boundaries and acceptance. Use shared version/sections, existing test management and adaptable minimal cases, without a new traceability matrix.

For installation, configuration, operation, API/CLI/SDK or recovery changes, exercise current user-doc commands/examples as black-box acceptance from representative PRD starts to observable outcomes. Use the existing quality entrypoint or record environment, steps, results and gaps. Links, doc builds and highlighting prove surface only. Unchanged-use refactors and one-off exploration without durable entrypoints need no documentation tests.

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

Combine layers without losing responsibilities. Check invariants where untrusted input becomes trusted state; downstream layers reuse results and test added risk, not duplicate probes, error-code tables or human reconciliation. Retain independent defenses at trust, consumer and safety boundaries. Scripts may combine module/E2E examples; large services need more than brittle E2E.

Follow multi-step capabilities from approved start through module transitions to the required observable outcome and applicable interruption recovery. Isolated module/payment/preparation success cannot close a journey without a usable next action. An instruction to run a main flow once avoids duplicate expense; completion, safety and impacted regression still apply.

### UI Evidence and Runtime

Apply to changed appearance, interaction or supported rendering environments, or requested visual/UX review. Use approved design revision and product acceptance. Select affected pages/states/viewports/themes from the change, shared dependencies and page map/examples. Local fixes may need only their target; shared token/component/shell changes need representative consumers and relevant exceptions. Expand for risk, not a whole-product matrix.

Distinguish claims, not mandatory suites; one check may support several:

- **Visual:** rendered design conformance: hierarchy, typography, spacing, alignment and shared-component consistency.
- **User journey:** navigation, feedback, errors and recovery carry the intended user to the required outcome; isolated screens/states cannot prove it.
- **Engineering:** state/data contracts, behavior, accessibility, integration and runtime constraints through existing suitable checks.

Requests or unresolved risk may warrant independent [Design visual review/task walkthrough](../../senmu-build-design/references/prototype-exploration-and-interface-review.md#visual-review-and-task-walkthrough). Discovery may infer a goal/path from safe entry, role and business context; acceptance needs the required goal. Return findings to their owner; do not silently change requirements.

Verify affected supported runtimes and disclose platform/state gaps. Browser/WebView evidence covers the web surface, not WinUI/native controls; a Linux pass does not prove Windows-specific behavior. Use the runtime that observes the changed behavior, without imposing native frameworks on web apps.

Screenshot comparison (e.g. Playwright) matches OS/browser versions, fonts, viewport/DPR, theme, fixtures and readiness. Control relevant time/randomness/animation; mask only irrelevant noise, never changed content/interaction. Review rendered before/after differences through existing project review/acceptance; human review applies only where policy requires it. Unreviewed replacements remain candidate baselines. Investigate unexplained differences before updates, never regenerate for green. Pixel thresholds do not prove usability or accepted design quality.

## 3. Test Design

Cover only relevant dimensions: normal/core outcomes; null/min/max/format/locale/time; invalid state, duplicate, reorder, timeout, cancellation, partial success; permissions, tenancy, ownership, sensitive data; commit/rollback, idempotency, race, retry effects; dependency failure, degradation, recovery, compensation, cleanup; schema/API/config/file/version compatibility; and legacy, migration equivalence, rollback.

Defects need failing-before/passing-after evidence or an explained repeatable alternative. Judge contract observability and defect sensitivity, not case counts or assertion names. Definedness, emptiness, absence and negative checks can be valid; inspect semantics before deleting them or claiming results.

Prefer test-first for clear behavior, fast feedback and checks without private internals: fail, implement, refactor. Exploration, one-off POCs, visual choices or costly unstable environments may stabilize the problem/prototype first. Writing order is not a gate; final checks must observe behavior and detect regression.

Replacement proves the new entrypoint works and is unique, and the old one unreachable. Approved compatibility proves bounded, non-default behavior and exit conditions. Historical tests retaining old controls/entrypoints are not requirement authority; delete or rewrite against the current contract.

Permanent retirement proves direct APIs/routes, jobs/events, flags/configuration, permissions and restart defaults cannot revive the capability, while remaining/replacement behavior survives. Test approved historical-data read, migration, compatibility or rollback separately with scope and exit. UI removal, deleted tests or always-failing requests do not prove executable legacy removed.

## 4. Doubles and Real Dependencies

- Use fakes, stubs and mocks at owned boundaries without losing the third-party/framework contract.
- A mock proves caller behavior, not compatibility. Critical integration needs contract tests, sandbox, or controlled real-service evidence.
- Identity, payment, storage, queue, protocol and SDK defects need production-shaped fixtures retaining behavior-changing fields, secret type, order, state and error. Simplification must preserve the risky difference.
- Inject/fix time, randomness, network, filesystem and environment explicitly, not by machine accident.
- Expectations use business rules, fixed examples, independent oracles or properties, not copied production algorithms.
- Repair schema/interface owners when doubles drift; do not conceal drift with more mocks.
- Name the production behavior at risk and assert public result, state, persistence or side effect. Mock calls, private order and internal fields alone do not prove business outcome. Adapter call-contract tests still need an upper layer to prove the result.

Real-service receipts state provider/model/route, environment/time and achieved stage: request accepted, terminal success, or result retrieved and checked. Async acceptance proves neither completion nor integration; one model/language sample cannot attest others. Reuse valid contract/entitlement evidence without exhaustive paid probes; disclose gaps. Use existing operation/receipt owners, and reconcile uncertain external outcomes before another write.

## 5. Data and Environment

- State test-data provenance, construction, privacy boundary, isolation, and cleanup.
- Do not copy personal data, secrets, production databases, or restricted assets by default.
- Keep tests independent/repeatable/parallelizable; essential order belongs in one scenario, not case order.
- Database tests define transactions, migrations, time zones, encodings, constraints, and cleanup.
- Tests requiring real credentials, paid calls, or external writes are opt-in and obey authority/stop conditions.

## 6. Non-Functional Verification

Load only for actual requirements/risks:

- Performance: representative data, baseline, metric, environment, repetitions, threshold.
- Reliability: timeout, retry, recovery, degradation, capacity, exhaustion.
- Security: authentication, authorization, input, sensitive data, dependencies, supply chain; specialist security audit remains separate.
- Accessibility: keyboard, semantics, focus, labels, contrast, assistive technology.
- Observability: critical success/failure signals, structured logs, metrics, traces, alerts.

A quick local run cannot prove production capacity. Record environment/limits; distinguish measurement from inference.

## 7. Impact and Regression Selection

Trace diff, call chains, contracts, data/configuration and analogous history to behavior, consumers, shared state/effects and compatibility/migration/rollback. Check key safety facts at the nearest affordable real-code/artifact boundary. Label source support, experimental proof or uncertainty; search/plausibility cannot prove no impact. Report confirmed, cleared and unknown risks without invented probabilities.

Small changes use targeted checks; cross-module/interface/schema/dependency/release-unit changes need affected real paths and project gates. First prove the original failure fixed on its original path or production-shaped fixture (section 3), then run impacted regressions. Generic green cannot replace the key dependency shape/current path, nor vice versa. One added test cannot attest old behavior.

During implementation check original failures/affected behavior; at review/closeout cover scope and consumers; run required full gates and unmet acceptance on the frozen integrated candidate. Branch passes are not integration. Reuse valid evidence, not stale approval; expand/rerun under section 0. Repair redundant project commands within authority, never bypass them.

Check safety, data, authorization, billing, production and irreversible boundaries with the first affected slice. Presentation-equivalent edits may share one interaction batch; changed semantics, hierarchy, operation, state, accessibility or acceptance require reassessing impact and batch.

### Evidence Reuse and Handoff

Engineering owns evidence scope/expiry. Reuse passing results with equivalent behavior and inputs: source/tests, resolved dependencies/toolchain, configuration, commands/options, fixtures/data and environment. Results remain available without unresolved failure or external-state drift. Same commit is insufficient; a different commit does not invalidate unrelated evidence.

Rerun changed inputs/dependent behavior, retain unaffected results and resolve unknown impact without default whole-suite repetition. Refresh time-sensitive evidence. Build reuse also needs output integrity; identical commands do not equate local/container builds. Rebuild affected missing, altered or untraceable artifacts.

Task/CI receipts retain scope, input identity, environment, result, gaps and reuse rationale; no new ledger, universal fingerprints or cache. Delivery maps evidence to the candidate and release gaps, renewing changed-candidate conclusions without relabelling old runs. Distinguish reused/new checks; totals prove neither requirements nor visual acceptance.

### Efficient Execution and Waiting

Keep one check instance; use completion notifications or suitable waits, not repeated empty turns. Read exit status, discovery/skips and failures first; retain logs without repeatedly loading them. Empty discovery or running processes are not passes. Test time and model-token cost differ.

Pipeline reuse uses job dependencies or trusted candidate-bound receipts, not latest green. Retain independent artifact/environment checks; repair redundant commands at their owner, without a universal cache.

## 8. Flaky, Skipped, and Failed Tests

- Flakiness is a defect, not a reason to rerun for green. A later pass cannot erase an unexplained failure on the same candidate; status stays unstable until root cause is fixed or valid quarantine applies.
- Quarantine/skip records owner, reason, risk, trigger, exit condition and restoration deadline.
- Report actual coverage when key tests are skipped, undiscovered or disconnected from real dependencies, even in green CI.
- Preserve first-failure output; distinguish product, test and environment defects when repairing infrastructure.
- Never weaken assertions, delete tests or downgrade failures merely for green; changed contracts require synchronized authority.

## 9. Quality Entrypoints and Evidence

Local `engineering/TESTING_STRATEGY.md` records layers/directories, risk mapping, data/doubles, commands/CI, real flows, skips and release blockers. Commands share configuration:

- Fast: affected formatting, lint, types, targeted tests.
- Full quality: all lint, types, unit/integration tests, build.
- Architecture/contract: dependencies, API/schema, migration compatibility.
- Real flow: main path, authorization, data, recovery in a controlled environment.
- User docs: executable affected commands/examples and walkthrough from representative start to core result.

### Make the Real Verification Path Usable

Use existing testing owners/commands/maps for the smallest usable recipe: setup, readiness/version/auth, actions/results/effects, evidence, cleanup and cost/credential/isolation/mutation limits. UI adds a reachable page/story/native entry, required state/runtime and relevant design basis/sample; no parallel catalog.

Exercise new/repaired recipes on one affected path before claiming verification; retain observed results after cleaning only owned processes/scratch. Missing access leaves a draft; one path cannot prove all features/environments.

Maintain recipes as behavior changes. Distinguish document drift, harness defects and product regressions; never rewrite expectations to conceal regression. Diagnostic injection and external effects still need authority.

At closeout, existing task/test reports expose the real entry, setup, results/failures/skips, environment, gaps and risk; reuse section 7 evidence. Design files/screenshots/build passes/URLs alone cannot prove reachable UI states or working journeys. Tool success is not acceptance, deployment or release.

### Diagnose the Verification Method

Repeated setup failures or green tests with unusable capabilities require method review, not default extra cases. Inspect native runner/framework APIs, schema, fixtures and observation boundary; exercise a representative setup-to-result path before expanding. Informative long checks are not inherently waste.

Prefer supported tools to custom parsers/comparators. Helpers must distinguish equivalent inputs from meaningful differences; normalization must preserve names, values, order and state. Green counts cannot rescue an unsound oracle. External fakes may be valid; manually advancing internal steps cannot replace missing application dispatch, persistence or recovery.

Existing receipts expose setup/collection/execution/result, discovered/executed/skipped scope and failure location; classify product/test/environment/unknown from evidence. Rerun affected work before closeout gates. Resume safely or reconstruct disposable fixtures from actual state, reconciling uncertain effects first. Bind evidence to its claim, not unchanged files after every edit.

## 10. Incremental Adoption in Legacy Projects

Baseline current behavior and high-risk invariants. Cover new/changed code; expand regressions by defect/change frequency and failure impact, not untouched areas by default. Consolidate duplicate entrypoints, excessive mocks and long-lived skips. Keep strategy, commands and real verification in project authority, not CI/chat alone.

Scheduled regressions supplement focused checks; required evidence pending remains unverified, and release obligations still apply.
