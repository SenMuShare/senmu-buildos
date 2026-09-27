---
name: senmu-build-assurance
description: "Conduct explicit audits, decision POCs, comparisons or disputed-cause reviews with scoped evidence. Audit scope does not imply reviewer independence. Not for routine domain self-checks or production implementation."
---

# Governance Assurance

Reviews are read-only by default; an authorized POC may write its isolated experiment materials, not the audited product or production state. Freeze the subject, version, scope, and standard; distinguish facts, inferences, and unknowns with reviewable evidence. A verdict does not itself authorize remediation.

## Route by Outcome

- For a decision POC, blind test, controlled experiment, ledger, or reproduction, read [Reproducible POC Governance](references/reproducible-poc-governance.md).
- For a code, architecture, governance, delivery, or whole-project review, read [Independent Review and Evidence Grading](references/independent-review-and-evidence-grading.md). Use `exhaustive_source` only when the user explicitly requests every file, function, or existing comment.
- For resumable or explicitly coverage-tracked Git reviews, use [Frozen Review Execution](references/frozen-review-execution.md). The helper is optional and does not change reviewer identity or domain ownership.

Explicit audits, cross-domain disputes and required independent verdicts use Assurance. Routine consistency checks stay with the domain; G3-G4 alone does not activate it. Choose reviewer identity separately from audit scope. Read only applicable Engineering guidance.

## Core Contract

- Declare the review as `independent`, `peer`, or `evidence-based self-review`; do not claim independence without demonstrable separation.
- Record the frozen target, coverage, evidence source and freshness, excluded scope, and stopping conditions.
- Evidence supports only what it observes. Static analysis, tests, production facts, and independent review are not interchangeable. Execution completion does not establish quality or approval.
- Seek counterevidence before assigning status, P0-P3, impact, minimum remediation, and re-review conditions.
- Keep `not_assessed`, `inconclusive`, `resolved_unverified`, and `verified_resolved` distinct.
- Review authority does not permit modification, release, deletion, or production changes. Return remediation to its domain owner. When the same request already authorizes repair, continue there after findings without another generic approval; review-only requests remain read-only.

Use the project's durable task owner for multi-stage reviews. Handoffs carry findings, evidence, scope, target outcomes, and re-review conditions, not copied standards.
