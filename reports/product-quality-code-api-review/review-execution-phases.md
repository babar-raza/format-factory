# Review Execution Phases

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Overview

The product quality review and fix cycle is divided into 6 phases (A through F). Phases A and B
are read-only (already complete in this sprint). Phases C through F are execution phases requiring
source modifications and are subject to Gate approval workflows.

---

## Phase A — Product Inventory and API Extraction (COMPLETE)

**Status:** COMPLETE (executed in this review sprint)

**Purpose:** Establish ground truth of what each product actually is — not what it claims to be.

**Inputs:**
- `src/net/` — all 10 .NET product directories
- `src/python/` — all 20 Python FOSS package directories
- `tests/` — test suite structure
- `examples/python/` — example scripts
- `packaging/python/` — build and package metadata

**Outputs produced:**
- `src-product-inventory.json` — maturity classification per product
- `product-format-matrix.json` — capability flags (has_load, has_save, etc.)
- `product-source-map.md` — file-by-file role mapping

**Completion criteria:** All 30 products inventoried with maturity classification and API entry points.

---

## Phase B — Deep Product Quality Review (COMPLETE)

**Status:** COMPLETE (executed in this review sprint)

**Purpose:** Score each product across 18 quality dimensions. Produce the problem matrix.

**Inputs:** Phase A outputs + full source inspection

**Outputs produced:**
- `public-api-matrix.json` — API quality scores
- `architecture-review-matrix.json` — class segregation scores
- `feature-availability-matrix.json` — FA-0 to FA-5 per feature per product
- `feature-complexity-matrix.json` — C0 to C5 complexity scores
- `dotnet-product-quality-matrix.json` — 18-dimension .NET commercial scores
- `python-product-quality-matrix.json` — FOSS readiness scores
- `test-meaningfulness-matrix.json` — TQ-0 to TQ-5 per product
- `examples-docs-package-matrix.json` — EW-0 to EW-5 per product
- `product-claim-vs-reality-matrix.json` — 9 contradictions classified
- `product-quality-problem-schema.json` — 20 problems (PQ-001 to PQ-020), P0/P1/P2/P3

**Completion criteria:** All matrices scored. Problem matrix finalized.

---

## Phase C — Dry Run Scoring Validation

**Status:** PENDING

**Purpose:** Validate that the scoring rubrics are calibrated correctly. Confirm rubrics catch
known-weak products and reward known-strong products.

**Method:** Apply rubric formulas to Phase B outputs. Compare scores against known expectations:

| Product | Expected Tier | Actual Score | Pass/Fail |
|---------|---------------|-------------|-----------|
| FODS .NET | COMMERCIAL_CANDIDATE | ~3.8-4.2 | Verify |
| FODT .NET | COMMERCIAL_CANDIDATE | ~3.8-4.0 | Verify |
| NetPBM .NET | COMMERCIAL_CANDIDATE | ~3.8-4.1 | Verify |
| ZST .NET | DEMO_PROTOTYPE | ~1.5-2.0 | Verify |
| HTML .NET | NOT_PRODUCT | ~0.5-1.0 | Verify |
| FODS Python | PY-3 to PY-4 | ~3.5-4.0 | Verify |
| FODP Python | PY-1 to PY-2 | ~1.2-1.8 | Verify |

**Pass criteria for dry run:**
- ZST .NET scores < 2.5 (lowest .NET product) ✓
- HTML/Markdown/TXT .NET score < 1.5 (writer-only) ✓
- FODP Python scores < 2.0 (read-only, no write) ✓
- FODS .NET scores > 3.5 (highest .NET commercial candidate) ✓
- No product with critical OPEN blocks_release=true problems scores > 3.5

**Inputs:** Phase B matrix files
**Outputs:** `dry-run-plan.md` (this session), `dry-run-results.md` (execution session)
**No source changes required.**

---

## Phase D — Live Read-Only Review

**Status:** PENDING

**Purpose:** Full product/code/API review. Confirm all NEEDS_CONFIRMATION findings. Finalize
the scored problem matrix for fix sprint planning.

**Method:**
1. Execute confirmation workflow from `product-quality-confirmation-process.md`
2. Update confidence levels for all LIKELY and NEEDS_CONFIRMATION problems
3. Re-score any products whose scores change after confirmation
4. Generate final problem matrix sorted by: (fix_priority ASC, blocks_release DESC, severity DESC)

**Key confirmation targets:**
- PQ-012: FODT .NET table operations wired? (NEEDS_CONFIRMATION → expect CONFIRMED)
- Contradiction-002: ZST capability map (NEEDS_VERIFICATION → expect CLAIM_CONTRADICTED)
- Contradiction-003: 14 Python formats at PROOF_LEVEL_4 (NEEDS_VERIFICATION → expect LIKELY_TRUE)

**Inputs:** Phase B outputs + confirmation process document
**Outputs:** Final `product-quality-problem-schema.json` (all VERIFIED), `confirmed-problem-report.md`
**No source changes required.**

---

## Phase E — Pilot Product Quality Fix

**Status:** PENDING (requires explicit approval)

**Purpose:** Prove fix → verify loop works before scaling to all 30 products.

