# R107 Deep Product Strategy

## Guiding Principle
R107 prioritizes **depth over breadth**: save/export/dogfood/object-model capabilities over shallow helper APIs.

## Lane A — FODS
1. **RemoveSheet** — Complete sheet lifecycle (Add/Rename/Copy/Clear/Remove)
2. **ExportSheetToCsv** — CSV export is a key missing export path

## Lane B — FODT
1. **ReplaceText hardening** — ReplaceText exists but needs boundary/edge tests
2. **ExportToPlainText** — Plain text export complements HTML/Markdown

## Lane C — Netpbm
1. **GetHistogram** — Image analysis depth (pixel frequency distribution)
2. **ExtractChannel** — PPM channel extraction for analysis pipelines

## FOSS Strategy
- ZST: dependency isolation + streaming proof
- Python Netpbm: PPM<->PGM conversion hardening
- SYLK: CSV export edge cases
- DIF: roundtrip proof
- PBM: binary P4 roundtrip

## Dogfood Strategy
- FODS->CSV pipeline (new ExportSheetToCsv)
- FODT->TXT pipeline (new ExportToPlainText)
- Netpbm histogram analysis pipeline
- SYLK->CSV export pipeline

## Depth Accounting
- 4/6 commercial APIs are save/export/dogfood/object-model-depth: PASS
- 2/6 are query/analysis (GetHistogram, ExtractChannel): within 2-shallow limit
