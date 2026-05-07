---
artifact_id: fods-gate6-oracle-blocker-report
artifact_type: gate-blocker-report
path: acquisition-packs/fods/gate6-oracle-blocker-report.md
format_id: fods
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-05-07"
notes: "Gate 6 oracle blocker report for FODS. Created run035 (2026-05-07). Hardened run036 (oracle_common.py, env var support, improved diagnostics, installation checklist)."
---

# FODS Gate 6 Oracle Blocker Report

**Format:** FODS
**Gate:** 6 — Oracle Comparison
**Status:** oracle_blocked_missing_tool
**Prepared by:** run035 (2026-05-07); updated run036 (2026-05-07)
**Gate 6 approved:** NO — blocked, cannot proceed to approval

---

## Blocker: LibreOffice Not Installed

Gate 6 oracle preflight has been executed twice — during run035 (initial) and run036 (re-run with hardened harness). Both runs produced `ORACLE_PREFLIGHT: FAIL`. The oracle tool (LibreOffice headless) was not found on the development machine.

---

## run036 Preflight Re-Run

The oracle harness was substantially hardened in run036 (see "Improvements Completed" section below). The re-run preflight produced the same FAIL result but with improved diagnostics:

```
============================================================
FODS Oracle Preflight Check
============================================================
Platform: Windows 10.0.26200
Python: 3.13.x

  Discovery: checking 10 candidates...
  MISS  [standard-path]: soffice (not found)
  MISS  [standard-path]: libreoffice (not found)
  MISS  [standard-path]: C:\Program Files\LibreOffice\program\soffice.exe (not found)
  MISS  [standard-path]: C:\Program Files (x86)\LibreOffice\program\soffice.exe (not found)
  MISS  [standard-path]: /usr/bin/soffice (not found)
  MISS  [standard-path]: /usr/bin/libreoffice (not found)
  MISS  [standard-path]: /usr/lib/libreoffice/program/soffice (not found)
  MISS  [standard-path]: /Applications/LibreOffice.app/Contents/MacOS/soffice (not found)

Oracle binary: NOT FOUND
  Checked env var: FORMAT_FACTORY_SOFFICE
  Checked 8 standard paths

FODS samples: 4 files found

ORACLE_PREFLIGHT: FAIL
Reasons:
  LibreOffice (soffice) not found
    To fix: install LibreOffice or set FORMAT_FACTORY_SOFFICE=<path>
```

### Preflight Result Table

| Check | run035 | run036 |
|---|---|---|
| `soffice --version` (PATH) | NOT FOUND | NOT FOUND |
| `libreoffice --version` (PATH) | NOT FOUND | NOT FOUND |
| `C:\Program Files\LibreOffice\program\soffice.exe` | NOT FOUND | NOT FOUND |
| `C:\Program Files (x86)\LibreOffice\program\soffice.exe` | NOT FOUND | NOT FOUND |
| `/usr/bin/soffice` | N/A | NOT FOUND |
| `/usr/bin/libreoffice` | N/A | NOT FOUND |
| `/usr/lib/libreoffice/program/soffice` | N/A | NOT FOUND |
| `/Applications/LibreOffice.app/Contents/MacOS/soffice` | N/A | NOT FOUND |
| `FORMAT_FACTORY_SOFFICE` env var | Not checked | NOT SET |
| FODS samples (4 required) | 4 found | 4 found |
| Oracle result | FAIL | FAIL |

---

## Resolution

To unblock Gate 6:

1. Install LibreOffice — see [oracle-installation-checklist.md](oracle-installation-checklist.md) for step-by-step instructions
2. **Windows:** `C:\Program Files\LibreOffice\program\soffice.exe` (standard install path — auto-discovered)
3. **Optional override:** set `FORMAT_FACTORY_SOFFICE=C:\Program Files\LibreOffice\program\soffice.exe`
4. Re-run preflight: `python tools/oracle/preflight_oracle.py --verbose`
5. When preflight passes (`ORACLE_PREFLIGHT: PASS`), issue an explicit TC-0026 execution prompt naming Oracle version

