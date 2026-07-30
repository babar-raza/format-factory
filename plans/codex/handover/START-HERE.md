---
artifact_id: FF6-HANDOVER-START-EVENT-34
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
local bytes. The native head is `FF6-EVENT-000034` /
`7cab150d9d49deeba140c6a0ce56e619ae560f8b0abc7510e555ca54d6f307da`.
Its latest immutable implementation is GitLab commit
`8e61ee11e7598b22093d397f4006d4f189b681d4`. XLIFF's accepted implementation
boundary remains `ff8f7d9f9ff1ff613be376e1361b0dd8304566e3`, and the canonical
continuation remains `XLF-04-BATCH-005-PARTIAL-002-C`.

## Mission

Deliver six independently publishable, professional Python libraries for
Jupyter Notebook, OpenRaster, NRRD, XLIFF, SafeTensors, and OASIS UBL. Each
library must provide the full practical format surface developers need,
production-grade architecture and typing, secure parsing and writing,
independent interoperability evidence, installed-wheel proof, and reproducible
release artifacts. Planning, source presence, test counts, contract compilation,
or a passing smoke test do not certify a product.

Current truth: controller `CONTRACT`, Event 34, `0/6` certified, every product
`UNASSESSED`. XLIFF is the selected lane because its complete stable contract
surface is still open. Event 34 additionally verifies 6,001 UBL local particle
nodes across 468 owners and stable anonymous-type identity machinery. The
pinned official package contains zero anonymous types, so this behavior is
proved with adversarial synthetic schemas and does not complete UBL-03.

The selected XLIFF candidate has three distinct digests. Do not substitute
one for another:

- candidate content:
  `647b9f67a1c64e9e9030652e9c527666fa8aadeb521ed48fda87cebcecbcb6b1`;
- normalized requirement:
  `bebad4a8709a137a204c13bf6a058d6c38e512099ebcf5ed7119e2668f38f61d`;
- occurrence:
  `bd3194ac5b25856e984d3eec9c38cb76f8b912fb63679034e236b766b8f6ca77`.

Earlier Event 32 packet bytes mislabeled the requirement digest as the
candidate-content digest. This packet corrects the label without changing the
candidate, authority, event, task, accepted counts, or product state.

## Mandatory resume order

1. Read [AGENTS.md](../../../AGENTS.md), then
   [Claude start](CLAUDE-START.md).
2. Fetch GitLab and require `HEAD == origin/main`, with `8e61ee11...` as an
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
   owner's scope. Event 34 also records seven exact XLIFF occurrence paths and
   both their baseline and occurrence hashes. Those bytes are non-promoting
   until governed takeover plus independent replay. Any other unattributed
   dirty path fails the transfer.
5. Register a fresh coordination identity. Never reuse the identity, token,
   lease, or execution manifest recorded by an earlier shift.
6. Read [the exact next microstep](NEXT-MICROSTEP.yaml), create fresh skill
   manifests, claim only its exact paths, run the mutation guard, and begin
   with the named RED test.
7. Before the shift ends: make the bounded increment green, commit explicit
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
- [Provider shift invariants](PROVIDER-SHIFT-CONTRACT.md), current Event 34
  overlay plus durable historical rationale.
- [Shift/resume protocol](SHIFT-AND-RESUME-PROTOCOL.md), current Event 34
  overlay plus historical failure examples.
- [Execution runbook](EXECUTION-RUNBOOK.md), durable phase procedure; current
  routing comes only from the Event 34 overlay and `NEXT-MICROSTEP.yaml`.
- [State-machine/taskcard protocol](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md),
  durable transaction rules with an Event 34 overlay.
- [Validation and release rules](VALIDATION-AND-RELEASE.md), durable gates and
  Event 31 as a retained negative control, not current routing.
- [UBL parallel checkpoint](PARALLEL-UBL-CHECKPOINT.yaml), historical
  foundation plus the current Event 34 UBL boundary.

## Canonical authorities

- [Product goal](../../strategic/ff6/product-goal.yaml)
- [Controller projection](../../strategic/ff6/controller-state.yaml)
- [Native event journal](../../strategic/ff6/events.jsonl)
- [Current XLIFF taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md)
- [Current UBL fallback taskcard](../../../taskcards/TC-FF6-UBL-TYPING-001.md)
- [Handover refresh taskcard](../../../taskcards/TC-FF6-HANDOVER-CLAUDE-001.md)
- [Accepted XLIFF repair proof](../../../reports/ff6/xliff-core-pairing-repair-run-manifest.yaml)
- [UBL anonymous-type TDD proof](../../../reports/skills-rff6/skill-transcripts/test-driven-development-ubl-schema-graph-004.json)
- [Event 34 handover receipt](../../../reports/skills-rff6/skill-transcripts/refresh-provider-neutral-handover-event-34.json)

The journal, controller, taskcard, evidence, and Git objects override this
derived packet if a newer valid event exists. Recompute; never hand-edit a
status to make documents agree.
