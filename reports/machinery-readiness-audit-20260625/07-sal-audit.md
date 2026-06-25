# Lane E: SAL / Spec Authority Layer Audit
# Sprint: ff-machinery-readiness-audit-20260625

## Summary Finding

**The SAL is a "Museum of Good Intentions"** (term from spec-to-feature-radical-correction-plan.md §2):
- Fully architected (20+ tools built)
- Extensively documented
- Beautifully implemented
- But largely dormant: 17 of 20 tools never called in production
- Replaced by a simpler reality: facts manually verified once and checked into git

---

## Component Inventory (Direct Evidence from Plan §2)

Source: plans/spec-to-feature-radical-correction-plan.md lines 190–214

| Component | File | Status | Downstream Consumer |
|---|---|---|---|
| spec_source_registry.py | tools/specification-authority-layer/ | **ACTIVE** | authority_conveyor.py, validate_spec_fact_refs.py |
| context_pack_builder.py | tools/specification-authority-layer/ | **ACTIVE** (read-only) | autonomous_cycle.py, capability_layer |
| spec_governance_runtime.py | tools/specification-authority-layer/ | **ACTIVE** | validate_spec_fact_refs.py |
| spec_parser.py | tools/specification-authority-layer/ | **DEAD** | NONE (test imports only) |
| spec_normalizer.py | tools/specification-authority-layer/ | **DEAD** | NONE (test imports only) |
| spec_indexer.py | tools/specification-authority-layer/ | **DEAD** | NONE (test imports only) |
| spec_digestor.py | tools/specification-authority-layer/ | **DEAD** | NONE (never checked) |
| requirement_extractor.py | tools/specification-authority-layer/ | **DEAD** | NONE (output QUARANTINED) |
| spec_verifier.py | tools/specification-authority-layer/ | **DEAD** | NONE (test imports only) |
| requirement_graph.py | tools/specification-authority-layer/ | **DEAD** | NONE (test imports only) |
| spec_vault_ingest.py | tools/specification-authority-layer/ | **DEAD** | NONE (test imports only) |
| acquire_spec.py | tools/spec-cache/ | **DEAD** | NONE (DRY-RUN only; --allow-network never used) |
| spec_index.py | tools/spec-cache/ | **DEAD** | NONE (never imported externally) |
| build_spec_workbench.py | tools/spec-normalize/ | **RAN ONCE** | Never updated again (run030, 2026-05-06) |
| build_section_index.py | tools/spec-normalize/ | **DEAD** | NEVER called |
| build_chunk_index.py | tools/spec-normalize/ | **DEAD** | NEVER called |
| normalize_pdf.py | tools/spec-normalize/ | **DEAD** | NEVER called |
| build_citation_map.py | tools/spec-normalize/ | **DEAD** | NEVER called |
| query_normalized_spec.py | tools/spec-normalize/ | **DEAD** | NEVER called |
| validate_normalized_spec.py | tools/spec-normalize/ | **DEAD** | NEVER called |

**Count: 3 ACTIVE, 1 RAN_ONCE, 16+ DEAD**

---

## What Actually Works (Verified Fact Flow)

Source: spec-to-feature-radical-correction-plan.md §2 ("What Actually Works")

```
acquisition-packs/{format}/verified-facts.yaml  (GIT — canonical authority, manually created)
    |
    v
.local/spec-cache/{format}/{version}/workbench/verified-facts-review.yaml  (runtime copy)
    |
    +---> capability_map_generator.py: _load_spec_facts() [lines 141-155]
    +---> validate_spec_fact_refs.py: blocking gate on work item declarations
    +---> authority_gate_validation.py: authority level P0-P6 computation
```

**The operational pipeline is:** Git → local copy → 3 read consumers. That's it.

No parsing. No normalization. No section indexing. No chunk indexing. No requirement extraction.
No graph building. No automated fact generation. All facts were hand-curated.

---

## Produced-But-Never-Consumed Artifacts

```
.local/spec-artifacts/ (34 files):
  FODS-SPEC-001-normalized.json    ← NEVER READ
  FODS-SPEC-001-index.json         ← NEVER READ
  FODS-SPEC-001-digest.json        ← NEVER READ
  FODS-SPEC-001-req-graph.json     ← NEVER READ
  FODS-SPEC-001-requirements.json  ← QUARANTINED
  [Similar for DIF, FODT, GNUMERIC, NETPBM, ZST]

.local/spec-cache/{format}/{version}/normalized/:
  text.txt      ← EXISTS (57,803 lines for FODS alone), NEVER QUERIED
  pages.jsonl   ← EXISTS, NEVER QUERIED
  sections.jsonl ← NOT CREATED (build_section_index never runs)
  chunks.jsonl   ← NOT CREATED (build_chunk_index never runs)
```

---

## Fact Count by Format

Source: spec-to-feature-radical-correction-plan.md §2

