# Architecture Constraints and Technical-Debt Governance

Use this standard to prevent continuous local delivery from degrading responsibility, dependencies, ownership, implementation uniqueness, and version truth. It protects long-term modifiability; formatted, tested, runnable code is not automatically architecturally healthy.

Apply to initialization, engineering-health reviews, cross-module work, refactoring, public interfaces/data, repeated agent rework, debt governance, and architecture-gate calibration. Ordinary G1 copy/style or behavior-neutral fixes do not load it.

## 1. Govern Separate Objects

- **Code quality:** names, function responsibility, types, errors, tests, comments, local readability.
- **Architecture contract:** module responsibility, dependency direction, data ownership, public interfaces, invariants, side effects, runtime boundaries.
- **Technical debt:** a known temporarily accepted implementation/governance gap that raises future cost or risk.
- **Engineering governance:** alignment among authority root, release unit, version, changelog, tag, quality commands, CI, Work Log, and release evidence.

Passing code quality/tests does not prove architecture or version health. Review each object with separate evidence and conclusions.

## 2. Architecture Principles

Turn principles into inspectable boundaries:

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

Record tradeoffs from project quality/risk when principles conflict. Performance may reduce boundaries but must not silently break ownership or permit uncontrolled layer crossing.

## 3. Triggers and Levels

Assess architecture when adding modules, services, shared packages, jobs, public interfaces, or dependencies; changing schemas, core state machines, permissions, billing, orders, file ownership, or cross-service flow; crossing modules/release units/frontend-backend; adding abstractions, frameworks, state containers, caches, queues, or persistence; creating a second implementation; seeing repeated patches or inconsistent agent structures; observing unusually large files/functions/dependencies/diffs; or when the owner asks whether complexity, debt, or version governance is degrading.

| Scenario | Default | Minimum action |
| --- | --- | --- |
| Read-only engineering health review | G2 | Read real code/governance, run read-only checks, report evidence; no business-code edits |
| Single-module calibration/local refactor | G2 | Update architecture contract, matching tests, dependency and full-diff verification |
| Cross-module/public API/database/release-unit change | G3 | Impact statement or ADR first; full quality/architecture gates and independent recheck |
| Payments, authorization, production data, security, major migration | G4 | G3 plus real risk-path evidence, rollback basis, retrospective |

## 4. Current-System Technical Specification

Long-lived code projects keep current technical facts in `engineering/SYSTEM_TECHNICAL_SPECIFICATION.md` or equivalent. Retain only facts affecting understanding, change, verification, or recovery; small projects may use a short combined document:

1. System boundary and explicit exclusions.
2. Module register: name, responsibility, path, public interface, data owner, allowed/forbidden dependencies, release unit.
3. Allowed dependency direction among UI, application, domain, data access, external services.
4. Business invariants for money, permissions, state, ownership, idempotency, consistency.
5. Side-effect boundaries and failure propagation for database, network, files, messages, caches, third parties.
6. Compatibility responsibility for APIs, events, schemas, SDKs, shared types, storage formats.
7. Independent build/deploy/rollback/version boundaries.
8. Legacy entrypoints, implementation, compatibility, and retirement; what must not seed new code.
9. Required quality attributes only, each tied to business impact, scope, observable target, verification, owner, constraints/dependencies, accepted tradeoff. Mark unmeasurable claims as hypotheses/open; avoid false universal precision.
10. Evidence that cohesion, coupling, dependency direction, information hiding, and ownership appear in directories, interfaces, tests, or commands.

Delete empty headings rather than filling “N/A.” Prefer small text tables/direction rules to unverifiable diagrams. The specification must match real paths, configuration, and release units. A template is available at `assets/architecture-governance/SYSTEM_TECHNICAL_SPECIFICATION.template.md`. Create version technical design only when technology, module/interface/data/state, migration, or risk needs durable explanation.

## 5. Architecture Change Contract

Before coding, explain impact for module/service add/split/merge/move; dependency-direction or forbidden-crossing changes; public API/event/schema/shared package/cross-module state; table/destructive migration/data-owner changes; dependencies/infrastructure/frameworks/durable jobs; replacement while old entrypoints/data/consumers remain; or global state/cache/retry/async/compatibility added for a local problem. G3-G4 or critical modules also need an ADR/equivalent.

Minimum impact statement:

- Why can current capability not satisfy the need?
- Which equivalents were searched and why is this not a second capability?
- Which modules, contracts, data, deployments, and release units change?
- What is the new dependency direction and does it violate the contract?
- How will it be tested, migrated, observed, and rolled back?
- Is it permanent design or registered temporary debt?

ADRs record decision, context, alternatives, consequences, and replacement condition—not every implementation detail.

A capability replacement closes old state, entrypoints, paths, data/consumers, tests, and current docs in one Change Unit. When a multi-consumer public contract cannot switch atomically, use `expand -> migrate -> contract`: add compatibility; migrate consumers while observing old use/failures/rollback; remove only after no unhandled consumers, data, or automation remains. Every phase is deployable, verifiable, recoverable; compatibility has owner/exit. Atomic switches may combine phases but retain impact, evidence, and rollback.

