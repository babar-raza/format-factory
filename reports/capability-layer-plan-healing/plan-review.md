# Plan Review — Capability & Feature Understanding Layer Sprint
# Generated: 2026-06-08
# Sprint ID: FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001
# Run ID: capability-feature-understanding-layer-healing-20260608-e382e5f

## Review Method
Each claim from the starting plan was verified against actual repo files.

---

## A. Path Existence Verification

| Path Claimed | Exists? | Verdict |
|---|---|---|
| `tools/capability_layer/` | NO | **CREATED THIS SPRINT** |
| `schemas/capability/` | NO | **CREATED THIS SPRINT** |
| `reports/capability-layer/` | NO | **CREATED THIS SPRINT** |
| `product-capability-matrix/poc-targets.yaml` | YES | Confirmed |
| `tools/requirements_authority/` | YES | Confirmed (15 Python files) |
| `tools/specification-authority-layer/` | YES | Confirmed (13 Python files) |
| `tools/supervisor/product_task_selector.py` | YES | Confirmed |
| `reports/r90/product-code-change-ledger.json` | YES | Confirmed (130 entries) |
| `src/python/fodg/fodg_codec.py` | YES | Confirmed |
| `src/python/gnumeric/gnumeric_codec.py` | YES | Confirmed |
| `schemas/format-understanding/` | YES | EXISTING — 6 FUL schemas (not in plan!) |
| `acquisition-packs/` | YES | EXISTING — per-format FUL packs |
| `taskcards/` | YES | EXISTING — 150+ taskcards |

---

## B. Product Implementation State (verified against source)

| Format | Plan Claimed | Actual Source State | Verdict |
|---|---|---|---|
| FODG | "probe/load only (6 fns)" | probe/load/extract_text/get_page_metadata/get_page_count/get_shape_count — CORRECT | CONFIRMED |
| Gnumeric | "`set_cell_value` missing" | **SET_CELL_VALUE ALREADY IMPLEMENTED** (lines 223-257 gnumeric_codec.py) | **PLAN STALE** |
| Gnumeric test | "test_r126 needs creation" | `test_r126_gnumeric_set_cell.py` **ALREADY EXISTS** | **PLAN STALE** |
| ABW | "13 functions, export_to_csv PASS (R123)" | Confirmed — export_to_csv present | CONFIRMED |
| TSV | "write_tsv PASS (R122), load_tsv PASS (R125)" | Confirmed in poc-targets... but TSV NOT IN poc-targets.yaml FOSS! | POC-TARGETS STALE |
| NDJSON | "7 functions complete" | Confirmed ndjson_codec.py | CONFIRMED, but NOT in poc-targets.yaml |

---

## C. poc-targets.yaml Staleness (last_updated: R114/2026-06-04)

**Missing from FOSS list (3 formats completely absent):**
- FODG — not in foss_reduced_products (probe_fodg added R122)
- TSV — not in foss_reduced_products
- NDJSON — not in foss_reduced_products

**Missing capabilities for existing FOSS formats:**
- ABW: `export_to_csv` missing from python_status (added R123)
- Gnumeric: `get_cell_value` missing (added R123), `get_sheet_names` missing (added R125), `set_cell_value` missing (added R125/R126)

**Summary of poc-targets.yaml staleness:** 3 formats missing, 4+ capabilities missing per format.
This CONFIRMS the need for healing.

---

## D. Stale Plan Assumptions (requiring correction)

| Assumption | Actual | Fix |
|---|---|---|
| "Auto-detect run ID — not R126" | Pattern: `<name>-YYYYMMDD-<hash>` | Run ID = `capability-feature-understanding-layer-healing-20260608-e382e5f` |
| "Gnumeric set_cell_value missing" | ALREADY IMPLEMENTED | Remove implementation work; only verify tests pass |
| "test_r126_gnumeric_set_cell.py needs creation" | FILE EXISTS | Only need to run tests |
| "FUL layer doesn't exist" | `schemas/format-understanding/` + `acquisition-packs/` + FUL-001/002 COMPLETED | Integrate with existing FUL, not replace it |
| "No taskcards exist" | 150+ taskcards in `taskcards/` | Prefix new taskcards with CAP- to avoid conflicts |
| "21 pre-existing supervisor failures" | MUST RE-DETECT | Run supervisor tests fresh |

---

## E. Format Understanding Layer — Existing Components

The plan did not acknowledge the existing FUL:
- `schemas/format-understanding/` — 6 schemas (FUL-001 COMPLETED 2026-05-08)
  - format-profile.schema.yaml
  - verified-facts.schema.yaml
  - implementation-requirements.schema.yaml
  - parser-strategy.schema.yaml
  - security-surface.schema.yaml
  - product-readiness.schema.yaml
- `acquisition-packs/` — per-format packs for: abw, csv, dif, fodg, fodp, fods, fodt, gnumeric, ods, odt, ora, pam, pbm, pgm, ppm, qoi, sylk, tsv, xcf, xpm, zpaq, zst
- `taskcards/FUL-001` — COMPLETED
- `taskcards/FUL-002` — COMPLETED (FODS FUL package)
- `taskcards/FUL-003`, `FUL-004` — check status

**Capability layer work must EXTEND the existing FUL, not create a competing system.**
The new capability layer adds: machine-readable capability maps, gap ledger, action queue, and product selector integration.

---

## F. Autonomous Continuation State

- `AUTONOMOUS_CONTINUE: YES`
- `next-action.json`: post-closeout CHECK for approval-gates.md (trivial, can be cleared)
- No unsafe continuation signals
- Safe to proceed

---

## G. Run ID Selection

Run ID selected: `capability-feature-understanding-layer-healing-20260608-e382e5f`
- Pattern: `<sprint-slug>-YYYYMMDD-<HEAD-short>`
- HEAD: `e382e5f`
- Evidence path: `.local/evidences/capability-feature-understanding-layer-healing-20260608-e382e5f/`
- Review package: `.local/supervisor/reviews/capability-feature-understanding-layer-healing-20260608-e382e5f/declaration-review-package.zip`

---

## H. Plan Review Verdict

| Category | Status |
|---|---|
| AUTONOMOUS_CONTINUE | YES — safe to proceed |
| Run ID | SELECTED: `capability-feature-understanding-layer-healing-20260608-e382e5f` |
| Stale assumptions corrected | YES — 6 corrections made |
| Paths verified | YES — all critical paths checked |
| FUL integration strategy | EXTEND existing FUL, don't replace |
| Phase E scope | FODG write/export (FODG only); Gnumeric verify tests only |
| Plan healing needed | YES — see normalized-plan.md |
