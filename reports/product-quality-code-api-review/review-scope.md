# Product Quality Review — Scope

## Products Under Review

### .NET Commercial Products (src/net/)
| Package | Namespace | Source Path |
|---------|-----------|-------------|
| FormatFactory.Fods | FormatFactory.Fods | src/net/fods/ |
| FormatFactory.Fodt | FormatFactory.Fodt | src/net/fodt/ |
| FormatFactory.Netpbm | FormatFactory.Netpbm | src/net/netpbm/ |
| FormatFactory.Ndjson | FormatFactory.Ndjson | src/net/ndjson/ |
| FormatFactory.Csv | FormatFactory.Csv | src/net/csv/ |
| FormatFactory.Tsv | FormatFactory.Tsv | src/net/tsv/ |
| FormatFactory.Zst | FormatFactory.Zst | src/net/zst/ |
| FormatFactory.Html | FormatFactory.Html | src/net/html/ |
| FormatFactory.Markdown | FormatFactory.Markdown | src/net/markdown/ |
| FormatFactory.Txt | FormatFactory.Txt | src/net/txt/ |

### Python FOSS Products (src/python/)
| Package Name | Format | Source Path |
|-------------|--------|-------------|
| format-factory-fods | FODS | src/python/fods/ |
| format-factory-fodt | FODT | src/python/fodt/ |
| format-factory-ods | ODS | src/python/ods/ |
| format-factory-odt | ODT | src/python/odt/ |
| format-factory-abw | ABW | src/python/abw/ |
| format-factory-csv | CSV | src/python/csv/ |
| format-factory-tsv | TSV | src/python/tsv/ |
| format-factory-dif | DIF | src/python/dif/ |
| format-factory-gnumeric | Gnumeric | src/python/gnumeric/ |
| format-factory-ndjson | NDJSON | src/python/ndjson/ |
| format-factory-toml | TOML | src/python/toml/ |
| format-factory-sylk | SYLK | src/python/sylk/ |
| format-factory-pbm | PBM | src/python/pbm/ |
| format-factory-pgm | PGM | src/python/pgm/ |
| format-factory-ppm | PPM | src/python/ppm/ |
| format-factory-qoi | QOI | src/python/qoi/ |
| format-factory-xcf | XCF | src/python/xcf/ |
| format-factory-zst | ZST | src/python/zst/ |
| format-factory-fodg | FODG | src/python/fodg/ |
| format-factory-fodp | FODP | src/python/fodp/ |

## Review Dimensions

For every product:
1. Public API quality (naming, discoverability, overloads, consistency)
2. Class segregation (parser/model/writer/exporter separation)
3. Object model depth (domain-specific types vs raw dicts/strings)
4. Feature availability (load/edit/save/export — FA-0 to FA-5)
5. Feature complexity (implementation depth — C0 to C5)
6. Feature comprehensiveness (format coverage — FC-0 to FC-5)
7. Error handling quality
8. Test meaningfulness (TQ-0 to TQ-5)
9. Examples and documentation quality
10. Packaging and import readiness
11. Commercial/FOSS readiness scoring (0–5)
12. Product claim vs. reality verification

## Out of Scope for This Sprint

- Governance validators (supervisor infrastructure)
- Spec/Compat architecture markers (spec stubs — reviewed but not fixed)
- Capability routing, gap ledger, SAL chains (automation infrastructure)
- Any MCP or GhidraMCP tooling
- Gate 8 or Gate 11 approval
- Commercial release authorization

## Deliverables

~47 files under `reports/product-quality-code-api-review/` covering:
- Phase 0: Preflight (7 files)
- Phase 1: Product inventory (4 files)
- Phase 2-5: API/architecture/feature review plans (9 files)
- Phase 6-7: .NET and Python review plans (6 files)
- Phase 8-11: Test/docs/claims/problem matrix (7 files)
- Phase 12: Execution phase design (5 files)
- Phase 13: Scoring rubrics (11 files)
- Phase 14: Master plan + risk register (6 files)
- Phase 15: Validation log (1 file)
