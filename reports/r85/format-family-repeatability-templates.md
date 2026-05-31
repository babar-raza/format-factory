# R85 Train H — Format Family Repeatability Templates

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Templates Created

### docs/format-family-playbooks/00-index.md
Index file listing all playbooks.

### docs/format-family-playbooks/xml-office-like.md
For: FODS, FODT, ODS, ODT
Covers: spec artifacts, object model skeleton, parser/writer/edit/export strategies, test requirements, package artifacts, .NET DOM strategy

### docs/format-family-playbooks/simple-binary-image.md
For: PBM, PGM, PPM, QOI
Covers: header parsing, pixel model, binary/ASCII variants, family-based export dogfooding, .NET image slice strategy

### text-table.md (stub) — not created in R85
For: SYLK, DIF, CSV, TSV
Status: HOLD — SYLK/DIF already implemented; template needed before next format

### compression-container.md (stub) — not created in R85
For: ZST, ZPAQ
Status: HOLD — ZST already implemented; ZPAQ blocked (Gate 3)

## Key Repeatability Pattern

Every format family playbook defines:
1. Acquisition inputs
2. Spec artifact structure
3. Object model skeleton
4. Parser strategy
5. Writer strategy
6. Edit model strategy
7. Export/dogfood strategy (using FF libraries)
8. Tests per gate
9. Package artifacts
10. Examples/docs

## TRAIN_H_STATUS: COMPLETE (2 of 4 playbooks; 2 deferred to next sprint)