### 5.1 Technical Consistency Self-Check

Engineering self-checks ordinary planning/implementation against REQ/acceptance, TD/ADR, task phase, and real code boundaries: requirement-to-design coverage, design-to-requirement source, task implementation/verification completeness, terminology/entity consistency, executable dependency order, and unplanned modules/interfaces/data/infrastructure.

Record in `TECHNICAL_REVIEW.md`, TD, or current review owner—not a second technical plan. Implementer review is evidence-based self-review. Use Assurance with a frozen object/evidence scope for requested independence, cross-domain dispute, or formal G3-G4 independent approval; Engineering performs revisions.

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

The unified quality command includes applicable architecture checks. If automation is impossible, retain a repeatable human checklist and evidence location.

## 8. Tests as Architecture Protection

Match evidence to change: domain tests for rules; contract tests for module APIs; migration/compatibility/rollback for schema/ownership; characterization/regression before splitting a complex legacy module; integration/real flow across services/release units; and replacement proof that the new entrypoint is working/unique, old paths unreachable, and state/data/consumers/events/filters closed. Any compatibility boundary needs owner, exit, and tests.

Do not lock refactoring with brittle private assertions or test only success while omitting authorization, partial failure, duplicate execution, and legacy-data compatibility.

## 9. Technical-Debt Register

Known problems that continue to increase cost/risk in G2-G4 belong in `engineering/TECH_DEBT.md`, project issues, or equivalent, with ID/title/status; location and affected module/unit; cause and symptoms; speed/correctness/safety/data/release impact; reason for current acceptance and rejected options; owner and repayment trigger/target; and acceptance/removal method.

Real-debt patches, global suppressions, compatibility branches, and TODOs reference the debt ID or nearby closeout. Do not call every TODO debt. Check repayment triggers when touching its module. Before release, report added, repaid, and still accepted debt without requiring zero debt. Mark repaid only after code, tests, docs, and old entrypoints close. Template: `assets/architecture-governance/TECH_DEBT_REGISTER.template.md`.

## 10. Existing-System Engineering and Debt Review

Review read-only first; findings do not authorize refactoring:

1. Confirm owner-approved authority root, Git root, branch, release units, runtime entrypoints.
2. Check worktree, recent commits, VERSION, changelog, tags, document applicability, runtime version.
3. Inventory languages, frameworks, modules, entrypoints, databases, dependencies, jobs, external services, deployment units.
4. Read current requirements, design, quality, tests, deployment, version, logs; cross-check code.
5. Run declared read-only quality, test, build, architecture commands and preserve failures without repairing baseline.
6. Inspect responsibility, dependencies, ownership, duplication, cycles, hotspots, large files/functions, broad catches, dead code, gaps, legacy.
7. In default `risk_based` mode, semantically sample core paths for invariants, permissions, transactions, idempotency, compensation, consistency at correct boundaries. Only an explicit per-file/function/comment request enters Assurance `exhaustive_source` with a durable completion ledger; sampling cannot claim exhaustive completion.
8. Classify code quality, architecture, debt, test gates, release governance, and separately owned business/safety risks.
9. Rank P0-P3 with location, evidence, impact, recommendation, verification; “refactor” alone is not actionable.
10. Submit report and phased remediation first. Without authority, do not mass-format, move, replace frameworks, or rewrite business logic.

Suggested report: `engineering/audits/ENGINEERING_GOVERNANCE_AND_TECH_DEBT_AUDIT_<YYYY-MM-DD>.md`.

- **P0:** production, data/money/authorization, release, or rollback danger; block affected release.
- **P1:** uncontrolled core architecture or conflicting version truth; prioritize governance.
- **P2:** continuing quality/debt cost; schedule soon.
- **P3:** optional style/low-risk improvement; not a blocker.

Use `assets/architecture-governance/ENGINEERING_AUDIT_TASK.template.md` for risk sampling and `EXHAUSTIVE_SOURCE_REVIEW_TASK.template.md` for exhaustive source governance under Assurance.

## 11. Review and Remediation Closure

Report scope, authority root, branch, commit, release unit, gaps; exact commands/results/evidence; current architecture/version facts; severity-ranked findings; quality/debt baseline; immediate/near/long-term actions; proposed contracts/commands/tests/registers; blind spots and owner decisions.

Remediation is separately authorized and phased: protect critical behavior with tests, repair high-risk boundaries/duplication, then clean low-risk structure/style. Run matching gates and update debt/logs per phase. Do not rewrite the system at once for visual cleanliness.

## 12. Noise Reduction and Exceptions

- Small prototypes may combine current technical specification into a short note and debt into issues; no committee or document sprawl.
- Do not substitute universal size, complexity, or coverage thresholds for project baselines, trends, and critical paths.
- Do not add all historical debt to an unrelated feature branch.
- Do not combine security, business-correctness, and engineering-governance audits into an unowned report. Cross-reference risks with clear next owners.
- This standard owns general governance and adoption, not language, framework, or domain specialist rules.
