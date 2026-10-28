# Architecture Constraints and Technical-Debt Governance

**Read by decision:** [Triggers](#3-triggers-and-levels) · [Current system](#4-current-system-technical-specification) · [Design changes](#5-architecture-change-contract) · [Operability](#52-operability-scenarios) · [Verification](#8-tests-as-architecture-protection) · [Debt review](#10-existing-system-engineering-and-debt-review).

Protect responsibilities, dependencies, ownership, unique implementation and version truth. Formatting/tests alone do not prove architecture health.

Use for initialization, architecture/debt review, cross-module work, refactoring, public contracts, repeated rework or gate calibration—not ordinary G1 copy/style or behavior-neutral fixes.

## 1. Govern Separate Objects

- **Code quality:** names, function responsibility, types, errors, tests, comments, local readability.
- **Architecture contract:** module responsibility, dependency direction, data ownership, public interfaces, invariants, side effects, runtime boundaries.
- **Technical debt:** a known temporarily accepted implementation/governance gap that raises future cost or risk.
- **Engineering governance:** alignment among authority root, release unit, version, changelog, tag, quality commands, CI, Work Log, and release evidence.

Assess each object with its own evidence and conclusion.

## 2. Architecture Principles

Inspect these boundaries:

| Principle | Required property | Review question |
| --- | --- | --- |
| High cohesion | Group rules, state, behavior around one capability/responsibility | Does one capability require unrelated modules? Does one module change for unrelated reasons? |
| Low coupling | Collaborate through minimum stable contracts; avoid shared internals/global mutable state | Do consumers know private fields, table layout, or initialization order? |
| One-way dependencies | Point toward stable policy/core; infrastructure does not control core rules | Can core logic be tested without UI/storage/vendor SDK? Any cycles? |
| Information hiding | Public APIs expose only consumer needs; internals vary independently | Does internal refactoring force many consumers to change? |
| Single ownership | One authority for data, state, effects, invariants | Do several entrypoints define one fact? |
| Separation of concerns | Separate business policy, orchestration, adapters, runtime | Are rules scattered across controllers, UI, SQL, scripts, deployment? |
| Replaceability/testability | Isolate valuable external boundaries; expose failure; verify contracts | Can key paths be unit/contract/integration tested? How much core changes on replacement? |
| Proportionate design | Abstract only for current quality attributes and known evolution | Does a layer solve real pressure or hypothetical future complexity? |

Use the [abstraction-value question](implementation-economy-and-overengineering.md#21-abstraction-value) when adding or removing a layer. Interface economy does not justify hiding side effects or weakening a real safety, compatibility or ownership boundary.

Record tradeoffs from project quality/risk when principles conflict. Performance tradeoffs cannot silently break ownership or allow uncontrolled layer crossing.

## 3. Triggers and Levels

Assess architecture when adding modules, services, shared packages, jobs, public interfaces, or dependencies; changing schemas, core state machines, permissions, billing, orders, file ownership, or cross-service flow; crossing modules/release units/frontend-backend; adding abstractions, frameworks, state containers, caches, queues, or persistence; creating a second implementation; seeing repeated patches or inconsistent agent structures; observing unusually large files/functions/dependencies/diffs; or when the owner asks whether complexity, debt, or version governance is degrading.

| Scenario | Default | Minimum action |
| --- | --- | --- |
| Read-only engineering health review | G2 | Read real code/governance, run read-only checks, report evidence; no business-code edits |
| Single-module architecture/ownership change | G2 | Update and verify affected contracts; contract-preserving local refactors may remain G1 |
| Cross-module/public API/database/release-unit change | G3 | Impact statement or ADR first; risk-path and affected architecture checks during development; declared full quality/CI at integration or release; independent recheck only when actual risk, separation of duties or explicit project policy requires it |
| Payments, authorization, production data, security, major migration | G4 | Phase-appropriate G3 checks plus early real risk-path evidence and recovery basis; independent review when required by risk/duties/policy; retrospective for incidents, material rework or explicit requests |

## 4. Current-System Technical Specification

Long-lived projects keep current technical facts in `engineering/SYSTEM_TECHNICAL_SPECIFICATION.md` or equivalent. Small projects may combine records. Keep only facts affecting understanding, change, verification or recovery:

1. System boundary and explicit exclusions.
2. Reuse the project's module navigation: capability, responsibility, real implementation, public interface, data owner, allowed/forbidden dependencies, release unit, contract and verification entrypoint. Missing implementation/checks are gaps, not invented paths or a second directory.
3. Allowed dependency direction among UI, application, domain, data access, external services.
4. Business invariants for money, permissions, state, ownership, idempotency, consistency.
5. Side-effect boundaries and failure propagation for database, network, files, messages, caches, third parties.
6. Compatibility responsibility for APIs, events, schemas, SDKs, shared types, storage formats.
7. Independent build/deploy/rollback/version boundaries.
8. Legacy entrypoints, implementation, compatibility, and retirement; what must not seed new code.
9. Required quality attributes only, each tied to business impact, scope, observable target, verification, owner, constraints/dependencies, accepted tradeoff. Mark unmeasurable claims as hypotheses/open; avoid false universal precision.
10. Evidence that cohesion, coupling, dependency direction, information hiding, and ownership appear in directories, interfaces, tests, or commands.

Remove empty headings; prefer concise tables or dependency rules and evidence-backed diagrams. Match actual paths, configuration and release units. Start from `assets/architecture-governance/SYSTEM_TECHNICAL_SPECIFICATION.template.md`. Each formal development version retains its Product Iteration technical design; unchanged structure may reference the current design and describe affected implementation/verification. ADRs depend on the decision, not the version.

## 5. Architecture Change Contract

Before coding, explain impact for module/service restructuring; dependency-direction or forbidden-crossing changes; public API/event/schema/shared package/cross-module state; table/destructive migration/data-owner changes; dependencies/infrastructure/frameworks/durable jobs; replacement while old entrypoints/data/consumers remain; or global state/cache/retry/async/compatibility added for a local problem. G3-G4 or critical modules also need an ADR/equivalent.

Minimum impact statement:

- Why can current capability not satisfy the need?
- Which equivalents were searched and why is this not a second capability?
- Which modules, contracts, data, deployments, and release units change?
- What is the new dependency direction and does it violate the contract?
- How will it be tested, migrated, observed, and rolled back?
- Is it permanent design or registered temporary debt?

### Design from the Caller to the Structure

Use this method when public interfaces, key state/data, module ownership or a genuinely uncertain architecture changes. Known patterns and local contract-preserving work do not require competing designs or an extra approval.

1. Reuse the affected-system model and effective design reasons. State the approved outcome, constraints and unmet need. Fill missing understanding before choosing; do not repeat completed investigation.
2. Show realistic caller usage: inputs, outputs, observable failure/cancellation and state transitions. Derive data, signatures, dependencies and ownership. Locate validation and external effects; identify complexity hidden inside the module.
3. When alternatives remain, compare structurally different viable shapes against the same goal, baseline, constraints and criteria: behavior, interface clarity, invariants, migration and maintenance cost. Sketch/prototype only to resolve uncertainty. Variations of one shape are not alternatives; settled designs need no competition.
4. Choose one coherent base; record fit, adapted ideas, rejected options and tradeoffs. Reconcile conflicting state models, not average them. Compare actual artifacts; model agreement is not proof. Record failed/missing candidates and unperformed independent review. Use Assurance's experiment contract for reproducible comparisons.
5. Keep usage, shape, reasons, preserved constraints and revisit conditions in the version design or existing owner. ADRs serve consequential durable decisions, not implementation details. Proceed within authority and preserve requested design checkpoints.
6. Implement and verify the unified result. Repeated similar deviations call for reassessment: missing requirement, wrong assumption or implementation overreach? Redesign the affected boundary rather than add unrelated patches; update the decision without rewriting historical reasons.

Small changes may need only a usage example and rationale; larger changes include affected modules and interfaces. Do not create placeholder bodies or files merely to prove design occurred.

A replacement closes old state, entrypoints, paths, data/consumers, tests and current docs in one Change Unit. Non-atomic public multi-consumer switches use `expand -> migrate -> contract`: add compatibility with owner/exit; migrate while observing old use, failures and rollback; remove only when no unhandled consumers, data or automation remain. Each phase is deployable, verifiable and recoverable. Atomic switches may combine phases, not omit impact, evidence or rollback.

### 5.1 Technical Consistency Self-Check

Self-check planning/implementation against REQ/acceptance, TD/ADR, task phase and real code: bidirectional requirement/design coverage, implementation/verification completeness, terminology/entities, executable dependency order and unplanned modules/interfaces/data/infrastructure.

Record at `TECHNICAL_REVIEW.md`, TD or the existing review owner, not a second plan. Implementer review remains self-review. Assurance owns explicit frozen-subject audits, cross-domain disputes or required independent verdicts; identify actual reviewers. Engineering revises.

### 5.2 Operability Scenarios

Operators are callers too. Assess sustained-service designs, deployment/recovery changes, relevant takeovers and recurring release friction—not covered routine work. Read actual environments, capacity, dependencies and operating/business constraints; ask only unresolved tradeoffs.

- Ordinary change: trace consumers and build inputs to safe update scope, coupling and reuse; directory diffs alone are insufficient.
- Interrupted change: reconcile real state, preserve completed effects and recover affected code, configuration, data and tasks through the actual entrypoint.
- Sustained operation: match peak/concurrent demand and resource/recovery references to capacity, retention and retirement.

Keep starting state, response, observable outcome, verification, tradeoff and revisit condition in the existing design/review. Do not invent targets or new infrastructure/registers/approvals. Small coupled releases remain valid. Remove redundant work and hand-synchronized facts before adding checks.

Engineering owns design fitness; Delivery verifies [release/recovery execution](../../senmu-build-delivery/references/deployment-testing-and-security.md#11-deployment-design-and-change-scope), using Workflow state semantics.

## 6. Change Budget and Task Splitting

Projects declare their own budget/escalation in `CODE_QUALITY.md`; BuildOS imposes no line count. Signals include modules/release units/public interfaces; new dependencies/migrations/config/services; changed files/behavior/rollback complexity; mixing behavior, formatting, moves, upgrades; and whether one reviewer/agent can fully understand and verify the diff.

When over budget, stop expanding despite runnable code and do one or more: submit TD/ADR first; split by independently verifiable/reversible behavior; separate mechanical from behavioral edits; add independent architecture review; or record owner-approved exception, risk, and closeout.

## 7. Architecture and Degradation Gates

Projects choose tools but declare which facts are machine-checked versus semantically reviewed. Prefer checks for forbidden/layer dependencies; cycles; duplicate code/capability and obsolete entrypoints; unused code/dependencies/orphan modules; public API/schema/migration/shared-type compatibility; complexity and large/high-fan hotspots as trends; and consistency among architecture docs, policy, directories, and dependencies.

- Enforce adopted dependency, cycle, release-unit and compatibility constraints under [gate policy](../../senmu-build-project/references/governance-levels-and-gates.md#2-gate-types). Revisions or equivalents require the owner’s authority and evidence for protected outcomes.
- G3-G4 additions of module/public interface/database/foundational dependency without impact, tests, and rollback basis cannot be complete.
- Complexity, duplication, and size are trends/hotspots, not universal numeric rejection.
- Baseline legacy projects; changed code must not worsen selected measures. Register debt instead of globally ignoring it.
- Automated success does not replace semantic review of responsibility, invariants, error meaning, and duplicate implementation.

Wire adopted dependency rules through the selected ecosystem tool into the quality command; verify allowed and forbidden fixtures. Review duplicate capabilities and change locality semantically. Without automation, retain a repeatable checklist and evidence.

## 8. Tests as Architecture Protection

Match evidence to change: domain tests for rules; contract tests for module APIs; migration/compatibility/rollback for schema/ownership; characterization/regression before splitting a complex legacy module; integration/real flow across services/release units; and replacement proof that the new entrypoint is working/unique, old paths unreachable, and state/data/consumers/events/filters closed. Any compatibility boundary needs owner, exit, and tests.

Do not lock refactoring with brittle private assertions or test only success while omitting authorization, partial failure, duplicate execution, and legacy-data compatibility.

## 9. Technical-Debt Register

Continuing G2-G4 cost/risk belongs in `engineering/TECH_DEBT.md`, issues or equivalent: ID/title/status, affected location/module/unit, cause/symptoms, speed/correctness/safety/data/release impact, acceptance rationale/rejected options, owner, repayment trigger/target and acceptance/removal method.

Real-debt patches, global suppressions, compatibility branches and TODOs link the debt ID or nearby closeout; not every TODO is debt. Recheck triggers when touching the module. Report added/repaid/accepted debt before release; zero debt is not required. Repayment closes code, tests, docs and old entrypoints. Template: `assets/architecture-governance/TECH_DEBT_REGISTER.template.md`.

## 10. Existing-System Engineering and Debt Review

Honor the requested scope: named module and necessary callers, or explicit repository-wide review. Otherwise select real hotspots/recurring friction; missing history is a gap. Safety/correctness outrank frequency. Local findings do not prove global health.

Review read-only; findings do not authorize refactoring:

1. Confirm authority/Git roots, branch/commit, worktree and runtime/release scope; reuse valid evidence.
2. Cross-check requirements, decisions, code and checks; inventory stacks, stores, jobs, services, deployments and versions only within the question or declared wider review.
3. Inspect responsibilities, dependencies, ownership, duplication, cycles, errors, dead/legacy paths and test gaps. Justify expansion by evidence, retaining connected money/data/authorization risks. Report inaccessible evidence; do not exceed authority.
4. Run sufficient authorized read-only checks. Preserve failures without baseline repair; require neither unrelated builds nor unauthorized production/paid probes.
5. Use `risk_based` sampling for declared invariants and failure paths. Explicit per-file/function/comment requests retain Assurance `exhaustive_source` and durable coverage; sampling is not exhaustive.
6. Report under section 11 at agreed coverage: limits, before/after responsibilities, benefit, cost and verification. Separate supported changes from unproven candidates. A sentence may replace a diagram; never invent savings.

Use the existing report owner and `assets/architecture-governance/ENGINEERING_AUDIT_TASK.template.md`; exhaustive reviews use `EXHAUSTIVE_SOURCE_REVIEW_TASK.template.md` under Assurance.

- **P0:** production, data/money/authorization, release, or rollback danger; block affected release.
- **P1:** uncontrolled core architecture or conflicting version truth; prioritize governance.
- **P2:** continuing quality/debt cost; schedule soon.
- **P3:** optional style/low-risk improvement; not a blocker.

## 11. Review and Remediation Closure

Report the requested conclusion, scoped identity/coverage, evidence, ranked findings and material owner decisions. Include baselines, diagrams or action plans only when needed to assess the result; preserve unknowns at the existing report owner.

Audit-only stays read-only; authorized audit-and-repair continues within scope without repeated approval. Preserve requested checkpoints and resolve uncovered authority or material choices. Verify critical behavior, repair confirmed causes/high-risk boundaries, then simplify authorized low-risk structure. Update affected debt/work records at meaningful transitions, not rewrite for visual cleanliness.

## 12. Noise Reduction and Exceptions

- Small prototypes may combine current technical specification into a short note and debt into issues; no committee or document sprawl.
- Do not substitute universal size, complexity, or coverage thresholds for project baselines, trends, and critical paths.
- Do not add all historical debt to an unrelated feature branch.
- Do not combine security, business-correctness, and engineering-governance audits into an unowned report. Cross-reference risks with clear next owners.
