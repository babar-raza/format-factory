# Oracle Layer Wave 6 Backfill Sprint Plan
# source_task: TC-ORC-007
# parent_mission: FORMAT-FACTORY-ORACLE-LAYER-HARDENING-001 (master-plan §74)
# gap_ledger_refs: GAP-ORC-BACKFILL-A, GAP-ORC-BACKFILL-B, GAP-ORC-BACKFILL-C, GAP-ORC-BACKFILL-D
# created: 2026-06-26
# status: PLANNING — not yet scheduled

---

## Mission Statement

Wave 6 completes the oracle layer maturity advance from Level 3 (reusable machinery exists)
to Level 4 (all formats have oracle packages). As of Wave 5 close:

- 3 formats have oracle packages + execution: CSV, ZST, FODS (7/8 PASS)
- 18 formats are at OBLIGATION_CREATED_BACKFILL_REQUIRED
- 4 formats are pipeline-only (ora, pam, xpm, zpaq) — no product implementation

This plan covers the 18 backfill formats grouped into 4 sprint batches.

---

## Template Files (do not modify)

All new oracle packages must use the existing Wave 3 templates as starting points:

- **Cells family:** `oracle/formats/csv/oracle-package.yaml` (SPEC_NORMATIVE, RFC 4180)
- **ODF family:** `oracle/formats/fods/oracle-package.yaml` (SPEC_NORMATIVE, ODF 1.3)
- **Archive/binary family:** `oracle/formats/zst/oracle-package.yaml` (AUTH_REF_VECTOR, RFC 8878)

Each new package must pass `tools/oracle/validate_oracle_obligations.py` obligation check
and produce verdicts via `tools/oracle/execute_oracle.py --format <format_id> --all`.

---

## Batch A — Cells Family (Priority: HIGH)

**Gap ledger entry:** GAP-ORC-BACKFILL-A
**Formats:** gnumeric, ods, dif, sylk
**Estimated cases per format:** 5 (3 valid + 1 invalid + 1 roundtrip)
**Authority sources:**

| Format | Authority Class | Source |
|--------|----------------|--------|
| gnumeric | AUTHORITATIVE_REFERENCE_VECTOR | gnumeric.org Workbook specification |
| ods | SPEC_NORMATIVE | ODF 1.3 OASIS §9 Spreadsheet |
| dif | AUTHORITATIVE_REFERENCE_VECTOR | VisiCalc/Lotus DIF format reference |
| sylk | AUTHORITATIVE_REFERENCE_VECTOR | Multiplan SYLK format specification |

**Python executor functions needed:**
- `execute_gnumeric_valid_case(case, pkg)` — reads GnumericDocument, checks sheet_count/cell_count
- `execute_ods_valid_case(case, pkg)` — reads OdsDocument, checks sheet/row/cell props
- `execute_dif_valid_case(case, pkg)` — reads DifDocument, checks vectors/tuples/row counts
- `execute_sylk_valid_case(case, pkg)` — reads SylkDocument, checks cell count/row count

**Estimated sprint:** 1 sprint (all 4 formats share tabular model pattern)

---

## Batch B — Words/Drawing Family (Priority: MEDIUM)

**Gap ledger entry:** GAP-ORC-BACKFILL-B
**Formats:** abw, fodt, fodg, fodp, odt
**Estimated cases per format:** 5 (2 valid + 2 invalid + 1 roundtrip)
**Authority sources:**

| Format | Authority Class | Source |
|--------|----------------|--------|
| abw | SPEC_NORMATIVE | AbiWord DTD (abiword.org) |
| fodt | SPEC_NORMATIVE | ODF 1.3 OASIS §3 Text Documents |
| fodg | SPEC_NORMATIVE | ODF 1.3 OASIS §10 Drawing |
| fodp | SPEC_NORMATIVE | ODF 1.3 OASIS §9 Presentation |
| odt | SPEC_NORMATIVE | ODF 1.3 OASIS §3 Text Documents |

**Python executor functions needed:**
- `execute_abw_valid_case(case, pkg)` — reads AbwDocument, checks paragraph_count/section_count
- `execute_fodt_valid_case(case, pkg)` — reads neutral_model, checks paragraph/heading counts
- `execute_fodg_valid_case(case, pkg)` — reads load(), checks page_count/shape_count
- `execute_fodp_valid_case(case, pkg)` — reads load(), checks page_count/slide_count
- `execute_odt_valid_case(case, pkg)` — reads OdtParser, checks paragraph_count

**Note:** FODT has an active acquisition oracle at Gate 6 — check acquisition reports before defining conflicting oracle cases.

**Estimated sprint:** 2 sprints (words and drawing are different parsers)

---

## Batch C — Imaging Family (Priority: LOW)

