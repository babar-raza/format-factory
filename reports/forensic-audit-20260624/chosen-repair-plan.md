# FORMAT FACTORY — SPEC-TO-CODE FORENSIC HEALING PLAN
# Version: 1.0 | Generated: 2026-06-24 | Mission: FF-FORENSIC-AUDIT-20260624

---

## 1. Mission and Scope

**Mission ID:** FF-FORENSIC-AUDIT-20260624
**Scope:** Complete forensic audit of all 25 governed formats across the full spec-to-product pipeline.
**Authorized by:** Explicit user instruction — "Format Factory All-Format Specification-to-Code Forensic Audit"
**Evidence root:** `reports/forensic-audit-20260624/`

This plan coordinates repair of the Format Factory specification-to-product pipeline. It does not replace `plans/strategic/spec-to-feature-radical-correction-plan.md` (the master plan) but adds the forensic traceability layer it requires.

---

## 2. Format Inventory (Summary)

| Status | Count | Formats |
|--------|-------|---------|
| production_track_real | 2 | fods, fodt |
| roundtrip_capable_library | 7 | ods, fodg, zst, abw, gnumeric, qoi, ndjson, toml |
| read_write_prototype | 2 | dif, sylk |
| read_only_prototype | 5 | odt, ppm, pgm, pbm, tsv |
| probe_only | 2 | xcf, fodp |
| prototype_read_write | 1 | csv |
| acquisition_only / blocked | 4 | xpm, pam, zpaq, ora |

Full inventory: [format-inventory.yaml](format-inventory.yaml)

---

## 3. Specification Inventory (Summary)

**Total SAL spec facts:** 14,486 (14,331 workbench-verified)
**ODF family share:** 13,204 facts (91.2% — fods + fodt + ods + odt + fodp + fodg + odf-shared)
**Non-ODF total:** 1,282 facts for 19 formats (avg 67 per format; but most is ZST at 109)

**Critical finding:** 13 non-ODF formats each have 3-9 facts only. Their SAL facts are bootstrap-seeded, not extracted from machine-readable spec text. The SAL pipeline is fully operational only for ODF 1.3.

Full inventory: [specification-source-inventory.yaml](specification-source-inventory.yaml)

---

## 4. Measurement Methodology

- **Spec facts:** Counted from `.local/sal-output/sal-facts-latest.json` (generated 2026-06-24)
- **Semantic units:** Equated to SAL fact count for quantitative pipeline measurement
- **Capabilities:** Counted from `reports/capability-layer/capability_summary.json`
- **Gaps:** Counted from `reports/capability-layer/gap-ledger.json` (1,018 entries)
- **Code LOC:** Measured via Python `sum(1 for _ in open(f))` on all `.py` or `.cs` files
- **Test counts:** Count of `test_*.py` files per format directory

---

## 5. Raw Spec Metrics (Top-Line)

| Metric | Value |
|--------|-------|
| Formats processed by SAL | 25 |
| Total spec facts | 14,486 |
| Verified facts | 14,331 (99.0%) |
| Bootstrap-only facts | 148 (1.0%) |
| ODF family facts | 13,204 |
| Non-ODF facts | 1,282 |
| Average non-ODF facts/format | 67 (skewed by ZST 109; median is 5) |

---

## 6. Normalized Fact Metrics

The SAL pipeline normalizes facts using workbench verification (text-verified or manually verified). Key classification:
- `text_verified`: machine-verified against spec text (dominant in FODS/FODT: 4865/4933 facts)
- `verified`: manually workbench-verified (all ODS/ODT/FODP/FODG/ZST verified facts)
- `bootstrap_only`: not verified — manually seeded without spec text confirmation (148 total)

**Finding:** For ODF formats, the normalization pipeline is excellent (99%+ verification). For non-ODF formats, all facts are either `bootstrap_only` or minimal `verified` (often 2-3 facts per format).

---

## 7. SAL/Authority Findings

| Finding | Evidence |
|---------|---------|
| ODF SAL pipeline: OPERATIONAL | FODS 5009 facts, FODT 4957 facts |
| ZST SAL pipeline: PARTIAL | 109 facts from RFC text (15 bootstrap) |
| Non-ODF (13 formats): CHAIN_BROKEN | Only 2-9 facts each; no automated extraction |
| Bootstrap-only facts: 148 | Not a blocking problem but they are unverified |
| No bypass of SAL detected | All facts pass through sal_master_runner.py |

