# /portfolio-reconcile

**Mission:** ALLFORMAT-DEEPENING-20260625
**Skill ID:** portfolio-reconcile
**Product Track:** all_format_deepening
**Idempotency:** Regenerates from obligation register on each run; safe to re-run.

## Purpose

Reads `reports/all-format-deepening/all-format-obligation-register.yaml`, counts entries by terminal state, verifies the portfolio equation, and writes a reconciliation record.

## Steps

1. Read `reports/all-format-deepening/all-format-obligation-register.yaml`
2. Count entries by terminal_state bucket:
   - `completed_and_verified`: all COMPLETED_AND_VERIFIED entries (including export_helper_scope)
   - `waiting_gate_11`: all WAITING_VALID_GATE_11_AUTHORIZATION entries
   - `blocked_external`: all BLOCKED_TRUE_EXTERNAL_DEPENDENCY entries
   - `open_gaps`: entries with terminal_state = null (still open)
3. Verify equation: `completed + waiting_gate_11 + blocked_external + open_gaps = total_surfaces`
4. Check no-exception audit:
   - `omitted: 0` — every surface has an entry
   - `deferred: 0` — no DEFERRED terminal state
   - `unknown: 0` — no entries with unrecognized state
5. Write output YAML

## Output File

`reports/all-format-deepening/portfolio-reconciliation-ALLFORMAT-DEEPENING-20260625.yaml`

```yaml
mission_id: ALLFORMAT-DEEPENING-20260625
generated_at: {timestamp}
total_surfaces: {count}
completed_and_verified: {count}
waiting_gate_11: {count}
blocked_external: {count}
open_gaps: {count}
omitted: 0
deferred: 0
unknown: 0
equation: "{completed} + {gate_11} + {blocked} + {open} = {total}"
counts_reconcile: true | false
no_exception_audit:
  every_format_in_register: true
  no_silent_deferral: true
  pilots_not_mistaken_for_portfolio_completion: true
  priority_not_used_as_scope_reduction: true
eligible_remaining: {open_gaps}
final_verdict: ALL_FORMATS_AND_PRODUCT_SURFACES_DEEPENED_AND_RECONCILED | ALL_FORMATS_ACCOUNTED_FOR_PRODUCT_DEEPENING_ACTIVE
```

## Verdict Rules

- `ALL_FORMATS_AND_PRODUCT_SURFACES_DEEPENED_AND_RECONCILED`: `open_gaps = 0` AND `counts_reconcile: true`
- `ALL_FORMATS_ACCOUNTED_FOR_PRODUCT_DEEPENING_ACTIVE`: `open_gaps > 0` AND `counts_reconcile: true`
- `FORMAT_OBLIGATION_REGISTER_INCOMPLETE`: `counts_reconcile: false`

## Fail Conditions

If `counts_reconcile: false`: STOP. Find the missing entry. Add it to the obligation register. Re-run.
If any `deferred > 0` or `unknown > 0`: STOP. Resolve the entry. Re-run.

## Required Inputs

- `mission_id` — value for `mission_id`

## Allowed Paths

- `registry/ — format and obligation registries (read/write)`
- `reports/ — deepening reports (write)`
- `plans/ — deepening plans (read/write)`

## Forbidden Paths

- `src/net/**` — no product source mutation in deepening skills
- `src/python/**` — no product source mutation in deepening skills
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the portfolio reconciliation report cannot be written
- Stop if the execution would modify any file under src/

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
