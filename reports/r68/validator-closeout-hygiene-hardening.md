# R68 Train E — Validator Closeout-Hygiene Hardening

Sprint: FORMAT-FACTORY-R68-FINAL-CLOSEOUT-HYGIENE-LOCAL-RC-SEAL-MEGA-TRAIN-001
Date: 2026-05-27

## Defect Repaired (IV-R68-006)

**Gap:** `validate_evidence_bundle.py` did not check for incomplete-closeout tokens
(`[to be filled]`, `TBD`, `UNKNOWN (N —`) in final report files. A bundle built before
final reports were filled in would PASS validation silently.

## Change Applied

**File:** `tools/evidence/validate_evidence_bundle.py`

Added:
1. `CLOSEOUT_HYGIENE_TOKENS` list: 5 tokens that indicate incomplete closeout
2. `CLOSEOUT_HYGIENE_REPORT_FILES` frozenset: 4 final report filenames scanned
3. `check_closeout_hygiene_tokens(zf)` function: scans those files in the ZIP
4. Wired into the `no_pending` block (R68 Train E label)

### Tokens Checked
- `[to be filled]`
- `[to be filled at closeout]`
- `[commit sha to be filled]`
- `post-bundle authoritative count: tbd`
- `unknown (3 —`

### Files Scanned
- `final-independent-verification.md`
- `python-tests-summary.txt`
- `lane-ownership.md`
- `final-verdict.md`

## New Test Files

| File | Tests | Result |
|---|---|---|
| tests/evidence/test_r68_closeout_hygiene.py | 11 | 11 PASS |
| tests/evidence/test_r68_final_report_no_placeholders.py | 7 | 7 PASS |
| Total | 18 | 18 PASS |

## Proof

The R68 bundle will be validated with `--check-no-pending`. If any bundled R67 or R68
report contains `[to be filled]` or `TBD`, validation fails with:

```
R68: Closeout-hygiene token '[to be filled]' found in bundled file
'repo/reports/r67/final-independent-verification.md' — report was not filled
in before bundle build.
```

TRAIN_E_CLOSEOUT: COMPLETE
