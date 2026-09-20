# OpenAI GPT Image Profile

Calibration: 2026-09-20. Applies to `gpt-image-2`, `gpt-image-2.5-sunburst` and `gpt-image-2.5-flare` on OpenAI's documented image interfaces. Verify aliases and wrappers independently; do not auto-upgrade a project's chosen model. This is an authored summary of the sources below, not a copied provider prompt.

## Prompt Adaptation

OpenAI's current prompting guide recommends concrete visual requirements rather than adjective piles. Express the approved composition and placement; quote exact visible copy and its required placement/count. Assign a distinct purpose to each reference image. In edits, distinguish requested changes from elements to retain. Use a readable format rather than assuming a magic syntax. An iterative request should name its change and repeat important preservation constraints; that advice applies only when iteration already belongs to the authorized workflow. Inspect the output for spelling, layout and unintended edits. [1]

BuildOS application: preserve the source brief's meaning and creative discretion. Do not import styles or exclusions from official examples. A prompt-only node still returns its existing prompt output, not an image or a new review loop.

## API and Version Boundaries

The Image API selects the renderer directly. The Responses API uses a supported main model plus an image-generation tool with its own model selection. Size, quality and output settings are request fields, not a substitute for the visual brief. The current quality levels for 2.5 include `xhigh` and `max`; GPT Image 2 has `low`, `medium` and `high`. GPT Image 2 handles image inputs at high fidelity automatically; omit `input_fidelity` for that model. Do not transfer those settings to a different version without checking its contract. [2]

BuildOS application: identify the actual endpoint before applying a parameter recommendation. Keep request configuration fixed during content-only reconciliation. Missing input assets are not permission to invent an edit target. Strict pixel preservation, accepted text or identity consistency requires appropriate output evidence, not a prompt assurance. Where achieving the requirement calls for compositing, different settings or another model, propose that separately.

## Verification and Revisit

Use the project's supplied text, references, protected elements and existing acceptance tests. Compare original and revised instructions under the same renderer and settings; keep failures and variability visible. No API calls or measured output-quality gains were performed to establish this profile. Revisit when a selected model, API contract or relevant official recommendation changes. Specific settings and cost tradeoffs stay with the project's adapter, not a universal preset.

[1]: https://developers.openai.com/api/docs/guides/image-prompting
[2]: https://developers.openai.com/api/docs/guides/image-generation
