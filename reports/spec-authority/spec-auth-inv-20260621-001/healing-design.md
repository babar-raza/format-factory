# Specs Authority Layer — Healing Design
**Run ID:** spec-auth-inv-20260621-001
**Date:** 2026-06-21

---

## 1. Target Architecture

The target specs authority layer is a governed local-first pipeline with:

```
Phase A — Acquisition (one-time per spec version):
  acquire_spec.py (T3 auth) → .local/spec-cache/<format>/<version>/spec.pdf
  → spec-index.yaml (SHA-256, URL, legal, stale=false)
  → .local/spec-source-registry/sources.jsonl (source_id, sha256_snapshot confirmed)

Phase B — Normalization (reproducible from Phase A):
  normalize_pdf.py → text.txt (source hash embedded in artifact header)
  build_section_index.py → section-index.yaml (stable section IDs)
  build_chunk_index.py → chunk-index.jsonl (stable chunk IDs, hash each chunk)
  build_citation_map.py → citation-map.yaml

Phase C — Fact Extraction + Verification (reproducible from Phase B):
  query_normalized_spec.py (lexical) → candidate sections
  requirement_extractor.py → CandidateRequirements (each with source_id, section_id, text_fragment, chunk_id)
  spec_verifier.py → VerifiedFacts (VERIFIED status requires: source_id, section, sha256, text_fragment match)
  authority_lifecycle.py → ai_draft → source_cited → source_verified (required steps)
  → .local/spec-cache/<format>/workbench/verified-facts-review.yaml

Phase D — SAL Output (daily refresh):
  sal_master_runner.py → reads workbench verified facts (Phase C output)
                       → for formats WITHOUT workbench: emits facts with status=bootstrap_only (NOT "verified")
                       → for formats WITH workbench: emits verified facts WITH source_id, sha256, section
  → .local/sal-output/sal-facts-latest.json (facts have source_id field)
  → .local/sal-output/sal-facts-<format>.json (per-format files)

Phase E — Integration:
  capability_compiler.py ← sal-facts-latest.json (enrichment)
  TC-GUARD-001 ← fact validity check (not just string presence)
  fact_product_linker.py ← product source comments → traceability matrix
  verified-facts gate in autonomous_cycle.py ← format must have workbench facts before product sprint
```

---

## 2. Minimum Viable Repair (Sprint 1 — closes P0+P1 gaps)

### MVR-1: Fix sal_master_runner.py to separate bootstrap from verified

**Change:** Add `status: "bootstrap_only"` to all hardcoded template facts. Rename `verification_status` to `fact_status` for clarity. Only emit `fact_status: "verified"` for facts read from workbench verified-facts-review.yaml.

**Code path:** `sal_master_runner.py` — add `_load_workbench_verified_facts(format_id)` method that reads `.local/spec-cache/<format>/*/workbench/verified-facts-review.yaml` and merges with template facts.

**Impact:** Zero regressions (backward compat maintained). Exposes gap clearly in capability map.

### MVR-2: Fix dogfood tests (GAP-SA-005)

**Change:** `sal_master_runner.py --all` should also write `sal-facts-<format>.json` per format. Two lines of code.

**Or:** Update dogfood tests to load from combined `sal-facts-latest.json` instead of per-format files.

**Priority:** Fix tests — 6 failing tests → 0 failures.

### MVR-3: Complete T3 authorization and spec fetch for ZST

**Why ZST:** ZST is governed by RFC 8878 (public domain), no legal risk. Spec text is available. Already has 15 verified facts in workbench.

**Steps:**
1. Complete T3-1 through T3-6 in `acquisition-packs/zst/` legal notes
2. Run `python tools/spec-cache/acquire_spec.py --format zst --version rfc8878 --url <rfc8878_url> --allow-network`
3. Run `python tools/spec-normalize/build_spec_workbench.py --format zst`
4. Run `python tools/specification-authority-layer/run_fact_verification.py --format zst`
5. Update sources.jsonl with sha256_snapshot

