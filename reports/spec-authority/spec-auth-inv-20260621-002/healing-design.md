# Specs Authority Layer — Healing Design
**Run ID:** spec-auth-inv-20260621-002
**Date:** 2026-06-21

---

## 1. Target Architecture

The healed SAL must be:
- **Single canonical output path** — one `sal-facts-latest.json` that all validators and tools read
- **Immutable spec source** — cached PDF/RFC with SHA-256; refresh_check.py wired to Step 0a
- **Verified facts in workbench** — anti-bypass verifier runs at SAL read time, not just write time
- **Fact quality classification** — `behavioral` vs `structural_enumeration` facts distinguished
- **Bidirectional traceability** — FACT-ID → product code → tests (proof graph populated)
- **Acquisition gate** — sha256_snapshot required before PRODUCT_SOURCE tasks are scheduled
- **AI lifecycle wired** — auto-extracted facts tracked through 12-state machine
- **Consistent validators** — V37 and V47 read from the same canonical path

---

## 2. Minimum Viable Repair (P0/P1 only — estimated 1-2 sprints)

### MVR-1: Fix sal-facts-latest.json overwrite (GAP-SA-NEW-001)

**File:** `tools/specification-authority-layer/sal_master_runner.py`

In `run_sal_pipeline()`:
```python
# BEFORE writing sal-facts-latest.json:
if formats and len(formats) < len(all_formats):
    # Single-format run — do NOT overwrite all-format latest
    # Write only per-format file
    per_format_path.write_text(...)
    return  # skip writing sal-facts-latest.json
```

Expected result: `--format zst` writes only `sal-facts-zst.json`; `--all` writes `sal-facts-latest.json`.

### MVR-2: Canonicalize validator paths (GAP-SA-NEW-002)

**File:** `tools/supervisor/governance_validators.py`, function `validate_spec_fact_authority_chain`

Change V37's `sal_path`:
```python
# FROM:
sal_path = repo_root / ".local" / "sal-output" / "sal-facts-latest.json"
# TO:
sal_path = repo_root / ".local" / "sal-output" / "sal-facts-latest.json"
# AND ensure Step 0a writes to BOTH paths (symlink or copy)
```

OR: Create a symlink `.local/spec-cache/sal-facts-latest.json → .local/sal-output/sal-facts-latest.json`.
After MVR-1 fixes the overwrite problem, canonicalize to `sal-output` path for both.

### MVR-3: Wire spec_verifier in SAL runner (GAP-SA-NEW-003)

**File:** `tools/specification-authority-layer/sal_master_runner.py`

In `_load_workbench_verified_facts()`:
```python
from tools.specification_authority_layer.spec_verifier import verify_requirements
# After loading facts from YAML:
results = verify_requirements(loaded_facts, registered_source_ids=known_source_ids)
verified = [r for r in results if r.status == "VERIFIED"]
# Log warnings for UNVERIFIABLE; skip ANTI_BYPASS_REJECTED
```

### MVR-4: Add spec_source governance validator (GAP-SA-NEW-004)

New governance validator `validate_spec_source_acquired`:
```python
def validate_spec_source_acquired(declaration, repo_root=None):
    """V48: PRODUCT_SOURCE items for formats with sha256_snapshot=null must be WARN (Phase 1)."""
    sources_path = repo_root / ".local" / "spec-source-registry" / "sources.jsonl"
    # Load sources; index by format_id; check sha256_snapshot
    # For each PRODUCT_SOURCE item with format_id not in sha256_present: add to warnings
```

Wire into `governance_validator_runner.py`.

---

## 3. Full Production Repair (P2/P3 — estimated 3-4 sprints)

### FPR-1: Bidirectional traceability (GAP-SA-NEW-005)

Create `tools/traceability/scan_fact_refs.py`:
- Scan `src/python/**/*.py` for `FACT-[A-Z]+-[0-9]+` patterns in comments/docstrings/fields
- Output: `{fact_id: [source_files]}` JSON

Create `tools/traceability/map_facts_to_tests.py`:
- Cross-reference scanned facts with test files in `tests/python/<format>/`
- Output: `{fact_id: {product_files: [...], test_files: [...]}}` JSON

Create `tools/traceability/populate_proof_graph.py`:
- Call `tools/requirements_authority/graph_store.py` with harvested facts
- Populate `.local/capability-proof-graph/`

Wire into sprint closeout after Step 2 of supervisor loop.

### FPR-2: Behavioral vs structural fact classification (GAP-SA-NEW-007)

Add `fact_category` field to workbench YAML schema:
```yaml
facts:
- claim_id: FACT-FODS-001
  fact_category: behavioral  # behavioral | structural_enumeration
  claim: ...
```

Update `fact_coverage_report.py` to report:
```
behavioral_coverage: 78/78 (100%)
structural_coverage: 4913/4913 (100%)
```

