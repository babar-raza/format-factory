---
artifact_id: accel003-final-zip-proof-repair-20260513
artifact_type: report
sprint_id: GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001
lane: A
generated_at: "2026-05-13"
visibility: internal
---

# ACCEL-003 Final-ZIP Proof Repair Report

## Defect Summary

**Previous (2-pass) behavior:**
- Pass 1: Build candidate ZIP, validate
- Write proof with candidate metrics to on-disk file
- Pass 2: Build final ZIP (proof inside ZIP had candidate-only metrics)
- AFTER Pass 2: Update on-disk proof with final metrics

**Defect:** The proof file embedded INSIDE the final ZIP contained only candidate metrics.
Tests only read from `metadata_dir/final-bundle-validation-proof.txt` (on-disk), not from
inside the ZIP itself. So the defect was hidden.

## Repair Design

**Chosen: 3-pass with self-reference note**

This is the honest, deterministic design. The proof embedded inside the final ZIP
cannot contain the hash of the ZIP it is inside (circular dependency). Instead:

| Pass | Action | Proof content after |
|------|--------|---------------------|
| Pass 1 | Build candidate, validate | Candidate metrics written to disk |
| Pass 2 | Build pre-proof final, validate | Candidate + pre-proof metrics embedded |
| Pass 3 | Rebuild final with complete proof, validate | Complete proof inside ZIP |
| Post-P3 | Compute Pass 3 hash/bytes | On-disk proof updated with external record |

**Self-reference note (embedded in proof inside ZIP):**
> The SHA-256 and bytes of the final ZIP (Pass 3) cannot be embedded in this proof
> before Pass 3 is built (circular dependency). Pre-proof SHA-256 above verifies the
> Pass 2 build independently. To verify Pass 3: compute SHA-256 of this ZIP externally.
> The on-disk proof file (metadata_dir) contains the final SHA-256 after Pass 3.

## Proof Structure

### Inside Final ZIP (Pass 3)
```
BUNDLE_VALIDATION: PASS
sprint_id: {sprint_id}
contract_id: {sprint_id}

=== CANDIDATE (Pass 1) ===
Candidate: {name}-candidate.zip
Candidate SHA-256: {hash}
Candidate entries: {n}
Candidate bytes: {n}
Candidate metadata: {n}

=== PRE-PROOF FINAL (Pass 2) ===
Pre-proof final: {name}.zip
Pre-proof SHA-256: {hash}    ← verifiable; ZIP existed before proof was embedded
Pre-proof entries: {n}
Pre-proof bytes: {n}
Pre-proof metadata: {n}

=== FINAL WITH PROOF EMBEDDED (Pass 3) ===
Final: {name}.zip
Final entries: {n}           ← deterministic (same file set as Pass 2)
Final metadata: {n}
Self-reference note: ...

Validator: validate_evidence_bundle.py --check-no-pending
Final validation: PASS
Timestamp: ...
```

### On-disk proof (additionally appended after Pass 3)
```
=== PASS 3 EXTERNAL VERIFICATION RECORD ===
Final SHA-256: {pass3_hash}    ← actual hash of the final ZIP after proof embedding
Final bytes: {pass3_bytes}
Final entries: {n}
Final metadata: {n}
Proof embedded in ZIP: YES
Pass 3 timestamp: ...
```

## Test Results

| Test | Description | Result |
|------|-------------|--------|
| test_auto_proof_happy_path | 3-pass builds, final exists, no placeholder | PASS |
| test_auto_proof_candidate_fail_stops_final | Failure stops output | PASS |
| test_auto_proof_proof_file_content | On-disk proof has all metrics | PASS |
| test_auto_proof_sprint_id_in_proof | sprint_id matches | PASS |
| test_build_bundle_unchanged_without_auto_proof | Non-auto-proof unchanged | PASS |
| test_auto_proof_final_no_pending | Final validates --check-no-pending | PASS |
| test_auto_proof_includes_final_bundle_metrics | On-disk has Final SHA-256 etc | PASS |
| test_proof_inside_zip_is_not_candidate_only | ZIP proof has pre-proof section | PASS |
| test_proof_inside_zip_has_required_fields | ZIP proof has path/entries/metadata/PASS | PASS |

**TOTAL: 9/9 PASS**

## Files Changed
- `tools/evidence/build_evidence_bundle.py` — 3-pass implementation
- `tests/evidence/test_auto_proof_bundle.py` — 9 tests (2 new: Test 8, Test 9)

## Lane Verdict

LANE_A_PASS_WITH_SELF_REFERENCE_NOTE
