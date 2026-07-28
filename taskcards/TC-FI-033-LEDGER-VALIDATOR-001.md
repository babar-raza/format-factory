---
artifact_id: TC-FI-033-LEDGER-VALIDATOR-001
artifact_type: taskcard
path: taskcards/TC-FI-033-LEDGER-VALIDATOR-001.md
format_id: null
product_family: six_python_production_program
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-26
---

# TC-FI-033-LEDGER-VALIDATOR-001: Fail Closed on Mixed Historical Ledger Records

**Status:** completed
**Skill:** `found-issue-ownership`
**Scope:** Canonical proof machinery supporting all six Python products.

## Objective

Prevent the R90 product-code ledger validator from throwing on historical
mixed-schema records. Preserve history verbatim, derive a current proof
projection only from current-shaped product entries, and return structured
errors for malformed current entries.

## Implementation

1. Reproduced the AttributeError against the real ledger.
2. Added regressions for a malformed current source record and a historical
   test-coverage record with string paths.
3. Partitioned current proof entries from historical entries before validation.
4. Made malformed current source items a deterministic validation error.
5. Kept the live result failing until the remaining current schema errors are
   migrated; no readiness label was changed.

## Evidence

- `22 passed, 1 xfailed`: focused validator and R90 acceleration tests.
- Real ledger: no exception; `valid=false`, 1,576 historical IDs reported,
  and 3,233 current-projection errors surfaced.

## Follow-on Obligation

Create a successor ledger-migration task that normalizes or explicitly retires
the remaining 1,205 current-shaped records and replaces worktree-byte hashes
with canonical content digests. This completed repair is not evidence that the
ledger is promotion-ready.