Gate 11 readiness threshold: ≥ 50 behavioral facts per ODF format.

### FPR-3: Staleness detection automation (GAP-SA-NEW-008)

In `tools/supervisor/autonomous_cycle.py` Step 0a, after SAL regeneration check:
```python
# Add refresh check
_refresh_tool = repo_root / "tools" / "spec-cache" / "refresh_check.py"
if _refresh_tool.exists():
    _rc = subprocess.run(["python", str(_refresh_tool), "--all"], ...)
    if _rc.returncode != 0:
        print("  WARNING: stale spec detected — re-acquire spec before next workbench build")
        # Non-blocking — log and continue
```

### FPR-4: Source hash propagation to acquisition packs (GAP-SA-NEW-009)

Create `tools/spec-cache/propagate_source_hash.py`:
```python
# For each format in acquisition-packs/:
#   Read .local/spec-cache/{format}/*/spec-index.yaml
#   Update acquisition-packs/{format}/pack.yaml source_hash field
#   Update acquisition-packs/{format}/spec-evidence.md source_hash field
```

### FPR-5: Authority lifecycle integration (GAP-SA-NEW-010)

Add lifecycle tracking to `build_spec_workbench.py`:
```python
from tools.ai.validators.authority_lifecycle import transition_with_evidence
# When creating a new fact via auto-extraction:
state = "source_cited"  # not authoritative_after_gate
# When hand-verified with spec line citation:
state = "source_verified"
# After independent agent verification:
state = "accepted_for_planning"
# After gate approval:
state = "authoritative_after_gate"
```

---

## 4. Data Model Changes

### 4a. Fact Schema (workbench/verified-facts-review.yaml)

Add fields:
```yaml
- claim_id: FACT-FODS-001
  fact_category: behavioral         # NEW: behavioral | structural_enumeration
  lifecycle_state: authoritative_after_gate  # NEW: 12-state lifecycle value
  # existing fields unchanged
```

### 4b. SAL Output Schema (sal-facts-latest.json)

Add field per fact:
```json
{
  "qname": "FACT-FODS-001",
  "fact_category": "behavioral",
  "lifecycle_state": "authoritative_after_gate",
  ...existing fields...
}
```

### 4c. Acquisition Pack Schema (pack.yaml)

Make source_hash required:
```yaml
source_hash: sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066  # required, not null
```

---

## 5. Spec Cache Rules (unchanged — document for clarity)

1. Spec files are cached ONLY under `.local/spec-cache/` (local-only, not committed)
2. SHA-256 computed at download time; stored in `spec-index.yaml:content_hash`
3. `stale: false` unless manually set or `refresh_check.py` detects hash mismatch
4. Re-download requires `--allow-network` flag and T3 re-authorization
5. No spec text in evidence bundles (AGENTS.md §Y5 forbidden file patterns)

---

## 6. Source Hash and Invalidation Rules

1. `spec-index.yaml:content_hash` = SHA-256 of cached file at download time
2. `workbench/verified-facts-review.yaml:provenance.source_sha256` = must match `spec-index.yaml:content_hash`
3. If source sha256 changes (refresh): workbench facts with `verification_status: verified` must be re-verified
4. `refresh_workbench.py` must be run after any source update
5. Governance validator V48 must detect sha256 mismatch between spec-index.yaml and workbench provenance

---

## 7. Format/Spec Version Isolation

- Each format has its own namespace in `.local/spec-cache/<format>/<version>/`
- SAL output uses `format_id` as primary key; no cross-format fact sharing
- Vector store (when implemented): `namespace_manager.py` enforces format isolation at index level
- Spec version: add `spec_version` field to fact references in declarations

---

## 8. Verified Fact Schema (canonical)

```yaml
claim_id: FACT-FODS-001
claim: <statement of fact>
fact_category: behavioral | structural_enumeration
lifecycle_state: ai_draft | source_cited | source_verified | ... | authoritative_after_gate
verification_status: verified | verified_with_note | pending_verification | not_found_in_normalized_text
provenance:
  spec_id: odf-1.3-part3          # registered source_id from sources.jsonl
  source_sha256: sha256:92cfe64…   # must match spec-index.yaml:content_hash
  section_id: 3.1.2
  page_start: 90
  normalized_artifact: text.txt
  extraction_method: tier1_section | xml_element_scan | automated_extraction
  chunk_id: <optional>
  verification_evidence: "text.txt line 7218: [exact spec text]"
  validated_by: independent_agent_verifier | deterministic_spec_text_search
  validated_at: 2026-06-07
  spec_page_confirmed: true | false | null
```

---

## 9. Requirement Generation Schema

Task-specific requirement packs generated from verified facts must include:

```yaml
requirement_id: REQ-FODS-PARSER-001
fact_refs:
  - FACT-FODS-001
  - FACT-FODS-004
statement: <requirement text>
acceptance_criteria: <testable criterion>
spec_section: 3.1.2
priority: must | should | may
```

