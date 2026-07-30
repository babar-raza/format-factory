---
artifact_id: FF6-HANDOVER-START-EVENT-35
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
local bytes. The native head is `FF6-EVENT-000035` /
`2866d7e70bd193f8aa7b60ca1f92f4f842d1cd470f97984c07f47d88ed2ea97d`.
Its immutable XLIFF implementation is GitLab commit
`591fcfe18808e5195c33570eaa9d334770e90166`, and the canonical continuation is
`XLF-04-BATCH-005-PARTIAL-002-D`.

## Mission

Deliver six independently publishable, professional Python libraries for
Jupyter Notebook, OpenRaster, NRRD, XLIFF, SafeTensors, and OASIS UBL. Each
library must provide the full practical format surface developers need,
production-grade architecture and typing, secure parsing and writing,
independent interoperability evidence, installed-wheel proof, and reproducible
release artifacts. Planning, source presence, test counts, contract compilation,
or a passing smoke test do not certify a product.

Current truth: controller `CONTRACT`, Event 35, `0/6` certified, every product
`UNASSESSED`. XLIFF is the selected lane because its complete stable contract
surface is still open. Event 35 accepts only 28 of 105 Core obligations and 4
of 1,130 candidate dispositions. Event 34 separately verifies 6,001 UBL local particle
nodes across 468 owners and stable anonymous-type identity machinery. The
pinned official package contains zero anonymous types, so this behavior is
proved with adversarial synthetic schemas and does not complete UBL-03.

The selected XLIFF candidate has three distinct digests. Do not substitute
one for another:

- candidate content:
  `af94362009857b0fdd3d19881cd2c8d1866e4f5a72849ec1edf057baf7e905a1`;
- normalized requirement:
  `d36657a907cd8be2ecf38d3fa7a78b3c3720486492cdadd09f4f0f7c25f30e84`;
- occurrence:
  `96949f8b0f510d573b4c95640fae3e68175b853410865eaf1460a5eaee4f332a`.

These identify the still-unadjudicated reciprocal report at
`schematron/rule[11]/report[2]`; they are not the digests of the report already
accepted by Event 35.

## Mandatory resume order

1. Read [AGENTS.md](../../../AGENTS.md), then
   [Claude start](CLAUDE-START.md).
2. Fetch GitLab and require `HEAD == origin/main`, with
   `ae31baed8bfeb8a35c4ece8e52283114ee48d860` as an
   ancestor, before any mutation. The packet commit is necessarily later than
   the control checkpoint.
3. First validate the committed GitLab checkpoint in a detached worktree:

   ```powershell
   .venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
   ```

4. Query coordination and Git status. If the shared worktree is clean, also
   run `validate_handover.py --require-clean --self-test`. If dirty paths have
   a current foreign owner, preserve them and use the detached validation as
   the packet proof; do not call the packet corrupt and do not enter that
   owner's scope. UBL partial-005 was committed at `d8c10680`, checkpointed at
   `ae31baed`, and its executor completed cleanly before this packet was
   sealed. The UBL result is verified partial progress but is not part of Event
   35 promotion. Re-query coordination and replay both commits before entering
   partial-006. Any unattributed dirty path fails the transfer.
5. Register a fresh coordination identity. Never reuse the identity, token,
   lease, or execution manifest recorded by an earlier shift.
6. Read [the exact next microstep](NEXT-MICROSTEP.yaml), create fresh skill
   manifests, claim only its exact paths, run the mutation guard, and begin
   with the named RED test.
7. Before the shift ends: make the bounded increment green, commit explicit
   files, push GitLab `main`, replay the immutable commit, append one native
   FF6 event, refresh this packet, validate it, then release only your leases.

If another live agent owns the XLIFF paths, do not overlap or wait. Select the
highest-severity unleased FF6 obligation. UBL partial-006 is an eligible
fallback only if a fresh coordination query shows it unleased and its two
predecessor commits replay cleanly. Any fallback must remain disjoint and must
not change the controller-selected XLIFF task.

## Current operational documents

- [Exact Claude commands](CLAUDE-START.md)
- [Active checkpoint and achieved work](ACTIVE-WORK-CHECKPOINT.md)
- [Machine-readable state](CURRENT-MACHINE-STATE.yaml)
- [Checkpoint digest contract](checkpoint.yaml)
- [Exact next microstep](NEXT-MICROSTEP.yaml)
- [Outgoing shift record](CURRENT-SHIFT-HANDOVER.md)
- [Recovery contract](INFLIGHT-RECOVERY.yaml)
- [Packet manifest](manifest.yaml)
- [Provider shift invariants](PROVIDER-SHIFT-CONTRACT.md), current Event 35
  overlay plus durable historical rationale.
- [Shift/resume protocol](SHIFT-AND-RESUME-PROTOCOL.md), current Event 35
  overlay plus historical failure examples.
- [Execution runbook](EXECUTION-RUNBOOK.md), durable phase procedure; current
  routing comes only from the Event 35 overlay and `NEXT-MICROSTEP.yaml`.
- [State-machine/taskcard protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md),
  durable transaction rules with an Event 35 overlay.
- [Validation and release rules](VALIDATION-AND-RELEASE.md), durable gates and
  Event 31 as a retained negative control, not current routing.
- [UBL parallel checkpoint](PARALLEL-UBL-CHECKPOINT.yaml), historical
  foundation plus the Event 34 verified UBL boundary and Event 35 supersession.

## Canonical authorities

- [Product goal](../../strategic/ff6/product-goal.yaml)
- [Controller projection](../../strategic/ff6/controller-state.yaml)
- [Native event journal](../../strategic/ff6/events.jsonl)
- [Current XLIFF taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
- [Current UBL fallback taskcard](../../../taskcards/TC-FF6-UBL-TYPING-001.md)
- [Handover refresh taskcard](../../../taskcards/TC-FF6-HANDOVER-CLAUDE-001.md)
- [Accepted XLIFF repair proof](../../../reports/ff6/xliff-core-pairing-repair-run-manifest.yaml)
- [UBL anonymous-type TDD proof](../../../reports/skills-rff6/skill-transcripts/test-driven-development-ubl-schema-graph-004.json)
- [Event 35 handover receipt](../../../reports/skills-rff6/skill-transcripts/refresh-provider-neutral-handover-event-35.json)

The journal, controller, taskcard, evidence, and Git objects override this
derived packet if a newer valid event exists. Recompute; never hand-edit a
status to make documents agree.
