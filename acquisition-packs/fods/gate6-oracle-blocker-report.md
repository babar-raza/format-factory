---
artifact_id: fods-gate6-oracle-blocker-report
artifact_type: gate-blocker-report
path: acquisition-packs/fods/gate6-oracle-blocker-report.md
format_id: fods
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-05-07"
notes: "Gate 6 oracle blocker report for FODS. Created run035 (2026-05-07). Hardened run036 (oracle_common.py, env var support, improved diagnostics, installation checklist). Updated run037 (oracle provider strategy, provider registry, validate_oracle_environment.py, provider options doc, preflight re-run 3). Updated run038 (harness self-test HARNESS_SELF_TEST_ONLY PASS 4/4, operator handoff, TC-0026 blocker wording corrected, preflight re-run 4). Updated run039 (current-state consistency tool, FODT scoring package, ODF reuse strategy, preflight re-run 5 — 5 consecutive FAIL). Updated run040 (clean-git loophole closed, consistency checker strengthened, FODT Gate 1 scoring verified DEC-034, human-review packet created, preflight re-run 6 — 6 consecutive FAIL). Updated run043 (BLOCKER RESOLVED: LibreOffice 26.2.3.2 installed via winget; oracle_common.py fixed for soffice.com; compare_fods_oracle.py parser call fixed; ORACLE_RUN PASS 4/4; ORACLE_COMPARE PASS 3 PASS 1 WARN; TC-0026 COMPLETED)."
---

# FODS Gate 6 Oracle Blocker Report

**Format:** FODS
**Gate:** 6 — Oracle Comparison
**Status:** RESOLVED — Gate 6 PASSED (Babar Raza, 2026-05-08, run044)
**Prepared by:** run035 (2026-05-07); updated run036–run040 (2026-05-07); updated run043 (2026-05-08); status updated run046 (2026-05-08)
**Gate 6 approved:** YES — PASSED (Babar Raza, 2026-05-08, run044). TC-0027 DEC-034 PASS 24/24. ORACLE_COMPARE: PASS 3/4 WARN 1/4.

---

## BLOCKER RESOLVED (run043)

Gate 6 oracle blocker was resolved in run043 (2026-05-08):

- LibreOffice 26.2.3.2 installed via `winget install -e --id TheDocumentFoundation.LibreOffice`
- `oracle_common.py` updated: added `soffice.com` (Windows console-mode variant) to candidates before `soffice.exe` (GUI wrapper that does not write to stdout in subprocess capture)
- `run_fods_oracle.py` updated: `--infilter=OpenDocument Spreadsheet Flat XML` + `--convert-to csv:Text - txt - csv (StarCalc)` for correct FODS→CSV conversion
- `compare_fods_oracle.py` updated: parser subprocess call fixed to correct CLI convention
- **ORACLE_PREFLIGHT: PASS** — LibreOffice 26.2.3.2 found at `C:\Program Files\LibreOffice\program\soffice.com`
- **ORACLE_RUN: PASS** — 4/4 samples converted
- **ORACLE_COMPARE: PASS** — 3/4 PASS, 1/4 WARN (multi-sheet CSV export limitation, expected)
- **TC-0026: COMPLETED** (oracle comparison executed)

Gate 6 is now pending TC-0027 independent verification, then human approval.

---

## Historical Blocker: LibreOffice Not Installed (runs 035–042)

Gate 6 oracle preflight was executed 9 times before resolution — run035 (initial), run036–041 (re-runs with various harness improvements), run042 (8th consecutive FAIL), run043 pre-install (9th consecutive FAIL). The oracle tool (LibreOffice headless) was not installed on the development machine during these runs.

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

| Check | run035 | run036 | run037 | run038 | run039 | run040 |
|---|---|---|---|---|---|---|
| `soffice --version` (PATH) | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| `libreoffice --version` (PATH) | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| `C:\Program Files\LibreOffice\program\soffice.exe` | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| `C:\Program Files (x86)\LibreOffice\program\soffice.exe` | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| `/usr/bin/soffice` | N/A | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| `/usr/bin/libreoffice` | N/A | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| `/usr/lib/libreoffice/program/soffice` | N/A | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| `/Applications/LibreOffice.app/Contents/MacOS/soffice` | N/A | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND |
| `FORMAT_FACTORY_SOFFICE` env var | Not checked | NOT SET | NOT SET | NOT SET | NOT SET | NOT SET |
| FODS samples (4 required) | 4 found | 4 found | 4 found | 4 found | 4 found | 4 found |
| Oracle result | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |

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

## Improvements Completed (run037)

