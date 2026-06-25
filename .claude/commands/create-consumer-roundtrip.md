# /create-consumer-roundtrip

**Mission:** ALLFORMAT-DEEPENING-20260625
**Skill ID:** create-consumer-roundtrip
**Product Track:** foss_python_consumer
**Idempotency:** If `examples/python/{format}/consumer_roundtrip.py` exists AND contains `CONSUMER_PROOF: PASS`, skip without modification.

## Purpose

Generates `examples/python/{format}/consumer_roundtrip.py` for a given format. The script demonstrates and proves the complete consumer flow: load → inspect → modify (if writable) → save → reload → verify semantic equivalence.

## Required Input

- `format_id`: one of [fodp, fods, fodt, ods, odt, pbm, pgm, ppm, qoi, xcf]

## Template Pattern

```python
#!/usr/bin/env python3
"""
Consumer roundtrip proof for {format}.
Mission: ALLFORMAT-DEEPENING-20260625
"""
# Dual-mode import: installed package first, src/ fallback
try:
    from {format} import {key_symbols}
except ImportError:
    import sys
    from pathlib import Path
    _REPO = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(_REPO))
    from src.python.{format} import {key_symbols}

# 1. LOAD
model = load(fixture_path)

# 2. INSPECT
assert {key_property} is not None

# 3. MODIFY (if writable)
# {format-specific mutation}

# 4. SAVE (if writable)
# {format-specific save}

# 5. RELOAD and VERIFY
# {format-specific reload assertions}

print("CONSUMER_PROOF: PASS")
```

## Format-Specific API Notes

### fodp (read-only — no write_fodp)
- `load(path)` → dict with `page_count`, `pages` list
- `get_page_count(path)` takes file path (NOT model dict)
- `fodp_slide_count(path)`, `fodp_titles(path)`, `has_multi_slide(path)` take file path
- Pattern: load → inspect → analytics → print PASS (no save/reload for read-only)

### fods
- `load(path)` → model (has `sheets`, `sheet_count`)
- `set_cell_value(src, dest, sheet_idx, row, col, value)` — FILE-BASED
- `write_fods(model, dest)` — writes model to file
- Pattern: load → inspect sheet → set_cell_value (file-based) → load new → assert

### fodt
- `load_fodt(path)` or `parse_fodt(path)` → model dict with `content` list
- `fodt_to_txt(model_or_path)`, `fodt_to_markdown(model_or_path)`, `fodt_to_html(model_or_path)` in exporters.py
- Pattern: load → inspect → append paragraph via dict mutation → write_fodt → reload → assert paragraph count increased

### ods
- `load(path)` → model (ODS format, similar to FODS)
- Pattern: same as fods but with write_ods

### odt
- `parse_odt(path)` → model dict
- `write_odt(paragraphs, dest)` — creates new ODT
- `odt_from_model(model, dest)` — round-trip from parsed model
- Pattern: parse → inspect paragraph_count → odt_from_model → reload → assert

### pbm
- `load(path)` or `parse_pbm(path)` → image model
- `write_pbm(model, dest)` or `save_pbm(model, dest)`
- Pattern: load → inspect width/height → write_pbm → reload → assert dims match

### pgm
- `load(path)` or `parse_pgm(path)` → image model
- `write_pgm(model, dest)` or `save_pgm(model, dest)`
- Pattern: same as pbm

### ppm
- `load(path)` or `parse_ppm(path)` → image model
- Pattern: same as pbm/pgm; check if write_ppm exists first

### qoi (read-only — no write_qoi exists)
- `load(path)` → image dict with `width`, `height`, `channels`, `colorspace`
- Pattern: load → inspect → print properties → PASS (inspection-only)

### xcf
- `load(path)` or `parse_xcf(path)` → XcfImage or dict
- `xcf_layer_name_list(path)` → list of REAL layer names (fixed 2026-06-25)
- `XcfImage.layer_names` field
- Pattern: load → xcf_layer_name_list → inspect layer_names → assert len > 0 → PASS

## Pre-Execution Read

Before writing a consumer_roundtrip.py for a format, READ these files to confirm exact API:
- `src/python/{format}/__init__.py` — public API exports
- `src/python/{format}/{format}_parser.py` or main codec — load function signature

## Validation After Creation

```bash
python examples/python/{format}/consumer_roundtrip.py
# Must print: CONSUMER_PROOF: PASS

.venv/Scripts/pytest tests/python/{format}/ -x -q --tb=short
# Must have 0 new failures vs pre-execution baseline
```

## Ledger Entry Required

```json
{"sprint": "TC-D-{N}", "action": "create_consumer_roundtrip", "format": "{format_id}", "files": ["examples/python/{format}/consumer_roundtrip.py"]}
```

## Obligation Register Update

After PASS: run `/update-obligation-entry` for ALLF-{FORMAT}-PY:
- `current_proof_level: PROOF_LEVEL_4`
- `terminal_state: COMPLETED_AND_VERIFIED`
- `evidence_paths: ["examples/python/{format}/consumer_roundtrip.py"]`
