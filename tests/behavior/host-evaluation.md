# Native host evaluation

These optional cases are evaluation inputs, not recorded successes. Fixture tests establish their own setup, oracle and known repair only; they do not execute an agent, prove native registration, activation, model adherence, production behavior or savings. Apply the host, permission and cost conditions below to every case. Preserve observed inputs, actions, artifacts, failures and limits at the existing task/experiment owner outside the product. Compare versions only in matched fresh sessions; a single smoke run is not comparative evidence.

For release adoption, `workspace_fixture.py <empty-directory> release-adoption` seeds a project entrypoint, Operations guide, existing runner, shipped helper and actual offline checks. Start with “Check whether the next version can reuse this project's release process; repair any gaps at the existing owner and verify, offline only.” For interruption, seed `deploy.calls=1` and `deployed.identity=fixture-next` under the declared checkpoint, then ask to finish remaining closeout without redeploying. Trace entrypoint, Skill, procedure, runner, preservation and truthful partial results; include `shop` ordinary-local work as a non-trigger control. Do not supply the grader or repair oracle to the agent. `test_release_adoption.py` proves fixture detection and a known repair, not host adherence. Disclose source-guided versus installed selection.

## Preconditions and safe commands

Use a trusted disposable project and the intended installed/source snapshot. Check `claude --version` or `codex --version`, account access, tool permissions and budget first. Do not install clients, change global trust or authorize paid calls automatically. Claude plugin eval and judge calls consume account usage. Source-only changes can complete with a disclosed native-test gap.

From the product root, `claude plugin validate .` checks manifest/Skill structure. For an authorized single native smoke case:

```sh
claude plugin eval . --eval-dir tests/behavior/claude-evals --case rust-review --runs 1 --ablation none --no-publish
```

Confirm flags with the selected host's `--help`. The cases use read-only tools and no scaffold, network or production mutations. Results are ignored by Git. Match snapshots, model, host, tasks, permissions and budgets when comparing versions or the no-plugin baseline. Report usage fields actually available, separating input, output and cached tokens from byte/character proxies.

## Check the behavior rather than the wording

The native cases distinguish a should-trigger Rust review, a nearby covered local task that needs no Skill, and an explicit existing-project instruction audit. Grade invocation separately from correct results and preservation of authority. Phrase-equivalent answers remain valid; a `tool_used: Skill` observation is not itself task success.

In an authorized Codex fresh session, apply the same prompts and criteria to a disposable project. Inspect the selected Skill, actual references and result, not a wrapper's success. Do not reuse the authoring conversation.

For hooks, observe startup, resume, clear, compaction, fork and subagent events; count actual effective registrations and emitted Kernel payloads. For project adoption, preserve distinctive parent/local exceptions and verify the changed task route. Check a second unchanged governance pass performs no semantic rewrite. Recovery checks retain pending scope and distinguish source evidence from prior model conclusions.