**Expected result:** ZST sha256_snapshot populated, workbench refreshed, fact verification runs against real text.

### MVR-4: Add source_id to workbench-sourced facts in SAL output

**Change:** When `sal_master_runner.py` emits a workbench fact, carry through its `source_id` from the YAML.

**Code path:** Update the workbench loading logic to include `source_id`, `section_id`, and `sha256` in emitted fact records.

---

## 3. Full Production Repair (Sprint 2-3 — closes all gaps)

### FPR-1: Wire run_extraction_pipeline.py into sal_master_runner.py

Replace the hardcoded template dict in `sal_master_runner.py` with a call to `run_extraction_pipeline.py` for formats with workbench. Hardcoded templates become the fallback for formats with no spec cache.

### FPR-2: Build fact_product_linker.py

New tool: `tools/traceability/fact_product_linker.py`
- Parses `src/python/*/` for `# spec_fact_refs: FACT-ID` comments
- Looks up each FACT-ID in `sal-facts-latest.json`
- Maps to test files via pytest collection meta
- Outputs `traceability-matrix.json`
- Required before Gate 11 sprint

### FPR-3: Add second-order TC-GUARD-001 check

`autonomous_cycle.py` step 2d2: after verifying `spec_fact_refs` string is present, load `sal-facts-latest.json` and verify each FACT-ID exists with `fact_status != "bootstrap_only"`.

### FPR-4: Automate staleness detection

`autonomous_cycle.py` step 0a: add hash comparison — read sha256 from spec-index.yaml, compute sha256 of cached spec file, compare. If mismatch → mark stale → trigger `refresh_workbench.py` for that format.

### FPR-5: Wire authority_lifecycle.py into extraction pipeline

`run_extraction_pipeline.py`: emit `authority_state` field on each extracted fact. Require `source_cited` transition before writing to workbench. Require `source_verified` transition after text-search confirms match.

### FPR-6: FODS workbench coverage campaign

Batch-run `run_fact_verification.py --format fods` against the 201 pending facts. Expected: ~60-80 additional verified via text search. Trim remaining unverifiable facts to "unsupported" status (not "pending"). Target: ≥80% effective coverage on FODS facts.

---

## 4. Data Model Changes

### 4.1 sal-facts-latest.json — add source_id field

```json
{
  "qname": "FACT-ZST-001",
  "section": "RFC 8878 §3.1",
  "description": "Zstandard frame begins with magic number 0xFD2FB528",
  "fact_status": "verified",
  "source_id": "SPEC-ZST-RFC8878",
  "sha256": "abc123...",
  "chunk_id": "zst-rfc8878-chunk-0042",
  "authority_state": "source_verified"
}
```

Add `source_id` (required), `sha256` (required for verified), `chunk_id` (recommended), `authority_state` (required).

### 4.2 verified-facts-review.yaml — ensure source_id present

Each entry must have `source_id` field. Migration: backfill from spec_source_registry for existing entries.

### 4.3 spec-index.yaml — add derived_artifacts stale flag

```yaml
stale: false
derived_artifacts_stale: false  # NEW: true if sha256 of current file != sha256 at time of normalization
```

---

## 5. Spec Cache Rules (confirmed / clarified)

1. Spec files live ONLY at `.local/spec-cache/` — never committed to git
2. spec-index.yaml metadata (no content) may appear in evidence bundles
3. `sha256_snapshot` must be populated before any normalization can run
4. `stale: true` must trigger workbench rebuild and facts re-verification
5. `acquire_spec.py --allow-network` requires all 6 T3 conditions documented in acquisition pack
6. Spec file hash is verified before normalization — hash mismatch → stop and log GAP G-NORM-002
7. Spec version isolation: facts from FODS 1.3 cannot be cited as FODS 1.2 facts

---

## 6. Source Hash and Invalidation Rules

