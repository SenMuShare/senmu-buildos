# Component Design Patterns

Choose patterns for the actual task—not popularity. First determine whether users compare, locate, edit, advance, or inspect results, then select the smallest composition.

| Pattern | Suitable task | Required relationship | Avoid |
| --- | --- | --- | --- |
| Command entry | locate actions, objects, navigation quickly | clear search, grouping, keyboard/touch paths, empty and unavailable states | hiding the primary journey by putting everything in a command palette |
| Canvas + inspector | edit an object and its properties | selection and inspector context stay synchronized; canvas remains the focus | permanently expanding all settings or showing stale properties after selection is lost |
| Index + detail | locate and inspect a record in a collection | stable selection, return position, deep links, empty/error states | losing filters, scroll, or selection feedback after opening detail |
| Comparison matrix | compare alternatives, versions, or metrics on shared dimensions | fixed row/column semantics, visible differences and bases, narrow-screen alternative | many cards that require users to remember values across views |
| Step flow | work with real order, checkpoints, or irreversible submission | explicit progress, saved state, back effects, failure recovery | splitting a short direct form into artificial steps |
| Metric + context | monitor results, trends, anomalies | value includes time, basis, change, next action; anomaly supports drill-down | isolated large numbers or color-only meaning |
| Preview + commit | generate, publish, import, or batch edit | align input, preview/diff, execution commitment and recovery; confirm according to consequences, without a mandatory second dialog | preview and execution using different data/defaults |

Design only states the task actually has. Common states are prompts, not a reason to invent hover, selection, or batch behavior. Critical states must be observable in implementation and real verification.

Use the project's real component/variant and representative content when a pattern is adopted. A component image is useful for appearance, but cannot demonstrate focus, selection, long content or a parent layout relationship. Extend the existing specimen or example; do not create a parallel component catalog solely for this task.

## Direct Manipulation and Play

Use this section only when manipulating objects or experiencing the process is part of the product: a timeline, spatial editor, knob, draw/game loop or animated collection. First identify the actual objects, how users recognize them, how input changes them, visible states, the next action and asset/rendering requirements. A state table is useful only for genuinely ambiguous relationships.

Trace input → object change → feedback → next operation or settlement. Include the states the loop really has, such as ready, active, processing/performance, locked, completed, failed and recoverable; replacing a label on one static image may not express the required change. Define the activation threshold, cancellation and what is locked during an operation; preserve an alternative to gesture-only input.

Where the loop consumes credit, saves progress or awards a result, carry the approved commitment/retry/recovery behavior to Engineering. Repeated input and refresh must not silently duplicate or erase the outcome. Product defines when commitment occurs; a dramatic animation must not invent that business rule. Longer presentation can be appropriate when the process is the experience, but reduced motion must retain the same valid result and available action.

Verify actual input, cancellation/repetition, visible result and relevant refresh/failure recovery. Inspect frame sequences for state changes and normal-speed operation for feel; declare missing device or sound/haptic evidence. State completeness and a graphics library alone do not establish a playable or usable experience.
