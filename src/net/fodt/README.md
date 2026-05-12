# FormatFactory.Fodt — .NET Commercial Parser (Skeleton)

## Status: Gate 11 Skeleton — NOT Release-Ready

This is a **commercial-only** .NET skeleton for the FODT (Flat OpenDocument Text)
parser. Created during DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001 (2026-05-12).

**Gate 11 has NOT been approved.** Full implementation is required before Gate 11
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

Tier 0 skeleton:

- `FodtParser.cs`: `GetParagraphCount()` validates XML well-formedness only
- Paragraph extraction: NOT IMPLEMENTED
- List traversal (iterative DFS): NOT IMPLEMENTED
- Iterparse streaming equivalent: NOT IMPLEMENTED
- Reference for algorithm: `src/python/fodt/list_traversal.py`

## What Remains for Gate 11

1. .NET 10 SDK installation (machine blocker)
2. Full Tier 0 parser implementation
3. Tier 1-2 features per `acquisition-packs/fodt/tier-map.yaml`
4. Test project (`tests/net/fodt/`)
5. NuGet packaging configuration
6. Commercial license confirmed
7. DEC-034 independent verification
8. Explicit Gate 11 human approval

## Commercial Licensing

See `acquisition-packs/fodt/gate11-commercial-licensing.md`.

## References

- Acquisition pack: `acquisition-packs/fodt/`
- Python FOSS source: `src/python/fodt/`
- Tier map: `acquisition-packs/fodt/tier-map.yaml`
- Gate 11 packaging plan: `acquisition-packs/fodt/gate11-packaging-plan.md`
