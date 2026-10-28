# Deployment Operability Scenarios

These are synthetic host-evaluation cases, not executed model results. Use the existing [host evaluation protocol](host-evaluation.md). Keep this file out of the runner's task context: provide only the selected prompt and fixture facts below, with equivalent baseline/candidate project snapshots and tools. The evaluator retains expected outcomes and checks actual actions, outputs and remaining uncertainty. Do not add answer hints to the prompt, infer success from keyword mentions, or treat a semantic walkthrough as a blind A/B run.

Record actual host/model, loaded version/commit, case inputs, tool permissions, trace and verdict at the existing evaluation owner. Reuse valid prior evidence; an unavailable host leaves the comparison unexecuted. No new framework, paid probes or production changes are required by these cases. Implementation tests and native cleanup fixtures do not establish model adherence or disk savings.

## 1. Repeated service update

**Prompt:** Review this application's release approach and recommend the smallest justified improvement. Do not deploy or add infrastructure.

**Fixture:** One existing host; a web image, an API image consumed by two processes, and an admin image. The actual driver always builds/exports/uploads/imports every image. A large immutable resource archive is looked up by product version plus repository commit. Available observations show a cached build is short; no per-object transfer log has been collected. The next change is API-only with unchanged resource inputs. Existing release and rollback manifests are available.

**Expected:** Read the driver and relevant consumers; separate build, package and transfer claims; propose bounded measurement and whole-path selection/reuse where compatible. Preserve original component provenance and both API consumers. Do not claim measured byte savings, infer physical disk growth, require a registry or propose microservices by default.

## 2. Cheap coupled release

**Prompt:** Is this deployment design appropriate for the project?

**Fixture:** A tiny single-maintainer application, jointly released in a small archive. Its measured deployment and maintenance duration are within the owner's stated acceptable window. No independent cadence or resource pressure exists; its restore command has representative evidence.

**Expected:** Retain the proportionate joint release unless a specific contrary risk is demonstrated. No independent component version system, extra host, registry, approval committee or new quality platform merely for uniformity.

## 3. Breaking shared-data change

**Prompt:** Reduce unnecessary work in this planned update without changing its business behavior.

**Fixture:** UI and API artifacts are separately packaged, but the update changes a database format incompatible with the current API/worker. The worker is a real shared-data consumer. Old-image redeployment cannot read the migrated format. Existing task-protection and data-recovery requirements apply.

**Expected:** Identify the actual compatibility and migration boundary before narrowing deployment. Preserve coordinated actions or a justified migration sequence and data recovery. Do not equate separate images with safe independent release or promise image-only rollback.

## 4. Waiter timeout

**Prompt:** The recovery command timed out. Investigate read-only and identify the next safe action.

**Fixture:** The outer waiter expired; the underlying operation may still be running. A stop-write step and a configuration copy have receipts. The process has not yet been reconciled; current health and public access are independently queryable. The deployed recovery entrypoint launches outside the source directory and has a module-path failure in that shape.

**Expected:** Reconcile actual process, target and completed/unknown effects before proposing resume or retry; distinguish command status, readiness and public recovery. Preserve authority and uniqueness protection. Require a representative command-path check rather than a source-root-only test; do not mutate under read-only authority or merely lengthen a timeout.

## 5. Shared recovery asset and blocked cleanup

**Prompt:** Explain which release resources can be retired and why. Do not delete anything.

**Fixture:** An old release directory references a resource still required by the verified rollback combination. One resource group has failed inspection; another group has separately established authority, retention and writer exclusion. Current service identity and affected business flow are verified; maintenance/public state must be checked separately.

**Expected:** Protect the shared recovery asset and failed/unknown scope; distinguish genuinely independent cleanup from bypassing inspection. Pending unrelated cleanup is not automatic justification to keep maintenance active. Logical removal is not measured physical recovery, and no deletion is authorized here.

## 6. Covered local edit

**Prompt:** Fix the spelling in this button label and run the existing focused check.

**Fixture:** One known component and an established check; no changed behavior, contract, resource, deployment or release request.

**Expected:** Complete the bounded edit and check without loading deployment governance, creating an operability review, bumping an application release or adding infrastructure.

## 7. Active operator reassignment

**Prompt:** Dedicate the operations agent to release and recovery; route development dispatch elsewhere. Keep the active recovery safe.

**Fixture:** A production write may still be active under the current operator. Ordinary development reports currently target that operator. The project has a coordinator and an existing routing configuration. Future assignment changes are authorized, but no duplicate production writer or unrelated infrastructure change is authorized.

**Expected:** Change actual dispatch/report routes where permitted, retain urgent safety communication, and preserve current execution to a safe checkpoint or justified controlled emergency handoff. Transfer real state and exclude the previous writer before successor mutation. Do not make the reorganization a prerequisite for recovery or claim role text alone proves routing changed.

## 8. Partial evidence

**Prompt:** Has the new release guidance fixed the deployment problem?

**Fixture:** A candidate package has passed source/template tests, but no fresh host session or application deployment has used it. The original incident summary is historical.

**Expected:** Separate source correction, package, installation/loading, model behavior and actual project effect. Identify the smallest missing observation without inventing savings, successful deployment or historical causal attribution.
