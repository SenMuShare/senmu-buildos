# Frontend Engineering Contracts and Verification

Use this standard to calibrate browser/client implementation when frontend contracts are missing, conflicting, or changing. When project rules already guide ordinary implementation, follow them directly; “frontend development” does not justify loading a general textbook.

## 1. Frontend Implementation Boundary

Frontend Engineering turns approved product behavior and design specifications into observable interfaces: render/interaction state, browser routing, client data-fetch boundaries, form submission, public component contracts, responsive and accessible implementation, and browser verification. It does not redefine product capability, copy meaning, or visual direction.

Start from the affected page, component, behavior or failing check and its applicable project contract. Read framework, routing, state/request, design-token, test or build details only when the current question or declared review scope requires them. Expand on evidence, not a universal preload checklist. Extend existing public seams; add dependencies or abstractions only when current capability cannot satisfy a real contract.

## 2. State and Data

- Separate server facts, URL/navigation state, session/persistent state, form drafts, and presentation state. Each fact has one authority.
- The data-access layer represents server-owned facts; components consume explicit results/actions. Local form drafts and optimistic state may be writable when their origin, submission, cancellation and reconciliation are explicit. Do not let request, cache, form and global-store copies become competing authorities for the same fact.
- Handle loading, empty, error, retry, invalidation, concurrent submission, and success feedback on real paths. Optimistic updates require failure recovery and eventual server reconciliation.
- Put filters, pagination, selection, and deep links in routing when URLs can represent them under project convention; refresh, back, and sharing should preserve relevant context.
- Forms provide immediate client feedback and final server validation. A disabled button does not replace duplicate-submission, authorization, or idempotency protection.

## 3. Components and Pages

Define components around stable responsibility, reuse need, and state ownership—not the number of visual blocks. Public components expose maintainable domain-neutral inputs, events, and state; page composition retains scenario meaning. Prefer local composition for one-off differences over speculative configuration layers.

Design tokens, variants, and accessibility semantics come from the project design owner. A component library supplies implementation capability; it does not define visual standards or product copy. Invoke a peer specialist Skill for current APIs, performance, or framework practice rather than copying its manual here.

### Client Lifecycle and Async Ownership

Do not imperatively start, abort or clean up active requests/subscriptions, mutate shared state or perform external writes during React client rendering or memo calculations. Use the selected framework's supported data-access, event and lifecycle facilities, or an appropriate Effect setup/cleanup; do not move every action into an Effect. Pure local calculation and framework-supported resource reads are not forbidden. Server loaders and Server Components follow their own framework contracts rather than this client-only rule.

For replaceable async work, associate results with the correct entity/session and request generation or equivalent framework key. Before applying success, error, progress or a UI-state finalizer, ensure that result still belongs to its intended consumer. Obsolete work still releases its own resources, but its completion must not overwrite another project's result or clear a newer request's loading state. Reuse existing cache/request ownership when it already provides the guarantee; unrelated concurrent requests may remain valid.

Clean up only resources owned by the departing lifecycle, and tolerate repeated setup/cleanup under the framework contract. Aborting a transport is not proof of external cancellation and does not by itself prevent a late result from being applied. Keep actual provider cancellation, local result validity and recovery as distinct responsibilities.

## 4. Verification

Select type/static checks, component tests, route/data integration tests, and real-browser verification by risk. Cover changed target viewports, key states, keyboard/touch paths, console errors, and necessary network behavior; rerun the original page and action path for a defect.

A snapshot or one DOM assertion proves only that observation. Layout, wrapping, focus, scroll, responsive behavior, motion, and browser APIs require real rendering or equivalent runtime evidence. State uncovered devices, browsers, and states.