**Alternative (non-standard install path):**
```
python tools/oracle/preflight_oracle.py --soffice-path "D:\LibreOffice\program\soffice.exe"
```

---

## Improvements Completed (run036)

Despite the oracle tool still being unavailable, the following harness improvements were made in run036:

| Deliverable | Status | Notes |
|---|---|---|
| `tools/oracle/oracle_common.py` | **NEW** | Shared constants, path model, LibreOffice discovery |
| `tools/oracle/preflight_oracle.py` | **HARDENED** | Uses oracle_common; --soffice-path CLI arg; --verbose flag; FORMAT_FACTORY_SOFFICE env var |
| `tools/oracle/run_fods_oracle.py` | **HARDENED** | Uses oracle_common; --soffice-path CLI arg |
| `tools/oracle/compare_fods_oracle.py` | **HARDENED** | Uses oracle_common; removed duplicate constants |
| `tools/oracle/summarize_oracle_results.py` | **HARDENED** | Uses oracle_common canonical path constants |
| `tools/oracle/README.md` | **UPDATED** | Discovery priority, canonical path model, status |
| `acquisition-packs/fods/oracle-installation-checklist.md` | **NEW** | Step-by-step operator install guide |
| `taskcards/TC-0026-fods-gate6-oracle-execution.md` | **UPDATED** | Canonical path model section added |
| `taskcards/TC-0027-fods-gate6-oracle-verification.md` | **UPDATED** | Stale path references fixed |
| `acquisition-packs/fods/gate6-oracle-plan.md` | **UPDATED** | Stale path references fixed |
| `acquisition-packs/fods/oracle-scope.md` | **UPDATED** | Stale path references fixed |

---

## What Was Completed (run035 + run036)

| Deliverable | Status |
|---|---|
| `tools/oracle/` (5 scripts + README + oracle_common) | Complete |
| `acquisition-packs/fods/gate6-oracle-plan.md` | Complete |
| `acquisition-packs/fods/oracle-scope.md` | Complete |
| `acquisition-packs/fods/oracle-risk-register.md` | Complete |
| `acquisition-packs/fods/oracle-installation-checklist.md` | Complete (run036) |
| Gate 5 PASSED (Babar Raza, 2026-05-06) | Recorded |
| TC-0024 CLOSED | Complete |
| TC-0025 COMPLETED | Planning reviewed |
| TC-0026 BLOCKED | blocked_missing_oracle_tool |
| TC-0027 | not_started (waiting for TC-0026) |

---

## Canonical Path Model

| Path | Location | Committed? |
|---|---|---|
| Raw oracle exports | `.local/oracle/fods/raw-exports/` | NO — local-only |
| Per-sample results | `.local/oracle/fods/per-sample-results/` | NO — local-only |
| Oracle manifest | `.local/oracle/fods/oracle-manifest.yaml` | NO — local-only |
| Preflight result | `.local/oracle/fods/oracle-preflight.yaml` | NO — local-only |
| Comparison summary | `.local/oracle/fods/comparison-summary.json` | NO — local-only |
| Oracle comparison report | `acquisition-packs/fods/gate6-oracle-comparison-report.md` | YES — sanitized only |
| Blocker report (if blocked) | `acquisition-packs/fods/gate6-oracle-blocker-report.md` | YES (this file) |

---

## TC Status After run036

| Taskcard | Status |
|---|---|
| TC-0025 (Gate 6 planning) | completed |
| TC-0026 (Gate 6 execution) | blocked_missing_oracle_tool |
| TC-0027 (Gate 6 verification) | not_started |

---

## Gate 6 Next Action

**next_allowed_action:** install_oracle_tool_then_execute_tc0026

1. Install LibreOffice locally (see [oracle-installation-checklist.md](oracle-installation-checklist.md))
2. Run `python tools/oracle/preflight_oracle.py --verbose` to confirm
3. Issue explicit TC-0026 execution prompt naming Oracle path and version

Gate 6 is NOT approved. No oracle comparison data exists.
