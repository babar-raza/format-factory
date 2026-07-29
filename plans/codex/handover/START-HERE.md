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

This is the only handover entrypoint. It is a derived index: fetched GitLab
`origin/main`, `AGENTS.md`, the native event journal, controller, taskcards,
and immutable proof always outrank this document.

## Current clean checkpoint

| Field | Verified value |
|---|---|
| Forge/branch | GitLab `origin/main` only |
| XLIFF implementation commit | `315efa5f5f4420202b5254c86ccd8863a91c385f` |
| Event/projection commit | `c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0` |
| Controller | `CONTRACT`, sequence 29 |
| Journal head | `FF6-EVENT-000029` |
| Event hash | `de12acdefd04c37a918e3fd27dcb8dd076f53e576ee7049cf1efc732d02028bb` |
| Active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` |
| First unmet step | `XLF-04` |
| Exact next microstep | `XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION` |
| Safe disjoint fallback | `UBL-03-PARTIAL-002` only if XLIFF is live-owned |
| Certified libraries | `0/6` |
| Promotions | all six `UNASSESSED` |
| Workspace dependency | none; checkpoint is committed and clean |

The packet commit cannot embed its own final hash. Its validator instead proves
that both cited commits are ancestors of fetched GitLab main.

## What the last shift achieved

Codex recovered the stale Batch 005 working set through governed lease
takeover, independently replayed it, hardened its truth boundary, and pushed
two commits:

1. `315efa5f` — source, tests, canonical census, and three production-skill
   receipts.
2. `c1f4be66` — Event 29, controller/taskcard projections, and plan-control
   receipt.

Implemented machinery:

- complete declared Core candidate census across modal prose, non-modal prose,
  Core XSD, and Core Schematron;
- content, occurrence, member, profile, and source-package digests;
- full replay of report content from pinned XLIFF 2.0/2.1 authority bytes;
- deterministic recomputation of disposition label, precision, rationale, and
  mapping IDs;
- negative controls rejecting forged mapping labels and self-consistent,
  rehashed authority-forged candidate content;
- honest `_UNVERIFIED` precision vocabulary;
- package-safe import structure without ad hoc `sys.path` mutation.

Observed proof:

```text
candidate rows: 1,130
modal normative prose: 182
non-modal prose: 588
Core XSD: 264
Core Schematron: 96
focused tests: 64 passed
census replay: 3 identical clean processes
census LF SHA-256: 24c1902b6387cc9fa3402f78392ba91c6e6656407719ec11cfaab1c4f3d22b9e
XLIFF authority audit: 5/5 MATCH
Ruff / strict Mypy / Pyright 1.1.411 / py_compile: PASS
affected format-contract suite: 94 passed, 1 named baseline-known deselection
production-program suite: 69 passed
```

## The critical truth boundary

The census is source-authentic; its semantic dispositions are not yet
independently verified:

- verified dispositions: `0`;
- unverified dispositions: `1,130`;
- expected obligation IDs: `105`;
- expected IDs without candidate mapping: `60`;
- source-bound obligation rows: `25`;
- missing source-bound obligation rows: `80`;
- denominator: `OPEN_AUTHORITY_CENSUS`;
- XLF-04: incomplete;
- Batch 005: incomplete.

The generator cannot certify its own mappings. The next provider must perform
independent authority reading through canonical SAL and add discriminating
tests when it finds contradictions. Mechanically copying generated
dispositions into SAL would be false closure.

## Deterministic resume rule

1. Fetch GitLab and validate this packet.
2. If Event 30 or later exists, validate the newer event chain and rebuild the
   projection; never execute stale instructions.
3. Register a fresh provider identity; never inherit the outgoing token,
   leases, manifests, or mutation authorizations.
4. If the exact XLIFF scope is available, claim it and execute the named
   Batch 005 partial microstep.
5. If XLIFF is live-owned, preserve it and continue only the disjoint UBL
   `UBL-03-PARTIAL-002` import/include and reference-resolution cycle.
6. A dirty or divergent workspace is investigated and preserved; it is never
   reset, cleaned, restored, or broadly stashed.

## Required reading order

1. [AGENTS.md](../../../AGENTS.md)
2. [Event 29 immutable packet](event-29/START-HERE.md)
3. [Current shift handover](CURRENT-SHIFT-HANDOVER.md)
4. [Claude start instructions](CLAUDE-START.md)
5. [Exact next microstep](NEXT-MICROSTEP.yaml)
6. [Provider-shift contract](PROVIDER-SHIFT-CONTRACT.md)
7. [Current machine state](CURRENT-MACHINE-STATE.yaml)
8. [Clean recovery boundary](INFLIGHT-RECOVERY.yaml)
9. [Parallel UBL checkpoint](PARALLEL-UBL-CHECKPOINT.yaml)
10. [Product goal](../../strategic/ff6/product-goal.yaml)
11. [Autonomous production plan](../../strategic/autonomous-six-python-production-execution-plan.md)
12. [Native controller](../../strategic/ff6/controller-state.yaml)
13. [Complete event journal](../../strategic/ff6/events.jsonl)
14. [Active XLIFF taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
15. [UBL fallback taskcard](../../../taskcards/TC-FF6-UBL-TYPING-001.md)

Supporting durable design:

- [Root causes and production truth](CURRENT-STATE-AND-ROOT-CAUSES.md)
- [Program execution runbook](EXECUTION-RUNBOOK.md)
- [Provider resume protocol](SHIFT-AND-RESUME-PROTOCOL.md)
- [State-machine/taskcard protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
- [Validation and release controls](VALIDATION-AND-RELEASE.md)
- [Historical Event 26](event-26/START-HERE.md)
- [Historical Event 27](event-27/START-HERE.md)
- [Historical Event 28](event-28/START-HERE.md)

## First commands

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 315efa5f5f4420202b5254c86ccd8863a91c385f origin/main
git merge-base --is-ancestor c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
python -m tools.supervisor.coordination --json status
```

Then follow [Event 29 runbook](event-29/RUNBOOK.md). Work remains autonomous:
do not ask for continuation, do not edit readiness labels, and do not claim a
library complete until its complete proof graph and certification gates pass.

The first bounded RED cycle is fixed in
[NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml). It targets one XLIFF 2.1
Schematron assertion whose generated mapping currently confuses incidental
XPath context names with direct semantic obligations. The incoming provider
must build a separate content-addressed adjudication authority; it must not
turn the existing proposal generator into its own verifier.
