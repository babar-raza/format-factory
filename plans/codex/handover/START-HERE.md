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
| Required ancestor | `78660ae1a310ab06cf00d977bbc26fb65914f1c9` |
| Controller state | `CONTRACT` |
| Journal head | `FF6-EVENT-000024` |
| Event hash | `10d96a6729d250fecb89f5f082682f583b5b8053fd620702dcd837dfaf541434` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` — `NEEDS_REPAIR` |
| Last completed child | `TC-FF6-NRRD-PROFILE-SURFACE-001` — `PASS` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` — `WORK_IN_PROGRESS` |
| Completed atomic steps | `XLF-01`, `XLF-02`, `XLF-03`, `XLF-04-BATCH-001`, `XLF-04-BATCH-002` |
| First unmet step | `XLF-04` |
| Shift microstate | `RESUMABLE` |
| Exact next action | Start `XLF-04-BATCH-003`: RED tests for the final two categories plus an explicit expected-ID denominator |
| Current compiled denominator | 110 capabilities / 672 obligations |
| Authority closure | 17/17 global; 5/5 XLIFF `MATCH` |
| Certified products | 0/6 |
| Promotion | all six `UNASSESSED` |

The packet commit necessarily comes after the source commit above. The incoming
executor must fetch `origin/main`, require the source commit to be an ancestor
of the fetched packet commit, and validate packet hashes. Never require the
packet to contain its own final commit hash.

## Read in this order

1. [`AGENTS.md`](../../../AGENTS.md)
2. [`skill-only-policy.yaml`](../../../docs/governance/skill-only-policy.yaml)
   and, for Codex, [`codex-adapter.md`](../../../docs/governance/codex-adapter.md);
   Claude uses the ambient hooks and `AGENTS.md` coordination contract because
   no separate Claude adapter is currently tracked
3. [`CURRENT-MACHINE-STATE.yaml`](CURRENT-MACHINE-STATE.yaml)
4. [`product-goal.yaml`](../../strategic/ff6/product-goal.yaml)
5. [`autonomous-six-python-production-execution-plan.md`](../../strategic/autonomous-six-python-production-execution-plan.md)
6. [`controller-state.yaml`](../../strategic/ff6/controller-state.yaml)
7. all records in [`events.jsonl`](../../strategic/ff6/events.jsonl)
8. [`current-gaps.yaml`](../../strategic/ff6/current-gaps.yaml)
9. [`capability-coverage.yaml`](../../strategic/ff6/capability-coverage.yaml)
10. [`TC-FF6-PROGRAM-CAPABILITIES-001.md`](../../../taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md)
11. [`TC-FF6-NRRD-PROFILE-SURFACE-001.md`](../../../taskcards/TC-FF6-NRRD-PROFILE-SURFACE-001.md)
12. [`TC-FF6-XLIFF-PROFILE-SURFACE-001.md`](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
13. [`xliff-authority-member-inventory.yaml`](../../../reports/ff6/xliff-authority-member-inventory.yaml)
14. [`extract_sal_facts.py`](../../../tools/spec/extract_sal_facts.py)
15. [`test_extract_sal_facts.py`](../../../tests/tools/test_extract_sal_facts.py)
16. [`xliff-normative-delta-matrix.yaml`](../../../reports/ff6/xliff-normative-delta-matrix.yaml)
17. [`xliff-core-obligation-inventory.yaml`](../../../reports/ff6/xliff-core-obligation-inventory.yaml)
18. [`XLF-04 batch-002 TDD receipt`](../../../reports/skills-rff6/skill-transcripts/test-driven-development-xliff-xlf04-core-batch-002.json)
19. [`XLF-04 batch-002 authority receipt`](../../../reports/skills-rff6/skill-transcripts/ingest-spec-sal-xliff-xlf04-core-batch-002.json)
20. [`plan-control event-24 receipt`](../../../reports/skills-rff6/skill-transcripts/plan-control-xliff-profile-surface-wip-005.json)
21. [`ACTIVE-WORK-CHECKPOINT.md`](ACTIVE-WORK-CHECKPOINT.md)
22. [`STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
23. [`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md)
24. [`EXECUTION-RUNBOOK.md`](EXECUTION-RUNBOOK.md)
25. [`CURRENT-STATE-AND-ROOT-CAUSES.md`](CURRENT-STATE-AND-ROOT-CAUSES.md)
26. [`VALIDATION-AND-RELEASE.md`](VALIDATION-AND-RELEASE.md)
27. [`CLAUDE-START.md`](CLAUDE-START.md)
28. [`checkpoint.yaml`](checkpoint.yaml)
29. [`manifest.yaml`](manifest.yaml)

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
disagree with event 24 and `capability-coverage.yaml`.

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
git merge-base --is-ancestor 78660ae1a310ab06cf00d977bbc26fb65914f1c9 origin/main
python tools/evidence/check_current_state_consistency.py
python -m tools.supervisor.coordination --json status
```

Then run the native FF6 journal check in
[`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md). Do not use
`tools.plan_control doctor` as an FF6 chain validator: it expects a different
event schema. That integration defect is tracked as `FF6-GAP-011`.

