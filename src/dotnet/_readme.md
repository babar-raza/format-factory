# src/dotnet — Phase 0 Placeholder (Superseded by src/net/)

**Document type:** Directory Orientation — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run011: layout change — production .NET source target is src/net/{format}/)

---

## IMPORTANT: Layout Change

**This directory (`src/dotnet/`) is a Phase 0 placeholder only.** Production .NET product source will NOT be created here.

**The target .NET product layout is format-first:**
```
src/net/{format}/     e.g. src/net/fods/
```

`src/dotnet/open-source/` and `src/dotnet/commercial/` are **obsolete paths** — they must never be created. The old layout has been superseded by the format-first model described in `docs/product-tracks.md` and `docs/architecture.md`.

`src/net/` will be created in Phase 4+ when the first format's .NET product implementation begins (Gate 9 passed + .NET implementation taskcards + explicit Phase 4 .NET implementation execution prompt).

---

## Purpose (Phase 0)

This directory contains only this orientation file. It marks the location of the future .NET product workspace and documents the layout change so agents do not recreate obsolete directory structures.

---

## Target Directory Structure (Phase 4+)

```
src/
  net/
    {format}/           .NET product workspace per format (Phase 4+)
    fods/               Example: FODS format .NET workspace
  dotnet/
    _readme.md          This file only (does not grow further)
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

SDK confirmation status: **Pending (TC-0003 not started).**

---

## Commercial Isolation Rules (Future — applies to src/net/{format}/)

The commercial isolation rules now apply to `src/net/{format}/` (format-first layout). `src/dotnet/commercial/` is an obsolete path and must not be created.

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

Never use `XDocument.Load()` or `XmlDocument.Load()` with default settings on untrusted input. See `docs/security.md` for the full threat model.

---

## Relationship to Other Documents

- `docs/product-tracks.md` — Track 2 (.NET product) definition and format-first layout
- `docs/security.md` — .NET parser security requirements
- `docs/gates.md` — Gate 10 (OSS) and Gate 11 (commercial) criteria
- `taskcards/TC-0003-sdk-baseline.md` — SDK baseline confirmation
