# Source Track Maturity Policy

**Document type:** Policy
**Created:** R32 (2026-05-19)
**Authority:** Defines quality tiers for Python FOSS, .NET commercial, acquisition-only, and prototype formats.

---

## Purpose

This policy establishes what "done" means for each product track and maturity level. Without it, a 141-line text extractor and a 761-line streaming parser with neutral model are treated equivalently because both exist in `src/python/`.

---

## Python FOSS Track (src/python/{format}/)

### Minimum for presence in src/python/
- Parser file with at least 5 format features extracted
- __init__.py with public API
- File size guard
- At least 30 tests in tests/python/{format}/
- Gate 5 neutral model or approved exemption

### Quality tiers

#### Tier: read_only_library_foundation
- Formal neutral model (dataclass or schema)
- Parser populates model from real corpus
- At least 50 tests
- Malformed input handling (Gate 7 level)
- Security review (Gate 8 level)
- No write/export required
- Example: FODS Python parser, ODS parser

#### Tier: read_write_library_foundation
- Everything in read_only_library_foundation, plus:
- Write/save capability (format-native output)
- At least 60 tests including write tests
- Example: ZST codec (compress+decompress)

#### Tier: export_capable_library
- Everything in read_write_library_foundation, plus:
- At least 1 export format (e.g., CSV, JSON, HTML)
- Export tests
- Example: (no Python format currently meets this — .NET FODS/FODT have exports)

#### Tier: roundtrip_capable_library
- Everything in export_capable_library, plus:
- Verified round-trip: parse -> model -> write -> parse -> compare
- Round-trip test suite
- Example: ZST (compress -> decompress verified)

### What does NOT belong in src/python/
- Probes that only read headers (should be probe_only in matrix)
- Parsers with no neutral model and <200 LOC
- Parsers that return plain dicts without schema

---

## .NET Commercial Track (src/net/{format}/)

### Minimum for presence in src/net/
- .csproj with target framework
- Parser class (non-throwing result pattern recommended)
- Document class with Load/Save minimum
- At least 1 Model class
- At least 50 .NET tests
- DTD prohibition + XmlResolver null for XML formats
- File size guard

### Quality tiers

#### Tier: C4-C6 vertical slice (current FODS/FODT state)
- Load/Save/Edit operations
- At least 1 exporter
- Round-trip verified
- 100+ tests
- commercial_product_ready: false

#### Tier: C7+ commercial candidate
- C4-C6 plus:
- Rich model (formatting, formulas, merged regions for spreadsheets; inline formatting for text)
- Multiple exporters
- Entity expansion guard (MaxCharactersFromEntities)
- G11-G human approval packet prepared
- commercial_product_ready: false until G11-G approved

#### Tier: production_track_real
- C7+ plus:
- G11-G approved by project lead
- commercial_product_ready: true
- NuGet package published
- Documentation complete

---

## Acquisition-Only Formats

Formats at Gates 1-3 with no source code.
- Only acquisition-packs/ and samples/ exist
- No quality expectations beyond pack.yaml correctness
- Cannot claim any parser or product maturity

---

## Prototype/Probe Formats

Formats with exploratory code only.
- May live in prototypes/by-format/ (correct location)
- May live in src/python/ (requires quarantine marker in completion matrix)
- Cannot claim Gate 5+ without neutral model
- Cannot claim Gate 10+ without write/export or approved read-only scope
- Test count may be <30

---

## Enforcement

1. `registry/format-completion-matrix.yaml` records `actual_maturity_class` per format.
2. `tests/evidence/test_source_track_maturity.py` validates maturity claims against source evidence.
3. Sprint reports must classify format maturity using these tiers.
4. Promotion from one tier to the next requires evidence (source + tests), not reports.
