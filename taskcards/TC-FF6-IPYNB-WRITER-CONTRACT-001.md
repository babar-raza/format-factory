---
artifact_id: TC-FF6-IPYNB-WRITER-CONTRACT-001
artifact_type: taskcard
path: taskcards/TC-FF6-IPYNB-WRITER-CONTRACT-001.md
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
  trigger: ipynb-writer-change
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
  The last two IPYNB capabilities with no valid evidence under GAP-017.
  IPYNB-WRITE-001 is MUST and has one unimplemented clause; IPYNB-EXPORT-001 is
  SHOULD and is entirely unimplemented.
---

## IPYNB-WRITE-001 (MUST) — `SAL-IPYNB-OBL-...FCCD0E0C`

> Write valid UTF-8 JSON with **configurable formatting** and canonical key
> ordering that never reorders cells or outputs; retain unknown fields and
> binary MIME payloads exactly.

Clause-by-clause against measured behavior:

| Clause | State |
|---|---|
| valid UTF-8 JSON | **implemented** — `ensure_ascii=False`; `héllo ☃` lands as real UTF-8 bytes, not `\uXXXX` escapes |
| canonical key ordering | **implemented** — `sort_keys=True` |
| never reorders cells or outputs | **implemented** — verified against deliberately out-of-order ids |
| retain unknown fields | **implemented** — proven for MIME bundles in TC-FF6-IPYNB-SHIPPED-COVERAGE-001 |
| retain binary MIME payloads exactly | **implemented** — base64 round-trips byte-exact |
| **configurable formatting** | **NOT IMPLEMENTED** — `indent=1` is hardcoded at `writer.py:142` and `:185`; neither `dumps()` nor `dump()` exposes any formatting parameter |

### Fix

Add an optional `indent` parameter to `dumps()` and `dump()`, defaulting to `1`
so current output is byte-identical.

**Canonical key ordering stays fixed.** The obligation makes formatting
configurable and ordering canonical — those are different words in the same
sentence. Exposing `sort_keys` would let a caller produce non-canonical output
and break the determinism the same obligation requires, so it is deliberately
not offered.

## IPYNB-EXPORT-001 (SHOULD) — `SAL-IPYNB-OBL-...35A6381D`

> Provide exporter adapter interfaces returning main output plus ancillary
> resources; keep exporter-specific preprocessors and resources outside the core
> parser.

`adapters/__init__.py` contains only a docstring — no interface, no
implementation. This capability is **entirely unimplemented**.

It is `SHOULD`, not `MUST`, and designing an exporter adapter surface is a
product-design task rather than a defect repair: it needs a decided contract for
what an "ancillary resource" is, how collection is reported, and how adapters
register. Inventing that here to close a checkbox would be exactly the
speculative generalization the directive's `principles` forbid.

**Recorded as `missing` with the reason stated, not implemented in this card.**
The second half of its requirement — keeping exporter concerns out of the core
parser — is already satisfied: the core has no notebook-framework dependency.

## RED scenarios

1. `dumps(doc, indent=4)` produces 4-space indentation.
2. `dumps(doc, indent=None)` produces compact output with no newlines.
3. `dumps(doc)` is byte-identical to today's output (default unchanged).
4. Every indent setting still yields canonical key ordering.
5. Every indent setting still preserves cell and output order.
6. Every indent setting round-trips to an equal document.
7. `dump()` accepts the same parameter and writes UTF-8.
8. Determinism byte-compare: repeated writes are byte-identical per setting.
9. Binary MIME payload integrity holds across every indent setting.

## Exact writable product paths

- `src/python/ipynb/src/format_factory/ipynb/codec/writer/writer.py`
- `tests/python/ipynb/test_obligation_writer_contract.py`
- `shared/format-contracts/implementation-evidence/ipynb.yaml`

## Acceptance criteria

- [x] All 9 RED scenarios captured failing where applicable, then passing.
- [x] Default output byte-identical to before the change.
- [x] `sort_keys` NOT exposed; canonical ordering remains non-negotiable.
- [x] Full IPYNB suite green, no regression against 520 passed / 3 failed.
- [x] `ruff` and `mypy` clean.
- [x] IPYNB-WRITE-001 leaves `missing`; IPYNB-EXPORT-001 stays `missing` with
      its reason recorded in the ledger.