| Deliverable | Status | Notes |
|---|---|---|
| `tools/oracle/provider_registry.yaml` | **NEW** | Oracle provider registry: LibreOffice entry + FODS assignment |
| `tools/oracle/validate_oracle_environment.py` | **NEW** | Environment check tool (reads registry, discovers providers) |
| `docs/ai/oracle-provider-strategy.md` | **NEW** | Oracle provider architecture, governance rules, future-format guide |
| `acquisition-packs/fods/oracle-provider-options.md` | **NEW** | Provider evaluation: LibreOffice APPROVED; others rejected/deferred |
| `tools/evidence/validate_evidence_bundle.py` | **HARDENED** | --check-no-pending flag: fails if any metadata file has PENDING marker |
| `tests/evidence/test_negative_bundle_validation.py` | **NEW** | 4 negative tests: thin bundle FAIL, PENDING marker FAIL, clean PASS |
| `plans/master-plan.md` header | **FIXED** | Latest commit: 82281e6→3216dcf (stale reference corrected) |
| `memory/09` latest commit | **FIXED** | "run036 commit pending"→3216dcf working tree clean |

## TC Status After run037

| Taskcard | Status |
|---|---|
| TC-0025 (Gate 6 planning) | completed |
| TC-0026 (Gate 6 execution) | blocked_missing_oracle_tool |
| TC-0027 (Gate 6 verification) | not_started |

---

## Improvements Completed (run038)

| Deliverable | Status | Notes |
|---|---|---|
| `tools/oracle/self_test_oracle_harness.py` | **NEW** | HARNESS_SELF_TEST_ONLY; validates compare/summarize plumbing using synthetic CSV fixtures; no LibreOffice required; ORACLE_HARNESS_SELF_TEST: PASS 4/4 |
| `acquisition-packs/fods/oracle-harness-self-test-report.md` | **NEW** | Auto-generated harness self-test report; PASS 4/4; clearly marked HARNESS_SELF_TEST_ONLY |
| `acquisition-packs/fods/oracle-operator-handoff.md` | **NEW** | Precise install/verify/execute instructions; exact TC-0026 prompt text; "What NOT to do" table |
| `taskcards/TC-0026-fods-gate6-oracle-execution.md` | **CORRECTED** | Blocker wording fixed: was "Blocking: Gate 6 human approval" (wrong), now "Blocking: LibreOffice missing" |
| `registry/format-registry.yaml` gate_6 | **UPDATED** | run038 preflight recorded as 4th consecutive FAIL; harness self-test + operator handoff documented |
| `registry/candidates/odf-flat-family-shortlist.yaml` | **NEW** | Next-format candidate shortlist; FODT recommended; gate_1_approved: false |
| `acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md` | **NEW** | Human-readable shortlist summary; CANDIDATE-ONLY |
| `taskcards/TC-0028-next-format-candidate-shortlist.md` | **NEW** | Independent verification sprint taskcard for shortlist |

## TC Status After run038

| Taskcard | Status |
|---|---|
| TC-0025 (Gate 6 planning) | completed |
| TC-0026 (Gate 6 execution) | blocked_missing_oracle_tool |
| TC-0027 (Gate 6 verification) | not_started |
| TC-0028 (Next-format candidate shortlist) | not_started — independent verification required |

---

## Improvements Completed (run039)

| Deliverable | Status | Notes |
|---|---|---|
| `tools/evidence/check_current_state_consistency.py` | **NEW** | Validates "Latest commit" in master-plan matches actual git HEAD; CURRENT_STATE_CONSISTENCY: PASS |
| `tests/evidence/test_current_state_consistency.py` | **NEW** | 4 negative tests for consistency checker — all PASS |
| `registry/candidates/fodt-gate1-scoring-package.yaml` | **NEW** | FODT Gate 1 7-factor scoring: 88/100, Accept band (candidate-only, gate_1_approved: false) |
| `taskcards/TC-0029-fodt-gate1-scoring-preparation.md` | **NEW** | TC for FODT Gate 1 scoring preparation and independent verification |
| `docs/python-foss/odf-flat-family-reuse-strategy.md` | **NEW** | ODF flat family pipeline reuse strategy (FODS→FODT~40-50% effort) |
| master-plan stale commit bc2bdf8 | **FIXED** | Was showing 998412c (stale run038 reference); corrected to bc2bdf8 |
| preflight re-run 5 | **CONFIRMED** | ORACLE_ENV: BLOCKED — 5 consecutive FAIL (run035–run039) |

## TC Status After run039

| Taskcard | Status |
|---|---|
| TC-0025 (Gate 6 planning) | completed |
| TC-0026 (Gate 6 execution) | blocked_missing_oracle_tool |
| TC-0027 (Gate 6 verification) | not_started |
| TC-0028 (Next-format candidate shortlist) | in_progress — shortlist verified run039; FODT scoring package created (TC-0029) |
| TC-0029 (FODT Gate 1 scoring preparation) | not_started — independent verification sprint required |

---

## Improvements Completed (run040)

