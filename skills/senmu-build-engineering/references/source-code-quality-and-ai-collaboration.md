# Source-Code Quality and AI Collaboration

Approved contracts define the target; code and checks show observed behavior. Resolve conflicts at their owner, not by rewriting requirements to fit code. Read stack guidance for rule gaps or standards review.

**By task:** [Comments](#4-comments-tools-and-tests) · [Understand](#understand-the-affected-system) · [Investigate](#read-only-investigation) · [Debug](#fault-debugging) · [Design](#design-change) · [Refactor](#behavior-preserving-refactoring) · [Review](#implementer-and-reviewer-responsibilities).

## 1. Quality Model and Authority

Quality includes correctness, security, clarity, local change, one source of truth, explicit effects, testability and deletability—not just format.

Precedence: safety and non-reducible Hard Gates > current project rules/machine configuration > applicable language/framework rules > this standard > community defaults.

AGENTS keeps principles, project differences, commands and routes. `CODE_QUALITY` owns quality decisions and exceptions; methods, architecture, debt and testing retain their owners. Resolve stale guidance from those owners and authorized decisions. Ask only about consequential unknowns or authority. Impose no vendor, framework or line count. Preserve privacy, safety, permissions, payments, production data and release boundaries.

## 2. Cross-Language Principles

- Each business fact, state, effect and invariant has one owner. Caches, derived UI and compatibility layers must not become competing sources.
- Model exclusive phases with their required data; reject invalid combinations at the responsible boundary. Independent booleans remain valid. Use project conventions, not a compulsory state-machine library, engine or document per state.
- Keep related knowledge with its owner. A small request changing unrelated modules signals boundary erosion. Name functions and modules by responsibility; avoid one-function-per-step layers or whole-codebase style renames.
- Make inputs, outputs, errors and effects explicit. Distinguish reading, computing, submitting and applying results. Network, database, cancellation and irreversible work must not look pure; asynchronous submission must not imply completion.
- Abstract for real variation, isolation, testing or a clear concept/complex boundary; otherwise keep simple one-use logic inline. Similarity alone does not justify a layer.
- Omit speculative guards, retries and compatibility paths without a reachable failure and proportionate benefit. Use existing authority for consequential scope or cost changes; retain required protections.
- Validate untrusted input at its boundary; reuse still-valid guarantees internally. New trust boundaries, changed state and distinct business invariants need checks. Type annotations and casts alone are not runtime validation.
- Before adding a dependency, compare standard, installed and platform capabilities, including maintenance, security, deployment and exit cost.
- Record temporary compatibility consumers, exit conditions and checks; do not copy it into new work.
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

### Writing comments

- Follow project language and ecosystem conventions. Without a project override, business comments default to Simplified Chinese. Never include secrets. No per-function quota or deletion target.
- Make names and structure clear before adding narration. Keep non-obvious reasons and internal business constraints, not just external limitations. Explain complex algorithms or regex mechanics when useful; “why, not what” is not a ban on explanation.
- Public API documentation states purpose, usage, inputs, results, failures and effects. Preserve legal notices and necessary nearby rationale; link substantial decisions to their existing owner. Add missing guidance for correct use or safe changes, not invented history.
- Explain a temporary workaround’s reason, scope and exit condition or link its issue. Do not normalize a defect with a confident explanation or require a new debt record for every note.
- Inspect consumers of suppressions, build/generator directives, docstrings and executable examples before changing them. A negative type test can legitimately use `@ts-expect-error`; its presence alone is not a defect. Keep suppressions scoped and justified; temporary ones need an exit condition.

### Governing existing comments

1. Review changed code and affected nearby comments during ordinary work; honor the declared scope of a dedicated audit. Read-only review does not edit. Cleanup does not authorize behavior redesign or unrelated sweeps. Govern vendor/generated content at its authorized source.
2. Check consequential claims against code, contracts, tests and design history. Long explanations and warning words are leads, not defects. Judge text and implementation separately. Investigate concrete gaps; trivial narration needs no history search.
3. Delete redundant/stale text, correct inaccuracies, add missing information and keep useful explanation. Repair exposed implementation defects within authority and verify them before closure. Deleting an explanation is not fixing its defect. Keep justified interim constraints pending repair.
4. If reasons remain unknown, keep the necessary warning as unverified information, not fact or a permanent veto. Record missing evidence and the next check in the existing task. Pause only the dependent consequential change; continue independent work.
5. Prefer correct structure or existing enforcement over repeated warnings. Add protection only for a real gap; verify replacement protection before removing a safety warning. Tests do not erase useful rationale or require a new check per comment.
6. Verify affected behavior, tool directives and documented/generated contracts; reuse valid evidence. Separate unresolved implementation risks from text cleanup, not by deletion counts. For recurring policy failures, use existing Learning and project-standard maintenance to distinguish wrong rules, missing routes and bad defaults. Repair the original owner without a new comment register.

Formal code projects declare format/autofix, fast quality, full quality, test, and real/integration entrypoints, with scope, cost, and external-system effects. Local and CI reuse configuration.

Tests observe business contracts, not private implementation. Reuse regressions; add coverage for meaningful success, boundary or failure gaps. External-call tests follow relevant deadline, retry, idempotency, late-result and unknown-outcome risks in section 3. Coverage percentages do not replace evidence for money, permissions, data and core flows.

## 5. AI Implementation, Debugging, and Review Loop

Use project rules and sufficient evidence for clear low-risk work. For material uncertainty, tradeoffs or rework, distinguish approved outcomes, constraints, assumptions and replaceable means. Compare meaningful options by fit, consequences, reversibility and lifecycle cost; obtain evidence when its decision value warrants cost or delay. Take a useful step, assess and adapt. This requires no fixed stages, reports, extra Skills, agents, approvals or registers. Select Architecture or Testing from Engineering as needed, not via language-profile preloads.

| Task | Completion evidence |
| --- | --- |
| Read-only investigation | Sources, mechanism, applicable reasons and unknowns |
| Fault debugging | Original failure, supported cause, fix and regression proof |
| Design change | Design-only: caller usage, structure, reasons and unverified questions. Authorized implementation: also prove changed behavior |
| Behavior-preserving refactoring | Baseline and equivalence proof |

### Understand the Affected System

Use for unfamiliar systems, cross-module or critical data/state changes, and code/contract conflicts. Reuse sufficient current understanding.

1. Start at the known entrypoint, symbol, error or failing test, else local navigation. Read requirements, constraints and checks. Known locations skip navigation, not constraints; fill missing stack/risk rules from specialist guidance.
2. Trace inputs, outputs, control flow, decorators, state, errors, effects, owners and invariants. Before changing public contracts, shared state, defaults or cross-module calls, identify direct/indirect consumers, configuration and runtime dispatch. State affected paths, safety evidence, checks and gaps. Expand for impact or uncertainty; reuse sufficient evidence and worktree-matched indexes. Empty searches do not rule out dynamic consumers.
3. Recover Decision Rationale, Rejected Alternatives, Preserved Constraints and Revisit Trigger from requirements/design/specifications. Fill gaps from relevant path/symbol history, introducing diffs, PRs, Issues or decisions; other authorized sources need leads. Blame locates changes, not intent. Distinguish verified (direct evidence), inferred (facts/alternatives) and unknown (missing, inaccessible or conflicting). Commit messages alone cannot prove intent; shallow history cannot prove no rationale existed.
4. Recheck historical conditions. State what to preserve, change within authority, avoid restoring and leave unproven. History cannot freeze decisions or excuse safety defects. Approved contracts define the target; resolve code conflicts at their owner.
5. Stop with sufficient evidence for the next step. Explain entry, flow, owners, effects, constraints and checks with sources. Keep useful findings in existing task/design records, not new documents. Missing reasons stay unknown.

### Read-Only Investigation

Scope the question, trace the system and explain mechanisms/tradeoffs with sources, preserving historical uncertainty. A file list is not an explanation.

Investigation does not authorize edits, runtime injection, external writes or paid probes. Report unavailable evidence and the smallest useful next check. A recommendation stays a recommendation unless the same request already authorizes implementation.

### Fault Debugging

Use the original symptom as the completion test.

1. Establish intended behavior and the symptom; distinguish `confirmed`, `likely_unreproduced`, `expected_behavior`, `duplicate` and `out_of_scope`. Preserve dirty work.
2. Use a repeatable regression, replay, CLI/browser script, differential run or controlled observation of the exact symptom on the original or production-shaped path. Run cheap failing tests before repair. If environment, state or authority prevents reproduction, state the evidence and missing observation; continue independently testable work without claiming reproduction.
3. Reduce inputs, configuration and steps one at a time, retaining failure and potentially causal production conditions. Compare healthy/failing paths using current knowledge and relevant history. Predict what distinguishes competing causes; run the cheapest useful probe, changing one variable at a time. Discard refuted hypotheses and temporary edits. Without new evidence, reassess the premise rather than add guards.
4. Repair the cause at its owner within scope; inspect analogous paths when evidence shows a shared pattern. Bounded repair or containment can be appropriate: disclose remaining causes and revisit conditions. Root repair grants no redesign authority.
5. Verify the original scenario as well as any minimized repro, then affected regressions under Testing. Preserve dependency shape, error and cancellation semantics. Generic green tests cannot replace original-path evidence; production-only state does not authorize production changes.
6. Remove task-owned debug logs, flags and unsupported workarounds. Report symptom, cause evidence, fix, before/after checks and gaps; unproven causes remain unverified. Continue with scoped review.

### Design Change

Confirm design-only or implementation scope. Establish the approved outcome and affected-system model; use Architecture for caller usage, data, interfaces, state and ownership. Compare alternatives for real choices. Design-only ends with proposal, reasons and unverified questions, not code changes or runtime claims. With implementation authority, investigate repeated deviations rather than patch a wrong design; verify behavior and affected consumers, then review.

### Behavior-Preserving Refactoring

Pin intended behavior before moving structure. Reuse regression coverage; fill real gaps with characterization, snapshots, replay or equivalence checks. Types and lint alone do not prove equivalence. An observed defect is not automatically approved behavior; separate its repair or return changed outcomes to Product.

State the target ownership and shape. Use Architecture for boundary decisions, not mechanical edits. Remove verified obsolete wiring in checkable steps. Migrate coordinated internal callers together while preserving required external compatibility. Verify the real entrypoint and affected consumers. Keep maintenance improvements, not fewer lines or layers at the cost of behavior.

### Scoped Review and Closeout

State the behavior change, scope, risk, checks and owners to synchronize. Complete the smallest end-to-end slice; use focused open-batch checks for credibility and early risk detection. Testing owns expansion, stopping and evidence reuse; do not run full gates after each item.

Product owns behavior and acceptance, design records own technical decisions, and tasks own progress. Each formal version retains a technical account under [Product Iteration](../../senmu-build-product/references/product-requirements-and-iteration.md), not another document per edit. Maintain changed responsibility, entrypoint, contract or verification routes under Project's [Index Contract](../../senmu-build-project/references/project-standard-discovery-and-on-demand-loading.md#4-index-contract). Trace affected routes in the receiving worktree to their real destinations; unchanged routes need no update.

Review the whole scoped diff, changed functions and comments against approved intent: types, valid states, transactions/effects, failure/recovery, reuse and necessary seams. Preserve outputs, errors, state and order. Paths/test totals are not semantic proof; synchronization outside write authority remains open.

Checkpoint commits and review heads may remain `in_progress`. Delivery seals only authorized, checked and reviewed batch closeout. Incomplete scope, failures or mixed work cannot close. Distinguish implementation, verification, acceptance and release. Record important decisions and remaining work, not every tool call.

### Implementer and Reviewer Responsibilities

For self-checks, useful delegation or required separation, select Review from Engineering, retaining evidence and repair boundaries. Implementation-only tasks do not preload it.

## 6. Risk Proportion and Legacy Projects

For reversible, single-owner G1 work preserving product, runtime and delivery contracts, read affected code and rules without unrelated governance artifacts. Authorized existing-document and route corrections remain in scope. Testing owns batch timing.

G2-G4 progressively need stronger evidence for types, behavior, builds, architecture, safety, data, authority and real flows. Higher risk alone does not invoke several Skills or independent reviewers. Verify high-risk paths early; do not postpone all checks to version end or run full gates for every unfinished edit.

Derive legacy-project rules from configuration, representative code and frequent changes. Preserve the stack; use official ecosystem guidance when no language Profile exists. Put stable executable differences in original owners.

Exceptions retain reason, scope, impact, owner and exit conditions. Keep full rules at one owner; entries and task briefs summarize and link. Distinguish source review from executed evidence.
