# Discovering Project Engineering Standards

Use this method to derive a mature codebase's coding, architecture, testing, and tooling standards from real evidence. Continue effective project practice while identifying defects that need governance; neither treat existing code as automatically correct nor impose BuildOS language preferences.

## 1. Select Representative Evidence

Confirm the current release unit and task slice, then sample evidence appropriate to the actual stack:

- public entrypoints, core business paths, and frequently changed modules;
- build, format, lint, type, test, and dependency configuration;
- normal/error paths, boundary handling, and persistence;
- unit, integration, end-to-end tests, and fixtures;
- architecture, ADR, quality, contribution, and release owners;
- recent commits or verified incident records that explain a rule's rationale.

Exclude generated code, vendors, caches, archives, demos, retired implementation, and unrelated worktrees/release units. Do not prescribe a file count; evidence must cover target decisions without requiring a full-repository read.

## 2. Patterns Worth Extracting

- Module responsibilities, dependency direction, public interfaces, and side-effect boundaries.
- Naming, types, errors, logging, configuration, and data migration.
- Framework components, project wrappers, standard library, dependencies, and reuse order.
- Test layers, real versus substituted dependencies, test data, and quality commands.
- Security, authorization, privacy, payments, production data, and release constraints.
- Stable, rational project choices that differ from common defaults and affect implementation.

Do not promote language basics, one-off unexplained style, obvious defects, or conflicting legacy implementations.

## 3. Classify Candidates

Record evidence for each candidate:

| Class | Meaning | Treatment |
| --- | --- | --- |
| Formal rule | Authoritative document/machine config matches production implementation | Preserve owner and add a short index route |
| Stable practice | Repeated consistently and supported by tests, tools, or history | Confirm, then write to the nearest engineering owner |
| Candidate | Signals exist but rationale, exceptions, or validity are unclear | Keep `candidate`; do not constrain implementation |
| Engineering defect | Duplicated, coupled, stale, or contrary to quality goals | Enter debt or authorized repair; never present as a standard |
| Legacy | Retained only for compatibility, rollback, or migration | Mark boundary and replacement; do not use as a template |

One file, occurrence frequency, or commit chronology never proves a standard alone.

## 4. Write Back and Index

Write complete rules by meaning to existing CODE_QUALITY, ARCHITECTURE, TESTING_STRATEGY, TECHNICAL_DESIGN, ADR, tool configuration, or equivalent. When needed, repair code, configuration, or the unified quality entrypoint so prose and execution agree.

The Project Map/established short index records only domain, applicability signal, decision summary, authoritative path, and status. It does not copy examples, long rules, or command catalogs. Update the specialist owner before the index.

Keep project engineering standards scannable and executable:

- Lead with rule and conditions, then the necessary rationale.
- Record only non-obvious, project-specific facts that change implementation; do not restate language basics or self-explanatory code.
- One entry owns one concept. Use short items and minimum positive/negative examples only to remove ambiguity.
- One semantic body has one owner; entrypoints and indexes state when to read it, which decision it affects, and where it lives.
- Put mechanically enforceable rules in existing formatter, lint, type, test, or architecture configuration; docs explain meaning, exceptions, and verification entrypoint without copying configuration.

## 5. Boundaries

- Current project languages, frameworks, and tools beat preference; do not initiate a stack rewrite without approved migration scope.
- Repair defective original owners instead of creating idealized parallel code or standards.
- Official external docs and open-source practice inform judgment but are not automatically adopted project rules.
- Load only standards relevant to current module, risk, and change; expand evidence for whole-repository refactors, migrations, or formal reviews.
- Use `senmu-build-assurance` when independent evidence sufficiency or a disputed conclusion is required; Engineering owns ordinary discovery and consistency self-checks.
