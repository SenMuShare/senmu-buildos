# Implementation Economy and Overengineering Governance

Use this standard to reduce unnecessary code, abstractions, dependencies, files, and maintenance while preserving requirement meaning, quality attributes, and risk gates. It applies to features, fixes, refactors, design review, and read-only engineering review. Minimum line count is not a substitute for correctness or quality.

## 1. Decision Order

Understand the real requirement, call path, data, and failure semantics, then find the smallest correct solution in this order:

1. Determine whether current behavior already satisfies the requirement or the request is an unapproved hypothesis. Do not build unneeded capability.
2. Reuse or repair an existing owner, public entrypoint, or safely extensible implementation; do not create a parallel capability.
3. Evaluate whether the language standard library, platform primitive, or installed dependency fully satisfies semantics, compatibility, and quality attributes.
4. Evaluate mature maintained open source, framework, component, or service when its total cost is below custom implementation.
5. Otherwise build a bounded, verifiable custom implementation with minimum maintenance surface.

Semantic fit and risk gates precede cost at every level. Existing availability alone does not qualify a candidate.

## 2. Smallest Correct Implementation

- Optimize for the smallest correct change satisfying approved requirements and quality attributes—not fewest lines, tests, or files.
- Prefer deleting obsolete branches, merging duplicate owners, shortening call chains, and extending current responsibilities. Before deletion, close behavior, consumers, data, and compatibility boundaries.
- Fix the source that manufactures a bug and inspect equivalent call paths; do not wrap symptoms in another patch or copy a “new version.”
- Quality words such as perfect, long-term, general, or must not affect anything constrain results but do not expand scope. Without an approved roadmap, real consumer/second use case, proven bottleneck, or explicit replacement/isolation/reuse/test pressure, do not add a platform, abstraction, plugin/rule system, general DSL, configuration surface, compatibility mode, placeholder module, or unplanned feature. Judge one-implementation interfaces, one-product factories, forwarding wrappers, and dynamic frameworks for static configuration by the same evidence.
- If the user says a proposal is excessive or too heavy, stop expanding and return to the minimum approved result. Remove unauthorized parts while retaining protections required for security, privacy, permissions, payments, data, law, irreversible actions, release integrity, and approved compatibility; do not defend the abandoned design.
- Preserve necessary calibration, fault tolerance, and observability for unavoidable variation in inputs, devices, networks, or hardware; do not hard-code an accidental sample in the name of simplicity.

## 3. Value-First Staging

- Before each action, decide whether it changes deliverable value, proves correctness, or only maintains hashes, receipts, dashboards, or progress records. Perform the first two as needed. Pure bookkeeping must not block the main path, negate confirmed results, or force rework unless it is itself a product feature, regulatory audit, security/authorization record, external-side-effect reconciliation, or release fact.
- Define the phase's minimum value slice before implementation: authoritative input through the real core path to observable result, matching verification, and deliverable output. Scaffolding, abstractions, generic platforms, or check systems alone are not a value slice.
- Leave every phase runnable, verifiable, handoff-ready, and—with data, deployment, or external side effects—recoverable. Do not open many incomplete branches for a later long session to reconcile.
- Do not invoke governance to front-load validators, checklists, approvals, and reports. Repair the production path and make correctness the default, then retain minimum executable gates for material residual risk.
- When repeated reads, failures, or scope growth yield no new evidence, stop and redefine cause, smallest next step, and stop condition. Do not create runtime counters or fixed tool/token caps.
- Security, privacy, authorization, payments, production data, irreversible actions, and release integrity must ship with the first affected value slice, never as later decoration.
- Multi-stage tasks record phase completion, state, evidence, and recovery in the declared Durable Task State Owner. Task state supports delivery and does not duplicate specialist facts.

### 3.1 G1 Contract-Preserving Fast Path

A `contract-preserving local change` has known, locally reversible impact and preserves product meaning/acceptance, user actions/information hierarchy, interaction affordance/accessibility, state/data, authorization, interfaces, cross-step workflow, external side effects, and delivery/runtime boundaries. Classification depends on contracts, not file count, lines, or “looks like UI.”

A `presentation-equivalent change` is a subset: styling, wording, or local layout may change while all those contracts remain equivalent. A change to meaning, information priority, operation, responsive/accessibility outcome, or explicit acceptance exits this subset.

The fast path also requires one known owner/release unit and excludes security, privacy, authorization, payments/billing, production data, paid external effects, destructive operations, and formal release. Any exclusion exits the path.

- Engineering is the sole primary BuildOS Skill. User visibility, future commit intent, or steps in code do not automatically compose Product, Delivery, or Workflow.
- Read affected code, project-local rules, and nearest matching tests only. Do not load unrelated references, the full product system, or release standards merely to restate local contracts.
- Modify only implementation and the nearest valuable test. Do not create Task, TD, ADR, PRD, Changelog, or release records; G1 normally has no Work Log.

The software-testing standard owns batch and test timing; this standard creates no second closeout rule.

## 4. Semantic-Fit Gate

Before adopting an existing/standard/native capability, confirm:

- It covers the required contract, not a similarly named subset. A parser is not a validator, a formatter is not a sanitizer, and component defaults are not product acceptance.
- Errors, boundaries, internationalization, accessibility, compatibility, performance, and data semantics meet project needs.
- Integration does not bypass authorization, transaction, state, ownership, or release boundaries.
- The current version/runtime truly provides it. Read project dependencies and official current material at task time rather than freezing volatile APIs here.
- For a framework public extension point, test the real contract and failure path first. Bypassing public APIs, observing internal DOM, calling private interfaces, or duplicating framework state is allowed only as an evidenced minimum adapter with isolation, compatibility risk, and exit condition. Passing custom tests alone does not prove it is better than framework capability.

When a mature capability covers only part of the requirement, retain an explicit narrow adapter rather than distort the business contract for “zero custom code.”

## 5. Protections Simplicity Cannot Remove

Retain risk-proportional protection for security, privacy, authorization, payments, production data, irreversible operations, data integrity, transactions, idempotency, compatible migration, compensation, rollback, accessibility, law, explicit acceptance, public contracts, known critical boundaries, regression tests, runtime observation, and release gates.

Verification is minimum sufficient by risk. A low-risk obvious change may need one visible check; a high-risk cross-boundary change may need layered tests and a real flow. Do not universalize “one test.”

## 6. Intentional Simplification and Debt

When the team deliberately chooses a smaller implementation with a known limit, record in `engineering/TECH_DEBT.md`, the issue system, or equivalent:

- the simplification boundary and impact;
- observable upgrade/repayment triggers;
- owner and acceptance method;
- a stable debt ID referenced by TODOs or compatibility branches.

Do not create a Skill-private comment format or second debt ledger. Without a real limit and continuing maintenance cost, do not label ordinary design explanation as debt.

## 7. Implementation and Review Output

Daily implementation needs no long scorecard, but must explain what was reused, why no parallel capability was added, and which semantics/risks were verified. Read-only review may add an `implementation economy` lens:

- unused code, dependencies, files, and old entrypoints safe to delete;
- duplicate implementation replaceable by an existing owner, platform/standard capability, or installed dependency;
- abstraction, wrapper, configuration, or scaffolding without real change pressure;
- implementation/call chains reducible without changing contracts.

Label these complexity opportunities separately from correctness, security, and business risk. Estimate removable lines, files, or dependencies only from actual diffs, dependency graphs, or reviewable paths; never infer project savings from generic benchmarks. Passing complexity review does not mean the overall code review passes.
