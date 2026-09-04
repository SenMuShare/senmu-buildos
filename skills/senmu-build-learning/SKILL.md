---
name: senmu-build-learning
description: Review BuildOS feedback, retrospectives, verified lessons, or external guidance for reusable rules. Not for ordinary corrections, logs, or independent audits.
---

# Organizational Learning

Keep raw feedback, candidate lessons, project rules, and formal BuildOS rules in distinct states. Resolve ordinary corrections in the current task. Load this skill only for inbox review, formal retrospectives, lesson promotion, or knowledge distillation.

## Route by Outcome

- Submit or review feedback candidates: [Feedback Review](references/feedback-candidates-and-central-adjudication.md).
- Retrospect, deduplicate, promote, or retire resolved lessons: [Organizational Learning](references/organizational-learning-and-governance-closure.md).
- Promote cross-project improvements into BuildOS: [BuildOS Evolution](references/buildos-evolution-and-upstream-feedback.md).
- Absorb websites, books, repositories, third-party skills, or engineering manuals: [Knowledge Distillation](references/engineering-knowledge-distillation-and-standard-promotion.md).

Run the project's validator when modifying formal Lessons Learned. Raw feedback does not need a Lessons ID.

## Core Contract

1. **Capture:** Use the local CLI only when BuildOS use in a real project shows that a skill, reference, template, script, hook, or rule caused error, misdirection, execution difficulty, empty guidance, unnecessary work, or inefficiency. Do not capture business requests or ordinary corrections automatically.
2. **Review:** Deduplicate by root cause and classify as `discard`, `project`, `buildos_candidate`, or `needs_evidence`.
3. **Promote:** Return project-specific rules to the project owner. Promote cross-project rules only with clear evidence, scope, disposition, and authoritative owner.

Record the component, concrete impact, and evidence or workaround. Dissatisfaction can start a candidate but a vague opinion is insufficient; frequency is not a mechanical threshold. Correct the source first. Do not add prompts, validators, or approvals for every mistake or duplicate a rule across skills, inboxes, logs, and lessons.

Handoff disputed facts or causes to Assurance and customer requirements to Product. Learning owns knowledge lifecycle, not domain facts or Git/release authorization.
