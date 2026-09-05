# Prototype Exploration and Interface Review

Use this standard when direction is uncertain, interaction risk is high, or the task needs holistic UI/UX judgment. Prototypes discover and compare design; they are not automatically product decisions, production code, or independent evidence.

## 1. When to Prototype

Prototype when alternatives materially change hierarchy or interaction; gesture, motion, or spatial relationships cannot be judged statically; a costly implementation needs task-path validation; or the user explicitly requests prototypes. Direction-only alternatives can use observed evidence and specifications without building a prototype.

Implement and verify local styling, an approved design, routine composition of mature components, or a cheap reversible change directly. Do not prototype merely to demonstrate process.

## 2. Materially Different Alternatives

Offer two or three alternatives when the decision warrants them. Differentiate information hierarchy, layout model, visual character, asset strategy, or interaction mechanism—not only color, radius, and shadow.

Hold core content, data, task, and device conditions constant. For each alternative state:

- what the user sees and completes first;
- the visual/interaction mechanism and suitable context;
- required assets and technical prerequisites;
- accessibility, performance, maintenance, and brand risks;
- why it is or is not recommended.

With sparse input, use understandable direction names and make a recommendation. Do not transfer a design-vocabulary questionnaire to the user.

## 3. Prototype Boundaries

- Use the project's prototype entrypoint, Storybook, test route, isolated example, or disposable workspace. Do not put candidates in production navigation, real data, or release sources.
- Reuse the stack, components, and fake data. Add dependencies only when the prototype question needs them and benefit exceeds install/maintenance cost.
- Static mockups test composition and visuals. Task paths, gestures, focus, responsiveness, and motion require interaction; screenshots cannot establish them.
- Record subject, version, target viewports, assumptions, and unknowns. A selected visual direction is not approval of the business requirement.
- Write selected stable decisions into the existing design, product, or implementation owner. Keep alternatives isolated and delete/archive/retain them only within authorization; do not leave permanent competing themes.

Assurance freezes subject and evidence for blind tests, controlled experiments, reproducible POCs, or independent verdicts. Design comparison alone is exploration or evidence-based self-review.

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

## 5. Closeout

Separate approved design, remaining candidates, runtime-verified behavior, unverified device/data/user behavior, and the project owner updated. Code checks, screenshots, and design self-review are not user research, independent review, or production usability.
