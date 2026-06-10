# Parser Defects and Limitations
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Summary

The spec parser (`tools/specification-authority-layer/spec_parser.py`) functioned correctly
for all 4 pilot sources. No blocking defects were found. The following limitations are
documented for Pilot R2 planning.

## Parse Results

| Source | Parse Method | Sections | Status |
|--------|-------------|----------|--------|
| src-zst-rfc8878 | plain_text | 5 | OK |
| src-netpbm-spec | plain_text | 5 | OK |
| src-dif-empirical | plain_text | 5 | OK |
| src-fods-odf | plain_text | 5 | OK |

## Limitations

### L-PARSER-001 — No Markdown heading detection for fixture sources
All 4 pilot sources are plain text fixtures (no `#` headings). The parser auto-detects
`plain_text` mode. For actual RFC text (with numbered sections like "1.1 Frame Format"),
the plain_text mode groups lines into sections by double-newline which may split
a single logical section.
- **Severity:** LOW (fixture-based pilot; real RFC text deferred to R2)
- **Impact:** Section boundaries may be suboptimal for real RFC text
- **Mitigation for R2:** Implement RFC-section detection (numbered section headings)

### L-PARSER-002 — Section heading extraction from plain text is heuristic
The plain_text parser uses line content as heading, which produces truncated headings
for long paragraphs. This can make the `search_index()` results less precise.
- **Severity:** LOW
- **Impact:** Index search quality reduced; requirement extraction still functions correctly
- **Mitigation for R2:** Add a `heading` extraction pass for structured plain text

### L-PARSER-003 — No multi-format support (HTML, PDF)
The parser only handles plain text and Markdown. Real RFC sources from tools.ietf.org
may be fetched as HTML or plain text. PDF format not supported.
- **Severity:** MEDIUM (blocks real RFC fetch in R2)
- **Impact:** R2 must fetch RFC as plain text; HTML fetch requires stripping
- **Mitigation for R2:** Add HTML→plain text stripping step in vault ingest

## Defects

No blocking defects found during Pilot R1. Parser produced valid artifacts for all 4 sources.

## Verdict

`PARSER_FUNCTIONAL_FOR_FIXTURE_PILOT — LIMITATIONS_DOCUMENTED_FOR_R2`
