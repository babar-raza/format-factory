# src/python — Python Open-Source Product (Format-First Layout)

**Document type:** Directory Orientation — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run011: layout change — production Python source target is src/python/{format}/)

---

## IMPORTANT: Layout Change

**This directory (`src/python/`) is a Phase 0 placeholder only.** Production Python product source will NOT be created in a flat `open-source/` subdirectory.

**The target Python product layout is format-first:**
```
src/python/{format}/     e.g. src/python/fods/
```

`src/python/open-source/` is an **obsolete path** — it must never be created. The old layout has been superseded by the format-first model described in `docs/product-tracks.md` and `docs/architecture.md`.

`src/python/` subdirectories will be created in Phase 4+ when the first format's Python product implementation begins (Gate 9 passed + Python implementation taskcards + explicit Phase 4 Python implementation execution prompt).

---

## Purpose

This directory contains the Python open-source product: production-quality parsers, converters, validators, and importers/exporters for all formats that have reached Gate 10. This is Track 1 of the four product tracks defined in `docs/product-tracks.md`.

---

## Target Directory Structure (Phase 4+)

```
src/
  python/
    {format}/           Python FOSS product workspace per format (Phase 4+)
    fods/               Example: FODS format Python workspace
      format_factory_fods/   Main package
      tests/                 Product tests
      pyproject.toml
  dotnet/
    _readme.md          Phase 0 placeholder only (see src/net/ for .NET product)
```

---

## Technology Baseline

| Property | Value |
|---|---|
| Minimum Python version | 3.11 |
| Tested Python versions | 3.11, 3.12, 3.13 (CI verifies all three) |
| Key security library | defusedxml (for any XML-based format) |
| License | Apache 2.0 (default); MIT if Apache creates dependency issues |
| Package format | pyproject.toml + pip-installable wheel |

**Note:** The developer machine runs Python 3.13.2. Product code targets Python 3.11+ for broadest adoption. Tests must pass on Python 3.11, 3.12, and 3.13. TC-0003 confirms the baseline.

---

## SDK Baseline Confirmation (TC-0003)

TC-0003 (Phase 1) verifies:
- Python 3.11 is available for CI baseline testing.
- `defusedxml` is pip-installable.
- Core XML library (`xml.etree.ElementTree`) behaves as expected on the target Python version.

SDK confirmation status: **Pending (TC-0003 not started).**

---

## Product vs. Prototype

Product code in `src/python/{format}/` is written from scratch in Phase 4+. It does NOT come from the prototype in `prototypes/by-format/`. The prototype demonstrates feasibility; the product is a clean implementation using the prototype as a design reference.

---

## Security Requirements

All parsers in this directory must comply with the threat model in `docs/security.md`. For XML-based formats:
- Use `defusedxml` for any XML parsing of untrusted input.
- Never use `xml.etree.ElementTree` with default settings on untrusted file input.
- Set `huge_tree=False` and `resolve_entities=False` if using `lxml` directly.
- Implement memory limits: reject files above 256 MB for text formats.

---

## Visibility

All production source files are `visibility: public` after Gate 10 approval. Before Gate 10, source files in this directory are `visibility: internal`.

---

## Relationship to Other Documents

- `docs/product-tracks.md` — Track 1 definition, technology baseline, license policy
- `docs/security.md` — parser security requirements
- `docs/gates.md` — Gate 10 (OSS readiness) pass criteria
- `taskcards/TC-0003-sdk-baseline.md` — SDK baseline confirmation
