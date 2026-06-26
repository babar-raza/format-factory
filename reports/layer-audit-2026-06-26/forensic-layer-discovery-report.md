# Format Factory — Forensic Layer Discovery Report
**Mission:** FORMAT-FACTORY-LAYER-AUDIT-20260626
**Date:** 2026-06-26
**HEAD:** a3ed0a0c (branch: main) — *Baseline Refresh 2026-06-26: updated from 555aa4c7, +179 commits*
**Authority:** Repository truth only. No prior report, summary, or conversation is trusted without verification.

---

### Baseline Refresh (2026-06-26)

Repository HEAD advanced from `555aa4c7` to `a3ed0a0c` (+179 commits). Dominant changes: 70 feat(net-deepening) commits expanding .NET commercial layer (L06), 15 feat(net) commits, 3 feat(oracle) commits (L05), and 1 feat(sal) commit completing SAL WIRE/BACKFILL (L01). Gap ledger updated: 1,246 entries (was 1,242); `closed_by` field absent in all sampled closed entries — closure evidence quality is INDETERMINATE.

---

## STATUS AND REPOSITORY BINDING

| Dimension | Value |
|---|---|
| Python format packages | 20 (abw csv dif fodg fodp fods fodt gnumeric ndjson ods odt pbm pgm ppm qoi sylk toml tsv xcf zst) |
| .NET format packages | 10 (csv fods fodt html markdown ndjson netpbm tsv txt zst) |
| Python source files | 614 |
| .NET source files | 138 |
| Supervisor tools | 199 Python files |
| Governance validators | 82 functions across 9 files |
| Registered skills | 72 |
| Claude commands | 72 |
| QName registry entries | 79 (75 implemented, 3 verified, 1 architecture_only) |
| GAP ledger entries | 1,242 (1,203 closed = 96.8%) |
| SAL facts total | 14,315 (but only 5 formats have real facts) |
| Sprint session | MODE 4, iteration=5, autonomous_continue=false (POST_PLAN_TERMINAL) |

---

## 1. DISCOVERED LAYERS — SUMMARY TABLE

| ID | Layer Name | Exists | Actual Form | Maturity | Target | Recommended Disposition |
|---|---|---|---|---|---|---|
| L01 | Specification Authority (SAL) | Partial | Tools exist; 5/20 formats have facts | L2 | L4 | RETAIN AND COMPLETE |
| L02 | QName Hierarchy Authority | Yes | 79 entries, 75 implemented | L3 | L4 | RETAIN AND HARDEN |
| L03 | Requirement and Capability | Yes | 1,242 entries, 96.8% closed | L3 | L4 | RETAIN AND AUDIT |
| L04 | Sample Corpus | Partial | 177 files, no governance | L2 | L3 | FORMALIZE AS SUBLAYER of L01 |
| L05 | Test Oracle / Conformance | Partial | FODS/FODT only, 2 of 20 | L2 | L4 | RETAIN AND EXTEND |
| L06 | Product Source | Yes | 20 Python + 10 .NET formats | L4 | L5 | RETAIN (ongoing) |
| L07 | Test Infrastructure | Yes | 2,092 Python + 389 .NET test files | L4 | L5 | RETAIN AND PRUNE |
| L08 | Evidence and Review Package | Yes | Active every sprint | L4 | L4 | RETAIN |
| L09 | State and Continuation | Yes | CCI hardened, 45 tests | L4 | L4 | RETAIN AND HARDEN |
| L10 | Plan and Prompt Authority | Yes | Fragmented — 16 plans + 200+ taskcards | L3 | L4 | CONSOLIDATE |
| L11 | Supervisor and Sprint | Yes | Production grade, 199 files | L5 | L5 | RETAIN |
| L12 | Governance and Policy | Yes | 82 validators, 109+ tests | L4 | L5 | RETAIN AND CONSOLIDATE |
| L13 | Skill and Command Execution | Yes | 72 skills, 72 commands | L4 | L5 | RETAIN AND HARDEN |
| L14 | Source-Change Handoff | Yes | Ledger + handoff scripts | L3 | L4 | MAKE SUBLAYER of L13 |
| L15 | Release and Packaging | Partial | Python local build only | L3 | L4 | RETAIN AND COMPLETE |
| L16 | AI Boundary | Partial | Contracts defined, weak enforcement | L2 | L3 | CONSOLIDATE OR SIMPLIFY |
| L17 | Feature Compilation | Yes | Two implementations, near-zero output | L3 | L3 | DEDUPLICATE |
| L18 | Knowledge and Discoverability | Yes | AGENTS.md 78KB, MEMORY.md truncated | L3 | L4 | RETAIN AND STRUCTURE |
| L19 | Dogfood and Consumer Evidence | Partial | Examples for most formats, not tracked | L2 | L3 | FORMALIZE AS SUBLAYER of L08 |
| L20 | Regression and Compatibility | Partial | Ledgers exist, no automation | L2 | L3 | FORMALIZE AS SUBLAYER of L07 |
| L21 | Provenance and Artifact Identity | Partial | git_head in declarations, no chain | L1 | L3 | CROSS-CUTTING POLICY in L08+L15 |
| L22 | Product Architecture | Yes | LOC caps + analytics separation | L3 | L4 | CROSS-CUTTING POLICY, enforced by L12 |
| L23 | Format and Legal Obligation | Partial | format-registry.yaml legal_category | L1 | L3 | SUBLAYER of L13 (skill-governed) |
| L24 | Security Authority | Partial | FODT malformed tests only | L1 | L3 | SUBLAYER of L07 |

