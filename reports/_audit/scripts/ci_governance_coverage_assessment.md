# CI Coverage Gap Assessment: Governance Validators
# TC-VNK-H-010 — Assessment Only (no ci.yml changes)
# Date: 2026-06-23

authoritative_plan: plans/secondary/vivid-napping-kurzweil-hardening-addendum.md
artifact_role: analysis_or_evidence_only
execution_authority: false

---

## Current CI Governance Coverage

From `.github/workflows/ci.yml`:
- **Line 45:** `python tools/test_runner.py --layer 3` — runs format tests
- **Line 63:** `python -c "from governance_validators import ..."` — import smoke test ONLY
- **No governance validator test suite execution** in CI

This means:
- V1-V63 validators are tested only via Python import (checks syntax, not behavior)
- Regressions in validator logic are invisible during PR review
- `source_structure_validator.py` runs only via autonomous_cycle (not CI)

---

## Timing Data

### Full governance test suite (MEASURED)
- **Command:** `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v --tb=short`
- **Total tests:** 109
- **Passed:** 108
- **Failed:** 1 (`TestRunAllValidators::test_governance_declaration_passes_all` — pre-existing)
- **Wall-clock time:** **616.34s (10 min 16 sec)**
- **Root cause of slowness:** `TestRunAllValidators` class exercises the full validator chain
  with file I/O. Individual unit tests are fast.

### Focused subset (V46/V57 integration tests)
- **Command:** `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -k "v46 or V46 or v57 or V57 or integration" --tb=short`
- **Result:** 4/4 pass in 0.26s (from prior convergence loop evidence)

### Unit tests only (excluding TestRunAllValidators)
- **Estimated:** ~104 tests in 3-5 minutes
- **Deselect:** `--deselect tests/supervisor/test_governance_validators.py::TestRunAllValidators`

### Pre-existing failures
- 1 test in `TestRunAllValidators` fails (down from earlier 5; test count grew from 64 to 109)
- Cataloged in `registry/known-failure-ledger.yaml`

---

## Assessment

### Option A: Add full governance test suite to CI
- **Time impact:** +10 minutes per PR (616s measured)
- **Verdict:** NOT RECOMMENDED — too slow for CI feedback loop
- **Reason:** TestRunAllValidators dominates. 1 pre-existing failure would cause CI red.

### Option B: Add unit tests excluding TestRunAllValidators (RECOMMENDED)
- **Time impact:** ~3-5 minutes per PR (104 tests, no slow integration path)
- **Coverage:** All individual validator tests including V46, V48, V57
- **Deselect:** `--deselect tests/supervisor/test_governance_validators.py::TestRunAllValidators`
- **Verdict:** RECOMMENDED — catches validator regressions with acceptable CI cost

### Option B2: Add focused subset only (alternative)
- **Time impact:** <5 seconds per PR
- **Coverage:** V46, V48, V57, canonical count only
- **Verdict:** ACCEPTABLE — minimal CI cost, covers newest validators only

### Option C: Keep as-is
- **Risk:** Governance regressions invisible in PRs
- **Mitigation:** Autonomous loop catches regressions within 1-2 sprint cycles
- **Verdict:** ACCEPTABLE if CI speed is paramount

---

## Proposed ci.yml Changes (Option B)

If approved, add to `governance-check` job after the existing smoke test step:

```yaml
      - name: Governance validator unit tests
        run: |
          pytest tests/supervisor/test_governance_validators.py -v \
            --deselect tests/supervisor/test_governance_validators.py::TestRunAllValidators \
            -q --timeout=300
```

This runs ~104 unit tests (est. 3-5 min), excluding the slow integration class.

Alternative (Option B2 — minimal):
```yaml
      - name: Governance validator focused tests
        run: |
          pytest tests/supervisor/test_governance_validators.py \
            -k "v46 or V46 or v48 or V48 or v57 or V57 or integration or canonical" \
            --tb=short -q
```

This runs only the newest validator tests (~0.3s).

---

## Recommendation

**GO with Option B** — add governance validator unit tests (excluding TestRunAllValidators)
to CI. ~104 tests, est. 3-5 minutes, zero known failures in this subset.
Implementation requires a separate taskcard (TC-VNK-H-010 is assessment only).
