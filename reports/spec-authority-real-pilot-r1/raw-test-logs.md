# Raw Test Logs
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Command

```
.local/venv/Scripts/python -m pytest tests/spec_authority/ tests/specification-authority-layer/ -v
```

## Output

```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\prora\OneDrive\Documents\GitHub\format-factory
configfile: pytest.ini
plugins: anyio-4.13.0
collecting ... collected 45 items

tests/spec_authority/test_real_pilots.py::test_source_registry_requires_source_id PASSED [  2%]
tests/spec_authority/test_real_pilots.py::test_citation_requires_registered_source PASSED [  4%]
tests/spec_authority/test_real_pilots.py::test_citation_rejects_empty_source_id PASSED [  6%]
tests/spec_authority/test_real_pilots.py::test_vault_ingest_produces_sha256 PASSED [  8%]
tests/spec_authority/test_real_pilots.py::test_vault_not_re_ingested_when_sha_matches PASSED [ 11%]
tests/spec_authority/test_real_pilots.py::test_normalized_output_has_source_ref PASSED [ 13%]
tests/spec_authority/test_real_pilots.py::test_normalized_artifact_has_sections PASSED [ 15%]
tests/spec_authority/test_real_pilots.py::test_requirements_have_source_ref_and_section_ref PASSED [ 17%]
tests/spec_authority/test_real_pilots.py::test_dif_requirements_not_overclaimed PASSED [ 20%]
tests/spec_authority/test_real_pilots.py::test_context_pack_has_manifest_sha256 PASSED [ 22%]
tests/spec_authority/test_real_pilots.py::test_context_pack_deterministic PASSED [ 24%]
tests/spec_authority/test_real_pilots.py::test_stale_source_triggers_stale_status PASSED [ 26%]
tests/spec_authority/test_real_pilots.py::test_empirical_source_cannot_become_accepted_spec_via_memory PASSED [ 28%]
tests/spec_authority/test_real_pilots.py::test_governance_rejects_unregistered_citation PASSED [ 31%]
tests/spec_authority/test_real_pilots.py::test_full_pipeline_zst PASSED  [ 33%]
tests/spec_authority/test_real_pilots.py::test_full_pipeline_netpbm PASSED [ 35%]
tests/spec_authority/test_real_pilots.py::test_full_pipeline_dif PASSED  [ 37%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_register_source PASSED [ 40%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_source_not_registered PASSED [ 42%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_validate_citation_rejects_unregistered PASSED [ 44%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_validate_citation_rejects_empty PASSED [ 46%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_validate_citation_allows_registered PASSED [ 48%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_ingest_text_fixture PASSED [ 51%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_snapshot_meta_available_after_ingest PASSED [ 53%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_snapshot_integrity_check PASSED [ 55%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_parse_markdown_spec PASSED [ 57%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_parse_netpbm_spec PASSED [ 60%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_normalize_produces_artifact PASSED [ 62%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_index_built_from_normalized_artifact PASSED [ 64%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_search_index PASSED [ 66%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_digest_computed PASSED [ 68%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_staleness_detection PASSED [ 71%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_extract_requirements_from_spec PASSED [ 73%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_anti_bypass_rejects_no_source_refs PASSED [ 75%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_anti_bypass_rejects_ai_summary_only PASSED [ 77%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_anti_bypass_allows_valid_claim PASSED [ 80%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_verifier_rejects_no_source_id PASSED [ 82%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_context_pack_built_deterministically PASSED [ 84%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_context_pack_verify_passes PASSED [ 86%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_context_pack_verify_rejects_missing_sha PASSED [ 88%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_usage_ledger_appends PASSED [ 91%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_memory_only_claim_rejected PASSED [ 93%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_pilot_zst PASSED [ 95%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_pilot_netpbm PASSED [ 97%]
tests/specification-authority-layer/test_spec_authority_mwp.py::test_pilot_dif PASSED [100%]

============================= 45 passed in 2.04s ==============================
```

## Result

**45 passed, 0 failed, 0 skipped**
