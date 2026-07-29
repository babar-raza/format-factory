---
artifact_id: FF6-AGENT-HANDOVER-START-001
artifact_type: agent_handover_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_state_path: plans/strategic/ff6/controller-state.yaml
---

# Start Here: Six Python Production Libraries

This is the single provider-neutral entry point for mission
`FF6-PRODUCTION-LIBRARIES-001`. Claude, Codex, or another governed executor
must reconstruct state from GitLab and the tracked machine records. Chat
history, model memory, old branches, ignored worktrees, and this prose packet
are not state authorities.

Absolute Windows path:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

## Current clean checkpoint

| Field | Verified value |
|---|---|
| Forge | GitLab only |
| Remote and branch | `origin/main` |
| GitLab handover checkpoint | `d02a00fedf669c6e2b2dd58e480715550fb2afe8` |
| Event/controller checkpoint | `220ee7f5b9d39c3684cff6af6331b56a03ae9e75` |
| Last journaled implementation | `2522752776f64ab800a2a21c8fa46c1f2a4e361c` |
| Controller state | `CONTRACT` |
| Journal head | `FF6-EVENT-000025` |
| Event hash | `237f7759e2286cfc08c547c53a0b47d44e1c77307329ec0215c5326e3f811e48` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` — `NEEDS_REPAIR` |
| Last completed child | `TC-FF6-NRRD-PROFILE-SURFACE-001` — `PASS` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` — `WORK_IN_PROGRESS` |
| Journaled atomic steps | `XLF-01`, `XLF-02`, `XLF-03`, `XLF-04-BATCH-001`, `XLF-04-BATCH-002`, `XLF-04-BATCH-003` |
| First unmet step | `XLF-04` |
| Shift microstate | `RESUMABLE` |
| Exact next action | Execute `XLF-04-BATCH-004` authority-candidate census; do not repeat batch 003 |
| Current compiled denominator | 110 capabilities / 672 obligations |
| Authority closure | 17/17 global; 5/5 XLIFF `MATCH` |
| Certified products | 0/6 |
| Promotion | all six `UNASSESSED` |

GitLab contains the UBL successor taskcard, XLIFF batch-003 implementation
commit `25227527`, and its event-25 controller projection in checkpoint commit
`220ee7f5`. The former local-only recovery condition has therefore been
resolved without rewriting either commit. Read
[`INFLIGHT-RECOVERY.yaml`](INFLIGHT-RECOVERY.yaml) for the reconciliation
audit and never duplicate batch 003.

Coordination ownership is intentionally not frozen into this packet. It lives
in the off-repo coordination database and can change after these tracked bytes
are committed. The incoming executor must query it live, register a new
identity, and acquire its own leases. A tracked `RESUMABLE` label proves the
Git/journal/task/proof boundary; it never transfers or vouches for a live
provider token.

## Read in this order

1. [`AGENTS.md`](../../../AGENTS.md)
2. [`skill-only-policy.yaml`](../../../docs/governance/skill-only-policy.yaml)
   and, for Codex, [`codex-adapter.md`](../../../docs/governance/codex-adapter.md);
   Claude uses the ambient hooks and `AGENTS.md` coordination contract because
   no separate Claude adapter is currently tracked
3. [`INFLIGHT-RECOVERY.yaml`](INFLIGHT-RECOVERY.yaml)
4. [`event-25/START-HERE.md`](event-25/START-HERE.md), the immutable compact
   event-25 replay bundle committed at `d02a00fe`
