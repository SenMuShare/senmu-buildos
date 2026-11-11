---
name: senmu-build-design
description: "Design, improve, recreate or review web/app pages and components: new interfaces, confusing or unattractive layouts, inconsistent styles, screenshot/reference adaptation and missing UI rules. Covers visual and interaction decisions. Not routine implementation of an agreed change."
---

# Interface Design

Turn interface needs into implementable decisions, even when the user supplies only a goal or symptom. Preserve adopted behavior, brand and components while establishing one UI standard.

## Route by Outcome

- New baselines, existing UI corrections, conflicting standards, page families, layout/type/color: [Visual Systems](references/visual-systems-and-design-language.md).
- Analyze/adapt a screenshot, URL, design, or interface: [Reference Analysis](references/reference-interface-analysis-and-reconstruction.md).
- Interaction, motion, accessibility, feel: [Interaction](references/interaction-motion-and-accessibility.md).
- Alternatives, prototype adoption/engineering acceptance, visual review or task walkthrough: [Prototypes](references/prototype-exploration-and-interface-review.md).
- Only for unresolved pattern/asset choices: [Pages](references/design-library/page-structures-and-visual-directions.md) or [Components](references/design-library/component-design-patterns.md); [Index](references/design-library/INDEX.md) maps choices. These are not project facts or required pre-reads.

Read only what is needed. Implement the selected or already-authorized direction under project/Engineering rules; use specialist skills for current APIs/methods only.

For persistent UI, use `design/UI_SPECIFICATION.md` at its governed root and the [UI Specification template](assets/design-governance/UI_SPECIFICATION.template.md). Project owns initialization/migration; Design owns its decisions. One-off exploration stays with its task.

## Core Contract

- Establish interface type, task, context, hierarchy, assets, and constraints. If needed, offer distinct directions with a recommendation and risks.
- Express hierarchy, layout, components, tokens, states, assets, responsiveness, and verification. Adjectives are not specifications.
- Resolve the UI specification through project routing. Preserve valid legacy decisions during Project's standardization. Own new decisions even for a maintained single page; routine covered changes stay with implementation.
- Make frequent actions direct/predictable. Motion must explain feedback, state, space, or change, with reduced-motion/non-hover paths.
- Design accessibility, responsiveness, and loading/empty/error/disabled states from the start; never rely on one sensory cue.
- Deliver direction analysis with observed evidence, implementable decisions, and limits. To claim implemented visual/interaction quality, verify real rendering at affected viewports/states; code or static checks alone are insufficient.
- Exploration is not a product decision. Write selected rules to the owner; isolate alternatives. Preserve requirement-related user/AI prototypes and UI drafts with explicit adoption scope and Product's version/feature linkage; chat-only images are not durable handoff.

Handoff undefined or changed business behavior, shared content meaning or product acceptance to Product; retain interaction design within approved outcomes. Engineering owns implementation contracts, Assurance explicit verdicts, and Delivery release facts.
