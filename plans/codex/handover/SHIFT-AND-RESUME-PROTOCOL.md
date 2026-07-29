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

## Current transfer boundary

- Required ancestor before this packet: `9437dcc47763c17ce090ce538d2ff7ba5350da0d`.
- Use the fetched `origin/main` descendant containing this packet.
- Controller state: `CONTRACT`.
- Event: `FF6-EVENT-000017`.
- Event hash:
  `44cb90a67aec8fff244de05d84c047f1d31077d694eda1ff1e27ee0aaa0f3015`.
- Completed task: `TC-FF6-AUTHORITY-CLOSURE-001` - `PASS`.
- Next task: `TC-FF6-IPYNB-PROFILE-SURFACE-001` - `READY`.
- Product promotion: none.

## Incoming provider procedure

1. Fetch `origin/main`; do not use GitHub or a provider branch.
2. Verify `9437dcc47763c17ce090ce538d2ff7ba5350da0d` is an ancestor.
3. Verify the worktree is clean before new mutation.
4. Read the ordered authority list in `START-HERE.md`.
5. Validate the journal through event 17 using FF6 native semantics:
   `previous_event_hash`, canonical JSON, sequential event IDs and hashes.
6. Verify controller head, parent/child task states, task index, current gaps,
   authority 15/15 match, and capability manifest digests.
7. Query coordination status.
8. Register a new identity for the incoming provider.
9. Confirm no live owner remains on the next task paths.
10. Claim logical task scope, exact tracked paths, generated output
    directories, transcript, and artifact directory.
11. Resolve the required registered skills and run the mutation guard.
12. Capture input baselines before writing.
13. Begin the first OpenRaster taskcard step.

Claude's hooks may auto-claim single files, but broad generated output sets
still require explicit claims. Codex follows the CLI protocol in
`docs/governance/codex-adapter.md`.

## Outgoing provider procedure

1. Stop only at a truthful task boundary.
2. Record completed and pending substeps in tracked state.
3. Run focused and required regression verification.
4. Journal close intent and verified close, or truthful WIP/repair state.
5. Refresh taskcard, index, gaps, controller, and this packet.
6. Validate all packet links, YAML, hashes, and event chain.
7. Stage only an explicit reviewed file list.
8. Run precommit coordination checks.
9. Fetch and classify remote movement.
10. Commit and push to GitLab main.
11. Verify remote main equals the commit.
12. Write/validate local receipt and evidence bundle as required.
13. Complete only its own coordination session.

Never transfer an uncommitted chat-only state as a clean checkpoint.

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

## Generic Plan Control contradiction

`python -m tools.plan_control --control-root plans/strategic/ff6 doctor`
currently fails at event 1 because it expects `previous_hash`. FF6 uses
`previous_event_hash` under `ff6/controller-event@1`.

This is `FF6-GAP-011`, not evidence that event 17 is corrupt. Validate the FF6
native chain and do not edit either journal schema ad hoc.

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
