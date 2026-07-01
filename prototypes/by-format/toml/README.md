---
artifact_id: toml-gate4-evidence-wrapper
artifact_type: gate4_evidence_wrapper
path: prototypes/by-format/toml/README.md
format_id: toml
visibility: internal
publish_allowed: false
retrospective: true
generated_by: claude-sonnet-4-6
generated_at: "2026-07-01"
notes: >
  Gate 4 evidence wrapper for TOML — RETROSPECTIVE. Gate 4 was never formally
  recorded despite full production implementation existing in src/python/toml/.
---

# TOML Gate 4 Evidence Wrapper (RETROSPECTIVE)

**Format:** Tom's Obvious Minimal Language (TOML)
**Gate:** Gate 4 (Parser Prototype — Evidence Wrapper)
**Evidence type:** EVIDENCE_WRAPPER
**Retrospective:** true
**Status:** gate4_passed
**Delegated source:** src/python/toml/toml_codec.py

---

## RETROSPECTIVE NOTICE

This Gate 4 evidence artifact is **retrospectively reconstructed**.

TOML received Gate 1 approval and was immediately implemented as a production-quality
source track in `src/python/toml/`. Gates 2, 3, and 4 were never formally recorded
in the registry despite the implementation and sample corpus existing.

**Gate 2 (retrospective):** TOML spec v1.0.0 at https://toml.io/en/v1.0.0. Open source.
**Gate 3 (retrospective):** Sample at `samples/by-format/toml/minimal.toml`.

---

## gate4_wrapper Manifest

```yaml
gate4_wrapper:
  format_id: toml
  evidence_type: EVIDENCE_WRAPPER
  retrospective: true
  delegated_source: src/python/toml/toml_codec.py
  delegated_symbols:
    - load_toml
    - probe_toml
    - TomlParseError
    - TomlInputError
  sample_corpus:
    - samples/by-format/toml/minimal.toml
  valid_probe: toml_gate4_probe.py::probe
  invalid_probe: toml_gate4_probe.py::probe_invalid
  limitations:
    - Retrospective evidence only
    - Sample corpus is minimal (1 sample found)
    - Gate 4 scope only
  test_paths:
    - tests/skills/test_toml_gate4_prototype.py
  source_revision: src/python/toml/ at HEAD
  compatibility_version: "1.0"
gate_3_corpus: samples/by-format/toml/
verdict: GATE4_PASSED
```

---

## Files

| File | Purpose |
|---|---|
| `toml_gate4_probe.py` | Thin evidence wrapper — no parsing logic |
| `gate4-evidence.yaml` | Gate 4 evidence record |
| `README.md` | This file |
