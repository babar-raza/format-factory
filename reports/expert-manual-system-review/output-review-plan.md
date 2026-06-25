# Output and Evidence Review Plan
# Format Factory — Expert Manual System Review
# Phase 6 output — Generated: 2026-06-25

## Purpose

Assess the quality and reliability of all types of outputs produced by Format Factory:
1. Source code outputs (products)
2. Test outputs
3. Sprint evidence bundles
4. Authority registry claims
5. Sprint review packages

## Output Types and Assessment

### Type 1: Source Code (src/ directory)

**Authority:** HIGHEST (actual product)
**Assessment approach:** Read source directly; form independent opinion; compare to authority claims.

| Product | Source Reviewed | Score | Key Finding |
|---------|----------------|-------|------------|
| FODS .NET | YES (FodsPdfExporter, FodsOdsExporter) | 3.79/5 | ODS "PROTOTYPE" vs. POC PASS; PDF Latin-1 only |
| FODT .NET | YES (FodtBody) | 3.67/5 | No table traversal in public API |
| ZST .NET | YES (ZstParser.cs) | ~0.5/5 | Probe-only confirmed; no decompression |
| FODP Python | YES (fodp_codec.py) | ~2.5/5 | Has exports; no write_fodp |
| ODS Python | YES (ods_writer.py) | ~3.0/5 | write_ods() confirmed functional |
| PBM/PGM/PPM | YES (summary) | ~3.0/5 | write_pbm/pgm/ppm confirmed |

### Type 2: Test Files

**Authority:** HIGH (actual behavior verification)
**Assessment approach:** Count test files, classify test types (smoke vs. behavioral vs. roundtrip), spot-check test names.

**Current issue:** Tests are not executed during this review — only structure inspected.
Test pass/fail state taken from last sprint evidence (840 tests passed 2026-06-25).

| Product | Test Files | Quality Assessment |
|---------|-----------|-------------------|
| FODS .NET | 71 | Good density; mix of unit and integration |
| FODT .NET | 64 | Good density |
| NetPBM | 56 | High density; strong for image library |
| CSV/TSV/NDJSON .NET | 6 each | Too thin for commercial quality |
| ZST .NET | 2 | Critically thin; probe-only tests |
| FODS Python | 93 | Excellent density |
| FODT Python | 131 | Excellent density |

### Type 3: Sprint Evidence Bundles

**Authority:** ADVISORY (generated from sprint claims)
**Location:** `.local/evidences/`
**Known issue:** Evidence quality grading requires LLM API keys. Without keys:
- Spec-parity `PRODUCT_SOURCE` items → `DEFERRED_WITH_REASON`
- Evidence quality can be 0.0 without blocking continuation
- Quality degradation is silent

**Assessment questions:**
1. How many evidence bundles exist?
2. What proportion of items are `DEFERRED_WITH_REASON` vs. genuinely graded?
3. Are evidence ZIPs being created?

### Type 4: Authority Registry Claims

**Authority:** ADVISORY (self-declared in poc-targets.yaml)
**Known discrepancy:** FodsOdsExporter marked "PROTOTYPE" in source but "PASS" in poc-targets.

| Registry | Authority | Known Issues |
|---------|-----------|-------------|
| poc-targets.yaml | SELF_DECLARED | ODS exporter PROTOTYPE vs. PASS |
| parity-matrix.yaml | SELF_DECLARED | FODS=PARTIAL, FODT=BLOCKED (per TC-QHARD-POST-005) |
| format-registry.yaml | AUTHORITATIVE | 25 formats including target writers |
| qname-registry/*.yaml | AUTHORITATIVE | 20 files; most seeded/implementing |

### Type 5: Sprint Review Packages

**Authority:** ADVISORY (generated from declarations)
**Last sprint:** `ff-test-coverage-20260625` — 840 tests passed, 0 failed
**Location:** `.local/evidences/ff-test-coverage-20260625/`

## Output Reliability Matrix

| Output Type | Reliability | Can Mislead | Action |
|-------------|-------------|-------------|--------|
| Source code (src/) | HIGHEST | NO | Read directly |
| Test files | HIGH | LOW (no execution) | Inspect names; classify types |
| Evidence declarations | MEDIUM | YES (if LLM unavailable) | Check DEFERRED items |
| poc-targets.yaml | MEDIUM | YES (PASS claims) | Verify against source |
| parity-matrix.yaml | LOW-MEDIUM | YES (advisory) | Cross-check with SAL |
| gap-ledger.json | LOW | YES (unknown categories) | Cannot route by category |
| Sprint review packages | MEDIUM | MEDIUM | Check included files |

## Review Constraints (From plan-mode-limitations.md)

- Tests are NOT executed — only structure inspected
- Physical output files (PDFs, PNGs, ZIPs) are NOT regenerated
- Installed package behavior is accepted from prior sprints
- Evidence quality without LLM grader is advisory only
