# Interface Visuals and Design Systems

Turn user goals, aesthetic intent, and product facts into implementable interface direction. This standard owns visual hierarchy, layout, typography, color, material, component presentation, asset strategy, and responsive design. It does not decide product features or maintain component-library APIs.

Read §1 for scope/authority, §2 for visual diagnosis, §3 for a shared baseline or remediation, and §4–5 for implementation and completion. A local correction does not require the cross-page procedure.

## 1. Authority and Evidence

Apply: approved behavior/content > adopted project design rules, brand assets, and page conventions > target platform/component ecosystem > this method. Preserve valid decisions when establishing or correcting the standard.

Persistent UI uses `design/UI_SPECIFICATION.md`, including a maintained single page. Locate it through the project's instructions/map, then inspect the affected theme, components and real interface. Its filename establishes the standard location, not approval or accuracy. Project owns initialization and legacy-document migration; use the Design template when establishing the specification. Choose scope before designing:

| Scope | Action |
| --- | --- |
| Named element with an agreed change | Implement directly; verify the affected relationship. Do not open directions or inventory the whole product. |
| New product or explicitly authorized redesign | Form a baseline from its tasks, content and constraints; validate a representative composition before extending it. |
| Existing product gains a page or flow | Inherit its visual language; design only missing relationships/states. A new route is not a new brand. |
| Existing UI refinement or system repair | Record the baseline, retain approved behavior/brand, and distinguish defects from legitimate variants before changing shared rules. |

Acquire only decision-changing facts: surface and users, primary task/action, navigation and states, real content/density, brand/assets, installed components/tokens, devices and input constraints. Keep unknowns explicit.

Do not demand professional vocabulary after “premium,” “bold,” or “technical.” Translate the request using §2. Recommend a suitable direction; compare alternatives only when the unresolved decision or user request warrants them. Continue an already-authorized direction without another approval ceremony.

For established products, reconstruct missing decisions from real interfaces, styles/themes, tokens, components, brand assets and stable patterns. Label observations, inferences, conflicts and unknowns. Authorized UI governance consolidates valid rules into the standard specification and retires superseded current instructions through Project's migration procedure. Routine covered edits may follow valid legacy rules during that transition, but do not declare standardization complete. Keep one-off exploration and incidental local choices in their task/implementation.

When documents or implementation disagree, compare authority, approved revision, scope and actual consumers. Classify differences as defects, intentional variants or unfinished migration. A compact editor, touch layout and marketing surface may differ legitimately. Majority usage and file timestamps do not decide authority. Reconcile decidable conflicts within scope, update the specification and superseded pointers, and track unresolved work in the existing task. Ask only for material product/brand choices that cannot be established. Preserve functioning exceptions rather than forcing identical screenshots.

## 2. Convert Aesthetics into Specification

Diagnose the visible relationship before choosing decoration. For an unclear request, name what the user sees, how it impairs the task or intended character, what changes, and what observation would establish improvement. For example:

| Feedback | Concrete decision |
| --- | --- |
| “Too crowded” | Separate groups, shorten redundant content or change density/reflow; keep decision data and actions readable. |
| “Too flat” or “no focus” | Establish the current object and main action, then adjust relative weight, placement and surface hierarchy. |
| “More refined/bold” | Choose type contrast, alignment, spacing, color roles and asset treatment from audience/brand evidence; do not apply a universal palette or small-text style. |
| “Generic” | Strengthen the product's actual objects, results or interaction; do not manufacture features or novelty for its own sake. |

Keep one short design intent that explains these choices. Preserve useful qualities during refinement; a reviewer's new preference is not a reason to restart the direction. Express the resulting specification through:

- **Hierarchy:** first-screen/primary-task priority, secondary retreat, primary versus risky actions.
- **Composition:** container, grid, alignment, whitespace, density, grouping, focus, scroll rhythm.
- **Typography:** family roles, scale, weight, line height, tracking, measure, multilingual behavior.
- **Color/material:** brand and semantic color, backgrounds, surfaces, borders, shadows, transparency, themes.
- **Components:** visual relationships among navigation, buttons, forms, lists, tables, cards, overlays, feedback.
- **Data visualization:** define trend, comparison, distribution, composition, or relationship before choosing a chart; make labels, legends, units, and non-color expression intelligible. Engineering owns library APIs.
- **Assets:** choose real product, photography, illustration, video, 3D, or data; give substitutes for missing assets.
- **Responsive:** define priority, reflow, collapse, density, and input changes; never merely scale down desktop.

