# Version, Artifact, and Release

Use for version identity, Tags, artifacts, retention and release closure. For authority/state questions, read [Release Authorization and Production Truth](release-authorization-and-production-truth.md). Git/worktree decisions use the Code/Merges route in the Delivery entrypoint; artifact-only work does not preload that manual.

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
4. After version preparation in the sole mutable release root, complete preflight once by accepting still-valid Engineering evidence and executing missing or invalidated checks under Delivery’s Testing and Acceptance contract. Fix failures in that root and renew the candidate conclusion; retain unaffected evidence. Freeze only the passing head, identified by commit, candidate number, and required artifact digest.
5. Produce/upload an immutable artifact or frozen composition from the verified candidate, reusing verified build output where applicable rather than rebuilding by stage convention; source-only releases retain exact commit. Reused components retain their original provenance under section 3.1. Do not create a formal Tag at candidate stage.
6. Deploy/publish from the frozen source/composition, then verify runtime identity, health, and affected core flow. Command success without evidence remains `deployed_unverified`.
7. Only after production/channel truth is `released`, create the immutable formal Tag and, as configured, push it and create the platform Release. For source distribution, first verify the frozen commit on the public main line.
8. Append a Release Record through the existing owner linking candidate, artifact, deployment, verification, and Tag. It does not mutate the candidate/runtime identity. If Tag/platform closure fails, preserve production facts and record the incomplete item; do not demote a live version to unreleased.

For a single-source artifact before artifact/deployment, ensure `reviewed_commit = tested_commit = release_source_head`; add `artifact_source_commit` when building/importing. At formal Tag, ensure `tag_commit` equals the verified release source. For a composition, bind review and testing to the frozen composition and verify each selected artifact against its own immutable provenance under section 3.1, not against one fabricated shared commit. The current candidate receipt may incorporate explicitly reconciled earlier runs; preserve their original source identities and never relabel them as fresh execution. Use `verify_release_identity.py` for its single-source contract, or an equivalent existing top-level composition check; never disable identity protection to admit a mixed release.

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

### 3.1 Composition and Reusable Runtime Assets

Use only when a release combines independently identified artifacts or large low-change runtime assets. Extend the existing manifest and driver, not a second release registry. Product version, component version, artifact digest and source commit answer different questions; neither one version for everything nor an independent version per internal module is mandatory.

Freeze the selected combination: component/artifact identity and immutable location, original source/build provenance, actual consumers, new versus reused selection, configuration/schema compatibility evidence and the verified recovery combination. The updated [Artifact Manifest](../assets/delivery-governance/ARTIFACT_MANIFEST.template.json) provides optional composition and per-item provenance fields; adapt existing owners rather than hand-copying their records. Its additive fields are not an automatic migration of strict external consumers.

In that template, `composition: null` retains the single-source form. When used, `composition` identifies the immutable selection record, compatibility evidence and rollback reference; top-level `source` then identifies the selection's source, not every component's source. `artifacts[].selection` is `new` or `reuse`; a reused item must resolve `provenance_ref` to its original source/build/inputs/digest evidence. A new single-source item may use top-level provenance. `component_id`, `component_version` and `consumer_refs` are optional where not meaningful. Selection does not itself imply skipped upload, import or restart: actual target availability and drift determine those actions.

Verify selected identities and relevant compatibility at the original driver, then read the target's actual running objects and affected flow. Candidate metadata is not production truth. Reuse available original proofs without checking out and rebuilding every old component. The single-source identity checker remains strict and does not validate a composition; treating its success as proof of a mixed release is invalid.

For immutable models, media catalogs and similar low-change assets, use content identity independent of product version when repeated production/transfer is a real cost. Reuse an existing artifact before generating another archive when relevant source inputs and build configuration remain equivalent and its integrity is established. Deterministic packaging or a canonical input manifest avoids incidental archive metadata defeating reuse. A content match alone does not establish authenticity, format compatibility, permissions or usable target availability.

Use an eligible existing target object after integrity/compatibility checks; an absent or corrupted copy needs controlled replacement or a blocked dependent step, not silent reuse. Do not overwrite a still-referenced object in place. Current deployment, verified rollback, pins and active recovery references protect shared resources. Retiring an old release directory must not remove a resource needed by another retained combination. Mutable databases, user inputs and changing task state do not become disposable content-addressed assets.

Record pending retention reason, responsible owner, next actor/action and the event that removes the hold in the existing receipt; unresolved ownership stays protected, not silently permanent. Storage cleanup still follows sections 4 and 6. Composition support adds no new deployment engine, global cache, registry service or universal hash inventory.

## 4. Retention and Cleanup

Default retention: current verified version, one verified rollback version, and explicit pins/compliance evidence. Rollback is not necessarily the adjacent version. Project policy may change counts without silently losing rollback, data, compliance, or evidence.

Cleanup affects only managed paths/registries of the current unit:

- Resolve current, rollback, pins, and all container references by digest/ID first.
- Never delete commits, formal Tags, changelog, Release Records, databases, volumes, other-project resources, or global caches.
- Never run cross-project global prune; force deletion needs separate authority.
- For formal release resources, `dry-run` is not cleanup completion; apply only after production verification and covered release authority. Non-release local resources follow their task lifecycle and existing cleanup authorization, not a production gate.

