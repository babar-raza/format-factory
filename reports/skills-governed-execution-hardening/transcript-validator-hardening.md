# Transcript Validator Hardening Report
Sprint: FORMAT-FACTORY-SKILLS-GOVERNED-EXECUTION-HARDENING-IV-001

---

## Result: VALIDATOR CATCHES ALL CRITICAL VIOLATIONS — PASS

---

## Validator: tools/supervisor/validate_skill_transcript.py

Required fields checked:
- invocation_id, skill_id, mode, inputs, allowed_files, actual_files_changed, tests_run, result

Additional checks:
- mode must be in {dry-run, live, anti-bypass-demo}
- result must be in {PASS, FAIL}
- actual_files_changed must be subset of allowed_files (when present)
- skill_id must be registered (warning if not in registry)
- timestamp recommended (warning if absent)

---

## Negative Fixture Test Results (11 fixtures)

| Fixture | Violation | Expected | Actual | Match |
|---------|-----------|----------|--------|-------|
| TRANS-POS-001 | None (compliant) | PASS | PASS | YES |
| TRANS-NEG-001 | Missing invocation_id | FAIL | FAIL | YES |
| TRANS-NEG-002 | Missing skill_id | FAIL | FAIL | YES |
| TRANS-NEG-003 | Missing allowed_files | FAIL | FAIL | YES |
| TRANS-NEG-004 | File outside allowed_files | FAIL | FAIL | YES |
| TRANS-NEG-005 | Forbidden file (src/python) | FAIL | FAIL | YES |
| TRANS-NEG-006 | Missing tests_run | FAIL | FAIL | YES |
| TRANS-NEG-007 | Missing result | FAIL | FAIL | YES |
| TRANS-NEG-008 | Missing timestamp | WARNING | WARNING | YES |
| TRANS-NEG-009 | Live mode, empty actual_files_changed | WARNING | WARNING | YES |
| TRANS-NEG-010 | Invalid mode value | FAIL | FAIL | YES |

All 11 fixtures match expected behavior.
All expected failures close as CLOSED_EXPECTED_FAILURE.
No unexpected passes or unexpected failures.

---

## Critical Boundary: Forbidden Path Protection

The validator checks that `actual_files_changed` is a subset of `allowed_files`.
If a transcript claims a file was changed that was not in allowed_files, the validator
returns FAIL. This means:
- An agent cannot claim it changed `src/python/sylk/sylk_parser.py` without that file
  being in the handoff's allowed_files.
- An agent cannot claim registry/format-registry.yaml was changed.
- An agent cannot claim .supervisor/policies.yaml was changed.

This boundary is critical for preventing false authority claims in transcripts.

---

## Gap: Capability Matrix Authority Check

The validator does NOT currently check whether a transcript is claiming a direct
capability matrix update vs. a proposed delta. This is a future hardening opportunity.
For now, the governed source-change contract's tier system handles this:
- Direct authority mutation → FAIL_CLOSED tier → requires product ledger + source diff
- If those are absent → transcript fails
