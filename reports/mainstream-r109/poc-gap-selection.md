# R109 POC Gap Selection

## Selected Gaps (from R108 fresh-mainstream-gaps.md)

### Depth .NET APIs (3 selected)
1. **FODS HasSheet** — Utility API for sheet existence check. Supports defensive programming patterns.
2. **FODT ExportToHtmlFile** — File-based HTML export. Complements ExportToMarkdownFile from R108.
3. **Netpbm Posterize** — Image processing depth. Quantize pixel values to configurable levels.

### FOSS Python (3 selected)
1. **ZST level boundary tests** — Verify behavior at compression level extremes (1, 22)
2. **SYLK roundtrip hardening** — Parse → CSV → re-verify data integrity
3. **PBM edge-case expansion** — Binary format, comment handling, whitespace tolerance

### Deferred to R110+
- FODS formula cell support (complex — needs expression parser)
- FODT table support (complex — needs table element model)
- Netpbm resize with interpolation (algorithmic complexity)
- Color space conversion (RGB↔HSV)
