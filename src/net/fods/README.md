# FormatFactory.Fods — .NET Commercial Parser (Skeleton)

## Status: Gate 11 Skeleton — NOT Release-Ready

This is a **commercial-only** .NET skeleton for the FODS (Flat OpenDocument Spreadsheet)
parser. Created during DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001 (2026-05-12).

**Gate 11 has NOT been approved.** Full implementation is required before Gate 11
can be approved and this package can be released.

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

## Current Implementation

Tier 0 skeleton:

- `FodsParser.cs`: `GetSheetNames()` validates XML well-formedness only
- Sheet data extraction: NOT IMPLEMENTED
- Multi-sheet support: NOT IMPLEMENTED
- Full iterparse equivalent: NOT IMPLEMENTED

## What Remains for Gate 11

1. Full Tier 0 parser implementation (sheet enumeration, cell parsing)
2. Tier 1-2 features per `acquisition-packs/fods/tier-map.yaml`
3. Comprehensive test suite
4. NuGet packaging configuration
5. DEC-034 independent verification
6. Explicit Gate 11 human approval

## Commercial Licensing

See `acquisition-packs/fods/gate11-commercial-licensing.md`.

## References

- Acquisition pack: `acquisition-packs/fods/`
- Python FOSS source: `src/python/fods/`
- Tier map: `acquisition-packs/fods/tier-map.yaml`
- Gate 11 packaging plan: `acquisition-packs/fods/gate11-packaging-plan.md`
