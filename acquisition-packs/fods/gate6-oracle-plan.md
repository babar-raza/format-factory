---
artifact_id: fods-gate6-oracle-plan
artifact_type: gate-planning
path: acquisition-packs/fods/gate6-oracle-plan.md
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
notes: "Gate 6 oracle comparison planning document for FODS. Created run034 (2026-05-06). Planning only — NO execution until Gate 5 approved."
---

# FODS Gate 6 — Oracle Comparison Plan

**Format:** FODS (Flat OpenDocument Spreadsheet)
**Gate:** 6 — Oracle Comparison Complete
**Status:** planning_only (Gate 5 not yet approved)
**Created:** run034 (2026-05-06)

---

## 1. Gate 6 Pass Criteria (from docs/gates.md)

1. An oracle tool has been selected and its version recorded.
2. All samples in the corpus have been loaded with the oracle tool and with the prototype parser.
3. An oracle comparison report exists at `acquisition-packs/fods/gate6-oracle-comparison-report.md` documenting all discrepancies.
4. Every discrepancy has been classified: prototype bug (fixed), spec ambiguity (documented), or oracle deviation from spec (documented).
5. No unresolved data-loss discrepancies remain. Minor presentation differences are acceptable.
6. Human review of the comparison report recorded.

---

## 2. Oracle Tool Selection

### 2a. Primary candidate: LibreOffice (headless mode)

| Property | Value |
|---|---|
| Tool | LibreOffice |
| Mode | Headless (`soffice --headless`) |
| Purpose | Load FODS files and export to structured format (CSV, JSON via macro, or XML) |
| Availability | Free, open-source, widely available |
| FODS support | Native (FODS is a first-class ODF format in LibreOffice) |
| Platform | Windows 11 Pro (dev machine) |
| Version requirement | Latest stable (verify on dev machine before execution) |

### 2b. Why LibreOffice

- LibreOffice is the reference implementation for ODF formats
- It supports FODS natively (flat XML variant of ODS)
- Headless mode allows automated batch processing
- It can export to CSV for cell-by-cell comparison
- It evaluates formulas (unlike our prototype which stores raw formulas)

### 2c. Alternative candidates (if LibreOffice unavailable)

| Tool | Notes |
|---|---|
| Apache OpenOffice | Also supports ODF; legacy, less maintained |
| Python odfpy | Python library for ODF; limited formula support |
| Calligra Sheets | KDE spreadsheet; ODF support |

Decision: LibreOffice headless is the primary choice. Alternatives only if LibreOffice cannot be installed.

---

## 3. Comparison Methodology

### 3a. Sample corpus

All 4 Gate 3 samples will be compared:

| Sample | Key features to compare |
|---|---|
| minimal-spreadsheet.fods | Single cell, string value |
| multi-sheet-basic.fods | 2 sheets, string values, sheet names |
| typed-values-basic.fods | Float, string, boolean value types |
| formula-basic.fods | SUM formula, cached value vs evaluated value |

### 3b. Comparison process

For each sample:

1. **Parser output**: Run `fods_parser.py` to get JSON output (already validated in Gate 4/5)
2. **Oracle output**: Load sample in LibreOffice headless, export to CSV (one CSV per sheet)
3. **Normalize both outputs**: Convert to a common comparison format:
   - Sheet name
   - Row index, column index
   - Cell text value (as string)
   - Cell value type
4. **Diff**: Compare cell-by-cell. Record every discrepancy.
5. **Classify**: Each discrepancy gets one classification:
   - `prototype_bug` — parser produces wrong output (must be fixed)
   - `spec_ambiguity` — spec is unclear; document interpretation
   - `oracle_deviation` — oracle deviates from spec (document)
   - `presentation_only` — formatting difference, no data loss
   - `formula_evaluation` — expected difference (prototype doesn't evaluate formulas)

### 3c. Expected known discrepancies

| Category | Expected? | Notes |
|---|---|---|
| Formula evaluation | YES | Prototype stores raw formulas; oracle evaluates them. This is expected and documented (Formula.evaluated=false in model). |
| Value precision | POSSIBLE | Float representation may differ between parser (Python float) and oracle (LibreOffice internal). |
| Empty cell handling | POSSIBLE | Parser may output empty cells differently than oracle CSV export. |
| Sheet ordering | UNLIKELY | Both should preserve sheet order from XML. |

### 3d. Comparison tool

A comparison script will be created at `tools/oracle/compare_fods_oracle.py`:
- Input: parser JSON + oracle CSV (per sheet)
- Output: discrepancy report (YAML or Markdown)
- Exit code: 0 if no unresolved data-loss discrepancies

---

## 4. Deliverables

| Deliverable | Path | Description |
|---|---|---|
| Oracle comparison report | `acquisition-packs/fods/gate6-oracle-comparison-report.md` | Sanitized report with discrepancy table (committed) |
| Oracle reference outputs | `.local/oracle/fods/` | CSV exports (local-only, never committed) |
| Comparison tool | `tools/oracle/compare_fods_oracle.py` | Automated comparison script |
| TC-0025 update | `taskcards/TC-0025-*.md` | Status update after planning |
| TC-0026 | `taskcards/TC-0026-*.md` | Gate 6 execution taskcard |

Note (run036): Canonical paths reconciled. `reports/fods-oracle.md` and `.local/oracle-outputs/fods/` were stale references — replaced with canonical paths above.

---

## 5. Prerequisites

- [ ] Gate 5 approved by human
- [ ] LibreOffice installed on dev machine (verify version)
- [ ] Explicit Gate 6 execution prompt issued by human
- [ ] TC-0025 planning reviewed

---

## 6. Timeline Estimate

Gate 6 planning is complete upon creation of this document. Gate 6 execution requires:
1. Gate 5 human approval
2. LibreOffice installation verification
3. Explicit Gate 6 execution prompt

---

## 7. Constraints

- NO Gate 6 execution until Gate 5 is approved
- NO product source code (`src/python/fods/`, `src/net/fods/`)
- NO security testing (Gate 7)
- NO release manifests
- Oracle outputs (CSV exports) are local-only artifacts
- Formula evaluation differences are expected and not data-loss discrepancies
