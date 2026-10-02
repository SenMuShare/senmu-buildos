---
name: senmu-build-engineering
description: "Investigate system behavior and rationale; design/review architecture, contracts, tests, documentation and upgrades. Excludes covered local work, visual design and release authority."
---

# Software Engineering

Follow project rules; load guidance for gaps, conflicts or review, not covered local work.

## Routes

Choose [Methods](references/source-code-quality-and-ai-collaboration.md#5-ai-implementation-debugging-and-review-loop): read-only understanding, fault debugging, design change or behavior-preserving refactoring. Evidence/counterexamples: [Review](references/conditioned-code-review.md).

Design: [Components](references/technology-and-component-selection.md), [Economy](references/implementation-economy-and-overengineering.md) or [Architecture](references/architecture-constraints-and-technical-debt.md). Verification: [Testing](references/software-testing-and-quality-verification.md); migrations: [Upgrades](references/source-modernization-and-stack-upgrades.md); [Project rules](references/project-engineering-standard-discovery.md) for local standards.

Shared boundaries: [Contracts](references/api-and-boundary-contract-governance.md).

Browser/state: [Frontend](references/frontend-engineering-contracts-and-validation.md). APIs/data/jobs: [Backend](references/backend-services-and-data-contracts.md). Public services, untrusted input or paid jobs: [Security](references/application-security-and-abuse.md). Frameworks: [Ant Design](references/frontend-ant-design-practice.md), [HTML/daisyUI](references/frontend-html-daisyui-practice.md).

Missing/reviewed stack rules:
[Python](references/python-engineering-profile.md), [TypeScript](references/typescript-engineering-profile.md), [Go](references/go-engineering-profile.md), [Java](references/java-engineering-profile.md), [Rust](references/stack-profiles/rust-engineering-profile.md), [JavaScript/Node](references/stack-profiles/javascript-node-engineering-profile.md), [C/C++](references/stack-profiles/c-cpp-engineering-profile.md), [Kotlin](references/stack-profiles/kotlin-engineering-profile.md), [Swift](references/stack-profiles/swift-engineering-profile.md), [PHP](references/stack-profiles/php-engineering-profile.md), [Dependencies/CI](references/stack-profiles/dependency-and-ci-review.md), [Schemas](references/stack-profiles/schema-and-migration-review.md).

Unclear stack: [Selection](references/stack-and-file-role-guidance.md). Unlisted stacks use project rules and official guidance; profiles never restrict language choice.

Docs: [Writing](references/technical-documentation-writing.md).

Frontend/backend references are not job roles or child skills.

## Execution contract

- Preserve approved behavior, original symptoms and ownership. Reuse supported capabilities; check consumers before retiring wiring. Product owns behavior and acceptance changes.
- Design caller usage before public contract, state or data changes. Formal versions retain a technical account; ADRs/POCs serve real decisions, not ceremony.
- Reversible G1 work follows Economy, Kernel isolation and authorized commits. Security, privacy, permissions, payments, production data, paid/destructive actions and release integrity never take that shortcut.
- Check original failures and affected regressions during work; consolidate required checks at closeout. Reuse valid evidence, test real gaps and stop with sufficient evidence and no blockers. Never weaken types, tests or security to pass.

Handoffs retain scope, evidence, authority and unfinished/unknown work.
