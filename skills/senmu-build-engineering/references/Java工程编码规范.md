# Java Engineering Profile

This profile owns Java-specific resource, exception, and build-tool application. The general source-quality standard owns cross-language responsibility, dependencies, side effects, tests, and review. Project formatter, Checkstyle/lint, imports, width, naming, and Javadoc conventions prevail; do not copy a vendor style guide here.

## Resources and Exceptions

- Manage an `AutoCloseable`/`Closeable` created or taken over by the current method with try-with-resources in the smallest scope. Files, streams, JDBC objects, and clients must not rely on garbage collection.
- Close several resources in reverse declaration order. When body and close both fail, preserve the body exception and inspect suppressed exceptions; handwritten `finally` must not overwrite the root cause.
- Do not close resources owned by a container, pool, or caller, but make ownership and lifetime discoverable in interfaces, framework configuration, or project contracts.
- Catch the most specific exception only when recovery, domain meaning, or boundary conversion is possible; preserve the original cause when wrapping. Never use empty catches, turn failure into `null`/success, or log the same stack at several layers.
- Follow project and public-API contracts for checked versus unchecked exceptions. Do not eliminate compile errors by wrapping everything in a meaningless `RuntimeException`.

## APIs and Structure

- Organize packages, classes, and methods by domain responsibility. Before adding a public API, establish callers, compatibility, thread safety, nullability, collection mutability, and resource ownership.
- Preserve the project's nullness annotation, `Optional`, or static-analysis convention. Do not mass-migrate by preference when no unified contract exists. Isolate external API compatibility in adapters.
- Do not expose mutable internal collections. Shared mutable state needs explicit synchronization, transaction, and lifetime semantics—not a comment that assumes safety.
- Javadoc documents public contract, preconditions, side effects, exceptions, and non-obvious tradeoffs without repeating signatures. Implementation comments explain reasons and constraints.

## Tools, Tests, and Completion

- Maven/Gradle or the unified project script provides format, static analysis, compile, test, and build entrypoints, shared locally and in CI. Govern generated code through its generator; do not patch products manually.
- Resource tests cover success, body failure, close failure, and multiple resources. Exception tests verify type, cause, suppressed exceptions, log count, and external error contract.
- Concurrency, transaction, serialization, and public-API changes remain governed by the project framework, JDK, and architecture contract; this profile imposes no universal framework or numeric threshold.

Before completion, confirm resource ownership/closure, intact cause chains, public API compatibility/thread semantics, and project-contracted formatter/static checks, compile, tests, and build. Report omissions truthfully.
