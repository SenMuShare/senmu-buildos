# Conditioned Code Review

Use these evidence recipes within the existing [scoped review](source-code-quality-and-ai-collaboration.md#scoped-review-and-closeout), not as another review phase or language standard. Project contracts and applicable language profiles remain authoritative. A visual code pattern is a lead, not a confirmed defect.

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

Review related producers/consumers together when the changed contract requires it. A file's primary reviewer owns its receipt; a cross-file contract needs an explicit check owner even when implementation files are reviewed separately. Share the minimum requirement, preserved/cancelled behavior, frozen scope, rules, existing evidence and unknowns rather than entire chats. This is a review method, not automatic dependency discovery.

Deduplicate findings by root cause, rule, object and impact, not wording alone. Preserve separate remediation responsibilities when several locations need independent repairs. When a finding is disproved, record the counterexample at the existing learning/feedback owner; do not silently turn it into a permanent global exemption.

Public synthetic cases should pair a genuine defect with a similar protected case: nullable vs validated caller input, unprotected vs atomic shared update, event-loop vs worker blocking, unmanaged vs framework-owned resource, and changed interface vs updated consumer. Deterministic record tests prove tooling; only actual host review on such cases can support model-quality claims.
