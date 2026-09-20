# Claude Code adapter

The adapter supplies the shared BuildOS kernel through Claude's lifecycle protocol.
It does not copy project instructions, change user settings or install another rulebook.

## Project instructions

During first adoption or instruction-related troubleshooting, inventory the project's
AGENTS, CLAUDE, local and scoped rule files through Project governance. File discovery
is not proof of loading. Keep the shared project's rules in one existing owner. Adopt compact shared working principles and reconcile local rules through Project's dual-track authoring contract; preserve the project document language and existing exceptions. Imports are not a reason to maintain another translated rulebook or duplicate the Kernel. A plugin update alone does not rewrite project instructions.

Claude Code v2.1.277 introduced native AGENTS support, subject to host settings and
availability. By default a project CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md on
the working-directory path takes precedence over AGENTS discovery. Restricted or older
sessions may load CLAUDE only. Do not enable telemetry, relax enterprise policy, or
change global settings just to activate BuildOS.

When the selected environment does not natively load the shared file, preserve the
existing CLAUDE-specific content and use a real relative import, for example
`@AGENTS.md` beside that file, rather than a copy or a sentence asking the model to
read it. Nested files retain their own scopes; Codex AGENTS.override.md is not a
Claude override. An existing working import needs no migration.

Confirm the host version, selected plugin source and the next session's actual loaded
instructions. Directly loaded AGENTS may not appear in /memory or /context; use the
host's AGENTS-loaded notice or a harmless question about a distinctive project rule.
CLAUDE imports can be checked through /context. Do not infer activation from VERSION,
file presence, an enabled plugin, or a wrapper's successful JSON output.

## Kernel and subagents

BuildOS's kernel is not the project's AGENTS content; retain a single shared kernel
owner. Explore/Plan and other read-only agents receive only the delegated scope and
necessary evidence, without a commit obligation or a preload of every project rule.

For a suspected duplicate lifecycle injection, inspect the selected host's registered
commands and actual startup/resume/compaction/subagent output in a disposable project.
The default hooks/hooks.json and manifest-selected hooks need host-level observation;
do not delete another adapter or add a persistent deduplication database on guesswork.
Transport tests prove payload shape, not a real host's registration or model behavior.

Official references (checked 2026-09-19):
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/plugins-reference
- https://code.claude.com/docs/en/sub-agents
