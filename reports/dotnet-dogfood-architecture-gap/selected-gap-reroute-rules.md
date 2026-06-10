# Selected Gap Reroute Rules

## New Classification: GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED

**Status name:** `GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED`

**Definition:** A dogfood export gap in the .NET commercial track where the target format writer library
does not yet exist inside the format-factory .NET ecosystem. The gap cannot be closed by a governed
skill invocation alone because the downstream writer library must first be created as a separate
architecture sprint. Skill invocation is explicitly not allowed (`allowed_skill_invocation: false`).

**Score:** 40 in `ACTION_SCORE` (versus 95 for `GAP_DOGFOOD_EXTERNAL`). This lower score ensures
blocked gaps are ranked below all actionable gaps during sprint selection.

**Reclassification trigger:** `gap_id in BLOCKED_GAP_IDS` (evaluated after `gap_id` is computed
inside the `_gap()` function). Blocked gaps have `architecture_blocked: true` set in the payload.

## Implementation Status: IMPLEMENTED

py_compile and pytest both passed. Changes are live in `tools/supervisor/select_poc_gaps.py`.

## Changes Made

File: `tools/supervisor/select_poc_gaps.py`

**Change 1 — GAP_STATUSES set:** Added `"GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED"` as a
recognized status.

**Change 2 — ACTION_SCORE dict:** Added `"GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED": 40` entry
(score 40, versus 95 for the base `GAP_DOGFOOD_EXTERNAL`).

**Change 3 — BLOCKED_GAP_IDS constant:** Added a `frozenset` containing the four confirmed
architecture-blocked gap IDs:
- `commercial-net-fods-dogfood-status-fods-to-csv-dotnet`
- `commercial-net-fods-dogfood-status-fods-to-html-dotnet`
- `commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet`
- `commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet`

**Change 4 — Reclassification step in `_gap()`:** After `gap["gap_id"]` is assigned, a guard checks
`if gap["gap_id"] in BLOCKED_GAP_IDS` and overwrites `current_status`, `poc_impact_score`,
`priority_score`, and sets `architecture_blocked: True`. No other logic was restructured.

**py_compile (before modification):** PASS (exit 0)
**py_compile (after modification):** PASS (exit 0)
**pytest `-k "select_poc or select_gap"`:** 26 passed, 0 failed

## Blocked Gap Ledger

Path: `reports/dotnet-dogfood-architecture-gap/blocked-dogfood-gap-ledger.json`

Contains 4 entries, one per blocked gap, each with `classification`, `blocker_type`,
`blocked_by_library`, `candidate_architecture_sprint`, `allowed_skill_invocation: false`,
`future_decision_required: true`, and `evidence` back-reference.

## Actionable Alternatives

Path: `reports/dotnet-dogfood-architecture-gap/actionable-gap-replacement-candidates.json`

Contains top 5 non-blocked gaps from `selected-product-gaps.json` in priority order:
1. `foss-reduced-sylk-python-status-installed-workflow` (score 110, skill_allowed: true)
2. `foss-reduced-netpbm-blockers-1` (score 90, skill_allowed: true)
3. `foss-reduced-sylk-blockers-1` (score 90, skill_allowed: true)
4. `foss-reduced-zst-blockers-1` (score 90, skill_allowed: true)
5. `commercial-net-fods-blockers-1` (score 70, skill_allowed: false — supervisor escalation)

## Local Verdict: ACCEPT
