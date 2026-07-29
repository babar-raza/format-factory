---
artifact_id: FF6-AGENT-HANDOVER-START-001
artifact_type: agent_handover_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
canonical_state_path: plans/strategic/ff6/controller-state.yaml
---

# Start Here: Six Python Production Libraries

This is the one provider-neutral entry point for Claude, Codex, or another
governed executor continuing mission `FF6-PRODUCTION-LIBRARIES-001`.

Absolute Windows path:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

The packet is derived navigation. Canonical truth remains the GitLab commit,
FF6 goal, journal, controller, current gaps, taskcards, contracts, source,
tests, and executed proof.

## Verified checkpoint

| Field | Current truth |
|---|---|
| Forge | GitLab only |
| Remote/branch | `origin/main` |
| Controller state | `CONTRACT` |
| Journal head | `FF6-EVENT-000016` |
| Event hash | `2ea206536ff0ccecaa0a4e93df32ada3e7575018f4cdcafb7525c59d51dd50ba` |
| Parent | `TC-FF6-PROGRAM-CAPABILITIES-001` — `NEEDS_REPAIR` |
| Completed repair | `TC-FF6-AUTHORITY-CLOSURE-001` — `PASS` |
| Exact next task | `TC-FF6-ORA-PROFILE-SURFACE-001` — `READY` |
| Capability inventory | 89 |
| Canonical obligations | 636 |
| Authority results | 15 `MATCH`; zero missing/mismatch/undeclared/legal-blocked |
| Certifications | 0 |
| Promotions | all six `UNASSESSED` |

The handover cannot embed the hash of the commit that will contain itself.
After this change set is committed and pushed, the receiving agent must fetch
`origin/main`, verify event 16 and the packet hashes, and use that remote
descendant as the source checkpoint.

## Read in order

1. [`AGENTS.md`](../../../AGENTS.md)
2. [`product-goal.yaml`](../../strategic/ff6/product-goal.yaml)
3. [`autonomous-six-python-production-execution-plan.md`](../../strategic/autonomous-six-python-production-execution-plan.md)
4. [`controller-state.yaml`](../../strategic/ff6/controller-state.yaml)
5. [`events.jsonl`](../../strategic/ff6/events.jsonl)
6. [`current-gaps.yaml`](../../strategic/ff6/current-gaps.yaml)
7. [`current-state.yaml`](../../strategic/ff6/current-state.yaml)
8. [`TC-FF6-PROGRAM-CAPABILITIES-001.md`](../../../taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md)
9. [`TC-FF6-ORA-PROFILE-SURFACE-001.md`](../../../taskcards/TC-FF6-ORA-PROFILE-SURFACE-001.md)
10. [`ACTIVE-WORK-CHECKPOINT.md`](ACTIVE-WORK-CHECKPOINT.md)
11. [`checkpoint.yaml`](checkpoint.yaml)
12. [`CURRENT-STATE-AND-ROOT-CAUSES.md`](CURRENT-STATE-AND-ROOT-CAUSES.md)
13. [`SHIFT-AND-RESUME-PROTOCOL.md`](SHIFT-AND-RESUME-PROTOCOL.md)
14. [`EXECUTION-RUNBOOK.md`](EXECUTION-RUNBOOK.md)
15. [`VALIDATION-AND-RELEASE.md`](VALIDATION-AND-RELEASE.md)
16. [`CLAUDE-START.md`](CLAUDE-START.md)
17. [`manifest.yaml`](manifest.yaml)

## What was actually achieved

The authority closure is production-grade machinery evidence, not a product
release:

- one canonical 15-source legal-aware lock;
- HTTPS/host/redirect/timeout/byte/ZIP/path/decompression protections;
- digest-before-placement and atomic concurrent publication;
- ignored content-addressed cache for external bytes;
- deterministic tracked internal product-requirement authorities;
- source researcher and strict ProductContract integration;
- complete generator/schema/research/source invalidation closure;
- clean offline replay: 15/15;
- clean online reconstruction from an empty CAS: 15/15 and 73,206,772 CAS
  bytes;
- six strict ProductContracts;
- 89 capabilities and 636 obligations;
- final capability aggregate
  `667cd4cb69773e6746ad46173b53de39c18ef44d39ef7db91c6337d8a3761a73`;
- final three-run digest
  `04114c84221edcdb00dae1097d75e55a7c1a6be75a074c9c0b8b07f0de5533a8`;
- 250 affected tests passed; one pre-existing CSV idempotency test is
  separately tracked and deselected because it mutates unrelated reports;
- Ruff, mypy, and Pyright 1.1.411 pass.

No product source was added in this task. No format was certified or promoted.

## What remains

The parent capability task is not complete. The deterministic compiler reports:

- OpenRaster: missing explicit 0.0.4/0.0.5 applicability and format-specific
  image/stack/group/layer/mask/compositing/rendering surface;
- IPYNB: explicit 4.0–4.4 applicability absent;
- NRRD: explicit NRRD0001–NRRD0004 applicability absent;
- XLIFF: explicit 2.0 applicability absent;
- UBL: the contract does not prove typed coverage for all 91 roots.

OpenRaster is selected first because `FF6-GAP-013` is the current
highest-severity blocking repair and OpenRaster has no product package at all.
The exact scope and exit criteria are in its taskcard. The later profile gaps
must remain visible and be scheduled; they are not implicitly deferred away.

## Mandatory resume preflight

```powershell
git fetch origin main
git status --short
git rev-parse HEAD
git rev-parse origin/main
python tools/evidence/check_current_state_consistency.py
python -m pytest tests/plan_control -q
python -m tools.supervisor.coordination --json status
```

Then independently validate all 16 FF6 events by:

1. parsing each JSONL record;
2. recomputing SHA-256 over canonical JSON with `event_hash` removed;
3. requiring `sequence` 1–16;
4. requiring each `previous_event_hash` to equal the preceding event hash;
5. requiring the controller head to equal event 16.

Do not run the generic Plan Control doctor as an FF6 chain validator. It uses
`previous_hash` and its own event schema. That integration mismatch is already
tracked in `FF6-GAP-011`.

Coordination may still report historical open conflicts unrelated to this
task. Preserve them. A new agent must register, claim the exact paths, compare
digests, and use governed takeover only for stale leases. Never release or
discard another agent’s work.

## Exact continuation

Execute only
[`TC-FF6-ORA-PROFILE-SURFACE-001.md`](../../../taskcards/TC-FF6-ORA-PROFILE-SURFACE-001.md).

Start with the three already locked OpenRaster authorities. Build a
source-located 0.0.3/0.0.4/0.0.5 delta matrix, repair SAL facts and evidence,
compile explicit format-specific capabilities and profile applicability, and
remove the compiler’s OpenRaster findings through evidence—not policy
suppression. Product source remains prohibited in this task.

## Provider shift rule

At every shift:

1. reach a bounded verified checkpoint;
2. append a close-intent or truthful WIP event;
3. update task, gaps, controller, and exact next task from evidence;
4. refresh this packet and its hashes;
5. stage explicit owned paths only;
6. run coordination precommit;
7. commit and push only GitLab `main`;
8. verify the remote commit;
9. release only the current agent’s leases and complete its session.

Never leave the next provider dependent on uncommitted changes, ignored proof,
conversation memory, a provider branch, or a request to continue.
