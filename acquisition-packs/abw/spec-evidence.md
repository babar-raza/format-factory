# ABW Gate 2 Spec Evidence
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 2 — Spec Retrieval

## Spec Retrieval Summary

ABW uses AWML (AbiWord Markup Language) 1.0. The primary DTD is at abisource.com which was
unreachable during this retrieval attempt. Spec understanding derived from secondary sources.

## Primary Spec: AWML 1.0 DTD

| Field | Value |
|-------|-------|
| Spec name | AbiWord Markup Language (AWML) 1.0 Strict |
| Public identifier | `-//ABISOURCE//DTD AWML 1.0 Strict//EN` |
| DTD URL | http://www.abisource.com/awml.dtd |
| Access date | 2026-05-16 |
| Retrieval status | **BLOCKED — abisource.com ECONNREFUSED** |
| Cache path | .local/spec-cache/abw/awml-1.0/spec-index.yaml |

## Secondary Sources (Retrieved Successfully)

| Source | URL | Status |
|--------|-----|--------|
| MobileRead Wiki ABW | https://wiki.mobileread.com/wiki/ABW | RETRIEVED |
| AbiWord GitHub repo | https://github.com/AbiWord/abiword | ACCESSIBLE |
| XML Matters article | https://gnosis.cx/publish/programming/xml_matters_33.html | RETRIEVED |

## Key Format Structure (from secondary sources)

### Root Element
```xml
<!DOCTYPE abiword PUBLIC "-//ABISOURCE//DTD AWML 1.0 Strict//EN" "http://www.abisource.com/awml.dtd">
<abiword template="false" styles="unlocked" version="1.0" fileformat="1.0" xml:lang="en-US">
```

### Key Namespaces
- `fo` — XSL Formatting Objects
- `math` — MathML
- `svg` — SVG graphics
- `dc` — Dublin Core metadata
- `xlink` — XLink references

### Key Elements
- `<abiword>` — root element with version/fileformat attributes
- `<styles>` — style definitions
- `<pagesize>` — page dimensions
- `<section>` — document sections
- `<p>` — paragraphs (with `style` and `props` attributes)
- `<c>` — character runs (inline styling via `props`)
- `<image>` — Base64-encoded inline images
- `<table>`, `<cell>` — table structures
- `<metadata>` — Dublin Core metadata

### Props Attribute Pattern
AbiWord uses a CSS-like `props` attribute for formatting:
```xml
<p props="text-align:left; margin-bottom:12pt; font-size:12pt">text</p>
```

## Spec Quality Assessment

| Criterion | Status |
|-----------|--------|
| DTD accessible | NO (abisource.com down) |
| Spec understanding from secondary | ADEQUATE |
| Format stability | STABLE (AbiWord format unchanged for years) |
| Documentation quality | LIMITED (DTD outdated, secondary sources sufficient) |
| Source code reference | AVAILABLE (AbiWord GitHub) |

## Gate 2 Outcome

Spec retrieval: **PASSED_WITH_NOTES** — DTD not downloadable (abisource.com down),
but format structure is sufficiently documented from secondary sources for acquisition
and prototype planning. Legal category 2 (minor gap). AbiWord source code is the
authoritative reference for implementation.

GATE_2_SPEC_EVIDENCE: PASSED_WITH_NOTES (DTD unreachable; secondary sources sufficient)
