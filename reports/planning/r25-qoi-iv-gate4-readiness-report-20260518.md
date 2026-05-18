# R25 — QOI Gate 3 Independent Verification and Gate 4 Readiness Report
# Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
# Date: 2026-05-18
# Gate: 4 — QOI Gate 3 IV

## Sample Corpus Verified

| File | Check | Result |
|------|-------|--------|
| valid/1x1-red.qoi | Magic qoif, 1x1, ch=4 (RGBA), cs=0, end marker correct | PASS |
| valid/2x2-black.qoi | Magic qoif, 2x2, ch=4 (RGBA), cs=0, end marker correct | PASS |
| valid/4x1-gradient.qoi | Magic qoif, 4x1, ch=3 (RGB), cs=0, end marker correct | PASS |
| invalid/wrong-magic.qoi | Magic = b'NOPE' (correctly fails magic check) | PASS |

### QOI Binary Verification Rules Applied

| Rule | Checked | All Samples |
|------|---------|-------------|
| Magic bytes = b'qoif' | YES | PASS (valid) / PASS (invalid rejects) |
| Header: width (4 bytes BE) | YES | PASS |
| Header: height (4 bytes BE) | YES | PASS |
| Channels: 3 (RGB) or 4 (RGBA) | YES | PASS |
| Colorspace: 0 (sRGB) or 1 (linear) | YES | PASS |
| End marker: 8 bytes 0x00..0x01 | YES | PASS |
| Invalid sample fails magic check | YES | PASS |

## Gate 3 IV Verdict

**gate_3_iv_status: verified**
All 3 valid QOI samples spec-accurate (magic, header, end marker).
Invalid sample correctly rejected by magic check.

## Gate 4 Readiness

| Field | Value |
|-------|-------|
| Gate 4 readiness | ready_for_parser_planning |
| Parser strategy | Python struct.unpack (stdlib only) |
| Key parsing target | 14-byte header → chunk loop (QOI_OP_RGB/RGBA/INDEX/DIFF/LUMA/RUN) → 8-byte end |
| Spec source | qoi.phoboslab.org (public domain) |
| Authorization | Gate 4 prototype planning only — no production source authorized |
| Parser notes | acquisition-packs/qoi/parser-notes.md |

**Gate 4 (QOI) — READY FOR PARSER PLANNING**
