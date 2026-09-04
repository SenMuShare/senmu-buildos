---
name: senmu-build-product
description: Define durable product scope, version placement, priority, acceptance, state, and cross-page interface content. Not for one-off edits, implementation review, technical design, or deployment.
---

# Product Management

Maintain one truth chain across optional requirements, version PRDs, current product specifications, and acceptance. Continue only for durable contract, version-placement, or cross-page content changes.

## Route by Outcome

- Requirements, versions, document transitions, freezing, reconciliation: [Product Iteration](references/需求与产品迭代管理规范.md).
- Cross-page buttons, states, errors, terms, generated content: [Interface Content](references/界面文案与内容设计规范.md), then only [Chinese](references/界面文案中文规范.md) or [English](references/界面文案英文规范.md). Fill gaps in existing standards.

Read a [User Requirements](assets/product-governance/USER_REQUIREMENTS.template.md), [Version PRD](assets/product-governance/PRD.template.md), or [Product Specification](assets/product-governance/PRODUCT_SPECIFICATION.template.md) template only when creating it. Decide low-risk discussions directly.

## Core Contract

- The user decides goals, preferences, and authorization; questions, claims, and proposals are inputs. Distinguish facts, expectations, assumptions, and advice. Judge independently from evidence, counterexamples, alternatives, cost, and risk. Explain material disagreement; after an informed decision, act within authorization and Kernel boundaries.
- Assign work to the current version, a successor, or an optional backlog. Infer when facts suffice; ask only if placement changes scope or timing. Never infer line roles from version numbers.
- Product owns cross-page language. Store terminology, voice, and platform differences in an existing product/design owner. One-off wording that preserves meaning stays with implementation.
- Templates structure chosen artifacts only; remove inapplicable optional sections and avoid empty ledgers.
- Backlogs are optional. Version PRDs define development/acceptance; product specifications store current facts. Keep status with requirements.
- For high investment, weak evidence, or uncertainty, compare doing nothing, reuse/buy, and the smallest solution. Avoid full discovery for cheap reversible changes.
- Record activation, persistence, failure, exit, switching, draft, and recovery only when acceptance changes. Presentation-only changes do not alter the PRD.
- Keep requirement lifecycle, iteration commitment, implementation completion, acceptance, and release distinct.
- Give implemented requirements stable IDs linking PRD, task, code, tests, acceptance, and release evidence.

Handoff design to Design, technology to Engineering, release facts to Delivery, authority conflicts to Project, and reusable lessons to Learning. Use the existing task owner across stages.
