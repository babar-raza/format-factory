---
artifact_id: FF6-HANDOVER-START-EVENT-32
artifact_type: provider_neutral_handover_entry
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# FF6 autonomous production program — start here

This is the only entry point an incoming Claude or Codex shift needs:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

The canonical repository is GitLab `origin/main`. Do not use the GitHub
remote, create a branch, reuse another provider identity, or depend on ignored
local bytes. The clean source checkpoint is GitLab commit
`530f18fe89a6875276e8f4442351445564df80e9`, containing native
`FF6-EVENT-000032`. Its accepted implementation is
`ff8f7d9f9ff1ff613be376e1361b0dd8304566e3`, and the exact continuation is
`XLF-04-BATCH-005-PARTIAL-002-C`.

## Mission

Deliver six independently publishable, professional Python libraries for
Jupyter Notebook, OpenRaster, NRRD, XLIFF, SafeTensors, and OASIS UBL. Each
library must provide the full practical format surface developers need,
production-grade architecture and typing, secure parsing and writing,
independent interoperability evidence, installed-wheel proof, and reproducible
release artifacts. Planning, source presence, test counts, contract compilation,
or a passing smoke test do not certify a product.

Current truth: controller `CONTRACT`, Event 32, `0/6` certified, every product
`UNASSESSED`. XLIFF is the selected lane because its complete stable contract
surface is still open. UBL schema-graph work is valid parallel progress but
does not complete UBL-03.

## Mandatory resume order

1. Read [AGENTS.md](../../../AGENTS.md), then
   [Claude start](CLAUDE-START.md).
2. Fetch GitLab and require `HEAD == origin/main == 530f18fe...` before any
   mutation.
3. Run:

   ```powershell
   .venv\Scripts\python.exe plans\codex\handover\validate_handover.py --require-clean --self-test
   .venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
   ```

4. Register a fresh coordination identity. Never reuse the identity, token,
   lease, or execution manifest recorded by an earlier shift.
5. Read [the exact next microstep](NEXT-MICROSTEP.yaml), create fresh skill
   manifests, claim only its exact paths, run the mutation guard, and begin
   with the named RED test.
6. Before the shift ends: make the bounded increment green, commit explicit
   files, push GitLab `main`, replay the immutable commit, append one native
   FF6 event, refresh this packet, validate it, then release only your leases.

If another live agent owns the XLIFF paths, do not overlap or wait. Select the
highest-severity unleased FF6 obligation, normally the UBL-03 continuation in
[the machine state](CURRENT-MACHINE-STATE.yaml), and journal that bounded
progress before returning to XLIFF.

## Current operational documents

- [Exact Claude commands](CLAUDE-START.md)
- [Active checkpoint and achieved work](ACTIVE-WORK-CHECKPOINT.md)
- [Machine-readable state](CURRENT-MACHINE-STATE.yaml)
- [Checkpoint digest contract](checkpoint.yaml)
- [Exact next microstep](NEXT-MICROSTEP.yaml)
- [Outgoing shift record](CURRENT-SHIFT-HANDOVER.md)
- [Recovery contract](INFLIGHT-RECOVERY.yaml)
- [Packet manifest](manifest.yaml)
- [Provider shift invariants](PROVIDER-SHIFT-CONTRACT.md)
- [Shift/resume protocol](SHIFT-AND-RESUME-PROTOCOL.md)
- [Execution runbook](EXECUTION-RUNBOOK.md)
- [State-machine/taskcard protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
- [Validation and release rules](VALIDATION-AND-RELEASE.md)
- [UBL parallel checkpoint](PARALLEL-UBL-CHECKPOINT.yaml)

## Canonical authorities

- [Product goal](../../strategic/ff6/product-goal.yaml)
- [Controller projection](../../strategic/ff6/controller-state.yaml)
- [Native event journal](../../strategic/ff6/events.jsonl)
- [Current XLIFF taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
- [Accepted XLIFF repair proof](../../../reports/ff6/xliff-core-pairing-repair-run-manifest.yaml)

The journal, controller, taskcard, evidence, and Git objects override this
derived packet if a newer valid event exists. Recompute; never hand-edit a
status to make documents agree.
