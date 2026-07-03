# Sprint Plan — PGM Brightness Histogram Tests + Evidence Closeout

> **plan_path:** C:\Users\prora\.claude\plans\logical-cuddling-naur.md
> **reassessment_date:** 2026-07-03
> **reassessment_verdict:** PRIOR_PLAN_90%_DONE_BY_OTHER_SESSIONS

---

## A. Current-State Reassessment

HEAD: `f792be4d` (6 commits ahead of plan baseline `c9de1a9c`)

| Plan Item | Status | Evidence |
|-----------|--------|---------|
| TC-H-001: Delete stubs (gnumeric/dogfood/toml) | **DONE** | 26,888 tests collected, 0 errors |
| TC-P-001: pgm_brightness_histogram tests | **PARTIAL** | 2 weak tests exist in test_r374 (isinstance + len > 0 only); no value assertions |
| TC-CR-001..009: Consumer roundtrips (9 formats) | **DONE** | All 9 files exist at expected paths with real content (≥62 LOC each) |
| TC-NET-001: FodsDocument.Load(Stream) | **DONE** | FodsDocument.cs:139 |
| TC-NET-002: FodtDocument.Load(Stream) | **DONE** | FodtDocument.cs:146 |
| TC-NET-003/004/005: NetPBM .NET READMEs | **DONE** | Unified project has README.md at src/net/netpbm/ |
| TC-GOV-001..005: Evidence closeout | **NOT DONE** | No declaration for this sprint's work |

**What changed since plan was written:**
- Multiple sessions advanced the work: stubs deleted, consumer roundtrips created, .NET stream overloads added
- HEAD advanced by 6 commits

**Remaining genuine work:**
1. A proper `pgm_brightness_histogram` test file with exact-value assertions (function confirmed at `grayscale_image.py:525`, bins=4 default, no dedicated tests with value assertions)
2. Evidence declaration and supervisor closeout

---

## B. Context

**Why this is still needed:**
- `pgm_brightness_histogram(file_path, bins=4)` exists at [src/python/pgm/grayscale_image.py:525](src/python/pgm/grayscale_image.py)
- Current tests (`test_r374_pgm_analytics.py:355–362`) only assert `isinstance(result, list)` and `len(result) > 0` — these are type-guards, not behavioral proof
- No test verifies bin placement logic, sum==pixel_count, default bin count, or edge cases
- A dedicated test file provides the `test_delta >= +8` needed for a non-zero sprint and closes the behavioral gap

---

## C. Execution Plan (Revised — Only Remaining Work)

### TC-FINAL-001: Create pgm_brightness_histogram Test File

**Target:** `tests/python/pgm/test_r259_pgm_brightness_histogram.py` (NEW)
**Precondition:** Verify test_r259 filename is unused (`ls tests/python/pgm/test_r259*` → no match)

**CRITICAL — Verified function behavior (bins=4 default):**
- `grayscale_image.py:525`: `def pgm_brightness_histogram(file_path, bins=4) -> list[int]`
- Algorithm: `bin_width = (maxval+1)/bins; idx = min(int(p/bin_width), bins-1)`
- 2x2-gradient.pgm pixels [0,85,170,255], maxval=255, bins=4:
  - pixel 0 → idx=0, pixel 85 → idx=1, pixel 170 → idx=2, pixel 255 → idx=3
  - Result: `[1, 1, 1, 1]`
- 1x1-white.pgm pixel=255, maxval=255, bins=4:
  - Result: `[0, 0, 0, 1]`

**Test file content:**
```python
"""Tests for pgm_brightness_histogram — behavioral assertions.

grayscale_image.py:525 — def pgm_brightness_histogram(file_path, bins=4)
Closes: GAP-PGM-FOSS-PGM_BRIGHT_HI-001
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm.grayscale_image import pgm_brightness_histogram

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")
_2X2_GRADIENT = str(_DIR / "2x2-gradient.pgm")
_3X1_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmBrightnessHistogram:
    def test_return_type(self):
        assert isinstance(pgm_brightness_histogram(_1X1_WHITE), list)
        assert all(isinstance(x, int) for x in pgm_brightness_histogram(_1X1_WHITE))

    def test_default_bins_is_4(self):
        assert len(pgm_brightness_histogram(_1X1_WHITE)) == 4

    def test_1x1_white_last_bin_gets_pixel(self):
        result = pgm_brightness_histogram(_1X1_WHITE)
        assert result == [0, 0, 0, 1]

    def test_2x2_gradient_uniform_distribution(self):
        # pixels [0,85,170,255], bins=4 → each lands in its own bin
        assert pgm_brightness_histogram(_2X2_GRADIENT) == [1, 1, 1, 1]

    def test_sum_equals_pixel_count(self):
        assert sum(pgm_brightness_histogram(_2X2_GRADIENT)) == 4

    def test_custom_bins_256(self):
        result = pgm_brightness_histogram(_2X2_GRADIENT, bins=256)
        assert len(result) == 256
        assert sum(result) == 4
        assert result[0] == 1
        assert result[85] == 1
        assert result[170] == 1
        assert result[255] == 1

    def test_3x1_ramp_sum_equals_3(self):
        assert sum(pgm_brightness_histogram(_3X1_RAMP)) == 3

    def test_consistent_across_calls(self):
        assert pgm_brightness_histogram(_1X1_WHITE) == pgm_brightness_histogram(_1X1_WHITE)
```

