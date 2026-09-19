# Backend Service and Data Contracts

Use this standard when server-side contracts for APIs, domain services, data, transactions, caches, queues, or background jobs are missing, conflicting, or changing. Follow sufficient project rules directly. Framework, database, payment, and migration details belong to the matching specialist Skill or project owner.

## 1. Establish Facts and Boundaries

Start from the affected request, event, job, interface or failing check and its applicable contract. Expand to callers, schemas, migrations, authorization, configuration or logs when evidence or the declared scope requires them, not as a mandatory reading list. Identify which domain owner may change the relevant facts and which systems only read, derive, cache or deliver them; known location does not exempt a relevant safety or consistency boundary.

API and event contracts define inputs, outputs, errors, authorization, compatibility, idempotency, timeouts, and observable results. Validate untrusted input and authorize at the real trust boundary. Hidden UI, disabled buttons, and caller conventions do not replace server protection.

## 2. Consistency and Side Effects

- Each business fact has one writable owner. Cross-service collaboration uses explicit API, event, or file contracts, never internal code dependencies or casual shared writes to core tables.
- Give each atomic business operation one explicit transaction owner. Extracting helpers or modules must preserve its commit/rollback boundary; a callee must not silently commit part of the operation. Keep lock duration bounded: do not hold database locks while awaiting a slow external service or human input unless the actual consistency protocol requires it and its cost/failure behavior is justified. This does not prohibit the database protocol's own network I/O. Moving an external call outside a transaction must preserve invariants through the project's existing state check, idempotency and reconciliation strategy, not create an unchecked race. When database commit and an external effect cannot be atomic together, specify order, duplicate handling, visible partial results and recovery without pretending local rollback undoes a completed external action.
- Treat duplicate requests, concurrent updates, reordering, timeouts, redelivery, and process restart as possible. Protect real invariants with constraints, versions, locks, or idempotency semantics.
- A cache is rebuildable derived state, never sole authority. Invalidation, fallback, tolerated staleness, and degraded behavior must match business risk.
- Queues and jobs define delivery semantics, deduplication, retry limits, dead-letter/manual recovery, progress, and result ownership. In-process variables are not recoverable run state.

## 3. Data Evolution

Schemas, indexes, and migrations serve current queries, constraints, and lifecycle. A destructive change defines compatibility window, read/write order, backfill, verification, and rollback boundary. Production-data changes, deletion and irreversible migration require authority and evidence for those exact effects. Reuse a still-valid approval covering them; an ordinary implementation request or a successful check does not grant that authority.

Logs, metrics, and traces retain only what diagnosis requires, excluding secrets, tokens, and unnecessary personal data. Observability cannot repair ambiguous business state; make state machines, errors, and recovery decidable first.

## 4. Verification

Combine unit, contract, integration, migration, and real-dependency tests by risk. On critical paths, verify relevant success, validation failure, denial, duplicate, concurrency, timeout, partial failure, retry, and restart recovery. Mock call counts do not replace database state, responses, events, or external observable results.

Bind verification to the real interface/schema/job version and test-data boundary. If real databases, queues, caches, or third-party sandboxes were not exercised, call the evidence static or substituted; do not claim production behavior.
