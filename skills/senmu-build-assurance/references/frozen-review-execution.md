# Frozen Review Execution

Use this optional helper for an interrupted, multi-batch or explicitly coverage-tracked Git review. Engineering can use it without activating Assurance. It does not add reviewers, approve a change, discover every symbol or prove a finding true. Ordinary small reviews keep their existing path.

## Ownership and input

Delivery owns the frozen `git_review_scope`; [review governance](independent-review-and-evidence-grading.md) owns findings and conclusions. The [execution helper](../scripts/manage_review_execution.py) owns only file identity, declared changed-range coverage and execution receipts. Do not introduce a second task register. Link its execution record from the existing review/task record.

The host performs semantic review. The helper makes no model/API calls and installs no external reviewer. Prepare business context from the existing requirement and technical owner: intended outcome, preserved behavior, cancelled work, applicable rules, affected contracts and unknowns. The `--rules-identity` argument is the caller's explicit identity for that effective rules/context package, preferably its content digest. It is required on every operation; the helper compares it but does not discover or hash undeclared project rules automatically.

Keep records and receipts in an explicitly authorized directory outside the reviewed worktree and Git metadata. Mutations require POSIX file locking; use canonical paths without symlinks. Source is read from original frozen Git blobs with replacement objects disabled and raw blob IDs rehashed. Explicit repository selection ignores inherited repository/object-routing and injected per-command configuration variables; normal Git configuration is not edited. Actual per-worktree and common Git metadata directories are queried, not inferred from a `.git` path component. Source is never substituted from a dirty worktree. There is no automatic project migration.

## Commands

Save Delivery's existing `manage_change_unit.py review` JSON as `scope.json`. Commands below use shell variables for the actual worktree, authorized record destination, helper and effective rules identity:

```bash
python3 "$HELPER" init --repo "$REPO" --scope "$SCOPE" --record "$RECORD" --rules-identity "$RULES_ID"
python3 "$HELPER" status --repo "$REPO" --record "$RECORD" --rules-identity "$RULES_ID" --limit 10 --offset 0
python3 "$HELPER" evidence --repo "$REPO" --record "$RECORD" --rules-identity "$RULES_ID" --item "$ITEM_ID" --side head
python3 "$HELPER" receipt --repo "$REPO" --record "$RECORD" --rules-identity "$RULES_ID" --item "$ITEM_ID" --state completed --receipt "$RECEIPT"
```

`init` preserves an existing matching record byte-for-byte and rejects a different snapshot or foreign file. `status` and `evidence` do not write. Delivery scope, execution and the approval Git identity check share the [canonical inventory](../../senmu-build-delivery/scripts/git_review_inventory.py): fixed rename policy, NUL-delimited paths and stable ordering. Git quoting, order and rename configuration must not split their file sets. The summary contains disjoint pending/completed/failed/validly-reused/invalid-source counts, remaining IDs and attempts, and `next_offset`; read the record for complete details. A successful status query is not a successful coverage check. Invalid external sources are shown as `invalid_source`, preserving the stored `reused` receipt without counting it as valid completion.

`evidence` emits hashes and line ranges, not source content. It defaults to the entire selected side; `--start` and `--end` select a precise range. Use `--side base` for deleted content and the old side of modified/renamed files. A completed receipt needs evidence for every existing side, covering every changed range. Multiple nonduplicate ranges per side are allowed; unchanged anchors alone cannot stand in for changed code. Zero-width insert/delete sides bind the nearest surviving boundary line. Adds, deletes and metadata-only changes bind full existing sides. The default whole-side proof is sufficient for these input ranges. Line coordinates count raw LF bytes, preserving CRLF, lone CR, Unicode separators and a missing final newline exactly; empty text has range `0..0`. Both old and new sensitive paths are guarded before blob reads; symlinks, submodules, binary/non-UTF-8 or over-limit contents remain unverified rather than disappearing from coverage. This is path protection, not a general secret scanner or binary reviewer.

## Receipts and recovery

A receipt is a JSON object containing `run_id`, `snapshot_identity`, `item_id`, integer `attempt`, `state`, and `executor`, copied from this run's current identifiers. For `completed`, add a meaningful `summary` and an `evidence` array containing the helper's exact proof objects. For `failed`, add `reason`. A proof binds side, blob, file digest, line range and range digest; it locates evidence, not the truth of the review summary.

Identical receipts are idempotent. A conflicting terminal result, another run/snapshot/item, or an old attempt is rejected. The record is revalidated against Git, stored proofs and required changed ranges before counting completion. A mutation validates the existing record once and the incoming result separately; bounded batch reads and command-local caches avoid duplicate immutable reads. Caches never persist across invocations, and final `check` revalidates the current record and evidence. Unknown schemas, omitted inventory, fabricated states and missing receipts fail closed.

```bash
python3 "$HELPER" retry --repo "$REPO" --record "$RECORD" --rules-identity "$RULES_ID" --item "$ITEM_ID" --run-id "$RUN_ID" --expected-attempt "$ATTEMPT" --operation-id "$OPERATION_ID" --reason "executor recovered after interruption"
```

Retry only pending/failed work, not completed work. Capture the run and expected attempt from the observed record, and choose one stable operation ID per intentional retry. Resending that same request returns its original transition without another increment, even after later progress. A different request targeting an old attempt or reusing an ID for changed intent is rejected. Do not refresh the expected attempt or generate a new ID merely because transport was interrupted. This preserves prior attempts and failures and prevents both old results and old retry requests from cancelling new work. Do not call `init` to erase progress. Concurrent mutations serialize with a nonblocking OS lock; a busy caller retries its operation. Atomic replacement avoids partial JSON writes.