| Deliverable | Status | Notes |
|---|---|---|
| `tools/evidence/validate_evidence_bundle.py` | **HARDENED** | Clean-git loophole closed: dirty git-status-final.txt now fails even with require_clean_git: false, unless emergency_blocker_bundle: true |
| `tools/evidence/build_evidence_bundle.py` | **HARDENED** | Same loophole fix: dirty git always fails at build time unless emergency_blocker_bundle: true |
| `tools/evidence/contracts/base-run.yaml` | **UPDATED** | require_clean_git: true + emergency_blocker_bundle: false added as base defaults |
| `tools/evidence/check_current_state_consistency.py` | **STRENGTHENED** | Now checks 10 invariants: master-plan commits, memory/09 commit, registry gate_6 not approved, FODT candidate-only, no acquisition-packs/fodt/, pack.yaml gate_6 |
| `tests/evidence/test_negative_bundle_validation.py` | **UPDATED** | 2 new negative tests added (6/6 total PASS): dirty-git-fails-even-with-require_clean_git_false, dirty-git-passes-with-emergency_blocker_bundle_true |
| TC-0029 DEC-034 verification | **PASS** | 7/7 scoring factors independently verified; 88/100 confirmed; Accept band confirmed |
| FODT Gate 1 human-review packet | **NEW** | acquisition-packs/_candidate-shortlists/fodt-gate1-human-review-packet.md — ready for human Gate 1 review decision |
| preflight re-run 6 | **CONFIRMED** | ORACLE_ENV: BLOCKED — 6 consecutive FAIL (run035–run040) |
| stale commits | **FIXED** | master-plan header d052510→54a27dc; memory/09 stale→54a27dc; Section 33 PENDING marker added |

## TC Status After run040

| Taskcard | Status |
|---|---|
| TC-0025 (Gate 6 planning) | completed |
| TC-0026 (Gate 6 execution) | blocked_missing_oracle_tool |
| TC-0027 (Gate 6 verification) | not_started |
| TC-0028 (Next-format candidate shortlist) | in_progress — shortlist verified run039; FODT scoring package created (TC-0029) |
| TC-0029 (FODT Gate 1 scoring preparation) | verification_passed_pending_human_review — DEC-034 PASS run040; human-review packet ready |

---

## Improvements Completed (run043)

| Deliverable | Status | Notes |
|---|---|---|
| LibreOffice 26.2.3.2 | **INSTALLED** | Via `winget install -e --id TheDocumentFoundation.LibreOffice` (official source, 355 MB MSI) |
| `tools/oracle/oracle_common.py` | **FIXED** | Added `soffice.com` before `soffice.exe` in LIBREOFFICE_CANDIDATES; also auto-try `.com` variant when env var points to `.exe` |
| `tools/oracle/run_fods_oracle.py` | **FIXED** | Replaced wrong `--infilter=calc_csv:44,34,UTF8` with `--infilter=OpenDocument Spreadsheet Flat XML`; `--convert-to` uses `csv:Text - txt - csv (StarCalc)` |
| `tools/oracle/compare_fods_oracle.py` | **FIXED** | `load_parser_via_subprocess` call corrected: was `--output json <path>` (wrong), now `<path>` (correct CLI convention) |
| Oracle preflight re-run 10 | **PASS** | ORACLE_PREFLIGHT: PASS — `soffice.com` found at `C:\Program Files\LibreOffice\program\soffice.com` |
| `python tools/oracle/run_fods_oracle.py` | **PASS** | ORACLE_RUN: PASS — 4/4 samples converted to CSV |
| `python tools/oracle/compare_fods_oracle.py` | **PASS** | ORACLE_COMPARE: PASS — 3/4 PASS, 1/4 WARN (multi-sheet CSV limit) |
| `python tools/oracle/summarize_oracle_results.py` | **PASS** | ORACLE_SUMMARIZE: PASS |
| `acquisition-packs/fods/gate6-oracle-comparison-report.md` | **CREATED** | 3 PASS, 1 WARN — oracle_comparison_created_pending_independent_verification |

## TC Status After run043

| Taskcard | Status |
|---|---|
| TC-0025 (Gate 6 planning) | completed |
| TC-0026 (Gate 6 execution) | **COMPLETED** — oracle comparison PASS 3/4 PASS 1/4 WARN |
| TC-0027 (Gate 6 verification) | not_started — DEC-034 independent verification required before human Gate 6 review |
| TC-0028 (Next-format candidate shortlist) | COMPLETED (run041) |
| TC-0029 (FODT Gate 1 scoring preparation) | COMPLETED (run041) |
| TC-0030 (FODT Gate 2) | COMPLETED (run042) — FODT Gate 2 APPROVED (run043) |
| TC-0031 (FODT Gate 2 DEC-034) | COMPLETED (run043) — independent verification PASS |

---

## Gate 6 Status (Closed)

**Gate 6 APPROVED** — Babar Raza, 2026-05-08, run044. TC-0027 DEC-034 PASS 24/24.

Gate 6 oracle comparison and independent verification are complete. Human approval has been recorded in registry/format-registry.yaml. This blocker report is archived for historical reference. Gate 7 planning was already in place (TC-0033); Gate 7 execution proceeded in run045.
