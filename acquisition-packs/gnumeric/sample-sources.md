# Gnumeric Gate 3 Sample Sources
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 3 — Sample Corpus

## Corpus Strategy

Samples are project-owned synthetic gzip-compressed XML files generated from
the Gnumeric v10 XSD schema documentation. No external downloads required.

## Samples Created

| Filename | Sample ID | Category | Description | Size |
|----------|-----------|----------|-------------|------|
| minimal-spreadsheet.gnumeric | gnumeric-minimal-01 | minimal | Single cell 'Hello' in Sheet1 | 307 bytes |
| multi-cell-basic.gnumeric | gnumeric-multi-01 | basic | 2x2 grid: Name/Score + Alice/42 | 337 bytes |
| empty-sheet.gnumeric | gnumeric-empty-01 | edge-case | Empty sheet (no cells) | 264 bytes |

All samples:
- License: Apache-2.0 (project-owned)
- Provenance: synthetic, deterministic
- Spec basis: Gnumeric XSD v10 (http://www.gnumeric.org/v10.dtd)
- Encoding: gzip-compressed XML
- Location: samples/by-format/gnumeric/

## Technical Notes

- Files generated using Python `gzip` module with `mtime=0` for determinism
- XML namespace: `xmlns:gnm="http://www.gnumeric.org/v10.dtd"`
- ValueType 60 = string, ValueType 40 = integer (from XSD schema)
- Files are valid gzip archives decompressible with gunzip/zcat

## External Source Candidates (for future corpus expansion)

1. GNOME project example files (if available under permissive license)
2. LibreOffice save-as gnumeric test files
3. Gnumeric application test suite (GPL-2.0 — would need clean-room separation)

For Gate 3 purposes, 3 synthetic samples are sufficient to validate corpus parsing.

GATE_3_SAMPLE_SOURCES: COMPLETE (3 synthetic project-owned Gnumeric samples)