Check text using the actual product language and fonts: long names/headings, mixed scripts, numbers with units, fallback fonts, wrapping, clipping and enlarged reading. Fix grouping, line height and content-driven containers before shrinking text. Do not impose one language or font-size range across products. Product's [Interface Copy](../../senmu-build-product/references/interface-copy-and-content-design.md) owns meaning, terminology and state truth; design does not rewrite approved copy to fit a picture.

Use coherent, realistic content to expose layout problems; keep synthetic content distinguishable in the handoff and never present invented business metrics, testimonials or success as evidence. Keep implementation notes out of product UI unless users need them to make an actual decision. For unresolved image/rendering choices, use the conditional [Page and Asset Patterns](design-library/page-structures-and-visual-directions.md#asset-and-rendering-choices).

Brand/marketing surfaces often need one strong visual, narrative rhythm, and a clear conversion action. Tools/admin surfaces prioritize task efficiency, density, distinguishable states, and stable placement. They may share a brand without sharing composition.

## 3. Design-System Boundary

The standard specification may be brief; a full system needs shared rules or durable components. Reuse actual tokens, themes and components. Do not add a competing `design-system/MASTER.md`, page-overlay directory or style database. External design tools remain revision-linked sources; the standard entry records their scope and update responsibility without an editable duplicate.

For cross-page work, keep or reference a small page/component map in the UI specification: family/task, real route/source, shared composition/components and distinctive states/viewports. Group by task and structure, not only URL. Select a live page, component example or Storybook as the representative of each affected family and validate before extending through consumers. Mark planned representatives as unimplemented; a static specimen is not evidence of working components.

A minimum system stores only decisions that reduce real disagreement:

1. foundational tokens: color, type, space, radius, border, shadow, elevation, motion semantics;
2. semantic roles: primary/secondary action, success/warning/error, surfaces, text hierarchy;
3. component states: default, hover, press, focus, selected, disabled, loading, empty, error;
4. responsive/theme rules tied to real breakpoints or container conditions;
5. allowed local exceptions with owner, rationale, and exit condition.

Tokens represent roles. Keep actual values in their implementation source; the specification explains semantics and links that source, not a second hand-maintained value table. Compose existing tokens before adding new ones. Do not scatter context-free values or mix incompatible style mechanisms without user benefit and consistency cost.

Keep inter-region spacing with the parent layout and internal spacing with the component; avoid stacking margins/padding or duplicate dividers for the same relationship. Apply one control grammar across related states, with stable hit areas and recognizable icon/label roles. Preserve semantic accessibility when styling a library component.

Correct repeated drift at the shared token, component or composition that owns it. Check affected consumers, including a legitimate different context, before applying a global replacement. A one-off composition may remain local. Record accepted differences with the exception rule above; record unfinished migration scope and its completion condition in the existing task/owner. Do not claim system-wide consistency while only a representative has been changed.

## 4. Implementation Handoff

- Local design: current state, target, concrete changes, verification.
- New/redesigned page: recommended direction, hierarchy/layout, components, tokens, assets, responsive behavior, key states, prohibited outcomes. When structure is uncertain, use a lightweight grayscale composition and meaningful state transition before expensive assets/detail; skip it when the approved structure is already clear.
- Cross-page system: hand over the §3 owner/map, actual theme/token entrypoint, representative composition, migration scope and verification. Engineering owns implementation; token compliance alone does not establish rendered quality.
- Another implementer: provide a self-contained specification without copying conversations, external libraries, or hidden intent.

For a selected prototype or image, read [Implementation Adoption](prototype-exploration-and-interface-review.md#implementation-adoption) before handing it to Engineering. Keep durable UI decisions in the standard specification, with the adopted revision and scope.

Derive the stack from project facts. Do not prescribe React, Tailwind, a component library, or animation library for visual preference. State the actual capability gap and let Engineering judge compatibility and maintenance.

## 5. Completion

Confirm first-glance hierarchy; discoverable primary task/action; content, brand, and visual consistency; fit for real data and extreme text; viable desktop/mobile behavior; distinguishable loading/empty/error/disabled/danger states; obtainable assets; implementable specification; and no parallel owner.
