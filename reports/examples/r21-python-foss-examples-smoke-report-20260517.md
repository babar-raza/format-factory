---
artifact_id: r21-python-foss-examples-smoke-report
artifact_type: report
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
gate: "4"
status: PASS
visibility: internal
---

# R21 Gate 4 — Python FOSS Examples and Smoke Report

## Deliverables Created

| Path | File |
|------|------|
| examples/python/zst/ | README.md, compress_decompress_file.py |
| examples/python/fodp/ | README.md, extract_presentation_text.py |
| examples/python/fodg/ | README.md, inspect_drawing_shapes.py |
| examples/python/gnumeric/ | README.md, extract_cells.py |
| examples/python/abw/ | README.md, extract_text.py |
| tests/examples/ | test_python_examples_smoke.py |

## Smoke Test Results

```
tests/examples/test_python_examples_smoke.py
18 passed in 0.74s
```

## Per-Format Summary

| Format | Script runs | Exit code | alpha-foss-preview label | No network imports |
|--------|-------------|-----------|--------------------------|-------------------|
| ZST    | ✓ | 0 | ✓ | ✓ |
| FODP   | ✓ | 0 | ✓ | ✓ |
| FODG   | ✓ | 0 | ✓ | ✓ |
| Gnumeric | ✓ | 0 | ✓ | ✓ |
| ABW    | ✓ | 0 | ✓ | ✓ |

## Design Notes

- ZST example gracefully handles missing `zstandard` library (exits 0 with clear error)
- All scripts reference samples from `samples/by-format/{format}/` (local, no download)
- All scripts print `alpha-foss-preview` and `NOT FOR COMMERCIAL USE` labels
- No subprocess, network, or socket calls in any example
- Example scripts use `PYTHONPATH=src/python` path injection pattern (self-contained)

## Gate 4 Verdict

GATE_4: PASS — Examples and smoke tests created and passing for all five formats.
