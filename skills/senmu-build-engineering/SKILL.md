---
name: senmu-build-engineering
description: "Choose/review architecture, component stacks and contracts; diagnose systems and ineffective verification; govern comments, docs and upgrades. Not routine edits, visual design or release authority."
---

# Software Engineering

Use project rules; load guidance for gaps/reviews. Missing UI decisions use Design; governance gaps use Project. Covered edits stay local.

## Routes

[Methods](references/source-code-quality-and-ai-collaboration.md#5-ai-implementation-debugging-and-review-loop): understanding, debugging, design or behavior-preserving refactoring. [Review](references/conditioned-code-review.md): evidence. [Comments](references/source-code-quality-and-ai-collaboration.md#4-comments-tools-and-tests).

Technical design: [Components](references/technology-and-component-selection.md), [Economy](references/implementation-economy-and-overengineering.md), [Architecture](references/architecture-constraints-and-technical-debt.md). [Testing](references/software-testing-and-quality-verification.md). [Upgrades](references/source-modernization-and-stack-upgrades.md). [Project rules](references/project-engineering-standard-discovery.md).

[Shared contracts](references/api-and-boundary-contract-governance.md).

UI basis/browser/state: [Frontend](references/frontend-engineering-contracts-and-validation.md). APIs/data/jobs: [Backend](references/backend-services-and-data-contracts.md). Public services, untrusted input or paid jobs: [Security](references/application-security-and-abuse.md). Frameworks: [Ant Design](references/frontend-ant-design-practice.md), [HTML/daisyUI](references/frontend-html-daisyui-practice.md).

Stack gaps/reviews:
[Python](references/python-engineering-profile.md), [TypeScript](references/typescript-engineering-profile.md), [Go](references/go-engineering-profile.md), [Java](references/java-engineering-profile.md), [Rust](references/stack-profiles/rust-engineering-profile.md), [JavaScript/Node](references/stack-profiles/javascript-node-engineering-profile.md), [C/C++](references/stack-profiles/c-cpp-engineering-profile.md), [Kotlin](references/stack-profiles/kotlin-engineering-profile.md), [Swift](references/stack-profiles/swift-engineering-profile.md), [PHP](references/stack-profiles/php-engineering-profile.md), [Dependencies/CI](references/stack-profiles/dependency-and-ci-review.md), [Schemas](references/stack-profiles/schema-and-migration-review.md).

[Selection](references/stack-and-file-role-guidance.md) routes gaps. Unlisted stacks follow project/official rules; profiles do not restrict languages.

Docs: [Writing](references/technical-documentation-writing.md). References are not roles or child skills.

Optional [selector](scripts/resolve_engineering_guidance.py): `--concern` routes gaps, not authority or monitoring.

## Execution contract

- Preserve approved behavior, symptoms and owners. Reuse capabilities; check consumers before retirement. Product owns business behavior and acceptance changes.
- Design caller usage before contract/state/data changes. Keep formal-version rationale; use ADRs/POCs for actual decisions.
- Reversible G1 work follows Economy, Kernel isolation and authorized commits. Security, privacy, permissions, payments, production data, paid/destructive actions and release integrity retain full protections.
- Check original failures and affected regressions. Reuse valid evidence, test real gaps and consolidate closeout checks. Stop when sufficient/unblocked; never weaken types, tests or security.

Handoffs retain scope, evidence, authority and gaps.
