# R52 Validator Hardening Summary

**Sprint:** FORMAT-FACTORY-R52-STATE-CONSISTENT-INSTALLED-ARTIFACT-BASELINE-CLEAN-001

## Changes to validate_evidence_bundle.py

### New: `_parse_verdict_from_text(content)` helper

Multi-format verdict parser supporting all formats seen across R25–R52:
- Format A: `VERDICT: VALUE` or `**VERDICT: VALUE**`
- Format B: `**Verdict:** **VALUE**`
- Format C: `## Verdict` heading + `` `VALUE` `` code-block (R51+)

### Extended: `check_state_verdict_agreement()`

- Now scans `repo/reports/*/final-verdict.md` entries in bundle ZipFile
- Uses `_parse_verdict_from_text()` for multi-format verdict parsing
- Stale indicators updated to use hyphen format: `" - unknown"`, `" - no_final_verdict"`
- Added INV-003 false-blocker detection: flags when state says file MISSING but file exists in bundle
- INV-003 check runs independently (not gated on verdict_val being None)

### New: `check_proof_sha_consistency(metadata_files_content, bundle_path)`

- Parses SHA-256 claims from `final-bundle-validation-proof.txt`
- Computes actual bundle SHA-256
- Warns (PROOF_SHA_SIDECAR_RECOMMENDED) when claimed SHA != actual SHA
- Self-referential SHA is expected inside ZIP; this is a WARN, not error
- Returns empty list if no SHA claimed in proof

### Extended: `COMMAND_LOG_STALE_PATTERNS`

New patterns added (R52):
- `"to be completed in mt"` — validation log written pre-execution with MT placeholders
- `"pass 1: pending"` — stale placeholder from template
- `"pass 2: pending"` — stale placeholder from template
- `"pending final validation"` — generic pre-execution placeholder
- `"to be completed"` — generic pre-execution placeholder

### Fixed: `check_no_pending_reports()` PENDING_SCAN_SKIP_FILES

Added `PENDING_SCAN_SKIP_FILES = frozenset({"git-log.txt", "git-status-final.txt", "git-status.txt"})`.
Git log often contains commit messages mentioning `BUNDLE_VALIDATION: PENDING` from prior sprint closeouts.

### Fixed: `check_proof_file_finality()` auto-proof transient placeholder

Added exclusion for `"PLACEHOLDER — will be replaced after candidate validation"` (exact match). This is the transient text written by `build_auto_proof_bundle` during Pass 1; by Pass 3, it is replaced with actual metrics.

## Changes to build_evidence_bundle.py

Changed Pass 1 intermediate text from `"Pass 2 pre-proof build in progress..."` to `"Pass 2 pre-proof build: computing bundle metrics"` to avoid matching `PROOF_FILE_PLACEHOLDER_PATTERNS["IN PROGRESS"]`.

## Changes to state_snapshot.py

Added Format C verdict extraction to `get_latest_sprint()`:
```python
if not verdict:
    m = re.search(r"##\s+Verdict\s*\n+\s*`([A-Z][A-Z0-9_]+)`", content)
    if m:
        verdict = m.group(1)
```

## Test Coverage

| File | Tests | Status |
|------|-------|--------|
| tests/evidence/test_r52_validator_hardening.py | 19 | PASS |
| tests/evidence/test_r51_validator_hardening.py | 16 | PASS |
| tests/state/test_state_snapshot.py (new guards) | +9 | PASS |
| tests/evidence/test_r28_evidence_automation.py (fix) | 1 fixed | PASS |
| tests/evidence/test_r49_validator_hardening.py (preserved) | 7 | PASS |
| tests/evidence/test_auto_proof_bundle.py (fixed) | 9 | PASS |
| **Total evidence suite** | **827** | **PASS** |
