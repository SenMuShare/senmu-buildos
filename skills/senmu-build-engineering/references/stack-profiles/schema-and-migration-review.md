# Schema and Migration Review

Use when SQL, Protobuf, GraphQL, Prisma or another schema changes a producer/consumer or stored-data contract. Syntax-specific tooling supplements the current API/data owner; do not introduce a second schema authority.

For SQL and ORM migrations, identify real engine/version, table size, transaction behavior, lock duration, default/backfill semantics and forward recovery. Test representative existing data and rerun behavior; a clean empty database is not migration evidence. Parameterize values and validate dynamic identifiers separately. A migration's successful execution does not prove a deployment rollback can undo data loss.

For Protobuf, preserve field numbers and wire compatibility; reserve removed fields where appropriate and verify the supported client generation. For GraphQL, consider nullability changes, field authorization, query depth/cost and batching amplification, not only resolver success. For Prisma, synchronize generated clients and consumers with the real migration and database constraints.

Review both producer and consumer when a schema, default, error or optionality changes. Keep unknown enum/protocol values decidable. Use current ecosystem compatibility checks and representative contract/migration tests; an unchanged consumer file can still need verification after a shared schema changes.

Calibration: [Protobuf best practices](https://protobuf.dev/best-practices/dos-donts/), [OWASP GraphQL](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html). Engine-specific migration behavior requires its current official documentation.
