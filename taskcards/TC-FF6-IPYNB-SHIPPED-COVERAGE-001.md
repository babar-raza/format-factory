---
artifact_id: TC-FF6-IPYNB-SHIPPED-COVERAGE-001
artifact_type: taskcard
path: taskcards/TC-FF6-IPYNB-SHIPPED-COVERAGE-001.md
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
  trigger: ipynb-shadow-package-retirement
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: IPYNB_PROOF_REQUIREMENT_AUDIT
status: ACCEPTED
lane: IPYNB
skill_ids:
  - test-driven-development
  - product-source-task
release_blockers: []
notes: >
  Closes the GAP-017 evidence hole for IPYNB-OUTPUT-001, the largest affected
  capability (7 of the 15 obligations with no valid evidence).
---

## Problem

GAP-017: six IPYNB capabilities have **no valid obligation evidence** because
their only tests import the deprecated `ipynb.*` shadow package rather than the
shipped `format_factory.ipynb` namespace. `forbidden_progress_claims` bars
counting that as coverage.

This card takes the largest of them, **IPYNB-OUTPUT-001 (7 obligations)**, whose
only test file was `test_ipynb_output_mime_api.py` — shadow-only.

## Why not port the shadow tests

The two packages genuinely differ where obligations are decided. For
IPYNB-ID-001 the shipped namespace generates cell ids only via explicit upgrade,
as its obligation requires, while the shadow package auto-assigns them on load,
which the obligation forbids. A mechanical port would carry the wrong
expectations across. Assertions here are derived from each obligation's own
`rule_text` and `required_tests`, then checked against observed shipped
behavior.

## Obligations covered

| Obligation | Requirement |
|---|---|
| `SAL-IPYNB-OBL-...11DA3594` | Output objects declare `output_type` of stream / display_data / execute_result / error, each with its own required fields. |
| `SAL-IPYNB-OBL-...8CA07D78` | (4.5) Code-cell outputs are typed objects with `output_type` in that set. |
| `SAL-IPYNB-OBL-...6B30D129` | display_data and execute_result carry `data` MIME maps and `metadata` objects. |
| `SAL-IPYNB-OBL-...C72D3E4B` | error outputs carry `ename`, `evalue`, and a `traceback` list of strings. |
| `SAL-IPYNB-OBL-...5AD56F9C` | Code cells carry `execution_count` (integer or null) and an `outputs` array. |
| `SAL-IPYNB-OBL-...14CBF763` | Support every output type and arbitrary MIME bundles, preserving execution counts, tracebacks, metadata, and unknown bundle entries. |
| `SAL-IPYNB-OBL-...7F2275F7` | Full MIME matrix including vendor types, binary payloads, large base64, and malformed bundles. |

Declared `required_tests` for all seven:
*"MIME-bundle matrix round-trips including vendor types and binary payloads"* and
*"MIME matrix fixtures per output type with byte-exact payload verification"*.
Both dimensions — **per output type** and **byte-exact payload** — must be
exercised, per `proof_requirement_audit_lesson`.

## Exact writable product paths

- `tests/python/ipynb/test_obligation_output_mime_matrix.py`
- `shared/format-contracts/implementation-evidence/ipynb.yaml`

No `src/` change is expected: this card supplies missing proof for behavior that
already exists. If a test reveals a real defect, that becomes its own card.

## Acceptance criteria

- [x] Every assertion imports `format_factory.ipynb`; no shadow-package import.
- [x] All four output types covered individually, not only in aggregate.
- [x] Byte-exact payload verification for binary/base64 and vendor MIME types.
- [x] `execution_count` proven for both integer and null.
- [x] Malformed bundles proven to fail closed.
- [x] Ledger regenerated; the 7 obligations leave `missing`.
- [x] Full IPYNB suite green with no regression against 421 passed / 3 failed.


## Execution record (2026-08-04)

35 tests, all importing `format_factory.ipynb`. Suite 421 -> 456 passed, same 3
known editable-install failures, no regression. The 7 IPYNB-OUTPUT-001
obligations move `missing` -> `partial`; the ledger's obligations without valid
evidence drop from 15 to 8.

### Three of my own assertions were wrong, and the library was right

Written from the obligation text before checking behavior, then corrected
against the official schema rather than by loosening the tests:

- `mime_types` is a property, not a method.
- Unknown **output types** inside a code cell are *rejected*, not preserved. The
  official 4.5 schema defines `output` as a oneOf over exactly the four known
  types. It does define an `unrecognized_output` for future minor revisions
  (`additionalProperties: true`, `output_type` explicitly NOT in that enum), but
  `output` never references it, so the strict path is conformant.
- Unknown **top-level keys** on a known output type are likewise rejected; each
  known definition sets `additionalProperties: false`.

The obligation's "preserving ... unknown bundle entries" therefore refers to
unknown MIME types *inside* the `data` bundle, which are preserved exactly --
now asserted directly rather than inferred.

Still `partial`, not `implemented`: these obligations have real evidence for the
first time, but the full per-obligation `proof_requirement` audit has not been
completed for them.
