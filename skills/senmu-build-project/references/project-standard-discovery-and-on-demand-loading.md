# Project Standard Discovery and Conditional Loading

Use this standard to find effective rules in an established project and load only what the current task needs. It does not create a BuildOS-private project knowledge base or promote personal preference, incidental style, or chat impressions into standards.

## 1. Two Different Artifacts

- **Authoritative standard:** complete project-specific rules, rationale, exceptions, and verification in existing owners such as CONTRIBUTING, CODE_QUALITY, ARCHITECTURE, TESTING_STRATEGY, WORKFLOW, DEPLOYMENT, or tool configuration. Under BuildOS, root `AGENTS.md` is a project-difference/router entrypoint, not a domain-standard owner.
- **Standards index:** domain, trigger, one-sentence decision summary, and authoritative path for fast selection. It does not copy the standard.

`governance/PROJECT_MAP.md` is the BuildOS standard/release default index. Map an established equivalent instead of adding `standards/`, `rules/`, or another Project Map. A core project may route directly from a short AGENTS, README, charter, and tool configuration.

## 2. When Discovery Is Needed

- Taking over an existing codebase, workflow, content system, or composite project.
- Scattered rules cause repeated questions, convention violations, or wrong entrypoints.
- Documents may have drifted from actual implementation.
- BuildOS initialization/governance applicability is unclear.
- Repeated tasks depend on a few project constraints but require full searches each time.

Skip full discovery when an ordinary task can already find clear rules from project entrypoints.

## 3. Discovery Process

1. Confirm project root, target release/delivery unit, task scope, and read/write authority.
2. Read short entrypoints and existing owners, then representative implementation, configuration, tests, runtime, or delivery evidence. Do not scan the entire repository for false certainty.
3. Route each actual constraint by meaning, not filename, `spec`, or keywords:
   - agent behavior and conditional reading -> project `AGENTS.md` or equivalent router;
   - current interface, safety, compatibility, data, quality, or runtime invariants -> Engineering/current engineering owner;
   - user/business outcome, scope, acceptance, product decision -> Product;
   - architecture, implementation path, tradeoff, rationale -> design/decision owner; update the current engineering constraint when it changes without copying full history;
   - workflow, delivery, task state, release fact, learning evidence -> Workflow, Delivery, Durable Task State, or Learning respectively.
4. Apply two admission tests. Durable agent instructions must be non-obvious, project-specific, repeatedly needed, or catastrophic if violated once. Current engineering constraints need only be valid, stable, implementation-relevant, and verifiable; prior failure is unnecessary. Exclude preferences, one-off task context, and unconfirmed judgment.
5. Retain evidence paths and distinguish formal rule, stable practice, candidate, legacy, and incidental style. A mixed file may remain physically intact when section responsibilities and current/history boundaries are clear. If classification is uncertain, report a candidate; keyword scripts do not migrate it.
6. Ask one concrete owner question only when rationale/exception changes behavior and evidence cannot resolve it.
7. After write authority, update the original domain owner. Select the closest existing document/configuration only when no owner exists; do not default to a new directory.
8. Add a short index route. Never present an unconfirmed candidate as mandatory.

For established `AGENTS.md`, decide per instruction: project facts, actual commands, authority paths, explicit overrides -> `retain`; project-specific text already owned elsewhere -> `compress_to_route`; BuildOS-generic duplicates -> `remove_duplicate`; conflict/staleness -> `reconcile_from_authority`; use `conflict_for_user_decision` only for a material decision that current evidence and existing authority cannot resolve. Never layer a BuildOS template over the old entrypoint first.

Engineering's project-standard discovery reference owns code-evidence methods. Product, Workflow, Delivery, and Learning decide their own domain rules.

## 4. Index Contract

Each entry states domain, trigger, affected decision, authoritative rule/configuration path, status (`active`, `candidate`, `legacy`, `retired`), and last calibration. The one-sentence summary selects content; it cannot replace execution of the full standard. Update the authority first, then the index.

Several triggers may point to one authority; identical entries are noise and should merge. In a BuildOS Project Map, use project-root-relative code paths or map-relative Markdown links for active entries. Validators establish declared reachability, boundary, and structural integrity only; they neither require every Markdown file in the index nor prove semantic correctness, consistency, or freshness.

Reserve validator errors for deterministic structural defects and warnings for exact duplicate entries or active paths requiring human verification. Warnings do not change the compliant exit code. `--json` returns stable `code`, `path`, `message`, `severity`, and counts. Approve CI or another persistent execution point according to project risk; script existence is not an active gate.

## 5. Conditional Loading

1. Codex already loads in-scope `AGENTS.md`. Select one shortest additional project router only when module/delivery unit is unresolved. Do not make README, maps, architecture, baselines, release records, and worktree registers a universal preflight chain.
2. Select the minimum rules from current signals. Read baseline/release owners for version, candidate, release, production identity, or rollback; Git/worktree owners for branches, parallel directories, or implementation baseline; specialist owners for identity, billing, safety, or domain signals.
3. Project `AGENTS.md` may contain project triggers/routes, not a catalog of every installed skill or a generic handoff process. Handoff to Workflow only when a real business agent, process contract, or run state is the subject.
4. Stop when active project standards answer the task. Read the necessary reference from one domain skill only for a gap, conflict, governance evolution, or explicit BuildOS request.
5. A `candidate` prompts investigation, never a gate; `legacy` supports compatibility, migration, or history only.
6. User instructions take precedence over Skill defaults within host permissions. Resolve freshness and apparent conflicts through current owners, runtime evidence, and explicit superseding user decisions before asking. Project overrides beat generic defaults; factual checks such as confirming a Git root are agent verification, not approval requests. Continue covered work and ask only for an unresolved outcome-changing choice or uncovered authority. Preserve explicit access, cost, production, destructive-action, and independent-review gates.

