# /build-obligation-register

**Mission:** ALLFORMAT-DEEPENING-20260625
**Skill ID:** build-obligation-register
**Product Track:** all_format_deepening
**Idempotency:** If `reports/all-format-deepening/all-format-obligation-register.yaml` exists and surface count matches, update entries only; do not recreate.

## Purpose

Scans all authoritative discovery sources and creates the all-format obligation register. Ensures zero formats are omitted, deferred, or silently excluded.

## Discovery Sources (scan ALL, use union)

- `shared/qname-registry/*.yaml` — 20 canonical format definitions
- `src/python/*/` — Python package roots
- `src/net/*/` — .NET project roots
- `packaging/python/package-matrix.yaml` — 16 Python packages
- `registry/parity-matrix.yaml` — cross-language parity and classification
- `registry/product-deepening-ledger.yaml` — current deepening status
- `tests/python/*/` and `tests/net/*/` — test roots

## Output Files

Create directory `reports/all-format-deepening/` if it does not exist.

1. `reports/all-format-deepening/all-format-universe.yaml`
2. `reports/all-format-deepening/all-format-obligation-register.yaml`
3. `reports/all-format-deepening/format-accounting-gate.yaml`

## Obligation Entry Schema (per surface)

```yaml
obligation_id: ALLF-{FORMAT}-{LANG}    # e.g. ALLF-FODS-PY
format_id: {format}
language: python | dotnet
source_present: true | false
package_present: true | false
current_proof_level: PROOF_LEVEL_0..5
target_proof_level: PROOF_LEVEL_4       # Python FOSS; PROOF_LEVEL_5 for .NET commercial ODF
current_state: queued | in_progress | completed_and_verified | waiting_gate_11 | blocked
terminal_state: null                    # until closed
classification: standalone_product | export_helper_only
evidence_paths: []
notes: ""
```

## Classification Rules

- `export_helper_only`: formats where `parity-matrix.yaml` has `standalone_product: false` (html, markdown, txt)
- `standalone_product`: all other formats

## Terminal State Rules

- `COMPLETED_AND_VERIFIED`: source present + tests pass + consumer_roundtrip.py prints CONSUMER_PROOF: PASS + proof level met
- `COMPLETED_AND_VERIFIED (export_helper_scope)`: export_helper_only classification + parent format exporters verified
- `WAITING_VALID_GATE_11_AUTHORIZATION`: Gate 10 complete + G11-G sub-gate approved + awaiting Babar Raza commercial sign-off
- `BLOCKED_TRUE_EXTERNAL_DEPENDENCY`: proven external blocker (credentials, regulatory)

## Format Accounting Gate

```yaml
format_accounting_gate:
  total_surfaces: {count}
  completed_and_verified: {count}
  waiting_gate_11: {count}
  open_gaps: {count}
  blocked_external: 0
  omitted: 0
  deferred: 0
  unknown: 0
  equation: "{completed} + {gate_11} + {open} + {blocked} = {total}"
  counts_reconcile: true | false
```

Required: `counts_reconcile: true` before continuing.

## Spot-Check Validation (run after building)

Run `/verify-obligation-entry` on at minimum:
- One COMPLETED_AND_VERIFIED entry (e.g. ALLF-ABW-PY)
- One WAITING_GATE_11 entry (e.g. ALLF-FODS-NET)
- One OPEN entry (e.g. ALLF-FODP-PY)

## Ledger Entry

Add to `reports/r90/product-code-change-ledger.json`:
```json
{"sprint": "TC-B-002", "action": "build_obligation_register", "files": ["reports/all-format-deepening/all-format-obligation-register.yaml"]}
```

## Required Inputs

- `mission_id` — value for `mission_id`
- `output_path` — file path where the output report should be written

## Allowed Paths

- `registry/ — format and obligation registries (read/write)`
- `reports/ — deepening reports (write)`
- `plans/ — deepening plans (read/write)`

## Forbidden Paths

- `src/net/**` — no product source mutation in deepening skills
- `src/python/**` — no product source mutation in deepening skills
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the obligation register cannot be written
- Stop if the execution would modify any file under src/

## Output Format

- Generated artifact written to the configured output path
- Confirmation message: file path and size
- Validation result confirming the output is well-formed
