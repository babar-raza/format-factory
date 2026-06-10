# Gap Analysis — Master Plan Healing Plan Repair

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-GOVERNANCE-REVIEW-HEALING-PLAN-001
**Source:** plans/master-plan.md (2229 lines, version 2.70)
**Date:** 2026-06-10

## Gaps Identified

| Gap ID | Description | Severity | Category | Affected Section(s) | Proposed Action |
|--------|-------------|----------|----------|---------------------|-----------------|
| GAP-MP-001 | Header version mismatch: header says 2.64, footer says 2.70 | CRITICAL | contradictory | Header (line 6), Footer (line 2228) | Rewrite header to 2.70 or next version |
| GAP-MP-002 | Header last_updated 2026-05-31 but content extends to 2026-06-04 (Section 44) | HIGH | stale | Header (line 7) | Update to actual last edit date |
| GAP-MP-003 | Section 6 last_completed_sprint = COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001 (2026-05-13), reality is R113+ and beyond | HIGH | stale | Section 6 (line 143) | Update to current sprint |
| GAP-MP-004 | Section 7 "bundle must be uploaded by human" rule (line 157) directly conflicts with Section 41 declaration-driven pipeline | CRITICAL | contradictory | Section 7 (lines 152-166), Section 41 (lines 1957-2033) | Archive Section 7, replace with pointer to Section 41 |
| GAP-MP-005 | Section 24 WIP limit "Product stages: 1 format" (line 660) contradicts 11 active POC targets in poc-targets.yaml | CRITICAL | contradictory | Section 24 (line 660) | Update WIP limits to reflect current multi-format reality |
| GAP-MP-006 | Section 5 rule 6 "No section may be split out" (line 107) contradicts existence of 29 docs/governance/ files | HIGH | contradictory | Section 5 (line 107) | Amend rule to allow authorized split-outs with canonical summary |
| GAP-MP-007 | Section 11 "Codex optional secondary executor" (line 296) — unsupported, never used | MEDIUM | unsupported | Section 11 (lines 295-296) | Mark as historical/deferred; remove from active operations |
| GAP-MP-008 | Section 13 "No functional commands exist yet" (line 347) — FALSE, 25 commands exist | CRITICAL | stale | Section 13 (line 347) | Update to reflect actual command inventory |
| GAP-MP-009 | Section 25 Active Taskcards (TC-0001..TC-0053) are deeply stale — project moved to declaration-driven model | HIGH | stale | Section 25 (lines 666-691) | Archive; replace with pointer to current taskcard model |
| GAP-MP-010 | Section 32 "Next required action" references Gate 11 G11-A from run047 era | HIGH | stale | Header (line 15) | Update to current next action |
| GAP-MP-011 | Section 33 Run Commit Ledger: ~380 lines of historical commit records (run001-run048) | MEDIUM | historical-only | Section 33 (lines 1052-1429) | Archive to docs/history/; replace with brief summary + pointer |
| GAP-MP-012 | Section 28 Healing Gap Register G-HEAL-001..025+ — historical-only | MEDIUM | historical-only | Section 28 (approx lines 779-841) | Archive to docs/history/ |
| GAP-MP-013 | Section 31 Phase 0 Review Checklist — historical-only, Phase 0 complete | MEDIUM | historical-only | Section 31 | Archive to docs/history/ |
| GAP-MP-014 | Section 9 Phase 0 Required Files (45-file list) — historical-only, Phase 0 accepted | MEDIUM | historical-only | Section 9 (lines 209-260) | Archive to docs/history/ |
| GAP-MP-015 | Section 36 S-F2F Secondary Sprint — closed/unauthorized, subordinate to main sprint | MEDIUM | historical-only | Section 36 (lines 1506-1577) | Archive to docs/history/ |
| GAP-MP-016 | Section 37 Format Understanding Layer — unauthorized backlog, never executed | MEDIUM | historical-only | Section 37 (lines 1582-1656) | Archive to docs/history/; condense to 5-line summary |
| GAP-MP-017 | Section 39 AI/LLM Platform Layer — unauthorized backlog, conflicts with ai-authority-boundary.md | HIGH | contradictory | Section 39 (lines 1747-1844) | Archive to docs/history/; conflicts with docs/governance/ai-authority-boundary.md |
| GAP-MP-018 | Section 7/33 legacy ZIP bundle model described as primary — superseded by declaration-driven pipeline (Section 41) | HIGH | stale | Section 7, Section 33 | Archive Section 7; update Section 33 header |
| GAP-MP-019 | No master-plan freshness/sync mechanism exists — drift accumulates silently | HIGH | missing | N/A | Create docs/governance/master-plan-sync-policy.md |
| GAP-MP-020 | No stale-claim lint defined — stale claims persist across sprints | HIGH | missing | N/A | Define stale-claim lint patterns and enforcement |
| GAP-MP-021 | state/current-state.md says "Gate 11 approved: False" but poc-targets.yaml shows gate_11_g11g: APPROVED_BY_BABAR_RAZA_2026_06_05 | CRITICAL | contradictory | External: state/current-state.md vs poc-targets.yaml | Resolve in execution; state/current-state.md must be updated |
| GAP-MP-022 | Section 6 says "Active formats in registry: fods, fodt" — ignores 9 other active POC targets | HIGH | stale | Section 6 (line 123) | Update to reflect all 11 POC targets |
| GAP-MP-023 | Section 6 says "Gate 11 NOT approved" (lines 9, 148) — contradicts Gate 11 G11-G approval 2026-06-05 | CRITICAL | contradictory | Section 6, Header | Update to reflect Gate 11 approval |
| GAP-MP-024 | Section 38 Format Expansion Roadmap references "Conway R1-R9" — never implemented, stale | MEDIUM | stale | Section 38 (lines 1661-1744) | Archive to docs/history/ |
| GAP-MP-025 | Run History table (Section 33) runs run001-run042 only — missing all R-numbered sprints | HIGH | stale | Section 33 (lines 1003-1048) | Archive; modern sprints use declaration-driven model |

## Summary

- **CRITICAL gaps:** 6 (GAP-MP-001, 004, 005, 008, 021, 023)
- **HIGH gaps:** 9 (GAP-MP-002, 003, 006, 010, 017, 018, 019, 020, 022, 025)
- **MEDIUM gaps:** 10 (GAP-MP-007, 009, 011, 012, 013, 014, 015, 016, 024)
- **Total:** 25 gaps

All gaps require resolution in the healing execution sprint. No gap may be ignored.
