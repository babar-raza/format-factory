# DEEPEN-QOI-PRODUCTION-TRACK

**Type:** Format deepening
**Created:** R32 (2026-05-19)
**Format:** QOI (Quite OK Image Format)
**Priority:** High — complete decoder exists, encoder is the natural next step

---

## Current Evidence-Backed Maturity
- **Class:** read_only_library_foundation
- **Source:** src/python/qoi/qoi_parser.py (307 LOC)
- **Tests:** 62 methods (header, all 6 chunk types, dimension guards, oracle, fuzz)
- **Gate:** G8
- **Model:** dataclass (QoiImage) — width, height, channels, colorspace, pixels

## Next Target Maturity
**roundtrip_capable_library**

## Feature Gaps
1. No QOI encoder (write)
2. No image export (PNG, raw pixel output)
3. No round-trip verification

## Source Gaps
- Missing: qoi_encoder.py (or qoi_writer.py)
- Missing: export to common image format

## Tests Required
- Encoder tests: model -> QOI bytes
- Round-trip: decode -> pixels -> encode -> decode -> compare
- Export tests: QOI -> raw pixel array
- Target: 80+ tests

## Stop Conditions
- Encoder must produce spec-compliant QOI (all 6 chunk types)
- Do not implement conversion to/from other image formats beyond raw pixels

## Evidence Required
- Encoder tests pass
- Round-trip tests pass (decode-encode-decode matches)
- Fuzz: encoded output parses correctly
