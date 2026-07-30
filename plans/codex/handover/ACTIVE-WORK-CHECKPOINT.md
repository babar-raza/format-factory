---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-EVENT-29
artifact_type: active_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Active Work Checkpoint

Committed checkpoint status: `RESUMABLE`

Shared-workspace transfer status at capture:
`RECOVERY_REQUIRED_RED_OBSERVED`

The underlying Event 29 boundary remains `CLEAN_COMMITTED_GITLAB_MAIN` at
GitLab head `edcc121152e4a238b62c33180f9e733badfde4b7`. The current working
tree adds a seven-file content-addressed overlay that is deliberately frozen
for lossless provider adoption.

`RESUMABLE` means a clean checkout can reconstruct Event 29 without any
provider-local byte, lease, token, execution manifest, or chat history. It
does not authorize a provider to skip fresh coordination registration and
exact-path claims.

It does not mean the current worktree is clean. A clean checkout would omit
the Partial-002-A adjudication work. Claude must adopt the local overlay from
[INFLIGHT-RECOVERY.yaml](INFLIGHT-RECOVERY.yaml) before continuing or it would
lose valid work.

XLIFF implementation checkpoint:
`315efa5f5f4420202b5254c86ccd8863a91c385f`

Controller/Event 29 projection checkpoint:
`c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0`

Native controller:

- state: `CONTRACT`
- event: `FF6-EVENT-000029`
- event hash:
  `de12acdefd04c37a918e3fd27dcb8dd076f53e576ee7049cf1efc732d02028bb`
- task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`
- task state: `WORK_IN_PROGRESS`
- first unmet step: `XLF-04`
- exact next microstep:
  `XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION`

Completed:

- `XLF-01`, `XLF-02`, `XLF-03`
- `XLF-04-BATCH-001`
- `XLF-04-BATCH-002`
- `XLF-04-BATCH-003`
- `XLF-04-BATCH-004`

Batch 005 partial evidence is bound to implementation commit `315efa5f`.
Current evidence is:

- 64 focused tests pass.
- 94 format-contract tests pass with one documented baseline-known stateful
  CSV test deselected.
- 69 production-program tests pass.
- Ruff, strict Mypy, Pyright 1.1.411, and bytecode compilation pass.
- Five of five XLIFF authority records match.
- Matrix, denominator, inventory, and candidate census check modes pass.
- Three census generations are byte-identical at
  `24c1902b6387cc9fa3402f78392ba91c6e6656407719ec11cfaab1c4f3d22b9e`.

Truth limit:

- All 1,130 candidate rows are content-, occurrence-, member-, profile-, and
  authority-bound, and the validator replays their source bytes.
- All 1,130 dispositions remain generated, deterministic proposals with zero
  independent semantic verification.
- The generator scans full semantic locations and requirements with
  keyword rules. Incidental XPath context names can therefore over-map a rule
  to unrelated hierarchy or cardinality obligations.
- 25 of 105 expected IDs have source-bound obligations.
- 80 expected IDs have no source-bound obligation.
- Candidate routing to 45 IDs is not obligation resolution.
- 60 expected IDs have no candidate mapping.
- All existing obligation rows remain `SOURCE_BOUND_UNVERIFIED`.
- XLF-04 and XLF-05 through XLF-08 remain.
- UBL package/root census and full 34-fact SAL authority replay exist; Event
  28 additionally binds the first UBL-03 root/type graph primitive. UBL-03
  through UBL-08, product
  implementation, verification, certification, extraction, and release
  preparation remain.
- Production certification remains `0/6`; promotion remains `UNASSESSED`.

Exact next action: follow [CLAUDE-START.md](CLAUDE-START.md),
[NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml), and the current
[Event 29 runbook](event-29/RUNBOOK.md). Events 25 through 28 remain immutable
history.

## Current recovery overlay

The earlier five-path Batch 005 recovery set is fully represented by
implementation commit `315efa5f` and native Event 29. A later seven-file
Partial-002-A overlay is now present:

- 3 tracked modified paths and 4 untracked paths;
- one content-addressed adjudication compiler/validator;
- one independent decision source and generated projection;
- 13 adjudication tests passing;
- one obligation-compiler test failing RED for the expected missing gate.

The overlay is not transferable by lease or provider token. The outgoing
identity releases its leases. The incoming provider registers a new identity,
verifies every byte hash, claims the paths, creates fresh manifests and
authorizations, and resumes at the compiler RED.

If unexpected dirty bytes appear after checkout, they are new evidence.
Preserve and classify them; do not interpret either the resolved Event 29
history or this exact seven-file record as permission to discard or adopt
different bytes.

## Parallel UBL checkpoint

Commit `7b5cce4fefaf3b7e8c4d1f1891821d1bfcd7acce` added a secure,
deterministic UBL 2.3 package census with:

- 890 package files;
- exactly 91 maindoc schemas and 91 unique root QNames;
- 15 common XSDs, 212 total XSDs, 76 official examples, and 14 code-list
  resources;
- 12 focused tests;
- passing Ruff, strict Mypy, Pyright, bytecode compilation, and 69-test
  production-program regression;
- three byte-identical report generations with SHA-256
  `787c8d9258dc25a8662ee934b9b0b14096de790db87826dab970792b9494976d`.

Commit `7fc49c290bdbfcb8c27bb8ca5c39f6f5576f242c` then repaired the stale
prose-target closure, replayed the canonical receipt deterministically, proved
all 34 facts promotable, and regenerated all descendant capability/
obligation invalidation inputs without changing their semantic scope.

Commit `f98d220a0a3903b1107de90b2e39bf480ec4b19d` adds the first deterministic
UBL-03 root/type binding primitive: 106 schemas, 91 roots, 182 nodes, 91
edges, and graph digest
`7b754187690ce1bb04db62657cfb552653cb381a1bdd745a56856e58215af029`.

This remains `VERIFIED_PARTIAL_NON_PROMOTING`. Event 28 binds that primitive,
the UBL taskcard is `WORK_IN_PROGRESS` at
`SCHEMA_GRAPH_ROOT_TYPE_BINDING_PARTIAL`, and XLIFF remains the canonical
active task. If the exact XLIFF scope is live-leased to another current
worker, the next disjoint UBL action is `UBL-03-PARTIAL-002`; it does not
replace XLIFF in the controller. See
[PARALLEL-UBL-CHECKPOINT.yaml](PARALLEL-UBL-CHECKPOINT.yaml).