| Format | Verified Facts | Source | Evidence |
|---|---|---|---|
| FODS | 10 (9 verified, 1 quarantined: FACT-FODS-002) | acquisition-packs/fods/verified-facts.yaml | Hardcoded in build_spec_workbench.py lines 115-137; ran run030 2026-05-06 |
| FODT | ~10 (similar to FODS) | acquisition-packs/fodt/verified-facts.yaml | Similar process |
| ZST | 2 (both verified) | .local/spec-cache/zst/rfc8878/ | FACT-ZST-001, FACT-ZST-002 |
| CSV | 2 (manually created) | FACT-CSV-001 (record), FACT-CSV-002 (field) | RFC 4180 refs; NOT SAL-extracted |
| NDJSON | 2 (manually created) | FACT-NDJSON-001, FACT-NDJSON-002 | ndjson.org refs; NOT SAL-extracted |
| Others (18 formats) | 1-3 per format | Manually created for qname registry seeding | Not SAL-extracted |

---

## SAL Chain Status Per Format

### CHAIN_INTACT (10 formats): ODS, ODT, FODS, FODT, FODG, FODP, PBM, PGM, PPM, QOI
- These use ODF 1.3 spec or image format specs that the SAL extraction ran against
- Facts were at least partially extracted or verified against actual spec text
- SAL facts in .local/spec-cache/ reference specific spec sections
- **Evidence:** reports/machinery-truth/ chain verification; CHAIN_INTACT status confirmed 2026-06-23

### CHAIN_BROKEN_AT_SAL (10 formats): ABW, CSV, DIF, GNUMERIC, NDJSON, SYLK, TOML, TSV, XCF, ZST
- SAL extraction never ran for RFC-based or schema-based spec formats
- Facts are provisional — created manually for qname registry seeding purposes
- No normalized spec text, no section index, no chunk index for these formats
- **Evidence:** 10 GAP-CHAIN-*-SAL entries added to gap-ledger.json (P3/LOW priority, MEMORY.md 2026-06-23)
- **Assessment:** EXPECTED state. Non-ODF formats require different SAL strategy (TC-0015).

---

## Integration Failure Root Cause

Source: spec-to-feature-radical-correction-plan.md §2

The pipeline was DESIGNED as:
```
spec_discovery → normalization → section_indexing → chunk_indexing →
fact_extraction → fact_verification → requirement_graph → capability_derivation
```

**It STOPPED after step 2 (normalization).** Steps 3-8 exist as code but were NEVER executed
in production. Facts were instead created manually in run030 (2026-05-06) and never regenerated.

**Root cause: No orchestrator chains these tools.**
- Each is a standalone CLI
- No scheduler, no cron, no master runner
- No automated trigger from new spec acquisition
- No automated re-run on spec update

---

## What Does Work Well

1. **3 active SAL tools** are correctly integrated:
   - `spec_source_registry.py`: tracks spec sources by format ID
   - `context_pack_builder.py`: builds context bundles for agent consumption
   - `spec_governance_runtime.py`: blocks spec fact citation fraud

2. **validate_spec_fact_refs.py** correctly blocks work items citing non-existent FACT-* IDs

3. **authority_gate_validation.py** correctly computes authority levels (P0-P6)

4. **Knowledge freshness validator** (V68) checks VERIFIED_CURRENT contracts vs source hashes

---

## Required Correction (from plan §2)

The SAL does NOT need to be rebuilt. The infrastructure EXISTS. It needs:

1. **ORCHESTRATION:** Create `sal_master_runner.py` that chains:
   `spec_discovery → spec_normalizer → build_section_index → build_chunk_index → requirement_extractor → fact_verification`

2. **WIRING:** Connect dormant tools to their intended downstream consumers

3. **CONSUMPTION:** Make capability layer actually read SAL-generated facts (not manual git files)

4. **ITERATION:** Run pipeline for at least 1 non-ODF format (e.g., CSV via RFC 4180 PDF) as proof

5. **VALIDATION:** Add validator that rejects formats with < N verified facts (SAL-generated, not manual)

**Cost:** Medium — infrastructure exists; requires orchestrator script + one test run

**Evidence this is possible:** FODS already has 57,803 lines of normalized spec text in
.local/spec-cache/fods/ — if the downstream tools were wired, FODS could have automated
fact extraction. CSV/ZST would need PDF download (acquire_spec.py exists but DRY-RUN only).

---

## SAL Audit Verdict

| Dimension | Status | Evidence |
|---|---|---|
| Is SAL built? | YES | 20+ tools exist with tests |
| Does SAL work? | PARTIAL | 3/20 tools active; 17 dormant |
| Are facts deterministic? | NO | Facts manually seeded; not auto-extracted |
| Are facts traceable to spec? | PARTIAL | ODF formats yes (spec section refs); non-ODF no |
| Does SAL reject unsupported claims? | YES | validate_spec_fact_refs.py blocking |
| Is SAL ready for broad product deepening? | NO | Non-ODF formats have provisional facts only |
| Can SAL be repaired without full rebuild? | YES | Infrastructure exists; needs orchestrator |
