---
artifact_id: fods-oracle-scope
artifact_type: gate-planning
path: acquisition-packs/fods/oracle-scope.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-06"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 6 oracle comparison scope document for FODS. Created run034 (2026-05-06). Planning only."
---

# FODS Gate 6 — Oracle Scope

**Format:** FODS
**Gate:** 6 — Oracle Comparison
**Status:** planning_only
**Created:** run034 (2026-05-06)

---

## In Scope

1. **Oracle tool selection and configuration** — LibreOffice headless with FODS file loading
2. **Oracle reference output generation** — CSV export per sheet for all 4 Gate 3 samples
3. **Cell-by-cell comparison** — Parser JSON output vs oracle CSV, normalized to common format
4. **Discrepancy classification** — Every difference classified (prototype_bug, spec_ambiguity, oracle_deviation, presentation_only, formula_evaluation)
5. **Comparison tool** — Python script at `tools/oracle/compare_fods_oracle.py`
6. **Oracle comparison report** — `acquisition-packs/fods/gate6-oracle-comparison-report.md` with sanitized discrepancy table (committed); raw outputs under `.local/oracle/fods/` (local-only)
7. **Prototype bug fixes** — If discrepancies reveal prototype bugs, fix them

---

## Out of Scope — FORBIDDEN

| Item | Reason | Gate |
|---|---|---|
| Product source code | Gate 10+ | `src/python/fods/`, `src/net/fods/` |
| Gate 6 self-approval | Human-only | — |
| Fuzz testing | Gate 7 | — |
| Security report | Gate 8 | — |
| CI workflows | Gate 10+ | — |
| Formula evaluation implementation | Out of scope for parser v1 | — |
| Neutral model changes | Requires separate TC if oracle reveals model gaps | — |
| New sample creation | Gate 3 corpus is frozen | — |

---

## Comparison Features

### What gets compared

| Feature | Parser output field | Oracle output | Comparable? |
|---|---|---|---|
| Sheet name | `sheets[*].name` | CSV filename or first-row header | YES |
| Sheet count | `sheet_count` | Number of CSV files | YES |
| Cell text | `cells[*].text` | CSV cell value | YES |
| Cell value (float) | `cells[*].value` (float) | CSV cell value | YES (modulo precision) |
| Cell value (string) | `cells[*].value` (string) | CSV cell value | YES |
| Cell value (boolean) | `cells[*].value` (bool) | CSV "TRUE"/"FALSE" | YES (with normalization) |
| Formula raw | `cells[*].formula` | Not in CSV export | NO — parser-only field |
| Formula cached value | `cells[*].formula.cached_value` | CSV shows evaluated result | COMPARE cached vs evaluated |

### What is NOT compared (documented exclusions)

| Feature | Reason |
|---|---|
| Cell styling | Out of scope for neutral model v1 |
| Column widths | Out of scope |
| Font information | Out of scope |
| Conditional formatting | Out of scope |
| Empty trailing cells | Parser may or may not emit trailing empty cells |
| Row/column repeats | Parser expands repeats; oracle CSV also expands |

---

## Success Criteria

Gate 6 PASSES when:
1. All 4 samples compared
2. No unresolved data-loss discrepancies remain
3. All discrepancies classified
4. Formula evaluation differences documented as expected
5. Oracle comparison report exists at `acquisition-packs/fods/gate6-oracle-comparison-report.md`
6. Human has reviewed and approved the comparison report
