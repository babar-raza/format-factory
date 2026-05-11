# Evidence Final-Proof Two-Pass Automation Plan
**Date:** 2026-05-11
**Sprint:** FODT-GATE10-APPROVAL-AND-SWARM-NEXT-LANES-001 (Lane D)

---

## 1. Recurring Problem Statement

Every evidence bundle build follows a two-pass pattern:

1. **Pass 1 (candidate):** Create a placeholder `final-bundle-validation-proof.txt`, build the zip, run the validator, capture the PASS output.
2. **Pass 2 (final):** Overwrite the placeholder with the real validator output (referencing the candidate zip hash/size), rebuild the zip, re-validate.

This two-pass pattern is manual, error-prone, and has caused at least two repair sprints (S-F2F-04-CLOSURE-PROOF-REPAIR-001 being the most recent). The placeholder file is sometimes committed or left with build-time content rather than the actual validation proof.

### Observed Failure Modes

| Failure | Sprints Affected | Root Cause |
|---|---|---|
| Placeholder proof committed as-is | S-F2F-04 closure | Builder does not auto-populate proof |
| Proof references candidate zip but final zip differs | Multiple | Manual copy-paste of validator output |
| Metadata count mismatch between passes | run046 regression | Proof file counted differently between passes |
| Builder runs before all metadata exists | Multiple | No dependency ordering in builder |

## 2. Proposed Builder-Level Fix

### 2a. Auto Two-Pass Mode

Add a `--auto-proof` flag to `build_evidence_bundle.py` that:

1. Creates the placeholder `final-bundle-validation-proof.txt` automatically.
2. Builds the candidate zip (pass 1).
3. Runs `validate_evidence_bundle.py` against the candidate zip.
4. If validation PASS: captures the validator output into `final-bundle-validation-proof.txt` with candidate zip metadata (path, size, entry count, sha256).
5. Rebuilds the final zip (pass 2) with the real proof file.
6. Runs validation against the final zip.
7. If final validation PASS: prints `BUNDLE_VALIDATION: PASS` and `EVIDENCE_BUNDLE: <path>`.
8. If any validation FAIL: stops with error, does NOT produce a final bundle.

### 2b. Exact Desired Behavior

```
$ python build_evidence_bundle.py \
    --repo-root . \
    --contract contracts/my-sprint.yaml \
    --metadata-dir .local/my-sprint-metadata/ \
    --output .local/evidence-bundles/my-sprint.zip \
    --auto-proof

[PASS 1] Building candidate bundle...
[PASS 1] Candidate: .local/evidence-bundles/my-sprint-candidate.zip
[PASS 1] Running validator on candidate...
[PASS 1] BUNDLE_VALIDATION: PASS (350 entries, 900,000 bytes, 35 metadata)
[PROOF] Writing final-bundle-validation-proof.txt with candidate results
[PASS 2] Rebuilding final bundle with real proof...
[PASS 2] Final: .local/evidence-bundles/my-sprint.zip
[PASS 2] Running validator on final...
BUNDLE_VALIDATION: PASS (350 entries, 900,001 bytes, 35 metadata)
EVIDENCE_BUNDLE: C:\Users\...\my-sprint.zip
```

### 2c. Proof File Content (Auto-Generated)

```
BUNDLE_VALIDATION: PASS
Candidate: my-sprint-candidate.zip
Candidate SHA-256: <hash>
Candidate entries: 350
Candidate bytes: 900,000
Candidate metadata: 35
Final rebuild includes this proof file.
Validator: validate_evidence_bundle.py
Contract: contracts/my-sprint.yaml
Timestamp: 2026-05-11T14:30:00Z
```

## 3. Tests Needed

| # | Test | Description |
|---|---|---|
| T1 | Auto-proof happy path | `--auto-proof` produces final bundle with real proof; validator PASS on both passes |
| T2 | Candidate fails validation | `--auto-proof` with bad contract; stops after pass 1 FAIL; no final bundle produced |
| T3 | Proof file content | Parse auto-generated proof; verify candidate hash, entry count, byte size present |
| T4 | No --auto-proof backwards compat | Without flag, builder behaves exactly as today (no two-pass) |
| T5 | --check-no-pending on final | Final bundle proof must not contain PENDING markers |
| T6 | Metadata count consistency | Pass 1 and pass 2 metadata counts match (proof file adds 0 new metadata — it replaces placeholder) |

## 4. Migration Strategy for Old Bundles

- No migration needed. Old bundles are immutable zips.
- Old contracts continue to work unchanged (no `--auto-proof` flag means old behavior).
- New contracts can opt into `--auto-proof` by documenting it in the sprint execution prompt.
- The proof file name (`final-bundle-validation-proof.txt`) does not change.

## 5. Acceptance Criteria

1. `--auto-proof` flag accepted by `build_evidence_bundle.py`.
2. Two-pass build completes without manual intervention.
3. Final proof file contains candidate zip metadata (hash, size, entries).
4. All 6 tests (T1-T6) pass.
5. Without `--auto-proof`, existing behavior is unchanged.
6. No new dependencies added (uses existing subprocess + validator).

## 6. When to Implement

**Recommended:** Next evidence-tooling sprint (ACCEL-003). This is NOT blocking any current work but will save 10-15 minutes per sprint and eliminate the proof-placeholder failure mode entirely.

**Not recommended for this sprint:** This sprint is a planning-only lane. Implementation would violate Lane D scope (report-only).

## 7. Relationship to Other Acceleration Items

- ACCEL-001 (controlled parallel lanes): independent — this addresses single-lane efficiency.
- ACCEL-002 (metadata note classification): independent — that addresses review packet efficiency.
- ACCEL-003 (this item): addresses build efficiency and eliminates a recurring error class.
