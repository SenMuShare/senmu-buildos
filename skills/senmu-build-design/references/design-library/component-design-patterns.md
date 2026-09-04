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
| Preview + commit | generate, publish, import, or batch edit | input, preview, diff, confirmation, execution, recovery form one chain | preview and execution using different data/defaults |

Design only states the task actually has. Common states are prompts, not a reason to invent hover, selection, or batch behavior. Critical states must be observable in implementation and real verification.
