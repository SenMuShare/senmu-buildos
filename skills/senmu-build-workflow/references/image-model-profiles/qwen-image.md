# Alibaba Model Studio Qwen Image Profile

Calibration: 2026-09-20. Scope: hosted `qwen-image-2.0`, `qwen-image-2.0-pro`, `qwen-image-3.0` and `qwen-image-3.0-pro` on the documented endpoint for the selected region and mode. Dated snapshots require matching documentation. This does not establish API compatibility for self-hosted Qwen or another vendor's wrapper.

## Model and Endpoint Differences

For the 2.0 text-to-image API, positive text and `negative_prompt` are distinct inputs. `prompt_extend` controls automatic rewriting of positive text, not the negative prompt. The synchronous DashScope request uses messages and a parameters object; output size uses a `width*height` string. Its documented text limits can truncate input, so preserve essential constraints instead of appending a large agent charter. Do not copy another family's size, count or asynchronous support. [1]

For 2.0 editing, inspect the dedicated editing API and preserve the actual order and purpose of supplied images. Text-to-image request knowledge alone is insufficient evidence of edit-input compatibility. [2]

Qwen 3.0 has a separate generation/editing API. In its OpenAI-compatible mode, editing uses the generations endpoint with an `image` extension, not OpenAI's multipart edits/mask interface. Compatible-mode dimensions use `x`, while DashScope uses `*`. `prompt_extend_mode=agent` is for text-to-image, not image editing. Provider extension fields are not OpenAI's own parameters. [3]

## Content Adaptation

BuildOS application of these interfaces: preserve exact supplied copy, image roles and the intended result in the project brief. Use the existing negative prompt only for actual exclusions, not an unrelated stock list. Distinguish instructions sent by the application from any provider-side rewrite. Keep rewrite settings, image count, model and endpoint unchanged during content-only governance; a setting change is a separate reviewed choice, not a silent prompt cleanup. Do not assume all Qwen variants support the same controls.

For a revised prompt, keep variables and the consuming schema intact. Localize the agent definition according to project policy without translating exact in-image copy or API keys. Do not invent image inputs, add a generation step to a prompt-only node or silently switch regions. Preserve permitted input-data boundaries when a hosted API is involved.

## Verification and Revisit

Check rendered requests as well as prose: selected model/endpoint/mode, actual image references, supplied copy, retained constraints and unchanged output contract. Only authorized image comparisons establish an effect; API-schema checks do not prove better imagery. No paid model runs were performed for this profile. Recheck current primary material for an unlisted model, snapshot, wrapper or changed API. General visual-brief rules are maintained in the parent guidance, not repeated as a Qwen-specific recipe.

[1]: https://help.aliyun.com/zh/model-studio/qwen-image-api
[2]: https://help.aliyun.com/zh/model-studio/qwen-image-edit-api
[3]: https://help.aliyun.com/zh/model-studio/qwen-image-generation-and-editing-api-reference