---

## 2. MOST IMPORTANT FINDING: THE SAL FACTS GAP

**The specification→fact pipeline is broken for 14 of 20 Python formats.**

```
Formats WITH real SAL facts (≥1 spec_fact):
  FODS:   4,987 facts  ✓
  FODT:   4,933 facts  ✓
  ODS:    1,066 facts  ✓
  ODT:    1,066 facts  ✓
  FODG:   1,066 facts  ✓
  FODP:   1,066 facts  ✓
  ZST:       94 facts  ✓ (partial)

Formats with ZERO SAL facts:
  CSV, TSV, NDJSON, ABW, DIF, GNUMERIC, SYLK, TOML, XCF, PBM, PGM, PPM, QOI, ORA
```

This breaks the entire intended flow for those 14 formats:

```
EXTERNAL SPEC → LOCAL SNAPSHOT → PARSED FACTS → QNAME → CAPABILITY → FEATURE → TASKCARD
    ✓ (PDFs exist)       ✓                 ✗ BROKEN HERE for 14 formats
```

**Consequence:** The QName registry entries for those 14 formats have no `spec_fact_ref`. The capability layer cannot trace gaps to spec requirements. The product source for those formats has no authoritative spec backing in the pipeline.

**Root cause:** The SAL extraction pipeline (`sal_master_runner.py`, `run_extraction_pipeline.py`) works for ODF family formats (FODS, FODT, ODS, ODT, FODG, FODP) because they share a common OASIS XML specification structure. For other formats (CSV/RFC 4180, ZST/RFC 8878, NDJSON/informal spec, etc.) the extractor has not been configured.

---

## 3. END-TO-END FLOW TRACE

### 3.1 FODS (Mature ODF Format — Best Case)

| Step | Artifact | Status |
|---|---|---|
| External spec | OASIS ODF 1.3 Part 3 | ✓ PDF at `.local/spec-cache/fods/` |
| Local snapshot | `OpenDocument-v1.3-os-part3-schema.pdf` 24MB | ✓ |
| Normalized text | `1.3/normalized/text.txt` 2.2MB | ✓ |
| SAL facts | 4,987 FACT-FODS-NNN records | ✓ |
| QName registry | 12 entries (`fods:table`, `fods:sheet`, etc.) | ✓ |
| Python source | 12 files (parser, neutral_model, constants, etc.) | ✓ |
| .NET source | 25 .cs files | ✓ |
| Python tests | 96 test files | ✓ |
| .NET tests | 99 test files | ✓ (611 tests per completion matrix) |
| Oracle | `oracle/formats/fods/` 5 files | ✓ |
| Packaging | Python wheel in matrix | ✓ |
| Gate 11 | 8/31 criteria met (C3/C4/C5/C8/C9 + P3/P4/P5) | PARTIAL |

