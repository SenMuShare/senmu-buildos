# Frontend Engineering Contracts and Verification

Use this standard to calibrate browser/client implementation when frontend contracts are missing, conflicting, or changing. When project rules already guide ordinary implementation, follow them directly; “frontend development” does not justify loading a general textbook.

## 1. Frontend Implementation Boundary

Frontend Engineering turns approved product behavior and design specifications into observable interfaces: render/interaction state, browser routing, client data-fetch boundaries, form submission, public component contracts, responsive and accessible implementation, and browser verification. It does not redefine product capability, copy meaning, or visual direction.

Read the project's framework, router, state management, request layer, component system, tokens, tests, and build entrypoints first. Extend existing public seams. Add dependencies or abstractions only when current capability cannot satisfy a real contract.

## 2. State and Data

- Separate server facts, URL/navigation state, session/persistent state, form drafts, and presentation state. Each fact has one authority.
- The data-access layer owns server data; components receive explicit results/actions. Do not create writable copies in request, cache, form, and global store layers.
- Handle loading, empty, error, retry, invalidation, concurrent submission, and success feedback on real paths. Optimistic updates require failure recovery and eventual server reconciliation.
- Put filters, pagination, selection, and deep links in routing when URLs can represent them under project convention; refresh, back, and sharing should preserve relevant context.
- Forms provide immediate client feedback and final server validation. A disabled button does not replace duplicate-submission, authorization, or idempotency protection.

## 3. Components and Pages

Define components around stable responsibility, reuse need, and state ownership—not the number of visual blocks. Public components expose maintainable domain-neutral inputs, events, and state; page composition retains scenario meaning. Prefer local composition for one-off differences over speculative configuration layers.

Design tokens, variants, and accessibility semantics come from the project design owner. A component library supplies implementation capability; it does not define visual standards or product copy. Invoke a peer specialist Skill for current APIs, performance, or framework practice rather than copying its manual here.

## 4. Verification

Select type/static checks, component tests, route/data integration tests, and real-browser verification by risk. Cover changed target viewports, key states, keyboard/touch paths, console errors, and necessary network behavior; rerun the original page and action path for a defect.

A snapshot or one DOM assertion proves only that observation. Layout, wrapping, focus, scroll, responsive behavior, motion, and browser APIs require real rendering or equivalent runtime evidence. State uncovered devices, browsers, and states.
