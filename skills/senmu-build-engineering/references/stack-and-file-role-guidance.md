# Stack and File-Role Guidance

Use a profile for a missing/conflicting local rule, an explicit standards review, or a new stack baseline. A supported profile supplies implementation and review decisions, not a compiler, permission to change language, or proof of safe code. Existing project rules and the selected toolchain prevail.

## Select the relevant boundary

| Subject | Conditional owner |
| --- | --- |
| Python | [Python](python-engineering-profile.md) |
| TypeScript | [TypeScript](typescript-engineering-profile.md) |
| Go | [Go](go-engineering-profile.md) |
| Java | [Java](java-engineering-profile.md) |
| Rust | [Rust](stack-profiles/rust-engineering-profile.md) |
| JavaScript or Node runtime | [JavaScript/Node](stack-profiles/javascript-node-engineering-profile.md) |
| C or C++ | [Native memory and ABI](stack-profiles/c-cpp-engineering-profile.md) |
| Kotlin | [Kotlin](stack-profiles/kotlin-engineering-profile.md) |
| Swift | [Swift](stack-profiles/swift-engineering-profile.md) |
| PHP | [PHP](stack-profiles/php-engineering-profile.md) |
| Dependencies, build manifests, shell, CI | [Build and supply chain](stack-profiles/dependency-and-ci-review.md) |
| SQL, Protobuf, GraphQL, Prisma | [Schema changes](stack-profiles/schema-and-migration-review.md) |
| Untrusted users, files, URLs or paid jobs | [Application security](application-security-and-abuse.md) |

Ant Design and HTML/daisyUI keep their existing conditional frontend owners. A browser-only JavaScript edit does not require Node deployment checks. A `.h` file needs its actual C/C++ consumer; `.m` is ambiguous and must not be guessed. For an unlisted stack, use project evidence and current official guidance, then promote only a recurring decision gap. Configuration and schema coverage are not counted as programming languages.

## Bounded selection helper

[resolve_engineering_guidance.py](../scripts/resolve_engineering_guidance.py) accepts explicit paths and optional runtime/risk signals; it does not crawl the repository, read its source, install tools or execute commands. It returns applicable reference routes, reasons and content digests, grouped without duplicate bodies. It is optional when the owner is already known.

From the BuildOS product root (the directory containing this package's `skills/`), run:

```sh
python3 skills/senmu-build-engineering/scripts/resolve_engineering_guidance.py --path src/task.rs --path Cargo.toml --risk paid-api
```

These are declared task paths, not files the command opens. From another directory, use the selected installation's absolute script path; no universal `$SELECTOR` variable is assumed.

The returned identity describes only these selected BuildOS references and declared signals. It is not the complete project's effective rule/context identity and must not be substituted blindly for the review executor's rules identity. Project instructions, framework constraints and actual risk still need their current owner. A filename match is a selection hint, not a semantic risk verdict.

Before reporting a language issue, establish a reachable failure and inspect its relevant counterexample. Apply the project's existing compiler, formatter, lint, tests and runtime checks; do not duplicate their diagnostics as new semantic findings. Check tool versions before using optional commands. No profile imposes an all-warnings, all-features or whole-repository migration policy.


The CLI defaults to a bounded summary; repeat the same arguments with `--format full` for every path-to-reference mapping. Counts and the identity always describe the full declared selection. Library `select()` retains full results. Declare a notebook's confirmed language per path, e.g. `--path analysis.ipynb --notebook-language analysis.ipynb=python`; the extension alone is not Python evidence. Unlisted kernels remain partial. For an established deployment role use `--file-role k8s/deployment.yaml=kubernetes` with the matching `--path`; `compose` and `terraform` are also supported. Common Compose overlays and Terraform JSON names route without treating all YAML as infrastructure. These are selection signals, not source inspection or security verdicts.
