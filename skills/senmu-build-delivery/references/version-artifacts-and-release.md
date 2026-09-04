# Version, Artifact, and Release

Use this standard for version identity, Tags, independent artifacts, retention, and release closure. Read [Release Authorization and Production Truth](release-authorization-and-production-truth.md) for authority/state and [Code Management and Integration](code-management-and-integration.md) for Git/worktrees.

## 1. Release Units and Version Identity

Create an independent version/Tag only for an object that independently builds, deploys, rolls back, and has distinct responsibility. Internal monorepo modules are not fictitious release units.

A formal unit relates product/requirement scope, necessary technical changes, frozen commit, `VERSION`, changelog, actual artifact, target environment, production verification, formal Tag, and rollback point. Correspondence is required; projects without versions/deployment do not invent layers. A formal Tag represents an already verified release, never a pre-deployment candidate.

Formal version, public source, deployment, and independent artifacts are composable rather than implied by a `release` profile, Tag, or platform source snapshot. Default to SemVer with stable scopes for multiple units, unless project authority differs. Local Tag, pushed Tag, platform Release, artifact upload, and deployment are separate states/authorities.

A local internal development snapshot may retain the latest formal version number but also records immutable source commit, source type, and install time. When content changes under one `VERSION`, directory names cannot identify the loaded runtime. SessionStart must echo concise `version@commit` to prove a new session loaded it; copied files or enabled plugin status proves installation only.

Task state, Work Log, Release Record, or internal receipts that do not change package/artifact content create no runtime identity and do not trigger rebuild/retest/reinstall. The installed snapshot stays bound to the last content-changing commit. Update identity only when a runtime consumes the record or it changes candidate, authority, artifact, production truth, or rollback decisions.

## 2. Candidate and Release Stages

Users need not specify Git command order. After explicit formal-release authority, execute the project-standard path automatically.

When a machine release driver exists, the following is its behavior contract, not a command list for manual replay. It may expose `plan/prepare/release/resume` or CI equivalents but remains one top-level owner. Generate/write back version metadata and Release Record from one structured fact; do not make the releaser edit duplicate versions manually.

1. Confirm scope, unit, environment, standard entrypoint, durable restrictions, and rollback; perform release intake under the code-management standard.
2. Integrate applicable completed commits in the sole clean release source. Reuse tests bound to sealed commits and add only conflict-impact checks.
3. Compute the next version from project policy, update version/changelog/candidate state, and create a frozen version commit. For public products, read the Product owner's review of README/site/repository description, synchronize changed narrative and supported languages, and prepare user-readable notes. A number-only change, generated commit list, or stale description fails. If repository description/Topics are machine-managed, the one release entrypoint synchronizes and reads them back before the formal Tag.
4. After version preparation in the sole mutable release root, run complete preflight once. Fix failures in that root; the old candidate is invalid. Freeze only the passing head, identified by commit, candidate number, and required artifact digest.
5. Build/upload one immutable artifact from the frozen commit; source-only releases retain exact commit. Do not create a formal Tag at candidate stage.
6. Deploy/publish from the frozen source, then verify runtime identity, health, and affected core flow. Command success without evidence remains `deployed_unverified`.
7. Only after production/channel truth is `released`, create the immutable formal Tag and, as configured, push it and create the platform Release. For source distribution, first verify the frozen commit on the public main line.
8. Append a Release Record through the existing owner linking candidate, artifact, deployment, verification, and Tag. It does not mutate the candidate/runtime identity. If Tag/platform closure fails, preserve production facts and record the incomplete item; do not demote a live version to unreleased.

Before artifact/deployment, ensure `reviewed_commit = tested_commit = release_source_head`; add `artifact_source_commit` when building/importing. At formal Tag, ensure `tag_commit` equals the verified release source. Use `verify_release_identity.py` or an equivalent top-level hard gate.

Version-line roles are project-defined, not inferred from numbers. `current_line`/`successor_line` may be `0.x`, `1.x`, `5.x`, CalVer, build numbers, channels, or nonnumeric branches. Read the version owner and promotion relationship.

With one current unit, one default target, and a declared standard entrypoint, “release the latest version” or “release the fix” authorizes configured non-extra-destructive layers. Ask only material choices for multiple units/environments, unclear scope, first-time remote setup, paid calls, irreversible migration, traffic change, or unplanned cleanup. Do not ask users to choose Git sequencing.

A request only for development, candidate, or preflight cannot pass `preflight_passed`; “prepare release” is not “release.” A formal release changing Skills, Hooks, routing, or behavior contracts needs a review of the frozen surface with no open blocking Finding; structural tests do not replace semantic review.

For a completed but unreleased hotfix, record code location, tests, risk, synchronization status, and release condition. Local success is not live.

## 3. Tags, Source Packages, and Artifacts

- A formal Tag immutably identifies the frozen commit after target verification. Pre-deployment candidates use commit, candidate number, and artifact identity.
- Source packages exclude secrets, production data, uploads, databases, caches, logs, and unauthorized material.
- Artifacts identify source commit, version, platform, build inputs, and digest.
- Commit/Tag proves source identity; even a formal Tag does not replace Release Record or target evidence. Claim reproducibility only with base image, lockfiles, toolchain, external inputs, and provenance.
- Verify target OS/architecture from manifests/runtime; names are insufficient.
- Formal configuration uses explicit versions/digests, never drifting `latest` identity.

## 4. Retention and Cleanup

Default retention: current verified version, one verified rollback version, and explicit pins/compliance evidence. Rollback is not necessarily the adjacent version. Project policy may change counts without silently losing rollback, data, compliance, or evidence.

Cleanup affects only managed paths/registries of the current unit:

- Resolve current, rollback, pins, and all container references by digest/ID first.
- Never delete commits, formal Tags, changelog, Release Records, databases, volumes, other-project resources, or global caches.
- Never run cross-project global prune; force deletion needs separate authority.
- `dry-run` is not closure; apply only after production verification and release authority.

Register local builder, production runtime, remote registry/artifact store, and current Git surface separately. Host cleanup does not close remote registry or Git.

## 5. Release Source and Production Verification

Build formal artifacts only from the unit's authoritative directory and frozen commit. Passing in another worktree does not replace release-source evidence; unrelated dirt elsewhere does not invalidate the candidate.

At the target, verify actual object/image identity; version endpoint/equivalent; health/readiness; affected user core flow; and required migration, permissions, safety, and rollback availability.

The completion report includes unit, version, commit/Tag, artifact, environment, verification, rollback point, retained set, and residual risk. Engineering chooses technology; Delivery closes compatibility, migration, build, deployment, and rollback effects.
