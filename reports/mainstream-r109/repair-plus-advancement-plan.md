# R109 Repair + Advancement Plan

## Repairs (from R108 evidence quality gap)
1. **Raw log capture:** All R109 test runs must capture stdout/stderr to log files
2. **Source diffs:** Generate diffs for every governed API change
3. **Skill transcripts:** Write /add-dotnet-api skill transcript for each API
4. **R108 regrading:** Upgrade all 13 R108 items with physical file verification + raw proof

## Product Advancement
1. **FODS:** HasSheet(string name) — returns bool, O(1) lookup
2. **FODT:** ExportToHtmlFile(string filePath) — writes HTML to disk
3. **Netpbm:** Posterize(int levels) — quantize pixel values to N levels

## FOSS Advancement
1. **ZST:** Compression level boundary tests + error path hardening
2. **SYLK:** Multi-sheet parsing + CSV roundtrip verification
3. **PBM:** Binary format detection + strict mode edge cases

## Dogfood Pipelines
1. **FODS:** HasSheet + GetColumnCount roundtrip pipeline
2. **FODT:** ExportToHtmlFile + ExportToMarkdownFile consistency check
