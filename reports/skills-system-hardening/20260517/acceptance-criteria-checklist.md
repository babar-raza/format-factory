# Acceptance Criteria Checklist
**Sprint:** FORMAT-FACTORY-SKILLS-PRD-HARDENING-001
**Date:** 2026-05-17

## settings.json (TC-001)
- [x] description updated to R19 state
- [x] description_last_updated = "r19-skills-hardening"
- [x] "blocked DEC-033" removed
- [x] "DEC-033 RESOLVED 2026-05-12" present
- [x] "ZST Gates 1-7" present
- [x] "FODP/FODG/Gnumeric/ABW Gates 1-3" present
- [x] phase_note updated, no DEC-033 blocking claim
- [x] UPDATED note appended to notes[]

## evidence-review-next-prompt.md (TC-002)
- [x] Step 0 dependency preflight added (6 required files)
- [x] Step 1 uses memory/00-index.md dynamic lookup (not hardcoded memory/09)
- [x] Step 6 has contract selection guidance (sort by mtime, fallback base-run.yaml)
- [x] Changelog 1.1 entry added

## memory-sprint.md (TC-003)
- [x] Step 14 explains permission dialog behavior
- [x] COMMIT_PENDING_HUMAN_APPROVAL pattern present
- [x] Output Format item 6 conditional
- [x] Step 12 NOTE: 55-file floor justification
- [x] Validation section explains permission-denied behavior
- [x] Changelog 1.1 entry added

## export-plan-context.md (TC-004)
- [x] Step 0 dependency + currency check added
- [x] Staleness guard Python snippet present
- [x] memory/34, memory/35 in standard file list
- [x] R17/R18 planning reports in standard file list
- [x] R11/R12 era entries removed from operational list
- [x] MANDATORY MAINTENANCE note in Notes section
- [x] last-updated: "2026-05-17"
- [x] Changelog 1.1 entry added

## export-plan-context.md git tracking (TC-000)
- [x] File was untracked; now committed (fd1ea04)
- [x] git status shows committed (not untracked)

## AGENTS.md J4 (TC-005)
- [x] J4 paragraph added after J3
- [x] CURRENT_INTERNAL_ONLY classification
- [x] Invocation pattern documented
- [x] fods/fodt scope restriction documented
- [x] Phase 1 deferral noted (TC-0004)

## TC-0004 prerequisites (TC-007)
- [x] PREREQUISITES section in TC-0004-commands-skills.md
- [x] All 7 deny entries listed
- [x] Settings update requirement documented
- [x] NOTE added to _readme.md Planned Commands footer

## docs/agent-methodology-index.md (TC-008)
- [x] Section 5 now has 5 rows (was 4)
- [x] /export-plan-context row with correct file link and mode description
