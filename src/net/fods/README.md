# FormatFactory.Fods — .NET Commercial (C4-C6 Vertical Slice)

## Status: Gate 11 commercial_readiness_in_progress — NOT Release-Ready

This is a **commercial-only** .NET implementation for the FODS (Flat OpenDocument
Spreadsheet) format. Skeleton created 2026-05-12; C4-C6 load/edit/save vertical slice
implemented 2026-05-13 during COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001.

**Gate 11 has NOT been approved.** `commercial_product_ready: false`.
Full C7+ capability + human approval required before Gate 11 can be approved and
this package can be released.

## Scope

- **Format:** FODS — Flat OpenDocument Spreadsheet
- **Root element:** `office:spreadsheet`
- **Namespace:** `urn:oasis:names:tc:opendocument:xmlns:table:1.0`
- **Target framework:** net10.0 LTS
- **Package ID:** FormatFactory.Fods (commercial)

## DEC-033 Option B: .NET Commercial Only

Per DEC-033 resolution (Babar Raza, 2026-05-12), this project is **commercial-only**:

- No .NET FOSS package is produced for FODS
- The FOSS track is Python: `src/python/fods/` (Apache-2.0, `format-factory-fods`)
- Developers needing a free parser use the Python package

## Current Implementation (C4-C6 Vertical Slice)

### Tier 0 streaming parser (FodsParser.cs — baseline, retained)
- `FodsParser.cs`: `Parse()` returns `FodsParseResult` with sheets, metadata, errors/warnings
- `FodsParser.GetSheetNames()`: convenience wrapper
- Security: `DtdProcessing.Prohibit`, `XmlResolver = null`, 50 MB size guard
- Streaming XmlReader; no DOM allocation

### C4-C6 DOM implementation (FodsDocument.cs — vertical slice)
- `FodsDocument.cs`: `Load(path)` → DOM-backed `FodsDocument`; `Save(path)` round-trip
- `FodsWriter.cs`: DOM serialization (UTF-8, preserves opaque nodes)
- `Model/FodsSheet.cs`: `Name` getter/setter, `Rows` collection
- `Model/FodsRow.cs`: `Cells` collection
- `Model/FodsCell.cs`: `Value` (display text), `SetText()` editor, `IsCovered`
- Security: DTD prohibited, XmlResolver=null, 50 MB size guard
- xUnit test suite: `tests/net/fods/` — 42/42 PASS (Tier 0 tests + DOM load/edit/save/roundtrip)

## What Remains for Gate 11

1. Broader entity coverage (styles, formulas, typed values) beyond Sheets/Rows/Cells
2. C9 export/conversion (PDF, HTML, PNG) — future roadmap
3. Full production hardening, error recovery, and edge-case coverage
4. NuGet packaging configuration
5. DEC-034 independent verification
6. Explicit Gate 11 human approval (G11-A through G11-G sub-gates)

## Product Maturity (Dual-Lane)
- **Lane A (Features):** A1 — Load + basic query
- **Lane B (DOM):** D4 — Editable XDocument DOM with mutation
- **DOM Applicable:** Yes (FULL — hierarchical XML spreadsheet)

## Commercial Licensing

See `acquisition-packs/fods/gate11-commercial-licensing.md`.

## References

- Acquisition pack: `acquisition-packs/fods/`
- Python FOSS source: `src/python/fods/`
- Tier map: `acquisition-packs/fods/tier-map.yaml`
- Gate 11 packaging plan: `acquisition-packs/fods/gate11-packaging-plan.md`

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:29+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Fods
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:29+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Flat OpenDocument Spreadsheet |
| Track | dotnet |
| Package | FormatFactory.Fods |
| Version | 0.1.0-tier0 |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | OASIS ODF 1.3 |
| QName coverage | 12/12 implemented |
| Source files | 20 |
| Test files | 511 |
<!-- END:README-PACKAGE_INFO -->
