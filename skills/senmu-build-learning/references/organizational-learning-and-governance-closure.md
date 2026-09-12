# Project Retrospectives and Organizational Learning

Use this standard to turn resolved or evidenced project experience into reusable knowledge. When BuildOS itself causes confusion, rework, inefficiency, or poor adoption, first submit an agent-generated candidate under [Feedback Candidates and Central Adjudication](feedback-candidates-and-central-adjudication.md). Ordinary user corrections, business requirements, and project bugs do not enter that inbox. A raw candidate does not trigger a formal retrospective, log, Lessons ID, or validator automatically.

The objective is not more ceremonial reports. Each effective correction should reduce repeated failure by later agents or developers.

## Navigation

1. Triggers; 2. Order; 3. Root-cause classes; 4. Executable contracts; 5. Promotion to lessons; 6. Retrieval and maintenance; 7. Template; 8. Document routing; 9. Prohibitions; 10. Minimum standard.

## 1. Triggers

Enter a lightweight retrospective after the issue is resolved, has reviewable evidence, or the user begins central adjudication when:

- An agent finds and corrects a wrong implementation, test, release, or documentation-sync approach.
- A project owner identifies a deviation and the agent corrects it.
- Local/production verification, build, deployment, merge, or rollback exposes a failure.
- The same class of problem occurs a second time in one project.
- A bug's root cause extends beyond code into requirements, design, testing strategy, release gates, or collaboration evidence.
- A later agent reworks because prior state, documentation, or branch status was insufficient.
- A process repeatedly returns to an old path despite documentation, entry scripts disagree with standards, or old cache/artifacts are mistaken for current authority.
- Existing Senmu BuildOS Skills omit a general governance problem.

Do not submit or formally review spelling, formatting, or a one-off command typo with no governance consequence.

## 2. Retrospective Order

A retrospective does not replace containment, repair, or owner decisions. Without repair authority, freeze facts and risk and hand off to the owner. With authority, review after required verification. Use `senmu-build-assurance` for an evidence-based verdict when root cause is disputed, impact is material, or independence is requested; ordinary project learning does not require Assurance.

Start this standard only when a candidate needs verification, a project rule needs correction, or promotion is being prepared:

1. Complete authorized containment/repair, or record the unresolved state and owner.
2. If repaired, verify the original failure path; otherwise preserve reviewable evidence and risk boundaries.
3. State what happened, why, how it was detected, and how it was handled.
4. Classify using the orthogonal dimensions in section 3.
5. Update the corresponding owner only within current write authority; otherwise record the proposed action.
6. Log only substantive fixes, decisions, or unresolved risks. Promote to a lesson and anti-regression entry only after reproduction and verification conditions are met.

Urgency may justify executing already-authorized containment or release first, but record the retrospective follow-up and trigger in the Work Log. Urgency never creates release, production-write, or destructive authority.

## 3. Root-Cause Classification

After verified rework, repeated failure or an owner correction, first finish the current requested result within its authority. A read-only retrospective or review records evidence, impact and recommendations; it does not repair the reviewed object, AGENTS or formal domain owners. Correcting the report itself grants no project-write authority.

Use one primary owner and orthogonal judgment fields, mapped into the existing Task, Lessons, Feedback or review owner only when a governance record is needed:

| Field | Values |
| --- | --- |
| primary_owner | project, product, design, engineering, workflow, delivery, assurance, learning |
| cause_type | execution, domain_rule_gap, instruction_routing_gap, capability_or_default_path_gap, buildos_component_gap, unknown |
| contributing_causes | Optional additional causes from the same cause vocabulary |
| evidence_state | hypothesis, supported, verified |
| recurrence | first_occurrence, repeated, catastrophic_first_occurrence |
| scope | project_specific, potentially_cross_project, cross_project_verified |
| actions | fix_current_result, no_durable_change, update_domain_owner, update_agents_route, improve_default_path_or_shared_capability, update_lesson, submit_buildos_feedback_candidate, collect_more_evidence |

These are judgment dimensions, not a new mandatory schema or ledger. Do not batch-migrate historical records, add required forms to ordinary tasks, or combine contradictory actions. A supporting cause does not create a second primary owner.

