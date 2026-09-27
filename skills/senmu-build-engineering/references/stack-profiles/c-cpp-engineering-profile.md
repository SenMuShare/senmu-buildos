# C and C++ Memory and ABI Profile

Confirm C versus C++, compiler, language standard, platform ABI and build definitions. A header's extension does not establish its consumer language. Do not apply C++ idioms as requirements for C or change a stable build system for a local fix.

## Lifetime and boundaries

In C++, prefer RAII owners and standard containers; use non-owning views only while their owners remain valid. In C, make allocation and release ownership explicit across every success/failure exit. Check double release, dangling references, use-after-free, iterator invalidation and incomplete initialization. A raw pointer can validly be non-owning; its presence alone is not a defect.

Check bounds and integer size/conversion before allocation, indexing or copying. Validate length arithmetic without overflow; a null check does not establish buffer capacity. Treat object lifetime, aliasing, alignment and signed overflow according to the actual language/compiler contract. Do not use undefined behavior as an optimization.

At ABI/FFI boundaries, specify representation, ownership transfer, allocator pairing, calling convention, version compatibility and error propagation. Exceptions must not escape into a consumer that cannot handle them. Preserve destructor and cleanup failures without hiding the original error.

## Concurrency and verification

Reason about the complete shared invariant, synchronization and memory ordering, not just individual atomic variables. Keep unsafe lifetime assumptions out of callbacks and detached threads. Prefer supported platform synchronization over hand-built lock-free algorithms without a demonstrated need and proof strategy.

Use the existing build/test entrypoint and warnings baseline. Where the relevant target supports them, use address/undefined-behavior/thread sanitizers or static analysis for affected risks; these tools do not prove absence of all defects. Preserve testable public boundaries instead of adding accessors solely for private assertions. Check real ABI/platform variants when their contract changed.

Calibration: [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines). Compiler- and C-specific behavior must be checked against the selected compiler/language documentation, not inferred from C++ rules.
