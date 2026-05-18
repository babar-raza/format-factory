# R23 ODT Acquisition Lane Report — Gates 1-3
# Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-PYTHON-PUBLICATION-DRYRUN-GATE11-HARDENING-NEXT-FORMATS-AND-PLAYBOOK-REPAIR-001
# Date: 2026-05-17
# Status: Gate 1 DELEGATED_PASS, Gate 2 FAST_PATH, Gate 3 PLANNED
# Awaiting human IV per DEC-034

## Format Identity

| Field        | Value                                           |
|--------------|-------------------------------------------------|
| format_id    | odt                                             |
| display_name | OpenDocument Text                               |
| extensions   | .odt                                            |
| mime_type    | application/vnd.oasis.opendocument.text         |
| family       | words                                           |
| spec_body    | OASIS Open Document Format TC                   |
| spec_version | ODF 1.3 (ISO/IEC 26300-3:2021)                  |
| legal_cat    | 1 (Open Standard Royalty-Free)                  |

## Gate 1 — Scoring Summary

Score: 88/100 → normalized 8.8/10 → Band: **Accept** (threshold 7.0)

| Criterion              | Score | Points | Evidence                                                                |
|------------------------|-------|--------|-------------------------------------------------------------------------|
| legal_safety           | 3     | 30     | OASIS ODF 1.3 RF. Same legal basis as FODT (already Gate 1 approved)   |
| spec_availability      | 3     | 20     | ODF 1.3 spec already in local spec cache — FAST_PATH eligible          |
| parseable_structure    | 2     | 10     | ZIP+XML container. Standard zipfile + ElementTree approach              |
| community_demand       | 3     | 15     | Most-deployed ODF text format. LibreOffice Writer default               |
| strategic_track_value  | 2     | 7      | ODF words family — direct container variant of FODT                    |
| implementation_complexity | 2  | 3      | ZIP container adds layer vs FODT flat XML; manageable with stdlib       |
| family_overlap         | 2     | 3      | Same family as FODT but distinct structure/MIME/deployment scope        |

Approval: delegated_agent_r23 (2026-05-17) — awaiting human IV per DEC-034.

## Gate 2 — Spec Evidence (Fast-Path)

Fast-path authorized: ODF 1.3 spec already acquired for FODT (Gate 2 PASSED 2026-05-08).

| Spec Item               | Status         | Notes                                                     |
|-------------------------|----------------|-----------------------------------------------------------|
| ODF 1.3 Part 3 content  | CACHED         | .local/spec-cache/fods/1.3/ — same spec as FODT          |
| ODF 1.3 ZIP container   | DOCUMENTED     | Part 2 package structure (mimetype, content.xml, etc.)   |
| Patent search           | WAIVED         | Same RF basis as FODT — no new patent risk                |
| Legal category          | 1              | OASIS royalty-free — confirmed same authority             |

Container structure (ODT ZIP):
```
mimetype          (first file, uncompressed: "application/vnd.oasis.opendocument.text")
META-INF/
  manifest.xml   (file list)
content.xml      (document body — same schema as FODT body)
styles.xml       (styles — optional)
meta.xml         (document metadata — optional)
settings.xml     (application settings — optional)
Thumbnails/      (optional)
Pictures/        (embedded images — optional)
```

Key parsing difference from FODT: zipfile.ZipFile required to extract content.xml before XML parsing.
Core XML schema: identical to FODT — `text:h`, `text:p`, `text:list`, `table:table`.

## Gate 3 — Sample Corpus Plan

Gate 3 samples: planned for R24 sprint.

| Sample Source                | License     | Status     | Notes                                         |
|------------------------------|-------------|------------|-----------------------------------------------|
| Synthetic via LibreOffice    | Apache-2.0  | planned_r24| Save as ODT from FODT reference samples       |
| Synthetic via Python odfpy   | Apache-2.0  | planned_r24| odfpy MIT-licensed for generation             |
| Reference ODT from odfpy tests| Apache-2.0 | planned_r24| odfpy test suite contains valid ODT samples   |

Minimum corpus: 3 samples covering: minimal document, headings+paragraphs, table-containing document.
All synthetic (project-owned, Apache-2.0).

## Strategic Assessment

- ODT is the container-format sibling of FODT (already Gates 1-8 passed)
- Same ODF schema, same OASIS RF legal basis
- Parser implementation: add zipfile extraction layer on top of existing FODT parser logic
- Implementation complexity: LOW-MEDIUM — existing FodtParser reusable with thin container wrapper
- ODT covers the wide deployment base (all LibreOffice Writer users)
- Aspose.Words covers ODT commercially — FOSS Python alternative provides differentiation

## Comparison: FODT vs ODT

| Aspect            | FODT (Flat)           | ODT (Container)            |
|-------------------|-----------------------|----------------------------|
| File structure    | Single XML file       | ZIP archive                |
| Parsing entry     | Direct XML parse      | zipfile + XML parse        |
| Deployment        | Rare (developer use)  | Universal (LibreOffice default) |
| Spec source       | ODF 1.3 (same)        | ODF 1.3 (same)             |
| Parser reuse      | N/A (base)            | FodtParser via zipfile layer|

## Next Steps (Not Authorized in R23)

1. Human IV of Gate 1 delegated decision (DEC-034)
2. Gate 3 sample corpus creation (R24)
3. Gate 4 parser prototype (reuse FodtParser + zipfile layer)
4. Gate 5 neutral model (reuse FODT neutral model with container additions)

## Invariants

- commercial_product_ready: false
- publication_authorized: false
- No implementation work authorized until Gates 1-3 human IV complete
