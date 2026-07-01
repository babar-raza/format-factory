---
artifact_id: ndjson-gate4-evidence-wrapper
artifact_type: gate4_evidence_wrapper
path: prototypes/by-format/ndjson/README.md
format_id: ndjson
visibility: internal
publish_allowed: false
retrospective: true
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
notes: >
  Gate 4 evidence wrapper for NDJSON — RETROSPECTIVE. Gate 4 was never formally
  recorded despite full production implementation existing in src/python/ndjson/.
  This wrapper reconstructs evidence from existing source + samples.
---

# NDJSON Gate 4 Evidence Wrapper (RETROSPECTIVE)

**Format:** Newline-Delimited JSON (NDJSON / JSONL)
**Gate:** Gate 4 (Parser Prototype — Evidence Wrapper)
**Evidence type:** EVIDENCE_WRAPPER
**Retrospective:** true
**Status:** gate4_passed
**Delegated source:** src/python/ndjson/ndjson_codec.py

---

## RETROSPECTIVE NOTICE

This Gate 4 evidence artifact is **retrospectively reconstructed**.

NDJSON received Gate 1 approval and was immediately implemented as a production-quality
source track in `src/python/ndjson/`. Gates 2, 3, and 4 were never formally recorded
in the registry despite the implementation and sample corpus existing.

This wrapper provides canonical Gate 4 traceability retroactively. It does not alter
or duplicate the implementation — it delegates entirely to `ndjson_codec.py`.

**Gate 2 (retrospective):** NDJSON specification is IETF RFC-proposed (RFC 7464 / ndjson.org).
Spec evidence: one JSON object per line, UTF-8, LF-terminated.

**Gate 3 (retrospective):** Sample corpus exists at `samples/by-format/ndjson/valid/minimal.ndjson`.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: ndjson
  evidence_type: EVIDENCE_WRAPPER
  retrospective: true
  delegated_source: src/python/ndjson/ndjson_codec.py
  delegated_symbols:
    - load_ndjson
    - probe_ndjson
    - NdjsonParseError
  sample_corpus:
    - samples/by-format/ndjson/valid/minimal.ndjson
  valid_probe: ndjson_gate4_probe.py::probe
  invalid_probe: ndjson_gate4_probe.py::probe_invalid
  limitations:
    - Retrospective evidence only — not contemporaneous with implementation
    - Sample corpus is minimal (1 valid sample found)
    - No write at Gate 4 (ndjson_codec.py has write support but it's above G4)
    - Gate 4 scope only
  test_paths:
    - tests/skills/test_ndjson_gate4_prototype.py
  source_revision: src/python/ndjson/ at HEAD
  compatibility_version: "1.0"
gate_3_corpus: samples/by-format/ndjson/valid/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `ndjson_gate4_probe.py` | Thin evidence wrapper — no parsing logic |
| `gate4-evidence.yaml` | Gate 4 evidence record |
| `README.md` | This file |