**Root cause:** SAL pipeline uses PDF text extraction + chunking (ODF) or RFC directory (ZST). For 13 other formats, no spec text is available in spec-cache — only manifest.yaml files.

---

## 8. QName and Hierarchy Findings

**Finding:** TOTAL BREAK in the FACT→QNAME pipeline.

- 20 qname-registry YAML files exist in `shared/qname-registry/`
- All 20 files have `entries: []` (zero entries)
- Parity matrix shows `?` for `qname_compliance` on all 24 formats
- No downstream tool reads or validates qname registry entries

This means the spec-to-code traceability chain **breaks completely at the QNAME layer**:
```
SPEC FACT → [BREAK] → QNAME → CLASS → FILE → CODE
```

Classes have `spec_qname` attributes (e.g., `spec_qname = "table:table"`) but these are not cross-referenced against any registered qname. V53 validates the attribute exists on classes but does not validate it against the registry.

---

## 9. Capability Findings

| Metric | Value |
|--------|-------|
| Total capabilities | 1,766 |
| ODF commercial (FODS/FODT) | 125 — spec-derived, reasonable |
| FOSS reduced (all other) | 1,641 — mostly POC-goal derived |
| Average inflation (non-ODF foss) | ~27x cap/verified-fact |
| Worst case inflation | NDJSON 22x, TSV 48x, XCF 54x |

**Root cause:** The capability_map_generator.py applies goal templates (load/save/inspect/convert) to every format. This produces 60-120 capabilities per format regardless of spec depth. The template is the right approach for ODF (5000 facts support all capabilities). It produces unsupported outputs for non-ODF formats with 2-9 facts.

---

## 10. Feature-Planning Findings

No separate feature-planning layer exists between capabilities and code. The capability = the feature. There is no:
- feature requirement specification document per format
- taskcard generator from capabilities
- acceptance-criteria generator from capabilities

The `capability_feature_compiler.py` converts capabilities directly to work items but does not add acceptance criteria or spec citations at the capability level.

---

## 11. Code Traceability Findings

| Layer | Finding |
|-------|---------|
| Python code present | 20 of 25 formats |
| .NET code present | 10 of 25 formats |
| Roundtrip capable (Python) | 10 formats |
| Read-only (Python) | 6 formats |
| Probe-only or prototype | 4 formats |
| No code | 4 formats |
| Analytics masquerade (40% of ledger) | 394 of 984 ledger entries = analytics type |

The product code quality is good for production-track formats (fods, fodt, zst). For shallow formats the code exists but doesn't implement the full capability contract.

---

## 12. Test/Integration/E2E Findings

| Format | Test Count | Assessment |
|--------|-----------|------------|
| fods (.NET) | 611 | Excellent |
| fodt (.NET) | 567 | Excellent |
| zst | 625 | Excellent (but for a simple codec) |
| fods (Python) | 211 | Good |
| fodt (Python) | 248 | Good |
| abw | 82 | Adequate |
| qoi | 108 | Good |
| ndjson | 80 | Good |
| gnumeric | 73 | Good |
| ods | 69 | Adequate |
| odt | 66 | Minimal |
| fodg | 60 | Minimal |
| xcf | 42 | Minimal |
| sylk | 46 | Minimal |
| ppm/pgm/pbm | 47-49 | Minimal (read-only) |
| dif | 40 | Minimal |
| fodp | 16 | Critical |
| csv, tsv | 19 each | Critical |
| toml | 15 | Critical |

No format has: integration tests, E2E consumer proof, or cross-format conversion tests.

---

## 13–14. Per-Format Metrics and Portfolio Metrics

See: [format-pipeline-metrics.csv](format-pipeline-metrics.csv) and [portfolio-pipeline-metrics.md](portfolio-pipeline-metrics.md)

**Portfolio grade: D+ (1.97/5.0)**
- Dimensions 6 and 7 (QName/Hierarchy): 0/5 across the entire portfolio
- Only FODS/FODT/ZST average ≥ 2.8/5.0

---

## 15. Process Grades

See portfolio-pipeline-metrics.md grading matrix.

**Bottom-line:** Every format fails QName Fidelity (0/5) and Hierarchy Fidelity (0/5). This is the single most impactful failure because it blocks code-generation and traceability.

---

## 16. Gap Register

See [forensic-gap-register.yaml](forensic-gap-register.yaml) — 18 forensic gaps identified.

