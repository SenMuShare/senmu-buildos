# Reference Interface Analysis and Reconstruction

Use this standard to turn a screenshot, URL, design file, or existing interface into an implementable specification. It supports faithful reconstruction or adaptation of a design language without importing the reference's product behavior, data, brand facts, or stack.

## 1. Choose the Outcome

- **Reconstruction:** match observable structure, proportions, visual relationships, responsive behavior, and key states. Mark unknown behavior; never invent it from a screenshot.
- **Design translation:** preserve hierarchy, rhythm, material, or interaction language while adapting content, brand, components, and user tasks.
- **Pattern extraction:** retain only reusable page structures, component patterns, or visual relationships rather than treating the whole page as a template.

Target product specifications, design owners, real content, and component ecosystem take precedence. References provide design evidence and candidates, not project facts.

## 2. Layered Analysis

Acquire the minimum surface that changes the decision: target viewport, first screen and long page, before/after interaction states, mobile differences, and necessary assets. Keep unobservable behavior unknown.

Separate observation from intended implementation across:

1. information and reading order: primary task/action, narrative order, density, scroll rhythm;
2. spatial structure: containers, grids, alignment, whitespace, proportions, sections, overlap, viewport relations;
3. visual language: type roles, color hierarchy, surfaces, borders, shadows, radius, images, icons;
4. components/states: navigation, cards, forms, lists, overlays, selection, feedback, visible state differences;
5. responsive/input: reflow, collapse, density, touch/pointer differences, content priority;
6. motion: purpose, trigger, rhythm, entry/exit, scrolling, focus, state changes, reduced-motion path.

With only a static screenshot, treat motion, hover, keyboard, and error states as unknown. An accessible URL does not establish every authentication, device, or data state.

## 3. Implementation Specification

Include what the task needs from:

- hierarchy, region order, layout constraints, and key dimensional relationships;
- semantic roles for typography, color, space, radius, borders, shadows, and motion;
- component composition, content rules, and applicable states;
- desktop, mobile, and intermediate-width priority/reflow;
- reusable, newly required, and substitute assets;
- observations, inferences, conflicts, unknowns, and items requiring user/runtime confirmation;
- target viewports, key states, and observable comparison criteria.

Product decides changes to function, content, permission, and business state. Project/Engineering or specialist skills own React, Ant Design, shadcn, GSAP, and other implementation APIs. Design specifies results rather than maintaining framework APIs.

## 4. Conditional Design Library

Read [Design Library Index](design-library/INDEX.md) only when the reference is incomplete, the user requests exploration, or observations must become a reusable pattern. Load one matching resource pack. The library supplies candidates; do not rotate themes, fill quotas, or mix conflicting languages.

## 5. Verification and Ownership

Compare the implementation at target viewports with real content and key states. Check hierarchy, proportions, wrapping, density, crop, responsiveness, and interaction feedback. Static code, one screenshot, or component presence does not establish completion.

Reference analysis does not become the design owner. Keep one-off results in the task. Write only approved, stable cross-page rules into the existing design system, tokens, component standard, or registered owner. Create a minimum design baseline only when no owner exists and durable need is confirmed.
