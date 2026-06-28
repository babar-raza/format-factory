# Certification Methodology Validation Report

```yaml
authoritative_plan: plans/.claude/crispy-jingling-snail.md
mission_id: CERT-EXHAUST-20260628
taskcard: TC-CERT-W1-METH-001
status: CLOSED
```

## Pilot Comparison Matrix

| Dimension | FODS | CSV | ZST |
|-----------|------|-----|-----|
| Python APIs | 103 | 97 | 101 |
| .NET APIs | 481 | 27 | 27 |
| Material Stubs | 4 | 11 | 2 |
| Exception Classes | 5 | 5 | 9 |
| Raise Sites | 14 | 7 | 29 |
| Uncovered Exceptions | 0 | 0 | 5 |
| QName Count | 12 | 3 | 3 |
| QName PASS | 12/12 | 3/3 | 3/3 |
| Oracle Status | PASS (8/8) | PASS (5/5) | PASS (6/6) |

## Tool Reliability Assessment

### inventory_extractor.py
- **Reliability:** HIGH. Correctly inventoried all 20 Python + 10 .NET formats.
- **Issue found:** Dynamic `__all__` computation (FODS uses runtime filtering) handled correctly.
- **Generalization verdict:** READY for portfolio rollout.

### stub_detector.py
- **Reliability:** MEDIUM → HIGH after fix.
- **Issue found:** Scanned `build/` directories (deeply nested artifacts), inflating findings 4x.
  Fixed by adding `build/` and `.egg-info/` to skip list.
- **Issue found:** `classification` field was absent; only `classification_note` provided.
  The `severity` field (`material` / `advisory`) serves the classification purpose adequately.
- **Generalization verdict:** READY after fix applied.

### exception_coverage_checker.py
- **Reliability:** MEDIUM → HIGH after fix.
- **Issue found:** Same `build/` directory scanning issue as stub_detector. Fixed.
- **Issue found:** Without `--test-path`, all exceptions show "uncovered." Test path must be
  provided explicitly. CLI should be documented.
- **ZST note:** 5 uncovered exceptions (ZstDecompressError, ZstDecompressionError,
  ZstFileNotFoundError, ZstInvalidFrameError, ZstOutputLimitExceeded) — these need test coverage
  or classification as intentionally untested internal exceptions.
- **Generalization verdict:** READY after fix applied.

### Oracle executor (execute_oracle.py)
- **Reliability:** HIGH. All three pilots pass with no issues.
- **FODS note:** PASS_WITH_SCHEMA_WARNING — schema validation warning is informational, not blocking.
- **ZST note:** Must use `.venv/Scripts/python` for zstandard package.
- **Generalization verdict:** Already running for all 20 formats (73/73 PASS).

### QName traceability
- **Reliability:** HIGH. All qnames map to real files at HEAD.
- **Generalization verdict:** READY. All 21 format registries follow same structure.

## Material Findings Summary

### Stubs requiring follow-up (17 total across pilots)
- **FODS (4):** Analytics stubs in spreadsheet_document.py and spreadsheet_model_document.py
- **CSV (11):** Analytics stubs in csv_analytics.py and tabular_document.py
- **ZST (2):** `decompress_bytes` and `get_frame_info` stubs in zst_codec.py

### Uncovered Exceptions (5 total, ZST only)
- ZstDecompressError, ZstDecompressionError, ZstFileNotFoundError, ZstInvalidFrameError, ZstOutputLimitExceeded

## Tool Fixes Applied Before Portfolio Rollout

1. `stub_detector.py` line 110: Added `build/` and `.egg-info/` to skip_dirs
2. `exception_coverage_checker.py` line 52: Same build directory filtering fix

## Generalization Verdict

All 5 certification tools produce consistent, comparable, machine-readable output across
three architecturally distinct format types (complex XML, simple text, binary compression).
The tool suite is **READY FOR PORTFOLIO ROLLOUT** with the fixes documented above.