| Event | Action | Automated? |
|-------|--------|------------|
| Initial spec acquisition | Write spec-index.yaml with sha256_snapshot | Yes (acquire_spec.py) |
| Daily autonomous cycle | Compare spec-index.yaml sha256 vs file sha256 | NO — add this |
| Hash mismatch detected | Set derived_artifacts_stale=true, log GAP, halt workbench use | NO — add this |
| Workbench refresh complete | Reset derived_artifacts_stale=false | After repair |
| Sources.jsonl status update | Update status to snapshot_available after sha256 confirmed | Yes (spec_source_registry.py) |

---

## 7. Format/Spec-Version Isolation

Current: Format-id prefix on fact QNames (FACT-FODS-001, FACT-ZST-001). This is necessary but not sufficient.

Additional required isolation:
- Each fact must carry `spec_version` field (e.g., "1.3" for ODF)
- Facts from different versions must not be mixed without explicit migration record
- `verified-facts-review.yaml` should live under `<format>/<version>/` path (already designed: `.local/spec-cache/fods/1.3/workbench/`)
- SAL output should group by format+version

---

## 8. Verified Fact Schema

```json
{
  "fact_id": "FACT-ZST-001",
  "format_id": "zst",
  "spec_version": "rfc8878",
  "source_id": "SPEC-ZST-RFC8878",
  "section_id": "3.1",
  "page": 5,
  "sha256": "abc123def456...",
  "text_fragment": "Zstandard frame begins with a magic number: 0xFD2FB528",
  "chunk_id": "zst-rfc8878-chunk-0042",
  "description": "Zstandard frame magic number identifies the format",
  "confidence": "verified",
  "authority_state": "source_verified",
  "verification_method": "deterministic_text_search",
  "verified_at": "2026-06-21T06:00:00Z",
  "verified_by": "run_fact_verification.py",
  "key_terms_matched": ["0xFD2FB528", "magic number", "Zstandard frame"]
}
```

**Required fields for `confidence: "verified"`:** fact_id, format_id, source_id, section_id, sha256, text_fragment, chunk_id, authority_state=source_verified.

**Not allowed for `confidence: "verified"`:** source_id=null, sha256=null, authority_state=ai_draft.

---

## 9. Requirement Generation Schema

```json
{
  "req_id": "REQ-ZST-MAGIC-001",
  "format_id": "zst",
  "source_fact_id": "FACT-ZST-001",
  "requirement_text": "Parser MUST read first 4 bytes and verify value equals 0xFD2FB528 to identify a Zstandard frame",
  "requirement_type": "parser",
  "priority": "MUST",
  "spec_citation": {
    "section_id": "3.1",
    "page": 5,
    "sha256": "abc123...",
    "spec_version": "rfc8878",
    "retrieval_method": "tier1_section"
  },
  "status": "active",
  "generated_at": "2026-06-21",
  "generated_by": "requirement_extractor.py"
}
```

---

## 10. Citation/Provenance Schema

Every spec excerpt cited in evidence must include:

```yaml
citation:
  section_id: "3.1"
  page: 5
  source_sha256: "abc123def456..."
  spec_version: "rfc8878"
  retrieval_method: "tier1_section"  # or tier1_element, tier2_keyword, tier2_sample_req, tier3_vector
  chunk_id: "zst-rfc8878-chunk-0042"
  spec_name: "RFC 8878 — Zstandard Compression and the application/zstd Media Type"
  accessed_at: "2026-06-21"
```

---

## 11. Lexical Retrieval Requirements

The three-tier strategy (from spec-retrieval-strategy.md) is the correct baseline:
- Tier 1 (deterministic): `--section`, `--element`, `--page` — always try first
- Tier 2 (lexical): `--keyword` — only if Tier 1 returns nothing useful
- Tier 3 (vector): planned for after workbench coverage ≥80%

Additional requirements post-repair:
- Lexical results must return chunk_id for citation
- False positive filter: result must contain actual spec content, not TOC reference
- Results must be format-scoped (no cross-format query bleed)
- Every query must be logged: `SPEC_QUERY: lexical keyword="<kw>" result_count=N format_id=<id>`