Do not turn an audit-only request into implementation. An explicit audit-and-optimize request authorizes the scoped fixes after assessment; it does not require a second generic approval. Before requesting missing authority, finish independent authorized work and present the concrete remaining action. If a Skill instruction actually blocks or redirects requested work, link the exact SKILL.md/reference, quote that instruction, and distinguish its requirement from interpretation.

Audit effective nested AGENTS/overrides and active worktree entrypoints, not just the top-level file. Exclude historical, third-party and generated copies from automatic rewriting; reconcile stale routes against registered owners. Do not assume changing directories hot-loads another repository's instructions: read its entrypoint when entering it.

## 6. Verify Routing

Existing paths, valid Markdown links, clean assessor output, and template validation prove structural preparation only. When the objective includes actual routing or context reduction, use fresh sessions to test at least:

- a low-risk single-unit task: direct owner, no global baseline/release/worktree/Project/Workflow load;
- a specialist-boundary task: applicable contract/baseline, no unrelated domains;
- release/rollback: candidate identity, release unit, authority, production evidence, recovery.

Without this independent behavior check, report at most `structural_routing_prepared` and list unverified behavior.

## 7. Completion

Discovery is complete only when evidence/scope are clear; each full rule is in one domain owner or remains an explicit candidate; the short index routes future agents; duplicate, stale, and legacy entrypoints are labeled; and no external example, preference, or one-off state masquerades as a durable standard.

When multiple installed copies expose the same skill, identify the host-selected source and revision before claiming a rule update is active. Source commits, installed snapshots, and already-running sessions are separate states. Repair the owning source; use its authorized install lifecycle rather than editing caches or silently removing another host's installation.


## 8. Project Instruction Maintenance

BuildOS owns the method; each project owns its effective instructions and standards. Review on initial adoption, an instruction-affecting BuildOS upgrade, changes to roots, commands, technical baselines or owners, a verified routing gap, or stale/conflicting effective instructions. Project owns the instruction chain; specialists own domain rules; Learning owns experience classification. Ordinary task completion and one-off model errors do not append instructions. Ordinary implementation reads its applicable entrypoint and continues; it does not trigger a project-wide governance audit.

Run `assess_project_governance.py --root <project>` for a read-only inventory of root/nested AGENTS and overrides, scope, and content fingerprints. Inspect coverage limits and separately assess the registered active worktree; excluded copies are not current authority. Compare changed paths/fingerprints with the prior assessment or Git revision in the existing task owner. A hash change locates review work; it does not establish a defect or effective host precedence. Inspect host/global and ancestor instructions, configured fallback files, nested AGENTS/overrides and referenced owners as needed. Reading their influence does not authorize changing user-global instructions or host configuration. Legitimate nested and override scopes remain supported.

History belongs in Git; do not create AGENTS.new/old/v2/optimized/backup files or another same-purpose instruction reference. For verified rework, repeated failure or owner correction, classify through [Organizational Learning](../../senmu-build-learning/references/organizational-learning-and-governance-closure.md#3-root-cause-classification); repair only within write authority. Add a short route only when future task entry needs the stable project fact.

Reconcile affected instructions in place: remove stale dynamic state, route to its owner, preserve business constraints and explicit overrides, and eliminate conflicting test/permission defaults in referenced policies as well as AGENTS. For an upgrade with no relevant instruction changes, record no migration needed; never rewrite every project to match a template. During merge/promotion, review instruction diffs against the receiving baseline so an older branch cannot silently restore retired rules.

Use one model-neutral contract for scope, autonomy, reuse, and evidence across supported models. Keep model-specific runtime settings in the host adapter; official prompt examples are tunable guidance, not an instruction to copy every example into every project. Record source/installed revision, affected owners, verification and unresolved behavior in the existing task/log. Do not create a second governance ledger, mandatory nightly job, or universal CI gate. Recheck the three routing scenarios when routing behavior changes; source edits alone do not prove a running session adopted them.


### Specialist Coordination and Task Evidence

Project repairs routing and ownership; it does not require every specialist to approve every task. On an affected governance change, resolve only the relevant boundary:

| Owner | Concrete contribution | Project checks |
| --- | --- | --- |
| Product | Approved behavior, acceptance, unfinished scope | Implementation choices cannot silently supersede these facts |
| Engineering | Existing component/service owner, shared state/request logic, SDK/adapter boundary, focused tests | The route reaches actual code/configuration, not only a prose instruction to reuse |
| Design | Project theme/token entrypoint, representative composition, affected viewport/state expectations | Correct token use and good rendered UI are separate claims |
| Delivery | Receiving baseline, open batch, candidate identity, reusable verification and release boundary | Instruction changes survive integration; local checks do not invent deployment facts |

Validate with a bounded real project task: trace its entrypoint to the actual implementation and existing acceptance, execute the smallest relevant available check, and record what was read/run, the observable result, and uncovered boundaries. A hypothetical plan is a routing probe, not an executed task. To claim reduced reading, testing, time or cost, compare equivalent task/scope evidence; otherwise report only the observed execution footprint. Keep this evidence in the current task owner, not a permanent per-action scorecard. Source behavior, rendered quality and production success each require their own relevant evidence.
