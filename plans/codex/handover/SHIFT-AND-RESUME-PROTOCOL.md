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

Claude and Codex are interchangeable executors, not separate sources of state.
Neither conversation history nor provider-local memory may unlock work.

The resumable state is:

```text
GitLab commit
+ FF6 controller projection
+ hash-chained FF6 event journal
+ current taskcard
+ current evidence/proof digests
+ off-repo coordination ownership
```

At this transfer, the last pre-shift source commit is
`2129ad278c5d7a8b7f81559388489e6231def550`. The reconstructable shift
checkpoint is the GitLab-main descendant containing controller state
`CONTRACT`, event 14, parent `TC-FF6-PROGRAM-CAPABILITIES-001` in
`NEEDS_REPAIR`, and active task `TC-FF6-AUTHORITY-CLOSURE-001` in
`WORK_IN_PROGRESS`. The exact completed and pending substeps are in
`ACTIVE-WORK-CHECKPOINT.md`.

## Start of every shift

1. Fetch `origin/main`.
2. Verify that the expected checkpoint is an ancestor of `origin/main`.
3. Create a fresh detached worktree from the exact current `origin/main`.
4. Read `START-HERE.md` and its ordered authorities.
5. Validate normalized digests and the FF6 event chain.
   At this packet version, require event 14 with hash
   `399a5069b3c843d1b4f668a8f7abeb0deffe40a234a584f6c9f7b5b3a3e70fc8`.
6. Run current-state consistency and focused plan-control tests.
7. Query coordination status.
8. Register a new provider identity.
9. Claim the task logical scope, worktree, exact output directories, taskcard,
   controller projection, event journal, and transcript.
10. Run provider preflight and the registered skill mutation guard.
11. Recompute the task's inputs before writing.
12. Compare each event-14 WIP path against its recorded LF-normalized digest.
    If any differs, classify it through coordination before executing.

Claude hooks may register and auto-claim individual files, but broad scopes and
generated output sets still require explicit claims. Codex must perform every
CLI step in `docs/governance/codex-adapter.md`.

## During a shift

- One taskcard owns one bounded, explicit changed-file set.
- Resume the first unchecked atomic step in the active taskcard. Do not restart
  completed steps unless their recorded input digest is invalidated.
- Before every write, preflight the target.
- After every write, record the resulting digest.
- Heartbeat during long work.
- Do not use `git add .`, `git add -A`, broad formatters, stash, reset, restore,
  checkout-discard, or clean.
- Do not resolve another agent's conflict or lease.
- If `origin/main` advances, stop integration, fetch, classify the delta, and
  replay affected verification.
- Use only GitLab `origin/main`; do not create provider branches or push to the
  configured GitHub remote.
- Do not edit promotion state directly.
- Do not let a blocked format stop safe work on another format.

## Checkpoint states

| State | Meaning | May next agent continue? |
|---|---|---|
| `INTENT_RECORDED` | Write-ahead event exists, mutation not yet verified | Only after inspecting owned worktree and task transcript |
| `WORK_IN_PROGRESS` | Bounded files changed, verification incomplete | Yes, after governed takeover and baseline recapture |
| `NEEDS_REPAIR` | Evidence failed and root cause is recorded | Yes, execute deterministic repair task |
| `TECHNICALLY_BLOCKED` | Three materially different repairs failed | Continue other unblocked work |
| `PASS` | Task acceptance passed, but task may not imply product completion | Yes, verify close projection |
| `COMPLETE` | Task closed with committed, pushed, remote-verified proof | Yes, select journaled next task |

Never label partial work `COMPLETE` merely to create a clean handoff.

## End of every shift

### If the task is complete

1. Run focused validation and required regression tier.
2. Write `TASK_CLOSE_INTENT`.
3. Compute all output and evidence digests.
4. Independently validate the output.
5. Write `TASK_CLOSED`.
6. Update controller state and task index.
7. Validate the event chain from event 1.
8. Stage exact paths.
9. Run coordination precommit check with the owning identity.
10. Fetch `origin/main` and verify expected ancestry.
11. Commit on the detached worktree.
12. Push `HEAD:main`.
13. Verify `refs/heads/main` equals the commit.
14. Write the local receipt and validate it.
15. Complete the coordination session.

### If the task is incomplete

1. Do not push a failing or internally contradictory source change.
2. A bounded partial implementation may be pushed only when it is internally
   valid, tested at its declared tier, explicitly non-promoting, and journaled
   as `WORK_IN_PROGRESS`.
3. Record exact completed substeps, changed files, failing command, evidence,
   root cause, and next deterministic action.
4. Prefer a clean committed checkpoint only when the partial artifact is valid,
   explicitly non-promoting, and the taskcard state is truthful.
5. Otherwise retain the isolated worktree, abandon the coordination session
   with a reason, and require governed takeover.
6. Never rely on ignored local files as the only checkpoint.

## Transfer handshake

The outgoing provider:

1. writes and validates the checkpoint event;
2. commits and remote-verifies the exact tracked paths;
3. records the final write set and commit in its local receipt;
4. completes its coordination session, releasing only its own leases.

The incoming provider:

1. fetches and validates the remote checkpoint before registering;
2. registers a new provider identity;
3. confirms no active owner remains;
4. claims the task and exact output paths;
5. if the prior owner is stale rather than complete, uses governed takeover
   with a reason and recaptures every baseline;
6. continues from the first unchecked taskcard step.

There is never a period in which two providers may mutate the same task scope.
The handoff packet transfers intent; the coordination plane transfers write
authority.

## Takeover

Takeover is allowed only for a stale/crashed owner and must use:

```powershell
python -m tools.supervisor.coordination takeover --help
```

The successor records a reason, claims the same scope, captures hashes before
writing, classifies every existing change, and preserves unexplained content.
Expiry alone is not permission to delete anything.

## Digest rule

For tracked text, compare both Git identity and LF-normalized SHA-256:

```powershell
git rev-parse HEAD:<path>
@'
from pathlib import Path
import hashlib
p = Path(r"<path>")
print(hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest())
'@ | python -
```

Raw Windows file bytes are diagnostic only when `core.autocrlf` can transform
line endings.

## Provider switch acceptance

A provider switch is safe only if:

- remote main contains the claimed checkpoint;
- all task inputs can be reconstructed from tracked files or immutable
  content-addressed artifacts;
- no required result exists only in chat or an ignored file;
- task ownership is released or transferred through coordination;
- next task and dependencies are journaled;
- failing and stale evidence remains visible;
- product promotion is no stronger than current proof.
