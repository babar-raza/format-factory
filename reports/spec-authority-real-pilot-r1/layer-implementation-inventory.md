# Layer Implementation Inventory — SAL Real Pilot R1
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Lane: A

---

## Primary Implementation Path

**Location:** `tools/specification-authority-layer/`

All 12 expected subsystem modules are present at this single path.
No alternative paths found (`tools/specification_authority/`, `tools/spec_authority/` — NOT FOUND).

---

## Subsystem Map

| Spec Subsystem | Module File | Status | Entry Function(s) |
|---|---|---|---|
| SpecSourceRegistry | `spec_source_registry.py` | PRESENT | `register_source()`, `load_registry()`, `validate_citation()` |
| SpecVault | `spec_vault_ingest.py` | PRESENT | `ingest_text_fixture()`, `ingest_local_file()`, `verify_snapshot_integrity()` |
| SpecParser | `spec_parser.py` | PRESENT | `parse_spec()`, `parse_spec_from_text()` |
| SpecNormalizer | `spec_normalizer.py` | PRESENT | `normalize_spec()`, `load_normalized_artifact()` |
| SpecIndexer | `spec_indexer.py` | PRESENT | `build_index()`, `search_index()`, `load_index()` |
| SpecDigestor | `spec_digestor.py` | PRESENT | `compute_digest()`, `check_staleness()`, `load_digest()` |
| RequirementExtractor | `requirement_extractor.py` | PRESENT | `extract_requirements()`, `load_requirements()` |
| SpecVerifier | `spec_verifier.py` | PRESENT | `verify_requirements()`, `check_anti_bypass()` |
| RequirementGraph | `requirement_graph.py` | PRESENT | `build_requirement_graph()`, `load_requirement_graph()` |
| ContextPackBuilder | `context_pack_builder.py` | PRESENT | `build_context_pack()`, `verify_context_pack()`, `load_context_pack()` |
| SpecGovernanceRuntime | `spec_governance_runtime.py` | PRESENT | `check_citation_allowed()`, `check_memory_only_claim()`, `load_usage_ledger()` |
| Package Init | `__init__.py` | PRESENT | (empty — direct module imports used) |

**All 12 subsystem modules: PRESENT**

---

## Capability Assessment

### What's wired and executable:

- `register_source()` → writes to `.local/spec-source-registry/sources.jsonl` (append-only JSONL)
- `ingest_text_fixture()` → writes to `.local/spec-vault/{source_id}/`; computes SHA-256
- `verify_snapshot_integrity()` → re-computes and compares SHA-256
- `parse_spec_from_text()` → auto-detects markdown vs plain text; produces `ParsedSpec` with sections
- `normalize_spec()` → strips control chars, normalizes whitespace; writes JSON artifact
- `build_index()` → builds term→section_id inverted index; supports `search_index()`
- `compute_digest()` → content digest (stable, excludes timestamps); enables staleness detection
- `check_staleness()` → compares stored snapshot sha256 to current; returns `stale` bool
- `extract_requirements()` → RFC-2119 keyword scan; produces `CandidateRequirement` list
- `verify_requirements()` → anti-hallucination cross-check against normalized artifact
- `build_requirement_graph()` → SpecSource + SpecRequirementRef + sourced_from edges
- `build_context_pack()` → deterministic manifest SHA-256; aggregates sources + requirements + index terms
- `verify_context_pack()` → recomputes manifest SHA-256; anti-bypass rejects if missing
- `check_citation_allowed()` → registry anti-bypass + usage ledger write
- `check_memory_only_claim()` → rejects raw_ai_summary_only and no-source_refs claims

### What is NOT present:

- **External network fetch** — no HTTP client; uses `deferred_local_fixture` or local files
- **PDF parser** — only text/markdown; large spec PDFs (ODF 1.3) would need preprocessing
- **RFC-body fetcher** — no direct RFC text download; uses fixtures
- **Staleness auto-trigger** — check_staleness() is callable but not auto-scheduled
- **Refresh pipeline** — no auto-recompute; staleness detection is advisory only

---

## Safe Pilot Execution Paths

1. **All 4 pilot formats** can run via `ingest_text_fixture()` + full pipeline
2. **Determinism test** is executable (run build_context_pack twice, compare manifest_sha256)
3. **Staleness test** is executable via `check_staleness()` with synthetic sha256
4. **Governance runtime** is executable via `check_citation_allowed()` + `check_memory_only_claim()`

**PILOT EXECUTION PATH CONFIRMED: tools/specification-authority-layer/**

---

## Test Coverage

- **Test file:** `tests/specification-authority-layer/test_spec_authority_mwp.py`
- **Test count:** 28 tests
- **Status:** 28/28 PASS (confirmed by Lane H run)
- **Coverage:** Source registration, vault ingest, parse, normalize, index, digest, staleness, requirement extraction, verification, context pack build+verify, usage ledger, governance runtime, pilot lifecycle tests (ZST, Netpbm, DIF)

No alternative test directories found at `tests/spec_authority/` or `tests/specification_authority/`.
