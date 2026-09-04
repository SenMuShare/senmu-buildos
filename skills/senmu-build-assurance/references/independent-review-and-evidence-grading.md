# Independent Review and Evidence Grading

Use this standard for reviews of code, architecture, governance, workflows, delivery readiness, production facts, or whole projects. It governs scope, evidence, findings, and re-review; it does not authorize remediation, release, deletion, or production changes.

## 1. Review Identity

Declare one identity:

- **Independent review:** the reviewer did not perform the main implementation or key decisions and chooses evidence and conclusions independently.
- **Peer review:** professional separation exists, although team context may be shared.
- **Evidence-based self-review:** the implementer or same agent reviews its own work. This can find defects but is not independent.

Identity describes separation, not competence. If separation is unproven, use self-review. For a formal independent verdict, hand a frozen subject—not a prescribed answer—to another executor.

Routine Product or Engineering consistency checks remain domain self-review. Assurance owns the frozen subject, Coverage Map, evidence, and verdict only when independence is requested, reviewer/implementer separation is required, a cross-domain dispute exists, or a G3-G4 gate explicitly requires independent evidence. Remediation stays with its domain owner.

## 2. Review Charter

Freeze before execution:

- objective, supported decision, requester, and audience;
- path, repository, commit/version, environment, time, and authoritative entrypoint;
- in/out scope, allowed sampling, and critical paths requiring full coverage;
- read-only boundary, allowed checks, and temporary-output location;
- applicable requirement, architecture, testing, release, or business standards and versions;
- finding priorities, conclusion states, and stopping conditions.

For “review the entire project,” map release units, modules, data/permission boundaries, entrypoints, and primary journeys. Review in bounded batches when needed. A representative sample cannot support a whole-project conclusion.

### 2.1 Modes and Completeness

- `risk_based`: default for ordinary changes, PRs, and large-project risk review. Sample by release unit, module, change, and high-risk path; state all unassessed scope and never imply every function was reviewed.
- `exhaustive_source`: only for an explicit request to cover every system, module, file, function, existing comment, or equivalent. Sampling and repeated rounds with no new findings do not prove completeness.

An `exhaustive_source` review must keep a stable control record and:

1. Freeze repository/tree identity, release units, systems, and languages; target changes invalidate the verdict.
2. Inventory every tracked first-party source file. Record exclusions for generated, vendor, lock, or mirrored files.
3. Use language-appropriate symbol analysis to inventory every function, method, constructor, accessor, behavior-bearing lambda, and top-level executable unit. Retain qualified name, line range, fingerprint, and evidence.
4. Check every unit for responsibility, abstraction, inputs/outputs, side effects, errors/resources, dependencies/architecture, duplication/economy, tests, and comments/docs; record why a dimension is inapplicable.
5. Check each existing comment/docstring for accuracy, necessity, freshness, and safety. Record missing necessary documentation under its unit's `comments_docs` check; do not demand noise comments.
6. Link findings both ways to files, units, or comments. Keep coverage completion distinct from verified remediation.

Create [Exhaustive Source Review Control](../assets/review-governance/EXHAUSTIVE_SOURCE_REVIEW_CONTROL.template.json), then run:

```bash
python3 <buildos>/skills/senmu-build-assurance/scripts/validate_exhaustive_source_review.py --record <control-record.json>
```

The validator proves record consistency, not complete symbol discovery. Record inventory method, tools/versions, limitations, and reconciliation with tracked files, language inventories, and entrypoints.

## 3. Evidence Levels

| Level | Meaning | Typical support |
| --- | --- | --- |
| `E0 unsupported` | statement, impression, or unlocatable summary | unverified hypothesis only |
| `E1 documentary` | current source, config, schema, docs, static artifact | structure, declarations, static constraints, potential risk |
| `E2 reproducible` | rerunnable command, test, build, query, deterministic check | behavior in a frozen environment |
| `E3 operational` | target identity, real data path, user journey, external receipt | current environment or actual chain |
| `E4 corroborated` | independent review, repeated runs, multiple sources/environments | high-impact, generalized, or stability claims |

