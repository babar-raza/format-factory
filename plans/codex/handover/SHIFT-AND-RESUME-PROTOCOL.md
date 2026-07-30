---
artifact_id: FF6-SHIFT-RESUME-PROTOCOL-001
artifact_type: provider_neutral_checkpoint_protocol
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
authoritative_state: false
historical_projection: true
---

# Provider-Neutral Shift and Resume Protocol

> Durable provider-shift protocol refreshed through Event 30. Current exact
> work is defined by [START-HERE.md](START-HERE.md),
> [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml), the native FF6 journal, and the
> immutable [Event 30 packet](event-30/START-HERE.md).

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

- Required XLIFF implementation ancestor:
  `e13e103de0bb789ff51a8e931af0fb649474be20`.
- Use the fetched `origin/main` descendant containing this packet.
- Controller state: `CONTRACT`.
- Event: `FF6-EVENT-000030`.
- Event hash:
  `2d365d013b94c386014d7e75813114de6d7a225e2a9e16d21a485a38cd2d9398`.
- Completed task: `TC-FF6-NRRD-PROFILE-SURFACE-001` - `PASS`.
- Active task: `TC-FF6-XLIFF-PROFILE-SURFACE-001` -
  `WORK_IN_PROGRESS`; XLF-01/XLF-02/XLF-03 and XLF-04 batches 001-004
  complete, XLF-04 still first unmet.
- Canonical event microstate: `RESUMABLE` at Event 30.
- Exact next action: `XLF-04-BATCH-005-PARTIAL-002-B`.
- Current boundary: 1,130 source-authentic candidates, one verified
  disposition, 26/105 source-bound IDs, and 79 missing rows.
- Workspace boundary: no product overlay and no provider-local recovery asset.
- Product promotion: none.

## Incoming provider procedure

1. Fetch `origin/main`; do not use GitHub or a provider branch.
2. Verify `e13e103de0bb789ff51a8e931af0fb649474be20` is an ancestor
   of fetched GitLab main.
3. Read `INFLIGHT-RECOVERY.yaml` and verify that no local recovery asset is
   required.
4. Read the ordered authority list in `START-HERE.md`.
5. Validate the journal through Event 30 using FF6 native semantics:
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
13. Replay Event 30 using `event-30/RUNBOOK.md`: verify both adjudication and
    obligation check modes, the three immutable smoke tests, exact
    adjudication and inventory digests, 5/5 XLIFF authority replay, and
    controller/taskcard agreement. Re-run broader completed behavior only if
    a bound input was invalidated.
14. Read `NEXT-MICROSTEP.yaml`; begin with its fixed candidate and RED
    controls, not a newly selected convenience batch.

## Implementation-only commit recovery

The former implementation-only recovery conditions are closed. GitLab
contains immutable implementation commit
`e13e103de0bb789ff51a8e931af0fb649474be20` and the Event 30 packet.
Incoming providers must verify the ancestor and must not append a duplicate
Event 30. `INFLIGHT-RECOVERY.yaml` records that no provider-local byte is
required.

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

### Handover transaction boundary

The transfer is a two-plane transaction:

| Plane | Durable commit content | Resume-time action |
|---|---|---|
| Product/control | implementation commit, native event, controller/task projections, proof digests, packet manifest | fetch and independently replay from GitLab `origin/main` |
| Coordination | provider identity, lease ownership, write journal, conflict state | query live; outgoing provider completes its own identity; incoming provider registers and claims anew |

The tracked packet must never claim that a coordination identity will remain
complete indefinitely. It records the requirement and the last verified
product/control boundary. The coordination CLI decides current ownership at
resume time. This prevents a packet commit from becoming stale merely because
a later provider registered, while still preventing simultaneous writers.

A shift is accepted only when all of the following are true:

1. GitLab `origin/main` contains the coherent implementation commit and its
   descendant checkpoint commit.
2. The native event identifies that implementation commit, exact output
   digests, validation boundary, first unmet criterion, and next action.
3. The derived packet hashes and links pass from the fetched bytes.
4. No required state exists only in chat, provider memory, an ignored
   worktree, or an unpushed commit.
5. The outgoing provider has completed its own coordination identity after
   remote verification.
6. The incoming provider independently replays the checkpoint and obtains new
   ownership before its first write.

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
| Implementation commit present, packet commit absent | Historical batch-003 case, now resolved by `220ee7f5`; preserve and verify both commits |
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

This is `FF6-GAP-011`, not evidence that Event 30 is corrupt. Validate the FF6
native chain and do not edit either journal schema ad hoc.

## XLIFF completed surface and next semantic denominator

The completed XLF-03 real-package check uses 293 XLIFF 2.0 and 420 XLIFF 2.1 DocBook
`section` elements. Direct IDs exist on only 197 and 312 of those sections.
The remaining sections use deterministic title-path locations. Both numbers
are useful diagnostics, but only 293/420 are the complete section denominator.
Changing the acceptance count to the ID-bearing subset would silently remove
source evidence. Conversely, the 36 matrix rows and the 1,130 candidate rows
are not themselves a denominator for verified semantic obligations. The 25
source-bound obligation rows are also not the denominator: their status is
`SOURCE_BOUND_UNVERIFIED`, and the report must remain incomplete until all
candidate dispositions are independently adjudicated and the 105-ID expected
set is fully matched. XLF-04 must enumerate complete Core rules with exact
authority locations and profile applicability; XLF-05 must do the same for
each official module. The first adjudication batch and its negative controls
are fixed in `NEXT-MICROSTEP.yaml`.

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