For each real builder/runtime/remote-store/Git surface, map build copies/dependencies, version payloads/transfers, images/containers, caches, logs and backups to protected consumers, policy and native exit owner in the existing Task/Run or Release Record. A helper covers only its declared subset. Before moving or retiring payloads, establish the recovery objective and verified custody: which existing copy/location or evidenced rebuild supplies it. Coordinate cross-surface order with original owners and script prerequisites; do not copy by default or bypass existing gates. Keep necessary evidence separately; rebuilding build outputs does not replace backups of changing data.

For a project with managed release resources, its existing release driver must invoke the scoped cleanup after successful target verification, not merely generate the helper or print a preview. During initialization, takeover or a change to that driver, trace the real call and validate it with a disposable fixture. Update current/verified-rollback/pin identities from the release's artifact facts before planning; template values are not a permanent retention registry. Reuse the existing release receipt for each real resource surface and preserve an explicit next action for incomplete closeout.

A receipt distinguishes `planned`, `disabled`/not configured, `no_candidates` after an enabled complete inventory, `completed`, `blocked` before removal, and `failed` after an attempted or partial removal. Planned counts are not removal counts. Enumeration/inspection failures must propagate; unknown is not zero. Aggregate against the expected groups established from producers and project policy, not only the groups that happened to run. Missing, disabled, unresolved held or unknown groups keep overall closeout pending/partial, even if images and one dependency copy succeeded. Disabling a group or leaving its target list empty is not evidence of inapplicability. Policy-protected current/rollback/pin/recovery/evidence objects may remain with verified identities, reason, owner and review/exit condition; unresolved ownership or consumers remain pending. Deployment truth stays separate: a live version can have pending cleanup without reversing its release or public availability. Inapplicable groups need evidence and a reason, not a fake cleanup command.

When a project adopts the bundled Release Control, its trusted managed-resource entrypoint can require `validate_release_control.py <record> --require-resource-closeout`. The optional `resource_closeout` block binds an expected group set and existing evidence references to the aggregate; closed releases reject incomplete groups. Adapt an existing equivalent owner rather than migrate every project. This checks declarations and coverage only: it neither authenticates evidence nor inventories, removes or measures resources. Source-only legacy records remain supported without the option.

Keep each cleanup plan's complete-inventory-before-removal boundary. When resource groups are proven independent with separately covered authority, retention and writer exclusion, the existing driver may call the helper with separate scoped configurations and retain every result. A failed Docker group need not stop independent local artifacts. Shared/unknown dependencies remain coupled; do not split just to bypass failed inspection. Validate and freeze independent config partitions before apply; keep each attempt receipt. Cancellation supervises and joins the active child before stopping remaining groups; uncertain partial results need reconciliation, not blind retries. The existing version-rule template contains a tested caller example. Adopt at the project owner; source updates do not rewire existing projects.

Use native cache GC, log rotation and backup expiry for continuous growth, with project-specific age/count/size budgets and review conditions. A release hook alone cannot bound growth between releases. Cache GC does not retire release directories or images; registry expiry does not reclaim builder storage. Do not copy a framework's fixed keep-count without its rollback and capacity assumptions.

The bundled template covers governed reproducible artifact directories and tagged image references on one selected Docker engine. Its receipt identifies that context/engine, counts image references rather than unique storage layers, and does not claim measured disk recovery. Retiring stopped containers, unowned/dangling images, shared build caches and remote registry objects requires the relevant project-native lifecycle and existing scope/authority; do not weaken container-reference protection or use global prune to force a two-version count.

## 5. Release Source and Production Verification

Build new formal artifacts only from the unit's authoritative directory and frozen commit. Reused artifacts retain their verified original provenance and join a frozen composition under section 3.1. Passing in another worktree does not replace release-source evidence; unrelated dirt elsewhere does not invalidate the candidate.

At the target, verify actual object/image identity; version endpoint/equivalent; health/readiness; affected user core flow; and required migration, permissions, safety, and rollback availability.

The completion report includes unit, version, commit/Tag, artifact or composition, environment, verification, rollback point, retained set, and residual risk. Engineering chooses technology; Delivery closes compatibility, migration, build, deployment, and rollback effects.

## 6. Native Resource and Distribution Checks

For container/image cleanup, resolve native IDs/digests and inspect all references, including stopped containers, current/rollback versions, pins, unique writable-layer data and shared builder usage. Use the existing scoped native resource entrypoint; never remove backend disk files or run global prune. Preserve uncertain/shared resources. Resource groups and retention facts belong in the existing Task/Run owner under Workflow closeout; report logical removal separately from measured disk space reclaimed.

Inspect actual package, image, archive and install staging contents with the existing allowlist/exclusions. `.gitignore` is insufficient. Exclude credentials, private configuration, personal material, local databases, user uploads and temporary caches unless the contract defines a safe necessary form. Assess absolute paths for privacy and portability rather than banning all paths. Use synthetic canaries in tests, never real secrets.