Levels are not scores: E1 may prove a static architecture breach; production release requires E3; durable or broadly superior behavior usually requires E4. Record locator, acquisition time, object version, method, and limitations.

Screenshots, log excerpts, passing tests, and zero exits prove only what they observe. Truncated output, stale reports, another branch, or historical production state cannot substitute for current evidence.

## 4. Evidence Register

For material evidence, record `evidence_id`, level, source, object identity, time, collection method, supported/contradicted claims, and limitations. Persist only redacted locators and controlled-query entrypoints for sensitive data.

For conflicts:

1. Check version, environment, time, and release unit.
2. Separate plans/candidates from runtime facts.
3. Refresh the most volatile authoritative source directly bearing on the claim.
4. If unresolved, preserve the conflict and weaken the conclusion; do not select by expectation.

## 5. Finding State and Priority

Use:

- `suspected`: signal without sufficient evidence.
- `confirmed`: evidence proves the issue and impact boundary.
- `disputed`: factual or standards conflict remains.
- `accepted_risk`: owner accepts it with expiry/re-review conditions.
- `resolved_unverified`: remediation reported but not reviewed.
- `verified_resolved`: original failure path re-reviewed successfully.
- `false_positive`: new evidence disproves it; retain the correction basis.
- `superseded`: a later finding/report replaces it.

Assign priority from impact, likelihood, recoverability, exposure, and urgency:

| Priority | Rule |
| --- | --- |
| `P0` | active/imminent security, privacy, financial, irreversible-data, or severe production incident; stop or isolate |
| `P1` | major critical-contract, core-journey, release-integrity, or high-risk-control defect; resolve before approval |
| `P2` | material impact with a safe workaround or planned path; do not dilute into generic advice |
| `P3` | low-risk maintainability or clarity improvement; do not present as blocking |

Do not infer severity from file count, code volume, forceful wording, or preference. For debt without a defect, record triggers and risk rather than defaulting to P1.

## 6. Execution

1. Read authoritative entrypoints, current state, and applicable owner rules.
2. Build Coverage Map and Evidence Register; start at high-risk boundaries.
3. Match search, static analysis, tests, runtime queries, and real flows to each claim.
4. Seek counterevidence, protections, and false positives.
5. Bind findings to objects, evidence, impact, priority rationale, and minimum remediation.
6. Reconcile coverage; list checks not run, failed, blocked, or inapplicable.

Read-only review may execute checks that do not change project, external, or production state. Put intermediates in an isolated temporary location. Database writes, snapshot updates, uploads, notifications, deployments, cleanup, or other external changes require separate authorization even when called tests.

## 7. Conclusions

- `supported`: matching in-scope evidence and no unresolved blocker.
- `supported_with_conditions`: holds with explicit conditions, P2/P3, or pending verification.
- `not_supported`: P0/P1, missing critical evidence, or contradictory facts defeat the claim.
- `inconclusive`: conflict, staleness, or blockage prevents judgment.
- `not_assessed`: excluded or not actually covered.

“No issues found” applies only to declared coverage. Machine gates prove only their contracts.

For `exhaustive_source`, `review_complete` means every frozen file, executable unit, and existing comment has a result; it does not mean conformance. Use `verified_complete` only after freezing the remediated target, disposing of every finding, rerunning original failures and applicable regressions, and revalidating the control record.

## 8. Remediation and Re-review

- Define remediation objective, owner, priority, and acceptance evidence; do not implement without authorization.
- The implementer updates the responsible domain owner; Assurance creates no second standard.
- Re-review the original finding against a newly frozen target, rerun its failure, and inspect regression risk.
- Preserve the original report; append status or create an explicit superseding report.
- Verified remediation does not establish product acceptance, release approval, or deployment.

Use the [Assurance Review Report](../assets/review-governance/ASSURANCE_REVIEW_REPORT.template.md) for charter, coverage, evidence, findings, and conclusions. If the project has an audit system, keep it as the sole owner.
