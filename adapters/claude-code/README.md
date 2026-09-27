# Claude Code adapter

## Single lifecycle registration

The packaged plugin uses only the default `hooks/hooks.json`. Claude loads that file together with any manifest-declared hooks, so `.claude-plugin/plugin.json` must not also register the legacy adapter configuration. The shared commands read host-provided `PLUGIN_ROOT`, `CLAUDE_PLUGIN_ROOT` or `ZCODE_PLUGIN_ROOT` as environment data, never interpolated JavaScript. A missing root/script reports an error instead of silent success. They emit the same Kernel lifecycle protocol; no new host-specific hook fields are required.

The files in `adapters/claude-code/hooks/` remain compatibility implementations for explicit integrations; they are not an additional packaged registration. Do not register them beside the default configuration. No persistent deduplication state is needed. Startup, resume, clear, compact, fork and subagent events must each receive one payload, including in a fresh process. Process tests prove command dispatch, not native registration or model adherence.

## Project instructions

During adoption or instruction troubleshooting, inventory AGENTS, CLAUDE, local rules and ancestors. Keep shared rules at one existing owner and reconcile only applicable differences through Project's instruction-authoring contract. Preserve language, exceptions, global settings and enterprise policy. Plugin updates do not rewrite projects or business agents.

Claude Code v2.1.277 introduced native AGENTS support. Its effective Project instructions setting and CLAUDE files on the working-directory path determine loading. Before v2.1.281, some restricted environments could read only CLAUDE. Do not enable telemetry or relax policy to activate BuildOS.

Where native loading is unavailable, preserve CLAUDE-specific content and use a real relative import such as `@AGENTS.md`, not copied text or a prose request to read it. Existing valid imports need no migration. Nested scope still applies; Codex `AGENTS.override.md` is not a Claude override. Imports organize files but still contribute startup context; prefer conditional rules or Skills for specialist detail.

Check the host version, selected plugin and fresh-session loaded instructions. From v2.1.280, `/memory` and `/context` list directly read AGENTS; older versions need the loaded notice or a harmless question about a distinctive rule. Native AGENTS does not fire `InstructionsLoaded`, while a CLAUDE import does. Neither VERSION nor file presence proves loading.

## Validation

From this product root, `claude plugin validate .` checks supported manifest/Skill syntax when the host is available. The optional native cases and cost/permission boundaries are documented in [host evaluation](../../tests/behavior/host-evaluation.md). Do not install tools, grant global trust or make paid calls merely to satisfy a source check.

For lifecycle problems, inspect actual commands and startup/resume/compaction/subagent output in a disposable project. Read-only agents receive delegated evidence, not a commit duty or all project rules. Keep the shared Kernel distinct from project AGENTS; never print the whole AGENTS from a Hook.

Official references checked 2026-09-26:
- https://code.claude.com/docs/en/plugins-reference
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/plugin-evals