**Flow verdict: MOST COMPLETE.** Gap: Gate 11 remains partial.

### 3.2 CSV (Tabular Format — Representative Gap Case)

| Step | Artifact | Status |
|---|---|---|
| External spec | RFC 4180 (informal, 1-page IETF memo) | Unclear |
| Local snapshot | `.local/spec-cache/csv/` 5 files | ✓ (exists) |
| SAL facts | **2 facts** (minimal) | ✗ BROKEN |
| QName registry | 3 entries | ✓ (entries exist, no spec_fact_ref) |
| Python source | 17 files | ✓ |
| .NET source | 10 .cs files | ✓ |
| Python tests | 53 files | ✓ |
| .NET tests | 19 files | ✓ |
| Oracle | `oracle/formats/csv/` 5 files (no LibreOffice comparator) | PARTIAL |
| Packaging | Not in package matrix | ✗ |

**Flow verdict: BROKEN AT STEP 3.** No authoritative spec facts. Downstream layers have no spec backing.

### 3.3 ZST (Binary/Compressed — Representative Binary Case)

| Step | Artifact | Status |
|---|---|---|
| External spec | RFC 8878 / Zstandard frame format | Exists in cache |
| SAL facts | **94 facts** | PARTIAL |
| QName registry | 3 entries | ✓ |
| Python source | 40 files (large analytics file) | ✓ |
| .NET source | 10 files | ✓ |
| Python tests | 294 test files | ✓ (many are arithmetic-deepening) |
| Oracle | Format oracle unclear (no LibreOffice equivalent) | ✗ |

**Flow verdict: PARTIAL.** 94 facts is better than 0 but ZST has 294 Python test files — many without spec backing.

---

## 4. FALSE LAYER IDENTIFICATION

### 4.1 `taskcards/` Directory (200+ Subdirs)
**NOT a layer.** This is a historical sprint archive. Active work items live in `.local/supervisor/next-work-items.json`. The taskcards/ directory has 200+ sprint subdirectories that no automated system reads. It is an observation surface that should be moved to `.local/sprint-history/` (gitignored) to reduce repository noise.

### 4.2 `docs/` as Architectural Authority
**NOT authoritative.** `docs/architecture.md` states: *"STALENESS WARNING: The folder tree and pipeline architecture sections below describe the Phase 0 design. The system has evolved significantly."* The actual architecture is enforced through `registry/source-structure-baseline.json`, governance validators, and `docs/code-quality/production-library-standard-v2.md`. Plain docs are human reference, not machine authority.

### 4.3 `ai_product_brain.py` / `ai_learning_loop.py` / `ai_implementation_designer.py`
**Status unclear — likely dead code.** Three Python files in `tools/supervisor/` with no documented consumers, no tests referencing them, and no skill registration. They appear to be exploratory tools that were never productionized. Recommend audit: either wire them into a declared consumer with tests, or delete.

### 4.4 `failure-memory.json` as Active Learning
**MEMORY.md states:** *"Zero durable learning: All decision rules are static. No failure-memory.json exists. Corrections do not auto-propagate."* The file `.local/supervisor/failure-memory.json` exists but drives no decisions in `autonomous_cycle.py`. This is a false layer — the file exists without being consumed.

### 4.5 Plans Hardening Addenda Proliferation
Six hardening addendum files exist in `plans/`:
- `floating-stargazing-globe-hardening-addendum-20260623.md`
- `cap-fact-forensics-repair-hardening-addendum.md`
- `vivid-napping-kurzweil-hardening-addendum.md`
- `misty-hopping-token-hardening-addendum.md`
- `generic-soaring-chipmunk-hardening-addendum.md`
- `oracle-layer-hardening-addendum.md`

