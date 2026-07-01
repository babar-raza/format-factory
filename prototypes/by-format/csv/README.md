---
artifact_id: csv-gate4-evidence-wrapper
artifact_type: gate4_evidence_wrapper
path: prototypes/by-format/csv/README.md
format_id: csv
visibility: internal
publish_allowed: false
retrospective: false
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
open_source_allowed: false
commercial_allowed: false
notes: "Gate 4 evidence wrapper for CSV. Delegates to src/python/csv/csv_parser.py."
---

# CSV Gate 4 Evidence Wrapper

**Format:** Comma-Separated Values (CSV)
**Gate:** Gate 4 (Parser Prototype — Evidence Wrapper)
**Evidence type:** EVIDENCE_WRAPPER
**Status:** gate4_passed
**Delegated source:** src/python/csv/csv_parser.py

---

## IMPORTANT — Wrapper Scope

This directory contains a **thin evidence wrapper** for Gate 4 CSV traceability.

- This is NOT an implementation. All parsing is in `src/python/csv/`.
- This wrapper delegates to `csv_parser.parse_csv()` and `csv_parser.probe_csv()`.
- It proves that a valid sample parses successfully and missing input is handled.
- It fails if `csv_parser`'s required symbols are removed (API drift detection).
- Gate 4 does NOT claim production quality or release readiness.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: csv
  evidence_type: EVIDENCE_WRAPPER
  delegated_source: src/python/csv/csv_parser.py
  delegated_symbols:
    - parse_csv
    - probe_csv
    - CsvInputError
    - CsvParseError
  sample_corpus:
    - samples/by-format/csv/minimal-2x2.csv
    - samples/by-format/csv/quoted-fields.csv
    - samples/by-format/csv/single-cell.csv
    - samples/by-format/csv/invalid-unterminated-quote.csv
  valid_probe: csv_gate4_probe.py::probe
  invalid_probe: csv_gate4_probe.py::probe_invalid
  limitations:
    - Parse-only wrapper; no writer or round-trip at Gate 4
    - Delegated source handles unterminated-quote samples permissively
    - No streaming mode; full file loaded to memory
    - Gate 4 scope only — does not imply production API readiness
  test_paths:
    - tests/skills/test_csv_gate4_prototype.py
  source_revision: src/python/csv/ at HEAD
  compatibility_version: "1.0"
gate_3_corpus: samples/by-format/csv/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `csv_gate4_probe.py` | Thin evidence wrapper — no parsing logic |
| `gate4-evidence.yaml` | Gate 4 evidence record |
| `README.md` | This file |

## Usage

```bash
# Probe a valid sample
python prototypes/by-format/csv/csv_gate4_probe.py samples/by-format/csv/minimal-2x2.csv

# Compatibility check
python prototypes/by-format/csv/csv_gate4_probe.py
```

## Gate 3 Corpus

- `samples/by-format/csv/minimal-2x2.csv` — 2 rows, 2 columns
- `samples/by-format/csv/quoted-fields.csv` — RFC 4180 quoted fields
- `samples/by-format/csv/single-cell.csv` — minimal single value
- `samples/by-format/csv/invalid-unterminated-quote.csv` — invalid input (rejection proof)
