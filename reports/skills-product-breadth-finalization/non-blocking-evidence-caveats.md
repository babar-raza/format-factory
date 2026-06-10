# Non-Blocking Evidence Caveats
Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001

All caveats below are non-blocking for finalization sprint progress.

---

## Caveat 1 — Hardening Sprint ACCEPTED_WITH_REWORK
Severity: LOW
Source: reports/skills-governed-execution-hardening/review-package-proof.md
Detail: Hardening sprint received ACCEPTED_WITH_REWORK (not full ACCEPTED) due to evidence_quality_score HIGH.
All 8 items were accepted. Zero product source changes. Zero test failures.
Impact on finalization: None — all hardening artifacts are consumable as-is.

## Caveat 2 — FODT/Netpbm Shells Had Placeholders
Severity: LOW
Detail: Shell packets used {N} and {FeatureName} placeholders. This is expected for shells.
Resolution: This sprint resolves the placeholders with concrete values (R114 for both families).
Impact: None — placeholder resolution is the purpose of this sprint.

## Caveat 3 — Acceleration Packet ai_rationale Is Fixture Error
Severity: LOW
Detail: Both acceleration packets have `ai_rationale: "[fixture_error] ModuleNotFoundError: No module named 'tools'"`.
Both carry `authority_state: ai_draft` and `non_authoritative: true`.
Impact: Acceleration AI designs are advisory only. Skills full packets supersede them.

## Caveat 4 — Netpbm Acceleration Packet Chose Stale Feature
Severity: LOW
Detail: Acceleration packet selected `netpbm_flip_diagonal` but NetpbmR106FlipDiagonalTests.cs already exists
(FlipDiagonal implemented at R106). The acceleration packet has `authority_state: ai_draft`.
Resolution: This sprint selects a new R114 feature for Netpbm handoff.
Impact: None — Skills lane corrects the stale ai_draft selection.

## Caveat 5 — No Lane Execution Ledger in Hardening Sprint
Severity: LOW
Detail: Hardening sprint's autonomous cycle flagged MEDIUM: missing_lane_ledger.
This was expected for a governance/hardening sprint (no product execution lanes).
Impact on finalization: None — this finalization sprint includes a lane execution ledger.
