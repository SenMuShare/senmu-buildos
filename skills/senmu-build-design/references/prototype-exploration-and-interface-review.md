# Prototype Exploration and Interface Review

Use this standard when direction is uncertain, interaction risk is high, or the task needs holistic UI/UX judgment. Prototypes discover and compare design; they are not automatically product decisions, production code, or independent evidence.

Use §1–2 for exploration, §3 for isolation and implementation adoption, §4 for review, and §5 for closeout. Read only the section that changes the current decision.

## 1. When to Prototype

Prototype when alternatives materially change hierarchy or interaction; gesture, motion, or spatial relationships cannot be judged statically; a costly implementation needs task-path validation; or the user explicitly requests prototypes. Direction-only alternatives can use observed evidence and specifications without building a prototype.

Implement and verify local styling, a selected or already-authorized design, routine composition of mature components, or a cheap reversible change directly. Do not prototype merely to demonstrate process. Missing artwork does not block requirement writing and does not require generating an image.

For a review-only request, inspect and report without implementing recommendations or creating alternative designs. A design-only request may finish with the requested specification or mockup; do not imply that a working interface was delivered.

## 2. Materially Different Alternatives

Offer alternatives only when the decision warrants them; follow the requested count or use the smallest useful comparison. Differentiate information hierarchy, layout model, visual character, asset strategy, or interaction mechanism—not only color, radius, and shadow. A fixed number of internal candidates or independent agents is not a prerequisite.

Hold core content, data, task, and device conditions constant. Explain each alternative's first action, visual/interaction mechanism, context, asset/technical prerequisites, accessibility/performance/maintenance/brand risks, and recommendation.

With sparse input, use understandable direction names and make a recommendation. Do not transfer a design-vocabulary questionnaire to the user.

Compare representative screens or the uncertain state before constructing several complete products. Include the current baseline for a redesign; keep input data and asset quality comparable. Reuse an available preview, side-by-side page or image set with visible revision/state/viewport identity, and inspect legibility at actual size. Record the selected revision and useful qualities to retain; do not treat a stale candidate number or a screenshot thumbnail as approval. Continue within existing authority once the choice is settled.

## 3. Prototype Boundaries

- Use the project's prototype entrypoint, Storybook, test route, isolated example, or disposable workspace. Do not put executable candidates in production navigation, real data, or runtime release sources. Approved design evidence may be preserved in the project's authorized documentation/asset location.
- Reuse the stack, components, and fake data. Add dependencies only when the prototype question needs them and benefit exceeds install/maintenance cost.
- Static mockups test composition and visuals. Task paths, gestures, focus, responsiveness, and motion require interaction; screenshots cannot establish them.
- Record subject, version, target viewports, assumptions, and unknowns. A selected visual direction is not approval of the business requirement.
- Write selected durable visual/interaction decisions into `design/UI_SPECIFICATION.md`; product meaning stays with Product and implementation facts with code. One-off exploration stays in its task. Keep alternatives isolated and delete/archive/retain them only within authorization; do not leave permanent competing themes.

Apply Product's [requirement-linked visual asset contract](../../senmu-build-product/references/product-requirements-and-iteration.md#23-requirement-linked-visual-assets) to preserve supplied/adopted references, including AI-generated images, with exact revisions, version/feature links and adoption/exclusion scope. Use the existing owners, retain earlier baselines, and reconcile image/text conflicts. A clear selection needs no repeated archive instruction; unavailable storage/bytes must be disclosed rather than reported as saved.

Assurance freezes subject and evidence for blind tests, controlled experiments, reproducible POCs, or independent verdicts. Design comparison alone is exploration or evidence-based self-review.

### Implementation Adoption

Consume Product's preserved revision, version/feature links and adoption/exclusion scope above; do not create a second asset register. Before translating a selected prototype or generated image into engineering work:

