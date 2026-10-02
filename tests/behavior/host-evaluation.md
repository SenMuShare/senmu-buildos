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

## Interface contract coaching cases

The `contract-repair`, `contract-local` and `contract-audit` inputs use `contract_fixture.py`, an offline synthetic workspace with a real loopback HTTP provider, an existing OpenAPI source, a capability map and a preserved legacy module. Inspect the trusted scaffold before use; it refuses nonempty projects. Apply the existing native-host, permission and budget preconditions. Repair allows scoped file edits and loopback tests; audit is read-only. Local styling must not trigger unrelated API repair. These are optional model inputs, not recorded successful model runs.

`test_contract_coach.py` exercises the selector, pending adoption, source fingerprints and real HTTP failure/repair/persistence controls. Its explicit fixture assertions are not a general OpenAPI validator. Source tests do not prove model adherence or native instruction loading. In fresh sessions, inspect actual reads, diffs and checks rather than exact wording. Compare an unchanged second governance run; separately test a new worktree, code-owned schema generation, frontend-to-backend evolution and two agents given mismatched contract baselines. Preserve current business meaning and characterize unmeasured cases instead of presenting a walkthrough as an executed evaluation.

## Executable contract follow-through

Use the optional `contract-generated` and `contract-baseline` cases in an empty disposable workspace with the intended plugin snapshot. Install the example tools only under the same explicit environment/network/cost authority described above. Setup never installs packages or runs model calls. A missing tool is a reported verification gap, not a passing case. Observe a fresh main session and, where the host supports it, a separately delegated consumer task; neither this document nor the fixture runner counts as that observation.

For `contract-generated`, verify the model discovers code-owned declarations, changes the owning field description, regenerates derived artifacts, runs actual checks and preserves functional behavior. For `contract-baseline`, verify it notices that the consumer handoff names a different contract revision, retains the approved response, reconciles the task baseline and does not "fix" the mismatch by weakening the schema. Keep the existing `contract-local` non-trigger case. Record selected source/revision, loaded instructions, actual calls, artifact diff, pass/fail/gaps and usage only when observed. Repeat unchanged governance to assess no-op behavior without treating scripted initializer idempotence as model evidence.
