# SAL Integration Matrix
**Mission:** spec-auth-inv-20260625-001
**Date:** 2026-06-25

## Format × SAL Integration Status

| Format | SAL Facts | QName Registry | RCAL Gap Entries | V13 Gate | Provenance |
|--------|-----------|----------------|-----------------|----------|------------|
| fods | 4987 | fods.yaml (VERIFIED) | GAP-FODS-* | PASSES | WORKBENCH_VERIFIED |
| fodt | 4933 | fodt.yaml (VERIFIED) | GAP-FODT-* | PASSES | WORKBENCH_VERIFIED |
| fodp | 1066 | fodp.yaml (VERIFIED) | GAP-FODP-* | PASSES | WORKBENCH_VERIFIED |
| fodg | 1066 | fodg.yaml (VERIFIED) | GAP-FODG-* | PASSES | WORKBENCH_VERIFIED |
| ods | 1066 | ods.yaml (VERIFIED) | GAP-ODS-* | PASSES | WORKBENCH_VERIFIED |
| odt | 1066 | odt.yaml (VERIFIED) | GAP-ODT-* | PASSES | WORKBENCH_VERIFIED |
| zst | 94 | zst.yaml (VERIFIED) | GAP-ZST-* | PASSES | MANUAL_IETF |
| csv | 2 | csv.yaml (VERIFIED) | GAP-CSV-* | PARTIAL | MANUAL_STUB |
| ndjson | 2 | ndjson.yaml (VERIFIED) | GAP-NDJSON-* | PARTIAL | MANUAL_STUB |
| pbm | 2 | pbm.yaml (VERIFIED) | GAP-PBM-* | PARTIAL | MANUAL_STUB |
| pgm | 2 | pgm.yaml (VERIFIED) | GAP-PGM-* | PARTIAL | MANUAL_STUB |
| ppm | 2 | ppm.yaml (VERIFIED) | GAP-PPM-* | PARTIAL | MANUAL_STUB |
| tsv | 2 | tsv.yaml (VERIFIED) | GAP-TSV-* | PARTIAL | MANUAL_STUB |
| gnumeric | 0 | gnumeric.yaml (VERIFIED) | GAP-GNUMERIC-* | BROKEN | NONE |
| abw | 0 | abw.yaml (VERIFIED) | GAP-ABW-* | BROKEN | NONE |
| qoi | 0 | qoi.yaml (VERIFIED) | GAP-QOI-* | BROKEN | NONE |
| xcf | 0 | xcf.yaml (VERIFIED) | GAP-XCF-* | BROKEN | NONE |
| dif | 0 | dif.yaml (VERIFIED) | GAP-DIF-* | BROKEN | NONE |
| sylk | 0 | sylk.yaml (VERIFIED) | GAP-SYLK-* | BROKEN | NONE |
| toml | 0 | toml.yaml (VERIFIED) | GAP-TOML-* | BROKEN | NONE |

## V13 Gate Status

V13 (`validate_spec_fact_refs_wired`) has a known degradation path:
- On ImportError (lxml/spec tools not installed), it demotes to WARN and does not block
- This means the gate is **only enforceable** when the spec toolchain is installed
- RC-003: V13 should log the ImportError but still fail the sprint with a clear error message

## Chain Status Summary

- **CHAIN_INTACT:** FODS, FODT, FODP, FODG, ODS, ODT, ZST (7 formats — ODF + ZST)
- **CHAIN_PARTIAL (stub facts only):** CSV, NDJSON, PBM, PGM, PPM, TSV (6 formats)
- **CHAIN_BROKEN_AT_SAL:** Gnumeric, ABW, QOI, XCF, DIF, SYLK, TOML (7 formats)
