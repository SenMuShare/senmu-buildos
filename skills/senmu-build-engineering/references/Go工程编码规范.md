# Go Engineering Profile

This profile owns Go-specific error values, goroutine lifecycles, package semantics, and standard tools. The general source-quality standard owns responsibility, dependencies, side effects, tests, and review. Project Go version, modules, generators, and deployment constraints prevail over preference.

## Packages and APIs

- Organize packages around nameable responsibilities. Use short, specific names that read naturally at call sites; avoid unowned `util`, `common`, `misc`, or `types` packages and do not repeat package names in exported identifiers.
- Define interfaces for real consumer substitution/test boundaries, preferably at the consumer and with minimum methods. Do not pre-create an interface for every implementation or pass pointers to interface values.
- Exported APIs, serialization, and cross-package state must define nil/empty, ownership, and concurrency semantics. `nil` and empty slices may be equivalent internally, but JSON, database, and external contracts must choose through tests.
- Write accurate `go doc` comments for exported identifiers and non-obvious constraints. Explain contract, concurrency, resources, and reasons—not implementation narration.

## Errors and Resources

- Return `error` for ordinary failure; callers handle, return, or stop at a genuinely unrecoverable entrypoint. Library APIs do not use `panic` for expected failure. Any panic for initialization failure or broken internal invariants needs a clear boundary.
- Use `%w` only when the underlying error becomes a caller-reliable API contract. Otherwise convert to a domain error without exposing implementation. Use `errors.Is`/`errors.As` for promised cause chains, never assembled message strings.
- Do not discard correctness or cleanup errors with `_`. When ignoring is safe, explain at the smallest site and support it with a contract or test.
- With `defer`, verify registration timing, loop cost, and error handling. Resource ownership must be discoverable; process exit is not cleanup.

## Concurrency and Cancellation

- Every goroutine needs an owner, exit condition, cancellation path, and wait/observation mechanism. Losing a reference does not stop it; blocked channels, background loops, and unreceived results can leak.
- Propagate request deadlines/cancellation through `context.Context`. Do not store Context as durable global state or launch ownerless work beyond request lifetime.
- Use channels to express ownership and synchronization, not unsynchronized mutable maps/slices. The sender or completion owner closes the channel.

## Tools, Tests, and Completion

- Use `gofmt` and project-selected `goimports`; the quality entrypoint covers at least `go vet`, `go test`, and `go build`, adding lint, vulnerability, or module checks as needed.
- Run matching `go test -race` after concurrency, shared-state, or goroutine-lifecycle changes. It detects only races on executed paths; disclose uncovered paths and platform limits.
- Test cause chains, cancellation, timeouts, duplicate close, goroutine exit, nil/empty contracts, and relevant contention. A green race run does not replace semantic review.

Before completion, confirm readable package responsibilities/call sites, preserved errors, observable goroutine exit, correct Context/resource lifetimes, and project-contracted format, vet, tests, race when applicable, and build.
