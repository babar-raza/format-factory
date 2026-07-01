# Product Tracks

**Document type:** Architecture Reference — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run011: format-first source layout, .NET FOSS packaging deferred)
**Authority:** This document defines the four product tracks, their technology baselines, licensing, and the mechanisms that prevent commercial-tier contamination of open-source releases.

---

## Purpose

The format-factory acquisition pipeline produces output that feeds four distinct product tracks. Each track has its own technology baseline, declared license, visibility classification, and release path. This document defines all four tracks and the rules that keep them isolated from one another.

---

## The Four Tracks

## Source Layout Model

The project uses a **format-first source layout**. Each format that reaches Phase 4 gets its own workspace directory within `src/python/` and `src/net/`.

```
src/
  python/
    _readme.md        [Phase 0 — orientation]
    {format}/         [Phase 4+ — Python FOSS product, one dir per format]
                      Example: src/python/fods/
  net/
    {format}/         [Phase 4+ — .NET product workspace, one dir per format]
                      Example: src/net/fods/
  dotnet/
    _readme.md        [Phase 0 — transitional placeholder; production .NET goes in src/net/]
```

**Obsolete paths (do not create):** `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/`. These were the old layout and are replaced by the format-first structure above. They must not be created.

---

### Track 1: Python FOSS Product

**Technology baseline:** Python 3.11 minimum. Python 3.12 and 3.13 may be tested but 3.11 is the lowest supported version.

**Scope:** Parsers, converters, validators, and importers for all formats that reach Gate 10. Packaged as a Python library, installable via pip. The library does not ship acquisition-layer tooling. **Controlled feature set: Tier 0-4 ceiling.**

**Declared license:** Apache 2.0 (preferred). MIT is an acceptable fallback. The exact license is confirmed per-format at Gate 10.

**Visibility:** `public` after Gate 10 approval.

**Key constraints:**
- No commercial references, namespaces, or feature flags.
- No dependency on proprietary libraries.
- All samples used in tests must have `provenance_status: confirmed` and a compatible open-source license.
- No LLM-generated code without human review and visibility upgraded from `generated` to `public`.

**Source location:** `src/python/{format}/` (created Phase 4+ — after Gate 9 human approval and explicit Phase 4 Python implementation execution prompt). Example: `src/python/fods/`. **Not** `src/python/open-source/`.

---

### Track 2: .NET Product (Commercial/Full-Feature by Default)

**Technology baseline:** Multi-targeted: `net8.0` (LTS) and `net10.0` (LTS). `net9.0` is NOT targeted — .NET 9 reached end-of-life in May 2026.

**Scope:** Full-feature .NET product workspace for each format. Covers Tier 0-6 implementation. Commercial-grade fidelity (Tiers 5-6) is the primary differentiator. May also produce FOSS-tier output — but see the packaging note below.

**Declared license:** Proprietary for commercial tiers. FOSS packaging decision deferred (DEC-033).

**Visibility:** Commercial-tier artifacts are `commercial`. Any FOSS-tier artifacts within this track default to `internal` until DEC-033 is resolved and Gate 10 approves them as `public`.

**Key constraints:**
- `src/net/{format}/` is NOT created until: (1) Gates 1-9 complete, (2) Gate 9 human approval recorded, (3) .NET implementation taskcards exist, and (4) an explicit Phase 4 .NET implementation execution prompt is issued.
- Commercial-tier source within `src/net/{format}/` additionally requires: Gate 10 passed + DD3 resolved + commercial implementation taskcards + explicit commercial implementation execution prompt. Gate 11 is commercial release readiness, not creation authorization.
- All commercial-tier features must be listed in the product mapping (Gate 9) before implementation begins.
- One-way dependency: commercial tiers may reference FOSS tiers; FOSS tiers must never reference commercial tiers.

**Source location:** `src/net/{format}/` (created Phase 4+). Example: `src/net/fods/`. **Not** `src/dotnet/open-source/` or `src/dotnet/commercial/`.

**FOSS packaging note (DEC-033 — deferred):** Whether `src/net/{format}/` produces a separate Apache 2.0-licensed NuGet package (parallel to the Python FOSS track) is not yet decided. This decision must be made before the first .NET release at Gate 10. Until DEC-033 is resolved, the .NET track is treated as commercial/full-feature only.

---

### Track 4: Acquisition Layer (Internal Only)

**Technology baseline:** Python 3.11+ for scripts; shell tools; LibreOffice 7.x for oracle comparison; any format-specific reference tools.

**Scope:** Everything that supports evidence gathering, scoring, prototyping, and testing but is NOT shipped to end users. This includes: scoring scripts (`tools/scoring/`), LLM endpoint client (`tools/llm/`), oracle comparison scripts (`tools/acquisition/`), validation scripts (`tools/validation/`), fuzz harnesses, and prototype parsers in `prototypes/`.