Each represents resolved work that should either be closed in master-plan.md or archived. Having 6 addendum files alongside the master plan fragments authority.

### 4.6 Gap Ledger 96.8% Closure Rate
**Suspicious, requires audit.** 1,203 of 1,242 gaps are closed. This is the *capability layer producing near-zero work items*, which causes the feature compiler to generate only 3 work items. Either:
- Most gaps were genuinely closed through verified implementation, OR
- The closure engine closed gaps based on supervisor grading without independent test evidence

This requires gap_verification_engine.py audit before trusting the ledger state.

---

## 5. HANDOFF GAP ANALYSIS

| Handoff | Upstream | Downstream | Status | Critical Issue |
|---|---|---|---|---|
| H01 | SAL (L01) | QName (L02) | PARTIAL | Broken for 14 formats with 0 SAL facts |
| H02 | SAL (L01) | Capability (L03) | UNVALIDATED | Gap closures lack SAL-backed provenance |
| H03 | Capability (L03) | Feature Compiler (L17) | PARTIAL | Near-zero output (3 work items) |
| H04 | Feature Compiler (L17) | Supervisor (L11) | VERIFIED | gap_ledger_ref injection works |
| H05 | Supervisor (L11) | Product Source (L06) | PARTIAL | Handoff exists but detection not prevention |
| H06 | Product Source (L06) | Tests (L07) | UNVALIDATED | 697 test files are arithmetic-only, no spec tracing |
| H07 | Tests (L07) | Evidence (L08) | VERIFIED | Test results captured correctly |
| H08 | Evidence (L08) | State/Continuation (L09) | VERIFIED | Continuation signal written correctly |
| H09 | Product Source (L06) | Packaging (L15) | PARTIAL | .NET NuGet not automated; install-proof is shallow |
| H10 | Oracle (L05) | Product Source (L06) | UNVALIDATED | No feedback loop from oracle discrepancies to source |
| H11 | QName (L02) | Product Source (L06) | PARTIAL | V53 enforces spec_qname but entries have no verified fact |

**Most critical gap:** H01 (SAL→QName) broken for 14 formats. Every downstream handoff for those formats lacks spec authority.

---

## 6. LAYER MATURITY SCORES — Full 25-Dimension Assessment (TC-LA-AUDIT-003)

**Generated:** 2026-06-26 | **Formula:** v1.0 | **Assessment file:** `reports/layer-audit-2026-06-26/maturity-assessment-full.yaml`

**Maturity Bands:** L0=Absent (0–0.5) · L1=Conceptual (0.5–1.5) · L2=Partial (1.5–2.5) · L3=Operational (2.5–3.5) · L4=Governed (3.5–4.5) · L5=Production (4.5–5.0)

**Scale:** 0=absent, 1=conceptual, 2=partial, 3=operational, 4=governed, 5=production

**Bucket weights:** Contract×1.5 · Validation×1.5 · Lifecycle×1.0 · Integration×1.0 · Overhead×0.75 · Σ=5.75

### CONTRACT Bucket (weight 1.5) — input_contract, output_contract, schema_quality, authority_clarity, provenance

| Layer | in_ctr | out_ctr | schema | authority | provenance | **Bucket Avg** |
|---|---|---|---|---|---|---|
| L01 SAL | 3 | 3 | **0** | 4 | 3 | 2.60 |
| L02 QName | 3 | 4 | 3 | 4 | 4 | 3.60 |
| L03 Capability | 3 | 4 | 3 | 4 | 3 | 3.40 |
| L05 Oracle | 4 | 4 | 3 | 5 | 3 | 3.80 |
| L06 .NET | 4 | 4 | 3 | 4 | 3 | 3.60 |
| L07 Python | 4 | 4 | 3 | 5 | 3 | 3.80 |
| L08 Evidence | 5 | 4 | 5 | 5 | 4 | 4.60 |
| L09 State | 5 | 5 | 4 | 5 | 4 | 4.60 |
| L11 Supervisor | 5 | 5 | 5 | 5 | 4 | 4.80 |
| L12 Governance | 5 | 4 | 5 | 5 | 4 | 4.60 |
| L13 Skills | 4 | 4 | 3 | 4 | 3 | 3.60 |

