# ACCEL-003: Evidence Final-Proof Automation Implementation Report
**Date:** 2026-05-11
**Sprint:** POST-FODT-GATE10-CONTROLLED-SWARM-001 (Lane B)

---

## Implementation Summary

Added `--auto-proof` flag to `tools/evidence/build_evidence_bundle.py` via new function `build_auto_proof_bundle()`.

## What Was Implemented

### New function: `build_auto_proof_bundle()`
- Located at end of `build_evidence_bundle.py` before `main()`
- Parameters: `repo_root, contract_path, output_path, metadata_dir, allow_legacy_root_metadata=False, require_clean_git=True`
- Pass 1: Write placeholder proof → build candidate → validate candidate
- If pass 1 fails: delete candidate, return False (no misleading output)
- Write real proof: sprint_id, contract_id, candidate name, SHA-256, entries, bytes, metadata count, timestamp
- Pass 2: Rebuild final with real proof → validate final
- If pass 2 fails: delete final, return False
- Success: prints `BUNDLE_VALIDATION: PASS` and `EVIDENCE_BUNDLE: <absolute_path>`

### New CLI flag: `--auto-proof`
- Added to `main()` argparse
- Mutually exclusive in behavior with `--dry-run` (documented in help text)
- When not used: existing behavior unchanged

### Key design choices
- `sprint_id` for proof text extracted from contract (not filename) to avoid METADATA_IDENTITY mismatch
- `require_clean_git` parameter enables test isolation via `emergency_blocker_bundle: true` in test contracts
- No new import dependencies (uses existing `subprocess`, `hashlib`, `zipfile`)

## Test Results

6/6 PASS (`tests/evidence/test_auto_proof_bundle.py`):
1. `test_auto_proof_happy_path` — PASS
2. `test_auto_proof_candidate_fail_stops_final` — PASS
3. `test_auto_proof_proof_file_content` — PASS
4. `test_auto_proof_sprint_id_in_proof` — PASS
5. `test_build_bundle_unchanged_without_auto_proof` — PASS
6. `test_auto_proof_final_no_pending` — PASS

## Usage

```bash
# New: two-pass auto-proof build
python tools/evidence/build_evidence_bundle.py \
  --repo-root . \
  --contract tools/evidence/contracts/my-sprint.yaml \
  --metadata-dir .local/my-sprint-metadata/ \
  --output .local/evidence-bundles/my-sprint.zip \
  --auto-proof

# Existing: unchanged
python tools/evidence/build_evidence_bundle.py \
  --repo-root . \
  --contract tools/evidence/contracts/my-sprint.yaml \
  --metadata-dir .local/my-sprint-metadata/ \
  --output .local/evidence-bundles/my-sprint.zip
```

## Backwards Compatibility: CONFIRMED
Existing builds without `--auto-proof` are unchanged.
