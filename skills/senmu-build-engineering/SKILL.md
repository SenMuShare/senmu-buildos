---
name: senmu-build-engineering
description: "Diagnose systems and ineffective verification; design/review architecture, contracts, tests, docs and upgrades. Not routine local work, visual design or release authority."
---

# Software Engineering

Use project rules; load guidance for gaps or ineffective methods. Continue productive covered work locally.

## Routes

[Methods](references/source-code-quality-and-ai-collaboration.md#5-ai-implementation-debugging-and-review-loop): understanding, debugging, design or behavior-preserving refactoring. [Review](references/conditioned-code-review.md): evidence and counterexamples.

Design: [Components](references/technology-and-component-selection.md), [Economy](references/implementation-economy-and-overengineering.md), [Architecture](references/architecture-constraints-and-technical-debt.md). Verification: [Testing](references/software-testing-and-quality-verification.md). Migrations: [Upgrades](references/source-modernization-and-stack-upgrades.md). Local standards: [Project rules](references/project-engineering-standard-discovery.md).

Shared boundaries: [Contracts](references/api-and-boundary-contract-governance.md).

Browser/state: [Frontend](references/frontend-engineering-contracts-and-validation.md). APIs/data/jobs: [Backend](references/backend-services-and-data-contracts.md). Public services, untrusted input or paid jobs: [Security](references/application-security-and-abuse.md). Frameworks: [Ant Design](references/frontend-ant-design-practice.md), [HTML/daisyUI](references/frontend-html-daisyui-practice.md).

Missing/reviewed stack rules:
[Python](references/python-engineering-profile.md), [TypeScript](references/typescript-engineering-profile.md), [Go](references/go-engineering-profile.md), [Java](references/java-engineering-profile.md), [Rust](references/stack-profiles/rust-engineering-profile.md), [JavaScript/Node](references/stack-profiles/javascript-node-engineering-profile.md), [C/C++](references/stack-profiles/c-cpp-engineering-profile.md), [Kotlin](references/stack-profiles/kotlin-engineering-profile.md), [Swift](references/stack-profiles/swift-engineering-profile.md), [PHP](references/stack-profiles/php-engineering-profile.md), [Dependencies/CI](references/stack-profiles/dependency-and-ci-review.md), [Schemas](references/stack-profiles/schema-and-migration-review.md).

Unclear stack: [Selection](references/stack-and-file-role-guidance.md). Unlisted stacks use project rules and official guidance; profiles never restrict language choice.

Docs: [Writing](references/technical-documentation-writing.md). Frontend/backend references are not job roles or child skills.

Optional [selector](scripts/resolve_engineering_guidance.py): `--concern` routes known/unlisted gaps, not monitoring or authority.

## Execution contract

- Preserve approved behavior, symptoms and owners. Reuse capabilities; check consumers before retiring wiring. Product owns behavior and acceptance changes.
- Design caller usage before contract/state/data changes. Formal versions retain technical rationale; ADRs/POCs serve real decisions.
- Reversible G1 work follows Economy, Kernel isolation and authorized commits. Security, privacy, permissions, payments, production data, paid/destructive actions and release integrity never take that shortcut.
- Check original failures and affected regressions. At closeout consolidate required checks, reuse valid evidence and test real gaps. Stop when sufficient and unblocked; never weaken types, tests or security.

Handoffs retain scope, evidence, authority and gaps.
