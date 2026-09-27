# JavaScript and Node Runtime Profile

Select browser or Node runtime first from the actual application, package manifest and build target. TypeScript shares these runtime obligations but keeps its type rules in its existing profile. Do not assume a `.js` file is a server or a TypeScript type validates JSON.

## Values, modules and async effects

Validate external JSON, messages and environment values before domain use. Distinguish absent, null, false, zero and empty values according to the API, rather than masking them with truthiness defaults. Avoid coercive equality at trust boundaries. Use maps or own-property checks for untrusted keys; never merge arbitrary properties into privileged configuration or object prototypes.

Preserve the project's ESM/CommonJS contract, package exports and supported runtime; do not add a second transpilation/module strategy to fix one import. Do not perform network or persistent writes at import time. Handle rejection at the real job/request boundary, preserve causes and ensure the response reflects the final outcome.

Use bounded concurrency and backpressure for streams and batches. `Promise.all` does not cancel already-started side effects when one promise rejects. Cancellation needs both propagation and rejection of stale results; do not assume abort undoes a completed write.

## Node service boundaries

Keep expensive synchronous operations, unbounded JSON/regex processing and CPU-heavy transforms off shared request event-loop paths. An offline bounded CLI may reasonably use synchronous operations. Worker threads or a queue must have bounded admission and lifetime, not merely move an unlimited workload elsewhere.

Prefer argument-based process APIs over shell interpolation. Validate URLs and redirects before server fetches, and keep time, byte and connection limits. Request security, per-tenant quotas and output escaping use the project's framework owners rather than bespoke middleware at every endpoint.

## Checks and counterexamples

Use the established formatter/linter and test runner; exercise invalid input, rejection, cancellation, stream cleanup and size limits at relevant boundaries. Do not report an unbounded computation without establishing controllable scale or a shared hot path. Test runtime/package compatibility with the actual installed version. No repository-wide conversion to TypeScript is implied.

Calibration: [Node event-loop and worker-pool guidance](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop), [Node security](https://nodejs.org/en/learn/getting-started/security-best-practices).