---

## 10. Citation/Provenance Schema

Evidence bundle citations must include:
```json
{
  "fact_id": "FACT-FODS-001",
  "spec_id": "odf-1.3-part3",
  "source_sha256": "sha256:92cfe64…",
  "section": "3.1.2",
  "line_evidence": "text.txt line 7218: '3.1.2 <office:document>...'"
}
```

---

## 11. Lexical Retrieval Requirements

- `tools/spec-normalize/query_normalized_spec.py`: existing implementation is CORRECT
- `tools/ai/retrieval/lexical_retriever.py`: TF-based ranking is CORRECT
- For acquisition planning: wire lexical_retriever to suggest spec sections for new formats
- Threshold: top-k=10, min_score=0.1 (configurable in retriever config)
- Results must include chunk_id for citation chain

---

## 12. Optional AI/Embedding Support Role

AI is permitted for:
- Section discovery (Tier 1 use: lexical_retriever.py active now)
- Candidate fact extraction from sections (Tier 2: authorized; output stays ai_draft)
- Fact summarization for review (Tier 2: authorized; output stays ai_draft)
- Vector search for large spec retrieval (Tier 3: TC-0015 evaluation required first)

AI is forbidden for:
- Final fact verification (only spec_verifier.py with source text match)
- Gate evidence
- Cross-format retrieval blending

---

## 13. Tests Required for Healing Verification

| Test | Priority | Blocks |
|------|---------|--------|
| single-format SAL run does not overwrite sal-facts-latest.json | P0 | GAP-SA-NEW-001 |
| V37 and V47 read same fact set | P0 | GAP-SA-NEW-002 |
| sal_master_runner calls spec_verifier on loaded facts | P1 | GAP-SA-NEW-003 |
| fact with no source_id excluded from SAL output | P1 | GAP-SA-NEW-003 |
| validate_spec_source_acquired warns for format with sha256=null | P1 | GAP-SA-NEW-004 |
| scan_fact_refs.py finds FACT-FODS-001 in fods/constants.py | P1 | GAP-SA-NEW-005 |
| proof graph has ≥1 product_file and ≥1 test_file for FACT-FODS-001 | P1 | GAP-SA-NEW-005 |
| behavioral vs structural fact count per format | P2 | GAP-SA-NEW-007 |
| refresh_check.py called and warns on stale spec in autonomous cycle | P2 | GAP-SA-NEW-008 |
| source_hash in pack.yaml matches spec-index.yaml sha256 | P2 | GAP-SA-NEW-009 |

---

## 14. Migration Plan

**Phase 1 (P0, immediate — this sprint):**
1. Fix sal_master_runner.py single-format overwrite guard
2. Canonicalize V37 and V47 paths

**Phase 2 (P1, next sprint):**
1. Wire spec_verifier into _load_workbench_verified_facts
2. Add validate_spec_source_acquired (V48)
3. Write scan_fact_refs.py and populate_proof_graph.py
4. Set require_spec_facts=True for formats with workbench coverage ≥50%

**Phase 3 (P2, +1 sprint):**
1. Add fact_category field to workbench schema and coverage reports
2. Wire refresh_check.py to autonomous_cycle.py
3. Write propagate_source_hash.py for acquisition packs

**Phase 4 (P3, when AI usage is authorized):**
1. Wire authority_lifecycle.py into build_spec_workbench.py
2. Activate lexical_retriever.py in acquisition planning

---

## 15. Backward Compatibility

- All existing verified-facts-review.yaml files remain valid (new fields are optional)
- All existing SAL output consumers continue to work (new fields are additive)
- V48 starts as WARN-only; existing formats with sha256=null are not immediately blocked
- Proof graph is additive — its absence doesn't break existing workflows

---

## 16. Evidence and Proof Requirements

After healing, each repair must produce:
- GAP-SA-NEW-001: `sal-facts-latest.json` has ≥20 format entries after `--all` run; unchanged after `--format zst`
- GAP-SA-NEW-002: `grep sal_path governance_validators.py` shows single canonical path for V37 and V47
- GAP-SA-NEW-003: test passes: inject corrupted workbench → SAL runner warns and excludes
- GAP-SA-NEW-004: V48 governance check in `test_governance_validators.py`
- GAP-SA-NEW-005: `.local/capability-proof-graph/fods-traceability.json` exists with FACT-FODS-001 entries

---

## 17. Rollback Plan

All repairs are additive or narrowly scoped:
- MVR-1 (sal_master_runner guard): revert single line; no data loss
- MVR-2 (path canonicalization): revert path string; no data loss
- MVR-3 (spec_verifier): disable by removing call; workbench unchanged
- MVR-4 (V48 validator): remove from runner list; no other impact
- FPR-1 (traceability): delete `.local/capability-proof-graph/`; no product impact