**Gap ledger entry:** GAP-ORC-BACKFILL-C
**Formats:** xcf, pbm, pgm, ppm, qoi
**Estimated cases per format:** 4 (2 valid + 1 invalid + 1 roundtrip)
**Authority sources:**

| Format | Authority Class | Source |
|--------|----------------|--------|
| xcf | AUTHORITATIVE_REFERENCE_VECTOR | GIMP XCF source (git.gnome.org/gimp) |
| pbm | SPEC_NORMATIVE | Netpbm manual (netpbm.sourceforge.net) |
| pgm | SPEC_NORMATIVE | Netpbm manual (netpbm.sourceforge.net) |
| ppm | SPEC_NORMATIVE | Netpbm manual (netpbm.sourceforge.net) |
| qoi | SPEC_NORMATIVE | qoiformat.org — The QOI specification |

**Python executor functions needed:**
- `execute_xcf_valid_case(case, pkg)` — reads XcfImage, checks width/height/layer_count
- `execute_pbm_valid_case(case, pkg)` — reads PbmImage, checks width/height/max_value=1
- `execute_pgm_valid_case(case, pkg)` — reads PgmImage, checks width/height/max_value
- `execute_ppm_valid_case(case, pkg)` — reads PpmImage, checks width/height/channels
- `execute_qoi_valid_case(case, pkg)` — reads QoiImage, checks width/height/colorspace

**Estimated sprint:** 2 sprints (imaging executors need pixel-level comparison)

---

## Batch D — Data Family (Priority: HIGH)

**Gap ledger entry:** GAP-ORC-BACKFILL-D
**Formats:** toml, tsv, ndjson
**Estimated cases per format:** 5 (3 valid + 1 invalid + 1 roundtrip)
**Authority sources:**

| Format | Authority Class | Source |
|--------|----------------|--------|
| toml | SPEC_NORMATIVE | toml.io v1.0 specification |
| tsv | AUTHORITATIVE_REFERENCE_VECTOR | IANA text/tab-separated-values |
| ndjson | SPEC_NORMATIVE | ndjson.org — NDJSON specification |

**Python executor functions needed:**
- `execute_toml_valid_case(case, pkg)` — reads TomlDocument, checks key_count/section_count
- `execute_tsv_valid_case(case, pkg)` — reads TsvDocument, checks row_count/column_count/headers
- `execute_ndjson_valid_case(case, pkg)` — reads NdjsonDocument, checks record_count/field_count

**Estimated sprint:** 1 sprint (data formats share CSV-like model pattern)

---

## Execution Order

| Sprint | Batch | Formats | Reason |
|--------|-------|---------|--------|
| Wave6-S1 | D (Data) | toml, tsv, ndjson | Simplest; shares CSV executor pattern |
| Wave6-S2 | A (Cells) | gnumeric, ods, dif, sylk | High-priority gate-critical formats |
| Wave6-S3 | B1 (Words) | abw, fodt, odt | Words family first |
| Wave6-S4 | B2 (Drawing) | fodg, fodp | Drawing family |
| Wave6-S5 | C (Imaging) | pbm, pgm, ppm, qoi, xcf | Lowest priority, most complex comparator |

---

## Acceptance Criteria (Wave 6 Complete)

For each format:
- [ ] `oracle/formats/{format}/oracle-package.yaml` exists with ≥3 cases
- [ ] `tools/oracle/execute_oracle.py --format {format} --all` produces ≥ 1 PASS
- [ ] `oracle/formats/{format}/reports/oracle-run-summary.json` shows `verdict != INVALID_ORACLE`
- [ ] `V82 validate_oracle_obligations()` still returns PASS (24/24)

**Oracle Level 4 Gate:** All 22 active formats (excluding 4 pipeline-only) have oracle packages
with at least 1 executed PASS verdict. Assessed in `oracle/oracle-layer-inventory.yaml`.

---

## Dependencies

- `tools/oracle/execute_oracle.py` — extend with new format handlers per batch
- `oracle/formats/{format}/oracle-package.yaml` — create from template (do not modify templates)
- `reports/capability-layer/gap-ledger.json` — update GAP-ORC-BACKFILL-* status as CLOSED
- `oracle/reports/oracle-coverage-report.json` — update format_coverage entries from OBLIGATION_CREATED → CASES_DEFINED_AND_PASSING
- `oracle/oracle-layer-inventory.yaml` — update maturity from Level 3 → Level 4 when all batches done

---

## Anti-Overclaim Rules

1. Do NOT advance any format from OBLIGATION_CREATED to CASES_DEFINED until the oracle package is committed AND at least 1 case executes as PASS.
2. Do NOT count synthetic test assertions as oracle execution evidence.
3. Do NOT modify existing CSV/ZST/FODS oracle packages when adding new format handlers.
4. Authority class must be explicitly set — do not default to SPEC_NORMATIVE without verifying the cited source exists.