### VALIDATION Bucket (weight 1.5) — validation, test_coverage, negative_controls, idempotency, evidence_quality

| Layer | valid | tests | neg_ctrl | idempot | evidence | **Bucket Avg** |
|---|---|---|---|---|---|---|
| L01 SAL | 2 | 1 | 1 | 3 | 2 | 1.80 |
| L02 QName | 4 | 3 | 3 | 4 | 3 | 3.40 |
| L03 Capability | 3 | 2 | 2 | 3 | 2 | 2.40 |
| L05 Oracle | 4 | 4 | 4 | 5 | 3 | 4.00 |
| L06 .NET | 5 | 4 | 4 | 4 | 4 | 4.20 |
| L07 Python | 5 | 5 | 4 | 4 | 4 | 4.40 |
| L08 Evidence | 5 | 4 | 3 | 4 | 5 | 4.20 |
| L09 State | 5 | 5 | 5 | 4 | 4 | 4.60 |
| L11 Supervisor | 5 | 5 | 5 | 5 | 5 | 5.00 |
| L12 Governance | 5 | 5 | 5 | 5 | 4 | 4.80 |
| L13 Skills | 3 | 3 | 2 | 4 | 3 | 3.00 |

### LIFECYCLE Bucket (weight 1.0) — failure_handling, recovery_rollback, versioning_compatibility, stale_state_detection, artifact_identity

| Layer | fail_hdl | recovery | versioning | stale_det | artifact | **Bucket Avg** |
|---|---|---|---|---|---|---|
| L01 SAL | 2 | 2 | 1 | 1 | 3 | 1.80 |
| L02 QName | 2 | 4 | 2 | 3 | 4 | 3.00 |
| L03 Capability | 2 | 3 | 2 | 2 | 3 | 2.40 |
| L05 Oracle | 4 | 4 | 2 | 2 | 4 | 3.20 |
| L06 .NET | 3 | 4 | 3 | 2 | 4 | 3.20 |
| L07 Python | 3 | 4 | 3 | 3 | 4 | 3.40 |
| L08 Evidence | 4 | 3 | 3 | 4 | 5 | 3.80 |
| L09 State | 4 | 4 | 3 | 4 | 4 | 3.80 |
| L11 Supervisor | 5 | 4 | 3 | 4 | 5 | 4.20 |
| L12 Governance | 4 | 4 | 3 | 3 | 4 | 3.60 |
| L13 Skills | 3 | 3 | 2 | 3 | 4 | 3.00 |

### INTEGRATION Bucket (weight 1.0) — skill_command_integration, supervisor_integration, consumer_adoption, responsibility_cohesion, producer_completeness

| Layer | skill_cmd | supervisor | consumer | cohesion | producer | **Bucket Avg** |
|---|---|---|---|---|---|---|
| L01 SAL | 4 | 2 | 3 | 4 | 2 | 3.00 |
| L02 QName | 3 | 3 | 4 | 5 | 3 | 3.60 |
| L03 Capability | 2 | 4 | 4 | 4 | 3 | 3.40 |
| L05 Oracle | 4 | 2 | 2 | 5 | 4 | 3.40 |
| L06 .NET | 3 | 3 | 3 | 4 | 3 | 3.20 |
| L07 Python | 4 | 5 | 4 | 5 | 4 | 4.40 |
| L08 Evidence | 4 | 5 | 4 | 5 | 4 | 4.40 |
| L09 State | 3 | 5 | 5 | 5 | 4 | 4.40 |
| L11 Supervisor | 4 | 5 | 5 | 5 | 5 | 4.80 |
| L12 Governance | 3 | 5 | 5 | 5 | 4 | 4.40 |
| L13 Skills | 5 | 4 | 4 | 4 | 4 | 4.20 |