| Finding | Action within current authorization |
| --- | --- |
| One-off execution error with clear rules and routes | Correct the result; no durable rule change; log only if useful |
| Missing or wrong domain rule | Update its specialist owner |
| Existing rule cannot be discovered | Project repairs the shortest effective instruction route |
| Correct default path is hard to use or absent | Improve shared capability, component, example or command |
| Verified repeated cause, or first catastrophic stable gap | Index a lesson and correct the actual source owner |
| Specific BuildOS component caused reviewable harm | Submit a feedback candidate; cross-project reproduction is not required at intake |
| Unverified cause | Retain a hypothesis and recheck condition, not a hard rule |

Project's [Instruction Maintenance](../../senmu-build-project/references/project-standard-discovery-and-on-demand-loading.md#8-project-instruction-maintenance) owns AGENTS scope and editing methods. Learning owns classification, evidence and lesson lifecycle; specialists own the formal rules. Only promotion to a general BuildOS rule needs cross-project evidence or a demonstrated stable mechanism affecting multiple project types, with benefit above maintenance/context cost. Follow the existing feedback and BuildOS evolution entrypoints; classification alone grants no source, install or release authority.

## 4. Converge on an Executable Contract

When a project repeatedly reverts after fixes, agents drift despite documentation, or legacy paths/artifacts become current defaults, do not merely add SOP prose or human review. Check for a missing executable contract.

Use this method only for a real deterministic runtime contract with material residual risk that existing tools/state owners cannot adequately carry. Ordinary repeated component implementation first needs its shared implementation, discovery route or example repaired. Reuse existing owners and add only missing, necessary elements from the following options, not a mandatory bundle:

- one public or explicitly routed entrypoint: command, script, server API, release pipeline, or task template;
- machine-readable policy/config/schema, not only a long SOP;
- policy ID, version ID, source ID, and state fields in ledgers, databases, manifests, render plans, release plans, or other intermediates;
- a policy-bound validator/doctor checking entrypoint, configuration, script constants, artifact fields, and key files for consistency;
- a legacy boundary identifying old artifacts as history, behavior/style reference, or rollback evidence—not templates for new work;
- invalidation rules for caches and derivatives so updated source does not coexist with stale formal output.

For the elements justified above, converge in this order; skip already satisfied or inapplicable steps:

1. Trace the real drift path: entrypoint, configuration, script constants, ledger fields, cache, old artifact, and validator inputs.
2. Remove or quarantine old entrypoints that induce regression. If retained, label them legacy/demo in names, docs, and gates.
3. Encode the current standard in machine-readable policy and make entry scripts write its policy/version ID.
4. Validate consistency among documentation, machine policy, script behavior, ledger fields, and artifact provenance.
5. Record root cause, legacy boundary, trigger, and future entrypoint in the Work Log and lesson/anti-regression register.

This is normally G3-G4 governance, but does not impose heavy gates on all small work. Apply it to formal production, release, migration, content-production, or repeatedly failing multi-agent chains.

## 5. Promote a Retrospective to a Durable Lesson

A Work Log is a timeline, not a durable rule index. When a conclusion is likely to recur, has a verified root cause, has a decidable action, and can be rechecked, use `senmu-build-learning` to create or update the project's Lessons Learned Register under its common schema. New default BuildOS projects use `governance/lessons/LESSONS_LEARNED.md` and IDs `LES-YYYYMMDD-NNN`. Synchronize stable business, architecture, implementation, workflow, or deployment rules into the matching specialist owner.

A repeated verified root cause requires governance review (two unrelated slips do not prove recurrence): create/update the lesson, find the production step repeatedly creating the defect, and determine why the old rule failed. Correct requirements, architecture, interfaces, defaults, implementation, public entrypoints, or operations first. Add the smallest automatic detection or gate only for material residual risk worth controlling. “Be careful next time” is not closure; neither is adding checks without correcting a confirmed defect source.

## 6. Lesson Retrieval and Maintenance

Lessons matter only when later tasks can find relevant, trustworthy entries:

