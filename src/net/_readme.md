# src/net/ — .NET Product Source Root

**Canonical .NET product directory.** Each format implementation lives at `src/net/{format}/`.

**Authority:** `registry/repository-layout.yaml` — language ID `dotnet` maps to `src/net/`.
**Resolver:** `tools/supervisor/path_resolver.py` — use `resolve_product_path("dotnet", format_id)`.
**Validator:** V110 (`governance_validators_path.py`) blocks sprints that reference prohibited paths.

---

## Active Format Directories

| Format | Path | .csproj |
|---|---|---|
| csv | `src/net/csv/` | `FormatFactory.Csv.csproj` |
| fods | `src/net/fods/` | `FormatFactory.Fods.csproj` |
| fodt | `src/net/fodt/` | `FormatFactory.Fodt.csproj` |
| html | `src/net/html/` | `FormatFactory.Html.csproj` |
| markdown | `src/net/markdown/` | `FormatFactory.Markdown.csproj` |
| ndjson | `src/net/ndjson/` | `FormatFactory.Ndjson.csproj` |
| netpbm | `src/net/netpbm/` | `FormatFactory.Netpbm.csproj` |
| tsv | `src/net/tsv/` | `FormatFactory.Tsv.csproj` |
| txt | `src/net/txt/` | `FormatFactory.Txt.csproj` |
| zst | `src/net/zst/` | `FormatFactory.Zst.csproj` |

---

## Layout per format

```
src/net/{format}/
  {Format}Document.cs    # domain model (≤800 LOC per V78)
  {Format}Parser.cs      # parse-only
  {Format}Writer.cs      # write-only (where applicable)
  Model/                 # supporting model classes
  Exceptions/            # exception hierarchy
  Spec/                  # architecture_only spec stubs (V73 validates SpecQName)
  bin/                   # build output (gitignored)
  obj/                   # build intermediates (gitignored)
```

---

## Technology Baseline

| Property | Value |
|---|---|
| Target frameworks | net8.0, net10.0 (multi-targeted) |
| .NET 9 | NOT TARGETED — .NET 9 reached EOL in May 2026 |
| Developer SDK | 9.0.200 (can compile net8.0 and net10.0 targets) |
| Key XML library | System.Xml with XmlReaderSettings |
| FOSS-tier license | Apache 2.0 (if .NET FOSS packaging resolved — DEC-033) |
| Commercial license | Proprietary (decided at Gate 11) |

**Note on .NET 9:** .NET 9 is a non-LTS release that reached end-of-life in May 2026. It is explicitly excluded from targets. Only net8.0 (LTS) and net10.0 (LTS) are supported.

---

## SDK Baseline Confirmation (TC-0003)

TC-0003 (Phase 1) verifies:
- .NET SDK 9.0.200 can produce net8.0 and net10.0 binaries.
- net10.0 SDK availability is confirmed or documented.
- `System.Xml.XmlReaderSettings` with `DtdProcessing.Prohibit` is available in net8.0 target.

SDK confirmation status: **Confirmed (TC-0003 completed 2026-06-18).**
- Developer machine: .NET SDK 10.0.204 (also has 9.0.200)
- net8.0 and net10.0 targets compile and test successfully (617 FODS tests pass)
- `dotnet --list-sdks` confirms: 9.0.200 and 10.0.204 both available

---

## Commercial Isolation Rules (applies to src/net/{format}/)

Within `src/net/{format}/`, the FOSS and commercial isolation mechanism is deferred to Phase 4 design (DEC-033). The principles are:
1. Physical or logical separation between FOSS-tier and commercial-tier source within `src/net/{format}/`.
2. Any open-source packaging must not include commercial-tier source.
3. CI (Phase 4+) builds FOSS tiers in isolation and verifies zero commercial namespace references.
4. One-way dependency: commercial tiers may reference FOSS tiers; FOSS tiers must never reference commercial tiers.

---

## Security Requirements

All .NET parsers must use `XmlReaderSettings` with:
- `DtdProcessing = DtdProcessing.Prohibit`
- `XmlResolver = null`
- `MaxCharactersFromEntities = 10000` (for DTD entity expansion protection)

Never use `XDocument.Load()` or `XmlDocument.Load()` with default settings on untrusted input. See `docs/governance/security.md` for the full threat model.

---

## Relationship to Other Documents

- `docs/product-factory/product-tracks.md` — Track 2 (.NET product) definition and format-first layout
- `docs/governance/security.md` — .NET parser security requirements
- `docs/gates.md` — Gate 10 (OSS) and Gate 11 (commercial) criteria
- `taskcards/TC-0003-sdk-baseline.md` — SDK baseline confirmation
- `registry/repository-layout.yaml` — Canonical path authority
- `tools/supervisor/path_resolver.py` — Path resolution utility

## Build Verification Note

Always use `dotnet build --no-incremental` for correctness verification.
Incremental builds can mask missing declarations (confirmed TC-PQLM-021, 2026-07-03).
