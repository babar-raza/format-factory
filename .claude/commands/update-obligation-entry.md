# /update-obligation-entry

**Mission:** ALLFORMAT-DEEPENING-20260625
**Skill ID:** update-obligation-entry
**Product Track:** all_format_deepening
**Idempotency:** Updates fields in place; re-run with same values is safe.

## Purpose

Updates specific fields of a single entry in `reports/all-format-deepening/all-format-obligation-register.yaml`.

## Required Inputs

- `obligation_id`: e.g. `ALLF-FODS-PY`
- Fields to update (one or more):
  - `current_state`: queued | in_progress | completed_and_verified | waiting_gate_11 | blocked
  - `current_proof_level`: PROOF_LEVEL_0..5
  - `terminal_state`: COMPLETED_AND_VERIFIED | WAITING_VALID_GATE_11_AUTHORIZATION | BLOCKED_TRUE_EXTERNAL_DEPENDENCY | null
  - `evidence_paths`: list of relative paths to evidence files

## Guards (enforced before writing)

1. **Cannot set `terminal_state: COMPLETED_AND_VERIFIED`** without at least one `evidence_paths` entry
2. **Cannot decrease `current_proof_level`** — proof level is monotonically increasing
3. **Cannot set `WAITING_VALID_GATE_11_AUTHORIZATION`** without gate 10 completion evidence
4. **Cannot set `BLOCKED_TRUE_EXTERNAL_DEPENDENCY`** without a documented blocker reason

## Steps

1. Read `reports/all-format-deepening/all-format-obligation-register.yaml`
2. Find entry with matching `obligation_id`
3. Apply guard checks
4. Update fields
5. Write file back
6. Print: `UPDATED: {obligation_id} → {terminal_state}`

## After Update

Run `/portfolio-reconcile` if `terminal_state` changed to verify counts still reconcile.
