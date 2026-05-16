# ABW Gate 3 Sample Sources
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 3 — Sample Corpus

## Corpus Strategy

Samples are project-owned synthetic plain-XML ABW files generated from
AWML 1.0 format documentation (secondary sources, MobileRead wiki + AbiWord source).

## Samples Created

| Filename | Sample ID | Category | Description | Size |
|----------|-----------|----------|-------------|------|
| minimal-document.abw | abw-minimal-01 | minimal | Single section, one paragraph 'Hello' | 278 bytes |
| two-paragraphs.abw | abw-basic-01 | basic | Two paragraphs with props attributes | 362 bytes |
| empty-section.abw | abw-empty-01 | edge-case | Empty section (no content) | 265 bytes |

All samples:
- License: Apache-2.0 (project-owned)
- Provenance: synthetic, deterministic
- Spec basis: AWML 1.0 (-//ABISOURCE//DTD AWML 1.0 Strict//EN)
- Encoding: plain XML (UTF-8)
- Location: samples/by-format/abw/

## Technical Notes

- DOCTYPE declaration included in each file (per format spec)
- Root: `<abiword template="false" styles="unlocked" version="1.0" fileformat="1.0">`
- Props pattern: CSS-style attribute `props="text-align:left"` on paragraphs
- Files are plain XML parseable with stdlib xml.etree.ElementTree

## External Source Candidates (for future corpus expansion)

1. AbiWord application — can save documents as .abw directly
2. Distrotech/abiword GitHub mirror — contains template .abw files
3. AbiWord docs corpus — user documentation in ABW format (fossies.org)
   Note: Check license before use

For Gate 3 purposes, 3 synthetic samples are sufficient to validate corpus parsing.

GATE_3_SAMPLE_SOURCES: COMPLETE (3 synthetic project-owned ABW samples)
