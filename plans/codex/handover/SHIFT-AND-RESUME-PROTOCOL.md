---
artifact_id: FF6-SHIFT-RESUME-PROTOCOL-001
artifact_type: provider_neutral_checkpoint_protocol
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
---

# Provider-Neutral Shift and Resume Protocol

## Invariant

Claude and Codex are interchangeable executors. The durable resume key is:

```text
GitLab origin/main commit
+ native FF6 controller and hash-chained journal
+ current taskcard and task index
+ current gaps and proof digests
+ off-repo coordination ownership
```

Conversation history, provider memory, model identity, and remaining token
budget are not operational authority.

Only one provider may own the active task's write scope at a time. Claude and
Codex may work in successive shifts, but they are not parallel writers for the
same taskcard or generated output set. Parallel work is allowed only for
disjoint, separately taskcarded scopes with non-overlapping leases.

## Current transfer boundary

- Required implementation ancestor before this packet:
  `4f0e8793d7aa694ccb45a57e9d3abc8f8cce92f7`.
- Use the fetched `origin/main` descendant containing this packet.
- Controller state: `CONTRACT`.
- Event: `FF6-EVENT-000023`.
- Event hash:
  `01c265ecd5284320a82f31316b404e3f3f4edbab3b92cd071be8f9ec27f83641`.
- Completed task: `TC-FF6-NRRD-PROFILE-SURFACE-001` - `PASS`.
- Active task: `TC-FF6-XLIFF-PROFILE-SURFACE-001` -
  `WORK_IN_PROGRESS`; XLF-01/XLF-02/XLF-03 and XLF-04-BATCH-001 complete,
  XLF-04 still first unmet.
- Shift microstate: `RESUMABLE`; the XLF-03 matrix and first seven
  source-bound Core obligations are validated at their declared boundary,
  while the complete Core denominator and semantics remain.
- Exact next action: XLF-04-BATCH-002 RED tests for the three named categories.
- Product promotion: none.

## Incoming provider procedure

1. Fetch `origin/main`; do not use GitHub or a provider branch.
2. Verify `4f0e8793d7aa694ccb45a57e9d3abc8f8cce92f7` is an ancestor.
3. Verify the worktree is clean before new mutation.
4. Read the ordered authority list in `START-HERE.md`.
5. Validate the journal through event 23 using FF6 native semantics:
   `previous_event_hash`, canonical JSON, sequential event IDs and hashes.
6. Verify controller head, parent/child task states, task index, current gaps,
   authority 17/17 global and 5/5 XLIFF match, and capability manifest
   digests.
7. Query coordination status.
8. Register a new identity for the incoming provider.
9. Confirm no live owner remains on the next task paths.
10. Claim logical task scope, exact tracked paths, generated output
    directories, transcript, and artifact directory.
11. Resolve the required registered skills and run the mutation guard.
12. Capture input baselines before writing.
13. Validate `reports/ff6/xliff-authority-member-inventory.yaml` against both
    pinned packages; replay 23 extractor tests, exact file digests, matrix
    check mode, static checks, and three identical outputs for both generated
    reports; then start `XLF-04-BATCH-002` as specified in
    `STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`. Re-run completed steps only if
    their recorded inputs were invalidated.

The new provider reconstructs the state; it does not accept a prior provider's
claim on trust. A mismatch produces a named discrepancy and invalidates only
the affected descendants. It does not authorize deleting the prior work,
resetting main, or rerunning unrelated completed taskcards.

Claude's hooks may auto-claim single files, but broad generated output sets
still require explicit claims. Codex follows the CLI protocol in
`docs/governance/codex-adapter.md`.

## Outgoing provider procedure

1. Stop only after the current microstep is `GREEN_VERIFIED`; do not plan a
   shift in `RED_OBSERVED`.
2. Record completed and pending behavior in the task skill receipt.
3. Run focused and required regression/static verification.
4. Stage only the coherent implementation/test/receipt files using an explicit
   reviewed list; run the precommit coordination check.
5. Fetch and classify remote movement, then commit the implementation slice.
6. Append the WIP/repair/close event referencing that immutable implementation
   commit and its source/test/evidence digests.
7. Refresh taskcard, index, gaps, controller, and this packet from the new
   journal head.
8. Validate all packet links, YAML/JSON, hashes, task agreement, and event
   chain.
9. Stage only the explicit control/packet/receipt files; run the precommit
   coordination check; commit the checkpoint projection.
10. Fetch again, classify any new remote movement, and push both commits only
    to GitLab main.
11. Verify remote main equals the checkpoint commit and contains the
    implementation commit as an ancestor.
12. Write/validate local receipt and evidence bundle as required.
13. Complete only the outgoing provider's coordination session.

Never transfer an uncommitted chat-only state as a clean checkpoint.

If the whole taskcard cannot finish in the current shift, the outgoing
provider must stop after an atomic microstep that leaves all touched artifacts
valid and the declared regression tier passing. It records
`WORK_IN_PROGRESS`, completed step IDs, the first unmet step, microstate,
immutable implementation commit, input/output digests, exact next test, and
validation outcomes. Broken, RED-only, or self-contradictory source is not a
checkpoint and must not be pushed to satisfy a token boundary.

## Token-budget and planned-shift protocol

The executor monitors its practical context/token boundary as an operational
resource, not as a mission exit criterion.

1. Before beginning a RED test, reserve enough capacity to implement GREEN,
   run its focused and regression tiers, write the receipt, and publish the
   two-commit checkpoint.
2. If that capacity is not available, do not mutate; refresh the current clean
   packet and transfer at the last `RESUMABLE` state.
