# Project Standard Discovery and Conditional Loading

Find effective project rules and read only what the task needs. Do not create a separate knowledge base or promote unadopted preferences, incidental style or chat impressions into standards.

## Contents

[Discovery](#3-discovery-process) · [Index](#4-index-contract) · [Loading](#5-conditional-loading) · [Verification](#6-verify-routing) · [Maintenance](#8-project-instruction-maintenance)

## 1. Two Different Artifacts

- **Authoritative standard:** full rules, rationale, exceptions and verification at the domain owner. Persistent UI uses `design/UI_SPECIFICATION.md`; other examples include CONTRIBUTING, CODE_QUALITY, ARCHITECTURE, TESTING_STRATEGY, WORKFLOW, DEPLOYMENT and tool configuration. Root `AGENTS.md` holds working agreements and routes, including useful shared principles, not full domain manuals.
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
   - technical interfaces, safety, compatibility, data, quality or runtime invariants -> Engineering;
   - user/business outcome, scope, acceptance, product decision -> Product;
   - visual/interaction rules, responsive behavior and accessibility -> Design/current UI specification;
   - architecture, implementation path, tradeoff or rationale -> Engineering's technical decision owner; update current constraints without copying history;
   - workflow, delivery, task state, release fact, learning evidence -> Workflow, Delivery, Durable Task State, or Learning respectively.
4. Apply two admission tests. Durable agent instructions must be non-obvious, project-specific, repeatedly needed or catastrophic if violated once. Current engineering constraints need only be valid, stable, implementation-relevant, and verifiable; prior failure is unnecessary. Exclude unadopted preferences, task-only context and unconfirmed judgment. Adopted shared principles follow the authoring contract even when reusable.
5. Retain evidence paths and distinguish formal rules, stable practice, candidates, legacy and incidental style. Identify section responsibilities in mixed files; during UI standardization, extract current UI rules to the standard entry and retire the old authority. Uncertain classifications stay candidates; keyword scripts do not migrate them.
6. Ask one concrete owner question only when rationale/exception changes behavior and evidence cannot resolve it.
7. Within write authority, update the domain owner or complete its required standard migration. Where no fixed standard applies, prefer a suitable existing document/configuration over a new directory.
8. Add a short index route. Never present an unconfirmed candidate as mandatory.

Preserve approved facts, commands, exceptions and scoped overrides in AGENTS. Replace duplicate bodies only after their adopted meaning is reachable at the domain owner. Resolve conflicts from current facts and authorized decisions; ask only for material missing choices. Templates never overwrite established instructions.

Engineering owns code-evidence discovery; each specialist decides its domain rules.

## 4. Index Contract

Reuse the project's existing navigation. `governance/PROJECT_MAP.md` is the standard/release default; a core project may use a short README or equivalent. Index capabilities and owning modules, not every file or function. Ordinary new files inherit a known module's ownership. Large modules may link existing local documentation; do not create a second catalog or require every task to read the full map.

For each governed capability, expose its purpose, owner, real implementation, applicable contract and verification entrypoint. Retain relevant state and delivery boundaries. Link effective design reasons through the same contract route without copying history. Reuse existing checks; mark missing or unverified facts. Planned modules have no verified implementation. Code shows behavior, not requirement authority.

Check that ordinary execution reaches the adopted stack/quality baseline, representative implementation and verification. Repair missing or conflicting local constraints within authority; a Skill catalog is no engineering baseline. Keep useful project constraints and conditional routes rather than copied profiles or per-module checklists.

During initialization or authorized governance, follow each governed route to current implementation, requirements and a relevant check. Run the smallest useful authorized check or record its limit. Generated drafts and valid paths prove no semantic acceptance. Cover declared scope or explicitly leave it unassessed; disclose sampling.

Update navigation in the same authorized change when responsibility, implementation, contract location or checks move; otherwise leave it alone. Update the owner first. Existing review checks affected routes at the receiving baseline, without a supervisor or whole-map gate. Report any necessary navigation outside write authority.

Index domain, trigger, short decision summary, authority path, status and calibration identity/date. Use project-relative code paths and map-relative links, not copied code, configurations or task state. Generated symbol indexes are disposable retrieval aids; refresh stale ones for the current worktree.

Use [Task Entry](task-entry-and-maintenance-economy.md) for selective lookup and real route verification, not claimed adoption or savings.

Several triggers may share an owner; merge identical rows. Validators prove declared reachability, boundaries and structure, not semantic correctness, freshness or complete project coverage. Keep structural defects as errors and duplicate/unverified entries as warnings under the existing output contract. A script does not create a CI gate.


## 5. Conditional Loading

1. Apply the host's effective in-scope instructions. Go directly to a known implementation location; when location is unclear, select one shortest useful router such as the relevant README or Project Map entry. Do not preload README, maps, architecture, release records and worktree registers as a universal chain.
2. Select the minimum rules from current signals. Read baseline/release owners for version, candidate, release, production identity, or rollback; Git/worktree owners for branches, parallel directories, or implementation baseline; specialist owners for identity, billing, safety, or domain signals.
3. Project `AGENTS.md` maps tasks to Skills and project owners/commands, not an installed Skill catalog or generic handoff process. Release/recovery follows that route; files alone do not prove adoption. Handoff to Workflow only for a real business agent, process contract, or run state.
4. Load only the applicable sections needed for the current decision. Clear project rules permit ordinary execution without reopening Project governance. Use the matching specialist guidance for an actual gap, conflict, contract change, requested review or explicit governance task; the complete user outcome remains in scope.
5. A `candidate` prompts investigation, never a gate; `legacy` supports compatibility, migration, or history only.
6. User instructions take precedence over Skill defaults within host permissions. Resolve freshness and apparent conflicts through current owners, runtime evidence, and explicit superseding user decisions before asking. Project overrides beat generic defaults; factual checks such as confirming a Git root are agent verification, not approval requests. Continue covered work and ask only for an unresolved outcome-changing choice or uncovered authority. Preserve explicit access, cost, production, destructive-action, and independent-review gates.

Do not turn an audit-only request into implementation. An explicit audit-and-optimize request authorizes the scoped fixes after assessment; it does not require a second generic approval. Before requesting missing authority, finish independent authorized work and present the concrete remaining action. If a Skill instruction actually blocks or redirects requested work, link the exact SKILL.md/reference, quote that instruction, and distinguish its requirement from interpretation.

Audit effective nested AGENTS/overrides and active worktree entrypoints, not just the top-level file. Exclude historical, third-party and generated copies from automatic rewriting; reconcile stale routes against registered owners. Do not assume changing directories hot-loads another repository's instructions: read its entrypoint when entering it.

## 6. Verify Routing

Distinguish preparation, semantic route validation and actual model behavior. Links and validators establish structural preparation. Following a capability route through current code, the applicable contract and the relevant check establishes a scoped semantic observation. Neither alone proves that a new session loads it automatically or that Token use falls.

Review changed navigation using ordinary tasks, specialist boundaries and release/recovery exceptions. Trace requirements, reasons, code and matching checks; include local non-triggers and changed historical conditions. Inspect generated entrypoints and host semantics. Preserve safety/release checks; bounded source work requires no paid A/B test.

Trace release adoption from project entry through Skill, procedure, runner and actual verification/closeout. Test interruption without redeployment and ordinary local non-triggers. Use realistic tasks and disposable resources, without supplying graders. A helper-only test is not adoption. Record observations in the existing task.

For behavior or savings claims, record actual inputs, loaded sources, actions, artifacts and limits under available authority. Include implicit UI requests and adjacent non-triggers; mentioning Design is not loading it. Missing runtime access leaves behavior unverified.


## 7. Completion

Discovery is complete only when evidence/scope are clear; each full rule is in one domain owner or remains an explicit candidate; the short index routes future agents; duplicate, stale, and legacy entrypoints are labeled; and no external example, preference, or one-off state masquerades as a durable standard.

When multiple installed copies expose the same skill, identify the host-selected source and revision before claiming a rule update is active. Source commits, installed snapshots, and already-running sessions are separate states. Repair the owning source; use its authorized install lifecycle rather than editing caches or silently removing another host's installation.


## 8. Project Instruction Maintenance

BuildOS owns methods; projects own effective instructions. Review on adoption, relevant upgrades, changed roots/commands/baselines/owners, verified routing gaps or stale/conflicting instructions. Project owns the chain, specialists their rules, Learning experience classification. Routine completion or a one-off error adds no instructions or whole-project audit.

Run `assess_project_governance.py --root <project>` for a read-only inventory of root/nested AGENTS, Codex overrides, CLAUDE/CLAUDE.local and `.claude/rules`, with scope and fingerprints. Inspect coverage limits and the registered active worktree; excluded copies have no current authority. Compare changed paths/fingerprints with prior evidence in the existing task. A hash locates review work, not defects or host precedence. Inspect relevant host/global, ancestor, fallback and nested rules without changing user-global instructions or host configuration. Preserve legitimate scoped overrides.

Distinguish files found from rules actually loaded by the host. Keep one shared body; prefer native loading, otherwise a relative import in the existing entrypoint, preserving host content and settings. Claude may prefer CLAUDE/CLAUDE.local over AGENTS and does not adopt Codex override semantics; see its [guide](../../../adapters/claude-code/README.md). Verify scope/loading before claiming compatibility. Do not rewrite on session start, duplicate rulebooks or change global/privacy settings.

For managed releases, verify the release driver's cleanup call, target identity, retention and truthful outcome under Delivery's [retention contract](../../senmu-build-delivery/references/version-artifacts-and-release.md#4-retention-and-cleanup). Repair missing wiring within authority; initializer files prove no operational workflow. Source-only projects acquire no Docker/server tasks.

History belongs in Git; do not create AGENTS.new/old/v2/optimized/backup files or another same-purpose instruction reference. For verified rework, repeated failure or owner correction, classify through [Organizational Learning](../../senmu-build-learning/references/organizational-learning-and-governance-closure.md#3-root-cause-classification); repair only within write authority. Add a short route only when future task entry needs the stable project fact.

Reconcile affected instructions and referenced policies: route stale state to its owner, preserve business constraints/overrides and resolve conflicting test/permission defaults. An irrelevant upgrade needs no migration. At merge/promotion, compare the receiving baseline so old branches cannot restore retired rules.

Keep one model-neutral contract and host-specific settings in adapters. Prompt examples are guidance. Record source/installed revisions, affected owners, checks and unknown behavior in the existing task; review routing under section 6 without another ledger, scheduled job or universal gate. Source checks prove no fresh-session behavior.

<a id="dual-track-instruction-authoring"></a>
### Dual-Track Instruction Authoring

For instruction initialization or improvement, follow [Instruction Authoring](project-instruction-authoring.md): reconcile existing instructions and adopt applicable shared working principles in the project language. Preserve approved exceptions; repeated governance of unchanged facts should not grow the entrypoint.

### Specialist Coordination and Task Evidence

Project repairs routing and ownership; it does not require every specialist to approve every task. On an affected governance change, resolve only the relevant boundary:

| Owner | Concrete contribution | Project checks |
| --- | --- | --- |
| Product | Approved behavior, acceptance, unfinished scope | Implementation choices cannot silently supersede these facts |
| Engineering | Existing component/service owner, shared state/request logic, SDK/adapter boundary, focused tests | The route reaches actual code/configuration, not only a prose instruction to reuse |
| Design | Standard UI specification, real theme/token/component entries, representative viewport/state expectations | The current rule is reachable; token use, rendered quality and task behavior are separate claims |
| Delivery | Receiving baseline, open batch, candidate identity, reusable verification and release boundary | Instruction changes survive integration; local checks do not invent deployment facts |

Follow the affected entrypoint to real code, its current contract and a relevant check. Run only authorized available checks and record observations and gaps in the existing task. Hypothetical scenarios support source review, not executed model behavior. Comparative cost or performance claims need comparable observations; add no second ledger or universal routing experiment.
