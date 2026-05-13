# FormatFactory.Fodt — .NET Commercial Parser (Tier 0)

## Status: Gate 11 Tier 0 — NOT Release-Ready

This is a **commercial-only** .NET Tier 0 implementation for the FODT (Flat OpenDocument
Text) parser. Skeleton created 2026-05-12; Tier 0 streaming parser implemented
2026-05-13 during GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001.

**Gate 11 has NOT been approved.** Full production hardening is required before Gate 11
can be approved and this package can be released.

## Scope

- **Format:** FODT — Flat OpenDocument Text
- **Root element:** `office:text`
- **Namespace:** `urn:oasis:names:tc:opendocument:xmlns:text:1.0`
- **Target framework:** net10.0 LTS
- **Package ID:** FormatFactory.Fodt (commercial)

## DEC-033 Option B: .NET Commercial Only

Per DEC-033 resolution (Babar Raza, 2026-05-12), this project is **commercial-only**:

- No .NET FOSS package is produced for FODT
- The FOSS track is Python: `src/python/fodt/` (Apache-2.0, `format-factory-fodt`)
- Developers needing a free parser use the Python package

## Current Implementation

Tier 0 streaming parser (GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001, 2026-05-13):

- `FodtParser.cs`: `Parse()` returns `FodtParseResult` with paragraph/heading/list counts,
  tables, metadata, errors/warnings
- `FodtParser.GetParagraphCount()`: convenience wrapper; throws `FodtParseException` on failure
- Security: `DtdProcessing.Prohibit`, `XmlResolver = null`, 50 MB size guard
- Streaming XmlReader: no DOM allocation
- Extracts: `office:document` mimetype/version, `office:meta` (title, creator, subject,
  initial-creator), `text:p`/`text:h` paragraph/heading counts, `text:list` counts,
  `table:table` list with row and cell counts
- xUnit test suite: `tests/net/fodt/` — 13/13 PASS (null path, file-not-found, size guard,
  empty file, malformed XML, DTD rejection, paragraph counting, list counting, table
  extraction, GetParagraphCount, GetParagraphCount exception, real sample integration)

## What Remains for Gate 11

1. Tier 1-2 features per `acquisition-packs/fodt/tier-map.yaml`
2. Full production hardening and error recovery
3. NuGet packaging configuration
4. DEC-034 independent verification
5. Explicit Gate 11 human approval

## Commercial Licensing

See `acquisition-packs/fodt/gate11-commercial-licensing.md`.

## References

- Acquisition pack: `acquisition-packs/fodt/`
- Python FOSS source: `src/python/fodt/`
- Tier map: `acquisition-packs/fodt/tier-map.yaml`
- Gate 11 packaging plan: `acquisition-packs/fodt/gate11-packaging-plan.md`