3. If capacity becomes constrained after RED, finish or safely revert only the
   executor's own bounded uncommitted microstep. Never discard another
   provider's bytes or publish RED as a checkpoint.
4. A planned shift ends only after remote verification and completion of the
   outgoing coordination identity.
5. The incoming provider registers a fresh identity and independently replays
   the checkpoint before mutation.

This makes provider rotation a normal state transition rather than an
exception that can create competing local truths.

## Crash and partial-state recovery matrix

| Observed state | Incoming action |
|---|---|
| Remote packet and implementation commits present; outgoing identity complete | Replay and resume the exact next microstep |
| Implementation commit present, packet commit absent | Validate the implementation commit, append or replay the missing journal/projection checkpoint without duplicating the implementation |
| Journal event present, projection/packet stale | Rebuild projections from the journal; do not append a duplicate event |
| Uncommitted GREEN tree owned by stale provider | Governed takeover, capture hashes, rerun required checks, then commit/journal |
| Uncommitted RED tree owned by stale provider | Governed takeover, preserve and classify; continue to GREEN or revert only that bounded owned microstep |
| Dirty bytes have no attributable owner | Preserve, register a conflict/gap, and continue only disjoint safe work |
| Remote main advanced on overlapping paths | Fetch, classify, integrate without history loss, and replay invalidated proof |
| Packet disagrees with valid journal/controller | Treat packet as stale and regenerate it from canonical state |

## During a shift

- One bounded taskcard owns each change set.
- Resume from the first unmet acceptance criterion, not from prose memory.
- Recompute a completed substep only if its inputs were invalidated.
- Preflight before every write and record every write.
- Heartbeat during long execution.
- Preserve unrelated dirty state.
- Never use broad staging, broad formatters, stash, reset, restore, clean, or
  checkout-discard.
- Never release another agent's lease.
- If remote main advances, fetch, classify overlap, and replay affected proof.
- A blocked format does not stop safe work on another.
- Promotion is computed from proof, never edited.

## Safe takeover

Takeover applies only to a stale or crashed owner. Use the governed
coordination `takeover --reason` operation. The successor must:

1. capture current hashes;
2. classify every existing change;
3. preserve unexplained content;
4. establish new leases;
5. rerun affected verification.

Lease expiry alone is not permission to discard filesystem content.

## Checkpoint meanings

| State | Resume behavior |
|---|---|
| `READY` | Claim and execute exact task |
| `WORK_IN_PROGRESS` | Take over safely and resume first unchecked step |
| `NEEDS_REPAIR` | Execute the recorded deterministic repair |
| `TECHNICALLY_BLOCKED` | Continue another unblocked path |
| `PASS` | Verify close projection; do not infer product certification |
| `COMPLETE` | Select the journaled successor |

## Digest and line-ending rule

For tracked text, use Git identity plus LF-normalized SHA-256. Raw Windows bytes
are not canonical when checkout settings transform line endings.

Canonical event hashing uses UTF-8 JSON with sorted keys and compact separators,
excluding `event_hash`.

## Native FF6 journal check

Use this check from the repository root. It validates the complete chain and
requires controller agreement; it does not modify files.

```powershell
@'
import hashlib
import json
import pathlib
import yaml

events_path = pathlib.Path("plans/strategic/ff6/events.jsonl")
controller_path = pathlib.Path("plans/strategic/ff6/controller-state.yaml")
events = [
    json.loads(line)
    for line in events_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
previous = None
for sequence, event in enumerate(events, 1):
    assert event["schema"] == "ff6/controller-event@1"
    assert event["sequence"] == sequence
    assert event["event_id"] == f"FF6-EVENT-{sequence:06d}"
    assert event.get("previous_event_hash") == previous
    claimed = event["event_hash"]
    body = dict(event)
    del body["event_hash"]
    observed = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert observed == claimed, event["event_id"]
    previous = claimed

controller = yaml.safe_load(controller_path.read_text(encoding="utf-8"))
assert controller["transition_sequence"] == len(events)
assert controller["last_verified_event"]["event_hash"] == previous
print(f"PASS events={len(events)} head={previous}")
'@ | python -
```

## Generic Plan Control contradiction

`python -m tools.plan_control --control-root plans/strategic/ff6 doctor`
currently fails at event 1 because it expects `previous_hash`. FF6 uses
`previous_event_hash` under `ff6/controller-event@1`.

This is `FF6-GAP-011`, not evidence that event 23 is corrupt. Validate the FF6
native chain and do not edit either journal schema ad hoc.

## XLIFF completed surface and next semantic denominator

The completed XLF-03 real-package check uses 293 XLIFF 2.0 and 420 XLIFF 2.1 DocBook
`section` elements. Direct IDs exist on only 197 and 312 of those sections.
The remaining sections use deterministic title-path locations. Both numbers
are useful diagnostics, but only 293/420 are the complete section denominator.
Changing the acceptance count to the ID-bearing subset would silently remove
source evidence. Conversely, the 36 matrix rows are not a denominator for
fine-grained semantic obligations. The seven batch-001 obligations also are
not the denominator: their status is `SOURCE_BOUND_UNVERIFIED`, and the report
must remain incomplete until an explicit expected-obligation ID set is
compiled and fully matched. XLF-04 must enumerate complete Core rules with
exact authority locations and profile applicability; XLF-05 must do the same
for each official module.

## Transfer acceptance

A provider switch is safe only when:

- the checkpoint is present on remote main;
- controller, journal, taskcard, task index, gaps, and packet agree;
- all continuation inputs are tracked or immutable content-addressed inputs;
- no required result exists only in chat;
- prior ownership is completed or governed takeover is recorded;
- the next step and acceptance criteria are deterministic;
- known failures and limits remain visible;
- promotion is no stronger than live proof.
