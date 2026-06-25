# src/ Architecture Gap Inventory
**Originally Generated:** 2026-06-17 — SRC Governance Healing (eventual-painting-torvalds)
**Last Updated:** 2026-06-25 — Governance & Machinery Healing (warm-jingling-sutherland)

---

## Update: 2026-06-25 (Post-Analytics-Separation State)

The 2026-06-17 inventory captured violations BEFORE the analytics separation sprints
(keen-dancing-hopper, FODT forensic healing, product deepening missions). Significant healing
occurred 2026-06-17 to 2026-06-25. LOC counts below verified at HEAD during TC-GH-PRE-001.

### Current State at HEAD (2026-06-25)

| File | 2026-06-17 LOC | HEAD LOC | Classification | Notes |
|------|----------------|----------|----------------|-------|
| src/python/zst/zst_codec.py | 3,873 | 899 | CLEAN (<800+delta) | Analytics extracted to zst_analytics.py; cap frozen at prior high |
| src/python/xcf/xcf_parser.py | 3,610 | 288 | CLEAN | Analytics extracted; major healing complete |
| src/python/fods/neutral_model.py | 4,127 | 717 | CLEAN | Partially healed; now below 800 LOC |
| src/python/fods/spreadsheet_document.py | N/A (not tracked) | 1,035 | MONOLITHIC | Remains; needs TC-ARCH-FODS-002 |
| src/python/abw/word_document.py | N/A (not tracked) | 1,026 | MONOLITHIC | Remains; needs TC-ARCH-ABW-001 |
| src/python/dif/interchange_document.py | N/A (not tracked) | 994 | LARGE | Needs TC-ARCH-DIF-001 |
| src/python/fodt/text_document.py | N/A (not tracked) | 990 | LARGE | Needs TC-ARCH-FODT-001 |
| src/python/csv/tabular_document.py | N/A (not tracked) | 960 | TARGET | Healing via TC-GH-008 (this sprint) |
| src/net/netpbm/Model/NetpbmImage.cs | 1,914 | 580 | CLEAN | Healed in prior sprint |
| src/net/fods/FodsDocument.cs | 1,386 | 769 | APPROACHING | Below 800; monitor |
| src/net/fodt/FodtDocument.cs | 977 | 754 | APPROACHING | Below 800; monitor |

**Classification thresholds:** CLEAN (<800 LOC or at baseline cap), APPROACHING (700-800 LOC),
LARGE (800-1000 LOC), MONOLITHIC (>1000 LOC).

### Healing Progress Summary

- Python files healed since 2026-06-17: 3 major (ZST -2,974 LOC, XCF -3,322 LOC, FODS neutral_model -3,410 LOC), several others
- .NET files healed since 2026-06-17: NetpbmImage.cs -1,334 LOC
- Remaining monolithic Python files requiring TC-ARCH-* taskcards: 5 (see Section 57 of master-plan.md)
- Current sprint TC-GH-008 targets: csv/tabular_document.py (960 LOC → target <800)
- Governance machinery upgraded this sprint: V73 (import direction) + V74 (error handling hierarchy)

### What Changed Since 2026-06-17

1. **Analytics separation completed for:** ZST → zst_analytics.py, XCF → xcf_analytics.py, FODG → fodg_analytics.py
2. **FODT neutral_model.py healed:** Was 1,916 LOC (GOV_BLOCK), now 279 LOC after forensic healing sprint
3. **FODS neutral_model.py healed:** Was 4,127 LOC, now 717 LOC
4. **FODS/FODT document classes** remain: these contain domain operations NOT analytics, so analytics-extraction didn't trigger on them
5. **Source structure baseline** now uses `baseline_loc_cap` (write-once) as primary enforcement — files at or below their cap PASS
6. **V69-V72 added** since 2026-06-17: skill idempotency, SAL authority chain, lane DAG ordering, artifact identity
7. **.pre-commit-config.yaml** still missing — addressed by TC-GH-005 (this sprint)

