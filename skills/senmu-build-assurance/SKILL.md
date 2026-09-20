---
name: senmu-build-assurance
description: "Design or assess decision POCs, comparisons, audits, reproductions, or disputed causes with graded evidence. Reviews are read-only; authorized experiments use isolated scope. Not for routine review or production implementation."
---

# Governance Assurance

Reviews are read-only by default; an authorized POC may write its isolated experiment materials, not the audited product or production state. Freeze the subject, version, scope, and standard; distinguish facts, inferences, and unknowns with reviewable evidence. A verdict does not itself authorize remediation.

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
- Review authority does not permit modification, release, deletion, or production changes. Return remediation to its domain owner. When the same request already authorizes repair, continue there after findings without another generic approval; review-only requests remain read-only.

Use the project's durable task owner for multi-stage reviews. Handoffs carry findings, evidence, scope, target outcomes, and re-review conditions, not copied standards.
