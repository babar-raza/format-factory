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
| Required ancestor | `4e3eff822f57ea336f52233c25452be2be75bbad` |
| Controller state | `CONTRACT` |
| Journal head | `FF6-EVENT-000020` |
| Event hash | `b7c06bba2afe60bcbc580d240cc57c4e990a017070b50d75904be469c75fea0c` |
| Parent task | `TC-FF6-PROGRAM-CAPABILITIES-001` — `NEEDS_REPAIR` |
| Last completed child | `TC-FF6-NRRD-PROFILE-SURFACE-001` — `PASS` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` — `WORK_IN_PROGRESS` |
| Completed atomic steps | `XLF-01`, `XLF-02` |
| First unmet step | `XLF-03` |
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
14. [`ACTIVE-WORK-CHECKPOINT.md`](ACTIVE-WORK-CHECKPOINT.md)
15. [`STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
16. [`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md)
17. [`EXECUTION-RUNBOOK.md`](EXECUTION-RUNBOOK.md)
18. [`CURRENT-STATE-AND-ROOT-CAUSES.md`](CURRENT-STATE-AND-ROOT-CAUSES.md)
19. [`VALIDATION-AND-RELEASE.md`](VALIDATION-AND-RELEASE.md)
20. [`CLAUDE-START.md`](CLAUDE-START.md)
21. [`checkpoint.yaml`](checkpoint.yaml)
22. [`manifest.yaml`](manifest.yaml)

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
disagree with event 20 and `capability-coverage.yaml`.

## Mechanical resume preflight

Run from the repository root:

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 4e3eff822f57ea336f52233c25452be2be75bbad origin/main
python tools/evidence/check_current_state_consistency.py
python -m tools.supervisor.coordination --json status
```

Then run the native FF6 journal check in
[`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md). Do not use
`tools.plan_control doctor` as an FF6 chain validator: it expects a different
event schema. That integration defect is tracked as `FF6-GAP-011`.

Resume only if:

- the worktree is clean or every dirty path is classified and outside scope;
- event 20 and controller state agree;
- the active `WORK_IN_PROGRESS` task exists in `taskcards/index.yaml`;
- the capability aggregate equals
  `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2`;
- all 17 authority artifacts still match, including all five XLIFF records;
- no live lease owns the intended files.

## Exact continuation

Resume only `TC-FF6-XLIFF-PROFILE-SURFACE-001` at `XLF-03`.

Steps `XLF-01` and `XLF-02` are complete at event 20. The official XLIFF 2.0
package and prose are now independently pinned, the 2.0 published SHA-1
cross-check passed, the 2.0/2.1 package inventory contains 42 exact members,
and clean offline XLIFF reconstruction passes 5/5. Recompute those steps only
if their input digests changed.

`XLF-03` must now compile a source-located normative delta and module matrix
from the tracked inventory and pinned authority bytes. The task must compile
exact XLIFF 2.0
and 2.1 Core plus separate coverage for all eight official 2.1 modules:
Translation Candidates/Matches, Glossary, Format Style, Metadata, Resource
Data, Size and Length Restriction, Validation, and ITS. The pinned bundle has
nine module schema vocabularies because the ITS module uses both `its` and
`itsm`. The Change Tracking extension is informative and must not inflate
normative coverage. XLIFF 2.2 remains isolated preview-only and XLIFF 1.2
remains a separate future model.

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
atomic substep to an integration-safe state, run the substep gates, append a
truthful `WORK_IN_PROGRESS` checkpoint event, refresh this packet, commit, push,
and remote-verify. A token boundary is never a reason to commit broken code or
to leave operational state only in chat.
