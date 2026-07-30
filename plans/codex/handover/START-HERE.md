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
| Control checkpoint | `240474babf868fa141850d4ed4792d3a8269ef28` |
| Preserved rejected attempt | `d99fc6bf3679cd39396afbf5621847e3009ddf31` |
| Last accepted XLIFF implementation | `e13e103de0bb789ff51a8e931af0fb649474be20` |
| Controller | `CONTRACT`, sequence 31 |
| Journal head | `FF6-EVENT-000031` |
| Event hash | `26f95f054774f35244a2edbfc08072156a1422acfb1e1d29c2c37a617dd90d55` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` |
| First unmet step | `XLF-04` |
| Exact next microstep | `XLF-04-BATCH-005-PARTIAL-002-B-REPAIR-001` |
| Exact next candidate | `XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1` |
| XLIFF obligation inventory | `26/105`, `79` missing |
| Candidate adjudication | `1/1,130` verified, `1,129` open |
| Certified libraries | `0/6` |
| Promotions | all six `UNASSESSED` |
| Product overlay | none; implementation is committed and pushed |
| Safe disjoint fallback | UBL `UBL-03-PARTIAL-002` only if XLIFF is live-owned |

Event 31 is a contradiction checkpoint. It preserves a mechanically passing
attempt while rejecting it from production acceptance. It is not a completed
XLIFF contract, product implementation, certification, release candidate, or
gate. Read [EVENT-31-DELTA.md](EVENT-31-DELTA.md) before the older Event 30
detail below.

The table describes the durable GitLab checkpoint, not an unconditional claim
that the shared worktree is idle. The prior executor committed both the
attempt and Event 31, but its XLIFF leases were still live at the last
observation. See [INFLIGHT-RECOVERY.yaml](INFLIGHT-RECOVERY.yaml). Claude must
requery ownership: follow a newer verified event if one exists, avoid XLIFF
while the owner remains live, or perform governed stale takeover without
erasing bytes.

Two control-plane constraints remain explicit: generic `tools.plan_control`
cannot validate the native FF6 event schema (`FF6-GAP-011`), and the shared
local `.local/artifact-index.yaml` is pre-existing invalid YAML at line 1163.
Neither invalidates Event 31. Do not "fix" either by deleting history or
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

## What Event 30 actually achieved and Event 31 preserved

Event 30 completed and pushed the bounded XLIFF Partial-002-A cycle:

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

Event 31 then preserved `d99fc6bf` as a mechanically green but
production-rejected attempt. Its 27/105 and 2/1,130 generated counts must not
replace the accepted boundary above. The exact causes and repair contract are
in [EVENT-31-DELTA.md](EVENT-31-DELTA.md).

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

A deeper read-only reassessment found the precise first machinery defect:
the current adjudicator requires accepted plus rejected IDs to equal the
generator's proposal set. It therefore cannot independently accept
`SAL-XLIFF-CORE-INLINE-PAIRING-001`, even though that is the denominator's
direct semantic owner and the generator omitted it. The successor must repair
this proof boundary before recording the decisions. It must also prove the
reverse direction from candidate
`XLF-CAND-CORE-SCHEMATRON-4BE479DD3F5875EF`, repair the incomplete
`SAL-XLIFF-00005` authority assertions, and avoid claiming XLIFF 2.0 pairing
from XLIFF 2.1 Schematron evidence. All exact digests, tests, file scopes, and
acceptance rules are in [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml).

Do not batch-adjudicate hundreds of candidates without discriminating tests.
The durable unit of progress is one independently evidenced decision family,
its negative controls, immutable replay, and native checkpoint event.

## Resume protocol

1. Read `AGENTS.md`, the Codex or Claude governance adapter, skill policy,
   current master plan, and applicable registered skill contracts.
2. Fetch GitLab `origin/main`; do not use GitHub or create another branch.
3. Run `plans/codex/handover/validate_committed_checkpoint.py --ref
   origin/main` to prove the committed packet in a temporary detached
   worktree.
4. Run `plans/codex/handover/validate_handover.py` separately in the shared
   checkout to detect overlays. A failure caused by live leased XLIFF paths is
   a routing signal, not permission to erase them.
5. Verify the implementation commit is an ancestor of `origin/main`.
6. Register a fresh coordination identity. Never reuse another provider's
   token, leases, manifests, or authorization.
7. Query live leases and preserve any unexplained dirty state.
8. If the XLIFF owner is live, execute only the serialized
   `UBL-03-PARTIAL-002` fallback. Otherwise claim XLIFF only after clean
   ownership recovery.
9. Claim only exact paths required after the first RED test establishes scope.
10. Replay both artifact check modes and the three immutable smoke tests.
11. Execute Partial-002-B Repair-001 using TDD, `ingest-spec-sal`, and
   `sal-pipeline-heal`.
12. Commit and push the bounded implementation to GitLab `main`.
13. Replay from the immutable commit.
14. Append one native event, rebuild current projections, refresh this packet,
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
8. [Event 31 delta](EVENT-31-DELTA.md)
9. [Immutable Event 31 packet](event-31/START-HERE.md)
10. [Immutable accepted Event 30 predecessor](event-30/START-HERE.md)
11. [Provider-shift contract](PROVIDER-SHIFT-CONTRACT.md)
12. [Root causes and structural design](CURRENT-STATE-AND-ROOT-CAUSES.md)
13. [Execution runbook](EXECUTION-RUNBOOK.md)
14. [State-machine/taskcard protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
15. [Validation and release controls](VALIDATION-AND-RELEASE.md)
16. [Product goal](../../strategic/ff6/product-goal.yaml)
17. [Autonomous production plan](../../strategic/autonomous-six-python-production-execution-plan.md)
18. [Native controller](../../strategic/ff6/controller-state.yaml)
19. [Complete event journal](../../strategic/ff6/events.jsonl)
20. [Active taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)

Historical Event 26 through 29 packets remain immutable evidence and are not
current instructions.

## First verification commands

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 240474babf868fa141850d4ed4792d3a8269ef28 origin/main
git merge-base --is-ancestor d99fc6bf3679cd39396afbf5621847e3009ddf31 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py
```

The first validator must pass for the committed packet. The second describes
the mutable shared checkout and may fail while the recorded live XLIFF overlay
exists. Then replay the exact checks from the Event 31 runbook in the
lane actually selected by coordination. A proof failure invalidates the
affected edge; it does not authorize editing a status.
