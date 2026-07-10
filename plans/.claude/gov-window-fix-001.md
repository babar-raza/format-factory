# Plan: GOV-WINDOW-FIX-001 — Restore V105/V106 Detection Coverage After TC-PQLM-027
# Mission: governance-window-fix
# Created: 2026-07-10 (in-session from pilot comparison output)

---

## Mission Summary

TC-PQLM-027 (glowing-foraging-starlight sprint) added governed TODO comments before
validation guards in FodsDocumentDataAnnotations.cs, EditOps.cs, and SheetFeatures.cs.
These comments pushed dict-access patterns beyond the fixed detection windows of the
V105 (300-char) and V106 (400-char) governance validators, silently removing 4 methods
from governance tracking ("governance masking").

## Root Cause

- `governance_validators_ext3.py` V105 uses `content[start:start + 300]` (line 498).
- `governance_validators_ext3.py` V106 uses `content[start:start + 400]` (line 579).
- Windows are counted from the END of the method signature `)`.
- TODO comments placed before validation guards push dict access toward/past boundaries.
- When a match string (e.g., `.TryGetValue` = 30 chars) ENDS beyond the boundary,
  `re.search(pattern, content[start:start+N])` does not find it.

## Masked Methods (Evidence from Pilot Run)

| Method | Validator | Window | Dict access char (before) | Dict access char (after) | Status |
|--------|-----------|--------|--------------------------|--------------------------|--------|
| GetConditionalFormatRule | V105 | 300 | 175 (end=205, within) | 275 (end=305, OUTSIDE) | MASKED |
| GetDataValidationRule    | V105 | 300 | 175 (end=205, within) | 273 (end=303, OUTSIDE) | MASKED |
| SetRowHeight             | V106 | 400 | 380 (within)          | 441 (OUTSIDE)           | MASKED |
| SetSheetProtected        | V106 | 400 | 318 (within)          | 406 (OUTSIDE)           | MASKED |

## Mandatory Outcomes

1. V105 window extended from 300 → 500 (headroom: match ends at ~305, window now 500)
2. V106 window extended from 400 → 600 (headroom: match at ~441, window now 600)
3. GetConditionalFormatRule detected as KNOWN by V105 (no new FAIL)
4. GetDataValidationRule detected as KNOWN by V105 (no new FAIL)
5. SetRowHeight detected as KNOWN by V106 (no new FAIL)
6. SetSheetProtected detected as KNOWN by V106 (no new FAIL)
7. No new FAIL violations in V105 or V106 (new=0)
8. V101/V102/V103 unchanged (PASS/PASS/WARN)
9. 876 Python xcf tests pass
10. 4233 .NET FODS tests pass
11. Idempotent on rerun

## Scope

- Allowed: governance_validators_ext3.py window size literals only
- Forbidden: known_violations baseline changes, detection logic changes, product source changes

## Non-Goals

- Implementing XML-backed replacements for masked methods
- Changing the validator's detection patterns
- Addressing FODT/other format violations

## Taskcard Status Table

| TC-ID | Title | Status | Evidence |
|-------|-------|--------|----------|
| TC-GWF-001 | Extend V105 window 300→500 in governance_validators_ext3.py | CLOSED | commit 6bc5ad75, line 498→500 |
| TC-GWF-002 | Extend V106 window 400→600 in governance_validators_ext3.py | CLOSED | commit 6bc5ad75, line 579→600 |
| TC-GWF-003 | Verify 4 masked methods re-appear as KNOWN in full scan | CLOSED | TARGET KNOWN confirmed (56 V105, 34 V106, new=0) |
| TC-GWF-004 | Regression: 876+4233 tests pass, V101/V102/V103 unchanged | CLOSED | pilot run + idempotency rerun |

## Proof Matrix

| Requirement | Proof Level | Evidence |
|-------------|-------------|---------|
| V105 window 300→500 | L3: Integration | validator run, full detection check |
| V106 window 400→600 | L3: Integration | validator run, full detection check |
| GetConditionalFormatRule KNOWN | L3: Integration | TARGET KNOWN in 56-item V105 list |
| GetDataValidationRule KNOWN | L3: Integration | TARGET KNOWN in 56-item V105 list |
| SetRowHeight KNOWN | L3: Integration | TARGET KNOWN in 34-item V106 list |
| SetSheetProtected KNOWN | L3: Integration | TARGET KNOWN in 34-item V106 list |
| Zero new FAIL | L3: Integration | new=0 both validators |
| Tests pass | L3: Integration | 876+4233 PASS |
| Idempotent | L5: Repeatable | two consecutive runs identical |

## Lifecycle Audit Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-GWF-001 | CLOSED |
| TC-GWF-002 | CLOSED |
| TC-GWF-003 | CLOSED |
| TC-GWF-004 | CLOSED |


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-10T08:09:49.090214+00:00"
  locked_by: "033f6a1ae2f3"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