### OVERHEAD Bucket (weight 0.75) — maintainability, machinery_overhead, product_value, observability, security_compliance

| Layer | maintain | mach_ovhd | prod_val | observ | security | **Bucket Avg** |
|---|---|---|---|---|---|---|
| L01 SAL | 3 | 2 | 4 | 2 | 3 | 2.80 |
| L02 QName | 4 | 3 | 4 | 3 | 4 | 3.60 |
| L03 Capability | 3 | 2 | 4 | 3 | 4 | 3.20 |
| L05 Oracle | 4 | 3 | 5 | 3 | 4 | 3.80 |
| L06 .NET | 4 | 3 | 5 | 3 | 4 | 3.80 |
| L07 Python | 4 | 3 | 5 | 4 | 4 | 4.00 |
| L08 Evidence | 4 | 3 | 5 | 4 | 4 | 4.00 |
| L09 State | 4 | 3 | 5 | 4 | 4 | 4.00 |
| L11 Supervisor | 4 | **2** | 5 | 5 | 4 | 4.00 |
| L12 Governance | 4 | 3 | 5 | 5 | 5 | 4.40 |
| L13 Skills | 3 | 3 | 4 | 3 | 4 | 3.40 |

### MATURITY SUMMARY — Weighted Scores and Verdicts

| Layer | Canonical Name | Ctr×1.5 | Val×1.5 | Lif×1.0 | Int×1.0 | Ovh×0.75 | **Weighted** | **Computed** | **Final** |
|---|---|---|---|---|---|---|---|---|---|
| L01 | Specification Authority (SAL) | 2.60 | 1.80 | 1.80 | 3.00 | 2.80 | **2.35** | L2 | **L2** |
| L02 | QName Hierarchy Authority | 3.60 | 3.40 | 3.00 | 3.60 | 3.60 | **3.44** | L3 | **L3** |
| L03 | Requirement and Capability Authority | 3.40 | 2.40 | 2.40 | 3.40 | 3.20 | **2.94** | L3 | **L3** |
| L05 | Oracle and Conformance Authority | 3.80 | 4.00 | 3.20 | 3.40 | 3.80 | **3.68** | L4 | **L3** ⚠️ |
| L06 | Product Source (.NET Commercial) | 3.60 | 4.20 | 3.20 | 3.20 | 3.80 | **3.64** | L4 | **L4** |
| L07 | Product Source (Python FOSS) | 3.80 | 4.40 | 3.40 | 4.40 | 4.00 | **4.02** | L4 | **L4** |
| L08 | Evidence and Review Package | 4.60 | 4.20 | 3.80 | 4.40 | 4.00 | **4.24** | L4 | **L4** |
| L09 | State and Continuation Authority | 4.60 | 4.60 | 3.80 | 4.40 | 4.00 | **4.35** | L4 | **L4** |
| L11 | Supervisor and Sprint Authority | 4.80 | 5.00 | 4.20 | 4.80 | 4.00 | **4.64** | L5 | **L5** |
| L12 | Governance and Policy Enforcement | 4.60 | 4.80 | 3.60 | 4.40 | 4.40 | **4.42** | L4 | **L4** |
| L13 | Skill and Command Execution | 3.60 | 3.00 | 3.00 | 4.20 | 3.40 | **3.42** | L3 | **L3** |

⚠️ L05: Human override from computed L4 → L3. Rationale: supervisor_integration=2, consumer_adoption=2 — oracle results not consumed in sprint loop. Infrastructure is complete but disconnected from continuous verification.

### Critical Zero Dimensions

| Layer | Zero-Scored Dimension | Impact |
|---|---|---|
| L01 SAL | `schema_quality=0` | No formal schema for sal-facts JSON; `schemas/` directory contains only `_readme.md` |

