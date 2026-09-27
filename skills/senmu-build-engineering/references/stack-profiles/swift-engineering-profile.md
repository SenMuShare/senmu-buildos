# Swift Engineering Profile

Establish Swift language mode, deployment targets, package/Xcode configuration and platform framework. A compiler upgrade does not automatically authorize changing deployment compatibility.

Use optionals and typed errors for ordinary absence/failure; force unwraps need an established invariant, not a guessed network response. Distinguish value copies from shared reference state. Review closure captures and ownership cycles with the actual lifetime; mechanically adding `weak` can lose required work.

Respect actor isolation and the selected concurrency mode. An actor serializes isolated access, but an `await` can allow reentrancy; revalidate state before committing a decision derived before suspension. `Sendable`/unchecked conformance needs a real transfer-safety basis. Detached tasks do not inherit every lifetime or context; cancellation must be observed and cleanup verified. Keep UI updates on the required actor without moving heavy work there merely to suppress a diagnostic.

At C/Objective-C interop, verify buffer lifetime, bridging, ownership transfer and error conversion. Unsafe pointer scopes must not escape into longer-lived asynchronous work. Keep platform, package and application responsibilities separate rather than wrapping every system API.

Run the project's Swift/Xcode build and tests for the affected target. Add relevant deallocation, actor reentrancy and cancellation cases; compiler warnings alone cannot establish business ordering or authorization. Platform-only checks left unrun remain explicit gaps.

Calibration: [Swift concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/). Consult the selected platform's current API availability and ownership contracts at implementation time.
