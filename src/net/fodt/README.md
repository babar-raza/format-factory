# FormatFactory.Fodt — .NET Commercial (C4-C6 Vertical Slice)

## Status: Gate 11 commercial_readiness_in_progress — NOT Release-Ready

This is a **commercial-only** .NET implementation for the FODT (Flat OpenDocument
Text) format. Skeleton created 2026-05-12; C4-C6 load/edit/save vertical slice
implemented 2026-05-13 during COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001.

**Gate 11 has NOT been approved.** `commercial_product_ready: false`.
Full C7+ capability + human approval required before Gate 11 can be approved and
this package can be released.

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

## Current Implementation (C4-C6 Vertical Slice)

### Tier 0 streaming parser (FodtParser.cs — baseline, retained)
- `FodtParser.cs`: `Parse()` returns `FodtParseResult` with paragraph/heading/list counts,
  tables, metadata, errors/warnings
- `FodtParser.GetParagraphCount()`: convenience wrapper
- Security: `DtdProcessing.Prohibit`, `XmlResolver = null`, 50 MB size guard
- Streaming XmlReader; no DOM allocation

### C4-C6 DOM implementation (FodtDocument.cs — vertical slice)
- `FodtDocument.cs`: `Load(path)` → DOM-backed `FodtDocument`; `Save(path)` round-trip
- `FodtWriter.cs`: DOM serialization (UTF-8, preserves opaque nodes)
- `Model/FodtBody.cs`: body container wrapping `office:body/office:text`
- `Model/FodtParagraph.cs`: `Text` getter, `SetText()` editor, `OutlineLevel`, `IsParagraph`/`IsHeading`
- Security: DTD prohibited, XmlResolver=null, 50 MB size guard
- xUnit test suite: `tests/net/fodt/` — 43/43 PASS (Tier 0 tests + DOM load/edit/save/roundtrip)

## What Remains for Gate 11

1. Broader entity coverage (styles, lists, tables) beyond Body/Paragraphs
2. C9 export/conversion (PDF, HTML, PNG) — future roadmap
3. Full production hardening, error recovery, and edge-case coverage
4. NuGet packaging configuration
5. DEC-034 independent verification
6. Explicit Gate 11 human approval (G11-A through G11-G sub-gates)

## Commercial Licensing

See `acquisition-packs/fodt/gate11-commercial-licensing.md`.

## References

- Acquisition pack: `acquisition-packs/fodt/`
- Python FOSS source: `src/python/fodt/`
- Tier map: `acquisition-packs/fodt/tier-map.yaml`
- Gate 11 packaging plan: `acquisition-packs/fodt/gate11-packaging-plan.md`

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:29+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Fodt
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:29+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Flat OpenDocument Text |
| Track | dotnet |
| Package | FormatFactory.Fodt |
| Version | 0.1.0-tier0 |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | OASIS ODF 1.3 |
| QName coverage | 8/9 implemented |
| Source files | 25 |
| Test files | 507 |
<!-- END:README-PACKAGE_INFO -->
