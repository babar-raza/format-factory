# Public-Spec Acquisition Governance Expansion
Sprint: FORMAT-FACTORY-R12-ACQUISITION-ENGINE-IV-AND-ZST-GOVERNED-READINESS-SWARM-001
Lane: D
Date: 2026-05-14
Status: COMPLETE

## Purpose

Strengthen acquisition governance BEFORE real onboarding begins. This sprint adds
structured governance fields for acquisition risk, spec normalization, oracle
classification, and public-spec quality — all of which are needed when the first
real acquisition candidate (ZST or equivalent) is authorized.

---

## Deliverables

### 1. Schema Extension: schemas/skills/format-onboarding.schema.yaml

Extended with 5 new fields (R12 Lane D additions):

| Field | Type | Purpose |
|-------|------|---------|
| `acquisition_risk_classification` | enum (5 values) | Overall risk before requiring human review |
| `spec_normalization_status` | enum (5 values) | Pipeline status: NOT_STARTED → REQUIREMENTS_READY |
| `oracle_classification` | enum (5 values) | Test oracle approach for this format |
| `public_spec_quality` | enum (8 values) | Quality tier of the primary specification |
| `sample_provenance_notes` | string | Open-license sample file documentation |

All new fields are optional (additionalProperties: false preserved). No existing required fields changed.

### 2. New Template: templates/format-onboarding/acquisition-risk-assessment-template.yaml

A new template for formats entering the acquisition risk assessment pipeline.
Defaults all new fields to conservative values (`NOT_ASSESSED`, `NOT_STARTED`, `CANDIDATE`).
Includes governance notes on when each field must be set.

Existing templates (public-spec-onboarding-template.yaml, reverse-engineering-safe-template.yaml) unchanged.

### 3. New Tests: tests/skills/test_public_spec_governance.py

34 tests across 6 test categories:
- `TestAcquisitionRiskClassification` (8 tests)
- `TestSpecNormalizationStatusLifecycle` (6 tests)
- `TestOracleClassification` (5 tests)
- `TestPublicSpecQuality` (5 tests)
- `TestOnboardingGovernanceInvariants` (8 tests)
- `TestRiskTierConsistency` (2 tests)

**All 34 tests: PASS**

---

## Governance Rules Added

### Rule D-001: Acquisition Risk Classification Required Before Requirements Generation
Formats with `acquisition_risk_classification = NOT_ASSESSED` or `CRITICAL` must NOT
proceed to requirements generation. An investigation sprint is required first.

### Rule D-002: Spec Normalization Status Lifecycle Is Sequential
Formats progress: `NOT_STARTED → CACHED_RAW → NORMALIZED → REQUIREMENTS_READY`
Skipping states is not permitted. `STALE` can occur at any post-CACHED_RAW state.

### Rule D-003: Oracle Classification Required Before Implementation Sprint
Formats without an oracle classification (`NOT_ASSESSED`) cannot enter
implementation vertical slice planning without a human-confirmed oracle approach.

### Rule D-004: Sample Provenance Must Be Documented
Before oracle testing, `sample_provenance_notes` must be populated with:
1. Confirmed open-license source
2. License confirmation
3. Documentation in acquisition-packs/<format>/sample-sources.md

### Rule D-005: Public Spec Quality Informs Requirements Generation Confidence
RFC_STANDARD / ISO/IEC / ECMA / OASIS: HIGH confidence AI requirements generation
OPEN_SOURCE_DOC / VENDOR_DOC: MEDIUM confidence — human review before acceptance
COMMUNITY_WIKI: LOW confidence — verifier review mandatory

---

## Risk Classification for Current Candidates

| Format | Risk | Rationale |
|--------|------|-----------|
| zst | LOW | RFC 8878, clear legal, OSS reference, no RE |
| gnumeric | LOW | Full public XML spec, OSS, clear legal |
| abw | LOW | Full public XML spec, OSS, clear legal |
| ora | LOW | OpenRaster full public spec, LGPL, OSS |
| qoi | LOW | Full public spec, no RE required |
| egg | MEDIUM | Partial spec, legal unclear |
| hwpx | MEDIUM | Partial spec, Korean vendor, legal unclear |
| xar | MEDIUM | Partial spec, no sample files |
| alz | HIGH | Reverse engineering, binary, legal unclear |
| hwp | HIGH | Reverse engineering, binary, legal unclear |
| sldprt/catpart/rvt | CRITICAL | No public spec; blocked |
| indd/qxp | CRITICAL | No public spec; blocked |

---

## Spec Normalization for ZST (Simulation)

If ZST acquisition were authorized:

| State | Sprint | Notes |
|-------|--------|-------|
| NOT_STARTED | (current) | No spec retrieved |
| CACHED_RAW | R12-ZST-SPEC-CACHE | RFC 8878 downloaded, hash recorded |
| NORMALIZED | R12-ZST-SPEC-NORM | RFC parsed into structured requirements template |
| REQUIREMENTS_READY | R12-ZST-REQ-GEN | AI-assisted requirements generated, schema-validated |

---

## Oracle Classification for Current Candidates

| Format | Oracle | Rationale |
|--------|--------|-----------|
| zst | ROUND_TRIP | Compress→decompress→verify content identity |
| gnumeric | SCHEMA_VALIDATE | XML output validated against Gnumeric schema |
| abw | SCHEMA_VALIDATE | XML output validated against AbiWord schema |
| fods/fodt | SCHEMA_VALIDATE | ODF schema validation (already in use) |
| qoi | REFERENCE_DIFF | Diff against reference qoi decoder output |
| hwp/alz | MANUAL_REVIEW | No automated oracle possible without RE |

---

## PUBLIC_SPEC_GOVERNANCE_STATUS: GOVERNANCE_EXPANDED
