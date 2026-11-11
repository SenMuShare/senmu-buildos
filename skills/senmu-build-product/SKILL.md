---
name: senmu-build-product
description: "Turn ideas or requests for a system into goals, scope, priorities, requirements, behavior and acceptance; govern versions and shared interface content. Not meaning-preserving local wording, implementation review, technical design or deployment."
---

# Product Management

Keep one chain from optional requirements and version PRDs to current product specifications and acceptance. A one-off request can change the product contract.

## Route by Outcome

- Requirements, versions, document transitions, freezing, reconciliation and linked prototypes/UI: [Product Iteration](references/product-requirements-and-iteration.md).
- Cross-page labels, user-facing state copy, error messages, terminology, generated content: [Interface Content](references/interface-copy-and-content-design.md), then only [Chinese](references/chinese-interface-copy.md) or [English](references/english-interface-copy.md). Fill gaps in existing standards.

Read the applicable [User Requirements](assets/product-governance/USER_REQUIREMENTS.template.md), [Version PRD](assets/product-governance/PRD.template.md), or [Product Specification](assets/product-governance/PRODUCT_SPECIFICATION.template.md) template when creating or materially updating it. Decide low-risk discussions directly.

## Core Contract

- The user decides goals, preferences, and authorization; questions, claims, and proposals are inputs. Distinguish facts, expectations, assumptions, and advice. Judge independently from evidence, counterexamples, alternatives, cost, and risk. Explain material disagreement; after an informed decision, act within authorization and Kernel boundaries.
- Assign work to the current version, a successor, or an optional backlog. Infer when facts suffice; ask only if placement changes scope or timing. Never infer line roles from version numbers.
- Product owns cross-page language. Store terminology, voice and platform differences with the product owner; the UI specification references it. Meaning-preserving local wording stays with implementation.
- Formal requirements use each feature's version and four Product Iteration sections unless the user replaces the format. Keep their substance even when brief; review meaning, exceptions and linked visual assets.
- Each formal development version has a PRD and technical account, possibly sections of an existing combined document. Small versions may be brief; do not create another set per edit. PRDs own approved scope/acceptance; implementation preserves them. Reconcile deviations before changing behavior. Mid-task feedback steers open scope unless replaced; retain unfinished requirements in the task owner. Backlogs are optional.
- For high investment, weak evidence, or uncertainty, compare doing nothing, reuse/buy, and the smallest solution. Avoid full discovery for cheap reversible changes.
- Infer interface needs from user tasks without requiring design vocabulary. Record activation, persistence, failure, exit, switching, draft and recovery; preserve business scope and adopted-design links in presentation changes.
- Keep requirement lifecycle, iteration commitment, implementation completion, acceptance, and release distinct.
- Give implemented requirements stable IDs linking PRD, task, code, tests, acceptance, and release evidence.

Handoff UI decisions to Design, technology to Engineering, initialization/owner conflicts to Project, release facts to Delivery and lessons to Learning. Follow the requested stage using the existing task owner.
