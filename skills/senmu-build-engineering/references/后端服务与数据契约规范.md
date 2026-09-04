# Backend Service and Data Contracts

Use this standard when server-side contracts for APIs, domain services, data, transactions, caches, queues, or background jobs are missing, conflicting, or changing. Follow sufficient project rules directly. Framework, database, payment, and migration details belong to the matching specialist Skill or project owner.

## 1. Establish Facts and Boundaries

Read real entrypoints, callers, interfaces, schemas, migrations, authorization, job runners, configuration, logs, and tests. Identify where requests/events enter, which domain owner may change core facts, and which systems only read, derive, cache, or deliver them.

API and event contracts define inputs, outputs, errors, authorization, compatibility, idempotency, timeouts, and observable results. Validate untrusted input and authorize at the real trust boundary. Hidden UI, disabled buttons, and caller conventions do not replace server protection.

## 2. Consistency and Side Effects

- Each business fact has one writable owner. Cross-service collaboration uses explicit API, event, or file contracts, never internal code dependencies or casual shared writes to core tables.
- Transactions cover only state changes that must be atomic. When database commit and external side effects cannot share a transaction, define order, idempotency key, retry, compensation, and visibility of partial failure.
- Treat duplicate requests, concurrent updates, reordering, timeouts, redelivery, and process restart as possible. Protect real invariants with constraints, versions, locks, or idempotency semantics.
- A cache is rebuildable derived state, never sole authority. Invalidation, fallback, tolerated staleness, and degraded behavior must match business risk.
- Queues and jobs define delivery semantics, deduplication, retry limits, dead-letter/manual recovery, progress, and result ownership. In-process variables are not recoverable run state.

## 3. Data Evolution

Schemas, indexes, and migrations serve current queries, constraints, and lifecycle. A destructive change defines compatibility window, read/write order, backfill, verification, and rollback boundary. Production-data modification/deletion or irreversible migration requires separate authority and evidence.

Logs, metrics, and traces retain only what diagnosis requires, excluding secrets, tokens, and unnecessary personal data. Observability cannot repair ambiguous business state; make state machines, errors, and recovery decidable first.

## 4. Verification

Combine unit, contract, integration, migration, and real-dependency tests by risk. On critical paths, verify relevant success, validation failure, denial, duplicate, concurrency, timeout, partial failure, retry, and restart recovery. Mock call counts do not replace database state, responses, events, or external observable results.

Bind verification to the real interface/schema/job version and test-data boundary. If real databases, queues, caches, or third-party sandboxes were not exercised, call the evidence static or substituted; do not claim production behavior.