1. At task start, retrieve relevant `active` entries by module, release unit, process, environment, trigger, and keywords; never load all history by default.
2. Before adding, deduplicate by symptom, cause, source owner, required/prohibited action, and tags. Update the existing entry or establish a supersession relationship when overlap is high.
3. `candidate` is not a hard rule. Move it to `active` only after evidence; close long-unverified candidates or retain an explicit recheck condition.
4. After code, architecture, process, or platform changes, evaluate related lessons as Keep, Update, Consolidate, Supersede, or Retire.
5. After a stable rule moves to authority, retain only trigger, cause, evidence, and index in the lesson; do not copy the authoritative body.
6. Large registers may split by stable domain with a short index, but the project retains one Lessons Learned owner—not private knowledge bases per agent or Skill.

### 6.1 Mechanical Register Validation

After adding, editing, promoting, superseding, or retiring a lesson, run the command declared by project governance policy. The default BuildOS instance uses:

```bash
python3 .senmu-buildos/validate_lessons.py governance/lessons/LESSONS_LEARNED.md
```

The validator may block duplicate IDs, invalid status, active entries missing root cause/scope/trigger/source action/evidence/authority, and invalid supersession. Possible duplicates, overly broad information, personal absolute paths, and possible secrets are warnings for Learning review. The script never merges, rewrites, or promotes lessons automatically.

A passing validator proves register structure and relationships only—not root-cause correctness, treatment effectiveness, or cross-project applicability. Those remain semantic judgments grounded in evidence, project owners, and promotion criteria.

## 7. Retrospective Template

When appending a retrospective to an existing Work Log, use [Retrospective Entry Template](../assets/learning-governance/RETROSPECTIVE_ENTRY.template.md) as needed. It defines field structure only. Evidence and promotion criteria determine actual content, Lessons ID, and BuildOS feedback status.

## 8. Document Routing

| Finding | Preferred owner |
| --- | --- |
| Unclear requirement boundary, user flow, or acceptance | PRD or requirement owner |
| Unclear architecture, interface, data model, state transition, or third-party call | TECHNICAL_DESIGN or technical owner |
| Unclear startup, deployment, environment, or production verification | DEPLOYMENT |
| Unclear test command, real acceptance path, or mock boundary | TESTING_STRATEGY |
| Unclear branch, merge, or multi-person/agent handoff | BRANCHING_STRATEGY |
| Unclear version, tag, artifact, or rollback point | VERSION_AND_RELEASE, CHANGELOG, or release owner |
| What changed, what was verified, what remains | WORKLOG |
| Verified recurring failure, trigger, and anti-regression gate | LESSONS_LEARNED plus the authoritative specialist owner |
| Cross-project governance problem | Matching BuildOS source owner after whole-repository analysis |

## 9. Prohibitions

- Do not promote every issue into a general Skill rule; excessive general rules become unexecutable.
- Do not default to a prompt, checklist, validator, or approval layer. Fix the production step first, then control residual risk if justified.
- Do not bypass whole-repository analysis in BuildOS source or `$skill-creator` abstraction/structure/verification for Skill changes.
- Do not claim a retrospective without root cause, classification, and resulting constraint.
- Do not put project paths, customer-private data, secrets, or unpublished business facts in general Skills.
- Do not use retrospectives in place of version, changelog, release verification, or rollback records.
- Do not encode a hypothesized root cause as a rule; retain it as a candidate.
- Do not confuse chronology/correlation with causation. Distinguish `confirmed root cause`, `contributing factor`, `hypothesis`, and `unresolved`.
- Do not turn the lesson register into a chronological duplicate of the Work Log; update or supersede the same failure mode.
- Do not treat one installed Skill as the BuildOS source project or call a direct edit to an application install a framework upgrade.

## 10. Minimum Standard

Every formal retrospective must:

- state the problem and root cause;
- state the fix and verification;
- classify the issue as project-specific or general governance;
- update the best project owner or explain why none changes;
- decide whether to create/update a Lessons ID; a repeated verified root cause requires governance review within authorization, but a machine gate requires material residual risk;
- for a general gap, create a cross-project candidate first, then—inside the BuildOS source project—perform whole-repository abstraction, layering, deduplication, and verification, using `$skill-creator` for Skill changes. Project-private facts remain only in the project.