---

Policy limits: max 800 LOC per file, max 60 functions per file.

---

## Summary

| Category | Count | Total excess LOC |
|---|---|---|
| Python mixed_model_analytics | 20 | ~52,000 above 800-LOC limit |
| .NET oversized | 3 | ~3,600 above 800-LOC limit |
| Supervisor/tools | 2 | ~940 above 800-LOC limit |
| **Total** | **25** | **~56,500** |

---

## Full Violation Table

| # | Relative path | LOC | Functions | Category | Note |
|---|---|---|---|---|---|
| 1 | src/net/fods/FodsDocument.cs | 1,386 | 0 | oversized | .NET model class |
| 2 | src/net/fodt/FodtDocument.cs | 977 | 0 | oversized | .NET model class |
| 3 | src/net/netpbm/Model/NetpbmImage.cs | 1,914 | 0 | oversized | .NET image model |
| 4 | src/python/abw/abw_codec.py | 3,215 | 371 | mixed_model_analytics | ABW parse + edit + export + analytics |
| 5 | src/python/csv/csv_parser.py | 3,026 | 350 | mixed_model_analytics | CSV parse + 300+ analytics |
| 6 | src/python/dif/dif_parser.py | 3,382 | 361 | mixed_model_analytics | DIF parse + analytics |
| 7 | src/python/fodg/fodg_codec.py | 3,920 | 573 | mixed_model_analytics | FODG codec + analytics (GREW: was 3,476) |
| 8 | src/python/fodp/fodp_codec.py | 2,365 | 327 | mixed_model_analytics | FODP codec + analytics |
| 9 | src/python/fods/neutral_model.py | 4,127 | 358 | mixed_model_analytics | FODS model + validation + analytics |
| 10 | src/python/fodt/neutral_model.py | 4,097 | 358 | mixed_model_analytics | FODT model + validation + analytics |
| 11 | src/python/gnumeric/gnumeric_codec.py | 3,706 | 382 | mixed_model_analytics | Gnumeric codec + analytics |
| 12 | src/python/ndjson/ndjson_codec.py | 3,396 | 349 | mixed_model_analytics | NDJSON codec + analytics |
| 13 | src/python/ods/ods_parser.py | 3,584 | 369 | mixed_model_analytics | ODS parse + analytics |
| 14 | src/python/odt/odt_parser.py | 2,179 | 314 | mixed_model_analytics | ODT parse + analytics |
| 15 | src/python/pbm/pbm_parser.py | 2,902 | 347 | mixed_model_analytics | PBM parse + analytics |
| 16 | src/python/pgm/pgm_parser.py | 2,831 | 344 | mixed_model_analytics | PGM parse + analytics |
| 17 | src/python/ppm/ppm_parser.py | 2,802 | 347 | mixed_model_analytics | PPM parse + analytics |
| 18 | src/python/qoi/qoi_parser.py | 2,610 | 345 | mixed_model_analytics | QOI parse + analytics |
| 19 | src/python/sylk/sylk_parser.py | 3,276 | 367 | mixed_model_analytics | SYLK parse + analytics |
| 20 | src/python/toml/toml_codec.py | 2,641 | 370 | mixed_model_analytics | TOML codec + analytics |
| 21 | src/python/tsv/tsv_parser.py | 3,351 | 367 | mixed_model_analytics | TSV parse + analytics |
| 22 | src/python/xcf/xcf_parser.py | 3,610 | 531 | mixed_model_analytics | XCF binary parse + analytics (GREW: was 3,101) |
| 23 | src/python/zst/zst_codec.py | 3,873 | 516 | mixed_model_analytics | ZST compress + analytics (GREW: was 3,472) |
| 24 | tools/supervisor/generate_next_worker_prompt.py | 1,318 | 22 | supervisor_tool | Grandfathered 2026-06-17 |
| 25 | tools/capability_layer/capability_map_generator.py | 1,204 | 23 | supervisor_tool | Grandfathered 2026-06-17 |

