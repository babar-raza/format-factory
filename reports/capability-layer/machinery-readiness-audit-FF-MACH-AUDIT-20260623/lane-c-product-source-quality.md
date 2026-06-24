# Lane C — Product Source Quality Audit
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-C | **Requirement:** REQ-LANE-C

## Format Quality Ratings

| Format | Rating | load/parse | Domain Classes | Serialization | spec_qname | Export Count |
|--------|--------|-----------|----------------|---------------|-----------|--------------|
| FODS (Python) | **GREEN** | parse_fods() → dict | FodsCell/Sheet/Document | write_fods() | All 3 classes | ~30 core |
| NDJSON | **GREEN** | load_ndjson() → list | NdjsonRecord | write_ndjson() | Yes | 116 (12% core, 88% analytics) |
| CSV | **YELLOW** | parse_csv() → dict | Limited | write_csv() | Yes | 86 |
| TSV | **YELLOW** | parse_tsv() → dict | Limited | write_tsv() | Yes | 94 |
| XCF | **ORANGE** | parse_xcf() → dict | XcfImage | No write | Yes | ~12 core |
| PGM | **YELLOW** | parse_pgm() | PgmImage | write_pgm() | Yes | ~40 |
| FODS (.NET) | **GREEN** | FodsDocument.Load() | DOM-backed | Save() | Yes | N/A |
| FODT (.NET) | **GREEN** | FodtDocument (977 LOC) | DOM-backed | Yes | Yes | N/A |
| Netpbm (.NET) | **YELLOW** | NetpbmImage (1914 LOC) | Model-backed | Yes | Partial | N/A |

## Detailed Findings

### FODS Python (GREEN — Baseline)
- 3 production classes: FodsCell (spec_qname="table:table-cell"), FodsSheet ("table:table"), FodsDocument ("office:document")
- Real @property accessors (value, value_type, text, formula, repeated, name, rows, row_count)
- parse_fods() with defusedxml XXE protection, returns neutral model dict
- write_fods() serializes neutral model to FODS XML
- Real load → modify → save workflow

### NDJSON (GREEN — Over-exported)
- load_ndjson() → list[Any], write_ndjson(), append_record(), filter_records()
- 116 exports in __init__.py: 14 core + 90+ analytics
- Analytics ratio: 88% — RC-5 evidence (over-export confirmed)
- Real codec with stdlib json only

### XCF (ORANGE — No Write, Synthetic Layer Names)
- parse_xcf() reads XCF header, property list, layer offsets
- XcfImage dataclass with spec_qname
- xcf_layer_name_list returns SYNTHETIC names (GAP-XCF-LAYER-NAMES tracked)
- No write capability — read-only format parser

### .NET Products
- FodsDocument.cs: 1293 LOC, DOM-backed (XDocument), DtdProcessing.Prohibit security
- FodtDocument: 977 LOC, similar DOM pattern
- NetpbmImage: 1914 LOC, model-backed
- All at baseline_loc_cap (oversized, deadline 2026-09-01)

## Over-Export Analysis (RC-5)
| Format | Total Exports | Core API | Analytics | Ratio |
|--------|--------------|----------|-----------|-------|
| NDJSON | 116 | 14 | 102 | 88% analytics |
| CSV | 86 | ~10 | ~76 | ~88% analytics |
| TSV | 94 | ~10 | ~84 | ~89% analytics |
| XCF | ~12 | ~8 | ~4 | ~33% analytics |