5. [`CURRENT-MACHINE-STATE.yaml`](CURRENT-MACHINE-STATE.yaml)
6. [`product-goal.yaml`](../../strategic/ff6/product-goal.yaml)
7. [`autonomous-six-python-production-execution-plan.md`](../../strategic/autonomous-six-python-production-execution-plan.md)
8. [`controller-state.yaml`](../../strategic/ff6/controller-state.yaml)
9. all records in [`events.jsonl`](../../strategic/ff6/events.jsonl)
10. [`current-gaps.yaml`](../../strategic/ff6/current-gaps.yaml)
11. [`capability-coverage.yaml`](../../strategic/ff6/capability-coverage.yaml)
12. [`TC-FF6-PROGRAM-CAPABILITIES-001.md`](../../../taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md)
13. [`TC-FF6-NRRD-PROFILE-SURFACE-001.md`](../../../taskcards/TC-FF6-NRRD-PROFILE-SURFACE-001.md)
14. [`TC-FF6-XLIFF-PROFILE-SURFACE-001.md`](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
15. [`TC-FF6-UBL-TYPING-001.md`](../../../taskcards/TC-FF6-UBL-TYPING-001.md)
16. [`xliff-authority-member-inventory.yaml`](../../../reports/ff6/xliff-authority-member-inventory.yaml)
17. [`extract_sal_facts.py`](../../../tools/spec/extract_sal_facts.py)
18. [`test_extract_sal_facts.py`](../../../tests/tools/test_extract_sal_facts.py)
19. [`xliff-normative-delta-matrix.yaml`](../../../reports/ff6/xliff-normative-delta-matrix.yaml)
20. [`xliff-core-obligation-denominator.yaml`](../../../reports/ff6/xliff-core-obligation-denominator.yaml)
21. [`xliff-core-obligation-inventory.yaml`](../../../reports/ff6/xliff-core-obligation-inventory.yaml)
22. [`XLF-04 batch-003 TDD receipt`](../../../reports/skills-rff6/skill-transcripts/test-driven-development-xliff-xlf04-core-batch-003.json)
23. [`XLF-04 batch-003 authority receipt`](../../../reports/skills-rff6/skill-transcripts/ingest-spec-sal-xliff-xlf04-core-batch-003.json)
24. [`plan-control event-25 receipt`](../../../reports/skills-rff6/skill-transcripts/plan-control-xliff-profile-surface-wip-006.json)
25. [`ACTIVE-WORK-CHECKPOINT.md`](ACTIVE-WORK-CHECKPOINT.md)
26. [`STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
27. [`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md)
28. [`EXECUTION-RUNBOOK.md`](EXECUTION-RUNBOOK.md)
29. [`CURRENT-STATE-AND-ROOT-CAUSES.md`](CURRENT-STATE-AND-ROOT-CAUSES.md)
30. [`VALIDATION-AND-RELEASE.md`](VALIDATION-AND-RELEASE.md)
31. [`CLAUDE-START.md`](CLAUDE-START.md)
32. [`checkpoint.yaml`](checkpoint.yaml)
33. [`manifest.yaml`](manifest.yaml)

## Authority precedence

If two records disagree, stop trusting the lower record and use this order:

1. fetched GitLab `origin/main` tracked bytes;
2. valid native FF6 journal;
3. controller projection;
4. current taskcard plus task index;
5. current gap and capability projections;
6. digest-bound contracts and proof;
7. this derived packet;
8. conversation or provider memory.

The assessment snapshot `current-state.yaml` remains valuable for product-tree
inventory, but it was captured at baseline commit `e4f8f5f…`. Its contract
hashes and pre-profile-repair capability totals are historical where they
disagree with event 25 and `capability-coverage.yaml`.

## Provider-shift contract

This packet transfers work, not an agent process. The incoming provider must
create a new coordination identity and must never reuse the outgoing
provider's token or assume its leases. The outgoing provider completes its
coordination session only after the packet commit is pushed and remotely
verified. If that session is still live when the incoming provider starts,
the incoming provider waits for normal completion or uses governed takeover
only after the owner is stale and every touched byte is classified.

The provider name does not change the goal, task, state machine, validation
threshold, or promotion rules. A shift is accepted only when all durable state
needed for the next action is recoverable from tracked GitLab `main` plus
content-addressed inputs. Provider memory may help locate evidence but may not
change the next task or close an acceptance criterion.

There is exactly one active product task after the transfer:
`TC-FF6-XLIFF-PROFILE-SURFACE-001`. The handover refresh is a derived
navigation operation; it neither creates a competing mission task nor changes
the native FF6 event head.

## Mechanical resume preflight

Run from the repository root:

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor d02a00fedf669c6e2b2dd58e480715550fb2afe8 origin/main
git merge-base --is-ancestor 220ee7f5b9d39c3684cff6af6331b56a03ae9e75 origin/main
git merge-base --is-ancestor 2522752776f64ab800a2a21c8fa46c1f2a4e361c origin/main
python tools/evidence/check_current_state_consistency.py
python -m tools.supervisor.coordination --json status
```

Then run the native FF6 journal check in
[`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md). Do not use
`tools.plan_control doctor` as an FF6 chain validator: it expects a different
event schema. That integration defect is tracked as `FF6-GAP-011`.

Resume only if:

- the worktree is clean or every dirty path is classified and outside scope;
- event 25 and controller state agree;
- the active `WORK_IN_PROGRESS` task exists in `taskcards/index.yaml`;
- the capability aggregate equals
  `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2`;
- all 17 authority artifacts still match, including all five XLIFF records;
- the committed source LF-normalized SHA-256 is
  `a5c67f56378e586bf46ddb8c39881ab9ea81e42e76539bac942c5220c45f0190`
  and the test SHA-256 is
  `bf7fa725496979e3f5a50125319f9974c6205803c8358adbfb0ba8677c52bc32`;
