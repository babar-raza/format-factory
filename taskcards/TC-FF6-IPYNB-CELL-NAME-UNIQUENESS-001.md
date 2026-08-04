---
artifact_id: TC-FF6-IPYNB-CELL-NAME-UNIQUENESS-001
artifact_type: taskcard
path: taskcards/TC-FF6-IPYNB-CELL-NAME-UNIQUENESS-001.md
format_id: ipynb
product_family: python-format-library
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-execution
source_hash: null
generated_by: claude
generated_at: 2026-08-04
reusable: false
refresh_policy:
  trigger: ipynb-validation-rule-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: IPYNB_PROOF_REQUIREMENT_AUDIT
status: ACCEPTED
lane: IPYNB
skill_ids:
  - product-source-task
  - test-driven-development
release_blockers: []
notes: >
  A MUST-level obligation is entirely unimplemented. Found by writing
  shipped-namespace coverage for the cell-identity capabilities under GAP-017 —
  the capability whose only tests were shadow-package tests.
---

## Defect

`SAL-IPYNB-OBL-...033A30BD` (MUST, profiles 4.2–4.5):

> For profiles 4.2 and later, perform an additional notebook-wide uniqueness
> check for present cell metadata names.

`SAL-IPYNB-OBL-...B9838FFD` records why it must be a *semantic* check:

> Since nbformat 4.2 cell names are expected to be unique within a notebook;
> from 4.4 the authority explicitly states that **JSON Schema cannot enforce
> uniqueness**.

Measured behavior — a two-cell notebook where both cells carry
`metadata.name = "dup"`:

| profile | duplicates | obligation requires rejection | |
|---|---|---|---|
| 4.0 | accepted | no | ok |
| 4.1 | accepted | no | ok |
| 4.2 | **accepted** | **yes** | **defect** |
| 4.3 | **accepted** | **yes** | **defect** |
| 4.4 | **accepted** | **yes** | **defect** |
| 4.5 | **accepted** | **yes** | **defect** |

There is no name-uniqueness code anywhere in the package — no `seen_names`, no
duplicate-name diagnostic code. Since the official schema provably cannot
express this, and nothing else checks it, duplicate cell names pass validation
silently at every profile that forbids them.

The machinery already exists for the sibling case: cell **ids** are checked for
duplicates via `seen_ids` and emit `IPYNB_CELL_ID_DUPLICATE`. The same shape was
simply never applied to names.

### Why it stayed hidden

This capability's only test file was `test_ipynb_cell_id.py`, which imports the
deprecated `ipynb.*` shadow package — so it never exercised the shipped
validator (GAP-017/GAP-018). The obligation had no valid evidence at all, which
is exactly the condition under which a MUST can go unimplemented unnoticed.

## RED scenarios

1. Duplicate `metadata.name` is rejected at 4.2, 4.3, 4.4 and 4.5.
2. Duplicate names remain accepted at 4.0 and 4.1 — the obligation scopes the
   check to 4.2+, so tightening earlier profiles would be its own defect.
3. Distinct names pass at every profile.
4. Absent names pass at every profile — the check applies to *present* names.
5. Cells with no `metadata` mapping at all do not crash the check.
6. Three cells where only two collide report the duplicate, not the distinct one.
7. The diagnostic points at the offending cell's own metadata path.
8. Empty-string names still fail as before (`^.+$`) and are not double-reported.

## Exact writable product paths

- `src/python/ipynb/src/format_factory/ipynb/validation/rules.py`
- `tests/python/ipynb/test_obligation_cell_identity.py`
- `shared/format-contracts/implementation-evidence/ipynb.yaml`

## Acceptance criteria

- [x] All 8 RED scenarios captured failing where applicable, then passing.
- [x] Diagnostic code follows the existing convention
      (`IPYNB_CELL_NAME_DUPLICATE`, mirroring `IPYNB_CELL_ID_DUPLICATE`).
- [x] Profiles 4.0 and 4.1 unchanged.
- [x] Full IPYNB suite green, no regression against 456 passed / 3 failed.
- [x] `ruff` and `mypy` clean.
- [x] Ledger regenerated; the affected obligations leave `missing`.