Resume only if:

- the worktree is clean or every dirty path is classified and outside scope;
- event 24 and controller state agree;
- the active `WORK_IN_PROGRESS` task exists in `taskcards/index.yaml`;
- the capability aggregate equals
  `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2`;
- all 17 authority artifacts still match, including all five XLIFF records;
- the committed source SHA-256 is
  `ac44f43456f5c1ac02f9c157ae6bb653be6f9eacbdd2eca55e40e8447f74b5ce`
  and the test SHA-256 is
  `5f0554a03eb3ac9f220e8f4a5b3ee58d4764b488a78db661dc649b8a55ee2070`;
- the matrix SHA-256 is
  `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
- the Core inventory SHA-256 is
  `5930f1e28d21e277325c9a88ad8486ce9076ff1aa680ae21979440fd85d3244b`;
- 24 focused tests, Ruff, strict Mypy, Pyright 1.1.411, bytecode compilation,
  matrix check mode, and three identical generations of both authority-bound
  outputs replay;
- no live lease owns the intended files.

## Exact continuation

Resume only `TC-FF6-XLIFF-PROFILE-SURFACE-001` at `XLF-04`.

Steps `XLF-01` through `XLF-03` and `XLF-04-BATCH-001` through
`XLF-04-BATCH-002` are complete at event 24. The immutable
implementation commit adds the deterministic CLI/default seed layer, complete
declared archive/XML/matrix negative controls, the real authority matrix, and
19 cumulative fine-grained, source-bound Core obligations. Recompute those
steps only if their recorded input digests changed.

The XLF-03 matrix contains 36 unique coarse source-surface anchors. It proves
authority/member/profile/Core-or-module ownership, not complete semantic
obligation coverage. This distinction is the critical resume boundary:
`XLF-04` must continue deriving and verifying the complete Core obligation inventory,
including hierarchy, cardinality, ordering, inline-code identity and pairing,
segmentation, state, original data, skeleton, extension, processing-agent,
security, resource-limit, preservation, and canonical-output rules.

The first two batches now cover ten categories, adding identifier/reference/
inheritance, language/direction/whitespace, and source-target correspondence
to the seven batch-001 categories. These obligations remain
`SOURCE_BOUND_UNVERIFIED`; they are not yet canonical SAL facts or behavior
proof.

The exact next cycle is:

1. replay event 24, the 24 tests, matrix check, both three-run digests, static
   checks, and 17/17 authority audit;
2. add the RED tests for `XLF-04-BATCH-003`, covering
   `semantic_roundtrip_canonical_output` and
   `xml_security_resource_limits` using exact pinned authority locations;
3. implement only enough authority-bound records and verifier behavior to make
   that bounded batch GREEN without changing the 19 stable existing IDs;
4. retain `complete: false` and
   `completeness_basis: EXPECTED_OBLIGATION_DENOMINATOR_ABSENT`;
5. separately compile an explicit expected-obligation ID denominator before
   any later completeness claim; category presence, counts, filenames, or
   prose assertions cannot satisfy that denominator;
6. reject any completeness attempt if the expected-ID denominator is absent,
   duplicated, contains unresolved IDs, or was inferred only from existing
   seeds.

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
