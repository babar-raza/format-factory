# Lane 3 — Validator Hardening

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## New Validator: validate_supervisor_evidence_bundle.py

**Location:** `tools/supervisor/validate_supervisor_evidence_bundle.py`
**Tests:** `tests/supervisor/test_validate_supervisor_evidence_bundle.py`

### Checks Implemented

| Check ID | Defect Prevented | Type | Test |
|---|---|---|---|
| SUP-V-001 | Bundle exists and is readable | FAIL | test_bundle_not_found |
| SUP-V-002 | Bundle is valid ZIP | FAIL | test_bundle_not_found |
| SUP-V-003 (D-SUP-01) | Contract file present in ZIP | FAIL | test_missing_contract_fails |
| SUP-V-004 (D-SUP-02) | reports/supervisor/ outputs present if claimed | FAIL | test_missing_supervisor_reports_fails |
| SUP-V-005 (D-SUP-03) | SHA correct or uses delegation label | WARN | test_stale_sha_warns, test_delegation_label_passes_sha_check |
| SUP-V-006 | BUNDLE_VALIDATION claim has raw log | WARN | test_false_bundle_validation_claim_warns |
| SUP-V-007 (D-SUP-04) | Replay fixture present if replay claimed | FAIL | test_missing_replay_fixture_fails |
| SUP-V-008 | No PENDING markers in final verdict | FAIL | test_pending_in_verdict_fails |
| SUP-V-009 | Accepted limitations have follow-up references | WARN | (good bundle test) |

### Test Results

```
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_good_bundle_passes PASSED
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_missing_contract_fails PASSED
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_stale_sha_warns PASSED
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_delegation_label_passes_sha_check PASSED
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_missing_supervisor_reports_fails PASSED
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_missing_replay_fixture_fails PASSED
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_false_bundle_validation_claim_warns PASSED
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_pending_in_verdict_fails PASSED
tests/supervisor/test_validate_supervisor_evidence_bundle.py::test_bundle_not_found PASSED

9 passed in 0.67s
```

### Integration with Sprint Protocol

The validator is run as part of final bundle verification:
```bash
python tools/supervisor/validate_supervisor_evidence_bundle.py \
  <bundle.zip> \
  --contract <contract.yaml>
```

Both `validate_evidence_bundle.py` (existing) AND `validate_supervisor_evidence_bundle.py` (new) must pass before final verdict is written.

## Hardening Design Decisions

1. **WARN vs FAIL for SHA mismatch**: One-generation-behind SHA is acceptable (circular dependency). Validator warns but doesn't fail. Delegation label is the recommended pattern.
2. **FAIL for missing contract**: This is unambiguous — a bundle without its own contract cannot be reviewed independently.
3. **FAIL for missing supervisor reports when claimed**: If the evidence summary claims `supervisor_loop.py run-on-latest | EXIT 0`, the outputs must be present.
4. **FAIL for PENDING markers**: PENDING in final verdict is always an error (validator already checks this via existing validate_evidence_bundle.py check_no_pending).
5. **WARN for missing raw validation log**: Not always included; bundle passes the actual validator anyway.
