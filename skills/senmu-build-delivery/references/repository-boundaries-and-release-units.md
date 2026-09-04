# Repository Boundaries and Release-Unit Governance

Use this standard to decide repository/release-unit boundaries for multi-product, multi-team, or multi-agent projects and govern versions, artifacts, interfaces, migrations, and public-contribution flow. It is not a directory-cleanup guide.

## 1. Triggers

Assess boundaries when one repository contains products/subproducts, website, admin, user/mobile clients, open APIs, or shared packages; teams/agents work on subsystems with different cadence; one release repeatedly needs stash/exclusion of another's work; several VERSION/changelogs/Tag prefixes/deploy scripts exist; an independently buildable/deployable/rollbackable subsystem is blocked by other workspace state; or the owner asks whether code will conflict, repositories should split, or teams should coordinate differently.

Use only lightweight reference for an early single-person prototype, one-off validation, tool without formal release, ordinary modules/pages inside one app, or naming disorder under one shared version/release.

## 2. Concepts

- **Product family:** related products sharing brand, identity, strategy, or standards, not necessarily a repository.
- **Repository boundary:** code, docs, version, and release responsibilities carried by one Git repository, selected for collaboration/delivery rather than directory habit.
- **Release unit:** system/service independently buildable, deployable, rollbackable, versioned, and changelogged, whether in monorepo or standalone.
- **Interface contract:** API, event, SDK, read-only database view, or file protocol between units; after a split, implicit same-repository editing is forbidden.
- **Authoritative working directory:** owner-approved daily entrypoint. Branches, worktrees, clones, migration staging, and builds may multiply, but one unit has one current code/ledger/formal-delivery source.
- **Publication model:** private-only, public-native, or private authority producing a controlled public projection. In the last model, public is not editable source authority; contributions enter private authority and are reprojected.

### 2.1 Governance Levels

| Level | Typical form | Strategy |
| --- | --- | --- |
| L0 Small monolith | One app, one person/early validation, no formal release | One repo; README covers start/test and excludes data from Git |
| L1 One product, several directories | Site/frontend/backend released together | Monorepo; one VERSION/changelog or service notes |
| L2 One product, several release units | Site/client/admin/backend independently deploy | Monorepo is valid with a unit register, path boundaries, independent VERSION/changelog/Tag |
| L3 Peer products on shared platform | Shared account/login/payment/admin/data foundation | Define units/data first, then choose mono/multi by team, permissions, blocking, shared code, CI; use explicit contracts |
| L4 High-concurrency teams/agents | Distinct teams/vendors/agents and cadences | Multi-repo, or strong path gates, CODEOWNERS, CI filters, independent pipelines |

Escalate when unfinished work blocks another unit repeatedly; releases need path exclusion/stash; units already have separate version/changelog/Tag/deploy; or shared identity/payment serves peer products whose ledgers, balances, orders, cost, or metrics must remain distinct. De-escalate when there are no real release users, one maintainer always ships everything, or alleged subprojects are inseparable pages.

### 2.2 Public Contributions into Private Authority

For private-authority/public-projection projects, a public PR is an inbound candidate:

1. Freeze public base/head, files, and source link. Public CI validates public content and has no private credentials.
2. Compute semantic diff from public base and import only allowlisted paths into a new internal Change Unit. Projection markers, private paths, unknown paths, or sensitive content fail closed. Never pull/merge public `main` into private main.
3. Resolve in internal authority with Product/Engineering decisions, privacy checks, and matching verification, then commit internally.
4. Regenerate the public projection from that internal commit onto an empty staging surface and verify contribution intent, preserving author attribution/PR link.
5. Only under public-update authority commit the public candidate and update/close the PR with final public commit. Contribution intake, internal merge, and public release are separate records.

All later edits still enter private authority first. If external contributions become the main development flow, evaluate a deliberate migration to public-source authority with private governance/release overlays. Never mix models.

## 3. Monorepo vs Multi-Repo

Continue monorepo when most apply: same team and cadence; strong path-scoped CI/CD; CODEOWNERS/branch protection/path review/deploy boundaries; substantial shared code requiring synchronized validation; unified version/release is meaningful; and the team can maintain workspaces, package versions, changesets, and dependency impact. Without these, unified management becomes mutual blocking.

Prefer multi-repo when most apply: independent teams/partners, product identity/roadmap/customer entry, build/deploy/rollback, versions/changelogs/artifacts/acceptance, mostly API/file collaboration rather than source sharing, frequent cross-unit blocking, or distinct permissions/cadence/responsibility. Its interface, shared-package, cross-repo release, and documentation costs remain real.

## 4. Identify a Release Unit

Ask whether the subsystem has an independent user/service responsibility, build, deploy, rollback, version/changelog need, owner/team, test/production verification path, and failure blast radius. A majority supports an independent unit. Repository splitting then depends on collaboration, authorization, blocking, and shared-code cost.

Do not invent a unit for an internal page/module that cannot deploy or roll back separately.

### 4.1 Repository and Release Unit Register

Multi-product/unit projects maintain `governance/REPOSITORY_AND_RELEASE_UNITS.md` or equivalent. Without it, an agent cannot casually decide to release units together.

Record for each unit: product/subproduct, path/repository, entry/service, VERSION, changelog, Tag prefix, build command, deploy/restart scope, shared dependencies, and prohibited inclusions.

