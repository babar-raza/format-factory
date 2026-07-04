# Idempotency Check
Generated: 2026-07-04

## Check

If TC-ARC-000 through TC-ARC-009 are run again in read-only mode, the output content should
be identical (timestamps may differ; content must be stable).

## Sources

All artifacts in reports/product-architecture/ are derived from:
1. The authoritative plan (imperative-drifting-conway.md) — stable
2. Registry files (qname-to-code-map.yaml, canonical-class-inventory.yaml) — stable
3. Source files in src/ — read-only during arc taskcards

## Expected Result

Re-running derivation from same inputs → same outputs. Idempotency is structural for
read-only analysis tasks. Only timestamps and git HEAD would differ between runs.

## Pilot 12 Verification

Pilot 12 (TC-ARC-013-12) will verify this by re-running TC-ARC-001..009 logic in read-only
mode and comparing checksums of produced YAML files. Any material content difference = FAIL.

## Status

IDEMPOTENCY_EXPECTED — will be confirmed by Pilot 12 evidence in pilot-evidence/.
