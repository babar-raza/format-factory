# R23 ODS Acquisition Lane Report — Gates 1-3
# Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-PYTHON-PUBLICATION-DRYRUN-GATE11-HARDENING-NEXT-FORMATS-AND-PLAYBOOK-REPAIR-001
# Date: 2026-05-17
# Status: Gate 1 DELEGATED_PASS, Gate 2 FAST_PATH, Gate 3 PLANNED
# Awaiting human IV per DEC-034

## Format Identity

| Field        | Value                                         |
|--------------|-----------------------------------------------|
| format_id    | ods                                           |
| display_name | OpenDocument Spreadsheet                      |
| extensions   | .ods                                          |
| mime_type    | application/vnd.oasis.opendocument.spreadsheet|
| family       | cells                                         |
| spec_body    | OASIS Open Document Format TC                 |
| spec_version | ODF 1.3 (ISO/IEC 26300-3:2021)                |
| legal_cat    | 1 (Open Standard Royalty-Free)                |

## Gate 1 — Scoring Summary

Score: 88/100 → normalized 8.8/10 → Band: **Accept** (threshold 7.0)

| Criterion              | Score | Points | Evidence                                                                |
|------------------------|-------|--------|-------------------------------------------------------------------------|
| legal_safety           | 3     | 30     | OASIS ODF 1.3 RF. Same legal basis as FODS (already Gate 1 approved)   |
| spec_availability      | 3     | 20     | ODF 1.3 spec already in local spec cache — FAST_PATH eligible          |
| parseable_structure    | 2     | 14     | ZIP+XML container. Standard zipfile + ElementTree approach              |
| community_demand       | 3     | 15     | Most-deployed ODF spreadsheet. LibreOffice default since 2012           |
| strategic_track_value  | 3     | 9      | ODF cells family — direct family extension from FODS                   |

Approval: delegated_agent_r23 (2026-05-17) — awaiting human IV per DEC-034.

## Gate 2 — Spec Evidence (Fast-Path)

Fast-path authorized: ODF 1.3 spec already acquired for FODS (Gate 2 PASSED 2026-05-05).

| Spec Item               | Status         | Notes                                                     |
|-------------------------|----------------|-----------------------------------------------------------|
| ODF 1.3 Part 3 content  | CACHED         | .local/spec-cache/fods/1.3/ — same spec as FODS          |
| ODF 1.3 ZIP container   | DOCUMENTED     | Part 2 package structure (mimetype, content.xml, etc.)   |
| Patent search           | WAIVED         | Same RF basis as FODS — no new patent risk                |
| Legal category          | 1              | OASIS royalty-free — confirmed same authority             |

Container structure (ODS ZIP):
```
mimetype          (first file, uncompressed: "application/vnd.oasis.opendocument.spreadsheet")
META-INF/
  manifest.xml   (file list)
content.xml      (spreadsheet data — same schema as FODS body)
styles.xml       (styles — optional)
meta.xml         (document metadata — optional)
settings.xml     (application settings — optional)
Thumbnails/      (optional)
```

Key parsing difference from FODS: zipfile.ZipFile required to extract content.xml before XML parsing.
Core XML schema: identical to FODS — `table:table`, `table:table-row`, `table:table-cell`.

## Gate 3 — Sample Corpus Plan

Gate 3 samples: planned for R24 sprint.

| Sample Source                | License     | Status     | Notes                                       |
|------------------------------|-------------|------------|---------------------------------------------|
| Synthetic via LibreOffice    | Apache-2.0  | planned_r24| Save as ODS from FODS reference samples     |
| Synthetic via Python odfpy   | Apache-2.0  | planned_r24| odfpy MIT-licensed for generation           |
| Reference ODS from odfpy tests| Apache-2.0 | planned_r24| odfpy test suite contains valid ODS samples |

Minimum corpus: 3 samples covering: minimal spreadsheet, multi-sheet, formula-containing sheet.
All synthetic (project-owned, Apache-2.0).

## Strategic Assessment

- ODS is the container-format sibling of FODS (already Gates 1-10 passed)
- Same ODF schema, same OASIS RF legal basis
- Parser implementation: add zipfile extraction layer on top of existing FODS parser logic
- Implementation complexity: LOW — existing FODS parser reusable with thin container wrapper
- Aspose supports ODS — differentiates by being FOSS/Apache-2.0 alternative

## Next Steps (Not Authorized in R23)

1. Human IV of Gate 1 delegated decision (DEC-034)
2. Gate 3 sample corpus creation (R24)
3. Gate 4 parser prototype (reuse FodsParser + zipfile layer)
4. Gate 5 neutral model (reuse FODS neutral model with container additions)

## Invariants

- commercial_product_ready: false
- publication_authorized: false
- No implementation work authorized until Gates 1-3 human IV complete
