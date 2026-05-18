# Memory 37 — R20 Productization Train: Source and Gate 11 Architecture

**Sprint:** FORMAT-FACTORY-R20-PRODUCTIZATION-TRAIN-ZST-FODP-FODG-GNUMERIC-ABW-SOURCE-AND-GATE11-ARCHITECTURE-SWARM-001
**Date:** 2026-05-16 to 2026-05-17
**BACKFILL NOTE:** This memory file was created 2026-05-18 (R24 sprint) as a memory continuity
repair. memory/36 (R19) existed; memory/38 (R21) existed; memory/37 (R20) was missing.
This backfill is based on evidence from live R20 reports in reports/governance/,
reports/implementation/, and reports/verification/.

---

## Sprint Summary

R20 "productization train" advanced five Python FOSS formats (ZST, FODP, FODG, Gnumeric, ABW)
from their R19 baseline state. Key objectives:
1. Implement ZST Python source (Gate 7 → source complete)
2. Implement FODP, FODG, Gnumeric, ABW Python source (Gates 4-7)
3. Produce FODS/FODT Gate 11 executable architecture plan (planning only)
4. Repair R19 evidence hygiene issues
5. Delegated decision cleanup

---

## R19 Baseline (from R20 preflight)

| Format | G1 | G2 | G3 | G4 | G5 | G6 | G7 | impl_authorized |
|--------|----|----|----|----|----|----|----|-----------------|
| ZST | passed | passed | passed | passed | waived | passed | passed | False |
| FODP | passed | passed_fast_path | passed | not_started | not_started | not_started | not_started | not_set |
| FODG | passed | passed_fast_path | passed | not_started | not_started | not_started | not_started | not_set |
| Gnumeric | passed | passed | passed | not_started | not_started | not_started | not_started | not_set |
| ABW | passed | passed_with_notes | passed | not_started | not_started | not_started | not_started | not_set |

---

## ZST Python Source Implementation

- **Authorization:** implementation_authorized=true (granted R19+)
- **Source file:** `src/python/zst/__init__.py`
- **Key implementation:** ZST probe + decompress using `zstandard` library; FrameHeaderInfo
  (is_unknown, single_segment); safe 64MiB decompression guard; Python 3.13 import path fix
  (importlib workaround → sys.path + regular import)
- **Report:** reports/implementation/r20-zst-python-source-implementation-report-20260516.md
- **Verification:** reports/verification/r20-zst-python-source-independent-verification-20260516.md

---

## FODP/FODG/Gnumeric/ABW Python Source

- **FODP:** src/python/fodp/fodp_codec.py — Flat ODP ZIP+XML parser
- **FODG:** src/python/fodg/fodg_codec.py — Flat ODG ZIP+XML parser
- **Gnumeric:** src/python/gnumeric/gnumeric_codec.py — gzip+XML, 64MiB guard
- **ABW:** src/python/abw/abw_codec.py — DOCTYPE strip, XXE-safe XML parser
- All: implementation_authorized=true, commercial_product_ready=false

---

## FODS/FODT Gate 11 Architecture Plan

- **Status:** PLANNING ONLY — Gate 11 NOT approved in R20
- **Report:** reports/governance/r20-gate11-fods-fodt-executable-architecture-plan-20260517.md
- **Scope:** C4 (Load), C5 (Save), C6 (Convert) architecture; commercial_product_ready: false
- **Key decision:** FODS/FODT .NET commercial track confirmed as vertical-slice C4-C6
- **G11-G:** not_started (human approval required — Babar Raza)

---

## R20 Evidence Hygiene

- **P-EVID-001 through P-EVID-004:** Policies established and tested in R19; R20 applied them
- **R19 bundle issues:** Classified in R20 preflight; evidence repaired in R20 closure
- **Delegated decision cleanup:** reports/governance/r20-delegated-decision-cleanup-report-20260516.md
- **Evidence hygiene hardening:** reports/governance/r20-evidence-hygiene-hardening-report-20260516.md

---

## Commercial Readiness State at R20 End

| Format | commercial_product_ready | Notes |
|--------|--------------------------|-------|
| ZST | false | Python FOSS source complete, not commercial |
| FODP | false | Python FOSS source complete |
| FODG | false | Python FOSS source complete |
| Gnumeric | false | Python FOSS source complete |
| ABW | false | Python FOSS source complete |
| FODS | false | Gate 11 planning only, no approval |
| FODT | false | Gate 11 planning only, no approval |

---

## Key Files Created in R20

- `src/python/zst/__init__.py` (and supporting modules)
- `src/python/fodp/__init__.py` / `fodp_codec.py`
- `src/python/fodg/__init__.py` / `fodg_codec.py`
- `src/python/gnumeric/__init__.py` / `gnumeric_codec.py`
- `src/python/abw/__init__.py` / `abw_codec.py`
- `reports/governance/r20-preflight-r19-baseline-and-lane-ownership-20260516.md`
- `reports/governance/r20-delegated-decision-cleanup-report-20260516.md`
- `reports/governance/r20-evidence-hygiene-hardening-report-20260516.md`
- `reports/governance/r20-gate11-fods-fodt-executable-architecture-plan-20260517.md`
- `reports/implementation/r20-zst-python-source-implementation-report-20260516.md`
- `reports/verification/r20-zst-python-source-independent-verification-20260516.md`

---

## Notes for Future Agents

- memory/36 = R19; memory/37 = R20 (this file); memory/38 = R21
- R20 is when Python FOSS source implementations first appeared for FODP/FODG/Gnumeric/ABW
- FODS/FODT Gate 11 planning was done in R20 but NOT approved until R23 (G11-E)
- The `__track__` field is "python-foss" (not "foss") — established in R23
