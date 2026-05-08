---
artifact_id: fodt-gate6-oracle-plan
artifact_type: acquisition-pack
path: acquisition-packs/fodt/gate6-oracle-plan.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 6 oracle comparison planning document. Created run046 (2026-05-08). Planning only — execution requires explicit Gate 6 prompt. LibreOffice already installed (run043 for FODS)."
---

# FODT Gate 6 — Oracle Comparison Plan

**Gate:** 6 — Oracle Comparison
**Format:** FODT (Flat OpenDocument Text)
**Run:** run046 planning (2026-05-08)
**Status:** planning_ready — execution blocked until explicit Gate 6 prompt

---

## Oracle Environment Status

**LibreOffice is already installed** (from FODS Gate 6, run043):
- Path: `C:\Program Files\LibreOffice\program\soffice.com` (console-mode)
- Version: 26.2.3.2 (winget install, 2026-05-08)
- Preflight: ORACLE_PREFLIGHT: PASS (run043+)

For FODT, the same LibreOffice installation is used. No additional tool installation required.

---

## Prerequisites (all met)

| Prerequisite | Status |
|---|---|
| FODT Gate 5 PASSED | PASS — Babar Raza, 2026-05-08, run046 |
| FODT neutral model defined | PASS — schemas/neutral-model/fodt/ |
| LibreOffice installed | PASS — run043, soffice.com at standard path |
| FODS oracle harness available | PASS — tools/oracle/ (already built) |
| 4 FODT samples available | PASS — samples/by-format/fodt/ |

---

## Oracle Comparison Approach

For FODT, the oracle comparison uses LibreOffice headless to convert `.fodt` files to text:
```
soffice --headless --convert-to txt:Text --outdir <outdir> <fodt_file>
```

The oracle comparison verifies that:
1. LibreOffice can open all 4 FODT samples without error
2. The text content extracted by the oracle matches the text extracted by fodt_parser.py
3. Word count is approximately consistent between oracle and parser

**Key difference from FODS:** FODS used CSV export (spreadsheet → CSV).
FODT uses text export (document → plain text).

---

## Execution Authorization

Gate 6 execution is blocked until:
1. Human issues explicit "FODT Gate 6 oracle execution" prompt
2. Oracle preflight confirms LibreOffice still available (validate_oracle_environment.py)
3. New oracle scripts created for FODT format (run_fodt_oracle.py, compare_fodt_oracle.py)
4. TC-0042 executed; TC-0043 DEC-034 verification run

---

## References

- `acquisition-packs/fodt/oracle-scope.md` — Scope and limitations
- `acquisition-packs/fodt/oracle-risk-register.md` — Risks and mitigations
- `tools/oracle/` — FODS oracle harness (reference implementation)
- `taskcards/TC-0041-fodt-gate6-oracle-planning.md` — Planning taskcard
- `taskcards/TC-0042-fodt-gate6-oracle-execution.md` — Execution taskcard
- `taskcards/TC-0043-fodt-gate6-oracle-verification.md` — Verification taskcard
