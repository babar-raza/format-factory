# Repository Inventory
# Format Factory — Expert Manual System Review
# Phase 1 output — Generated: 2026-06-25

## Summary

| Dimension | Count |
|-----------|-------|
| .NET projects | 10 |
| Python packages | 20 |
| Registered formats | 25 |
| Governance validators | 50 |
| Skills registered | 65 |
| Gap ledger entries | 1,132 |
| QName registry files | 20 |
| SAL spec-cache formats with facts | 2 (FODS, FODT) |
| SAL spec-cache formats broken | 10 |
| Total test files (Python) | 1,000+ |
| Total test files (.NET) | 140+ |

## Source Directory Summary

### src/net/ — .NET Commercial Products

| Project | LOC | Test Files | Gate | Notes |
|---------|-----|-----------|------|-------|
| FormatFactory.Fods | 3,569 | 71 | G11-G APPROVED | Full DOM, 6 exporters |
| FormatFactory.Fodt | 2,543 | 64 | G11-G APPROVED | Full DOM, 5 exporters |
| FormatFactory.Netpbm | ~1,940 | 56 | In Progress | Transforms/filters/analyzer |
| FormatFactory.Csv | 380 | 6 | In Progress | Thin parser |
| FormatFactory.Tsv | 410 | 6 | In Progress | Has CSV exporter |
| FormatFactory.Ndjson | 419 | 6 | In Progress | Has CSV exporter |
| FormatFactory.Zst | 233 | 2 | In Progress | Probe-only (no decompression) |
| FormatFactory.Html | 118 | 1 | N/A | Target writer utility only |
| FormatFactory.Markdown | 84 | 1 | N/A | Target writer utility only |
| FormatFactory.Txt | 70 | 1 | N/A | Target writer utility only |

### src/python/ — Python FOSS Packages

| Package | Key LOC | Write | Export | Compat Facades | Classification |
|---------|---------|-------|--------|----------------|----------------|
| fods | Large | YES | YES | 12 | LOAD_EDIT_SAVE_POC |
| fodt | Large | YES | YES | 10 | LOAD_EDIT_SAVE_POC |
| abw | Medium | YES | YES | 2 | PARSER_WITH_MODEL |
| csv | Medium | YES | — | 3 | PARSER_WITH_MODEL |
| dif | Medium | YES | YES(html) | 3 | THIN_PARSER |
| fodg | Large | YES | YES(txt/json) | 2 | LOAD_EDIT_SAVE_POC |
| fodp | Medium | NO | YES(txt/csv/json) | 2 | READ_ONLY |
| gnumeric | 760 | YES | YES(csv/json) | 0 | PARSER_WITH_MODEL |
| ndjson | 570+ | YES | — | 1 | PARSER_WITH_MODEL |
| ods | Medium | YES | YES(csv) | 0 | PARSER_WITH_MODEL |
| odt | Medium | YES | — | 0 | PARSER_WITH_MODEL |
| pbm | Medium | YES | YES(pgm/ppm) | 0 | PARSER_WITH_MODEL |
| pgm | Medium | YES | YES(ppm) | 0 | PARSER_WITH_MODEL |
| ppm | Medium | YES | — | 0 | THIN_PARSER |
| qoi | Medium | YES(encoder) | — | 0 | PARSER_WITH_MODEL |
| sylk | 741 | YES(file-based) | YES(csv) | 3 | PARSER_WITH_MODEL |
| toml | 728 | YES | — | 0 | PARSER_WITH_MODEL |
| tsv | Medium | YES | — | 3 | PARSER_WITH_MODEL |
| xcf | 1,272 | NO | — | 0 | PARSER_ONLY |
| zst | 1,549 | NO | — | 0 | PARSER_WITH_MODEL |

## Registry Files

| File | Contents |
|------|---------|
| registry/format-registry.yaml | 25 formats, scored, legal categories, gates |
| registry/parity-matrix.yaml | Spec parity status per format |
| registry/source-structure-baseline.json | LOC caps, known violations |
| registry/known-failure-ledger.yaml | Pre-existing failures catalog |
| shared/qname-registry/*.yaml | 20 format-specific YAML files |
| product-capability-matrix/poc-targets.yaml | Capability matrix PASS/FAIL per format |

## Autonomous Machinery

| File | LOC | Purpose |
|------|-----|---------|
| tools/supervisor/autonomous_cycle.py | 2,406 | Main sprint execution |
| tools/supervisor/governance_validators.py | 3,181 | 50 validators (V1-V68) |
| tools/supervisor/sprint_executor.py | Large | Sprint runner |
| tools/supervisor/grade_declared_work.py | Large | LLM-based grader |
| tools/supervisor/check_continuation.py | ~500 | Continue/stop decision |
| .supervisor/skill-registry.yaml | — | 65 skills registered |

## Key Authority Files

| File | Authority | Known Issues |
|------|-----------|-------------|
| .local/spec-cache/sal-facts-fods.json | AUTHORITATIVE | 4,988 facts — CHAIN_INTACT |
| .local/spec-cache/sal-facts-fodt.json | AUTHORITATIVE | 4,936 facts — CHAIN_INTACT |
| reports/capability-layer/gap-ledger.json | ADVISORY | 1,132 gaps; 1,131 with "unknown" category |
| reports/capability-layer/unified-capability-map.json | ADVISORY | Generated from broken gap ledger |