`reused` additionally requires `source.record` and `source.receipt_identity`, referencing a retained, valid `completed` receipt in another run of exactly the same snapshot and rules. `source.record` must be an absolute canonical, non-symlink path. Relative paths are rejected at admission, never resolved against the current shell directory. Legacy relative-source records remain inspectable as invalid-source evidence; explicitly reopen their affected items rather than guessing their original directory. The receipt identity is its canonical sorted-JSON SHA-256. Its evidence must match. Validate the source record identity/inventory and the referenced directly completed receipt; unrelated reused items do not create a chain for this receipt. Invented links, missing required sources, tampered target proofs and actual chained reuse are rejected. This is not an approval of unrelated source-record findings. Resuming the original run is normally simpler. A new code/rules/context snapshot starts a new record; changed-snapshot reuse and automatic impact analysis are not implemented. Apply Engineering's evidence-reuse judgment without claiming the helper automated it.

## Recovering an invalid external source

A malformed local envelope, changed inventory or incorrect local proof still blocks the entire operation. If those local facts are valid but one external reuse source is missing, unreadable, wrong or unsupported, `status` reports that item separately and unrelated pending work may continue. Final `check` remains nonzero and incomplete. Restoring the exact valid source restores validity without editing this record.

```bash
python3 "$HELPER" reopen --repo "$REPO" --record "$RECORD" --rules-identity "$RULES_ID" --item "$ITEM_ID" --run-id "$RUN_ID" --expected-attempt "$ATTEMPT" --operation-id "$OPERATION_ID" --reason "source unavailable; explicitly re-review this item"
```

`reopen` is restricted to a reused item with invalid external evidence and still-valid local proofs. It preserves the original receipt, its identity, the invalidation reason and the request, then starts a new pending attempt. It cannot erase valid reuse or directly completed work. The same causal/idempotent request rules as `retry` apply under the existing mutation lock. Re-review and submit a fresh receipt; no old result is promoted to new work or approval. A source restored before this command means there is no invalid item to reopen.

## Coverage is not approval

```bash
python3 "$HELPER" check --repo "$REPO" --record "$RECORD" --rules-identity "$RULES_ID" --base "$BASE" --head "$HEAD"
```

A project that adopts execution coverage can connect it to the existing approval entrypoint in one command. From the BuildOS product root, use the actual authorized repository, retained execution record, approval record and expected rules identity:

```bash
python3 skills/senmu-build-delivery/scripts/validate_change_review.py --record "$APPROVAL_RECORD" --repo "$REPO" --execution-record "$RECORD" --rules-identity "$RULES_ID" --require-current-head --required-review peer
```

Keep the project's adopted `--required-review` level; `peer` here is an example, not authority to downgrade it. The gate validates the retained execution record against its exact base/head and expected rules, rechecks complete nonempty coverage and uses the captured pairing instead of repeating similarity detection. Pending/failed work, invalid reuse or mismatched inputs block. Findings, quality checks and approval requirements are still checked separately; coverage never promotes a draft or grants approval. The standalone `check` remains useful for execution diagnostics. Projects not adopting coverage retain the legacy invocation without both new options; adopted callers must supply both, and `--repo`. No project command is silently migrated. Empty inputs are skipped, not passed. Failed or pending files cannot be waived into completion. Newly completed and validly reused counts remain separate. `quality_outcome` and `approval_outcome` always remain `not_assessed` here.

Keep review findings in their existing owner, including counterevidence, original failure, impact, disposition and recheck condition. A complete file receipt may contain real defects. Machine consistency, semantic review, product acceptance, private release and local activation are separate facts.

## Schema-3 upgrade

BuildOS 2.21.2 uses execution schema 3 for corrected LF coordinates, canonical inventory policy and changed-range coverage. Schema-2 records are retained as historical evidence, never overwritten or silently promoted. Recapture the scope through current Delivery, retain the old record, and run `init` at a new authorized record path. Recheck actual coverage and submit new schema-3 receipts; do not merely edit the schema number or present old runs as newly executed. Same-schema interruption recovery remains unchanged.

`execution_complete` means all required file receipts have verifiable declared input coverage. It does not prove that a model read every line, that every defect was found, or that findings were closed. Finding disposition and project approval retain their existing owners. Unsupported binary/oversized/encoding inputs still require a separately authorized review path; this patch does not add a waiver or an alternative-evidence importer.

## 2.21.3 caller compatibility

Valid schema-3 records and legacy pending/failed retry history remain readable; no bulk record migration occurs. New retry/reopen callers must supply run, expected attempt and operation identity. Reopened history uses the versioned operation extension and retains its prior reused receipt; an older runtime may reject that history and must not be used to mutate it. Historical replacement-derived proofs fail revalidation instead of being silently accepted. Schema-2 handling remains unchanged. Diagnostic recovery never weakens the final check, findings or project approval.


A new Delivery scope carries its captured `inventory_items`. Initialization and later checks validate that pairing against every raw add/delete/modify object, without repeating attribute-dependent similarity detection. New snapshots bind the captured inventory identity; older schema-3 records are checked by the same complete raw-input comparison and are not rewritten. A rename grouping does not prove historical intent. Legacy scopes lacking captured items can still be initialized only if their declared paths match the current capture; otherwise recapture. Reuse still requires the identical snapshot identity; do not silently promote old results to a newly shaped snapshot.

Machine diff reads isolate inherited display options. JSON reads are byte- and depth-bounded: malformed local records block; malformed external sources use per-item diagnosis and explicit reopen. Each operation retains a bounded source-file view for repeated references, rechecks every referenced receipt, and discards that view before the next command. No cache is an approval or a cross-session verdict.
