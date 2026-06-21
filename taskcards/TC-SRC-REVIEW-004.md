# TC-SRC-REVIEW-004: FODT Source-to-Spec Manifest

**Lane**: SRC-REVIEW
**Status**: backlog
**Owner**: autonomous agent
**Prerequisites**: TC-SRC-REVIEW-003 COMPLETE
**item_type**: GOVERNANCE_ASSET
**gap_ledger_ref**: GAP-QNAME-FODT-002

## Objective

Create `shared/spec-manifests/fodt-source-map.yaml` mapping existing FODT classes to their
canonical QName equivalents, with verified file locations.

## Key Verified Facts

- FodtParagraph: `src/python/fodt/models.py` (NOT neutral_model.py)
- FodtSpan: `src/python/fodt/models.py`
- FodtDocument: `src/python/fodt/models.py` (public facade — stays permanently)
- neutral_model.py = dict builder ONLY (build_document, make_warning, validate_document)
- FodtBody: .NET ONLY at `src/net/fodt/Model/FodtBody.cs` (no Python equivalent)

## Execution Steps

1. Create `shared/spec-manifests/fodt-source-map.yaml` with entries for:
   - Python: FodtParagraph → Text.Paragraph (models.py, migration_status: pending)
   - Python: FodtSpan → Text.Span (models.py, migration_status: pending)
   - Python: FodtDocument → null/null (models.py, migration_status: keep_as_facade)
   - .NET: FodtBody → Office.Body (Model/FodtBody.cs, migration_status: pending)
   - .NET: FodtParagraph → Text.Paragraph (Model/FodtParagraph.cs, migration_status: pending)

## Validation

- File parses as valid YAML
- FodtParagraph.file = src/python/fodt/models.py (NOT neutral_model.py)
- FodtDocument.migration_status = keep_as_facade

## Evidence Required

- `shared/spec-manifests/fodt-source-map.yaml` content

## Completion Criteria

Manifest exists, parses, has correct file paths for all 5 class entries
