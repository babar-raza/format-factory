# R85 Train O — Dogfood Export Map

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Purpose

Authoritative per-format, per-track dogfood export coverage matrix as of R85.

## Matrix

| Format | Track | Export Target | Dogfood Status | Write Backend | Notes |
|--------|-------|--------------|---------------|---------------|-------|
| FODS | Python | (read/parse only — no export) | NOT_APPLICABLE | — | FODS→CSV not yet implemented |
| FODT | Python | TXT | IMPLEMENTED | document_to_text (FF neutral_model) | fodt/neutral_model.py |
| FODT | .NET | TXT | GAP_DOGFOOD_EXTERNAL | FodtTxtExporter (raw write) | No FF .NET text lib yet |
| FODT | .NET | HTML | GAP_DOGFOOD_EXTERNAL | FodtHtmlExporter (raw write) | No FF .NET HTML lib yet |
| FODT | .NET | Markdown | GAP_DOGFOOD_EXTERNAL | FodtMarkdownExporter (raw write) | No FF .NET MD lib yet |
| PBM | Python | PGM | IMPLEMENTED | write_pgm (FF pgm library) | pbm/pbm_to_pgm.py; R85 Train M |
| PBM | .NET | PGM | IMPLEMENTED | NetpbmWriter (FF netpbm) | NetpbmExporter.PbmToPgm; R85 Train K |
| PBM | .NET | PPM | IMPLEMENTED | NetpbmWriter (FF netpbm) | NetpbmExporter.PbmToPpm; R85 Train K |
| SYLK | Python | CSV | IMPLEMENTED | sylk_to_csv (FF SYLK parser; no extern) | sylk/sylk_to_csv.py; R84 |
| ZST | Python | (decompress only) | NOT_APPLICABLE | — | ZST is compression layer |
| DIF | Python | CSV | NOT_IMPLEMENTED | — | HOLD until SYLK POC complete |

## IMPLEMENTED Count

Python IMPLEMENTED: 3 (FODT→TXT, PBM→PGM, SYLK→CSV)
.NET IMPLEMENTED: 2 (PBM→PGM, PBM→PPM)
GAP_DOGFOOD_EXTERNAL: 3 (.NET FODT→TXT/HTML/MD)
NOT_IMPLEMENTED: 1 (DIF→CSV, on hold)
NOT_APPLICABLE: 2 (ZST, FODS read-only)

## Enforcement Tests

| Test File | What It Checks |
|-----------|---------------|
| tests/python/netpbm/test_r85_pbm_to_pgm_dogfood.py | No PIL/cv2; uses write_pgm |
| tests/python/sylk/test_r84_sylk_to_csv.py | Verifies sylk_to_csv produces valid CSV |
| tests/net/netpbm/NetpbmExporterTests.cs | PbmToPgm + PbmToPpm use FF model |

## Gap Remediation Backlog

| Gap ID | Description | Prerequisite | Target Sprint |
|--------|-------------|-------------|--------------|
| GAP-DOGFOOD-NET-TXT-001 | FODT .NET TXT exporter uses raw write | .NET text FF library | R87+ |
| GAP-DOGFOOD-NET-HTML-001 | FODT .NET HTML exporter uses raw write | .NET HTML FF library | R88+ |
| GAP-DOGFOOD-NET-MD-001 | FODT .NET Markdown exporter uses raw write | .NET MD FF library | R88+ |
| GAP-DOGFOOD-DIF-CSV-001 | DIF→CSV not implemented | SYLK POC complete | R86 |

## TRAIN_O_STATUS: COMPLETE
