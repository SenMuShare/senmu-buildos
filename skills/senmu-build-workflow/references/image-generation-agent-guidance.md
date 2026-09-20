# Image Agent Definition and Prompt Adaptation

Load only while defining or governing an image-generation/editing agent or reusable image-prompt node. Do not generate images just because this guidance was read. A non-image agent does not load image profiles, and a fixed model call does not require a multi-agent architecture.

## Separate the Four Concerns

- Agent charter: stable business responsibility, tools, permissions, decisions and acceptance.
- Run brief: this task's inputs, reference assets, desired result and preserved constraints.
- Render prompt: the visual instructions derived from that brief for the selected image model.
- Request configuration: actual provider/model, endpoint, mode and supported parameters owned by the project's adapter/configuration.

Do not send the whole agent charter, governance records or other models' manuals as the render prompt. Do not assume an API reads project Markdown. Confirm the actual assembly and consuming request. A text planner and the image renderer may use different models; record both only where they are actually present. Final image text language is independent of the charter's language.

## Meaning-Preserving Visual Brief

Capture only applicable, supplied or already-approved requirements: subject and purpose; composition and placement; medium/style; exact visible text; reference-image roles; requested edits and protected elements; exclusions; output requirements and acceptance. These are content questions, not mandatory new API fields. Preserve the project's field names and output format. Do not invent a brand, style, reference image or tool capability to fill missing slots.

For example, when the original brief already requires preserving identity and changing only a background, group those two constraints explicitly rather than adding a new lighting style. Example slots illustrate mapping, not a compulsory template:

```text
Requested result: <approved task>
Source assets and their roles: <actual inputs, only when present>
Change: <authorized differences>
Preserve: <existing protected content>
Exact visible text: <verbatim supplied copy, when applicable>
```

Dimensions, quality and format must also be represented in the supported request fields where applicable; prose is not evidence of parameter configuration. Keep the existing parameters during content-only governance. If a desired result requires a capability or workflow change, report that separately rather than quietly switching models or adding regeneration.

## Select One Applicable Profile

Resolve the exact model/version, provider, endpoint, mode and relevant rewrite settings from current project evidence. A brand name, alias or chat UI name alone is insufficient.

| Confirmed target | Conditional guidance |
| --- | --- |
| OpenAI GPT Image 2 or GPT Image 2.5 via its documented APIs | [GPT Image profile](image-model-profiles/openai-gpt-image.md) |
| Alibaba Model Studio Qwen-Image 2.0 or 3.0 via its documented APIs | [Qwen Image profile](image-model-profiles/qwen-image.md) |
| Another model/version, private deployment or incompatible wrapper | Keep the common brief; check its current primary documentation, retain unsupported facts as unknown, and do not borrow parameter support by name similarity. |

Profiles are scoped reference guidance, not model-selection orders. Recheck changed capabilities when the model, endpoint or relevant source changes, not on every image run. A new profile needs exact applicability, official sources/date, decision-changing differences, limitations and a counterexample; keep common business rules here or in the Agent Framework. Route the new file and its tests through the existing Workflow owner. No global model catalog, forced provider or automatic network-refresh service is required.

## Adoption and Acceptance

Write only the needed adopted instructions into the project's existing definition/prompt owner. Runtime uses that definition, configuration and run inputs, not all BuildOS profiles. The minimum useful check is against the business contract: required content, exact text, reference fidelity, protected regions, dimensions/format and downstream consumption where applicable. Missing source assets block editing claims; response success alone does not prove accepted imagery.

Preserve existing evaluation, retry, cost and release boundaries. Compare effects with real authorized outputs before claiming improvement; no prompt can guarantee an absolute best result. Provider examples are starting points, not authority to change project intent.
