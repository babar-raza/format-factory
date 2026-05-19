# FODS/FODT Commercial Gap Analysis

**Sprint:** R33 Lane H
**Date:** 2026-05-19

---

## Current State

| Aspect | FODS | FODT |
|--------|------|------|
| Python LOC | 715 | 761 |
| .NET LOC | 1,286 | 1,222 |
| Python tests | 70 | 101 |
| .NET tests | 160 | 142 |
| .NET capability | C4-C6 (Load/Save/Edit) | C4-C6 (Load/Save/Edit) |
| .NET exporters | CSV, HTML, JSON | HTML, TXT, Markdown |
| Round-trip | .NET only | .NET only |
| Python write | No | No |
| Gate 11 status | g11f_hardening_in_progress | g11f_hardening_in_progress |
| G11-G (human) | NOT_STARTED | NOT_STARTED |

## Gaps for Commercial Readiness (C7+)

### Model Richness (Critical)
- Current: Tier 0-1 (basic cell/paragraph with value types)
- Needed: Tier 3+ (formatting, merged regions, formulas for FODS; inline formatting, tables, lists for FODT)
- **FODS gaps:** Cell formatting (bold/italic/color/font), merged cells, conditional formatting, formulas (store, not evaluate), named ranges
- **FODT gaps:** Inline formatting (bold/italic/underline/font), hyperlinks, tables with cells, images (reference tracking), page breaks

### Security Hardening
- Current: defusedxml, 100MB guard, DTD prohibited
- Needed: MaxCharactersFromEntities guard, XXE double-check with nested entities test

### Test Depth for C7+
- Need: round-trip tests for each new model feature, malformed input tests for extended features, export fidelity tests

### Python Write Capability
- Current: Python is read-only for both FODS and FODT
- Needed for full product value: Python write using neutral model -> XML serialization
- Lower priority than .NET C7+ but required for Python FOSS product completeness

## Recommended Deepening Order

1. **FODS .NET model enrichment** — merged cells, cell formatting storage, formula text capture
2. **FODT .NET model enrichment** — inline formatting spans, hyperlinks, table support
3. **Test expansion** — round-trip tests for each new feature
4. **Python write** — serialize neutral model back to flat XML
5. **G11-G preparation** — commercial readiness evidence packet for Babar Raza

## Estimated Effort

| Work Item | Estimated LOC | Tests |
|-----------|---------------|-------|
| FODS merged cells + formatting | ~200 .NET | ~20 |
| FODT inline formatting + hyperlinks | ~200 .NET | ~20 |
| FODS formula text capture | ~50 .NET | ~10 |
| FODT table support | ~150 .NET | ~15 |
| Python FODS writer | ~300 Python | ~30 |
| Python FODT writer | ~300 Python | ~30 |
| Security hardening | ~50 each | ~10 |

**Total:** ~1,250 LOC, ~135 tests across 2-3 focused sprints.

## This Sprint's Contribution

R33 does not modify FODS/FODT source. This gap analysis documents the path from current C4-C6 to C7+ and feeds into COMMERCIAL-FODS-FODT-G11-GAP-CLOSURE.md taskcard.