---

## 12. Optional AI/Embedding Support Role

See ai-embeddings-audit.md §6 for full architecture. Summary:

- Phase 1 (now): Lexical only. No embeddings. Fix GAP-SA-001 through GAP-SA-005 first.
- Phase 2 (after ≥80% workbench coverage on 3+ formats): Introduce embedding-assisted section finder. Advisory only. Source hash gate required.
- Phase 3 (after Phase 2 proven): AI-assisted draft requirement generation. Authority lifecycle required.
- NEVER: AI output as verified fact without source text confirmation.

---

## 13. Tests Required

| Test | Type | Priority |
|------|------|----------|
| Every fact in sal-facts-latest.json has non-null source_id | Unit | P0 |
| spec_verifier rejects fact with no source_id | Unit | P0 |
| Dogfood: sal-facts-fods.json loadable and has provenance | Integration | P1 |
| Dogfood: sal-facts-fodt.json loadable | Integration | P1 |
| ZST: sha256_snapshot in sources.jsonl is non-null | Integration | P1 |
| ZST: run_fact_verification.py finds ≥12/15 facts in spec text | Integration | P1 |
| FODS: after batch verification, effective coverage ≥60% | Integration | P1 |
| TC-GUARD-001 rejects FAKE-001 as spec_fact_refs | Unit | P2 |
| Staleness: modified sha256 triggers derived_artifacts_stale | Unit | P2 |
| Traceability: FACT-FODS-001 appears in product source AND test | Integration | P1 |
| Authority lifecycle: fact cannot jump from ai_draft to verified | Unit | P2 (exists — keep) |
| Cross-format: ZST fact cannot be cited in FODS context | Unit | P2 |

---

## 14. Migration Plan from Current State

| Step | Action | Risk | Rollback |
|------|--------|------|---------|
| 1 | Fix sal_master_runner.py — add bootstrap_only status | LOW — additive change | Revert file |
| 2 | Add per-format sal-facts output — fix dogfood tests | LOW | Revert file |
| 3 | Fetch ZST RFC8878 with --allow-network | MEDIUM — network op | Not needed; file can be deleted |
| 4 | Run ZST workbench build + verification | LOW — local only | Delete workbench artifacts |
| 5 | Add source_id to workbench-sourced SAL facts | LOW — additive | Revert file |
| 6 | Batch-verify FODS pending facts | LOW — read-only against cached text | Restore workbench YAML from git |
| 7 | Add fact_id lookup to TC-GUARD-001 | MEDIUM — may block existing declarations | Add --skip-fact-lookup flag |
| 8 | Build fact_product_linker.py | LOW — new tool, no source changes | Delete tool |
| 9 | Add hash staleness check to autonomous_cycle.py | MEDIUM — changes cycle behavior | Add --skip-hash-check flag |

---

## 15. Backward Compatibility Concerns

1. `sal-facts-latest.json` schema change: adding `source_id`, `sha256`, `fact_status` fields. Consumers using `verification_status` field must update to `fact_status`. Check: `capability_compiler.py` uses `spec_facts` list — update field names.

2. Dogfood tests expect per-format files: add these; combined file remains.

3. TC-GUARD-001 second-order check: may block existing declarations that use real FACT-IDs but against bootstrap_only facts. Add `bootstrap_only` as a warning (not block) until workbench coverage reaches 50%.

---

## 16. Evidence and Proof Requirements

Each repair sprint must produce:
- Test output showing before/after pass count
- `sal-facts-latest.json` snippet showing new fields present
- `fact-coverage-summary.md` showing coverage improvement
- `run_fact_verification.py` log showing verified count
- Git diff of changed files

---

## 17. Rollback Plan

All changes are:
- Local-only (no spec text committed to git)
- Additive (new fields, new files)
- Tool-level (not product source changes in SAL repair sprints 1-4)

Rollback for any step: `git checkout <file>` or delete new tool. No database migrations. No network state.
