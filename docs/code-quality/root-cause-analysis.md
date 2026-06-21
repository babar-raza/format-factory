# Root Cause Analysis — SRC Governance Machinery Bypass
**Sprint:** SRC Governance Healing (eventual-painting-torvalds)
**Date:** 2026-06-17
**Status:** Source-confirmed

---

## Summary

The Format Factory governance machinery (source_structure_validator.py, governance_validators.py,
tests/test_source_structure.py) is **correctly designed and wired**. Every component that should
block monolith growth does block it — when it sees the right data. The bypass is upstream: a
sprint closeout script updates the data the machinery reads before the machinery reads it.

---

## RCA-1 (CRITICAL): CLAUDE.md Step 0 Overwrites Baseline Before Validators Run

**Location:** CLAUDE.md lines 126–130 (now fixed by TC-MACH-006)
**Severity:** CRITICAL — primary root cause of all governance bypasses

**Mechanism:**
The Sprint Closeout Step 0 one-liner iterated all `known_violations` entries in
`registry/source-structure-baseline.json` and updated `loc` and `functions` to match the
CURRENT state of every Python file. The script ran as Step 0 of sprint closeout, before
`autonomous-cycle` (Step 2) which calls `run_all_governance_validators()`.

By the time `validate_monolith_detection()` checked `current_loc > baseline_loc`, the
baseline_loc WAS the current_loc. The validator's `worsened_violations` list was always empty.

**Exact script (now replaced):**
```python
python -c "import json,ast;from pathlib import Path;bp=Path('registry/source-structure-baseline.json');b=json.loads(bp.read_text());k=b['known_violations'];[exec('entry[\"loc\"]=sum(1 for _ in Path(rel).open());tree=ast.parse(Path(rel).read_text());entry[\"functions\"]=sum(1 for n in ast.iter_child_nodes(tree) if isinstance(n,ast.FunctionDef))') for rel,entry in k.items() if Path(rel).is_file() and rel.endswith('.py')];bp.write_text(json.dumps(b,indent=2)+chr(10))"
```

**What it did:** For every file in `known_violations`, overwrote `loc` = current line count.
**Effect:** `baseline_loc` always equals `current_loc` → `current_loc > baseline_loc` is never True.
**Evidence:** FODG grew 3,476→3,920 LOC; XCF grew 3,101→3,610 LOC; ZST grew 3,472→3,873 LOC — all on 2026-06-17, all in a single session, all without triggering any governance block.

**What was NOT broken:** The validator logic is correct. The blocking path exists. It was simply never reached because the input data was always synchronized to avoid triggering it.

**Fix (TC-MACH-006, implemented):** Replaced Step 0 script with a new-violations-only detector that skips all files already in `known_violations`. Existing violations have frozen `baseline_loc_cap` ceilings that the new script never touches.

---

## RCA-2 (HIGH): No Write-Once Ceiling in Baseline JSON

**Location:** registry/source-structure-baseline.json
**Severity:** HIGH — defense-in-depth gap; allows future bypass if RCA-1 recurs

**Mechanism:**
The baseline JSON has only a mutable `loc` field per violation entry. Even with RCA-1 fixed,
any script or manual edit that sets `loc = current_loc` defeats the regression check.
There is no immutable `baseline_loc_cap` field that records the ceiling at the time of
grandfathering.

**Fix (TC-MACH-001, pending):** Add `baseline_loc_cap` and `baseline_functions_cap` fields
to every known_violations entry. These are set once (to current `loc`/`functions` values)
and must never be increased. The validator (after TC-MACH-002) and regression tests (after
TC-MACH-005) compare against `baseline_loc_cap`, not `loc`.

---

## RCA-3 (HIGH): No Pre-Commit Architecture Gate

**Location:** .pre-commit-config.yaml (16 lines)
**Severity:** HIGH — allows monolith growth to reach HEAD before any check runs

**Mechanism:**
The pre-commit configuration runs only Ruff and basic file checks. No architecture
validator runs before a commit is created. Violations exist in git history before the
CI pipeline (which runs post-commit) can detect them.

**Note:** This is less critical than RCA-1/RCA-2 because CI does run the architecture
validators. However, pre-commit feedback is faster and prevents violations from entering
the commit history at all.

