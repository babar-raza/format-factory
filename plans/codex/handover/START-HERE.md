---
artifact_id: FF6-PROVIDER-NEUTRAL-HANDOVER-START
artifact_type: handover_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# FF6 production mission — start here

Absolute start path:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

This is the only operational entrypoint for Claude, Codex, or another governed
executor. It is a derived index. Fetched GitLab `origin/main`, `AGENTS.md`, the
native event journal, controller, taskcards, and immutable proof always outrank
this packet.

## Current clean checkpoint

| Field | Verified value |
|---|---|
| Forge and branch | GitLab `origin/main` only |
| Implementation commit | `e13e103de0bb789ff51a8e931af0fb649474be20` |
| Controller | `CONTRACT`, sequence 30 |
| Journal head | `FF6-EVENT-000030` |
| Event hash | `2d365d013b94c386014d7e75813114de6d7a225e2a9e16d21a485a38cd2d9398` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` |
| First unmet step | `XLF-04` |
| Exact next microstep | `XLF-04-BATCH-005-PARTIAL-002-B` |
| Exact next candidate | `XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1` |
| XLIFF obligation inventory | `26/105`, `79` missing |
| Candidate adjudication | `1/1,130` verified, `1,129` open |
| Certified libraries | `0/6` |
| Promotions | all six `UNASSESSED` |
| Product overlay | none; implementation is committed and pushed |
| Safe disjoint fallback | UBL `UBL-03-PARTIAL-002` only if XLIFF is live-owned |

Event 30 is a partial contract-evidence checkpoint. It is not a completed XLIFF
contract, product implementation, certification, release candidate, or gate.

Two control-plane constraints remain explicit: generic `tools.plan_control`
cannot validate the native FF6 event schema (`FF6-GAP-011`), and the shared
local `.local/artifact-index.yaml` is pre-existing invalid YAML at line 1163.
Neither invalidates Event 30. Do not "fix" either by deleting history or
silently converting status; follow the native chain and create a separately
governed reconciliation task.

## Mission objective

Produce six independently publishable, production-grade Python libraries:

- Jupyter Notebook;
- OpenRaster;
- NRRD;
- XLIFF 2.0/2.1, including official 2.1 modules;
- SafeTensors;
- OASIS UBL 2.3, including all 91 document roots.

Each library must have a complete authority-backed product contract, secure and
typed implementation, independent interoperability evidence, installed-wheel
proof, cross-platform CI evidence, reproducible packages, SBOM, provenance,
documentation, and repository extraction readiness. No count, source file,
test definition, or agent assertion is sufficient proof by itself.

The mission remains in controller state `CONTRACT` because XLIFF and UBL
contract surfaces are still incomplete. Product source expansion is not the
current task.

## What Event 30 actually achieved

The previous shift completed and pushed the bounded XLIFF Partial-002-A cycle:

- introduced a separate content-addressed candidate-adjudication compiler;
- kept generated candidate proposals distinct from independent decisions;
- independently accepted only the root `trgLang` obligation for candidate
  `XLF-CAND-CORE-SCHEMATRON-B109E9507A685F90`;
- explicitly rejected four overmapped proposal IDs with reason codes;
- invalidated evidence when candidate, occurrence, authority member,
  denominator, decision, SAL store, SAL manifest, SAL receipt, or adjudicator
  content changes;
- gated the real Batch 005 obligation compiler on replayed adjudication proof;
- preserved Batch 003 byte identity;
- grew the source-bound inventory from 25 to 26 rows without claiming
  completeness.

Proof boundary:

```text
candidate census:          1,130
verified dispositions:     1
unverified dispositions:   1,129
expected obligation IDs:   105
source-bound rows:          26
missing rows:               79
XLF-04 complete:            false
products certified:        0/6
```

Immutable artifact replay:

```text
adjudication SHA-256:
28399664d50afdd15e9f8b5ab2824a9566aa478fd0fcb18c97ce1451fd90d521

