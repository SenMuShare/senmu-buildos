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
4. Classify the cause as execution error, project-specific rule gap, or general governance gap.
5. Update the corresponding document or Skill according to classification.
6. Log only substantive fixes, decisions, or unresolved risks. Promote to a lesson and anti-regression entry only after reproduction and verification conditions are met.

Urgency may justify executing already-authorized containment or release first, but record the retrospective follow-up and trigger in the Work Log. Urgency never creates release, production-write, or destructive authority.

## 3. Root-Cause Classification

### 3.1 One-Off Execution Error

Signals: the current agent failed to read an existing file, omitted an existing script, misunderstood user direction, or used the wrong order; the project rule was already clear; no governance change is needed.

Treatment:

- Record facts, verification, and reminder in the Work Log retrospective section.
- Acknowledge the correction in the final report and state that the existing standard is now satisfied.
- Do not hide a one-off mistake behind additional process.

### 3.2 Project-Specific Rule Gap

Signals: the issue depends on this project's business, deployment topology, data flow, customer process, channel rules, directories, or release method and may not generalize.

Treatment:

- Update the matching project owner: PRD, TECHNICAL_DESIGN, DEPLOYMENT, TESTING_STRATEGY, BRANCHING_STRATEGY, VERSION_AND_RELEASE, WORKLOG, README, or equivalent.
- Prefer the project's existing `governance/` or `docs/` structure.
- Record that the rule is project-specific and why it is not abstracted into a general Skill.

### 3.3 General Governance Gap

Signals: the issue is likely across projects—for example, omitting version/changelog after a fix, treating local verification as production proof, confusing release units, losing handoff state, rebuilding an existing component, or promoting a project preference as universal. BuildOS lacks a clear gate or uses wording too vague for reliable execution. A project-independent rule would improve other projects.

Treatment:

- Fix the current project's owners first; a general change alone does not resolve the application project.
- Create a BuildOS candidate only when recurrence is likely across projects, the rule is project-independent, and ordinary tasks do not inherit disproportionate burden.
- Maintain the generalization as a separate task in the BuildOS source project under [BuildOS Evolution and Upstream Feedback](buildos-evolution-and-upstream-feedback.md), using whole-repository analysis. Use `$skill-creator` when Skill entry, structure, or triggering changes.
- Source edits, Git commits, candidate installation, and public release are separate authorities and states; a valid project retrospective does not authorize them.
- Report abstraction basis, candidate/update location, verification, and true boundaries of every state.

## 4. Converge on an Executable Contract

When a project repeatedly reverts after fixes, agents drift despite documentation, or legacy paths/artifacts become current defaults, do not merely add SOP prose or human review. Check for a missing executable contract.

An executable contract is the minimum set of project facts that later agents can discover, execute, and validate mechanically:

- one public or explicitly routed entrypoint: command, script, server API, release pipeline, or task template;
- machine-readable policy/config/schema, not only a long SOP;
- policy ID, version ID, source ID, and state fields in ledgers, databases, manifests, render plans, release plans, or other intermediates;
- a policy-bound validator/doctor checking entrypoint, configuration, script constants, artifact fields, and key files for consistency;
- a legacy boundary identifying old artifacts as history, behavior/style reference, or rollback evidence—not templates for new work;
- invalidation rules for caches and derivatives so updated source does not coexist with stale formal output.

Converge in this order:

1. Trace the real drift path: entrypoint, configuration, script constants, ledger fields, cache, old artifact, and validator inputs.
2. Remove or quarantine old entrypoints that induce regression. If retained, label them legacy/demo in names, docs, and gates.
3. Encode the current standard in machine-readable policy and make entry scripts write its policy/version ID.
4. Validate consistency among documentation, machine policy, script behavior, ledger fields, and artifact provenance.
5. Record root cause, legacy boundary, trigger, and future entrypoint in the Work Log and lesson/anti-regression register.

This is normally G3-G4 governance, but does not impose heavy gates on all small work. Apply it to formal production, release, migration, content-production, or repeatedly failing multi-agent chains.

## 5. Promote a Retrospective to a Durable Lesson

A Work Log is a timeline, not a durable rule index. When a conclusion is likely to recur, has a verified root cause, has a decidable action, and can be rechecked, use `senmu-build-learning` to create or update the project's Lessons Learned Register under its common schema. New default BuildOS projects use `governance/lessons/LESSONS_LEARNED.md` and IDs `LES-YYYYMMDD-NNN`. Synchronize stable business, architecture, implementation, workflow, or deployment rules into the matching specialist owner.

The second occurrence of the same failure forces governance escalation: create/update the lesson, find the production step repeatedly creating the defect, and determine why the old rule failed. Correct requirements, architecture, interfaces, defaults, implementation, public entrypoints, or operations first. Add the smallest automatic detection or gate only for material residual risk worth controlling. “Be careful next time” is not closure; neither is adding checks without correcting a confirmed defect source.

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
- decide whether to create/update a Lessons ID; the second occurrence forces governance escalation, but a machine gate requires material residual risk;
- for a general gap, create a cross-project candidate first, then—inside the BuildOS source project—perform whole-repository abstraction, layering, deduplication, and verification, using `$skill-creator` for Skill changes. Project-private facts remain only in the project.
