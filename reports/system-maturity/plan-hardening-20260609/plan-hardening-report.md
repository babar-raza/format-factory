# Plan Hardening Report
## Plan Hardening Sprint 2026-06-09

---

## What the Earlier Weakness/Maturity Plan Got Right

1. **Gate 11 contradiction CONFIRMED:** context-pack claims APPROVED, registry says NOT. Registry wins. This was the plan's strongest finding.
2. **Shallow formats outnumber deep formats:** Verified. 10 deep + 4 medium + 6 shallow/skeleton.
3. **Queue-backed autonomy unproven end-to-end:** Verified. Components exist but integrated flow never validated.
4. **Evidence automation partial:** Verified, though actual auto percentage is ~47% (not 80% as claimed).
5. **Git state dirty:** Verified. 78 modified + 375 untracked files.
6. **Python FOSS unpublished:** Verified. Wheels built locally but no PyPI publication.
7. **Authority classifications have drifted:** Verified. FODT corrected P0→P4, context-pack overclaims Gate 11.
8. **Correct root-cause groupings:** Advisory-vs-authoritative drift, integration gap, breadth-first strategy, publication infrastructure missing, checkpoint discipline — all valid.

## What the Earlier Plan Got Wrong

1. **"Python has no write/export for FODS/FODT"** — WRONG. Python FODS has write_fods()/workbook_to_xml(). Python FODT has write_fodt()/document_to_xml(). All 5 core formats have write functions.
2. **"150+ untracked files"** — UNDERSTATED. Actual count is 375. Earlier plan missed 225+ files.
3. **".NET is Tier 0-1 only / skeleton"** — WRONG. FODS .NET has 2,179 LOC with Load/Parse/Edit/Save/Export(CSV/HTML/JSON) and roundtrip. FODT .NET has 2,035 LOC with paragraph/heading editing and 4 export formats. Both exceed Tier 1.
4. **"Evidence automation is 80%"** — OVERSTATED. Actual field-by-field analysis shows ~47% auto-generated. The auto fields cover data-heavy items (git, tests) but majority of declaration fields are still manual.
5. **"Test count drops are STALE"** — CORRECT conclusion but INSUFFICIENT analysis. Drops were caused by sprint scope differences (targeted vs full suite), not test deletion. Should have documented full-suite counts at checkpoints.

## What the Earlier Plan Failed to Verify

1. **Did not verify Python write capability** — claimed "no write" without reading __init__.py exports
2. **Did not verify .NET LOC or actual operations** — claimed "skeleton" without reading .cs files
3. **Did not count untracked files precisely** — estimated "150+" when actual is 375
4. **Did not verify evidence auto-packager field coverage** — claimed "80%" without code inspection
5. **Did not cross-check master-plan.md** — master-plan says "C2" for .NET but code exceeds C2

## What the Earlier Plan Overstated

1. **W1 severity:** .NET is not skeleton. It's a functional prototype with real operations.
2. **W3 severity:** With 5 Python formats having write capability, product depth is better than claimed.
3. **W10 (governance over-weight):** Recent sprints are product-focused. The ratio is improving.
4. **W13 (evidence problems):** Mostly resolved. Current state has 0 blocking violations.

## What the Earlier Plan Understated

1. **Git risk:** 375 untracked files include 2 new Python modules, 150+ tests, 10+ tools — all at risk of loss from any destructive git command. This is a REAL risk, not just housekeeping.
2. **Context-pack contradiction severity:** Not just a data error — any automation reading context-pack for gate status will make wrong decisions. This is an active systemic risk.
3. **Lane ledger gap:** Lane ledger has only 1 entry. This means NO sprint execution is traceable through the ledger. Evidence automation cannot work without ledger data.

## What the Earlier Plan Put in the Wrong Order

1. **Proposed product implementation before contradiction resolution** — Sprint 2 included "Add Python write capability" but the Gate 11 contradiction must be documented first to prevent downstream confusion.
2. **Proposed 15 report files but no governance framework** — Reports without taskcards and state machine are unverifiable. This sprint adds the missing governance layer.
3. **Mixed product execution with planning** — Earlier plan treated investigation and execution as one sprint. This sprint correctly separates Stage 1 (planning/hardening) from Stage 2 (controlled execution).

## Claims Requiring Current Repo Proof (Verified in This Sprint)

| Claim | Verified? | Method |
|---|---|---|
| Gate 11 NOT approved | YES | Read registry verbatim: approved_by: null |
| Context-pack claims Gate 11 approved | YES | Read context-pack verbatim: APPROVED_BY_BABAR_RAZA_2026_06_05 |
| Python write capability exists | YES | Read __init__.py exports for 5 formats |
| .NET exceeds Tier 1 | YES | Read .cs files, counted LOC, documented operations |
| 375 untracked files | YES | git status --short output classified |
| Evidence auto 47% not 80% | YES | Code inspection of evidence_auto_packager.py |
| Lane ledger has 1 entry | YES | Read lane-execution-ledger.json |

## Claims Demoted Until Verified

| Claim | Original Status | Demoted Status | Reason |
|---|---|---|---|
| FODS P6 authority | CLAIMED | P4-P5 PENDING | FACT-FODS-002 needs_review |
| "80% evidence automation" | CLAIMED | ~47% VERIFIED | Field-by-field analysis contradicts |
| Queue-backed autonomy "infrastructure complete" | CLAIMED | COMPONENTS EXIST | No integrated end-to-end proof |
