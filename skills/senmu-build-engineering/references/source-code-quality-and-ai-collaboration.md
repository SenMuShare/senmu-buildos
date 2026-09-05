# Source-Code Quality and AI Collaboration

This standard owns only cross-language rules that change engineering decisions. Current code, configuration, quality commands, and specialist project owners prevail. Load language/framework references only when project rules are missing or standards review requires them.

## 1. Quality Model and Authority

Quality is not format compliance. It includes correctness, security, local comprehensibility, locality of change, one source of truth, explicit side effects, testability, and deletability.

Precedence: safety and non-reducible Hard Gates > current project rules/machine configuration > applicable language/framework rules > this standard > community defaults.

Project `AGENTS.md` contains deltas, real commands, and routing; `CODE_QUALITY` owns project quality decisions/exceptions; architecture, debt, and testing remain with their owners. Do not copy BuildOS prose into a project. Present conflicts for user decision when project rules are stale, inconsistent, or weaken safety, privacy, authorization, payments, production-data, or release gates.

## 2. Cross-Language Principles

- Each business fact, state, side effect, and invariant has one owner. Cache, derived UI, and compatibility layers never become silent second sources.
- Keep a change in the module owning its knowledge. A small change requiring many unrelated modules signals boundary erosion.
- Organize functions/modules by nameable responsibility, not line limits. Keep business rules, I/O, persistence, and external calls distinguishable.
- Make inputs, outputs, failures, and side effects discoverable. Do not hide networks, databases, files, or irreversible actions behind apparently pure interfaces.
- Abstract for known variation, isolation, or testing value; similarity and hypothetical futures do not require a layer.
- Compare standard library, existing dependencies, and platform capability before adding a dependency, including maintenance, security, deployment, and exit cost.
- Temporary compatibility surfaces record consumers, exit conditions, and verification; they are not templates for new work.
- A replacement closes old state, entrypoints, call chains, tests, and docs as one unit, proving the new entrypoint is unique and the old one unreachable or explicitly approved as compatibility.
- When Product permanently retires a capability, remove frontend entrypoints, routes/APIs, jobs/events, service branches, flags/configuration, permission exposure, read/write paths, invalid tests, and current docs. Prove UI, direct calls, automation, and restart defaults cannot restore it. CSS hiding, disconnected controls, disabled-by-default flags, fixed failures, and live backend code retained “for later” are not removal. Retain only approved compatibility, rollback, data-retention, or legal boundaries with owner, consumer, non-default entry, exit condition, and verification. Destruction of historical data requires separate authority.

## 3. Errors, Distributed Calls, and Resources

- Catch only errors that can be handled; preserve causes and convert at the proper boundary. Do not swallow failure, return a success-shaped value, or log the same exception repeatedly.
- External calls need an end-to-end deadline covering connection, DNS/TLS, pool wait, request, and response read. Streaming/offline work also needs cancellation, resource caps, and stop conditions.
- One layer owns retry within a total attempt/time budget, only for classified recoverable failures, with capped backoff, jitter, and quota where needed. Prevent retry multiplication.
- Side-effect retries use a stable intent key atomically linked to the result. Reject or explicitly adjudicate different parameters under one key. For unknown outcomes, query, reconcile, or recover manually before resending.
- Define transaction, cancellation, partial-success, duplicate, and late-result semantics, and close files, connections, locks, and sessions.

### External Capability and Identifier Mapping

- Separate stable domain identifiers from external service, endpoint-version, model, or protocol codes. Mapping keys include the real target/version and preserve meaningful region, locale, and capability differences; similar names are not merge evidence.
- Runtime selects only a verified capability record matching the actual endpoint. Unknown, unmapped, or unsupported values fail closed or enter explicit Product policy; never guess the nearest code or reuse another interface's identifier.
- Record source, version, and verification time for changing capabilities. Configuration, implementation, tests, and runtime evidence must reference one mapping identity.

## 4. Comments, Tools, and Tests

Identifiers follow ecosystem conventions. Unless project rules say otherwise, business comments use Simplified Chinese to explain rationale, constraints, and prohibited changes, not translate each line. Explain complex business rules, compatibility, transactions, idempotency, concurrency, security, performance, and non-obvious effects. Remove stale comments, large dead-code blocks, and sensitive information.

Formal code projects declare format/autofix, fast quality, full quality, test, and real/integration entrypoints, with scope, cost, and external-system effects. Local and CI reuse configuration. Suppressions record scope, reason, and exit condition.

Tests observe business contracts, not private implementation. Reuse a regression covering the original defect; add one only when existing coverage or alternate repeatable evidence is insufficient. Cover critical success, boundaries, and meaningful failures. For remote calls, test risk-relevant deadlines, budgets, backoff, amplification, idempotency, duplicates/late results, and reconciliation of unknown outcomes. Coverage percentages do not replace risk coverage for money, permissions, data, and core flows.

## 5. AI Implementation, Debugging, and Review Loop

