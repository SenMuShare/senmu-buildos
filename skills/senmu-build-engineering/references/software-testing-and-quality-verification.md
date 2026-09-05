# Software Testing and Quality Verification

This standard defines cross-language testing and quality verification. It prescribes neither one test pyramid nor universal coverage. Select the minimum sufficient evidence from behavior, risk, boundaries, and failure cost. Product owns acceptance; Delivery owns real release. Test evidence supports but cannot replace either decision.

## 1. Strategy Inputs

Before creating/changing strategy, establish requirements, invariants, and observable acceptance; affected current user docs/examples and Product-declared documentation acceptance paths; modules, public interfaces, data ownership, dependencies; database/file/network/message/payment/authorization/external effects; runtime, supported versions, compatibility, release/rollback; failure impact, probability, detectability, and recovery cost; and existing tests, CI, real environments, and defect history.

For reversible, low-impact changes, do not add tests that merely mirror implementation or assert instruction wording. Run required checks once; broaden or repeat only for new changes, failures, or unresolved risk. Instruction audits additionally use the Project routing behavior check; shorter text and passing link checks do not prove model performance.

Choose layers by risk. A pure function may need only unit/property tests; a cross-service transaction, authorization boundary, or data migration needs contract, integration, rollback, and real-path evidence.

Version `TEST_CASES.md` derives directly from that PRD's pages/features/capabilities, product behavior, interaction, errors, boundaries, and acceptance and mirrors its content structure. Shared version/sections provide linkage; do not create a traceability matrix. Retain an existing test-management owner. Templates are adaptable outlines: a low-risk change keeps only matching cases.

When installation, configuration, user operation, public API, CLI, SDK, or recovery changes, treat affected current Get Started/tutorial/manual/reference paths as black-box acceptance input. From representative PRD starting points, execute real commands/examples and verify observable results/final state. Automate documentation code blocks in the unified quality entrypoint when possible; otherwise record environment, steps, result, and blind spots. Link checks, documentation builds, and syntax highlighting prove only document surface, not product behavior. Internal refactors with unchanged use contracts and one-off exploration with no durable entrypoint add no documentation tests.

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

## 3. Test Design

Cover only relevant dimensions: normal/core outcomes; null/min/max/format/locale/time; invalid state, duplicate, reorder, timeout, cancellation, partial success; permissions, tenancy, ownership, sensitive data; commit/rollback, idempotency, race, retry effects; dependency failure, degradation, recovery, compensation, cleanup; schema/API/config/file/version compatibility; and legacy, migration equivalence, rollback.

A defect needs a regression that fails before and passes after, or an explanation of alternate repeatable evidence. Do not duplicate equivalent cases for count.

When behavior is expressible before implementation, feedback is fast, and tests need not penetrate internals, prefer one test that fails because the capability is absent, then implement minimally and refactor. Do not force test-first for exploratory algorithms, one-off POCs, visual direction, or expensive unstable environments; first stabilize the problem/contract/prototype, then add evidence nearest the risk. Test-first reduces misunderstanding, not an approval ritual. Final tests must observe real behavior and fail on regression regardless of writing order.

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

Derive impact from diff, call chain, public contracts, data, and configuration. Check direct behavior, callers/consumers, shared state/effects, compatibility/migration/rollback, and analogous implementations/history.

For small changes, run targeted tests/checks. Cross-module, public interface, schema, dependency, or release-unit changes require impact-based checks and relevant real paths, plus any full gate required by the project. Once matching and required checks pass, expand or repeat only for new changes, failures, or unresolved concerns. One new test does not prove old behavior unaffected.

First answer whether the original issue is fixed: close root cause with an original-path or production-shaped test that fails before and passes after. Then run impacted regressions, and run complete project gates only on a frozen candidate. Many generic regressions cannot replace the key dependency shape/current main path; a passing key path cannot replace its impacted regressions.

Test timing follows the development batch, not user-message boundaries. During an open batch, after each item run only low-cost checks needed for credibility and early direct-regression detection—not full gates. When the owner confirms test/closeout or scope freezes, run matching builds, impacted regressions, and declared full gates once over the complete change. Reuse evidence at release while the candidate is unchanged. After code/config/schema/behavior changes, rerun affected checks and any full gate required by project entrypoints.

Safety, data, authorization, billing, production, and irreversible boundaries receive checks with the first affected slice, not first at batch end. Presentation-equivalent edits may form one interaction batch; once semantics, hierarchy, operation, state, accessibility, or acceptance changes, reassess impact and batch.

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

The final report records exact commands, results, failures/skips, environment, gaps, and residual risk. Tool success is not acceptance, deployment, or release.

## 10. Incremental Adoption in Legacy Projects

1. Baseline current behavior and high-risk invariants.
2. Add matching verification for new/changed code; do not expand untested areas.
3. Add regressions by defect frequency, change frequency, and failure impact.
4. Consolidate duplicate entrypoints, excessive mocks, and long-lived skips.
5. Put strategy, commands, and real capabilities in project authority—not CI or chat alone.