**Top 5 by impact:**
1. **FG-QNAME-001** — QName registry 0 entries (affects all 20 formats, critical)
2. **FG-SAL-001** — Non-ODF facts 3-22 per format (affects 14 formats, critical)
3. **FG-CAP-001** — Capability inflation 27x (affects 13 formats, high)
4. **FG-DOTNET-001** — No .NET for 15 formats (affects all commercial targets, high)
5. **FG-PROD-005** — CSV/TSV incomplete (simple formats deserve roundtrip)

---

## 17. Root-Cause Register

See [root-cause-register.yaml](root-cause-register.yaml) — 9 root causes identified.

**Dominant root causes:**
- **RC-001:** SAL pipeline non-ODF gap (spec text not ingested)
- **RC-002:** QName registry never populated by any tool
- **RC-003:** Capability inflation from POC-goal templates
- **RC-004:** Analytics masquerade rotation (suspended but not cleaned)
- **RC-005:** 8 formats with shallow implementations

---

## 18. Fix-Option Analysis

For each root cause, one primary strategy is chosen:

| Root Cause | Option A | Option B | Chosen |
|------------|----------|----------|--------|
| RC-001 (spec extraction) | Build generic RFC/XML ingestion adapters | Continue manual bootstrap seeding | **Option A** (automated, scalable) |
| RC-002 (qname empty) | Build qname generator from SAL facts | Populate registry manually per format | **Option A for ODF, Option B for non-ODF** |
| RC-003 (cap inflation) | Audit and reclassify existing caps | Delete unsupported caps | **Audit/reclassify (preserve, don't delete)** |
| RC-004 (analytics) | Audit and mark deprecated in docstrings | Delete analytics functions | **Docstring marking (LOC cap prevents deletion anyway)** |
| RC-005 (shallow impls) | Write missing implementations | Accept current state as final | **Write missing implementations** |

---

## 19–20. Requirements and Taskcard Register

See [taskcard-register.yaml](taskcard-register.yaml) — 18 taskcards for 6 execution batches.

**Critical path taskcards:**
```
TC-FG-SAL-001-A (RFC ingestion)
    ↓
TC-FG-QNAME-001-ODF (ODF qname population) — parallel with SAL repair
    ↓
TC-FG-CAP-001 (capability audit)
    ↓
TC-FG-PROD-004 (NetPBM write — pilot)
TC-FG-PROD-005 (CSV/TSV roundtrip — pilot)
TC-FG-SAL-002 (TOML spec — pilot)
    ↓
TC-FG-PROD-001 (ODT write)
TC-FG-PROD-002 (FODP full model)
TC-FG-PROD-003 (XCF real layers)
```

---

## 21. Dependency Graph

```
BATCH-0 (baseline) ──► BATCH-1 (spec repair) ──► BATCH-3 (cap repair)
                    ──► BATCH-2 (qname repair)         ↓
                                                  BATCH-4 (pilots)
                                                        ↓
                                                  BATCH-5 (backfill)
                                                        ↓
                                                  BATCH-6 (packages)
```

See [execution-batch-register.yaml](execution-batch-register.yaml)

---

## 22. Execution Priorities

| Priority | Taskcards | Rationale |
|----------|-----------|-----------|
| P0 | TC-FG-SAL-001-A | Spec facts are the foundation of everything |
| P1 | TC-FG-QNAME-001-ODF, TC-FG-SAL-001-B, TC-FG-CAP-001 | QName break blocks traceability chain |
| P2 | TC-FG-PROD-001, TC-FG-PROD-005, TC-FG-TEST-001, TC-FG-QNAME-002 | Product completeness |
| P3 | TC-FG-PROD-003, TC-FG-PROD-004, TC-FG-GOV-001 | Non-critical improvements |
| P4 | TC-FG-DOTNET-001 | Blocked by Gate 11 anyway |

---

## 23. Pilot Strategy

Three pilots prove different failure classes:

**Pilot A: TOML** — Rich spec not yet processed
- Chain: TOML 1.0 spec → RFC ingestion → 60+ facts → capability audit → code unchanged → 80+ tests
- Proves: spec extraction adapter works for structured community specs

**Pilot B: PPM** — Simple format missing write path
- Chain: NetPBM spec (short) → existing 5 facts sufficient → write_ppm added → roundtrip test
- Proves: product backfill path for simple read-only formats

**Pilot C: CSV** — Gate 1-4 format needing roundtrip
- Chain: RFC 4180 facts → CSV roundtrip → gates 5-10 → local package build
- Proves: gates 5-10 pipeline works for a simple format

---

## 24. Backfill Strategy

After each pilot passes, apply the same pattern to related formats:
- TOML pilot → NDJSON (similar data family, similar depth)
- PPM pilot → PGM, PBM (same NetPBM family)
- CSV pilot → TSV, DIF, SYLK (cells family)

Preserve all existing working implementations. Backfill only the missing layers (write path, tests, gates).

---

## 25. Product Healing Strategy

For each probe-only or partial format:
1. Determine which spec facts exist
2. Determine what implementation depth they support
3. Implement missing layers in priority order: read > write > roundtrip > error handling
4. Write tests for each layer
5. Run gates to confirm

Do NOT claim production maturity for formats with sparse spec facts (≤ 9 verified). Mark them as `alpha-foss-preview` which is the current correct classification.

---

## 26. Evidence Contract

All taskcards in this plan must produce:
- Evidence artifact in `reports/forensic-audit-20260624/` or `.local/evidences/`
- Test results (pass/fail count)
- Before/after fact counts (for Batch 1 work)
- Before/after entry counts (for Batch 2 work)
- Code diff summary (for Batch 4/5 work)

---

## 27. Rollback and Recovery

All repairs are additive:
- Batch 1 (spec ingestion): only writes to `.local/spec-cache/` — no product code changes
- Batch 2 (qname): only writes to `shared/qname-registry/` — no product code changes
- Batch 3 (capability): only writes to `reports/forensic-audit-20260624/` — no product code changes
- Batches 4-5 (product): add new source files / test files — do NOT modify existing working code

Rollback: `git checkout` on any changed source file. Evidence artifacts are reports-only.

---

## 28. Anti-Overclaim Rules

1. Do NOT claim qname traceability until qname-registry has > 0 entries
2. Do NOT claim capability-to-spec linkage until per-capability fact IDs are written
3. Do NOT claim format production-ready until all 10 gates are passed
4. Do NOT claim SAL chain intact until spec-cache has chunked text for the format
5. Do NOT claim test coverage without counting actual test count
6. Do NOT claim packaging without a wheel build + install log

---

## 29. Closeout Criteria

This forensic audit mission closes when:

**Spec layer:**
- [ ] All 20 non-ODF/non-trivial formats have > 10 verified facts each
- [ ] TOML spec fully ingested (60+ facts)
- [ ] Gnumeric, ABW have 30+ facts each

**QName layer:**
- [ ] All 20 qname-registry files have > 5 entries each
- [ ] Parity matrix: 0 formats with '?' qname_compliance
- [ ] V-NEW-QNAME-REGISTRY validator registered and passing

**Capability layer:**
- [ ] All 1,641 foss_reduced capabilities have derivation_class field
- [ ] ODF capabilities have per-capability spec_fact_refs

**Product layer:**
- [ ] ODT has write + roundtrip
- [ ] FODP has full page model
- [ ] NetPBM (PPM/PGM/PBM) have write paths
- [ ] CSV + TSV have roundtrip
- [ ] TOML has 80+ tests
- [ ] XCF returns real layer names

**Evidence:**
- [ ] All 6 execution batches have exit gate evidence
- [ ] Portfolio grade re-measured post-repair
- [ ] No '?' fields in any pipeline inventory artifact

---

## 30. Autonomous Execution Handoff

**Recommended entry point for autonomous execution:**

```bash
# Start with Batch 0 (already complete — this plan IS Batch 0)
# Proceed to Batch 1 — most impactful

# Batch 1: Build RFC ingestion adapter (highest priority)
# Implementation target: tools/spec/sal_rfc_ingester.py
# Input: .local/spec-cache/zst/rfc8878/ + .local/spec-cache/csv/ + .local/spec-cache/toml/
# Output: .local/spec-cache/{format}/verified-facts-rfc.yaml

# Run parallel with Batch 2 ODF qname population:
# Implementation target: populate shared/qname-registry/fods.yaml (20+ entries)
# Source: .local/sal-output/sal-facts-latest.json FODS entries

# After Batch 1+2: run pilots (Batch 4)
# Pilot B (simplest): add write_ppm to src/python/ppm/ + tests
```

**Autonomous agent instruction:**
- Execute taskcards in priority order: P0 → P1 → P2 → P3
- Each taskcard has bounded scope and clear verification
- All work is additive (no deletions)
- Report metric changes after each taskcard

---

*Document ends. See companion files in reports/forensic-audit-20260624/ for full registers.*
