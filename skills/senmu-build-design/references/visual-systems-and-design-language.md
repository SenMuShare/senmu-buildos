# Interface Visuals and Design Systems

Turn user goals, aesthetic intent, and product facts into implementable interface direction. This standard owns visual hierarchy, layout, typography, color, material, component presentation, asset strategy, and responsive design. It does not decide product features or maintain component-library APIs.

## 1. Authority and Evidence

Apply: approved behavior/content > existing project design system, brand assets, and page conventions > target platform/component ecosystem > this method. Reuse a sound owner; govern it only when missing, conflicting, duplicated, or durably changing.

Acquire only facts that change design:

- surface type: marketing, application, admin, mobile, desktop, embedded, or mixed;
- primary users, task, action, and operating context;
- current navigation, hierarchy, states, and real data density;
- logo, typography, colors, icons, photography, video, screenshots, and brand constraints;
- installed components, design tokens, responsive conventions, and devices.

Do not demand professional vocabulary after “premium,” “bold,” or “technical.” Restate the business/context accurately, then offer two or three understandable directions that materially differ in composition and asset strategy, each with feel, fit, assets, risk, and a recommendation. If direction is sufficient, specify it directly.

For established products without formal design documents, reconstruct the baseline from real interfaces, styles/themes, tokens, components, brand assets, and stable patterns. Label observations, inferences, conflicts, and unknowns. Write a minimum design owner only with authorization and durable cross-page need; keep local decisions in their task and implementation.

## 2. Convert Aesthetics into Specification

- **Hierarchy:** first-screen/primary-task priority, secondary retreat, primary versus risky actions.
- **Composition:** container, grid, alignment, whitespace, density, grouping, focus, scroll rhythm.
- **Typography:** family roles, scale, weight, line height, tracking, measure, multilingual behavior.
- **Color/material:** brand and semantic color, backgrounds, surfaces, borders, shadows, transparency, themes.
- **Components:** visual relationships among navigation, buttons, forms, lists, tables, cards, overlays, feedback.
- **Data visualization:** define trend, comparison, distribution, composition, or relationship before choosing a chart; make labels, legends, units, and non-color expression intelligible. Engineering owns library APIs.
- **Assets:** choose real product, photography, illustration, video, 3D, or data; give substitutes for missing assets.
- **Responsive:** define priority, reflow, collapse, density, and input changes; never merely scale down desktop.

Brand/marketing surfaces often need one strong visual, narrative rhythm, and a clear conversion action. Tools/admin surfaces prioritize task efficiency, density, distinguishable states, and stable placement. They may share a brand without sharing composition.

## 3. Design-System Boundary

Create or modify a system only for shared rules across pages or durable components. Prefer existing tokens, themes, components, and documentation; do not default to `design-system/MASTER.md`, page-overlay directories, or a new style database.

A minimum system stores only decisions that reduce real disagreement:

1. foundational tokens: color, type, space, radius, border, shadow, elevation, motion semantics;
2. semantic roles: primary/secondary action, success/warning/error, surfaces, text hierarchy;
3. component states: default, hover, press, focus, selected, disabled, loading, empty, error;
4. responsive/theme rules tied to real breakpoints or container conditions;
5. allowed local exceptions with owner, rationale, and exit condition.

Tokens represent roles; do not scatter context-free values through components. Do not add tokens merely for uniformity when composition from existing tokens suffices. Do not mix incompatible style mechanisms casually; state user benefit and consistency cost when breaking convention.

## 4. Implementation Handoff

- Local design: current state, target, concrete changes, verification.
- New/redesigned page: recommended direction, hierarchy/layout, components, tokens, assets, responsive behavior, key states, prohibited outcomes.
- Cross-page system: update the existing design owner and state migration scope, compatibility, and verification entrypoint.
- Another implementer: provide a self-contained specification without copying conversations, external libraries, or hidden intent.

Derive the stack from project facts. Do not prescribe React, Tailwind, a component library, or animation library for visual preference. State the actual capability gap and let Engineering judge compatibility and maintenance.

## 5. Completion

Confirm first-glance hierarchy; discoverable primary task/action; content, brand, and visual consistency; fit for real data and extreme text; viable desktop/mobile behavior; distinguishable loading/empty/error/disabled/danger states; obtainable assets; implementable specification; and no parallel owner.
