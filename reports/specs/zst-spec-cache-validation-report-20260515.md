# ZST Spec Cache Validation Report
Sprint: FORMAT-FACTORY-R14-ZST-SPEC-RETRIEVAL-AND-GATE2-SWARM-001
Gate: 6 (Lane G)
Date: 2026-05-15

---

## Validation Method

1. `tools/spec-cache/refresh_check.py validate --format-id zst` — schema validation
2. Python SHA-256 verification against recorded hashes
3. New deterministic test suite: `tests/skills/test_zst_spec_cache_gate2.py` (20 tests)

---

## Schema Validation (existing tool)

Command: `python tools/spec-cache/refresh_check.py validate --format-id zst`

```
VALID: zst/rfc8878  — .local/spec-cache/zst/rfc8878/spec-index.yaml
VALID: zst/rfc9659  — .local/spec-cache/zst/rfc9659/spec-index.yaml
```

Result: **PASS**

---

## New Tests: test_zst_spec_cache_gate2.py

File: `tests/skills/test_zst_spec_cache_gate2.py`
Tests: 20

```
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_spec_cache_zst_root_exists
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc8878_file_exists
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc9659_file_exists
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_manifest_yaml_exists
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_update_relationship_yaml_exists
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc8878_sha256_matches
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc9659_sha256_matches
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc8878_spec_index_sha256_matches_file
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc9659_spec_index_sha256_matches_file
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc8878_spec_index_format_id_is_zst
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc9659_spec_index_format_id_is_zst
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc8878_spec_index_local_only
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_rfc8878_not_stale
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_update_relationship_rfc8878_updated_by_rfc9659
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_update_relationship_rfc9659_scope_http_only
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_manifest_both_rfcs_present
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_no_generated_requirements_zst
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_no_src_net_zst
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_no_src_python_zst
PASSED tests/skills/test_zst_spec_cache_gate2.py::test_no_unrelated_specs_in_zst_cache

20 passed in 0.40s
```

---

## Checklist Verification

| Check | Method | Result |
|-------|--------|--------|
| manifest.yaml exists | test_manifest_yaml_exists | PASS |
| All source files listed in manifest exist | test_rfc8878_file_exists, test_rfc9659_file_exists | PASS |
| All SHA-256 hashes match | test_rfc8878_sha256_matches, test_rfc9659_sha256_matches | PASS |
| RFC 8878 and RFC 9659 both represented | test_manifest_both_rfcs_present | PASS |
| RFC 8878 -> updated_by RFC 9659 relationship recorded | test_update_relationship_rfc8878_updated_by_rfc9659 | PASS |
| RFC 9659 scope is HTTP-only | test_update_relationship_rfc9659_scope_http_only | PASS |
| No unrelated specs cached | test_no_unrelated_specs_in_zst_cache | PASS |
| No generated requirements | test_no_generated_requirements_zst | PASS |
| No embeddings | (no embeddings directory exists) | PASS |
| No src mutations | test_no_src_net_zst, test_no_src_python_zst | PASS |

---

SPEC_CACHE_VALIDATION_REPORT: PASS
20/20 tests PASS
