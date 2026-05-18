# R23 Non-ODF Candidate Acceleration Report — QOI (Gate 12)
# Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-PYTHON-PUBLICATION-DRYRUN-GATE11-HARDENING-NEXT-FORMATS-AND-PLAYBOOK-REPAIR-001
# Date: 2026-05-17
# Status: Gate 1 PASS (8.1/10), Gate 2 PASS
# Imaging family — First non-ODF, non-compression format acquisition

## Purpose

This report covers the QOI (Quite OK Image Format) acceleration in R23 as the first non-ODF
imaging-family candidate. It documents the decision process, scoring rationale, and current
gate status.

## Format Profile

| Field                 | Value                                                     |
|-----------------------|-----------------------------------------------------------|
| format_id             | qoi                                                       |
| display_name          | Quite OK Image Format                                     |
| extensions            | .qoi                                                      |
| mime_type             | image/qoi (IANA registered 2022)                          |
| family                | imaging                                                   |
| spec_body             | Dominic Szablewski / phoboslab                            |
| spec_version          | QOI 1.0 (November 2021)                                   |
| legal_category        | 1 (MIT license on reference implementation)               |
| aspose_supported      | false (NOT_SUPPORTED)                                     |
| acquisition_risk      | LOW                                                       |

## Why QOI Was Selected (Non-ODF Lane)

1. **MIT license** — reference C implementation at github.com/phoboslab/qoi (MIT). No patent claims.
2. **Single-page spec** — complete format definition at qoi.phoboslab.org. Simple enough to implement in <200 lines Python.
3. **IANA-registered MIME** — `image/qoi` registered November 2022. Formally recognized format.
4. **NOT_SUPPORTED by Aspose** — positive commercial differentiation. No major vendor parser tooling exists.
5. **First imaging family** — establishes imaging track, expands product surface beyond ODF/compression families.
6. **Growing community** — multiple language ports (Rust, Python, Go, C#). Used in embedded/game development.

## Gate 1 — Scoring

Score: 81/100 → normalized 8.1/10 → Band: **Accept** (threshold 7.0)

| Criterion              | Score | Points | Evidence                                                                     |
|------------------------|-------|--------|------------------------------------------------------------------------------|
| legal_safety           | 3     | 30     | MIT license on reference implementation. Author states no patents. IANA registered.|
| spec_availability      | 2     | 13     | Single-page spec at qoi.phoboslab.org. Complete but concise. Maintained by author.|
| parseable_structure    | 3     | 15     | Simple sequential binary. 14-byte header + RLE chunks. No container/compression layers.|
| community_demand       | 2     | 10     | Growing interest, multiple ports. Not yet mainstream.                        |
| strategic_track_value  | 1     | 3      | First imaging format — establishes track but early stage.                    |
| implementation_complexity | 3  | 5      | <300 lines C reference; Python possible in <200 lines. struct.unpack patterns.|
| family_overlap         | 3     | 5      | No overlap — no imaging formats currently in system.                         |

Approval: delegated_agent_r23 (2026-05-17) — awaiting human IV per DEC-034.

## Gate 2 — Spec Summary

Spec: qoi.phoboslab.org — single-page format definition (no download required).

```
QOI Header (14 bytes):
  - magic:      4 bytes  "qoif"
  - width:      4 bytes  big-endian u32
  - height:     4 bytes  big-endian u32
  - channels:   1 byte   3=RGB, 4=RGBA
  - colorspace: 1 byte   0=sRGB+linear-alpha, 1=all-linear

Pixel Encoding Chunks (variable length):
  - QOI_OP_RGB   (0xFE):        3-byte literal RGB
  - QOI_OP_RGBA  (0xFF):        4-byte literal RGBA
  - QOI_OP_INDEX (2b+6b):       reference to 64-slot running hash array
  - QOI_OP_DIFF  (2b+6b):       small RGB delta (bias -2..+1)
  - QOI_OP_LUMA  (2b+6b+8b):    larger green-channel delta
  - QOI_OP_RUN   (2b+6b):       run-length repeat (1..62)

End Marker (8 bytes): 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x01
```

Patent status: Author explicitly states no patents. MIT license on reference implementation.
Legal category: 1 (open, no patent claims, MIT reference impl).

## Gate 3 — Sample Corpus Plan

Gate 3 samples: planned for R24 sprint.

| Sample Source                   | License  | Status     | Notes                                      |
|---------------------------------|----------|------------|---------------------------------------------|
| QOI reference test suite        | MIT      | planned_r24| github.com/phoboslab/qoi/tree/master        |
| Synthetic via Python qoi library | MIT     | planned_r24| PyPI `qoi` package (MIT) for generation     |
| Generated from PNG references   | Apache-2.0 | planned_r24| Convert from Apache-licensed PNGs          |

Minimum corpus: 3 samples (minimal RGB image, RGBA image with transparency, run-length dominated image).
MIT license on reference samples — legally safe.

## Implementation Plan (Future Sprints)

Gate 4 parser prototype approach:
- Pure Python, stdlib struct + bytes
- probe_qoi(path): validate magic, parse header → width/height/channels/colorspace
- decode_qoi(path): full pixel decode → numpy array or list of tuples
- No external dependencies required (optional: use `qoi` PyPI package for oracle)

Oracle strategy:
- Encode test pixel arrays with Python `qoi` library (MIT)
- Decode with our parser
- Compare pixel arrays element-by-element

## Differentiation Analysis

| Competitor       | QOI Support | Notes                                                    |
|------------------|-------------|----------------------------------------------------------|
| Aspose           | NONE        | No Aspose class handles .qoi as of 2026-05-17           |
| Pillow (PIL)     | Via plugin  | qoi-pillow plugin exists but not in core                |
| ImageMagick      | Partial     | Added QOI support in 7.1.0 but not default              |
| Our Python FOSS  | PLANNED     | First-mover advantage in commercial-adjacent FOSS space  |

## Verdict

QOI accepted into imaging acquisition lane. Gates 1-2 passed (delegated, R23).
Gate 3 corpus planned for R24. No implementation work authorized until human IV.

## Hard Invariants

- commercial_product_ready: false
- publication_authorized: false
- No implementation authorized (Gates 1-3 IV incomplete per DEC-034)
- Gate 1/2 approvals are delegated — require human IV before Gate 3 execution
