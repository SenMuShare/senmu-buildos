# Dependencies, Build Inputs, Shell and CI

Use for manifests, lockfiles, build definitions, scripts and workflows. Establish their role before syntax: two YAML files can govern entirely different trust boundaries. Reuse current package/build/CI tooling; do not install a new scanner for each file.

## Supply-chain decisions

Before adding a dependency, use the existing capability and selection order. Verify official package/repository identity, supported version, maintenance, license, permissions, transitive surface and installation/build scripts. Stars or a clean scanner report do not prove trust. Prefer one supported SDK inside the application's narrow adapter; do not duplicate provider retries or expose provider identifiers throughout the domain.

Keep manifest and lockfile changes consistent with the chosen package manager. Pin deployed artifacts and workflow actions to verifiable identities; document deliberate compatible ranges for reusable libraries. Do not universally demand exact versions for every library constraint, or copy secrets from real config into examples. Review Cargo build scripts/features, npm lifecycle scripts, Maven/Gradle plugins and Composer hooks as executable inputs.

## Workflow and shell boundaries

Determine trigger, code origin, token permissions, secret access and execution environment together. Missing `permissions` requires inspecting inherited policy; it is not proof of broad permissions. Untrusted PR content must not run with privileged credentials. Pass untrusted text as data through well-quoted arguments/environment rather than interpolating it into shell programs. A full action commit protects identity, not the trustworthiness of its source.

Use sufficient history for actual Git operations, not mandatory full history for every checkout. Set bounded jobs, preserve failure propagation and distinguish optional checks from skipped required evidence. Cache by relevant inputs without letting untrusted writes poison privileged jobs. Cancel obsolete build checks when safe, not a deployment already applying irreversible changes.

Shell work preserves exit codes, quoting, pipeline behavior and cleanup ownership; `set -e` alone is not an error model. Never pipe an unverified remote installer into a privileged shell. Use the selected formatter, shell analysis and workflow validation; inspect their actual coverage, permissions and execution cost. Local fixtures exercise failure and malicious-looking text without touching real credentials.

Calibration: [GitHub workflow security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions), [OpenSSF Scorecard](https://scorecard.dev/). Scanner output is evidence for its checks, not complete release approval.