**Recommended pilot target:** ZST .NET Writer (PQ-007)

**Rationale for ZST as pilot:**
- PQ-007 is CRITICAL severity, P0, blocks_release=true
- ZstDocument is currently a pure DTO with no write/compress capability
- Python ZST has compress/decompress — the .NET product is the only family member missing this
- Adding ZstWriter is a contained, bounded change (new class, no impact on ZstParser or ZstDocument)
- Verification is straightforward: write a roundtrip test (compress string → decompress → compare)

**Alternative pilot targets (if ZST writer is too large):**
- Option B: Python pyproject.toml metadata enrichment across all 20 packages (PQ-004)
  - Low risk, high packaging value, XS effort per package
  - Verification: read pyproject.toml files and confirm new fields present
- Option C: FODP Python write capability stub (PQ-009)
  - Add `write_fodp()` raising `NotImplementedError("FODP write not yet supported")`
  - Rename `consumer_roundtrip.py` to `consumer_inspect.py`
  - XS effort, HIGH visibility fix

**Pilot fix → verify sequence:**
1. Read target source file
2. Implement fix (source modification — requires approval for this phase)
3. Write regression test
4. Run test: `pytest tests/... -v`
5. Update problem status in `product-quality-problem-schema.json` to RESOLVED
6. Update `product-claim-vs-reality-matrix.json` if applicable
7. Record evidence in `.local/evidences/product-quality-fixes/`

**Inputs:** Phase D confirmed problem matrix + approval
**Outputs:** Fixed source file + regression test + evidence bundle
**Source changes: YES — requires sprint approval**

---

## Phase F — Unified Product Quality Execution

**Status:** PENDING (requires Phase E completion + approval)

**Purpose:** Systematically fix all P0, P1, P2 problems across all 30 products.

**Execution groups (ordered by priority):**

### Group 1 — Release Blockers (P0, blocks_release=true)

| PQ-ID | Product | Fix | Effort |
|-------|---------|-----|--------|
| PQ-007 | ZST .NET | Add ZstWriter class | L |
| PQ-006 | FODS .NET | Fix csproj Gate 11 description | XS |
| PQ-002 | FODS Python | Choose one canonical API | L |
| PQ-009 | FODP Python | Add write stub + rename example | XS |

### Group 2 — Critical P1 Packaging and API Fixes

| PQ-ID | Product | Fix | Effort |
|-------|---------|-----|--------|
| PQ-004 | All Python (20) | Enrich pyproject.toml metadata | S per package |
| PQ-005 | All .NET (10) | Create README.md per product | M per product |
| PQ-014 | All 30 products | Create README.md | XL total |
| PQ-001 | All Python (20) | Replace wildcard imports with explicit __all__ | M |
| PQ-008 | FODS .NET, FODT .NET | Add Load(Stream) overload | S each |
| PQ-010 | NDJSON .NET | Add NdjsonRecord typed wrapper | M |
| PQ-012 | FODT .NET | Wire table operations or remove stubs | L or XS |

### Group 3 — P2 API and Documentation Improvements

| PQ-ID | Product | Fix | Effort |
|-------|---------|-----|--------|
| PQ-003 | All Python | Update examples to use installed-package imports | M |
| PQ-011 | NDJSON .NET | Rename Load(string content) to LoadFromContent | XS |
| PQ-018 | FODS .NET | Remove static GetColumnHeaders overload | XS |
| PQ-019 | All Python | Add CLI entry points to key packages | M |

### Group 4 — P3 Deferred (if capacity allows)

| PQ-ID | Product | Fix | Effort |
|-------|---------|-----|--------|
| PQ-013 | NetPBM .NET | Add XML doc comment to NetpbmExporter | XS |
| PQ-016 | All Python | Delete or wire _shared/ base classes | S |
| PQ-017 | All .NET | Rename sprint-named tests to feature-based | L |
| PQ-020 | All Python | Generate .pyi type stubs | L |

**Total estimated effort for P0+P1+P2:** ~L-XL (weeks of fix work)
**Verification method:** Automated test suite (existing + new regression tests) + manual API smoke test

**Inputs:** Phase E pilot + approved problem matrix
**Outputs:** Fixed products + updated test suite + release candidates
**Source changes: YES — requires full sprint authorization**

---

## Phase Dependency Graph

```
Phase A (DONE) ──► Phase B (DONE) ──► Phase C (dry run)
                                           │
                                           ▼
                                       Phase D (live read-only)
                                           │
                                           ▼
                                       Phase E (pilot fix) ──► Phase F (unified fixes)
```

---

## Success Criteria per Phase

| Phase | Success Criteria |
|-------|-----------------|
| A | All 30 products inventoried; maturity assigned |
| B | All matrix files populated; 20+ problems identified |
| C | Rubric correctly scores ZST .NET < 2.5 and FODS .NET > 3.5 |
| D | All NEEDS_CONFIRMATION problems resolved; final problem matrix locked |
| E | Pilot fix implemented, test passes, problem status RESOLVED |
| F | All P0 problems RESOLVED; P1 problems >= 80% RESOLVED |
