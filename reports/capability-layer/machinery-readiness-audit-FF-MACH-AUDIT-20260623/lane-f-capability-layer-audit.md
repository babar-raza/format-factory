# Lane F — Capability Layer Audit
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-F | **Requirement:** REQ-LANE-F

## 1. RC-2 Confirmation — capability_compiler.py Analysis

### capability_compiler.py (514 LOC, 9 phases)
- **Location:** tools/supervisor/capability_compiler.py
- **Phases implemented:** 9 (SAL reading, validation, scoring, feature IR generation, taskcard generation, test matrix, evidence matrix, gate projection, summary)
- **Output files written:** feature IRs, taskcards, test/evidence matrices, gate projections
- **Does NOT write:** selected-product-gaps.json

### RC-2 CONFIRMED — But Root Cause Is More Nuanced
The original analysis stated "capability_compiler.py has no output path." This is PARTIALLY correct:
- capability_compiler.py DOES write many outputs (feature IRs, gate projections, etc.)
- capability_compiler.py does NOT write to selected-product-gaps.json
- **The actual writer** of selected-product-gaps.json is `tools/supervisor/select_poc_gaps.py` (lines 476-514)
- select_poc_gaps.py sources from `poc-targets.yaml`, NOT from gap-ledger priority scoring
- selected-product-gaps.json is ALWAYS EMPTY (selected_gap_count: 0)

### The Bridge Gap
```
gap-ledger.json (938 gaps) → capability_compiler.py (scores, generates IRs) → [NO BRIDGE] → selected-product-gaps.json (0 selected)
                                                                                    ↑
                                                           select_poc_gaps.py reads poc-targets.yaml (static POC matrix) → still 0 selected
```

The fix requires connecting capability_compiler's gap scoring to selected-product-gaps.json, either by:
1. Adding write_selected_gaps() to capability_compiler.py (plan Option A)
2. Modifying select_poc_gaps.py to use gap-ledger scoring instead of poc-targets.yaml

## 2. Gap Ledger Statistics

| Metric | Value |
|--------|-------|
| Total gaps | 938 |
| Open | 99 |
| Closed | 838 |
| Not yet parsed | 1 |

### Priority Distribution
| Priority | Count |
|----------|-------|
| P0 | 5 |
| P1 | 9 |
| P2 | 913 |
| P3 | 11 |

### Open Gaps by Format (top 5)
| Format | Open Gaps |
|--------|-----------|
| ABW | 39 |
| NDJSON | 19 |
| FODT | 9 |
| ZST | 6 |
| FODG | 5 |

## 3. selected-product-gaps.json Status
- **File:** .local/supervisor/selected-product-gaps.json
- **Content:** `selected_gap_count: 0` (EMPTY)
- **RC-1 CONFIRMED:** Work queue degenerates to advisory templates because no gaps are selected

## 4. Key Finding — select_poc_gaps.py
The existence of select_poc_gaps.py (discovered during investigation) changes the repair design:
- This tool ALREADY has the schema and write logic for selected-product-gaps.json
- The fix should augment its data source (add gap-ledger scoring) rather than creating a parallel writer in capability_compiler.py
- See capability-compiler-completion-design.md for updated design
