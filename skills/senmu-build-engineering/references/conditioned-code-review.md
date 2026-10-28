# Conditioned Code Review

Use these evidence recipes within the existing scoped Engineering review, not as another phase or language standard. Project contracts and applicable language profiles remain authoritative. A visual code pattern is a lead, not a confirmed defect.

**Read as needed:** [Evidence](#evidence-and-counterexamples) · [Responsibilities](#review-responsibilities).

## Evidence and counterexamples

For a material finding identify the violated contract, reachable trigger, evidence, impact, minimum repair and recheck condition. Inspect the protections that could disprove it. Keep insufficiently supported claims suspected, conflicts disputed and refuted findings false-positive with their correction basis. Finding confidence, impact priority and execution completion are different dimensions.

| Lead | Evidence required before confirmation | Counterevidence to inspect |
| --- | --- | --- |
| Null/empty access | An actual source can produce the value and reach the access | Caller validation, parsing and enforced preconditions |
| Shared-state race | Concurrent invocation, shared mutation and a reachable non-atomic interval | Whole-operation locks/transactions, single-executor constraints, read-only sharing |
| Async blocking | Blocking work actually executes on the event-loop path | Executor, worker or framework isolation already in use |
| Repeated side effects | A real retry/duplicate path and an insufficient intent/result binding | Downstream idempotency, reconciliation of unknown outcomes, retry ownership |
| Resource leak | Ownership plus an uncovered normal/error/cancellation exit | Enclosing context manager, framework lifecycle, transferred ownership |
| Performance | Relevant data scale, frequency or hot path and an explainable cost | Small/cold paths, existing indexing/caching, measured dominant cost elsewhere |
| Injection/path escape | Untrusted input reaches the dangerous operation | Parameterization, validated boundary, permissions and isolation |
| Mutable defaults | Actual mutation or a demonstrated project-contract violation | Read-only use, deliberate cache/sentinel; do not invent cross-request corruption |
| Runtime compatibility | The actual minimum/runtime/CI/deployment versions | Project-selected toolchain, compatible API alternatives; the agent's runtime is not authority |
| CI/workflow failure | Trigger, effective permissions, checkout identity, command, dependencies and failure propagation | Trusted baseline, isolation and explicit project settings; an absent field alone is not proof |
| Comment, warning or suppression | A false/missing claim or a demonstrated implementation problem; distinguish text cleanup from code repair and identify affected consumers | Valid internal rationale, complex algorithms, public contracts, legal notices, negative type tests, tool directives and justified temporary constraints |

Review related producers/consumers together when the changed contract requires it. A file's primary reviewer owns its receipt; a cross-file contract needs an explicit check owner even when implementation files are reviewed separately. Share the minimum requirement, preserved/cancelled behavior, frozen scope, rules, existing evidence and unknowns rather than entire chats. This is a review method, not automatic dependency discovery.

Deduplicate findings by root cause, rule, object and impact, not wording alone. Preserve separate remediation responsibilities when several locations need independent repairs. When a finding is disproved, record the counterexample at the existing learning/feedback owner; do not silently turn it into a permanent global exemption.

Public synthetic cases should pair a genuine defect with a similar protected case: nullable vs validated caller input, unprotected vs atomic shared update, event-loop vs worker blocking, unmanaged vs framework-owned resource, and changed interface vs updated consumer. Deterministic record tests prove tooling; only actual host review on such cases can support model-quality claims.

## Review responsibilities

Low-risk work may use evidence-based self-review. Delegate for useful independent exploration, disjoint edits or required review separation. Prefer existing deterministic tools when sufficient. Do not fix model, agent or round counts. Missing host capability permits authorized sequential work, not claims of independent review.

Isolate writers and serialize genuine shared mutation. Account for every slice as a result, blocker, failure or cancellation. Inspect artifacts, not just summaries. When rules, risk or the owner requires separate review:

1. **Implementer Brief:** give the goal, baseline, Task/requirement, `Global Constraints`, `Interfaces`, writable/forbidden paths, inputs, outputs, acceptance, checks, permissions and stop conditions. Do not copy full chats or unrelated standards.
2. **Implementer Report:** identify behavior, changed files/interfaces, exact head, actual checks, deviations and gaps. A claim of completion is not evidence.
3. **Task Review:** challenge assumptions, direction, missing boundaries and simpler alternatives. Trace shared causes. Judge `Requirement/Spec` against approved behavior, scope, non-goals and acceptance. Judge `Engineering/Standards` against correctness, safety, data, compatibility, retirement, tests and maintenance. Include applicable functional and nonfunctional requirements, cohesion, coupling, reuse and framework/design rules. Neither axis substitutes for the other. A Finding names axis, location, trigger, impact, severity and recheck condition. Challenger is a method, not an extra job; same-executor review stays self-review. Assurance owns independent conclusions.
4. **Scoped Re-review:** batch ordinary findings within the agreed scope; interrupt for urgent safety issues. Route repairs by Delivery's [Review Repair Routing](../../senmu-build-delivery/references/multi-agent-change-units-and-version-line-closeout.md#7-review-repair-routing). Recheck findings, delta and affected behavior, not unchanged scope; track unrelated issues separately. Open blockers prevent approval.
5. **Final Review:** summarize both axes over `base..head`, closed findings, checks and blind spots. A new commit renews the candidate conclusion over changed and affected scope; unchanged evidence remains reusable. Delivery may reuse a verdict for the unchanged frozen candidate. Model agreement is not proof or independence.

An internal cache, performance, transaction, queue, consistency or version design that changes user actions, visible state, persistence, recovery or acceptance returns to Product. Compare options preserving approved behavior; never implement first and rewrite the PRD to authorize it.
