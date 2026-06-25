# Live Read-Only Run Plan
# Format Factory — Expert Manual System Review
# Phase 8 output — Generated: 2026-06-25

## Purpose

Full review of all 30 products (10 .NET + 20 Python) using verified rubric.
This is Phase D — the complete expert assessment pass.

## Scope

All files in `src/`, all test files in `tests/`, all authority registries.
No source modifications. All findings go to phase-d-live-run/ reports.

## .NET Product Review Sequence

| Order | Product | Expected Band | Key Focus |
|-------|---------|--------------|-----------|
| 1 | FODS | Commercial candidate | ODS exporter PROTOTYPE vs PASS |
| 2 | FODT | Commercial candidate | No table traversal in public API |
| 3 | NetPBM | Commercial candidate | No export story |
| 4 | CSV | POC candidate | No edit API |
| 5 | TSV | POC candidate | Minimal tests |
| 6 | NDJSON | POC candidate | Minimal tests |
| 7 | ZST | Not a product | No decompression |
| 8 | HTML | N/A (utility) | Not a format product |
| 9 | Markdown | N/A (utility) | Not a format product |
| 10 | TXT | N/A (utility) | Not a format product |

## Python Package Review Sequence

| Order | Package | Expected Level | Key Focus |
|-------|---------|--------------|-----------|
| 1 | FODS | PY-4 | Compat facade quality |
| 2 | FODT | PY-4 | neutral_model.py healed |
| 3 | GNUMERIC | PY-3 | Dict model clarity |
| 4 | SYLK | PY-3 | File-based API design |
| 5 | TOML | PY-3 | Config round-trip |
| 6 | NDJSON | PY-3 | Analytics ratio |
| 7 | ZST | PY-3 | Core vs analytics |
| 8 | XCF | PY-2 | Layer names real |
| 9 | PBM | PY-3 | Write + convert |
| 10 | PGM | PY-3 | Write + convert |
| 11 | PPM | PY-3 | Write only |
| 12 | QOI | PY-3 | Encoder quality |
| 13 | ABW | PY-3 | Append paragraph |
| 14 | ODS | PY-3 | write_ods quality |
| 15 | ODT | PY-3 | odt_writer quality |
| 16 | CSV | PY-3 | Name conflict handling |
| 17 | TSV | PY-3 | write_tsv API |
| 18 | DIF | PY-2-3 | Thin exporter |
| 19 | FODG | PY-3 | Large codec |
| 20 | FODP | PY-2 | No write_fodp |

## Layer Review Sequence

| Order | Layer | Expected Maturity | Key Focus |
|-------|-------|-------------------|-----------|
| 1 | Gap Ledger | L1 | 99.9% unknown category |
| 2 | SAL | L4/L0 | Chain broken for 10 formats |
| 3 | Evidence | L3 | LLM grader dependency |
| 4 | Supervisor | L3 | LOC violations; dispatcher stubs |
| 5 | Skills | L2 | Empty implementation_paths |
| 6 | Governance | L4 | LOC self-violation; 50 validators |
| 7 | Registries | L3-L4 | PASS claims vs source |

## Review Data Sources

For each .NET product review:
- Read: `src/net/{format}/*.cs` (parser, model, writer, exporters)
- Read: `tests/net/{format}/*.cs` (spot-check test names)
- Read: `product-capability-matrix/poc-targets.yaml` (claims)
- Check: `registry/format-registry.yaml` (gate status)

For each Python package review:
- Read: `src/python/{format}/__init__.py`, `*_parser.py`, `*_codec.py`, `models.py`
- Read: `tests/python/{format}/` (file count and names)
- Check: `shared/qname-registry/{format}.yaml` (spec_qname compliance)
- Check: `product-capability-matrix/poc-targets.yaml` (claims)

## Output Format

Each product produces a JSON score block in `phase-d-live-run/dotnet-scored-matrix.json`
or `phase-d-live-run/python-scored-matrix.json`:

```json
{
  "format": "FODS",
  "scores": {
    "api_design": 4,
    "architecture": 4,
    "object_model": 4,
    "error_handling": 3,
    "roundtrip": 3,
    "export_dogfood": 4,
    "tests": 4,
    "polish": 3
  },
  "total": 3.6,
  "band": "COMMERCIAL_CANDIDATE_WITH_KNOWN_GAPS",
  "key_gaps": ["PDF_LATIN1_ONLY", "ODS_PROTOTYPE_VS_PASS"]
}
```
