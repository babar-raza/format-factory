# R69 Work-Ahead W2 — R70/R71 Next-Format Queue

Sprint: FORMAT-FACTORY-R69-FINAL-DELIVERY-SEAL-RC-CLOSURE-WORKAHEAD-MEGA-TRAIN-001
Date: 2026-05-27

## Top 4 Parser/Prototype Candidates

| Rank | Format | Rationale |
|---|---|---|
| 1 | XLSX (Office Open XML Spreadsheet) | Public spec (ECMA-376); XML-package; high demand; Python openpyxl available |
| 2 | HTML | Universal spec (W3C); lightweight parser; complements FODS text export |
| 3 | RTF (Rich Text Format) | Public spec (Microsoft RTF 1.9); widely used; complements FODT |
| 4 | Markdown | De facto spec; text-based; natural complement to FODT text export |

## Top 4 Package/Readiness Candidates

| Rank | Format | Current Gate | Next Step |
|---|---|---|---|
| 1 | ODS | Gate 7 | Gate 8 security review (awaiting human approval) |
| 2 | ODT | Gate 7 | Gate 8 security review (awaiting human approval) |
| 3 | CSV | Gate 8 | Gate 9 local release candidate |
| 4 | TSV | Gate 8 | Gate 9 local release candidate |

## Top 4 Fixture/Sample Gaps

| Format | Gap | Action |
|---|---|---|
| XLSX | No acquisition pack, no samples | Create acquisition-packs/xlsx/ in R70 |
| HTML | No parser, no samples | Parser scaffold in R70 |
| RTF | No parser, no samples | Parser scaffold in R71 |
| ODS/ODT | Gate 8 samples need review | Human IV required per DEC-034 |

## Gate Status (No Changes)

No gate status was changed by this work-ahead lane. All rankings are analysis only.

NEXT_FORMAT_QUEUE: PREPARED