The register answers which units share identity/account/payment/database/API; which data requires separate ledgers/balances/orders/usage/cost/metrics; which units release independently or together; and which paths/services are excluded by default.

## 5. Split-Assessment Gate

Do not continue relying on stash, temporary exclusions, or verbal agreement when several teams have dirty work in one workspace; release scripts ignore unrelated subprojects; one Tag/version cannot identify the shipped subsystem; a hotfix is blocked by another unit; agents mix logs/versions/release records; or the owner repeatedly reports conflicts and differing cadences. These are boundary, unit, or script-governance defects, not merely operator mistakes.

## 6. Migration Strategy

Avoid big-bang splits. Move low-coupling, low-risk, clear-entry projects first (site/docs/static frontend); then independent frontend on shared APIs (admin); then core platform/backend; finally shared packages, SDKs, types, design tokens, and common scripts.

Do not create a large shared package first. Allow small temporary duplication until boundaries stabilize.

## 7. Pre-Split Gate

Confirm target and rationale; current product/unit/owner; target repository name, README, VERSION, changelog, deployment/testing docs; history-retention method such as `git filter-repo`/`git subtree split`; cross-directory imports, relative paths, shared scripts/config; environment/secret ownership; shared database/storage/uploads/payment/permissions/session; release scripts, artifacts, image Tags, rollback; migration freeze window; and rollback to original layout.

## 8. Post-Split Acceptance

Verify independent install, build, test, and startup; own README/VERSION/changelog/deploy docs; no duplicate active source in old repository or explicit read-only archive/migration status; production release/rollback points to new artifacts; CI/manual release cannot ship another repository; documented compatible contracts; team awareness of repository/branch/release; and updated project index.

### 8.1 Governance Migration Package

A split migrates more than source. Each extracted formal unit closes:

- README with repository role, startup, docs, exclusions.
- VERSION/changelog continuing the real product line—never arbitrary `0.1.x` unless an unshipped prototype.
- Tag prefix and old/history policy.
- Build, artifact, deploy, health, rollback documentation.
- Independent preflight, real-flow acceptance, and unverified risks.
- Work Log of migration, evidence, retired paths, next step.
- Updated unit register.
- Archive location/read-only status for old repo/scripts/snapshots/temp paths.

Perform a real or rehearsed release proving the unit can independently build/package/deploy/start from the new repository. Directory movement alone is not governance completion.

## 9. Interface Contracts

- HTTP uses OpenAPI, interface tables, or equivalent.
- SDK/shared packages have version, changelog, compatibility.
- Events/messages/jobs/files specify fields, states, retry, failure handling.
- A frontend repo never imports another backend repo's internals.
- Services do not casually write one core table; shared databases define read/write boundaries.

Compatible changes release normally. Breaking changes need migration and dual-read/write or progressive rollout. Payments, authorization, accounts, balances, orders, and user data use high governance.

## 10. Multi-Team and Multi-Agent Rules

- Every task declares target repository/unit, writable paths, and exclusions.
- Before release, detect unfinished work from other units.
- Never mix unit versions, Tags, changelogs, or Work Logs.
- For temporary same-repository work, use branches/worktrees/path scopes rather than long-lived stash.
- Declare authority root at start. An external worktree isolates development but gains no project-root, ledger, or delivery authority.
- After split/migration/main replacement, the old directory is read-only archive or ceases as an active entrypoint; one unit cannot retain two current directories.
- Preserve and isolate unrelated subprojects, branches, worktrees, and POCs. Do not roll back, force into main, or include them unless candidate reachability, scope, or shared production resources prove an effect.

Task boundaries/recovery belong to Durable Task State. Add these delivery fields:

```markdown
### Current Task Boundary
- Target product/subproduct:
- Target repository or directory:
- Target release unit:
- Writable paths:
- Explicit exclusions:
- Shared dependencies/interfaces:
- Coupled release required:
- If another release unit appears: stop, report, and exclude from this commit/release.
```

Release blockers:

- Stop when `git diff --name-only`/PR files leave allowed paths and explain provenance.
- Unit VERSION, changelog, Tag prefix, build, and deployed service must agree.
- A frontend/site-only release does not restart backend, database, or other clients unless in scope.
- Changes to shared identity, account, payment, authorization, or database schema escalate governance and require reassessment of all affected units.
- If code, ledgers, artifacts, and scripts point to different working directories, stop and close authority under Code Management first.
- Private-to-public projection starts from empty staging using an allowlist, scanning paths, identity, secrets, and internal owners and binding approval to candidate identity. Never archive the whole private Git root and rely on blacklist deletion.

## 11. Project Adoption

Persist as `governance/REPOSITORY_AND_RELEASE_UNITS.md` or merge into existing `governance/GOVERNANCE.md`, `delivery/RELEASE_PLAN.md`, or `delivery/BRANCHING.md` with product-family relationships, unit register, repository list, each unit's owner/version/Tag/deploy/rollback, interface-owner paths, and migration phases/freeze windows.

## 12. Responsibility Split

- Project directory standard owns directory/document placement.
- Version/artifact standard owns versions, Tags, artifacts, deployment, rollback.
- Code-management standard owns branches, integration, review, unreleased boundaries.
- This standard owns repository/release-unit decisions and mono-to-multi migration.

For naming/layout only, use the directory standard. When teams, release, versions, and workspaces block one another, use this standard.
