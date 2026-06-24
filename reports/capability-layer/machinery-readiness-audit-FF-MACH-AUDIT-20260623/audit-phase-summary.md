# Audit Phase Summary — FF-MACH-AUDIT-20260623
**Plan:** sorted-purring-stardust | **Taskcard:** TC-EVI-001-03

## Investigation Findings Summary

### Root Causes Confirmed
| RC | Status | Summary |
|----|--------|---------|
| RC-1 | CONFIRMED | selected-product-gaps.json is always empty (selected_gap_count: 0) |
| RC-2 | CONFIRMED (refined) | capability_compiler.py has no bridge to selected-product-gaps.json; select_poc_gaps.py is the actual writer but sources from static poc-targets.yaml |
| RC-3 | CONFIRMED | Lane enforcement runs at Step 2e (post-grading), not Step 1b (pre-grading) |
| RC-4 | PARTIALLY CONFIRMED | V49 EXISTS (WARN-only for spec_qname structure); gap is V50 (spec_fact_refs density) |
| RC-5 | CONFIRMED | NDJSON 88%, CSV 88%, TSV 89% analytics exports |
| RC-6 | CONFIRMED | 17 Python + 12 .NET architecture_only stubs untracked in gap-ledger |
| RC-7 | CONFIRMED | SAL staleness is warn-only; also found CLI mismatch (--all vs scan subcommand) |
| RC-8 | CONFIRMED | FM-0013: 283 occurrences, escalated=true, no action handler |

### Key Corrections to Original Analysis
- Validator count: 56 (not 48)
- Gap ledger: 938 gaps (not 926)
- capability_compiler.py: 514 LOC with 9 phases (not 150+ LOC)
- V49 already exists — rescoped TC-MACH-VAL-001 to V50

### Phase 6 Repair Sequence (Ready to Execute)
1. TC-MACH-CAP-001 — write_selected_gaps() in capability_compiler.py
2. TC-MACH-CAP-002 — Wire gap selection into task generator
3. TC-MACH-VAL-001 — V50 spec_fact_refs density validator
4. TC-MACH-LANE-001 — Preventive lane guard at Step 1b
5. TC-MACH-SAL-001 — SAL staleness escalation
6. TC-MACH-BACK-001 — Backfill facility skeleton
7. TC-MACH-SRC-001 — V51 public API surface governance
8. TC-MACH-FM-001 — Failure memory escalation thresholds
9. TC-MACH-CAP-003 — Track architecture_only stubs in gap-ledger

All 9 repairs have detailed designs from investigation lanes. Proceeding to implementation.
