# Python QName Architecture — Phase 0 Baseline Inventory
Generated: 2026-06-21
Plan: plans/enhanced-qname-python-governed-plan.md

## QName Compliance Matrix

| Format | Archetype | Classes | With QName | spec/ | Compat/ | Status |
|--------|-----------|---------|-----------|-------|---------|--------|
| fods | XML ODF Spreadsheet | 26 | 21 | 15 | 3 | PARTIAL — Compat exists, no office/ class |
| fodt | XML ODF Text | 15 | 11 | 8 | 0 | PARTIAL — spec exists, Compat MISSING |
| ods | XML ODF Spreadsheet | 11 | 3 | 3 | 0 | PARTIAL — spec stubs only |
| abw | XML Document | 2 | 0 | 0 | 0 | NOT_STARTED |
| csv | Tabular | 5 | 0 | 0 | 0 | NOT_STARTED |
| dif | Tabular | 5 | 0 | 0 | 0 | NOT_STARTED |
| fodg | XML ODF Drawing | 2 | 0 | 0 | 0 | NOT_STARTED |
| fodp | XML ODF Presentation | 2 | 0 | 0 | 0 | NOT_STARTED |
| gnumeric | XML Spreadsheet | 2 | 0 | 0 | 0 | NOT_STARTED |
| ndjson | Text/Records | 2 | 0 | 0 | 0 | NOT_STARTED |
| odt | XML ODF Text | 7 | 0 | 0 | 0 | NOT_STARTED |
| pbm | Binary/Image | 6 | 0 | 0 | 0 | NOT_STARTED |
| pgm | Binary/Image | 6 | 0 | 0 | 0 | NOT_STARTED |
| ppm | Binary/Image | 6 | 0 | 0 | 0 | NOT_STARTED |
| qoi | Binary/Image | 7 | 0 | 0 | 0 | NOT_STARTED |
| sylk | Tabular | 6 | 0 | 0 | 0 | NOT_STARTED |
| toml | Text/Tabular | 4 | 0 | 0 | 0 | NOT_STARTED |
| tsv | Tabular | 4 | 0 | 0 | 0 | NOT_STARTED |
| xcf | Binary/Image | 6 | 0 | 0 | 0 | NOT_STARTED |
| zst | Binary/Archive | 7 | 0 | 0 | 0 | NOT_STARTED |

## Analytics Overflow Files (Burn-Down Queue)

| File | LOC | Functions | Priority |
|------|-----|-----------|----------|
| fodg/fodg_analytics.py | 4915 | 772 | P3 (Phase 4) |
| xcf/xcf_analytics.py | 5725 | 820 | P3 (Phase 7) |
| zst/zst_analytics.py | 5513 | 848 | P3 (Phase 7) |
| fodt/fodt_analytics.py | 996 | 92 | P2 (Phase 2) |
| abw/abw_analytics.py | 1021 | 98 | P2 (Phase 3) |
| fods/fods_analytics.py | 1030 | 24 | P1 (Phase 2) |
| dif/dif_analytics.py | 1024 | 66 | P4 (Phase 6) |
| csv/csv_analytics.py | 968 | 65 | P4 (Phase 6) |

Note: ZST/XCF/FODG analytics rotation SUSPENDED (per MEMORY). No new functions.
Burn-down governed by cap: current files are at cap — no new additions allowed.

## SAL Fact Availability

| Format | Facts Available | Notes |
|--------|----------------|-------|
| fods | 4987 | sal-facts-fods.json (FACT-FODS-NNN IDs) |
| fodt | (check) | sal-facts-fodt.json |
| abw | 0 | sal-facts-abw.json is empty — structural QNames needed |
| csv | (check) | available |
| All others | (check) | files exist, counts TBD |

## Execution Priority (from plan)

Phase 1: Reviewer skill (tools/review/python_qname_reviewer.py)
Phase 2: FODT Compat/ layer
Phase 3: ABW spec classes + Compat
Phase 4+: FODG, FODP, ODS, ODT, Tabular, Binary formats
