# R110 Anti-Skip False Negative Analysis

## Issue 1: Why evidence_quality_score remained 0.0

### Observed
- evidence_quality_score: 0.0 (in grade_declared_work.py output)
- All 18 items graded ACCEPTED_WITH_LIMITATIONS

### Root Cause
The grading function in `grade_declared_work.py:148-175` requires `has_concrete_proof` to be True
for ACCEPTED_VERIFIED. This requires at least one of:
1. `tests_with_content` non-empty
2. `criteria_verified` True
3. `has_valid_transcript` True

None of these fired because:

**tests_with_content:** The inspector (`inspect_declared_evidence.py:146-235`) populates
`tests_with_content` from `tests_supporting` / `test_references`. R110 declaration had NO
`tests_supporting` field — only `evidence_paths` containing test file paths.

The fallback at line 223:
```python
if not tests_with_content and not tests_empty_or_stub and test_summaries:
```
requires `test_summaries` to be truthy. But `test_summaries` is only populated from non-file-path
entries in `tests`. Since `tests=[]` (no `tests_supporting` field), `test_summaries=[]` (falsy).
The fallback never fires.

**criteria_verified:** The acceptance criteria patterns are checked against the first 3 evidence_paths.
For API items, these are: test file, source file, skill transcript. None contain the pattern "PASS"
or quoted strings from the criteria. The raw log (which does contain pass counts) is at position 4-5.

**has_valid_transcript:** Transcript validation via `check_transcript_in_evidence()` looks for
JSON transcripts. R110 skill transcripts are Markdown files, so JSON parsing fails silently.

### Fix Required
In `inspect_declared_evidence.py:223`, change:
```python
if not tests_with_content and not tests_empty_or_stub and test_summaries:
```
to:
```python
if not tests_with_content and not tests_empty_or_stub:
```
This removes the `test_summaries` guard so evidence_paths are always scanned for test files
when no explicit test references exist.

Additionally, increase the evidence_paths scan limit from 3 to all paths in the criteria verification.

## Issue 2: Lane Ledger Detection

### Observed
The anti-skip checker may have reported missing_lane_ledger.

### Analysis
The lane-execution-ledger.json exists at `reports/mainstream-r110/lane-execution-ledger.json`.
The anti-skip checker in `autonomous_cycle.py:193` resolves the evidence_root from the declaration:
```python
sample_outputs_dir = evidence_root / "sample-outputs"
```
where `evidence_root = .local/evidences/mainstream-r110/`.

The lane ledger is NOT under `.local/evidences/mainstream-r110/` — it is under `reports/mainstream-r110/`.
The anti-skip checker looks for it under the evidence_root, not under the reports directory.

### Fix Required
Anti-skip checker should also scan `reports/<sprint>/` for lane-execution-ledger.json,
or the evidence declaration should include the lane ledger path explicitly.

## Issue 3: Sample Outputs Detection

### Observed
The anti-skip checker may have reported missing_sample_outputs.

### Analysis
Same path mismatch as Issue 2. Sample outputs are at `reports/mainstream-r110/sample-outputs/`,
not under `.local/evidences/mainstream-r110/sample-outputs/`.

### Fix Required
Same as Issue 2 — anti-skip should search both evidence_root and reports directory.

## Summary

| Issue | Component | Root Cause | Fix Owner |
|-------|-----------|-----------|-----------|
| evidence_quality_score=0.0 | inspect_declared_evidence.py:223 | test_summaries guard prevents fallback when tests_supporting absent | Supervisor |
| criteria not verified | inspect_declared_evidence.py:210 | Only checks first 3 evidence_paths, raw log at position 4+ | Supervisor |
| transcripts not recognized | transcript validator | Expects JSON, R110 transcripts are Markdown | Supervisor |
| lane ledger not found | anti-skip checker | Searches evidence_root, not reports/ directory | Acceleration |
| sample outputs not found | anti-skip checker | Searches evidence_root, not reports/ directory | Acceleration |
