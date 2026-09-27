# Kotlin Engineering Profile

Confirm platform (JVM, Android, Native or multiplatform), Kotlin/toolchain versions and framework lifecycle before applying a rule. Keep existing Java interoperability and build ownership.

Use nullable types to express real absence; validate platform types from Java and external deserialization. Do not spread `!!` through ordinary input paths, but do not report a proven invariant as a reachable null failure. Data-class `copy` is shallow: mutable children still share identity. Read-only collection interfaces do not by themselves guarantee immutable backing data.

Keep coroutine scope and job ownership tied to the actual request, screen or service lifecycle. Propagate cancellation; broad catches must not swallow `CancellationException`. Move blocking work to an appropriate supported boundary, without assuming `suspend` makes synchronous I/O nonblocking. Detached/global tasks need a real lifetime and shutdown owner. Review concurrent read-modify-write as a whole invariant.

Prefer sealed/domain types when they close invalid states, and preserve unknown values at open protocol boundaries. Avoid reflection or dependency-injection ceremony without framework or substitution pressure. At Java interop, check overloads, nullability, exception and asynchronous callback contracts.

Use existing Gradle compilation, lint and tests for the actual source sets. Exercise cancellation, parent/child failure and lifecycle changes where relevant; coroutine test scheduling alone does not prove production thread behavior. Android UI and persistence checks remain platform-specific.

Calibration: [Kotlin coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html), [cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html).
