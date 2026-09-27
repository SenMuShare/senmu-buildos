# Native host evaluation

These are optional execution inputs, not recorded successes. Local contract tests do not establish model adherence, native hook registration or token savings. Keep results outside the distributable product, in the existing task/experiment owner.

## Preconditions and safe commands

Use a trusted disposable project and the intended installed/source snapshot. Check `claude --version` or `codex --version`, account access, tool permissions and budget first. Do not install clients, change global trust or authorize paid calls automatically. Claude plugin eval and judge calls consume account usage. Source-only changes can complete with a disclosed native-test gap.

From the product root, `claude plugin validate .` checks manifest/Skill structure. For an authorized single native smoke case:

```sh
claude plugin eval . --eval-dir tests/behavior/claude-evals --case rust-review --runs 1 --ablation none --no-publish
```

Confirm flags with the selected host's `--help`. The cases use read-only tools and no scaffold, network or production mutations. Results are ignored by Git. A one-run smoke result is not comparative evidence; use matched snapshots, model, host, tasks, permissions and budgets before comparing versions or the no-plugin baseline. Report usage fields actually available, separating input, output and cached tokens from byte/character proxies.

## Check the behavior rather than the wording

The native cases distinguish a should-trigger Rust review, a nearby covered local task that needs no Skill, and an explicit existing-project instruction audit. Grade invocation separately from correct results and preservation of authority. Phrase-equivalent answers remain valid; a `tool_used: Skill` observation is not itself task success.

In an authorized Codex fresh session, apply the same prompts and criteria to a disposable project. Inspect the selected Skill, actual references and result, not a wrapper's success. Do not reuse the authoring conversation. Missing native clients/access leave these observations unverified.

For hooks, observe startup, resume, clear, compaction, fork and subagent events; count actual effective registrations and emitted Kernel payloads. For project adoption, preserve distinctive parent/local exceptions and verify the changed task route. Check a second unchanged governance pass performs no semantic rewrite. Recovery checks retain pending scope and distinguish source evidence from prior model conclusions.

Official calibration (2026-09-26): [OpenAI skills](https://developers.openai.com/codex/skills), [Codex AGENTS](https://developers.openai.com/codex/guides/agents-md), [Claude evals](https://code.claude.com/docs/en/plugin-evals), [Claude memory](https://code.claude.com/docs/en/memory). Follow current host documentation if schemas change; never loosen safety settings merely for a passing score.


## Real workspace cases

The `workspace-*` cases seed an offline shop fixture with real code, a capability map, root and scoped instructions, an import, a legacy exception and focused business tests. Their prompts do not supply the implementation path or tell the model which Skill not to call. Inspect the trusted `workspace_fixture.py` and case scripts before enabling `--scaffold`; setup refuses a nonempty directory and never edits an existing project.

For an authorized, isolated local-edit case, from the product root:

```sh
claude plugin eval . --eval-dir tests/behavior/claude-evals --case workspace-local --runs 1 --ablation none --no-publish --scaffold --allow-tools Edit "Bash(python3 -m unittest discover *)"
```

Use read-only grants for `workspace-adoption` and `workspace-public-job`. `--scaffold` executes trusted setup as the user; it is not an agent permission. Do not widen global trust or tool grants just to raise scores. The local regression runs real fixture tests before/after a known minimal fix and checks preservation. That proves fixture behavior, not model behavior or native instruction loading. Observe native traces and outcomes separately, then repeat an unchanged governance request in a fresh session to assess semantic no-op behavior; this repeated-model observation remains unmeasured until run.

The `workspace-hard-bug` and `workspace-resume` inputs extend the same fixture generator. The former tests a multi-step late-result defect; the latter seeds corrected arithmetic and a remaining zero-receipt defect. Their outcome graders inspect actual code, commands, preserved scope and item accounting, not exact phrases. The ordinary fixture regression deliberately performs the repair to establish that these inputs detect their defects; that is not a model run. Run a fresh native session only under the same explicit host, tool and cost preconditions above, using the selected case name and its declared scaffold. Record unchanged/rejected alternatives and failures, not just favorable traces.

## Host-path and instruction-discovery repair observations

For an authorized fresh-session smoke check, use a disposable installation path containing spaces, an apostrophe or non-ASCII characters. Observe one Kernel payload per lifecycle event; missing root/script errors must not be recorded as loaded instructions. Existing `tests/hooks/path-inputs.test.js` verifies packaged commands in child processes only, not native host registration.

For instruction adoption, use project-local links, a deliberately unread external link, inline imports and fenced/inline code examples. Preserve one distinctive project exception, then repeat an unchanged audit. Compare the assessor's candidate inventory with actual host loading; external targets remain unread by the assessor and scoped directory links remain unscanned. The expected audit has no automatic rewrite/deletion. `test_instruction_inventory_edges.py` verifies these fixtures, not model adherence. Retain the same permission, cost and evidence preconditions above.
