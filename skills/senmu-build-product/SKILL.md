---
name: senmu-build-product
description: "Defines product goals, scope, priorities, versions, behavior, acceptance and shared interface content. Excludes meaning-preserving local wording, implementation review, technical design and deployment."
---

# Product Management

Maintain one truth chain across optional requirements, version PRDs, current product specifications, and acceptance. Use for product decisions, behavior/acceptance changes, version placement or shared content; a one-off request can still change a product contract.

## Route by Outcome

- Requirements, versions, document transitions, freezing, reconciliation and linked prototypes/UI: [Product Iteration](references/product-requirements-and-iteration.md).
- Cross-page labels, user-facing state copy, error messages, terminology, generated content: [Interface Content](references/interface-copy-and-content-design.md), then only [Chinese](references/chinese-interface-copy.md) or [English](references/english-interface-copy.md). Fill gaps in existing standards.

Read the applicable [User Requirements](assets/product-governance/USER_REQUIREMENTS.template.md), [Version PRD](assets/product-governance/PRD.template.md), or [Product Specification](assets/product-governance/PRODUCT_SPECIFICATION.template.md) template when creating or materially updating it. Decide low-risk discussions directly.

## Core Contract

- The user decides goals, preferences, and authorization; questions, claims, and proposals are inputs. Distinguish facts, expectations, assumptions, and advice. Judge independently from evidence, counterexamples, alternatives, cost, and risk. Explain material disagreement; after an informed decision, act within authorization and Kernel boundaries.
- Assign work to the current version, a successor, or an optional backlog. Infer when facts suffice; ask only if placement changes scope or timing. Never infer line roles from version numbers.
- Product owns cross-page language. Store terminology, voice, and platform differences in an existing product/design owner. One-off wording that preserves meaning stays with implementation.
- Formal requirement drafts and updates use each feature's version plus four sections from Product Iteration, unless the user explicitly replaces the format. Brevity never removes required sections. Check meaning, exceptions and linked visual assets, not just headings.
- Each formal development version has a PRD and technical account, possibly sections of an existing combined document. Small versions may be brief; do not create another set per edit. PRDs own approved scope/acceptance; implementation preserves them. Reconcile deviations before changing behavior. Mid-task feedback steers open scope unless replaced; retain unfinished requirements in the task owner. Backlogs are optional.
- For high investment, weak evidence, or uncertainty, compare doing nothing, reuse/buy, and the smallest solution. Avoid full discovery for cheap reversible changes.
- Record activation, persistence, failure, exit, switching, draft, and recovery when acceptance changes. Presentation-only changes preserve business scope; maintain affected adopted-design links.
- Keep requirement lifecycle, iteration commitment, implementation completion, acceptance, and release distinct.
- Give implemented requirements stable IDs linking PRD, task, code, tests, acceptance, and release evidence.

Handoff design to Design, technology to Engineering, release facts to Delivery, authority conflicts to Project, and reusable lessons to Learning. Use the existing task owner across stages.