### Key Gaps by Layer

| Layer | Top Gap | Score Drag |
|---|---|---|
| L01 | No formal SAL schema; 14/20 formats have 0 spec facts | schema_quality=0, test_coverage=1 |
| L02 | No versioning upgrade path; no registration validation | versioning_compatibility=2 |
| L03 | `closed_by` field absent from all closed entries (INDETERMINATE audit verdict) | evidence_quality=2 |
| L05 | Oracle not wired into sprint cycle; verdicts not auto-consumed | supervisor_integration=2, consumer_adoption=2 |
| L06 | Only 10/20 formats; not published to nuget.org | producer_completeness=3, consumer_adoption=3 |
| L07 | 8/20 formats read-only (no write support); not published to PyPI | — |
| L08 | Recovery from failed closeout is manual | recovery_rollback=3 |
| L09 | No skill for state management; stale lock cleanup manual | skill_command_integration=3 |
| L11 | failure-memory.json orphaned; grade-cache 565KB unbounded | machinery_overhead=2 |
| L12 | CI skill-attribution-check is allow_failure=true; grade-cache unbounded | stale_state_detection=3 |
| L13 | No skill versioning; no failure tests; CI enforcement advisory only | versioning_compatibility=2, negative_controls=2 |

---

## 7. TARGET LAYER ARCHITECTURE

The system requires **11 true independent layers** and several sublayers/policies:

```
TRUE INDEPENDENT LAYERS:
┌─────────────────────────────────────────────────────────────────┐
│  L01: Specification Authority                                    │
│    (PDFs → normalized text → SAL facts → authorized facts)      │
│    L04 (Sample Corpus) is a sublayer                            │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  L02: QName and Hierarchy Authority                              │
│    (spec_facts → qname registry → spec_qname validation)        │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  L03: Requirement and Capability Authority                        │
│    (qname + spec_facts → gap_ledger → capability map)           │
│    L17 (Feature Compilation) is a sublayer output               │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  L05: Oracle and Conformance Authority                           │
│    (reference implementation comparison for all formats)         │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  L06: Product Source Layer                                       │
│    (Python FOSS + .NET commercial implementations)               │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  L07: Test Infrastructure                                        │
│    (unit + integration + conformance + security tests)           │
│    L20 (Regression), L24 (Security) are sublayers               │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  L08: Evidence and Review Package                                │
│    (declarations + grading + SHA-256 packages)                   │
│    L19 (Dogfood), L21 (Provenance) are sublayers/policies       │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  L09: State and Continuation Authority                           │
│    (continuation-signal + plan locks + session identity)         │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  L11: Supervisor and Sprint Authority                            │
│    (orchestration, grading, approval gates, next-sprint)         │
│    L10 (Plans) is a sublayer                                     │
└─────────────────────────────────────────────────────────────────┘

CROSS-CUTTING LAYERS (not independent, enforced everywhere):
┌────────────────────────────────────────────────────────────────┐
│  L12: Governance and Policy Enforcement (wired into L11)        │
│  L13: Skill and Command Execution Authority (controls all work) │
│  L22: Product Architecture Authority (enforced by L12)          │
│  L23: Format and Legal Obligation (gated by L13)               │
└────────────────────────────────────────────────────────────────┘

PACKAGING / RELEASE (sublayer of L13 skills):
┌────────────────────────────────────────────────────────────────┐
│  L15: Release and Packaging (Python wheels + .NET NuGet)        │
└────────────────────────────────────────────────────────────────┘
```

---

## 8. GENERATED MICRO-TASKCARDS

Ten micro-taskcards are defined in [layer-audit-baseline.yaml](layer-audit-baseline.yaml):