- the matrix SHA-256 is
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
- the Core inventory SHA-256 is
  `ae4d00af06fffc1eaf7741cd131d8ed7e7fc8a89b2a195acf4f649b5f44b6bbb`;
- 27 focused tests, Ruff, strict Mypy, Pyright 1.1.411, bytecode compilation,
  matrix check mode, and three identical generations of both authority-bound
  outputs replay;
- no live lease owns the intended files.

## Exact continuation

Resume only `TC-FF6-XLIFF-PROFILE-SURFACE-001` at `XLF-04`. Batch 003 and its
event/controller projection are already on GitLab. Do not repeat its RED/GREEN
cycle or append a second event for it.

Steps `XLF-01` through `XLF-03` and `XLF-04-BATCH-001` through
`XLF-04-BATCH-003` are complete at event 25. The immutable batch-003
implementation raises the cumulative Core inventory to 25 source-bound
obligations against an explicit 105-ID expected denominator. It resolves 25
IDs and leaves 80 missing. Recompute completed steps only if their recorded
input digests changed.

The XLF-03 matrix contains 36 unique coarse source-surface anchors. It proves
authority/member/profile/Core-or-module ownership, not complete semantic
obligation coverage. This distinction is the critical resume boundary:
`XLF-04` must continue deriving and verifying the complete Core obligation inventory,
including hierarchy, cardinality, ordering, inline-code identity and pairing,
segmentation, state, original data, skeleton, extension, processing-agent,
security, resource-limit, preservation, and canonical-output rules.

The first three batches represent all 12 declared categories, including the
two production-policy categories added by batch 003. Category presence is not
denominator completion. These obligations remain
`SOURCE_BOUND_UNVERIFIED`; they are not yet canonical SAL facts or behavior
proof.

If commits `25227527` or `220ee7f5` are missing or fail independent validation,
record that contradiction before selecting any repair. Otherwise the exact
next cycle is `XLF-04-BATCH-004`:

1. replay event 25, both batch-003 transcripts, the 27 focused tests, affected
   regressions, static checks, deterministic generation, and 17/17 authority
   audit;
2. obtain governed ownership without reusing or releasing the old identity;
3. compile a deterministic Core authority-candidate census across direct and
   leaf normative prose, Core XSD constraints, Core Schematron assertions,
   and exact XLIFF 2.0/2.1 deltas;
4. map every candidate exactly once to an expected obligation ID or a
   reasoned non-obligation disposition;
5. reject unmapped candidates, duplicate mappings, unexplained count drift,
   and any attempt to set `complete=true`;
6. implement the highest-severity unresolved expected-ID slice under RED,
   GREEN, focused regression, deterministic replay, receipt, commit, and one
   new controller event.

Do not inflate the 36 anchors into a false “complete Core” count. XLF-05 still
must split all eight official 2.1 modules—Translation Candidates/Matches,
Glossary, Format Style, Metadata, Resource Data, Size and Length Restriction,
Validation, and ITS—into first-class capability families. The pinned bundle
has nine module schema vocabularies because ITS uses `its` and `itsm`. Change
Tracking remains informative. XLIFF 2.2 remains uncompiled without a pinned
authority and XLIFF 1.2 remains a separate future compatibility model.

This is contract and obligation work only. Product source, product tests,
packaging, certification, gate movement, and promotion are prohibited.

The executor must not:

- repeat the completed OpenRaster, IPYNB, or NRRD repairs;
- repeat authority acquisition unless event-20 inputs were invalidated;
- infer XLIFF 2.0 from the pinned XLIFF 2.1 prose or schema bundle;
- collapse eight normative modules into one generic module-support claim,
  omit either `fs` or ITS, count the `its`/`itsm` vocabularies as two modules,
  or count the informative Change Tracking extension as a normative module;
- treat XSD validity as proof of inline pairing, segmentation, state,
  extension-preservation, ITS, or agent processing requirements;
- mix XLIFF 2.2 preview obligations into either stable profile;
- hide `FF6-XLIFF-PROFILE-001` by editing policy;
- close the parent while XLIFF or UBL mandatory gaps remain;
- create a branch, use GitHub, or ask whether to continue.

## Shift invariant

Every provider shift ends at a GitLab-main checkpoint that contains:

- a valid task state and event head;
- explicit completed and remaining acceptance criteria;
- current proof and failure boundaries;
- a deterministic exact next action;
- refreshed packet hashes;
- no unexplained or required uncommitted work.

If a provider cannot finish the whole taskcard, it must finish the current
microstep to an integration-safe state, run its gates, commit the coherent
slice, append a truthful `WORK_IN_PROGRESS` checkpoint event that binds that
commit, refresh this packet, commit, push, and remote-verify. A token boundary
is never a reason to commit broken code or leave operational state only in
chat.
