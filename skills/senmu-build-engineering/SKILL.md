---
name: senmu-build-engineering
description: Govern architecture, engineering contracts, implementation review, testing strategy, technical debt, or refactoring when project rules are missing or changing. Not for routine fixes, visual or interaction direction or prototype validation, or ordinary implementation under clear project rules.
---

# Software Engineering

Verify project entrypoints, code, configuration, tests, and commands. Return when project rules suffice; continue for missing, conflicting, changing, or explicitly reviewed engineering contracts.

## Route by Outcome

- Quality, defects, AI collaboration, review: [Source Quality](references/source-code-quality-and-ai-collaboration.md).
- Technology/framework/component choice: [Technology Selection](references/technology-and-component-selection.md).
- Minimum correct implementation, reuse, overengineering: [Implementation Economy](references/implementation-economy-and-overengineering.md).
- Architecture, dependencies, change budgets, debt: [Architecture](references/architecture-constraints-and-technical-debt.md).
- Frontend state, navigation, forms, responsive/browser checks: [Frontend](references/frontend-engineering-contracts-and-validation.md).
- APIs, services, data, transactions, caches, queues, jobs: [Backend](references/backend-services-and-data-contracts.md).
- Test strategy, doubles, dependencies, data, flakiness: [Testing](references/software-testing-and-quality-verification.md).
- Source modernization or stack upgrades: [Modernization](references/source-modernization-and-stack-upgrades.md).
- Derive rules from an existing codebase: [Discovery](references/project-engineering-standard-discovery.md).
- Only if local rules are absent/under review: [Python](references/python-engineering-profile.md), [TypeScript](references/typescript-engineering-profile.md), [Go](references/go-engineering-profile.md), [Java](references/java-engineering-profile.md), [Ant Design](references/frontend-ant-design-practice.md), [HTML/daisyUI](references/frontend-html-daisyui-practice.md).

Read matched references only; one profile does not imply others. Frontend/backend are references, not child skills or job roles.

## Fast Path

Engineering alone handles a reversible, contract-preserving G1 change with one owner. Add no skills, PRD, ADR, or changelog. Follow Kernel isolation, proportional verification, and local commit. Check open-batch items narrowly; consolidate after test intent. Exclude security, privacy, permissions, payments, production data, paid/destructive actions, and releases.

## Core Contract

- Preserve the symptom and call chain; search owners and existing capabilities before expanding scope or building replacements.
- Implement small changes directly. Create TD/ADR/POC only for durable public-contract, data, infrastructure, or release-boundary changes. Return behavior/acceptance changes to Product.
- Rerun the original path, then impact-based regressions. Report partial verification if the symptom was not covered. Never weaken types, tests, or security to pass.

Handoff only on real responsibility change, carrying facts, scope, evidence, unknowns, and authorization.