---

## Baseline Growth Events

These violations grew AFTER being initially grandfathered. Growth proves the bypass mechanism:

| File | Initial LOC | Current LOC | Growth | Date of growth | Mechanism |
|---|---|---|---|---|---|
| src/python/fodg/fodg_codec.py | 3,476 | 3,920 | +444 | 2026-06-17 | Product deepening sprints adding analytics functions; CLAUDE.md Step 0 updated baseline |
| src/python/xcf/xcf_parser.py | 3,101 | 3,610 | +509 | 2026-06-17 | Same as above |
| src/python/zst/zst_codec.py | 3,472 | 3,873 | +401 | 2026-06-17 | Same as above |
| **Total growth** | | | **+1,354 LOC** | | Governance bypass via CLAUDE.md Step 0 |

---

## Root Cause Per Category

### Python mixed_model_analytics (20 files)
- **Root cause:** Product deepening sprints add 50–100 analytics functions per sprint to the primary codec/parser file. No enforcement prevents this because CLAUDE.md Step 0 updates the baseline before validators run.
- **Bypass mechanism:** Step 0 one-liner overwrites `loc` and `functions` in baseline JSON → validator sees `current_loc == baseline_loc` → no worsening detected → sprint proceeds.
- **Not a validator bug:** The validator logic is correct. The bypass is upstream.

### .NET oversized (3 files)
- **Root cause:** No architecture decomposition has occurred for .NET yet. FodsDocument.cs, FodtDocument.cs, NetpbmImage.cs grew during initial implementation without enforcement.
- **Bypass mechanism:** Step 0 script skips `.cs` files (checks `.endswith('.py')`). However, .NET violations don't grow because no product deepening sprint touches .NET. Current LOC = frozen at baseline values.

### Supervisor tools (2 files)
- **Root cause:** generate_next_worker_prompt.py and capability_map_generator.py grew during supervisor infrastructure work. Grandfathered explicitly on 2026-06-17.
- **Growth risk:** LOW — these files are not targeted by product deepening sprints.

---

## Architecture Anti-Pattern: Mixed Responsibilities

All 20 Python violations share the same structural failure — a single file contains all of:

| Layer | Examples | Should be in |
|---|---|---|
| Parsing | XML/binary reading, delimiter detection | `{format}_parser.py` |
| Domain model | Document/sheet/cell/image structures | `{format}_model.py` |
| Validation | Schema compliance, constraint checks | `{format}_validator.py` or `neutral_model.py` |
| Export/write | Serialize to XML/JSON/CSV/bytes | `{format}_writer.py` |
| Analytics | 200–500 pure functions for statistics | `{format}_analytics.py` or `analytics/` |

No module in src/python/ has achieved proper layer separation. The FODS/FODT modules are closest (separate parser.py, writer.py, neutral_model.py) but neutral_model.py itself contains 4,000+ lines of mixed model + analytics.

---

## Remediation Status

| Category | Machinery fix required | Product fix required | Gated on |
|---|---|---|---|
| Step 0 bypass mechanism | TC-MACH-006 (READY) | N/A | Nothing |
| No write-once cap | TC-MACH-001 | N/A | TC-BEST-001 |
| Validator uses mutable `loc` | TC-MACH-002 | N/A | TC-MACH-001 |
| No pre-commit architecture check | TC-MACH-004 | N/A | TC-MACH-007 |
| No existing regression test for cap | TC-MACH-005 | N/A | TC-MACH-001 |
| Python files > 800 LOC (20 files) | N/A | TC-PRODUCT-PLAN-001 | TC-PROVE-001 |
| .NET files > 800 LOC (3 files) | N/A | TC-PRODUCT-PLAN-001 | TC-PROVE-001 |
