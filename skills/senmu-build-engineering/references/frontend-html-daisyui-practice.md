# Lightweight HTML and daisyUI Frontend Profile

Use this profile for lightweight H5 pages, campaigns, documentation pages, small internal tools, and static deliverables that need only native HTML, limited JavaScript, and one UI system. It owns technical route and implementation only. Route creation/review of visual direction, design system, responsive experience, or interaction quality to `senmu-build-design`. This is not the default for all frontend work; preserve an established React, Vue, Ant Design, or other stable stack.

## 1. Applicability

HTML-first fits when the page opens directly or is statically hosted with simple build/runtime boundaries; routes, shared state, and complex interaction are limited; no large component state, SSR, complex data layer, or long-lived multi-person SPA architecture is needed; and value comes mainly from content, forms, presentation, or local interaction.

Retain the project framework for complex routing, real-time collaboration, extensive shared state, a durable component platform, or an existing framework baseline. Do not rewrite a mature system to appear lightweight.

## 2. Technology Route

1. Reuse current HTML, CSS, JavaScript, and build entrypoints.
2. For a new lightweight page, prefer semantic HTML and small modular JavaScript.
3. Evaluate Tailwind CSS plus daisyUI when consistent component presentation is needed.
4. Adopt a framework only after real reuse, state, or routing pressure appears.

daisyUI supports installation as a Tailwind plugin and through CDN. Tailwind documents Play CDN for development rather than production. Formal delivery should prefer locked project versions and reproducible CSS builds. See [daisyUI install](https://daisyui.com/docs/install/), [daisyUI CDN](https://daisyui.com/docs/cdn/), and [Tailwind Play CDN](https://tailwindcss.com/docs/installation/play-cdn).

Do not freeze versions in this general profile. Inspect dependencies, lockfiles, build method, and current official documentation before implementation.

## 3. Page and Components

- Use semantic `header`, `nav`, `main`, `section`, `form`, and `button`; do not build everything from meaningless `div`s.
- Reuse daisyUI component classes/theme variables instead of rebuilding buttons, cards, dialogs, and forms in CSS.
- Preserve approved hierarchy, spacing, color roles, and design tokens. Custom CSS expresses only real uncovered differences.
- Organize JavaScript by behavior with discoverable event entrypoints, state, I/O, and errors; avoid one monolithic inline script.
- For approved simple state motion, prefer component capability or CSS transitions with the project's reduced-motion path. Complex motion follows Design decisions and the matching technical specialist.

## 4. Responsive and Accessible Behavior

- Start from the narrow-screen core flow; define mobile breakpoints, touch sizes, wrapping, and horizontal overflow.
- Associate form controls with labels and errors and make them keyboard reachable.
- Dialogs, menus, and drawers manage focus, Escape, close behavior, and background scroll.
- Color is not the only state signal; verify contrast plus loading, empty, error, and disabled states.
- Images declare dimensions, alternative text, and loading strategy to avoid layout shift and unnecessary size.

## 5. Data, Security, and Runtime

- Never embed secrets, production credentials, or server-only business rules in HTML/client JavaScript.
- Escape and validate external input for its context; never concatenate untrusted HTML.
- Network requests handle timeouts, errors, duplicate submission, and recoverable user feedback.
- Record provenance, privacy, availability, and offline effects of CDNs, fonts, analytics, and third-party assets.
- A static page gains no backend authority; authentication, payments, data ownership, and sensitive operations remain server contracts.

## 6. Delivery and Verification

By risk, verify direct/static-host entrypoints and assets; mobile/desktop layouts; keyboard, focus, labels, and key accessibility; console, network failure, empty states, and duplicate submission; reproducible build, locked dependencies, asset size, and caching; and project lint, HTML validation, browser tests, or visual acceptance.

When promoting a CDN prototype to a formal page, decide whether dependencies/build artifacts must become local and locked. “Opens locally” is not production completion.
