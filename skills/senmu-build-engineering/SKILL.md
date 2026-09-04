---
name: senmu-build-engineering
description: Govern architecture, engineering contracts, implementation review, testing strategy, technical debt, or refactoring when project rules are missing or changing. Not for routine fixes, visual or interaction direction or prototype validation, or ordinary implementation under clear project rules.
---

# Software Engineering

Verify project entrypoints, code, configuration, tests, and commands. Return when project rules suffice; continue for missing, conflicting, changing, or explicitly reviewed engineering contracts.

## Route by Outcome

- Quality, defects, AI collaboration, review: [Source Quality](references/源代码工程质量与AI协作规范.md).
- Technology/framework/component choice: [Technology Selection](references/技术路线与组件选型.md).
- Minimum correct implementation, reuse, overengineering: [Implementation Economy](references/实现经济性与过度工程治理规范.md).
- Architecture, dependencies, change budgets, debt: [Architecture](references/架构约束与技术债治理规范.md).
- Frontend state, navigation, forms, responsive/browser checks: [Frontend](references/前端工程契约与验证规范.md).
- APIs, services, data, transactions, caches, queues, jobs: [Backend](references/后端服务与数据契约规范.md).
- Test strategy, doubles, dependencies, data, flakiness: [Testing](references/软件测试与质量验证规范.md).
- Source modernization or stack upgrades: [Modernization](references/源码级重构与技术栈升级规范.md).
- Derive rules from an existing codebase: [Discovery](references/项目工程规范发现方法.md).
- Only if local rules are absent/under review: [Python](references/Python工程编码规范.md), [TypeScript](references/TypeScript工程编码规范.md), [Go](references/Go工程编码规范.md), [Java](references/Java工程编码规范.md), [Ant Design](references/frontend-ant-design-practice.md), [HTML/daisyUI](references/frontend-html-daisyui-practice.md).

Read matched references only; one profile does not imply others. Frontend/backend are references, not child skills or job roles.

## Fast Path

Engineering alone handles a reversible, contract-preserving G1 change with one owner. Add no skills, PRD, ADR, or changelog. Follow Kernel isolation, proportional verification, and local commit. Check open-batch items narrowly; consolidate after test intent. Exclude security, privacy, permissions, payments, production data, paid/destructive actions, and releases.

## Core Contract

- Preserve the symptom and call chain; search owners and existing capabilities before expanding scope or building replacements.
- Implement small changes directly. Create TD/ADR/POC only for durable public-contract, data, infrastructure, or release-boundary changes. Return behavior/acceptance changes to Product.
- Rerun the original path, then impact-based regressions. Report partial verification if the symptom was not covered. Never weaken types, tests, or security to pass.

Handoff only on real responsibility change, carrying facts, scope, evidence, unknowns, and authorization.
