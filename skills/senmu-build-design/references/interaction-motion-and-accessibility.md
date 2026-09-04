# Interaction, Motion, and Accessibility

This standard governs interaction, feedback, motion, gestures, and accessibility. Interfaces should be direct, predictable, interruptible, and usable across inputs and abilities. More motion or one universal duration is not a quality measure.

## 1. Design Interaction Before Motion

For every critical interaction, define the user goal, trigger, immediate feedback, processing/success/failure/cancel states, focus and return behavior, and undo/recovery. Return undefined product behavior to Product; animation cannot hide missing states.

Before adding motion, evaluate:

1. **Frequency:** shortcuts, core navigation, and repeated actions should switch immediately or use minimal feedback; rare, explanatory, and completion moments have more expressive budget.
2. **Purpose:** accept feedback, state change, spatial continuity, reduced abruptness, explanation, or occasional delight. “Looks cool” is insufficient.
3. **Functional impact:** do not keep data moving while users read, compare, or operate. Motion must not delay input, conceal results, or block the next action.
4. **Alternatives:** reduced motion, keyboard, touch, precise pointer, and non-hover devices must complete the same task.

Choosing no motion is valid when no purpose survives these checks.

## 2. Physical and Temporal Behavior

- Give perceptible feedback immediately. Drag and swipe follow input continuously, not only after release.
- Repeated or reversed actions continue from the visible state rather than waiting for stale animation. Gesture systems should preserve position and velocity where useful.
- Establish spatial origin and corresponding enter/exit paths. Derive modal, panel, or overlay movement from the actual relationship rather than one universal rule.
- Prefer existing component behavior or CSS for simple predetermined changes, browser animation APIs for programmatic control, and existing Motion/GSAP-like dependencies only for springs, dragging, scroll choreography, or complex timelines. Do not install a library for a fade.
- Prefer transforms and opacity; enumerate animated properties. Avoid unbounded `transition: all`, continuous layout work, or parent-level inherited-variable updates that fan out across children.
- Reuse project tokens for duration, easing, springs, and stagger, then tune for size, distance, frequency, and product character. Interface feedback is normally shorter than narrative motion; exits should rarely feel slower than entrances. Do not promote fixed numbers without runtime evidence.

Verify interruptibility, browser load, and input latency in the running interface. Library or property presence does not prove smoothness.

## 3. Gestures and Direct Manipulation

- Preserve the grab point, use the platform event model and pointer capture, and update one-to-one during movement. Define multi-touch, bounds, cancellation, and focus loss.
- Resolve release targets from position, direction, and velocity. Express draggable bounds through progressive resistance rather than sudden freezing. Tune thresholds from component size, platform convention, and device tests.
- Do not lock unrelated input during animation. Retrigger, reverse, or exit from the current visible state.
- Gestures are never the sole path. Drag, swipe, long-press, and hover features also need a discoverable button, keyboard, or menu route.

Reuse component support for focus, gesture, collision, scroll lock, and semantics. Build custom behavior only when existing capabilities cannot satisfy the approved interaction.

## 4. Accessibility as Input

Validate against current target-platform and project standards rather than a frozen numeric checklist. Cover at least:

- semantic structure, control names, visible labels, and state announcements;
- keyboard order, visible focus, skip mechanisms, and overlay focus entry/return;
- text/key-graphic contrast, zoom, dynamic type, and long-text reflow;
- touch targets, adjacent actions, misactivation prevention, and dangerous-action recovery;
- non-color, non-position, non-icon, non-sound, non-vibration, and non-motion expression;
- reduced-motion removal of large travel, bounce, parallax, and loops while retaining useful brief fades/state changes;
- legibility of transparent surfaces under reduced transparency, high contrast, and complex backgrounds;
- stop, alternative, or avoidance for autoplay, flashing, full-screen motion, and brightness jumps.

## 5. Review

Reproduce the real interface and key states, then record location, current behavior, user impact, and minimum improvement. Prioritize task failure, mistakes, inaccessibility, comprehension cost, frequency, and affected users—not taste or a default defect hunt.

Verify target viewports, keyboard, touch/pointer, reduced motion, loading/failure, longest content, rapid retriggering, and reversal. Inspect motion at normal speed and slow/frame progression for endpoints, curves, origins, and coordinated properties. Test gestures on real devices. Mark feel as pending runtime verification when code cannot establish it.