**Fix (TC-MACH-004, pending):** Add a local pre-commit hook calling
`python tools/validators/source_structure_validator.py --check-baseline-growth`
that runs only when `src/python/` or `src/net/` files are staged.

---

## RCA-4 (MEDIUM): Validator CLI Lacks Targeted Growth-Check Flag

**Location:** tools/validators/source_structure_validator.py lines 529+ (main())
**Severity:** MEDIUM — makes pre-commit integration harder

**Mechanism:**
The validator CLI only accepts `--repo-root` and `--json`. No `--check-baseline-growth`
flag exists for a targeted "did any violation grow beyond its cap?" check. The full scan
is heavier than needed for pre-commit.

**Fix (TC-MACH-007, pending):** Add `--check-baseline-growth` flag that runs `run_full_scan()`
and exits 1 if `worsened_violations` is non-empty.

---

## RCA-5 (MEDIUM): Existing Regression Tests Compare Against Mutable `loc`

**Location:** tests/test_source_structure.py, TestMonolithBaselineNoRegression
**Severity:** MEDIUM — tests are correct in design but compare against the wrong field

**Mechanism:**
`test_no_loc_regression()` compares current file LOC against `bl["loc"]` from baseline JSON.
After RCA-1 (Step 0) runs and updates `bl["loc"]` to current_loc, the comparison is always
equal → test passes even when the file has grown.

With RCA-1 fixed (TC-MACH-006), the tests will work correctly in practice. However, after
TC-MACH-001 adds `baseline_loc_cap`, the tests should compare against the cap (the
immutable ceiling) rather than the mutable `loc` for defense in depth.

**Fix (TC-MACH-005, pending):** Update comparison from `bl["loc"]` to
`bl.get("baseline_loc_cap", bl["loc"])` in both `test_no_loc_regression()` and
`test_no_function_count_regression()`. Add `test_baseline_loc_cap_exists()` to verify
all entries have the cap field.

---

## What Works Correctly (Do Not Modify)

| Component | Status | Evidence |
|---|---|---|
| `validate_monolith_detection()` in governance_validators.py | Correctly sets `blocks_sprint: True` on FAIL | Line 2466 (source-confirmed) |
| `run_all_governance_validators()` in governance_validators.py | Correctly includes monolith detection as blocking | Lines 2748–2828 (source-confirmed) |
| `run_full_scan()` in source_structure_validator.py | Correctly tracks worsened_violations and sets blocks_sprint | Lines 445–481 (source-confirmed) |
| `TestMonolithBaselineNoRegression` in test_source_structure.py | Correct test structure; just uses wrong comparison field | Lines 138–177 |
| 7-layer test organization | Layer 0 structural tests run in every CI fast-test pass | .github/workflows/ci.yml |
| Blocking logic: `blocks_sprint = any(r.get("blocks_sprint") for r in results if r["result"] == "FAIL")` | Correct aggregation | governance_validators.py line 2815 |

---

## Causal Chain

```
Product deepening sprint adds 50 analytics functions to fodg_codec.py
  → CLAUDE.md Step 0 (best-effort, runs first) updates known_violations["fodg_codec.py"]["loc"] = 3920
  → autonomous-cycle runs (Step 2)
  → validate_monolith_detection() reads baseline: baseline_loc = 3920
  → checks: current_loc (3920) > baseline_loc (3920) → False
  → worsened_violations = []
  → blocks_sprint = False
  → sprint ACCEPTED despite file growing by 444 LOC
  → Next sprint: same pattern
```

**After TC-MACH-006 + TC-MACH-001 + TC-MACH-002:**
```
Product deepening sprint adds 50 analytics functions to fodg_codec.py
  → CLAUDE.md Step 0 runs: sees fodg_codec.py is already in known_violations → SKIPS it
  → known_violations["fodg_codec.py"] unchanged; baseline_loc_cap = 3920
  → autonomous-cycle runs (Step 2)
  → validate_monolith_detection() reads baseline: baseline_loc_cap = 3920
  → checks: current_loc (3970) > baseline_loc_cap (3920) → True
  → worsened_violations = ["fodg_codec.py: 3970 > cap 3920"]
  → blocks_sprint = True
  → sprint REJECTED — monolith growth detected
```