obligation inventory SHA-256:
83b9f2da44b33a93cea6740e7510b32b961dda80791f9f148c163e913922f5e0
```

The bounded evidence also records 89 focused passes across split runs, 94
format-contract passes with one named baseline-known CSV deselection, 69
production-program passes, three identical generations, static-analysis
passes, canonical SAL verification, five matching XLIFF authorities, and three
zero-warning production-skill transcripts. These results prove only the
bounded change.

## Exact next work

Open [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml). The selected candidate is:

```text
candidate: XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1
authority: schemas/xliff_core_2.1.sch
location:  schematron/rule[47]/assert[2]
rule:      subFlowsStart and subFlowsEnd on pc must be used as a pair
```

The generated proposal lists generic validator, segment hierarchy, ignorable
hierarchy, and inline `pc` obligations. Those are hypotheses, not evidence.
The next executor must independently adjudicate the direct semantic owner,
write a failing test first, reject incidental context mappings, and only then
compile any obligation proven by authority and canonical SAL.

Do not batch-adjudicate hundreds of candidates without discriminating tests.
The durable unit of progress is one independently evidenced decision family,
its negative controls, immutable replay, and native checkpoint event.

## Resume protocol

1. Read `AGENTS.md`, the Codex or Claude governance adapter, skill policy,
   current master plan, and applicable registered skill contracts.
2. Fetch GitLab `origin/main`; do not use GitHub or create another branch.
3. Run `plans/codex/handover/validate_handover.py`.
4. Verify the implementation commit is an ancestor of `origin/main`.
5. Register a fresh coordination identity. Never reuse another provider's
   token, leases, manifests, or authorization.
6. Query live leases and preserve any unexplained dirty state.
7. Claim only exact paths required after the first RED test establishes scope.
8. Replay both artifact check modes and the three immutable smoke tests.
9. Execute Partial-002-B using TDD, `ingest-spec-sal`, and
   `sal-pipeline-heal`.
10. Commit and push the bounded implementation to GitLab `main`.
11. Replay from the immutable commit.
12. Append one native event, rebuild current projections, refresh this packet,
    validate negative controls, and commit/push the checkpoint metadata.

If XLIFF exact paths have a current live owner, use only the serialized UBL
fallback in [PARALLEL-UBL-CHECKPOINT.yaml](PARALLEL-UBL-CHECKPOINT.yaml).

## Required reading order

1. [AGENTS.md](../../../AGENTS.md)
2. [Claude execution instructions](CLAUDE-START.md)
3. [Current machine state](CURRENT-MACHINE-STATE.yaml)
4. [Exact next microstep](NEXT-MICROSTEP.yaml)
5. [Checkpoint record](checkpoint.yaml)
6. [Recovery and provider transfer rules](INFLIGHT-RECOVERY.yaml)
7. [Current shift handover](CURRENT-SHIFT-HANDOVER.md)
8. [Immutable Event 30 packet](event-30/START-HERE.md)
9. [Provider-shift contract](PROVIDER-SHIFT-CONTRACT.md)
10. [Root causes and structural design](CURRENT-STATE-AND-ROOT-CAUSES.md)
11. [Execution runbook](EXECUTION-RUNBOOK.md)
12. [State-machine/taskcard protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
13. [Validation and release controls](VALIDATION-AND-RELEASE.md)
14. [Product goal](../../strategic/ff6/product-goal.yaml)
15. [Autonomous production plan](../../strategic/autonomous-six-python-production-execution-plan.md)
16. [Native controller](../../strategic/ff6/controller-state.yaml)
17. [Complete event journal](../../strategic/ff6/events.jsonl)
18. [Active taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)

Historical Event 26 through 29 packets remain immutable evidence and are not
current instructions.

## First verification commands

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor e13e103de0bb789ff51a8e931af0fb649474be20 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py
```

Then replay the exact artifact checks from the Event 30 runbook. A failure
invalidates the affected proof edge; it does not authorize editing a status.
