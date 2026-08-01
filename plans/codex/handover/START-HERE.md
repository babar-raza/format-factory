---
artifact_id: FF6-HANDOVER-START-EVENT-44
artifact_type: provider_neutral_handover_entry
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# FF6 production program: start here

Canonical start file:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

GitLab `origin/main` is the only integration authority. The current native
controller head is `FF6-EVENT-000044` (sequence `44`), hash
`20e8f7fac635994e4f1051a5dd9cd3bd0a2da3b0e361d006a17d834536fc09cd`, derived from source checkpoint
`4c4b80517a34534416492a772c6d3d81bfde9809`. Product certification remains `0`;
all six promotion states remain `UNASSESSED`.

## Mission

Deliver independently publishable production-grade Python libraries for
IPYNB, OpenRaster, NRRD, XLIFF, SafeTensors, and OASIS UBL. Completion requires
all six technical certifications, installed-wheel proof, independent
interoperability, security/resource-limit proof, reproducible packages,
documentation, SBOMs, provenance, and extraction-ready repositories.

## Exact immediate controller work

Run `TC-FF6-ACCEL-CONTROL-001` through the registered
`refresh-provider-neutral-handover` skill. Current action:

> Generate tracked handovers from Event 44 and controller state, then run stale-value and integration-lock controls before closing A3.

The product lane remains `TC-FF6-XLIFF-PROFILE-SURFACE-001` at
`XLF-04-BATCH-005-PARTIAL-002-I`. Its accepted semantic checkpoint is
`d95af5aeb248907b4d23457ecd288723fc9c2050`. Do not start that product mutation until this
control slice closes and a fresh controller selection authorizes it.

## Honest boundary

- technical certifications: `0`;
- OpenRaster source: absent;
- the other five product trees: partial and non-certified;
- XLIFF: `31` of
  `105` expected Core obligations,
  `9` of
  `1130` candidate dispositions;
- UBL: `91` roots identified, but UBL-03 is incomplete;
- no gate, release, publication, certification, or product promotion follows
  from this packet.

## Mandatory resume order

1. Read [AGENTS.md](../../../AGENTS.md) and the active control
   [taskcard](../../../taskcards/TC-FF6-ACCEL-CONTROL-001.md).
2. Fetch only GitLab `origin/main`; require local `HEAD == origin/main` before
   a clean transfer mutation.
3. Run `python plans/codex/handover/validate_handover.py --self-test --require-clean`.
4. Query coordination, register a fresh identity, claim exact paths, create a
   live skill manifest, and use preflight/record-write for every mutation.
5. Execute the immediate controller action above. A new provider must never
   reuse this shift's identity, token, lease, manifest, or authorization.

## Packet map

- [Machine state](CURRENT-MACHINE-STATE.yaml)
- [Checkpoint contract](checkpoint.yaml)
- [Current shift handover](CURRENT-SHIFT-HANDOVER.md)
- [Exact task split](NEXT-MICROSTEP.yaml)
- [Provider commands](CLAUDE-START.md)
- [Active work checkpoint](ACTIVE-WORK-CHECKPOINT.md)
- [Recovery contract](INFLIGHT-RECOVERY.yaml)
- [Clean replay rules](CLEAN-REPLAY-REPAIR.md)
- [Root causes and durable design](CURRENT-STATE-AND-ROOT-CAUSES.md)
- [Provider shift contract](PROVIDER-SHIFT-CONTRACT.md)
- [Execution runbook](EXECUTION-RUNBOOK.md)
- [State machine and taskcards](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
- [Validation and release](VALIDATION-AND-RELEASE.md)
- [Parallel UBL checkpoint](PARALLEL-UBL-CHECKPOINT.yaml)
- [Manifest](manifest.yaml)