**Acceptance:** `.venv/Scripts/pytest tests/python/pgm/test_r259_pgm_brightness_histogram.py -v` → 8 passed

**Rollback:** `del tests/python/pgm/test_r259_pgm_brightness_histogram.py`

---

### TC-FINAL-002: Full PGM Regression

Command: `.venv/Scripts/pytest tests/python/pgm/ -q`
Expected: All existing tests pass + 8 new tests pass, 0 failures, 0 errors.

---

### TC-FINAL-003: Evidence Declaration + Supervisor Closeout

**run_id:** `pgm-histogram-tests-20260703-{git_short_hash}`

Steps (in order):

1. Create `.local/evidences/{run_id}/` directory
2. Capture test log: `pytest test_r259_pgm_brightness_histogram.py -v > .local/evidences/{run_id}/histogram-test-log.txt`
3. Write `.local/evidences/{run_id}/evidence-declaration.yaml` with:
   - `run_id`, `sprint_id`, `start_time`, `end_time`
   - `git_head_start: f792be4d`, `git_head_end: {current}`
   - One work item: `TEST-PGM-BRIGHTNESS-HIST-001` (type: PRODUCT_TEST, status: completed)
   - `evidence_paths: ["tests/python/pgm/test_r259_pgm_brightness_histogram.py", ".local/evidences/{run_id}/histogram-test-log.txt"]`
   - `worker_self_verdict: ACCEPTED`, `worker_self_grade: A`
4. Validate: `python tools/supervisor/sprint_executor_validate.py .local/evidences/{run_id}/evidence-declaration.yaml --repair`
5. Supervisor: `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/{run_id}/evidence-declaration.yaml`
   - Exit 0 or 3: proceed; exit 1: fix and retry; exit 9: log and proceed
6. Check continuation: `python tools/supervisor/check_continuation.py`
7. Plan terminal: `python tools/supervisor/write_plan_lock.py --plan-path C:/Users/prora/.claude/plans/logical-cuddling-naur.md --terminal`

---

## D. DAG

```
TC-FINAL-001 (create test file)
      |
TC-FINAL-002 (run regression)
      |
TC-FINAL-003 (evidence + closeout)
      |
  [TERMINAL — POST_PLAN_TERMINAL STOP]
```

---

## Key File References

| File | Status | Role |
|------|--------|------|
| [src/python/pgm/grayscale_image.py:525](src/python/pgm/grayscale_image.py) | EXISTS | pgm_brightness_histogram(file_path, bins=4) |
| [tests/python/pgm/test_r259_pgm_brightness_histogram.py](tests/python/pgm/test_r259_pgm_brightness_histogram.py) | MISSING → CREATE | 8 behavioral tests |
| [samples/by-format/pgm/valid/2x2-gradient.pgm](samples/by-format/pgm/valid/2x2-gradient.pgm) | EXISTS | pixels [0,85,170,255] maxval=255 |
| [samples/by-format/pgm/valid/1x1-white.pgm](samples/by-format/pgm/valid/1x1-white.pgm) | EXISTS | single pixel=255 |
| [samples/by-format/pgm/valid/3x1-ramp.pgm](samples/by-format/pgm/valid/3x1-ramp.pgm) | EXISTS | 3 pixels |

---

## Execution Handoff

1. Write plan lock: `python tools/supervisor/write_plan_lock.py --plan-path C:/Users/prora/.claude/plans/logical-cuddling-naur.md`
2. Execute TC-FINAL-001 → TC-FINAL-002 → TC-FINAL-003 in order
3. After TC-FINAL-003 complete: `write_plan_lock.py --terminal` then STOP (POST_PLAN_TERMINAL)
4. Do NOT switch to next-sprint.md while this plan is active


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-03T13:16:12.446187+00:00"
  locked_by: "af3d4a5638a5"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
