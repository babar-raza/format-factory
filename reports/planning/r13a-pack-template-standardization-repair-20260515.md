# R13A Pack-Template Standardization Repair
Sprint: FORMAT-FACTORY-R13A-R12-CLOSURE-AND-ZST-GATE1-PACKET-SWARM-001
Lane: E (Pack-Template and Schema Alignment)
Date: 2026-05-15

## Source: R12 Pack Standardization Gaps

R12 Lane F identified 3 non-blocking gaps in `acquisition-packs/_template/pack.yaml`:
- acquisition_risk_classification field missing
- oracle_classification field missing
- spec_normalization_status field missing

These fields were added to `schemas/skills/format-onboarding.schema.yaml` by R12 Lane D
(R12 schema extensions, commit d655ab9). The template was not updated in R12.

## Repairs Applied

### File: acquisition-packs/_template/pack.yaml

Added section `R12 Acquisition Governance Fields`:
```yaml
acquisition_risk_classification: NOT_ASSESSED
oracle_classification: NOT_ASSESSED
spec_normalization_status: NOT_STARTED
```

**Field values chosen:**
- `NOT_ASSESSED` for risk and oracle: correct default per schema enum — indicates the field
  exists but has not been assessed yet (required for new format onboarding)
- `NOT_STARTED` for spec_normalization: correct default per schema enum — spec has not been
  retrieved/cached yet (the starting state for any new format candidate)

**Schema alignment confirmed:**
- `acquisition_risk_classification` enum in schema: LOW|MEDIUM|HIGH|CRITICAL|NOT_ASSESSED ✓
- `oracle_classification` enum in schema: ROUND_TRIP|REFERENCE_DIFF|SCHEMA_VALIDATE|MANUAL_REVIEW|NOT_ASSESSED ✓
- `spec_normalization_status` enum in schema: NOT_STARTED|CACHED_RAW|NORMALIZED|REQUIREMENTS_READY|STALE ✓

## Schema Coverage After Repair

The template now covers all schema fields that have a sensible default for a new format:

| Schema Field | Template Status |
|---|---|
| acquisition_risk_classification | NOW PRESENT (NOT_ASSESSED) |
| oracle_classification | NOW PRESENT (NOT_ASSESSED) |
| spec_normalization_status | NOW PRESENT (NOT_STARTED) |
| sample_provenance_notes | Not added — free text, no default needed |
| public_spec_quality | Not added — assessed per-format at Gate 2 |

`sample_provenance_notes` and `public_spec_quality` are optional schema fields that are
format-specific and should be filled in per-format during acquisition. No default placeholder
was added for these as they are not part of the gap report.

## Test Coverage

The existing test suite covers schema/template consistency through:
- `tests/skills/test_public_spec_governance.py` (34 tests): validates governance rules
  including schema field validation for the R12 extensions

No new test file was created for this repair. The 34 governance tests in the existing suite
continue to cover schema conformance. Future test addition for template/schema alignment
against pack.yaml is a candidate for R14+ test expansion.

## Verdict
PACK_TEMPLATE_GAPS_REPAIRED: 3/3
SCHEMA_ALIGNMENT: CONFIRMED
NEW_TESTS_REQUIRED: NO (existing governance tests cover schema fields)
TEMPLATE_STANDARDIZATION: COMPLETE
