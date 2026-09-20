# Project Standard Discovery and Conditional Loading

Find effective project rules and read only what the task needs. Do not create a separate knowledge base or promote unadopted preferences, incidental style or chat impressions into standards.

## Contents

[Discovery](#3-discovery-process) · [Index](#4-index-contract) · [Loading](#5-conditional-loading) · [Verification](#6-verify-routing) · [Maintenance](#8-project-instruction-maintenance)

## 1. Two Different Artifacts

- **Authoritative standard:** complete project-specific rules, rationale, exceptions, and verification in existing owners such as CONTRIBUTING, CODE_QUALITY, ARCHITECTURE, TESTING_STRATEGY, WORKFLOW, DEPLOYMENT, or tool configuration. Under BuildOS, root `AGENTS.md` is a working-agreement and project-difference/router entrypoint, not an owner of complete domain manuals. Concise adopted shared principles are allowed; project uniqueness is not required for a useful working agreement.
- **Standards index:** domain, trigger, one-sentence decision summary, and authoritative path for fast selection. It does not copy the standard.

Use `governance/PROJECT_MAP.md` for a new standard/release project, or map its existing equivalent. Add no parallel index. Core projects may route directly through AGENTS, README, a charter or configuration.

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
4. Apply two admission tests. Durable agent instructions must be non-obvious, project-specific, repeatedly needed, or catastrophic if violated once. Current engineering constraints need only be valid, stable, implementation-relevant, and verifiable; prior failure is unnecessary. Exclude unadopted personal preferences, one-off task context, and unconfirmed judgment. Explicitly adopted team working principles follow the authoring contract below; do not reject them merely because they are reusable across projects.
5. Retain evidence paths and distinguish formal rule, stable practice, candidate, legacy, and incidental style. A mixed file may remain physically intact when section responsibilities and current/history boundaries are clear. If classification is uncertain, report a candidate; keyword scripts do not migrate it.
6. Ask one concrete owner question only when rationale/exception changes behavior and evidence cannot resolve it.
7. After write authority, update the original domain owner. Select the closest existing document/configuration only when no owner exists; do not default to a new directory.
8. Add a short index route. Never present an unconfirmed candidate as mandatory.

For established `AGENTS.md`, retain approved project facts, actual commands, authority routes, concise adopted constraints and explicit overrides. Compress a rule to a route when its complete owner remains available to ordinary execution. Remove a duplicate body only after preserving its authoritative meaning and a usable consumer path; matching BuildOS wording does not cancel an adopted project contract. Reconcile stale/conflicting content from current owners and authorized superseding decisions. Ask only for an unresolved material choice. Never cover an existing entrypoint with a fresh BuildOS template or create a parallel instruction file.

Engineering owns code-evidence discovery; each specialist decides its domain rules.

## 4. Index Contract

Reuse the project's existing navigation. `governance/PROJECT_MAP.md` is the standard/release default; a core project may use a short README or equivalent. Index capabilities and owning modules, not every file or function. Ordinary new files inherit a known module's ownership. Large modules may link existing local documentation; do not create a second catalog or require every task to read the full map.

For each capability in the declared governance scope, make these facts discoverable: a recognizable purpose and owner; the real implementation entrypoint; the applicable rule/contract; and the relevant verification entrypoint. Retain state-source and delivery-unit boundaries where applicable. Reuse an existing check or documented observation; mark missing or unverified facts honestly. Planned modules have no verified implementation yet. Source/configuration shows observed behavior, while approved contracts define the target.

Navigation adoption also checks that ordinary execution can reach a sufficient engineering baseline for the selected stack and affected risks. Use the existing CODE_QUALITY, technical owner, framework configuration, representative implementation and verification entrypoint; repair a missing or contradictory local constraint within governance authority. A list of installed Skills or a link to unrelated guidance is not that baseline. Keep only useful adopted project constraints and conditional routes, not a copy of every language profile or a mandatory per-module checklist.

Build routes from current code and project owners during initialization or authorized established-project governance. An initializer produces a draft, not semantic acceptance. Follow the governed routes to actual implementation, applicable requirements and a relevant test/command definition. Run the smallest useful check only when available and authorized; otherwise record the limit. A valid path proves reachability, not that it serves the claimed capability. Declared scope must be covered or explicitly left unassessed; do not claim whole-project governance from an undisclosed sample.

The implementer maintains affected navigation in the same authorized change when module responsibility, public/implementation entrypoint, contract location or verification entrypoint changes. If none changes, leave navigation alone. Update the actual owner before its route. Existing review checks the affected route against the receiving worktree and baseline; no new supervisor, per-edit form or whole-map gate is required. If write authority excludes the needed navigation update, report that specific remaining action.

Keep standards-index entries distinct from full rules: domain, trigger, one-sentence decision summary, authoritative path, status and relevant calibration identity/date. Use project-root-relative code paths or map-relative Markdown links. Preserve meaningful paths and roles; do not copy source code, whole tool configurations or dynamic task state into the map. Generated symbol indexes are disposable retrieval aids, not approved project policy, and must be refreshed for the current worktree when stale.

Several triggers may share an owner; merge identical rows. Validators prove declared reachability, boundaries and structure, not semantic correctness, freshness or complete project coverage. Keep structural defects as errors and duplicate/unverified entries as warnings under the existing output contract. A script does not create a CI gate.


## 5. Conditional Loading

1. Apply the host's effective in-scope instructions. Go directly to a known implementation location; when location is unclear, select one shortest useful router such as the relevant README or Project Map entry. Do not preload README, maps, architecture, release records and worktree registers as a universal chain.
2. Select the minimum rules from current signals. Read baseline/release owners for version, candidate, release, production identity, or rollback; Git/worktree owners for branches, parallel directories, or implementation baseline; specialist owners for identity, billing, safety, or domain signals.
3. Project `AGENTS.md` may contain project triggers/routes, not a catalog of every installed skill or a generic handoff process. Handoff to Workflow only when a real business agent, process contract, or run state is the subject.
4. Load only the applicable sections needed for the current decision. Clear project rules permit ordinary execution without reopening Project governance. Use the matching specialist guidance for an actual gap, conflict, contract change, requested review or explicit governance task; the complete user outcome remains in scope.
5. A `candidate` prompts investigation, never a gate; `legacy` supports compatibility, migration, or history only.
6. User instructions take precedence over Skill defaults within host permissions. Resolve freshness and apparent conflicts through current owners, runtime evidence, and explicit superseding user decisions before asking. Project overrides beat generic defaults; factual checks such as confirming a Git root are agent verification, not approval requests. Continue covered work and ask only for an unresolved outcome-changing choice or uncovered authority. Preserve explicit access, cost, production, destructive-action, and independent-review gates.

Do not turn an audit-only request into implementation. An explicit audit-and-optimize request authorizes the scoped fixes after assessment; it does not require a second generic approval. Before requesting missing authority, finish independent authorized work and present the concrete remaining action. If a Skill instruction actually blocks or redirects requested work, link the exact SKILL.md/reference, quote that instruction, and distinguish its requirement from interpretation.

Audit effective nested AGENTS/overrides and active worktree entrypoints, not just the top-level file. Exclude historical, third-party and generated copies from automatic rewriting; reconcile stale routes against registered owners. Do not assume changing directories hot-loads another repository's instructions: read its entrypoint when entering it.

## 6. Verify Routing

Distinguish preparation, semantic route validation and actual model behavior. Links and validators establish structural preparation. Following a capability route through current code, the applicable contract and the relevant check establishes a scoped semantic observation. Neither alone proves that a new session loads it automatically or that Token use falls.

For a navigation/source correction, inspect the ordinary local task, relevant specialist boundary and release/rollback exception as applicable to the changed scope. Use current host loading behavior and actual generated entrypoints; do not require a paid A/B competition or new session experiment merely to finish bounded source work. Preserve separately approved safety and release checks.

If actual session behavior or a reduction is claimed, obtain corresponding observations under available authority and disclose the compared scope, loaded sources and limits. Missing runtime access leaves that claim unverified; it is not permission to fabricate evidence or to reopen every unrelated document.


## 7. Completion

Discovery is complete only when evidence/scope are clear; each full rule is in one domain owner or remains an explicit candidate; the short index routes future agents; duplicate, stale, and legacy entrypoints are labeled; and no external example, preference, or one-off state masquerades as a durable standard.

When multiple installed copies expose the same skill, identify the host-selected source and revision before claiming a rule update is active. Source commits, installed snapshots, and already-running sessions are separate states. Repair the owning source; use its authorized install lifecycle rather than editing caches or silently removing another host's installation.


## 8. Project Instruction Maintenance

BuildOS owns the method; each project owns its effective instructions and standards. Review on initial adoption, an instruction-affecting BuildOS upgrade, changes to roots, commands, technical baselines or owners, a verified routing gap, or stale/conflicting effective instructions. Project owns the instruction chain; specialists own domain rules; Learning owns experience classification. Ordinary task completion and one-off model errors do not append instructions. Ordinary implementation reads its applicable entrypoint and continues; it does not trigger a project-wide governance audit.

Run `assess_project_governance.py --root <project>` for a read-only inventory of root/nested AGENTS, Codex overrides, CLAUDE/CLAUDE.local and `.claude/rules` candidates, scope, and content fingerprints. Inspect coverage limits and separately assess the registered active worktree; excluded copies are not current authority. Compare changed paths/fingerprints with the prior assessment or Git revision in the existing task owner. A hash change locates review work; it does not establish a defect or effective host precedence. Inspect host/global and ancestor instructions, configured fallback files, nested AGENTS/overrides and referenced owners as needed. Reading their influence does not authorize changing user-global instructions or host configuration. Legitimate nested and override scopes remain supported.

When establishing or repairing instructions, distinguish files found from files confirmed loaded by the selected host. Keep one authoritative body for shared rules. Prefer native loading when available; otherwise use an explicit relative import in the existing host entrypoint, preserving host-specific content and user settings. Claude may prefer project CLAUDE/CLAUDE.local files over AGENTS and does not adopt Codex override semantics. Confirm scope and actual loading before claiming compatibility; do not rewrite files at session start, duplicate whole rulebooks, or change global/privacy settings. Claude-specific activation details live in the adapter's [guide](../../../adapters/claude-code/README.md).

For a project that actually releases managed artifacts, adoption/governance also verifies the existing release driver's cleanup call, per-target identity/retention configuration and truthful outcome under Delivery's [retention contract](../../senmu-build-delivery/references/version-artifacts-and-release.md#4-retention-and-cleanup). Resolve missing wiring in that project under write authority; the initializer's files alone are not an operational release workflow. A source-only project does not acquire invented Docker or server tasks.

History belongs in Git; do not create AGENTS.new/old/v2/optimized/backup files or another same-purpose instruction reference. For verified rework, repeated failure or owner correction, classify through [Organizational Learning](../../senmu-build-learning/references/organizational-learning-and-governance-closure.md#3-root-cause-classification); repair only within write authority. Add a short route only when future task entry needs the stable project fact.

Reconcile affected instructions in place: remove stale dynamic state, route to its owner, preserve business constraints and explicit overrides, and eliminate conflicting test/permission defaults in referenced policies as well as AGENTS. For an upgrade with no relevant instruction changes, record no migration needed; never rewrite every project to match a template. During merge/promotion, review instruction diffs against the receiving baseline so an older branch cannot silently restore retired rules.

Use one model-neutral contract for scope, autonomy, reuse, and evidence across supported models. Keep model-specific runtime settings in the host adapter; official prompt examples are tunable guidance, not an instruction to copy every example into every project. Record source/installed revision, affected owners, verification and unresolved behavior in the existing task/log. Do not create a second governance ledger, mandatory nightly job, or universal CI gate. Review the affected routing scenarios under section 6; distinguish source/route verification from any still-unverified fresh-session behavior.

<a id="dual-track-instruction-authoring"></a>
### Dual-Track Instruction Authoring

For instruction initialization or improvement, follow [Instruction Authoring](project-instruction-authoring.md): reconcile existing instructions and adopt applicable shared working principles in the project language. Preserve approved exceptions; repeated governance of unchanged facts should not grow the entrypoint.

### Specialist Coordination and Task Evidence

Project repairs routing and ownership; it does not require every specialist to approve every task. On an affected governance change, resolve only the relevant boundary:

| Owner | Concrete contribution | Project checks |
| --- | --- | --- |
| Product | Approved behavior, acceptance, unfinished scope | Implementation choices cannot silently supersede these facts |
| Engineering | Existing component/service owner, shared state/request logic, SDK/adapter boundary, focused tests | The route reaches actual code/configuration, not only a prose instruction to reuse |
| Design | Project theme/token entrypoint, representative composition, affected viewport/state expectations | Correct token use and good rendered UI are separate claims |
| Delivery | Receiving baseline, open batch, candidate identity, reusable verification and release boundary | Instruction changes survive integration; local checks do not invent deployment facts |

For the scoped governance outcome, follow a real project entrypoint to its implementation, current contract and relevant check; execute only available checks within authority. Record the exact observation and remaining uncertainty in the existing task. Hypothetical scenarios support semantic review, not a claim of executed model behavior. Comparative reading, testing, time or cost claims need comparable observations. Do not create a per-action scorecard, universal routing experiment or second ledger.
