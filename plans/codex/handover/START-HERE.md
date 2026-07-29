---
artifact_id: FF6-PROVIDER-NEUTRAL-HANDOVER-START
artifact_type: handover_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
---

# FF6 Provider-Neutral Handover: Start Here

This is the only current human entrypoint for the six-library production
mission. It is written for Claude, Codex, or another governed executor. The
canonical repository state always wins over this derived packet.

Absolute path:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

## Current committed checkpoint

| Field | Verified value |
|---|---|
| Forge / branch | GitLab `origin/main` only |
| Packet input checkpoint | `9ff40eb0900efe417b36a2d10486630b1c4b635a` |
| Latest bounded implementation ancestor | `7b5cce4fefaf3b7e8c4d1f1891821d1bfcd7acce` |
| Controller handover source | `18bb295f94e43338611ef88caff073eed17411c9` |
| Controller Event 26 commit | `15ab7d0455e109bd88289e16d73c0835324a21ab` |
| Controller state | `CONTRACT` |
| Native event | `FF6-EVENT-000026` |
| Event hash | `34b36bf5dc4344713ac1c0f026b30e6b15fb6a63b86f4876ee98230952fabcd0` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` |
| Task state | `WORK_IN_PROGRESS` |
| Completed task steps | `XLF-01`, `XLF-02`, `XLF-03` |
| Completed XLF-04 batches | `001`, `002`, `003`, `004` |
| First unmet step | `XLF-04` |
| Exact next microstep | `XLF-04-BATCH-005` |
| Production certifications | `0/6` |
| Promotion state | all six products `UNASSESSED` |

The packet commit that contains this file must descend from the source
checkpoint. It cannot truthfully embed its own final commit hash.

At the final refresh, the committed handover scope was clean and remote
verified, while a separately leased Batch 005 worker owned two untracked
implementation paths in the shared worktree. Those classified paths are
preserved and are not part of this handover commit.

## Current transfer state

Two different states exist and must never be collapsed into one status:

| Boundary | State | Meaning |
|---|---|---|
| Committed Event 26 checkpoint | `RESUMABLE` | A clean checkout of GitLab `origin/main` can reconstruct the last verified state without local-only files |
| Shared workspace at 2026-07-29T18:36Z | `IN_FLIGHT_RED_NOT_TRANSFERABLE` | Another live Codex identity owns Batch 005 RED work; Claude must not claim, overwrite, commit, or present those bytes as a clean checkpoint |

The live owner observed at capture was
`agent-codex-20260729T181022-74dc4a`. It owned:

- `tools/spec/xliff_core_candidate_binding.py`
- `tests/tools/test_extract_sal_facts_candidate_binding.py`
- `logical:FF6-XLIFF-BATCH005`

The focused in-flight test file produced `17 passed, 10 failed`. The ten
failures are the expected RED integration boundary: the committed census is
still schema v1, non-modal prose is not classified, and the committed
standalone validator does not yet reject the eight forged candidate-content
mutations. This is evidence of unfinished work, not a regression in the clean
Event 26 checkpoint and not completion evidence.

The optional local recovery bytes are content-addressed:

| Path | LF-normalized SHA-256 | Bytes | Lines | Role |
|---|---|---:|---:|---|
| `tools/spec/xliff_core_candidate_binding.py` | `042c670acefff8d0a6932ea3df7f1582f887f756148dd0bdfc356f69ca56f8b7` | 14,443 | 387 | green standalone binding primitive |
| `tests/tools/test_extract_sal_facts_candidate_binding.py` | `fcb25b8f9400fc72a485eea23e8daf7d29e579f45a27353e3bf9a15d4c89dcb3` | 13,375 | 427 | RED integration and tamper controls |

They are deliberately not required for a clean-checkout resume. If present,
the validator requires exact bytes and untracked status unless the path is
explicitly classified as a newer active foreign XLIFF working set. Active
foreign bytes are preserved but deliberately not frozen. If absent, resume
from Event 26. If different without that active classification, preserve them
and reconcile the conflict; never overwrite or silently prefer either copy.

At the 2026-07-29T19:17Z refresh, a newer live XLIFF worker,
`agent-codex-20260729T190440-e2dd38`, owned the Batch 005 logical scope and
eleven exact implementation/report/receipt paths. State:
`ACTIVE_XLIFF_BATCH005_FOREIGN_WORKING_SET`. Its tracked extractor, primary
test, and candidate-census paths already differed from HEAD, so the handover
does not freeze or stage those changing bytes. This identity is an observation
only, not a credential or permanent owner. Requery coordination before acting;
while it remains live, preserve its paths and use the disjoint UBL resume.

At 2026-07-29T19:27:45Z, GitLab `origin/main` and local `HEAD` both resolved
to `9ff40eb0900efe417b36a2d10486630b1c4b635a`. The XLIFF owner's recorded
process (`PID 31488`) was absent, but its coordination record was still
`ACTIVE`: the last heartbeat was `2026-07-29T19:17:24.722412Z` and its
configured TTL was 7,200 seconds. Process absence is a warning, not takeover
authority. Until the coordination plane changes the lease to stale or the
owner completes, Claude must not touch those eleven paths. This distinction
prevents a provider shift from converting a process-level observation into an
unsafe filesystem write.

The three UBL paths that were live during the prior packet are no longer
foreign untracked work. They were independently verified, committed, and
pushed to GitLab main at
`7b5cce4fefaf3b7e8c4d1f1891821d1bfcd7acce`.

State: `COMMITTED_PARALLEL_CHECKPOINT_NON_CONTROLLER`.

- `reports/ff6/ubl-package-root-census.yaml`
- `tests/tools/test_compile_ubl_schema_graph.py`
- `tools/spec/compile_ubl_schema_graph.py`

They establish a secure, deterministic census of 890 UBL 2.3 package members
and exactly 91 document roots. The report digest is
`787c8d9258dc25a8662ee934b9b0b14096de790db87826dab970792b9494976d`.
This is real bounded progress, but it does not change Event 26, complete
UBL-01, advance the UBL taskcard from `READY`, prove the reachable schema
graph, or prove product readiness. The full UBL SAL replay fails closed on a
stale `SRC-UBL-001` prose-target digest. Read the
[parallel UBL checkpoint](PARALLEL-UBL-CHECKPOINT.yaml) before resuming that
lane.

At resume time, query the coordination plane and GitLab again. The captured
identity and test counts are forensic observations, not transferable
credentials or timeless authority. Use the decision table in
[Claude/Codex execution instructions](CLAUDE-START.md#transfer-state-discriminator).

Claude's first executable decision is deterministic:

1. If Event 27 or later is on GitLab, recompute from the journal and ignore
   this runtime observation.
2. If the XLIFF lease is still live, leave the five current dirty XLIFF paths
   untouched and execute the disjoint UBL stale-SAL closure repair.
3. If the XLIFF lease is stale and no newer commit exists, use governed
   `takeover --reason`, recapture every baseline, and continue Batch 005 from
   the preserved bytes.
4. If the XLIFF owner completed and released cleanly, claim the exact paths
   under Claude's new identity and independently rerun the focused tests
   before accepting any result.

## Mission

Produce six independently publishable, production-grade Python libraries:

- Jupyter Notebook (`format-factory-ipynb`)
- OpenRaster (`format-factory-openraster`)
- NRRD (`format-factory-nrrd`)
- XLIFF (`format-factory-xliff`)
- SafeTensors (`format-factory-safetensors`)
- OASIS UBL (`format-factory-ubl`)

The libraries and every developer-facing capability must be secure, typed,
documented, maintainable, interoperable, professionally structured, tested
against installed wheels, and supported by current digest-bound evidence.
Planning, source presence, test counts, package smoke tests, candidate routing,
or old readiness labels do not satisfy this goal.

Read the canonical [product goal](../../strategic/ff6/product-goal.yaml) and
[execution plan](../../strategic/autonomous-six-python-production-execution-plan.md)
before changing mission state.

## True current product state

The program has a deterministic 110-capability / 672-obligation planning
universe. That is a contract denominator, not implementation proof.
For the active XLIFF Core work, 25 of 105 expected IDs have source-bound
obligation rows and 80 remain missing.

| Format | Contract-stage state | Source state | Production state |
|---|---|---|---|
| IPYNB | profile surface repaired; 25 capabilities / 68 obligations | existing partial package | not certified |
| OpenRaster | profile surface repaired; 20 / 134 | no Python product package | not certified |
| NRRD | profile surface repaired; 21 / 65 | existing partial package | not certified |
| XLIFF | profile compilation in progress; 15 / 125 | existing partial package | not certified |
| SafeTensors | compiled planning surface; 11 / 86 | existing partial package | not certified |
| UBL | exact package/root census verified; full SAL replay and typing repair remain; 18 / 194 | existing partial package | not certified |

All six ProductContracts remain lifecycle `DRAFT`. Five existing oracle
summaries are shallow `D0` partial evidence, the existing install proofs have
stale input closures, clean-checkout collection is not yet proven, corpus
adequacy is not proven, and OpenRaster source is absent. See
[current gaps](../../strategic/ff6/current-gaps.yaml).

## Exact next work

Resume `TC-FF6-XLIFF-PROFILE-SURFACE-001` at `XLF-04-BATCH-005`.

1. Add RED controls for the independent post-commit finding that the
   standalone census validator accepts forged normalized requirement text,
   member/source digests, and occurrence locations.
2. Bind every candidate occurrence with an explicit candidate class and a
   content-sensitive digest while preserving stable candidate identity.
3. Classify every non-modal Core prose paragraph excluded by Batch 004.
4. Replace all 78 coarse structural dispositions with an exact semantic
   mapping or an explicit, source-located, reasoned non-obligation.
5. Expand the 105-ID expected-obligation denominator when the newly classified
   authority surface exposes missing normative behavior.
6. Compile source-bound obligations for remaining expected IDs without
   changing the meaning or identity of the 25 stable rows already present.
7. Keep `complete: false` until the full Core authority surface is exhaustive,
   every expected ID has a source-bound obligation, and canonical SAL
   verification succeeds.

Do not start product source, architecture, packaging, certification,
promotion, release, or gate work. Do not skip to XLF-05 while this mandatory
XLF-04 work is safely executable.

If live coordination shows another agent owns the XLIFF Batch 005 scope, do
not wait and do not compete for those paths. Resume the disjoint
`TC-FF6-UBL-TYPING-001` lane at
`FF6-UBL-SAL-PROSE-TARGET-STALE-001`: repair and replay the stale prose-target
proof closure. Only after that full replay passes may the UBL state advance to
`AUTHORITY_REVALIDATED` and UBL-03 reachable-schema-graph work begin.

Read [Claude/Codex execution instructions](CLAUDE-START.md), the
[active checkpoint](ACTIVE-WORK-CHECKPOINT.md), and the
[machine state](CURRENT-MACHINE-STATE.yaml) before acting. The immutable
Event 26 packet is [here](event-26/START-HERE.md).

## Resume preflight

Run from the repository root:

```powershell
git fetch origin
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 9ff40eb0900efe417b36a2d10486630b1c4b635a origin/main
git merge-base --is-ancestor 7b5cce4fefaf3b7e8c4d1f1891821d1bfcd7acce origin/main
git merge-base --is-ancestor 18bb295f94e43338611ef88caff073eed17411c9 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
python -m tools.supervisor.coordination status
```

Proceed only when:

- the handover source checkpoint is an ancestor of fetched `origin/main`;
- the handover validator returns `valid: true`;
- the native controller and journal still select the same task/microstep;
- any local changes are classified and preserved;
- the workspace transfer state has been recomputed from live coordination,
  Git, and test evidence;
- the incoming provider has registered its own coordination identity and
  claimed exact paths;
- the registered skill route and execution manifest cover every intended
  mutation.

If `origin/main` has advanced, do not blindly follow this projection. Recompute
the latest native event, controller, taskcard, gaps, proofs, and exact next
task, then refresh this packet through `/refresh-provider-neutral-handover`.

## Authority and reading order

Read these in order:

1. [AGENTS.md](../../../AGENTS.md)
2. [Codex adapter](../../../docs/governance/codex-adapter.md) when using Codex
3. [Product goal](../../strategic/ff6/product-goal.yaml)
4. [Execution plan](../../strategic/autonomous-six-python-production-execution-plan.md)
5. [Controller](../../strategic/ff6/controller-state.yaml)
6. [Complete event journal](../../strategic/ff6/events.jsonl)
7. [Current gaps](../../strategic/ff6/current-gaps.yaml)
8. [Active XLIFF taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
9. [Machine state](CURRENT-MACHINE-STATE.yaml)
10. [Event 26 runbook](event-26/RUNBOOK.md)

The root [manifest](manifest.yaml) binds the current packet and canonical
inputs. [Checkpoint](checkpoint.yaml) is the compact machine projection.
[Recovery](INFLIGHT-RECOVERY.yaml) describes dirty-worktree and crash cases.
[Validation](validate_handover.py) proves hashes, links, journal agreement,
task registration, GitLab ancestry, and negative controls.

## Historical documents

The following files retain deeper design background but are historical
projections. Their embedded Event 24/25 exact-next instructions are superseded
by this file and Event 26:

- [root-cause analysis](CURRENT-STATE-AND-ROOT-CAUSES.md)
- [older execution runbook](EXECUTION-RUNBOOK.md)
- [shift protocol](SHIFT-AND-RESUME-PROTOCOL.md)
- [state-machine protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
- [validation and release notes](VALIDATION-AND-RELEASE.md)
- [Event 25 packet](event-25/START-HERE.md)

Use them for rationale only. Never select work from a historical packet.

## Shift invariants

- One writer owns the active task at a time.
- Provider identities, tokens, leases, local manifests, and uncommitted state
  are never transferred as authority.
- Every shift ends only at a `RESUMABLE` boundary: successful work committed,
  pushed to GitLab `main`, native event appended, controller/task projections
  updated, and the handover refreshed and validated.
- RED-only, unjournaled, local-only, or unexplained dirty states are recovery
  states, not clean checkpoints.
- Existing user or agent work is preserved. Never reset, clean, stash, restore,
  or overwrite unexplained paths.
- Explicit file staging only. Never use `git add .` or `git add -A`.
- The next executor recomputes state from GitLab, the journal, controller,
  taskcard, proofs, and coordination plane; it does not trust conversation
  memory.