1. Read real entrypoints, requirements/acceptance, call chain, configuration, tests, analogous implementation, and applicable Task/TD/ADR decisions. Freeze the symptom and classify `confirmed`, `likely_unreproduced`, `expected_behavior`, `duplicate`, or `out_of_scope`; use Kernel protection for dirty work before writing. For surprising or apparently redundant behavior, check Decision Rationale, Rejected Alternatives, Preserved Constraints, and Revisit Trigger. Do not silently restore a rejected option while conditions remain; if conditions changed, return new evidence to the owner and preserve supersession. Historical decisions never exempt apparent safety defects.
2. Trace the highest upstream cause that explains the symptom: requirement/responsibility owner -> architecture/dependencies -> call/data/state/side-effect chain -> business logic/invariants -> local implementation. Eliminate the class at that owner, then residual defects. Expand only with evidence; a sufficient local cause without upstream signals does not require architecture review.
3. State behavior change, scope, risk, tests, and owners to synchronize. Close the smallest end-to-end slice from authoritative input through real path to observable result and matching verification. Prompts, checklists, and validators do not replace root-cause repair.
4. During an open batch, run only targeted checks needed to keep implementation credible and address failures. Do not trigger every full gate after each item. Update durable task state only at meaningful phases.
5. Route user behavior/acceptance changes to Product; module/public interface/data/dependency/durable direction to TD/ADR; execution-order changes to Task.
6. Review reuse, quality, and efficiency only for stable changed scope and necessary seams. Preserve outputs, errors, state, side effects, and order; line deletion and abstraction count are not outcomes.
7. Review the complete diff, changed functions, and existing comments. Self-review does not replace required separation-of-duty approval.
8. A clear phase may use a local checkpoint commit while the Change Unit remains `in_progress`. After test/handoff confirmation, freeze the complete diff, run batch checks from the testing standard, and seal a stable commit. Do not fake closeout when scope is incomplete, checks fail, project rules prohibit it, or another contributor's changes would be mixed. Engineering may claim only `implemented`.

### Fault Debugging

Create a short, stable failing loop that distinguishes before/after. Proceed: reproduce/narrow -> compare healthy path -> rank hypotheses -> observe one variable -> fix -> regress original path -> regress impact surface -> clean up. Preserve the original symptom, key dependency shape, and reproducible entrypoint. Make each hypothesis falsifiable by logs, debugger, minimal script, test, or configuration comparison. Change one observation/variable at a time; remove unsupported hypotheses and temporary edits. If repeated attempts add no evidence, only move symptoms, or continually expand scope, stop and reassess owner, interface assumptions, architecture boundary, and smallest next step. Prove the original path first, then impact scope, and remove debug logs, flags, scripts, and weakened protections. Without a stable red condition, report evidence strength rather than a closed root cause.

### Implementer and Reviewer Responsibilities

Ordinary low-risk work may use evidence-based self-review. Invoke this protocol only when project rules, risk, or owner requires separation; it does not prescribe agent count or rounds:

1. **Implementer Brief:** reference Task/requirement; include `Global Constraints`, `Interfaces`, writable scope, acceptance, and output contract—never full chat or unrelated standards.
2. **Implementer Report:** actual behavior, files/interfaces, tests, deviations, known gaps, and exact head; “done” is not evidence.
3. **Task Review:** begin with a lightweight Challenger Review that attempts to falsify direction, assumptions, omitted boundaries, and simpler alternatives. Trace shared upstream causes rather than fragmenting symptoms. Conclude on two independent axes: `Requirement/Spec` checks approved requirement, acceptance, scope, non-goals, and user-visible behavior; `Engineering/Standards` checks the real diff for correctness, safety, data, compatibility, full retirement, tests, and maintenance cost. One passing axis cannot hide another failure. A Finding names axis, location, trigger, impact, severity, and recheck condition. Challenger is a method, not a job or mandatory extra agent; same-executor review remains self-review. Use Assurance rules for an independent conclusion.
4. **Scoped Re-review:** repair within the current Change Unit. Recheck the Finding, repair diff, and affected chain, not unrelated checklists. Register new problems separately; open blockers prevent approval.
5. **Final Review:** summarize both axes over complete `base..head`, closed Findings, matching tests, and blind spots. Any new commit invalidates the conclusion. Delivery may reuse it while frozen head remains unchanged.

If an internal performance, cache, transaction, queue, consistency, or version design changes user actions, visible state, activation/persistence, undo/recovery, or acceptance, compare engineering alternatives that preserve approved behavior and return to Product. Never implement first and rewrite the PRD to self-authorize.

## 6. Risk Proportion and Legacy Projects

For G1 locally reversible, single-owner changes preserving product/runtime/delivery contracts, read only affected code and local rules; do not create Task, TD, ADR, PRD, or Changelog. The testing standard owns check and batch-close timing.

G2-G4 progressively add types, tests, build, architecture, safety, data, authorization, and real-flow verification. A higher level increases evidence strength; it does not automatically invoke several Skills or independent review.

In legacy projects, derive rules from real configuration, representative code, and frequent changes; write only stable, repeated, executable project differences to original owners. Without a language Profile, preserve the stack and use project configuration plus the official ecosystem.

Every exception records reason, scope, impact, owner, and exit condition. A reusable rule has one owner and is not copied across entrypoint, language Profile, project docs, and lesson register.
