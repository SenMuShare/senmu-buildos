# Deployment Verification and Safety

Use this standard for deployment design, documentation, release verification, and runtime safety in formally delivered projects. Engineering owns architecture fitness and unit/integration/contract/E2E design; Delivery decides whether executable release paths and their evidence satisfy the current release gate.

## 1. Deployment Documentation

Document local startup; formal/test environments; dependent services; environment variables/configuration; secret/certificate/private-config storage; build/deploy commands; health checks; post-release verification; rollback; routine release versus first-time/disaster-recovery scripts; artifact build/upload/retention/cleanup; and hardware constraints such as disk, memory, CPU, image count, and log retention.

For a project that actually deploys, deliver or maintain its smallest usable script/CI entrypoint alongside the procedure, within write authority. Reuse an existing runner; do not wait for repeated omissions to automate stable actions or prescribe a new platform. Bind version, source/artifact identity, target and recovery inputs at execution. Change the runner when its process, compatibility or environment changes, not merely because the product version increments; Git retains earlier runner versions. A source review does not install build dependencies just to inspect that runner.

Coordinate preparation, deployment, verification and [resource lifecycle](version-artifacts-and-release.md#4-retention-and-cleanup) through the existing entrypoint. Last consumers include release, cleanup and backup scripts' actual prerequisites, not only running services. Close generated local resources under task authority and release resources under the release contract. Aggregate partial failures and next actions there.

End with a project-tailored checklist covering target health and version, core pages/APIs, actual image/package/static revision, Docker architecture when used, affected core flow, startup errors, Tag/VERSION/changelog consistency, hotfix patch version/rollback/production path/unreleased changes, other unreleased changes, and known risks.

Never report only “deployment complete”; record actual results. Artifact-based releases verify the target object, not merely local build:

- Docker: running image tag/digest, architecture, container start time, health.
- Static site: deployed-file identity/time, key HTTP status, assets from this build.
- Backend: version endpoint, health, startup logs, dependency connections.

After a partially failed deployment that may have replaced services, reconcile production state before choosing rollback or retry. Never assume the old version remains.

### 1.1 Deployment Design and Change Scope

Use when establishing or changing a release driver, assessing its operability, or diagnosing recurring release friction; ordinary releases use the established entrypoint. Reuse Engineering's [operability scenarios](../../senmu-build-engineering/references/architecture-constraints-and-technical-debt.md#52-operability-scenarios) rather than creating another readiness review or register.

Inspect the current topology and actual entrypoint before recommending infrastructure. Distinguish product, release unit, component, image, running service and transfer package. Several services can consume one image. Select the smallest safe change scope from build inputs, resolved dependencies, configuration, shared consumers, API/schema compatibility and recovery requirements, not file count alone. Safe reuse does not require microservices or separate repositories; inexpensive coupled releases may remain appropriate.

Trace the selected scope through build, packaging, upload, import, service update, target verification and rollback selection. A skip in one stage does not remove fixed work in later stages. Keep one authoritative plan at the existing driver/manifest owner and derive its consumers; do not add a controller or duplicate component list for each phase. [Artifact composition](version-artifacts-and-release.md#31-composition-and-reusable-runtime-assets) owns mixed provenance and reusable resource identity. Configuration-only changes and target-side drift may need actions even when code is unchanged.

When repeated version omissions expose hand-synchronized rules, inspect the bounded affected call chain before another write. Derive release identity from its existing owner; retain genuine capability, schema and migration compatibility decisions. Do not replace narrow allowlists with unrestricted acceptance or turn every release into a repository-wide scan.

### 1.2 Cost and Maintenance Window

Use existing receipts to distinguish build, package preparation, transfer, import, startup/readiness, traffic or maintenance transition, affected-flow verification and retention closeout. Record newly executed versus reused work, elapsed time and actual transfer bytes where relevant. Directory logical size, transferred bytes and exclusive physical storage are different observations; cache hits do not prove that later transfer was skipped. Unknown measurements stay unknown.

Remove proven redundant work before accelerating it. Then compare bounded changes against the same representative workload and current constraints. Consider a registry, another host or a different deployment strategy only when remaining measured cost or risk justifies its operating burden; neither Docker nor whole-image transfer is intrinsically defective.

Move immutable preparation and applicable offline verification before the maintenance window only when authority, peak capacity, writer isolation and running-service safety permit it. Upload or import can still consume scarce shared disk and I/O. Preserve required draining, paid-task protection, stop-write, migration and live-state checks at the actual mutation boundary. Never shorten downtime by bypassing these protections or promise zero downtime on an unverified topology.

Track target identity, technical readiness, affected business verification, maintenance/public access and retention closeout as separate facts in the existing receipt. Required task/data reconciliation may block reopening; unrelated archive or bookkeeping failure must not become a new maintenance prerequisite. A service may be restored with cleanup pending, but the incomplete closeout remains owned and reported. Health alone does not prove public recovery, and cleanup success does not prove business acceptance.

### 1.3 Recovery Entrypoints and Evidence

For a new or repaired release/recovery path, exercise the real public command from a representative starting state with the relevant interpreter, working directory, import/package path, options, permissions and configuration. Check whether recovery depends on code, dependencies or state that the failed deployment may have removed. Use an isolated production-shaped fixture where sufficient; disclose untested target differences. A help command, mocked success or a run from the source root does not prove an operations-directory entrypoint works. Follow Engineering's [real verification path](../../senmu-build-engineering/references/software-testing-and-quality-verification.md#make-the-real-verification-path-usable).

Choose a consequential interruption boundary and verify through the existing driver that completed side effects are not replayed, unknown outcomes are reconciled and authorized continuation can reach the required restored state. Reuse [Run State and Recovery](../../senmu-build-workflow/references/workflow-run-state-and-recovery.md#5-recovery-decision) and [production reconciliation](release-authorization-and-production-truth.md#7-failure-partial-deployment-and-rollback); do not create another recovery engine or manually edit execution markers.

Calibrate startup/readiness and outer wait budgets from observed phases and total elapsed time. A timeout or cancellation of the waiter does not prove the underlying action stopped or failed. Refresh actual state, then choose bounded waiting, resume, forward repair or rollback within authority. Do not blindly restart the whole flow, keep extending a deadline without evidence, or remove uniqueness/idempotency protection. Recovery covers affected code, configuration, data, tasks and public access, not just old images.

Active operations use Project's [incident execution boundary](../../senmu-build-project/references/task-execution-and-state-management.md#44-incident-execution-boundary). An organizational or architecture improvement cannot become a new prerequisite for the current operator to reach a safe point.

## 2. Resources and Artifacts

[Version, Artifact, and Release](version-artifacts-and-release.md#4-retention-and-cleanup) owns identity, retention and cleanup. Apply it to real environments.

Confirm that every real resource surface has managed scope, retention, disk cap, dry-run, cleanup entrypoint, and receipt; do not invent nonexistent registries. Verify current and rollback objects before cleanup, using image digest/ID rather than movable tags. Delete old tarballs, images, uploads, and dangling objects only when precisely owned by this unit; never global-prune across projects. Logs/uploads need retention.

Choose the build location from actual builder/runtime volume capacity, platform compatibility, reusable results and whole-path cost. A small runtime server is a reason to evaluate off-host builds, not proof that the local machine has capacity or that another cloud machine is necessary. Keep measured available space separate from estimated peak demand and reserve; when inputs are stale or missing, use a fresh observation or bounded sample before claiming a capacity shortfall. Reuse Workflow's [storage-pressure method](../../senmu-build-workflow/references/workflow-materials-and-deliverables.md#8-task-resource-closeout); do not create another capacity gate.

Document artifact naming/location, retention policy/source (or BuildOS rollback default), cleanup, rollback retrieval, and whether server-side builds are allowed. For adoption or a release-driver change, trace producers through cleanup and aggregate status in the actual driver after target verification. Exercise repeated releases, an omitted/disabled group and partial failure with disposable fixtures; verify resource bounds and current/rollback/shared-consumer protection, not only helper exit codes. Reuse project capacity budgets; do not require physical-space claims from logical fixture counts. A generated config, an enabled flag or a dry-run is not evidence that production, local Docker or another surface ran cleanup. Ordinary releases reuse the configured driver; do not repeat project-wide governance.

## 3. Testing and Acceptance

Accept impact-matched Engineering evidence under its [Evidence Reuse and Handoff](../../senmu-build-engineering/references/software-testing-and-quality-verification.md#evidence-reuse-and-handoff) contract. At preflight, integration, artifact preparation and deployment, map still-valid results to current obligations; changing stages does not reset verification. Run missing or invalidated checks and record gaps in the existing receipt. Artifact contents/platform, target configuration, runtime identity, health and rollback are distinct obligations that development tests cannot discharge. A preflight build may supply artifact preparation only when its inputs and retained outputs satisfy that contract; packaging still verifies the resulting package/image. Do not add caching machinery merely to express this policy.

Distinguish:

- unit/component tests for functions, components, boundary states;
- API/business tests for authorization, billing, isolation, failures;
- real-flow tests for the user's full core task.

Mocks may cover component state, third-party failure, and pure boundaries. They cannot replace core acceptance for upload, payment, export, authorization, file processing, playback, orders, or AI jobs.

State affected paths, tested paths, untested paths and risks, and whether production verification is needed.

After a Bug/Hotfix passes Engineering checks, also determine version/changelog update; Work Log cause/fix/evidence/risk/next step; and, if releasing, Tag/artifact/production evidence/rollback point. If not releasing, record reason, code location, and future release condition.

### Public-service exposure

For a new service, first establish whether and how it is reachable. Public exposure or changes to network/runtime trust use the [public-service baseline](security/public-service-security-baseline.md). Keep actual control configuration and evidence in the deployment owner; an initialized document is not live protection. Source-only projects keep their existing path.

## 4. Security and Sensitive Information

Do not commit `.env`/`.env.*`, API/access/secret/app keys, payment keys/certificates/private or SSH keys, user uploads, database files, real production data, local runtime data, or private server configuration.

May commit `.env.example`, redacted templates, secret-free deployment scripts, and redacted technical/test docs.

Identity, permissions, payments, upload, deletion, export, and administrator actions require backend enforcement. Hidden frontend controls are not authorization.

## 5. High-Risk Functions

Inspect server boundaries for login/registration/password reset; admin actions; payments/orders/refunds/balances; upload/download/export/delete; tenant/user isolation; third-party secrets; AI calls and cost accounting; and public static-file access.

If any relies only on hidden UI, client validation, or mock data, stop the candidate and return it to Engineering. Delivery does not patch business code during deployment unless repair is also authorized.

Resource retention, actual distribution contents and truthful disk-space reporting use [Artifacts and Release](version-artifacts-and-release.md); ordinary material recovery uses Workflow’s material owner. Do not duplicate or weaken those cleanup contracts here.
