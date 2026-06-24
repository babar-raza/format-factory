# Capability Compiler Completion Design
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-F | **Requirement:** REQ-LANE-F

## Current State

### capability_compiler.py (514 LOC)
- 9 phases implemented: SAL reading → validation → scoring → feature IRs → taskcards → test matrix → evidence matrix → gate projection → summary
- Outputs feature IRs, taskcards, test/evidence matrices, gate projections
- Does NOT output selected-product-gaps.json

### select_poc_gaps.py (514 LOC)
- ACTUAL writer of selected-product-gaps.json (lines 476-514)
- Sources from poc-targets.yaml (static POC matrix)
- Currently produces selected_gap_count: 0

## Design: write_selected_gaps()

### Option A — Add to capability_compiler.py (original plan)
```python
def write_selected_gaps(gaps: list, output_path: str) -> None:
    """Select top gaps from gap-ledger based on priority scoring.

    Selection rules:
    - status=open only
    - Sort by priority (P0→0, P1→10, P2→20, P3→30) + impact adjustments
    - Take top 5
    - Max 2 per format
    - blocks_poc=true or blocks_readiness=true get priority boost (-10)

    Output schema matches selected-product-gaps.json:
    {
        "selected_gap_count": int,
        "selected_gaps": [
            {"gap_id": str, "format": str, "priority": str, "spec_facts": list, "status": str}
        ],
        "streams": {"mainstream": int}
    }
    """
```

### Option B — Augment select_poc_gaps.py (discovered alternative)
Modify select_poc_gaps.py to read gap-ledger.json as secondary source alongside poc-targets.yaml. This preserves existing schema and write logic.

### Recommended: Option A (per plan)
Rationale: capability_compiler.py already has gap scoring logic. Adding the output writer there is minimal and keeps the compilation pipeline self-contained. select_poc_gaps.py can continue to exist for POC-specific selection.

### Integration Point
After capability_compiler.py is enhanced:
1. autonomous_task_generator.py calls capability_compiler with --output flag
2. If selected-product-gaps.json is non-empty, uses gap IDs as priority filter
3. Fallback: if compiler fails or produces 0 gaps, falls back to direct gap-ledger reading

### CLI Addition
```
python tools/supervisor/capability_compiler.py --output .local/supervisor/selected-product-gaps.json
```