1. State which relationships must match, which are illustrative, and which details are unresolved. Preserve approved behavior and copy; a visual choice does not approve missing business states.
2. Map adopted regions to real project components, variants, tokens and routes. Keep the visual goal while using maintainable project code; do not embed the prototype or introduce a second equivalent component library merely to resemble it.
3. Define relevant comparison conditions: logical viewports, real content/data, languages, themes, density, input and states. Mark behavior unobservable from a static image as unknown.
4. Compare the implementation revision or equivalent version identity with that baseline. Record material deviations, impact, reason and acceptance or pending decision in the existing task/owner; never overwrite the baseline to make implementation appear compliant.
5. Link current rendered and operated evidence to the implemented revision and conditions. Verify layout/content relationships separately from state transitions, persistence and recovery. Report whether the adopted scope is implemented, partially implemented or unverified; an image comparison or token audit alone cannot establish acceptance.

Use only the conditions relevant to this adoption. Small local changes need no full matrix or new handoff document. Repair generated text/layout artifacts where authorized; faithful implementation of an approved design does not permit arbitrary spacing, copy or language changes. Return unresolved behavior/content to Product and implementation feasibility to Engineering.

## 4. Review Scope

Declare whether the subject is a component, page, flow, design system, or cross-device experience, then examine:

1. **Comprehension/hierarchy:** location, primary content, next action, exit.
2. **Consistency:** reuse of project-owned concepts, components, tokens, states, interactions.
3. **Task efficiency:** direct frequent paths, appropriate density, recoverable errors.
4. **State completeness:** loading, empty, error, disabled, selected, dangerous, long-content states.
5. **Responsive/input:** viable viewport, keyboard, touch, and precise-pointer behavior.
6. **Accessibility:** semantics, focus, names, contrast, zoom, non-color expression, reduced motion.
7. **Motion/feel:** purpose, frequency, feedback, space, interruptibility, performance.
8. **Feasibility:** component reuse, obtainable assets/data, and dependency cost.

Each finding identifies location, evidence, user impact, recommended outcome, and verification. Treat pure preference without task, comprehension, consistency, brand, or accessibility impact as optional—not a defect. Rank by user impact and frequency; prefer a few high-confidence findings over a long aesthetic list.

For an existing-system correction, evaluate the accepted baseline and legitimate variants rather than an imagined redesign. Separate defects, risks and optional improvements; preserve useful qualities. Aesthetic scores are not release thresholds. If structure prevents the task, revisit it before decorative fixes. Stop preference loops without observable benefit.

### Visual Review and Task Walkthrough

For independent review, use Assurance's identity and evidence requirements. Give the reviewer the current subject, scope, constraints and accessible evidence without prior scores or a defense of the implementation. Authorship and review standards need not be secret; isolation means a genuinely separate execution, not relabeling self-review.

- **Visual review:** provide current real rendering with viewport/state identity and existing design constraints. Use a whole-page view for rhythm and a readable view for text/details. Do not infer task success, persistence or normal-speed motion from static images.
- **Task walkthrough:** when discoverability or a changed flow is uncertain, provide a safe real entry, relevant user/role context, necessary test data and limits. Let the reviewer infer a likely goal and path when that is the question; do not give the expected clicks. For requirement acceptance, give the required goal instead—an unguided path cannot prove every required flow.

Record observation, action and actual result; separate facts, inferred causes and tool/data limits. Reproduce material findings before declaring defects. After correction, verify the affected task/recovery through project/Engineering checks; repeat independent walkthrough only for remaining risk. Without a runnable interface, report static analysis. Agent observations cannot establish human completion rate/time or replace user research.

## 5. Closeout

Separate approved design, remaining candidates, runtime-verified behavior, unverified device/data/user behavior, and the project owner updated. Check requirement/design links and saved revisions as part of the handoff. Code checks, screenshots, and design self-review are not user research, independent review, or production usability.

Reuse unchanged evidence only when its revision and affected dependencies still support the claim; refresh evidence touched by shared styling or behavior changes. Keep process captures/candidates in the authorized task location and production dependencies in normal project paths. Report unresolved build, service or data blockers to the responsible owner rather than silently dropping those conditions from “complete.”
