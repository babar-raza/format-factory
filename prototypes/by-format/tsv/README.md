---
artifact_id: tsv-gate4-evidence-wrapper
artifact_type: gate4_evidence_wrapper
path: prototypes/by-format/tsv/README.md
format_id: tsv
visibility: internal
publish_allowed: false
retrospective: false
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
notes: "Gate 4 evidence wrapper for TSV. Delegates to src/python/tsv/tsv_parser.py."
---

# TSV Gate 4 Evidence Wrapper

**Format:** Tab-Separated Values (TSV)
**Gate:** Gate 4 (Parser Prototype — Evidence Wrapper)
**Evidence type:** EVIDENCE_WRAPPER
**Status:** gate4_passed
**Delegated source:** src/python/tsv/tsv_parser.py

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: tsv
  evidence_type: EVIDENCE_WRAPPER
  delegated_source: src/python/tsv/tsv_parser.py
  delegated_symbols:
    - parse_tsv
    - probe_tsv
    - TsvInputError
    - TsvParseError
  sample_corpus:
    - samples/by-format/tsv/minimal-2x2.tsv
    - samples/by-format/tsv/multi-column.tsv
    - samples/by-format/tsv/single-cell.tsv
    - samples/by-format/tsv/invalid-binary-garbage.tsv
  valid_probe: tsv_gate4_probe.py::probe
  invalid_probe: tsv_gate4_probe.py::probe_invalid
  limitations:
    - Tab delimiter assumed; no auto-detection of other delimiters
    - No write or round-trip at Gate 4
    - Gate 4 scope only
  test_paths:
    - tests/skills/test_tsv_gate4_prototype.py
  source_revision: src/python/tsv/ at HEAD
  compatibility_version: "1.0"
gate_3_corpus: samples/by-format/tsv/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `tsv_gate4_probe.py` | Thin evidence wrapper — no parsing logic |
| `gate4-evidence.yaml` | Gate 4 evidence record |
| `README.md` | This file |
