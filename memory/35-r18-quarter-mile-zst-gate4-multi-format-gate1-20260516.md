# Memory: R18 Quarter-Mile Sprint — ZST Gate 4 Prototype + Multi-Format Gate 1
Sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Author: claude-sonnet-4-6

## Summary

R18 "quarter-mile" sprint completed the following:
1. ZST Gate 4 prototype (4 files, 38 tests PASS, 15/15 corpus PASS)
2. ZST Gate 5 decision (NEUTRAL_MODEL_NOT_APPLICABLE — codec format)
3. FODP Gate 1 APPROVED (8.7, OASIS RF, Aspose.Slides FULL_RT)
4. FODG Gate 1 APPROVED (8.1, OASIS RF, Aspose.Imaging LOAD_ONLY)
5. Gnumeric Gate 1 APPROVED (8.2, Cat2, Aspose NOT_SUPPORTED)
6. ABW Gate 1 APPROVED (7.8, Cat2, Aspose NOT_SUPPORTED; spec risk MEDIUM)
7. ORA scored_pending_human_approval (6.8, Borderline)
8. dnumber/.numbers FORMAL_REJECT closed (Category 5; Apple Numbers)
9. Registry expanded to 8 formats; master-plan v2.63

## ZST Gate 4 Prototype

Location: `prototypes/by-format/zst/`

Files:
- `README.md` — non-production boundary, security notes
- `frame_header.py` — pure Python RFC 8878 frame header reader (no zstandard dep)
- `zst_probe.py` — decompressor + metadata reporter (uses python-zstandard)
- `validate_corpus.py` — corpus validator + round-trips

Key design decisions:
- Always use `stream_reader()` for decompression (handles frames without Content_Size)
- ASCII arrows (`->`) in print output to avoid cp1252 encoding errors on Windows
- frame_header.py uses `from __future__ import annotations` + dataclass — loads fine via sys.path approach but fails with importlib.util.spec_from_file_location in Python 3.13 tests; solution: add PROTO_DIR to sys.path and use regular import

Test file: `tests/skills/test_zst_gate4_prototype.py` — 38/38 PASS

Registry: gate_4.status = prototype_complete (not passed — human approval still needed)
IV report: `reports/verification/r18-zst-gate4-prototype-iv-20260516.md` (10/10 PASS)

## ZST Gate 5 Decision

File: `acquisition-packs/zst/gate5-requirements-readiness.md`
Decision: NEUTRAL_MODEL_NOT_APPLICABLE (G-NORM-004 waiver)
Reason: ZST is a pure compression codec. No document object model. No named fields.
Neutral model not meaningful for byte-stream compression formats.
Gate 5 NOT APPROVED — requires human execution prompt.

## Multi-Format Gate 1 Results

| Format | Score | Legal | Aspose | Status |
|--------|-------|-------|--------|--------|
| FODP | 8.7 | Cat 1 (OASIS RF) | FULL_ROUND_TRIP (Slides) | APPROVED |
| FODG | 8.1 | Cat 1 (OASIS RF) | LOAD_ONLY (Imaging) | APPROVED |
| Gnumeric | 8.2 | Cat 2 (OSS) | NOT_SUPPORTED | APPROVED |
| ABW | 7.8 | Cat 2 (OSS) | NOT_SUPPORTED | APPROVED |
| ORA | 6.8 | Cat 2 (community) | NOT_SUPPORTED | PENDING_HUMAN |
| dnumber | 0 | Cat 5 (proprietary) | n/a | FORMAL_REJECT |

IV reports:
- FODP/FODG: `reports/verification/r18-fodp-fodg-gate1-iv-20260516.md` (20/20 PASS)
- Gnumeric/ABW: `reports/verification/r18-gnumeric-abw-gate1-iv-20260516.md` (20/20 PASS)

## Acquisition Packs Created

- `acquisition-packs/fodp/` — pack.yaml + gate1-decision-packet.md
- `acquisition-packs/fodg/` — pack.yaml + gate1-decision-packet.md
- `acquisition-packs/gnumeric/` — pack.yaml + gate1-decision-packet.md
- `acquisition-packs/abw/` — pack.yaml + gate1-decision-packet.md
- `acquisition-packs/ora/` — pack.yaml + gate1-scoring-packet.md (pending)

## Gate 2 Fast-Path

FODP and FODG are Gate 2 fast-path eligible (same OASIS ODF 1.3 spec as FODS/FODT, already cached).
Fast-path authorization document: `reports/planning/r18-fodp-fodg-gate2-fastpath-decision-20260516.md`
Gate 2 fast-path requires separate human execution prompt.

Gnumeric and ABW are NOT fast-path eligible (different spec bodies).

## Aspose Support Audit Results (R18 confirmed)

| Format | Aspose Product | Support Level |
|--------|---------------|---------------|
| FODP | Aspose.Slides | FULL_ROUND_TRIP (LoadFormat.Fodp + SaveFormat.Fodp, since Java 20.4) |
| FODG | Aspose.Imaging | LOAD_ONLY (ODG import; no save confirmed) |
| Gnumeric | Aspose.Cells | NOT_SUPPORTED |
| ABW | Aspose.Words | NOT_SUPPORTED |
| ORA | Aspose.Imaging | NOT_SUPPORTED |

## Registry State

8 formats now in registry/format-registry.yaml:
- fods: Gates 1-10 PASSED; Gate 11 in_progress
- fodt: Gates 1-10 PASSED; Gate 11 in_progress
- zst: Gates 1-3 PASSED; Gate 4 prototype_complete
- fodp: Gate 1 PASSED (score 8.7)
- fodg: Gate 1 PASSED (score 8.1)
- gnumeric: Gate 1 PASSED (score 8.2)
- abw: Gate 1 PASSED (score 7.8)
- ora: Gate 1 scored_pending_human_approval (score 6.8)

## Key Technical Notes

### frame_header.py Python 3.13 import issue
`from __future__ import annotations` + `@dataclass` in frame_header.py causes failure
when loaded via `importlib.util.spec_from_file_location` in Python 3.13 tests.
Solution: Add PROTO_DIR to sys.path and use regular `import frame_header`.
The module works correctly when loaded this way.

### ZST dict-compressed.zst behavior
Content_Size in header = 64 bytes (compressed frame field), actual decompressed = 4160 bytes.
This is expected RFC 8878 behavior when dictionary is used.
stream_reader() handles this correctly.

### ABW spec risk
AWML 1.0 DTD is outdated ("very much out-of-date" per project docs).
Reference implementation (AbiWord source code) required to supplement DTD.
acquisition_risk_classification: MEDIUM. Must be re-evaluated at Gate 2.

## Next Steps (Post-R18)

1. Full test suite validation (Gate 12) — expected 1400+ tests
2. Adversarial review (Gate 13) — 22 attacks
3. Evidence bundle build + commit (Gate 14)
4. Next sprints needed:
   - ZST Gate 4 approval + Gate 5 (human prompt required)
   - FODP/FODG Gate 2 fast-path (human prompt required)
   - Gnumeric/ABW Gate 2 (human prompt required)
   - ORA Gate 1 human decision
   - FODS/FODT Gate 11 sub-gates (separate track, untouched in R18)

## Hard Invariants Maintained

- No src/python/zst/ or src/net/zst/ created ✓
- No generated-requirements/zst/ created ✓
- FODS/FODT Gate 11 not touched ✓
- commercial_product_ready: false for all formats ✓
- No GitHub push or PR ✓