**Declared license:** Internal only — not released.

**Visibility:** `internal` (governance docs, taskcards, acquisition packs, prototypes) or `evidence-only` (spec analysis, legal notes, oracle outputs).

**Key constraints:**
- Acquisition-layer tooling must never be bundled into Track 1 or Track 2 releases.
- Prototype code in `prototypes/by-format/` is reference-only and is never promoted directly to `src/`. Product code is written from scratch with the prototype as a design reference.
- LLM prompts, responses, and agent run records are local-only (`.local/`) and never committed.

---

## Contamination Prevention Mechanisms

Four mechanisms prevent commercial-tier code from appearing in FOSS releases:

### Mechanism 1: Physical Separation Within Format Workspace

Within `src/net/{format}/`, commercial-tier source is physically separated from FOSS-tier source. The exact separation mechanism (separate subdirectories, separate project files, or separate solution files) is defined at Phase 4 time after DEC-033 is resolved. The core rule: no FOSS build artifact may contain commercial-tier source.

### Mechanism 2: CI Boundary Check (Phase 4+)

The CI pipeline includes a boundary check job that:
1. Builds only the FOSS-scope project(s) in a clean environment.
2. Scans all compiled outputs for any reference to commercial namespaces.
3. Fails the build if any commercial reference is found.

Until CI exists (Phase 4+), this check is performed manually at Gate 10.

### Mechanism 3: One-Way Dependency Rule

Commercial tiers may reference FOSS tiers; FOSS tiers must never reference commercial tiers. This is verified at Gate 10 by reviewing all `<ProjectReference>` elements in FOSS project files.

### Mechanism 4: License Header Enforcement

All files containing commercial-tier features carry a proprietary license header. A lint step (Phase 4+) verifies that no file with a proprietary license header appears in the FOSS build output.

---

## Technology Baseline Summary

| Track | Language | Runtime Targets | License | Source Layout |
|---|---|---|---|---|
| Python FOSS | Python 3.11+ | CPython 3.11, 3.12, 3.13 | Apache 2.0 | `src/python/{format}/` |
| .NET product | C# 12+ | net8.0, net10.0 | Commercial (FOSS packaging TBD — DEC-033) | `src/net/{format}/` |
| Acquisition Layer | Python 3.11+ | CPython 3.11+ | Internal only | `tools/`, `acquisition-packs/` |

**Note on .NET 9:** .NET 9 is not targeted because it reached end-of-life in May 2026. Any non-LTS .NET version requires a deliberate decision before it is added as a target. The project always targets the current LTS versions (`net8.0` until it expires; `net10.0` as the successor LTS).

---

## Feature Tier Assignments

Features are assigned to tiers 0-6. Tiers 0-4 are open-source eligible. Tiers 5-6 are commercial-only.

| Tier | Name | Description | Track |
|---|---|---|---|
| 0 | Detect | Identify format by signature/extension | OSS |
| 1 | Metadata | Read document properties, sheet names, author | OSS |
| 2 | Import Core | Read primary data (cell values, text, shapes) | OSS |
| 3 | Export Basic | Write valid minimal output | OSS |
| 4 | Roundtrip | Read + write with full fidelity on reference files | OSS |
| 5 | Commercial Full Fidelity | Complex styles, embedded objects, advanced features | Commercial |
| 6 | Advanced Repair | Recover data from malformed or corrupt files | Commercial |

Tier assignments per format are defined at Gate 9 (Product Mapping). They are recorded in the acquisition pack's delivery plan section and in `registry/format-registry.yaml`.

---

## Release Path by Track

| Track | Release Gate | Release Type | Manifest Required |
|---|---|---|---|
| Python FOSS (`src/python/{format}/`) | Gate 10 | PyPI package | Yes |
| .NET FOSS subset (if DEC-033 resolved) | Gate 10 | NuGet package (Apache 2.0) | Yes |
| .NET Commercial tiers (`src/net/{format}/`) | Gate 11 | NuGet package (commercial) | Yes |
| Acquisition Layer | Never | Not released | N/A |

Release manifests list all artifacts included in the release with their visibility, license, and provenance status. No release proceeds without a human-reviewed manifest. The manifest generator is TC-0006 scope (Phase 3+). Until TC-0006 exists, manifests are created manually.

---

## Relationship to Other Documents

- `docs/architecture.md` — overall system structure and folder layout
- `docs/release-control.md` — visibility classification and release policy
- `docs/legal-and-licensing.md` — license requirements and format legal categories
- `docs/gates.md` — Gate 10 and Gate 11 pass criteria
- `docs/acquisition-workflow.md` — how formats move through the pipeline to product
