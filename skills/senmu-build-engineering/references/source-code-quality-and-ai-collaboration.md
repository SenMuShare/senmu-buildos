# Source-Code Quality and AI Collaboration

Approved contracts define the target; code, configuration and checks show observed behavior. Resolve conflicts at their owner, not by changing requirements to fit code. Read stack guidance for a rule gap or standards review.

**Read by task:** [Understand the system](#understand-the-affected-system) · [Investigate](#read-only-investigation) · [Fix a defect](#fault-debugging) · [Change a design](#design-change) · [Refactor](#behavior-preserving-refactoring) · [Review and hand off](#implementer-and-reviewer-responsibilities).

## 1. Quality Model and Authority

Quality is not format compliance. It includes correctness, security, local comprehensibility, locality of change, one source of truth, explicit side effects, testability, and deletability.

Precedence: safety and non-reducible Hard Gates > current project rules/machine configuration > applicable language/framework rules > this standard > community defaults.

AGENTS carries adopted principles, project differences, commands and routes. `CODE_QUALITY` owns quality decisions and exceptions; architecture, debt and testing keep their owners. Shared principles impose no vendor, framework or line count. Keep full methods with their owner. Resolve stale guidance from current owners and authorized decisions; ask only about consequential unknowns or authority. Preserve privacy, safety, permissions, payments, production-data and release boundaries.

## 2. Cross-Language Principles

- Each business fact, state, side effect, and invariant has one owner. Cache, derived UI, and compatibility layers never become silent second sources.
- Model mutually exclusive phases with their required data so invalid combinations are rejected at the relevant boundary. Genuinely independent booleans remain valid. Use the project language and model, not a compulsory state-machine library, engine or document per state.
- Keep knowledge in its owning module. Unrelated modules changing for one small request signal boundary erosion.
- Name modules and functions by responsibility, not length. Distinguish reading, computing, submitting and applying results. Keep related rules together; avoid one-function-per-step layers and whole-codebase style renames.
- Expose inputs, outputs, errors and effects. Do not hide network, database, cancellation or irreversible work behind a pure-looking query. Preserve the difference between asynchronous submission and confirmed completion using project conventions.
- Abstract for known variation, isolation, or testing value; similarity and hypothetical futures do not require a layer.
- Compare standard library, existing dependencies, and platform capability before adding a dependency, including maintenance, security, deployment, and exit cost.
- Temporary compatibility surfaces record consumers, exit conditions, and verification; they are not templates for new work.
- A replacement closes old state, entrypoints, call chains, tests, and docs as one unit, proving the new entrypoint is unique and the old one unreachable or explicitly approved as compatibility.
- When Product permanently retires a capability, remove frontend entrypoints, routes/APIs, jobs/events, service branches, flags/configuration, permission exposure, read/write paths, invalid tests, and current docs. Prove UI, direct calls, automation, and restart defaults cannot restore it. CSS hiding, disconnected controls, disabled-by-default flags, fixed failures, and live backend code retained “for later” are not removal. Retain only approved compatibility, rollback, data-retention, or legal boundaries with owner, consumer, non-default entry, exit condition, and verification. Destruction of historical data requires separate authority.

## 3. Errors, Distributed Calls, and Resources

- Catch errors only where they can be handled or translated without losing their cause. Where callers need different recovery decisions, distinguish a confirmed rejection, a known execution failure and an unknown external outcome. A timeout or cancellation request alone does not prove that an external action did not happen. Do not swallow failure, return success-shaped values or repeatedly log the same exception across layers; use existing exception/result conventions rather than forcing one universal result type on every function.
- External calls need an end-to-end deadline covering connection, DNS/TLS, pool wait, request, and response read. Streaming/offline work also needs cancellation, resource caps, and stop conditions.
- One layer owns retry within a total attempt/time budget, only for classified recoverable failures, with capped backoff, jitter, and quota where needed. Prevent retry multiplication.
- Side-effect retries use a stable intent key atomically linked to the result. Reject or explicitly adjudicate different parameters under one key. For unknown outcomes, query, reconcile, or recover manually before resending.
- Preserve transaction, cancellation, partial-success, duplicate and late-result semantics, and close owned resources. If rollback, cleanup or compensation also fails, retain both the original problem and the recovery failure and report the remaining uncertainty. Do not claim restored state merely because recovery was attempted, mask the original cause in cleanup or resend a side effect while its earlier outcome is unknown.

### External Capability and Identifier Mapping

- Separate stable domain identifiers from external service, endpoint-version, model, or protocol codes. Mapping keys include the real target/version and preserve meaningful region, locale, and capability differences; similar names are not merge evidence.
- Runtime selects only a verified capability record matching the actual endpoint. Unknown, unmapped, or unsupported values fail closed or enter explicit Product policy; never guess the nearest code or reuse another interface's identifier.
- Record source, version, and verification time for changing capabilities. Configuration, implementation, tests, and runtime evidence must reference one mapping identity.

## 4. Comments, Tools, and Tests

Identifiers follow ecosystem conventions. Unless project rules differ, use Simplified Chinese business comments to explain non-obvious intent, constraints and prohibited changes, not narrate code. Explain relevant compatibility, transactions, idempotency, concurrency, security and performance. Remove stale/dead comments and sensitive data. Before deleting a business warning, trace its reason and current applicability. Preserve useful intent nearby or link the decision; uncertainty requires investigation, not deletion.

Formal code projects declare format/autofix, fast quality, full quality, test, and real/integration entrypoints, with scope, cost, and external-system effects. Local and CI reuse configuration. Suppressions record scope, reason, and exit condition.

Tests observe business contracts, not private implementation. Reuse regressions; add coverage for meaningful success, boundary or failure gaps. External-call tests follow relevant deadline, retry, idempotency, late-result and unknown-outcome risks in section 3. Coverage percentages do not replace evidence for money, permissions, data and core flows.

## 5. AI Implementation, Debugging, and Review Loop

Choose the requested result. These methods do not themselves require extra Skills, agents, approvals or registers. Use project rules and sufficient understanding for clear low-risk work. Select Architecture or Testing from the Engineering entry as needed; do not preload their manuals through a language profile.

| Task | Completion evidence |
| --- | --- |
| Read-only investigation | Sources, mechanism, applicable reasons and unknowns |
| Fault debugging | Original failure, supported cause, fix and regression proof |
| Design change | Design-only: caller usage, structure, reasons and unverified questions. Authorized implementation: also prove changed behavior |
| Behavior-preserving refactoring | Baseline and equivalence proof |

### Understand the Affected System

Use for unfamiliar systems, cross-module or critical data/state changes, and code/contract conflicts. Reuse sufficient current understanding.

1. Start at the known entrypoint, symbol, error or failing test, else local navigation. Read requirements, constraints and checks. Known locations skip navigation, not constraints; fill missing stack/risk rules from specialist guidance.
2. Trace inputs, outputs, control flow, decorators, state, errors, effects, owners and invariants. Before changing public contracts, shared state, defaults or cross-module calls, identify direct/indirect consumers, configuration and runtime dispatch. State affected paths, why others stay safe with evidence, and checks or gaps. Expand only as justified; use worktree-matched indexes. An empty search does not rule out dynamic consumers. Reuse sufficient evidence; extra checks follow impact or uncertainty.
3. Recover Decision Rationale, Rejected Alternatives, Preserved Constraints and Revisit Trigger from requirements/design/specifications. Resolve gaps using path/symbol history, introducing diffs and linked PRs, Issues or decisions; other authorized sources need relevant leads. Blame locates changes, not intent. Separate verified (direct evidence/ref), inferred (facts and alternatives) and unknown (missing, inaccessible or conflicting evidence). Commit messages alone do not prove intent; shallow history cannot prove no rationale existed.
4. Recheck historical conditions. State what to preserve, change within authority, avoid restoring and leave unproven. History cannot freeze decisions or excuse safety defects. Approved contracts define the target; resolve code conflicts at their owner.
5. Stop with sufficient evidence for the next step. Explain entry, flow, owners, effects, constraints and checks with sources. Keep useful findings in existing task/design records, not new documents. Missing reasons stay unknown.

### Read-Only Investigation

Scope the question, trace the system, then explain its mechanism and tradeoffs with sources. A file list is not an explanation. Preserve uncertainty about history.

Investigation does not authorize edits, runtime injection, external writes or paid probes. Report unavailable evidence and the smallest useful next check. A recommendation stays a recommendation unless the same request already authorizes implementation.

### Fault Debugging

Use the original symptom as the completion test.

1. Establish intended behavior and the symptom; distinguish `confirmed`, `likely_unreproduced`, `expected_behavior`, `duplicate` and `out_of_scope`. Preserve dirty work.
2. Use a repeatable regression, replay, CLI/browser script, differential run or controlled observation of the exact symptom on the original or production-shaped path. Run cheap failing tests before repair. If environment, state or authority prevents reproduction, state the evidence and missing observation; continue independently testable work without claiming reproduction.
3. Reduce inputs, configuration and steps one at a time while retaining the failure and potentially causal production conditions. Compare healthy and failing paths with current system knowledge and relevant history. Name discriminating predictions for competing causes and run the cheapest useful probe. Change one variable at a time; discard refuted hypotheses and temporary edits. If probes add no evidence, reassess the premise rather than adding guards.
4. Repair the cause at its owner within scope; inspect analogous paths when evidence shows a shared pattern. Bounded repair or containment can be appropriate: disclose remaining causes and revisit conditions. Root repair grants no redesign authority.
5. Verify the original scenario as well as any minimized repro, then affected regressions under Testing. Preserve dependency shape, error and cancellation semantics. Generic green tests cannot replace original-path evidence; production-only state does not authorize production changes.
6. Remove task-owned debug logs, flags and unsupported workarounds. Report symptom, cause evidence, fix, before/after checks and gaps; unproven causes remain unverified. Continue with scoped review.

### Design Change

Confirm whether the request ends at a design or includes implementation. Establish the approved outcome and affected-system model, then use Architecture to design caller usage, data, interfaces, state and ownership. Compare alternatives only for a real choice. A design-only request ends with the proposal, reasons and unverified questions; it does not authorize code changes or runtime claims. With implementation authority, investigate repeated deviations instead of patching a wrong design, then verify the behavior and affected consumers and review.

### Behavior-Preserving Refactoring

Pin intended behavior before moving structure. Reuse regression coverage; fill real gaps with characterization, snapshots, replay or equivalence checks. Types and lint alone do not prove equivalence. An observed defect is not automatically approved behavior; separate its repair or return changed outcomes to Product.

State the target ownership and shape. Use Architecture for boundary decisions, not mechanical edits. Remove verified obsolete wiring in checkable steps. Migrate coordinated internal callers together while preserving required external compatibility. Verify the real entrypoint and affected consumers. Keep maintenance improvements, not fewer lines or layers at the cost of behavior.

### Scoped Review and Closeout

State the behavior change, scope, risk, checks and owners to synchronize. Complete the smallest end-to-end slice. During an open batch, run focused checks for credibility and early risk detection. Testing owns expansion, stopping and evidence reuse; do not run full gates after each item.

Product owns behavior and acceptance, design records own technical decisions, and tasks own progress. Each formal version retains a technical account under [Product Iteration](../../senmu-build-product/references/product-requirements-and-iteration.md), not another document per edit. Maintain changed responsibility, entrypoint, contract or verification routes under Project's [Index Contract](../../senmu-build-project/references/project-standard-discovery-and-on-demand-loading.md#4-index-contract). Trace affected routes in the receiving worktree to their real destinations; unchanged routes need no update.

Review the whole scoped diff, changed functions and existing comments against approved intent. Check types, valid states, transactions/effects, failure/recovery, reuse and necessary seams. Preserve outputs, errors, state and order. Paths and test totals are not semantic proof. A synchronization outside write authority remains an explicit open action.

Checkpoint commits and review heads may remain `in_progress`. Delivery seals only authorized, checked and reviewed batch closeout. Incomplete scope, failures or mixed work cannot close. Distinguish implementation, verification, acceptance and release. Record important decisions and remaining work, not every tool call.

### Implementer and Reviewer Responsibilities

Low-risk work may use evidence-based self-review. Delegate for useful independent exploration, disjoint edits or required review separation. Prefer existing deterministic tools when sufficient. Do not fix model, agent or round counts. Missing host capability permits authorized sequential work, not claims of independent review.

Isolate writers and serialize genuine shared mutation. Account for every slice as a result, blocker, failure or cancellation. Inspect artifacts, not just summaries. When rules, risk or the owner requires separate review:

1. **Implementer Brief:** give the goal, baseline, Task/requirement, `Global Constraints`, `Interfaces`, writable/forbidden paths, inputs, outputs, acceptance, checks, permissions and stop conditions. Do not copy full chats or unrelated standards.
2. **Implementer Report:** identify behavior, changed files/interfaces, exact head, actual checks, deviations and gaps. A claim of completion is not evidence.
3. **Task Review:** challenge assumptions, direction, missing boundaries and simpler alternatives. Trace shared causes. Judge `Requirement/Spec` against approved behavior, scope, non-goals and acceptance. Judge `Engineering/Standards` against correctness, safety, data, compatibility, retirement, tests and maintenance. Include applicable functional and nonfunctional requirements, cohesion, coupling, reuse and framework/design rules. Neither axis substitutes for the other. A Finding names axis, location, trigger, impact, severity and recheck condition. Challenger is a method, not an extra job; same-executor review stays self-review. Assurance owns independent conclusions.
4. **Scoped Re-review:** batch ordinary findings within the agreed scope; interrupt for urgent safety issues. Route repairs by Delivery's [Review Repair Routing](../../senmu-build-delivery/references/multi-agent-change-units-and-version-line-closeout.md#7-review-repair-routing). Recheck findings, delta and affected behavior, not unchanged scope; track unrelated issues separately. Open blockers prevent approval.
5. **Final Review:** summarize both axes over `base..head`, closed findings, checks and blind spots. A new commit renews the candidate conclusion over changed and affected scope; unchanged evidence remains reusable. Delivery may reuse a verdict for the unchanged frozen candidate. Model agreement is not proof or independence.

An internal cache, performance, transaction, queue, consistency or version design that changes user actions, visible state, persistence, recovery or acceptance returns to Product. Compare options preserving approved behavior; never implement first and rewrite the PRD to authorize it.

## 6. Risk Proportion and Legacy Projects

For reversible, single-owner G1 work preserving product, runtime and delivery contracts, read affected code and rules without unrelated governance artifacts. Authorized existing-document and route corrections remain in scope. Testing owns batch timing.

G2-G4 progressively need stronger evidence for types, behavior, builds, architecture, safety, data, authority and real flows. Higher risk alone does not invoke several Skills or independent reviewers. Verify high-risk paths early; do not postpone all checks to version end or run full gates for every unfinished edit.

Derive legacy-project rules from configuration, representative code and frequent changes. Preserve the stack; use official ecosystem guidance when no language Profile exists. Put stable executable differences in original owners.

Record an exception's reason, scope, impact, owner and exit condition. Keep each complete rule with one owner; entrypoints and task briefs carry only useful scoped summaries and a working route. Source review and executed evidence remain distinct.