| ID | Title | Layer | Effort | Priority |
|---|---|---|---|---|
| TC-LA-001 | Register SAL skill + wire to 14 missing formats | L01 | HIGH | P0 |
| TC-LA-002 | Audit gap-ledger closure claims (96.8% closed suspicious) | L03 | MEDIUM | P0 |
| TC-LA-003 | Extend oracle to 5 additional formats | L05 | HIGH | P1 |
| TC-LA-004 | Create /ingest-spec-sal skill and idempotency proof | L13 | LOW | P1 |
| TC-LA-005 | Formalize provenance chain from spec fact to deployed package | L21 | MEDIUM | P1 |
| TC-LA-006 | Archive taskcards/ directory, migrate active items | L10 | LOW | P2 |
| TC-LA-007 | Deduplicate feature compilation implementations | L17 | LOW | P2 |
| TC-LA-008 | Add SAL facts schema, wire validation | L01 | LOW | P2 |
| TC-LA-009 | Fix MEMORY.md truncation — move to topic files | L18 | LOW | P2 |
| TC-LA-010 | Register /run-oracle skill, extend to all 20 formats | L05 | HIGH | P1 |

---

## 9. PRINCIPLES VERIFICATION

| Principle | Status | Finding |
|---|---|---|
| Repository truth outranks reports | ENFORCED | Verified directly from files |
| A folder name ≠ layer exists | VERIFIED | `taskcards/` is not a layer |
| A prompt ≠ implemented layer | VERIFIED | `docs/architecture.md` is stale |
| Schema without producer/consumer is incomplete | VERIFIED | L21 provenance is schema-only |
| Report-only component is not a layer | VERIFIED | `reports/` is observation surface |
| Every proposed layer must justify operational value | VERIFIED | L16 AI boundary is weak, consolidate |
| Gates 0–10 remain autonomous | CONFIRMED | Only Gate 11 G11-G requires Babar Raza |
| Product delivery remains the purpose | CONFIRMED | Machinery serves product work |

---

## 10. EXECUTIVE SUMMARY OF FINDINGS

**What's working well:**
- Supervisor and Sprint Authority (L11) is production-grade — 199 tools, complex but functional
- Governance validators (L12) catch structural violations — 82 functions, 109+ tests
- Skills/Commands (L13) are well-organized — 72 skills covering most work types
- Evidence and Review Package (L08) works every sprint
- State/Continuation (L09) with CCI hardening prevents cross-chat contamination
- Product Source (L06) has 20 Python formats + 10 .NET formats with tests

**Most critical structural failure:**
- L01 (Specification Authority) is broken for 14 of 20 formats — no SAL facts = no spec backing
- This breaks the entire intended flow: spec→fact→qname→capability→feature→product

**Suspicious condition requiring immediate audit:**
- Gap ledger is 96.8% closed (1,203/1,242) — but feature compiler produces only 3 work items
- Either capabilities are genuinely implemented or the closure engine overclaimed

**Complexity concerns:**
- 199 Python files in tools/supervisor/ — single most complex directory
- `taskcards/` has 200+ subdirs with no active authority role
- AGENTS.md is 78KB; MEMORY.md exceeds its 200-line limit

**Machinery that exceeds product value:**
- `ai_product_brain.py`, `ai_learning_loop.py`, `ai_implementation_designer.py` — no consumers, not tested
- `failure-memory.json` — file exists but drives no decisions
- 6 hardening addendum files in plans/ — fragment authority

**Next highest-value actions (in order):**
1. TC-LA-001: Wire SAL to 14 missing formats (P0 — unblocks entire spec→product flow)
2. TC-LA-002: Audit gap-ledger closure claims (P0 — determines if capability layer is honest)
3. TC-LA-004: Register /ingest-spec-sal skill (P1 — gates 1 on governance)
4. TC-LA-003: Extend oracle to 5+ formats (P1 — independent conformance evidence)
5. TC-LA-005: Provenance chain formalization (P1 — enables trustworthy artifact identity)

---

*This report was generated from repository HEAD 555aa4c7 on 2026-06-26.*
*Machine-readable findings: [layer-audit-baseline.yaml](layer-audit-baseline.yaml)*
