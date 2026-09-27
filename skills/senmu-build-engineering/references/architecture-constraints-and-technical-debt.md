# Architecture Constraints and Technical-Debt Governance

**Read by decision:** [Triggers](#3-triggers-and-levels) · [Current system](#4-current-system-technical-specification) · [Design changes](#5-architecture-change-contract) · [Verification](#8-tests-as-architecture-protection) · [Debt review](#10-existing-system-engineering-and-debt-review).

Protect responsibilities, dependencies, ownership, unique implementation and version truth. Formatting/tests alone do not prove architecture health.

Use for initialization, architecture/debt review, cross-module work, refactoring, public contracts, repeated rework or gate calibration; skip ordinary G1 copy/style and behavior-neutral fixes.

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
| Single-module calibration/local refactor | G2 | Update architecture contract, matching tests, dependency and full-diff verification |
| Cross-module/public API/database/release-unit change | G3 | Impact statement or ADR first; risk-path and affected architecture checks during development; declared full quality/CI at integration or release; independent recheck only when actual risk, separation of duties or explicit project policy requires it |
| Payments, authorization, production data, security, major migration | G4 | Phase-appropriate G3 checks plus early real risk-path evidence and recovery basis; independent review when required by risk/duties/policy; retrospective for incidents, material rework or explicit requests |

## 4. Current-System Technical Specification

Long-lived code projects keep current technical facts in `engineering/SYSTEM_TECHNICAL_SPECIFICATION.md` or equivalent. Retain only facts affecting understanding, change, verification, or recovery; small projects may use a short combined document:

1. System boundary and explicit exclusions.
2. Module register: capability, responsibility, actual implementation entrypoint, public interface, data owner, allowed/forbidden dependencies, release unit, and the applicable contract and verification entrypoint. Reuse the project's navigation entry rather than maintaining a second module directory. A missing implementation or check is an explicit gap, not an invented path.
3. Allowed dependency direction among UI, application, domain, data access, external services.
4. Business invariants for money, permissions, state, ownership, idempotency, consistency.
5. Side-effect boundaries and failure propagation for database, network, files, messages, caches, third parties.
6. Compatibility responsibility for APIs, events, schemas, SDKs, shared types, storage formats.
7. Independent build/deploy/rollback/version boundaries.
8. Legacy entrypoints, implementation, compatibility, and retirement; what must not seed new code.
9. Required quality attributes only, each tied to business impact, scope, observable target, verification, owner, constraints/dependencies, accepted tradeoff. Mark unmeasurable claims as hypotheses/open; avoid false universal precision.
10. Evidence that cohesion, coupling, dependency direction, information hiding, and ownership appear in directories, interfaces, tests, or commands.

Remove empty headings. Prefer concise tables or dependency rules; diagrams need evidence. Match real paths, configuration and release units. Use `assets/architecture-governance/SYSTEM_TECHNICAL_SPECIFICATION.template.md` when creating the document. Keep a technical design for each formal development version under Product Iteration. When the structure is unchanged, reference the current design and briefly state the affected implementation and verification. ADRs remain conditional on the decision, not required per version.

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

1. Start from the affected-system model and effective design reasons already established for this task. State the approved outcome, constraints and what current capability cannot satisfy. If that understanding is missing, establish it before choosing a design; do not restart a completed investigation.
2. Show how the user or calling module will use the change. Name realistic inputs, outputs, observable failure and cancellation behavior, and relevant state transitions. Derive data structures, signatures, dependencies and ownership from that usage. Name where external effects and validation occur and which complexity stays inside the module.
3. When multiple viable shapes remain, compare structurally different candidates against the same goal, baseline, constraints and decision criteria. Use sketches or isolated prototypes only as needed to settle uncertainty. Evaluate behavior, interface clarity, invariants, migration and maintenance cost. A second variation of the same shape is not meaningful exploration; a settled design does not require a competition.
4. Choose one coherent base. Record why it fits, what compatible ideas were adapted, what was rejected and the tradeoffs accepted. Reconcile incompatible state models instead of averaging them. Compare actual artifacts; agreement among models is a clue, not proof. Record failed or missing candidates and do not claim unperformed independent review. Use Assurance's experiment contract when a comparison needs reproducible measurements.
5. Record the chosen usage, shape, reasons, preserved constraints and revisit conditions in the version technical design or existing decision owner. Use an ADR for a durable consequential decision, not every implementation detail. Proceed within existing authority; preserve an explicitly requested design checkpoint.
6. Implement against the chosen design and verify the unified result. Repeated deviations of the same kind are evidence to reconsider the design. Explain whether the cause is a missing requirement, a wrong assumption or implementation overreach; redesign the affected boundary rather than adding unrelated patches. Update the decision record without rewriting historical reasons.

For a small change, a short usage example and explanation can suffice. For a larger change, include the affected module map and interfaces. Do not generate placeholder bodies or extra files solely to prove that design happened.

A capability replacement closes old state, entrypoints, paths, data/consumers, tests, and current docs in one Change Unit. When a multi-consumer public contract cannot switch atomically, use `expand -> migrate -> contract`: add compatibility; migrate consumers while observing old use/failures/rollback; remove only after no unhandled consumers, data, or automation remains. Every phase is deployable, verifiable, recoverable; compatibility has owner/exit. Atomic switches may combine phases but retain impact, evidence, and rollback.

### 5.1 Technical Consistency Self-Check

Engineering self-checks ordinary planning/implementation against REQ/acceptance, TD/ADR, task phase, and real code boundaries: requirement-to-design coverage, design-to-requirement source, task implementation/verification completeness, terminology/entity consistency, executable dependency order, and unplanned modules/interfaces/data/infrastructure.

Record in `TECHNICAL_REVIEW.md`, TD, or current review owner—not a second technical plan. Implementer review is evidence-based self-review. Use Assurance for an explicit frozen-subject audit, cross-domain dispute or required independent verdict. State actual reviewer identity separately; Engineering performs revisions.

## 6. Change Budget and Task Splitting

Projects declare their own budget/escalation in `CODE_QUALITY.md`; BuildOS imposes no line count. Signals include modules/release units/public interfaces; new dependencies/migrations/config/services; changed files/behavior/rollback complexity; mixing behavior, formatting, moves, upgrades; and whether one reviewer/agent can fully understand and verify the diff.

When over budget, stop expanding despite runnable code and do one or more: submit TD/ADR first; split by independently verifiable/reversible behavior; separate mechanical from behavioral edits; add independent architecture review; or record owner-approved exception, risk, and closeout.

## 7. Architecture and Degradation Gates

Projects choose tools but declare which facts are machine-checked versus semantically reviewed. Prefer checks for forbidden/layer dependencies; cycles; duplicate code/capability and obsolete entrypoints; unused code/dependencies/orphan modules; public API/schema/migration/shared-type compatibility; complexity and large/high-fan hotspots as trends; and consistency among architecture docs, policy, directories, and dependencies.

- Declared forbidden dependencies, cycles, cross-release-unit internal references, and destructive contracts are Hard Gates.
- G3-G4 additions of module/public interface/database/foundational dependency without impact, tests, and rollback basis cannot be complete.
- Complexity, duplication, and size are trends/hotspots, not universal numeric rejection.
- Baseline legacy projects; changed code must not worsen selected measures. Register debt instead of globally ignoring it.
- Automated success does not replace semantic review of responsibility, invariants, error meaning, and duplicate implementation.

Wire adopted dependency rules through the selected ecosystem tool into the quality command; verify allowed and forbidden fixtures. Review duplicate capabilities and change locality semantically. Without automation, retain a repeatable checklist and evidence.

## 8. Tests as Architecture Protection

Match evidence to change: domain tests for rules; contract tests for module APIs; migration/compatibility/rollback for schema/ownership; characterization/regression before splitting a complex legacy module; integration/real flow across services/release units; and replacement proof that the new entrypoint is working/unique, old paths unreachable, and state/data/consumers/events/filters closed. Any compatibility boundary needs owner, exit, and tests.

Do not lock refactoring with brittle private assertions or test only success while omitting authorization, partial failure, duplicate execution, and legacy-data compatibility.

## 9. Technical-Debt Register

Known problems that continue to increase cost/risk in G2-G4 belong in `engineering/TECH_DEBT.md`, project issues, or equivalent, with ID/title/status; location and affected module/unit; cause and symptoms; speed/correctness/safety/data/release impact; reason for current acceptance and rejected options; owner and repayment trigger/target; and acceptance/removal method.

Real-debt patches, global suppressions, compatibility branches, and TODOs reference the debt ID or nearby closeout. Do not call every TODO debt. Check repayment triggers when touching its module. Before release, report added, repaid, and still accepted debt without requiring zero debt. Mark repaid only after code, tests, docs, and old entrypoints close. Template: `assets/architecture-governance/TECH_DEBT_REGISTER.template.md`.

## 10. Existing-System Engineering and Debt Review

Choose scope first. Inspect a named module and necessary callers, not unrelated systems. Otherwise use actual change hotspots or recurring friction; missing history is a gap. Safety and correctness outrank frequency. Honor repository-wide requests; local findings do not establish global health.

Review read-only; findings do not authorize refactoring:

1. Confirm authority and Git roots, branch/commit, worktree and affected runtime/release boundaries. Reuse valid evidence.
2. Cross-check relevant requirements, decisions, code and checks. Inventory stacks, stores, jobs, services, deployment and versions only as needed for the question or declared wider review.
3. Inspect responsibilities, dependencies, ownership, duplication, cycles, error handling, dead/legacy paths and test gaps. Expand on evidence and state why. Connected money, data and authorization risks remain in scope; report inaccessible evidence rather than exceed authority.
4. Run sufficient authorized read-only checks; preserve failures without baseline repair. Unrelated builds and unauthorized production or paid probes are not prerequisites.
5. Use `risk_based` sampling for declared invariants and failure paths. Explicit per-file/function/comment requests retain Assurance `exhaustive_source` and durable coverage; sampling is not exhaustive.
6. Report under section 11 and stop at agreed coverage with limits stated. Show before/after responsibilities, benefit, cost and verification. Separate supported changes from unproven candidates; a sentence may replace a diagram. Never invent savings.

Use the existing report owner and `assets/architecture-governance/ENGINEERING_AUDIT_TASK.template.md`; exhaustive reviews use `EXHAUSTIVE_SOURCE_REVIEW_TASK.template.md` under Assurance.

- **P0:** production, data/money/authorization, release, or rollback danger; block affected release.
- **P1:** uncontrolled core architecture or conflicting version truth; prioritize governance.
- **P2:** continuing quality/debt cost; schedule soon.
- **P3:** optional style/low-risk improvement; not a blocker.

## 11. Review and Remediation Closure

Report scope, authority root, branch, commit, release unit, gaps; exact commands/results/evidence; current architecture/version facts; severity-ranked findings; quality/debt baseline; immediate/near/long-term actions; proposed contracts/commands/tests/registers; blind spots and owner decisions.

Remediation requires authority for the affected scope, not renewed approval at each phase. An audit-only request remains read-only; an audit-and-repair request continues within its existing scope. Preserve explicit approval checkpoints and ask only for uncovered authority or an unresolved material choice. Protect critical behavior with matching checks, repair confirmed causes and high-risk boundaries, then simplify low-risk structure where authorized. Update affected debt and work records at meaningful transitions; do not rewrite the system for visual cleanliness.

## 12. Noise Reduction and Exceptions

- Small prototypes may combine current technical specification into a short note and debt into issues; no committee or document sprawl.
- Do not substitute universal size, complexity, or coverage thresholds for project baselines, trends, and critical paths.
- Do not add all historical debt to an unrelated feature branch.
- Do not combine security, business-correctness, and engineering-governance audits into an unowned report. Cross-reference risks with clear next owners.
- This standard owns general governance and adoption, not language, framework, or domain specialist rules.