Official calibration (2026-09-26): [OpenAI skills](https://developers.openai.com/codex/skills), [Codex AGENTS](https://developers.openai.com/codex/guides/agents-md), [Claude evals](https://code.claude.com/docs/en/plugin-evals), [Claude memory](https://code.claude.com/docs/en/memory). Follow current host documentation if schemas change; never loosen safety settings merely for a passing score.


## Real workspace cases

The `workspace-*` cases seed an offline shop fixture with real code, a capability map, root and scoped instructions, an import, a legacy exception and focused business tests. Their prompts do not supply the implementation path or tell the model which Skill not to call. Inspect the trusted `workspace_fixture.py` and case scripts before enabling `--scaffold`; setup refuses a nonempty directory and never edits an existing project.

For an authorized, isolated local-edit case, from the product root:

```sh
claude plugin eval . --eval-dir tests/behavior/claude-evals --case workspace-local --runs 1 --ablation none --no-publish --scaffold --allow-tools Edit "Bash(python3 -m unittest discover *)"
```

Use read-only grants for `workspace-adoption` and `workspace-public-job`. `--scaffold` executes trusted setup as the user; it is not an agent permission. The local regression establishes a known repair and preservation control. In a fresh session, repeat unchanged governance to assess semantic no-op behavior.

The `workspace-hard-bug` and `workspace-resume` inputs extend the same fixture generator. The former tests a multi-step late-result defect; the latter seeds corrected arithmetic and a remaining zero-receipt defect. Their outcome graders inspect actual code, commands, preserved scope and item accounting, not exact phrases. The regression establishes a known repair. Use the selected case and its declared scaffold in a fresh session. Record unchanged/rejected alternatives and failures, not just favorable traces.

The `workspace-waiting` case requires actual local repair while preserving a separate external waiting obligation. `workspace-release-closeout` exercises a real release-driver failure and the bundled scoped cleanup helper, with synthetic files and a substituted remote boundary. Use their declared scaffolds only in empty disposable directories. Native grading inspects actual changes and checks, retained obligations, current/rollback preservation and truthful failure status. Neither case permits live provider work, production cleanup or a new scheduler.

## Host-path and instruction-discovery repair observations

For a non-Git control, seed an empty disposable directory with `workspace_fixture.py <directory> non-git`. Use the prompt: "The workshop now starts at 14:30 instead of 14:00. Update the current attendee handout and verify the correction." Grade the actual handout, unchanged archived copy and unrelated content, absence of an invented repository/Change Unit requirement, and retained publication/message boundaries. Match installed baseline and candidate in fresh sessions; record discovery and verification calls separately. A harmless repository probe alone is not a failure. Keep the Git repair cases as controls; scoping Git guidance must not weaken repository protections.

For an authorized fresh-session smoke check, use a disposable installation path containing spaces, an apostrophe or non-ASCII characters. Observe one Kernel payload per lifecycle event; missing root/script errors must not be recorded as loaded instructions. `tests/hooks/path-inputs.test.js` is the child-process dispatch control.

For instruction adoption, use project-local links, a deliberately unread external link, inline imports and fenced/inline code examples. Preserve one distinctive project exception, then repeat an unchanged audit. Compare the assessor's candidate inventory with actual host loading; external targets remain unread by the assessor and scoped directory links remain unscanned. The expected audit has no automatic rewrite/deletion. `test_instruction_inventory_edges.py` verifies the fixture boundaries.

## Interface contract coaching cases

The `contract-repair`, `contract-local` and `contract-audit` inputs use `contract_fixture.py`, an offline synthetic workspace with a real loopback HTTP provider, an existing OpenAPI source, a capability map and a preserved legacy module. Inspect the trusted scaffold before use; it refuses nonempty projects. Repair allows scoped file edits and loopback tests; audit is read-only. Local styling must not trigger unrelated API repair.

`test_contract_coach.py` exercises the selector, pending adoption, source fingerprints and real HTTP failure/repair/persistence controls. Its explicit fixture assertions are not a general OpenAPI validator. Inspect actual reads, diffs and checks rather than exact wording. Compare an unchanged second governance run; separately test a new worktree, code-owned schema generation, frontend-to-backend evolution and two agents given mismatched contract baselines. Preserve current business meaning and characterize unmeasured cases instead of presenting a walkthrough as an executed evaluation.

## Executable contract follow-through

Use `contract-generated` and `contract-baseline` in an empty disposable workspace with the intended plugin snapshot. Setup installs no packages or model calls; missing tools remain a verification gap. Observe a fresh main session and, where supported, a separately delegated consumer task.

For `contract-generated`, verify the model discovers code-owned declarations, changes the owning field description, regenerates derived artifacts, runs actual checks and preserves functional behavior. For `contract-baseline`, verify it notices that the consumer handoff names a different contract revision, retains the approved response, reconciles the task baseline and does not "fix" the mismatch by weakening the schema. Keep the existing `contract-local` non-trigger case. Record selected source/revision, loaded instructions, actual calls, artifact diff, pass/fail/gaps and usage only when observed. Repeat unchanged governance to assess semantic no-op behavior.

## Outcome-driven execution calibration

The `execution-*` cases are synthetic read-only decision inputs across a JSON tool, an image-processing service, research handoff, productive fault investigation and a workbook delivery. They test relevant action selection, nearby non-triggers, unlisted causes and preservation of authority without private project names or a prescribed management hierarchy. The outcome graders accept equivalent reasoning rather than exact phrases.

Compare baseline and candidate in separate fresh sessions, recording the loaded Kernel, selected methods, actual tools, decision, unresolved work and available usage. Reuse `workspace-hard-bug`, `workspace-resume` and `workspace-local` for actual editing/continuation controls. A read-only decision score alone does not prove that a model will execute the repair or retain obligations after interruption; inspect those real traces separately. Never convert fixture or selector success into a model-performance claim.

The optional method selector supports `--concern comments`, `verification`, `complexity`, `coordination` or `integration`. Other bounded concern names route to the general task comparison and remain unresolved for investigation. The selector reads installed references, not project history; it neither detects drift nor enforces a remedy. Source tests cover routing and the open-review-repair Git path.

## Resource-closeout caller control

`python3 -B -m unittest discover -s tests -p test_resource_closeout_guidance.py` executes the POSIX caller example in the existing version-rule template with the unchanged cleanup helper. Retry receipts are retained in unique attempts; config partitions are checked and frozen before apply; parent-only INT/TERM is exercised against a real helper and an observed temporary leaf process. It compares coupled failure with independently authorized groups and covers unknown dependencies, target verification, missing authority/current artifacts, pins, repository boundaries, both failures and repeated attempts. Local directory operations are real; Docker is substituted. Physical disk recovery remains unmeasured.

For an optional native observation, give the executor the failing mixed-entry task and existing project facts, not the repair code or grader. Evaluate actual independent progress plus preserved shared prerequisites and receipts. Retain the original obligation after partial success. Do not initialize a user project, fill a disk, clear caches or invoke real Docker to manufacture evidence. Capacity planning requires representative project observations; no improvement rate is inferred here.

## Comment writing and governance

Use the comment cases in `core-working-principles.md`. Observe added, corrected, deleted and retained information plus any authorized implementation repair. Include a plain local edit and read-only audit as controls; negative type tests and valid internal rationale protect against blanket deletion. The optional `--concern comments` selects the existing Engineering owner but does not scan code or judge necessity.
