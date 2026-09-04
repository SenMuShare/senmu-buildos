# Release Authorization and Production Truth Protocol

Use this protocol for formal delivery, deployment, production launch, hotfix, rollback, and other external-environment changes. It separates plan, candidate, authority, execution, and production truth so code completion, passing preflight, or a Tag cannot be misreported as live.

## 1. Four Objects

| Object | Question | Typical owner |
| --- | --- | --- |
| Version and Release Plan | What will release, with which scope/gates? | `delivery/RELEASE_PLAN.md` |
| Release Candidate | Which unambiguous revision/artifact awaits approval? | Git commit, CI/artifact store, Artifact Manifest |
| Release Record | What did one release attempt actually do and produce? | `evidence/releases/` or release system |
| Production Truth | What is actually running now? | Platform, version endpoint, health, user-visible flow |

A plan is not a candidate; a candidate is not authority; deployment completion is not verified release; a record cannot overwrite target-environment truth.

## 2. State Model

| State | Meaning |
| --- | --- |
| `planned` | Scope planned; no unambiguous candidate |
| `candidate` | Revision, version, and candidate artifact locked; not approved |
| `preflight_passed` | Pre-release gates passed; no external-change authority |
| `authorized` | User explicitly authorized this scope/environment |
| `deploying` | Target environment is changing |
| `deployed_unverified` | Deployment action ended; production evidence incomplete |
| `released` | Target identity, health, and affected core flow verified |
| `failed` | Attempt failed/partial; current state requires reconciliation |
| `rolled_back` | Rollback action and resulting production truth verified |
| `cancelled` | Candidate explicitly stopped |
| `superseded` | Later version replaces it; history retained |

Advance only as far as evidence. If external change is uncertain, use `deployed_unverified` or `failed`; never guess old, successful, or rolled back.

## 3. Authorization Boundary

An implementation/fix request leaves the development batch `in_progress`; it does not seal, integrate, run full candidate gates, or prepare release. “Send for testing,” “close this batch,” “prepare release,” or “generate a candidate” permits local/CI freeze, integration, preflight, and reversible preparation only—not production change.

This task needs explicit release intent for formal Tag/push/release page/artifact; remote upload, production connection, deployment/migration; service restart, traffic/domain/config/production-data change; public notification, listing, content publication, or remote rollback-resource cleanup.

Valid authority identifies target release unit, environment, and allowed action; high risk should also identify candidate/version, service scope, window, and rollback. It binds one exact candidate and bounded release session, not a permanent pass or one command. No release intent means no authority; past releases, credentials, executable scripts, or a plan containing “release” are insufficient.

Natural language combines with registered project facts. If the project has one current unit, one default production environment, and one standard release entrypoint, “release the latest version” or “release this fix batch” authorizes that entrypoint's configured ordinary version commit, immutable Tag, existing remote sync, platform Release, artifact, deployment, production verification, and Release Record. It does not cover first-time remote resources, extra paid services, irreversible migrations, unplanned data/artifact deletion, cross-project action, or undeclared environments.

With multiple units/environments, unclear inclusion, or extra high-risk effects, ask only for the choice that changes the outcome. Delivery then decides merge/version/Tag order. Do not force a nontechnical user to authorize commit, Tag, push, and deploy one by one.

Before execution, identify local Git, remote, hosting platform, and deployment target separately. Without a remote, complete a local version only; do not create a repository. A user-authorized technical layer does not imply outer layers. Under standard-release authority, the declared entrypoint determines which existing remote, Tag, platform Release, and deployment layers apply.

Release authorization may cover project-declared retention and managed cleanup after production identity, health, and affected flow pass. A user-provided retention count/cadence becomes preferred policy. If it loses a verified rollback point, violates compliance, or deletes evidence, explain and obtain risk acceptance. Authority never extends to undeclared repositories, other projects, volumes, databases, Git history, or global caches. Remote registry cleanup needs explicit plan/authority coverage and the sole release entrypoint.

Within the same candidate, artifact, and environment, recover side-effect-free connection/upload/query failures under the project retry budget while production state is clear. A changed revision, artifact, environment, migration, rollback boundary, switch to hotfix, or ambiguous production truth invalidates authority and requires reconfirmation.

“Do not release” or “not yet” is a durable release constraint written to the existing task/release owner, scoped by default to unit/environment and optionally line/batch. Session change, commit, integration, preflight, or failed attempt does not remove it. A hotfix exception binds one exact commit/rollback point and does not lift other restrictions.

## 4. Candidate and Artifact Identity

Lock release unit, version, source revision/baseline; artifact ID/hash/platform/build entry/build environment; config/schema/migration versions and compatibility; included/excluded scope and coupled units; quality evidence, gaps, risks, and rollback candidate.

A formal Tag represents a verified formal release, points immutably to the frozen commit, and is associated by the Release Record with environment/channel evidence. Pre-deployment candidates use commit, candidate number, and Artifact Manifest. Creating/pushing a formal Tag is a release action and needs authority.

Use [Artifact Manifest](../assets/delivery-governance/ARTIFACT_MANIFEST.template.json) when needed. When an artifact store already preserves provenance/hash/platform, record its query entrypoint rather than duplicate it.

## 5. Release Record

Every release or rollback attempt has a new `release_id` linking authorization time/source/scope; unit, environment, version, commit, Tag, artifact hash; start/end, entrypoint, operator, actual actions; backup/migration/config/service/traffic changes; each gate, health, identity, and core-flow result/evidence; failure point, partial success, production state, rollback decision, and remaining work.

It is append-only fact; never rewrite a failed attempt silently. Use [Release Record](../assets/delivery-governance/RELEASE_RECORD.template.md) or retain an equivalent external object ID/link.

## 6. Determine Production Truth

Use a sufficient combination for the release unit:

- actual platform deployment, image digest, package version, or static revision;
- public version endpoint, build metadata, or equivalent runtime identity;
- health/readiness, dependency connections, startup logs, error rate;
- affected user-visible core flow or business API;
- actual migration, queue, schedule, cache, and external-integration state.

Local tests, candidate docs, Git Tag, green CI, successful upload, one health endpoint, or deployment exit 0 cannot alone prove `released`. On conflict, remain unverified and investigate the target; docs never override runtime.

## 7. Failure, Partial Deployment, and Rollback

- After interruption, inventory every affected service, configuration, data, and traffic state before continuing or rolling back.
- Rollback addresses code/artifact, configuration, schema/data, and external effects separately. Redeploying an old image is not full rollback after an irreversible migration.
- A backup supports rollback only when identity, integrity, retention location, and restore entrypoint are verified. Material data change needs a restore exercise or equivalent evidence.
- Verify target version, health, and affected flow after rollback before `rolled_back`.
- Preserve failed records, incident evidence, and original `release_id`; a new attempt gets a new ID.

## 8. Boundaries with Other States

- Product `accepted` does not authorize release.
- Engineering provides quality evidence; Delivery decides whether release gates are met.
- Workflow Run Manifest owns internal production-run facts; Release Record owns launch attempts.
- Task state links these objects without copying release bodies.
- Hooks do not read credentials, execute releases, or grant authority from session phase.

## 9. Closeout

Ensure state does not exceed evidence/authority; revision, version, Tag, artifact, config, and environment correspond; the Release Record reconstructs every external action, check, failure, and rollback; target identity and affected flow are verified; and unreleased, unverified, failed, and rolled back remain distinct.
