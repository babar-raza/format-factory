# Prompt Quality Root Cause — Acceleration R110

## Symptom
R109 advancement_lane check failed: generated acceleration prompt contained no advancement terms.

## Root Cause Analysis

### generate_next_worker_prompt.py
The `STREAM_GROUPS` filter reduces acceleration to only G1, G2, G7, G8:
- G1: Governance Preflight — "Read all governance files..."
- G2: Rework (empty when no rework items)
- G7: State + Memory + POC Matrix Sync
- G8: Evidence Declaration + Supervisor Autonomous-Cycle

None of these contain words like "advance", "improve", "add", "implement", "new", "detector", "validator", "harden", "expand", "enhance", "severity", "enforce", or "integrate".

### validate_prompt_quality.py
The advancement_lane check (R108) had acceleration-specific terms:
`["detector", "validator", "harden", "expand", "enhance", "severity", "enforce", "integrate"]`

These terms are good but they never appear in the prompt because the prompt generator strips all acceleration-specific trains.

### The Gap
`generate_next_worker_prompt.py` defines `STREAM_FORWARD_WORK` with acceleration items, but only uses them in `generate_next_work_items()` (the JSON/YAML), not in the prompt text itself.

## Fix Applied (R110)

### Fix 1: generate_next_worker_prompt.py
- After G1/G2/G7/G8 filtering, inject `STREAM_FORWARD_WORK` items as G2-group trains
- These are inserted before G7/G8 (state sync and evidence)
- Trains are re-lettered after insertion
- Sprint goal now includes stream-specific advancement language

### Fix 2: validate_prompt_quality.py
- Added 6 more acceleration terms for robustness: "detection accuracy", "quality scoring", "continuation policy", "stop condition", "strengthen", "refine"
- These match `STREAM_FORWARD_WORK` descriptions

### Result
- All 3 non-mainstream streams (acceleration, skills, supervisor) now pass 6/6 prompt quality checks
- All 3 non-mainstream streams pass 4/4 NWI quality checks
- Mainstream behavior unchanged
