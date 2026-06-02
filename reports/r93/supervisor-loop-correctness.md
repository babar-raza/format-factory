---
sprint: R93
generated_by: r93-worker
train: F
---

# Autonomous Supervisor Loop Correctness (Train F)

Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

## Problem (D92-01 root cause)

`supervisor_loop.py autonomous-cycle` correctly called `autonomous_cycle.py` which
wrote a valid `evidence-review.json` via `bridge_to_legacy_format`. But subsequently,
the legacy `validate_evidence_for_supervisor.py` was invoked (via another path), treating
the `declaration-review-package.zip` as an evidence bundle and failing, which overwrote
the correctly-bridged `evidence-review.json`.

## Fix Applied

File: `tools/supervisor/supervisor_loop.py` — `cmd_autonomous_cycle()`

### Change 1: Added explicit D92-01 prevention comment

Added docstring explicitly stating that `cmd_autonomous_cycle` MUST NOT call
`cmd_review()` (which calls legacy bundle-validator). The bundle-validator
treats declaration-review-package.zip as a bundle and overwrites evidence-review.json.

### Change 2: Context-pack rebuild before packet generation

Added a call to `build_context_pack.py` before `generate_supervisor_packet.py`
so that the context-pack has fresh data for the enrichment logic (Train C fix).

This ensures that if evidence-review.json is stale/corrupted in a future run,
the context-pack has the authoritative current state.

## Loop Correctness Verification

Correct sequence for `autonomous-cycle --declaration <path>`:
1. `autonomous_cycle.py` → validate → inspect → grade → bridge_to_legacy_format → write continuation-signal
2. `build_context_pack.py` → update .supervisor/context-pack.yaml with current state
3. `generate_supervisor_packet.py` → read evidence-review.json (enriched from context-pack if stale) → write session-resume.md, approval-gates.md, next-sprint.md

**NEVER in this sequence:** `validate_evidence_for_supervisor.py` (bundle-validator).
The bundle-validator is LEGACY-ONLY and should not run in declaration-mode pipeline.

## Remaining Risk

If a user accidentally runs `supervisor_loop.py run-on-latest` after a declaration-based
sprint, it will discover the declaration-review-package.zip and run the bundle-validator
on it, re-creating the D92-01 corruption. This is mitigated by:
1. The Train C fix enriching generate_supervisor_packet.py from context-pack
2. The `run-on-latest` command printing a WARNING about being legacy

A future hardening would add a `.local/supervisor/mode.json` file that marks the
pipeline as "declaration-mode", and `run-on-latest` would refuse to run if in
declaration-mode.

## Status: LOOP CORRECTNESS HARDENED — D92-01 MITIGATED
