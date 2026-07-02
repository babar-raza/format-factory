# /verify-obligation-entry

**Mission:** ALLFORMAT-DEEPENING-20260625
**Skill ID:** verify-obligation-entry
**Product Track:** all_format_deepening
**Idempotency:** Safe to re-run; updates entry fields in place.

## Purpose

Verifies a single entry in `reports/all-format-deepening/all-format-obligation-register.yaml` against the actual current state of the repository. Updates the entry's `current_state`, `current_proof_level`, and `terminal_state` fields based on evidence.

## Required Input

- `obligation_id`: e.g. `ALLF-FODS-PY`

## Verification Steps

### For Python formats (ALLF-{FORMAT}-PY)

1. **Source check:** Verify `src/python/{format}/` exists
2. **Test check:** Run `.venv/Scripts/pytest tests/python/{format}/ -x -q --tb=short`
   - If 0 failures: test evidence confirmed
3. **Consumer proof check:** Check if `examples/python/{format}/consumer_roundtrip.py` exists
   - If yes: run it; check output for `CONSUMER_PROOF: PASS`
4. **Proof level determination:**
   - consumer_roundtrip.py exists + PASS → PROOF_LEVEL_4
   - tests pass but no consumer_roundtrip.py → PROOF_LEVEL_3
   - no tests or tests fail → PROOF_LEVEL_2 or lower

### For .NET formats (ALLF-{FORMAT}-NET)

1. **Source check:** Verify `src/net/{format}/` exists with document model class
2. **Test check:** Run `dotnet test tests/net/{format}/ -v minimal 2>&1 | tail -5`
3. **Gate check:** Run `/check-gate {format} 10` to determine gate status
4. **Export helper check:** If `parity-matrix.yaml` has `standalone_product: false`, mark as `COMPLETED_AND_VERIFIED (export_helper_scope)` if parent exporter tests pass

## Output

Print one of:
- `VERIFIED: ALLF-{FORMAT}-{LANG} → PROOF_LEVEL_4, COMPLETED_AND_VERIFIED`
- `GAP_FOUND: ALLF-{FORMAT}-{LANG} → PROOF_LEVEL_3, missing consumer_roundtrip.py`
- `GAP_FOUND: ALLF-{FORMAT}-{LANG} → PROOF_LEVEL_2, test failures detected`

Update the YAML entry fields: `current_state`, `current_proof_level`, `terminal_state`, `evidence_paths`

## Rollback

No rollback needed — read-only verification + YAML field updates in obligation register only (not source code).

## Required Inputs

- `obligation_id` — identifier of the obligation entry to verify or update

## Allowed Paths

- `registry/ — format and obligation registries (read/write)`
- `reports/ — deepening reports (write)`
- `plans/ — deepening plans (read/write)`

## Forbidden Paths

- `src/net/**` — no product source mutation in deepening skills
- `src/python/**` — no product source mutation in deepening skills
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the obligation entry cannot be verified
- Stop if the execution would modify any file under src/

## Output Format

- Summary of items synced, added, removed, or unchanged
- Report file at `reports/` confirming final state
- Exit code 0 on success; non-zero with error message on failure
