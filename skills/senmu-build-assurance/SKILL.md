---
name: senmu-build-assurance
description: "Produce read-only, evidence-graded POC, audit, reproduction, or disputed-cause verdicts. Not for implementation, routine review, retrospectives, or fixes."
---

# Governance Assurance

Operate read-only by default. Freeze the subject, version, scope, and standard; then distinguish facts, inferences, and unknowns with reviewable evidence. Produce a verdict without automatically remediating it.

## Route by Outcome

- For a decision POC, blind test, controlled experiment, ledger, or reproduction, read [Reproducible POC Governance](references/reproducible-poc-governance.md).
- For a code, architecture, governance, delivery, or whole-project review, read [Independent Review and Evidence Grading](references/independent-review-and-evidence-grading.md). Use `exhaustive_source` only when the user explicitly requests every file, function, or existing comment.

Routine consistency checks remain with the domain skill; G3-G4 alone does not activate Assurance. Read only the applicable Engineering reference when an engineering standard is needed.

## Core Contract

- Declare the review as `independent`, `peer`, or `evidence-based self-review`; do not claim independence without demonstrable separation.
- Record the frozen target, coverage, evidence source and freshness, excluded scope, and stopping conditions.
- Evidence supports only what it observes. Static analysis, tests, production facts, and independent review are not interchangeable.
- Seek counterevidence before assigning status, P0-P3, impact, minimum remediation, and re-review conditions.
- Keep `not_assessed`, `inconclusive`, `resolved_unverified`, and `verified_resolved` distinct.
- Review authority does not permit modification, release, deletion, or production changes. Return remediation to its domain owner.

Use the project's durable task owner for multi-stage reviews. Handoffs carry findings, evidence, scope, target outcomes, and re-review conditions, not copied standards.
