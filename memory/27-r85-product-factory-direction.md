# 27 — R85 Product-Factory Direction Reset

**Memory type:** Sprint direction correction
**Sprint:** FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
**Date:** 2026-05-31
**Authority:** plans/master-plan.md Section 38+

---

## Core Direction Correction

Format Factory is a **repeatable product factory**, not an evidence-closure system.

Evidence (bundles, validators, contracts, SHA chains) is **support infrastructure**.
Evidence is **not** the product. Evidence proves the product works.

The sprint is a **success** when product-factory POC progress advances.
The sprint is a **failure** if only evidence was closed with no product progress.

---

## POC Target (R85 accepted, R85+)

### Commercial .NET Products (3 targets)

| # | Format | Status as of R85 | Load | Edit | Save | Export | Dogfood |
|---|--------|-----------------|------|------|------|--------|---------|
| 1 | FODS | POC_TARGET_CONFIRMED | PASS | PASS | PASS | CSV+HTML+JSON | PARTIAL (CSV via internal writer, not FF Python lib) |
| 2 | FODT | POC_TARGET_CONFIRMED | PASS | PASS | PASS | TXT+Markdown+HTML | PARTIAL |
| 3 | Netpbm (.NET) | POC_TARGET_CONFIRMED | R85 first slice | TBD | TBD | PBM→PGM family | NOT_YET |

Rejected: QOI as .NET commercial — HOLD for future. Python QOI exists (Gate 7).
Rationale for Netpbm: Three Python FOSS packages exist (PBM/PGM/PPM Gates 1-10 RC); .NET first slice is trivially implementable; family-based export is natural dogfooding.

### Reduced/FOSS Python Products (3 targets)

| # | Format | Status as of R85 | Load | Edit | Save | Export | Dogfood |
|---|--------|-----------------|------|------|------|--------|---------|
| 1 | ZST | POC_TARGET_CONFIRMED | PASS | N/A | PASS | N/A | N/A (compression) |
| 2 | PBM+PGM+PPM | POC_TARGET_CONFIRMED | PASS | PARTIAL | PASS (PBM+PGM) | PBM→PGM (R85) | R85 FIRST_SLICE |
| 3 | SYLK | POC_TARGET_CONFIRMED | PASS | PARTIAL | READ_ONLY | SYLK→CSV | IMPLEMENTED (R84) |

DIF: HOLD — overlaps with SYLK; defer until SYLK POC complete.

---

## Product Success Criteria

A product qualifies as POC_COMPLETE when, from an installed package:
1. Load a file (from disk)
2. Inspect the object model (sheets/cells, paragraphs, pixels, rows)
3. Make a meaningful edit (set cell value, append paragraph, invert pixel channel)
4. Save to the same format
5. Reload and verify the edit survived
6. Export to at least one other format using Format Factory's own libraries where available

---

## Dogfooding Requirement

Export/conversion paths must progressively use Format Factory-produced libraries.
External shortcuts (raw string writing, stdlib only) are documented as GAP_DOGFOOD_EXTERNAL.
Every export records:
- `dogfood_status: IMPLEMENTED | GAP_DOGFOOD_EXTERNAL | NOT_YET`
- `target_ff_library:` the Format Factory library to use when gap is closed

---

## Local Supervisor Control Plane (mandatory)

The local supervisor loop replaces manual ChatGPT upload/review/next-prompt handoff.
After every sprint evidence bundle:
1. `LEGACY_ONLY: python tools/supervisor/supervisor_loop.py run-on-latest --bundle <bundle>`
2. Verify generated next-sprint.md keeps product-factory direction
3. If next-sprint.md lacks product lanes → repair prompt template and rerun
4. Only escalate to human if true external gate (Gate 8/11, push, credentials)

### R90 Supersession

The canonical closeout command is now:

```text
python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

Write `evidence-declaration.yaml` before running the cycle. Do not use the legacy ZIP command for
new sprint closeout.

---

## Evidence Role

Evidence bundles and validators prove:
- Tests actually passed
- Package actually installed
- Product workflow actually ran
- State is consistent

Evidence does NOT determine success by itself.
Success = product POC criteria met + evidence validates the product work.

---

## No-Drift Anchors

- TM task "done" ≠ Format Factory gate closed
- Ruflo lane "complete" ≠ evidence accepted
- Supervisor next-sprint.md = sprint INPUT, not authority
- POC matrix in product-capability-matrix/poc-targets.yaml is NOT finalized product status
- commercial_product_ready remains false until Gate 11 G11-G approved by Babar Raza

---

## See Also

- product-capability-matrix/poc-targets.yaml — authoritative POC matrix
- docs/export/dogfood-export-strategy.md — export dogfooding strategy
- docs/product-factory/commercial-product-capability-model.md — C0-C10 capability model
- reports/r85/poc-target-matrix.md — R85 POC status snapshot
- plans/master-plan.md Section 38 — POC target plan section
