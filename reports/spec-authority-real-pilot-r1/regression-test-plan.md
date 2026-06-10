# Regression Test Plan
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Purpose

Define the minimum regression test suite for the Specification Authority Layer that must
pass before each pilot iteration (R2, R3, ...).

## Test File

`tests/spec_authority/test_real_pilots.py` (17 tests)

## Test Categories

### Category 1: Anti-Bypass (3 tests)
- test_source_registry_requires_source_id
- test_citation_requires_registered_source
- test_citation_rejects_empty_source_id

**Invariant:** The SAL must reject unregistered and memory-only sources at every pipeline stage.

### Category 2: Vault Integrity (2 tests)
- test_vault_ingest_produces_sha256
- test_vault_not_re_ingested_when_sha_matches

**Invariant:** Every ingested snapshot must have a stable SHA-256. Identical content must
produce identical SHA-256 (idempotent).

### Category 3: Normalization (2 tests)
- test_normalized_output_has_source_ref
- test_normalized_artifact_has_sections

**Invariant:** Every normalized artifact must retain source_id and sha256 fields, and must
have at least 1 section.

### Category 4: Requirement Extraction (2 tests)
- test_requirements_have_source_ref_and_section_ref
- test_dif_requirements_not_overclaimed

**Invariant:** All extracted requirements must have source_id and section_id. DIF requirements
must be EMPIRICAL_ONLY (never ACCEPTED_SPEC).

### Category 5: Context Pack (2 tests)
- test_context_pack_has_manifest_sha256
- test_context_pack_deterministic

**Invariant:** Context packs must have a non-empty manifest_sha256. Identical sources must
produce identical manifest_sha256 across runs (determinism contract).

### Category 6: Staleness (1 test)
- test_stale_source_triggers_stale_status

**Invariant:** A mutated SHA-256 must trigger stale=True in check_staleness().

### Category 7: Authority Governance (2 tests)
- test_empirical_source_cannot_become_accepted_spec_via_memory
- test_governance_rejects_unregistered_citation

**Invariant:** Empirical sources cannot be promoted. Unregistered citations must be rejected.

### Category 8: Full Pipeline (3 tests)
- test_full_pipeline_zst
- test_full_pipeline_netpbm
- test_full_pipeline_dif

**Invariant:** End-to-end pipeline from ingest through context pack succeeds for minimum
3 pilot formats. ZST must produce ACCEPTED_SPEC. DIF must produce EMPIRICAL_ONLY.

## Run Command

```bash
.local/venv/Scripts/python -m pytest tests/spec_authority/ tests/specification-authority-layer/ -v
```

Expected: 45 passed (17 pilot + 28 MWP), 0 failed.

## Pilot R2 Additions

For Pilot R2 (real RFC fetch), add:
- test_real_rfc8878_fetch_produces_stable_sha256
- test_staleness_triggered_by_content_change_at_url
- test_html_stripping_preserves_section_structure

## Verdict

`REGRESSION_TEST_PLAN_COMPLETE — 17_TESTS_IN_8_CATEGORIES`
