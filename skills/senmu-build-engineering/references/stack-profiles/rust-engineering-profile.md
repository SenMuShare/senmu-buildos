# Rust Engineering Profile

Apply to Rust implementation, review, Cargo workspaces and FFI boundaries. Establish edition, minimum supported Rust, feature combinations and targets from the actual crate/toolchain. Keep general architecture and testing with their existing owners.

## Ownership and failure

Prefer borrowing or ownership transfer when the contract allows it; do not scatter `clone()` or interior mutability just to suppress borrowing errors. A snapshot, independent task lifetime or measured simplification can justify a clone. An `Arc` shares ownership but does not make its payload safe for concurrent mutation. Identify cycles and use weak ownership only when one side is genuinely non-owning.

Use `Result` for recoverable failures and preserve typed causes at API boundaries. Reachable ordinary user errors must not become undocumented panics. `unwrap` in a test or after an established invariant is not automatically a defect; prove the failing input/invariant before reporting it. Distinguish optional data from an error rather than replacing both with defaults.

## Async and unsafe boundaries

Keep synchronous lock guards and blocking work out of suspension paths unless the selected runtime explicitly supports the operation. Observe owned tasks, cancellation and shutdown; dropping a handle is not proof that a task stopped. Examine partial writes and cleanup when a future is cancelled. A mutex is not a substitute for a complete atomic business operation.

Prefer safe library interfaces. Keep necessary `unsafe` blocks narrow and document the invariant: pointer validity, alignment, initialized length, aliasing, lifetime, ownership and allocator pairing. Check these at FFI boundaries, including failure cleanup. Do not infer soundness from compilation, a safety comment, or passing ordinary tests. Rust memory safety does not establish authorization or business correctness.

## Crate contracts and verification

Represent meaningful states and units with enums or newtypes when they prevent actual invalid combinations. Avoid exposing storage/locking implementation in public APIs without a consumer need. Keep macros proportional; verify multiple evaluation, generated-name collisions and cross-crate hygiene when defining macros, not on every invocation.

Use the project's Cargo entrypoints. Typical checks include `cargo fmt --check`, `cargo clippy`, and `cargo test` for the affected packages and supported targets/features; build scripts and dependencies may execute code, so use the authorized environment. Do not force `--all-features` when features are mutually exclusive. Miri, sanitizers or concurrency exploration supplement a relevant unsafe/race investigation where supported, not every small edit. Record which configurations were actually exercised.

Calibration: [Rust error handling](https://doc.rust-lang.org/book/ch09-00-error-handling.html), [unsafe contracts](https://doc.rust-lang.org/book/ch19-01-unsafe-rust.html), [Clippy](https://doc.rust-lang.org/clippy/). Review current tool behavior at adoption; retain crate-specific exceptions locally.
