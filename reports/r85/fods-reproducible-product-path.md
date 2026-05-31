# R85 Train G — FODS Reproducible Product Path

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Reproducibility Audit: Python FOSS FODS

### 1. Acquisition/spec evidence
- acquisition-packs/fods/ — PRESENT (gate10 review packet, format-profile, dec033 record, release manifests)
- ODF 1.3 Part 3 spec cached locally
- STATUS: PRESENT

### 2. Format Understanding Layer
- format_understanding/fods/ — NOT present as standalone dir (specs cached in acquisition-packs/)
- NOTE: FODS understanding captured through Gates 1-9 acquisition; no standalone FUL dir created
- STATUS: PARTIAL (gate evidence exists; no separate FUL directory)

### 3. Requirements map
- generated-requirements/fods/ — PRESENT (6 artifacts from AI requirements pipeline)
- STATUS: PRESENT

### 4. Object model inventory
- schemas/neutral-model/fods/ — PRESENT (6 entities, 19 mappings, 21 rules)
- STATUS: PRESENT

### 5. Parser/writer/source inventory
- src/python/fods/ — PRESENT (7 files: parser.py, writer.py, neutral_model.py, csv_exporter.py, constants.py, exceptions.py, __init__.py)
- STATUS: PRESENT

### 6. Tests
- tests/python/fods/ — PRESENT (comprehensive test suite; R84 adds workbook_to_csv, workbook_get_cell_value)
- STATUS: PRESENT

### 7. Package artifacts build
- packaging/python/build-local-packages.py + package-matrix.yaml — PRESENT
- .local/r84-packages/fods/dist/ — PRESENT (wheel + sdist from R84)
- STATUS: PRESENT

### 8. Installed package workflow
- examples/python/fods/ — PRESENT (edit_save_fods.py, edit_save_export_fods.py, edit_save_export_fods_installed.py)
- R82 installed-workflow proof: 12-step PASS
- STATUS: PRESENT

### 9. Examples/docs
- examples/python/fods/ — 3 example files
- docs/python-foss/ — PRESENT
- release-manifests/python-foss/fods.yaml — PRESENT
- STATUS: PRESENT

### 10. Evidence/review package contains proof
- R84 supervisor review package (11 MB) includes package artifacts and raw logs
- STATUS: PRESENT

## Reproducibility Classification

REPRODUCES_VERIFY_ONLY

Rationale:
- All source, tests, packages, and workflows are present and reproducible from repo
- Full reproducibility requires re-running acquisition (spec download, corpus) which is external-state-dependent
- The build path (source → wheel → install → test) reproduces deterministically
- Format Understanding Layer is in acquisition-packs/, not a standalone FUL directory

## Reproducibility Gap Ledger

| Gap ID | Description | Impact | Action |
|--------|-------------|--------|--------|
| REP-001 | No standalone FUL directory for FODS | LOW | None required; evidence in acquisition-packs/ |
| REP-002 | Spec download requires external network for fresh acquisition | LOW | Spec cached locally; not blocking |
| REP-003 | build-local-packages.py requires pip install (network) | MEDIUM | Use cached wheels from .local/r84-packages/ |

## TRAIN_G_STATUS: COMPLETE
