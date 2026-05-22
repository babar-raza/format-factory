# R49 Export-Format Acquisition Ranking

**Sprint:** FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
**Lane:** MT8
**Date:** 2026-05-22

---

## Purpose

Rank export target formats by acquisition value, implementation difficulty, and strategic fit.
This drives which export paths to implement next in the Format Factory pipeline.

---

## Tier 1: Immediate (already exist in codebase)

These exporters are ALREADY IMPLEMENTED in `.NET`:

| Target format | Source | .NET exporter | Status |
|--------------|--------|--------------|--------|
| CSV | FODS | `FodsCsvExporter.cs` | COMPLETE |
| JSON | FODS | `FodsJsonExporter.cs` | COMPLETE |
| HTML | FODS | `FodsHtmlExporter.cs` | COMPLETE |
| TXT | FODT | `FodtTxtExporter.cs` | COMPLETE |
| Markdown | FODT | `FodtMarkdownExporter.cs` | COMPLETE |
| HTML | FODT | `FodtHtmlExporter.cs` | COMPLETE |

These Tier 1 paths require no additional acquisition work.

---

## Tier 2: Short-Win Python Exports (implement from neutral model)

| Target | Source | Effort | Value | Priority |
|--------|--------|--------|-------|----------|
| CSV | FODS (Python) | Very low | High | **#1** — straightforward from neutral model `sheets[].rows[].cells[].value` |
| TXT | FODT (Python) | Very low | High | **#2** — trivial join of `blocks[].text` |
| Markdown | FODT (Python) | Low | High | **#3** — headings → `##`, paragraphs → plain text |
| JSON | FODS (Python) | Low | Medium | **#4** — dump neutral model as JSON |

Python Tier 2 exports are ideal for dogfooding: use Format Factory Python writer → then Python exporter.

---

## Tier 3: Dogfooding Exports (prove library self-consumption)

| Chain | Proof value |
|-------|-------------|
| FODS neutral model → write_fods() → FodsCsvExporter | Proves Python writer output consumed by .NET |
| FODT neutral model → write_fodt() → FodtTxtExporter | Proves Python writer output consumed by .NET |
| FODS neutral model → Python CSV exporter | Proves Python-to-Python pipeline |
| FODT neutral model → Python TXT exporter | Proves Python-to-Python pipeline |

Dogfooding target: R50 sprint.

---

## Tier 4: Long-Train Targets (require external libraries)

| Target | Difficulty | Dependencies | Strategic value |
|--------|-----------|-------------|----------------|
| PDF (from FODT) | High | reportlab / fpdf2 | Commercial priority (documents) |
| PDF (from FODS) | High | reportlab / fpdf2 | Commercial priority (spreadsheets) |
| XLSX (from FODS) | High | openpyxl or custom | High interoperability |
| DOCX (from FODT) | High | python-docx or custom | High interoperability |
| SVG (from FODS) | Very high | custom renderer | Niche |
| PNG/JPEG (rasterize) | Very high | Pillow + renderer | Niche |

Tier 4 targets require gate review before acquisition.

---

## Acquisition Ranking Summary

| Rank | Format | Source | Track | Sprint target |
|------|--------|--------|-------|--------------|
| 1 | CSV | FODS Python | Python FOSS | R50 |
| 2 | TXT | FODT Python | Python FOSS | R50 |
| 3 | Markdown | FODT Python | Python FOSS | R50 |
| 4 | JSON | FODS Python | Python FOSS | R51 |
| 5 | PDF | FODT .NET | .NET commercial | R52+ (after G11-G) |
| 6 | XLSX | FODS .NET | .NET commercial | R52+ (after G11-G) |
| 7 | DOCX | FODT .NET | .NET commercial | R52+ (after G11-G) |

---

## Gate Requirements for New Export Formats

New export formats do NOT require full Gate 1-11 cycle if they are purely derived outputs:
- Python export: requires test proving neutral-model → export file chain
- .NET export: requires G11-E (exporter) sub-gate evidence
- All exports: commercial_product_ready: false until G11-G approval

---

## Recommendation

Implement Python CSV (FODS) and Python TXT/Markdown (FODT) exporters in R50 as Tier 2 quick-wins.
These prove the dogfooding story (Python write → Python export) and give immediate user value.
Defer Tier 4 (PDF/XLSX/DOCX) until after Gate 11 G11-G approval.
